#!/usr/bin/env bash

# The record of the last passed verification of a working tree.
# Source this file; do not execute it. It needs scripts/lib/fingerprint.sh.
#
# ./scripts/verify.sh writes the record after a run in which every check
# passed. It names the content that was verified by its fingerprint, so any
# change to a file that Git does not ignore makes it stale. A script that
# needs a passed verification can then skip a second run on identical content
# with './scripts/verify.sh --reuse'.
#
# The record is a working file that Git ignores. Without that ignore rule no
# record is written, because the file would become part of the fingerprint.
#
# A run inside an agent session counts like any other: the record says which
# content passed, whoever started the run. An agent could write the file
# instead of running the checks; that is accepted, because CI runs every check
# on a clean checkout before a merge.

VERIFICATION_RECORD=".agents/verification/passed"

# verification_recordable <root>
# Succeeds when a record can be kept for the working tree at <root>.
verification_recordable() {
  command -v git >/dev/null 2>&1 || return 1
  [[ "$(git -C "$1" rev-parse --show-toplevel 2>/dev/null)" == "$1" ]] || return 1
  git -C "$1" check-ignore -q "$VERIFICATION_RECORD" 2>/dev/null
}

# verification_field <root> <field>
# Prints the value of 'tree', 'workflow-tests', 'verified-at', or 'selection' in the
# record, or nothing when there is no record.
verification_field() {
  [[ -f "$1/$VERIFICATION_RECORD" ]] || return 0
  sed -n "s/^$2: //p" "$1/$VERIFICATION_RECORD" | head -n 1
}

# verification_write <root> <tree> <workflow-tests> [<selection>]
# <workflow-tests> is 'ran', 'skipped', or 'none'. <selection> is the summary
# line of a run with a base (ADR 014 decision 5); it names the base and says
# whether the run was selective or full, and why. Without it the run verified
# everything.
verification_write() {
  mkdir -p "$(dirname "$1/$VERIFICATION_RECORD")" &&
    printf 'tree: %s\nworkflow-tests: %s\nverified-at: %s\n' \
      "$2" "$3" "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" >"$1/$VERIFICATION_RECORD" &&
    { [[ -z "${4:-}" ]] || printf 'selection: %s\n' "$4" >>"$1/$VERIFICATION_RECORD"; }
}

# verification_forget <root>
verification_forget() {
  rm -f "$1/$VERIFICATION_RECORD"
}
