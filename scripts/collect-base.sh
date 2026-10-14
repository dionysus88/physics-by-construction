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

rm -rf "$out"
mkdir -p "$out"
cp "$site/_digests.json" "$out/digests.json"
cp "$site/_pages.json" "$out/pages.json"
cp -R "$site/_freeze" "$out/freeze"
echo "Collected the base: $(find "$out/freeze" -type f | wc -l | tr -d ' ') stored files."
