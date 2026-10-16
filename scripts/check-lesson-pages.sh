#!/usr/bin/env bash

set -euo pipefail

# The single-page render of the lessons the targeted run selected (ADR 017
# decision 7, F119).
#
# Usage: check-lesson-pages.sh [<root>]
#
# Reads the selection of the run, .agents/verification/selection.json under
# <root> (this repository by default). Only the selection of the targeted run
# (its tier is "targeted") names lessons for this check: a run that builds
# the site, the full run and a run with --base, executes the selected lessons
# in the build, builds them again for determinism, and reproduces each of
# them in a fresh clone, so this check has nothing to do there and says so.
#
# For the targeted run it renders each selected lesson page alone, as the
# page's "Reproduce this" commands do: in a clone of the working tree (the
# files Git tracks or would add) with its own locked environment (`uv sync
# --locked`, so the page's package is the clone's and reads the clone's
# files: the record of its Lean build, its data), with the Lean build first
# in the clone when a selected lesson displays Lean modules, and `uv run
# --locked quarto render <page>` there, within the 30-second budget of a
# lesson page. A failing cell, an equation that cannot become MathML, or a
# slow page fails the check. When a file under lean/ differs from the base
# branch, it also runs the Lean build of this checkout, so a changed proof
# that no selected lesson displays is checked too. It never builds the site:
# the experiment check of ADR 016 decision 4 joins here when the lessons
# declare their entry points (F117).
#
# UV_PROJECT, which the tests set to run this script on a copy of the
# repository, applies to the script's own Python helper only; the commands in
# the clone run without it, in the clone's environment.

default_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
root="${1:-$default_root}"
project="${UV_PROJECT:-$root}"
budget_seconds=30

fail() {
  echo "Error: $*" >&2
  exit 1
}

[[ -d "$root" ]] || fail "$root is not a directory."
root="$(cd "$root" && pwd -P)"
git -C "$root" rev-parse --is-inside-work-tree >/dev/null 2>&1 ||
  fail "$root is not a Git working tree; the clone of the working tree needs one."
selection_file="$root/.agents/verification/selection.json"

# The tier of the selection and the lessons it executes, one per line.
read_selection() {
  uv run --locked --project "$project" python -c '
import sys
from pathlib import Path

from pbc.authoring import selection as selecting

data = selecting.read(Path(sys.argv[1]))
print(data.get("tier") or "none" if data else "none")
for lesson in (data or {}).get("execute", []):
    print(lesson)
' "$root"
}

tier=""
lessons=()
while IFS= read -r line; do
  if [[ -z "$tier" ]]; then
    tier="$line"
  else
    lessons+=("$line")
  fi
done < <(read_selection)
[[ -n "$tier" ]] || fail "the selection of the run could not be read."

if [[ "$tier" != "targeted" ]]; then
  echo "Nothing to render: this run has no targeted selection, so the site build, the determinism check, and the reproduction cover every lesson it executes."
  exit 0
fi

# A changed proof that no selected lesson displays: the Lean build of this
# checkout, when a file under lean/ differs from the base branch (counting
# uncommitted and untracked files), or when that cannot be determined.
lean_changed=1
for ref in origin/main main; do
  merge_base="$(git -C "$root" merge-base "$ref" HEAD 2>/dev/null)" || continue
  [[ -n "$merge_base" ]] || continue
  changed="$(
    git -C "$root" diff --name-only "$merge_base" -- lean &&
      git -C "$root" ls-files --others --exclude-standard -- lean
  )" || break
  [[ -n "$changed" ]] || lean_changed=0
  break
done
if [[ "$lean_changed" -eq 1 ]]; then
  echo "-- The Lean build: a file under lean/ differs from the base branch, or that cannot be determined."
  (cd "$root" && ./scripts/check-lean.sh) || fail "the Lean build failed."
fi

if [[ "${#lessons[@]}" -eq 0 ]]; then
  echo "Nothing to render: the targeted run selected no lesson."
  exit 0
fi

# A clone of the working tree: the files Git tracks or would add, as a
# learner's clone holds them, without the ignored state of this checkout.
clone="$(mktemp -d "${TMPDIR:-/tmp}/lesson-pages.XXXXXX")"
trap 'rm -rf "$clone"' EXIT
(
  cd "$root" &&
    git ls-files -z --cached --others --exclude-standard |
    while IFS= read -r -d '' file; do
      [[ -f "$file" ]] && printf '%s\0' "$file"
    done |
    tar --null -T - -cf - |
    tar -C "$clone" -xf -
) || fail "the working tree could not be copied."

# The clone's own locked environment, as the page's commands say ("uv sync
# --locked" after the clone). The package is installed from the clone, so a
# page rendered there reads the clone's files, not this checkout's: the
# record of the Lean build below, the datasets. From uv's cache this takes
# seconds.
log="$clone/render.log"
echo "-- The locked environment of the clone"
if ! (cd "$clone" && env -u UV_PROJECT uv sync --locked) >"$log" 2>&1; then
  cat "$log" >&2
  fail "the locked environment could not be installed in the clone."
fi

# A lesson that displays Lean modules reads the record of the Lean build of
# its repository, so the clone builds the proofs first, with the packages of
# this checkout, as the page's commands say.
displays_lean=0
for lesson in "${lessons[@]}"; do
  [[ -f "$root/$lesson/index.qmd" ]] || fail "$lesson has no index.qmd."
  if grep -Eq '^[[:space:]]*lean-modules:' "$root/$lesson/index.qmd"; then
    displays_lean=1
  fi
done
if [[ "$displays_lean" -eq 1 ]]; then
  echo "-- The Lean build in the clone: a selected lesson displays Lean modules."
  if [[ -d "$root/lean/.lake/packages" ]]; then
    mkdir -p "$clone/lean/.lake"
    ln -s "$root/lean/.lake/packages" "$clone/lean/.lake/packages"
  fi
  (cd "$clone" && env -u UV_PROJECT ./scripts/check-lean.sh) ||
    fail "the Lean build failed in the clone."
fi

for lesson in "${lessons[@]}"; do
  page="$lesson/index.qmd"
  echo "-- Rendering $page alone"
  started="$(date +%s)"
  if ! (cd "$clone" && env -u UV_PROJECT uv run --locked quarto render "$page") >"$log" 2>&1; then
    cat "$log" >&2
    fail "the page $page does not render."
  fi
  seconds=$(($(date +%s) - started))
  if grep -Fq "Could not convert TeX math" "$log"; then
    cat "$log" >&2
    fail "an equation of $page could not be converted to MathML."
  fi
  [[ "$seconds" -lt "$budget_seconds" ]] ||
    fail "the page $page took $seconds s to render; the budget of a lesson page is $budget_seconds s."
  echo "Rendered $page in $seconds s"
done
echo "Rendered ${#lessons[@]} selected lesson page(s) alone; no site was built."
