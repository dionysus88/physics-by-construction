#!/usr/bin/env bash

set -euo pipefail

# Gathers the verified base of a run that built the whole site (ADR 014).
#
# Usage: collect-base.sh <directory>
#
# Copies what the build left beside the site into <directory>: digests.json
# (the input digest of every lesson and the identity of the checks), pages.json
# (the checksum of every built page) and freeze/ (the executed results of the
# lessons). The workflow uploads the directory from a run on main, and a later
# job publishes it as the base once the job verify passed.
#
# It also writes provenance.json: the full ref, the commit and the run of the
# workflow run that collects it (GITHUB_REF, GITHUB_SHA, GITHUB_RUN_ID). The
# runs API names the branch of a run only by its short name, which a tag push
# fills with the tag's name; fetch-base.sh accepts a base only when this
# record names refs/heads/main and the run that the runs API checked.

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
site="${PBC_SOURCE_DIR:-$root/site}"

fail() {
  echo "Error: $*" >&2
  exit 1
}

[[ $# -eq 1 ]] || fail "usage: $0 <directory>"
out="$1"

[[ -f "$site/_digests.json" ]] || fail "$site/_digests.json is missing: the site was not built."
[[ -f "$site/_pages.json" ]] || fail "$site/_pages.json is missing: the site was not built."
[[ -d "$site/_freeze" ]] || fail "$site/_freeze is missing: no results were stored."
[[ -z "$(find "$site/_freeze" -type l -print -quit)" ]] || fail "$site/_freeze holds a link."
[[ "${GITHUB_REF:-}" == refs/* ]] || fail "GITHUB_REF is not set: only a workflow run collects a base."
[[ "${GITHUB_SHA:-}" =~ ^[0-9a-f]{40}$ ]] || fail "GITHUB_SHA is not set to a commit."
[[ "${GITHUB_RUN_ID:-}" =~ ^[0-9]+$ ]] || fail "GITHUB_RUN_ID is not set to a run id."
command -v jq >/dev/null 2>&1 || fail "jq is required."

rm -rf "$out"
mkdir -p "$out"
cp "$site/_digests.json" "$out/digests.json"
cp "$site/_pages.json" "$out/pages.json"
cp -R "$site/_freeze" "$out/freeze"
jq -n --arg ref "$GITHUB_REF" --arg sha "$GITHUB_SHA" --argjson run "$GITHUB_RUN_ID" \
  '{ref: $ref, sha: $sha, run_id: $run}' >"$out/provenance.json"
echo "Collected the base: $(find "$out/freeze" -type f | wc -l | tr -d ' ') stored files."
