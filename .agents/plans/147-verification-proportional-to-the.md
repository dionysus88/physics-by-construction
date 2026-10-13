# Plan — Issue #147 (F61): verification proportional to the change

Status: first version, for approval before anything is built. The feature
changes the CI workflow, a workflow permission, and the meaning of the merge
gate on pull requests, which only the human may approve (Issue risk: High).

Source: Issue #147, ADR 014 (decisions 1 to 11), ADR 012, ADR 003.

## Current state (inspected)

- `scripts/verify.sh` runs the checks of `scripts/verify.conf` with groups
  and `--only`; no base option exists.
- `scripts/build-site.sh` renders every page with `freeze: false` (see
  `site/_quarto.yml`); no store is written.
- `scripts/check-determinism.sh` copies the sources and builds a second time.
- `.github/workflows/ci.yml` has jobs code, workflow, integration, build,
  e2e (matrix), verify, deploy; `contents: read` by default.
- The header and provenance (`reproduce_this` in `src/pbc/authoring/reproduce.py`,
  `build_commit()`) are executed cells, so a replayed store would carry the
  base's navigation and commit.

## Decisions the human must take before step 1

1. **Mechanism for decision 9.** Recommended: move the header and the
   provenance, excerpt and Lean helpers out of executed cells into a
   post-render step over marked regions (a Quarto post-render script).
   Alternative: write the store without the outputs of marked cells and run
   them on every build. The recommendation keeps the store free of context
   and makes the F113 assembly render without executing any cell.
2. **Base transport.** Recommended: artifacts of earlier runs, read with
   `actions: read`, because the provenance check of the producing run (event,
   head branch, conclusion, via the runs API) is explicit and testable. The
   default-branch cache is the alternative; if chosen, the plan must record
   its scoping argument (Issue, "In scope").
3. **Approval of the workflow change** (new read scope, base steps, the
   upload of the base from `main` only).

## Steps (each reviewed; verify.sh at the end of each)

1. **Input digest.** One function in the authoring package: hashes the lesson
   directory, the transitive imports of its executed cells under `src/pbc`,
   dataset samples and cards (via the name analysis in `tests/support/data_use.py`),
   displayed Lean modules, toolchain and manifest, Python pins, shared site
   files, and `src/pbc/authoring`. Returns no digest for a dynamic import, a
   composed path, a non-Python cell, or a read outside known locations.
   Tests: one per input kind changes the digest; each unfollowable case gives
   none. The build writes every lesson's digest beside the site.
2. **Identity of the checks** (decision 10): one digest over the files the
   Issue lists, written into the base.
3. **Selection in `./scripts/verify.sh`**: `--base <dir>`; computes the
   selection once, writes it to one file the checks read; missing, truncated,
   older-format or identity-less base, or any lesson without a digest, gives
   the full selection and a reason in the record; `--only` combines; the
   record names the base. No option: unchanged. Tests per Issue list.
4. **Store and build with a base**: default build writes the store (listed in
   `.gitignore`, rejected by the committed-artifact check); with a base,
   restore results, drop changed lessons' entries, time each executed lesson
   against 30 s; the determinism check starts from the same restored state.
5. **Regenerated context** per decision 1 above; template and helpers change
   once; tests: insertion, retitle, prerequisite/related links, commit
   provenance, on a fixture site with a base.
6. **Page checks and reproduction by selection**: compare the built site with
   the base checksums after normalising the build commit; reproduction only
   for lessons this run executed; never compare bytes with the base.
7. **Workflow**: a `main` push uploads the base after `verify` passed; a pull
   request fetches the latest base only from a `push` run on `refs/heads/main`
   with `verify` concluded `success`, read from the run record; fork and
   pull-request artifacts never accepted; `main` never receives a base; no
   job gains write permissions. Tests of the workflow file per Issue list.
8. **Documentation**: `docs/architecture.md`, `docs/deployment.md`,
   `docs/development.md`; status of ADR 014 recorded with the merge; ADR 002,
   003, 012 name it in their status (ADR edits need the human's approval).
9. **Measurement** (needs real CI): three consecutive one-lesson pull
   requests, render cost per page without execution, the full `main` run warm
   and cold, projection to 110 lessons and the lesson count where one job
   leaves 35 minutes; recorded in `docs/release-readiness.md`.

## Not doable in an unattended session

Steps 7 and 9 need GitHub runs and human approval; acceptance criteria 1, 2
(artifact inspection) and 9 cannot be met without them.
