# Plan: F119, remove redundant verification and blanket local build obligations (Issue #185)

Applies what the audit of F118 (`docs/verification-audit.md`, Issue #180,
pull request #182) justified, under ADR 017 decisions 7 and 8, which the
owner accepted on 2026-10-15. Nothing of incremental `main` (decisions 1 to
6 and 9), no timeout change, no change to `docs/roadmap.md` or
`docs/PROJECT_REQUIREMENTS.md`.

## Steps

1. **The regression test, then the third build.** A new test
   `tests/integration/test_determinism_check.py` runs
   `scripts/check-determinism.sh` with a fake `scripts/build-site.sh` that
   writes a fixture tree: two trees that differ in one byte of one file
   under `previews/`, a missing preview, and an extra one each fail the
   check and name the file, in a full run and in a selective run (the
   selection reaches the build); identical trees pass. Then
   `test_a_second_build_gives_byte_identical_previews` leaves
   `tests/e2e/test_lessons.py` and `tests/support/second_build.py` goes;
   the two tests of `tests/integration/test_store.py` that used the helper
   exercise the determinism check instead. A lesson executes three times
   in a full run (build 1, build 2, its reproduction), asserted by
   `tests/integration/test_verification_audit.py`; the audit records
   before (four) and after (three).
2. **The division of `integration`.** `scripts/verify.conf` declares the
   three parts of the audit as three checks in three groups:
   `check-tests-quarto` (`integration-quarto`: `test_store.py`,
   `test_context.py`, `test_home_build.py`, `test_site_build.py`),
   `check-tests-browser` (`integration-browser`: `test_site_checks.py`,
   `test_lesson_template.py`, `test_setup_page.py`, `test_browser_check.py`,
   `test_site_check_division.py`), and `check-tests-other`
   (`integration-other`: every other file, by `--ignore` of the named
   ones, so a new file runs without a change). `.github/workflows/ci.yml`
   runs them as three jobs with the preparation each part needs (Quarto
   only; the browser; the Lean packages), and `verify` needs them. The F58
   tests of the division (`test_site_check_division.py`,
   `test_ci_workflow.py`) are extended: every test of `tests/integration`
   runs exactly once, and the named files exist.
3. **The check identity.** `tests/integration` leaves `CHECK_DIRECTORIES`
   in `src/pbc/authoring/digest.py`: it is the one input the audit showed
   to be in the domain of no reused result (no check a base reduces reads
   it; `check-tests-*` are its only consumers and are never reduced by a
   base). The identity stays one digest over the inputs of every domain
   (S, R, V, B), so a change to any of them, and to an input that no
   classification names, invalidates every reused result. Tests: the
   completeness test of the split (no file of `tests/e2e`, `tests/support`,
   `scripts`, `src`, or `.github` reads, imports, or executes a file of
   `tests/integration`; its only consumers in `scripts/verify.conf` are
   the `check-tests-*` checks, in groups a base never reduces); a change to
   an unclassified input (a new file under `tests/support`) gives a full
   run; a change to an input of each domain gives a full run ("no reused
   result is certified by older check logic"); a change to
   `tests/integration` keeps the selection selective.
4. **`scripts/fetch-base.sh` on a developer's machine.** Without
   `GITHUB_REPOSITORY` the repository comes from `gh repo view`; without
   `GH_TOKEN` the script uses the login of `gh` and reports "No base: gh is
   not logged in" when there is none. CI, which sets both, is unchanged.
   Tests in `tests/integration/test_fetch_base.py` with the fake `gh`.
5. **The targeted run: `./scripts/verify.sh --targeted`.** The three tiers:
   - `--targeted` (an ordinary change): fetches the base into
     `.agents/verification/base` (or takes `--base <directory>`), computes
     the selection CI will make and reports it, and runs the checks of the
     groups the reserved entry `targeted: <groups>` of `scripts/verify.conf`
     names (`default` and `code`: lint, format, unit tests, lesson source
     checks, dataset checks, the docs and workflow structure checks, the
     workflow self-tests when a workflow file changed) and
     `lesson-pages`, the single-page render of each selected lesson in a
     clone of the working tree (`scripts/check-lesson-pages.sh`, with the
     Lean build for a lesson that displays Lean and for a change under
     `lean/`). It performs no site build, no determinism build, and no
     built-site check. It does not guess: without an acceptable base it
     reports "No base: ... CI will run everything" and ends with status 1;
     when the selection names a full run it reports "CI will run
     everything: <reason>" and names the full run; when a selected lesson is
     not in the base (a new lesson) it names `--base`. A pass is recorded
     with its tier, the base (the run that produced it), and the selection.
     A project whose `scripts/verify.conf` declares no `targeted:` entry has
     one tier: `--targeted` runs every check.
   - `--base [<directory>]` (a change that alters what other pages display
     of a lesson): as today, with the base fetched when no directory is
     given; recorded with the tier `base`.
   - `./scripts/verify.sh` without options: unchanged; recorded with the
     tier `full`.
   - `--reuse` reuses a recorded full pass as today; `--reuse --targeted`
     reuses a recorded pass of any tier, otherwise runs the targeted run.
   Tests: `tests/integration/test_selection.py` (the real selection module,
   a project with echo checks and a fake `fetch-base.sh`) for each tier's
   exact checks, that the targeted run builds no site, the refusals, and
   the record; `tests/verify-test.sh` for the reserved entry and the
   fallback; `tests/integration/test_lesson_pages_check.py` for the render
   script (nothing to do without a targeted selection; a selected lesson
   renders in a clone and no site is built; a broken page fails and is
   named); a test in `test_verification_audit.py` that the groups of the
   targeted entry hold no check that builds or reads the site.
   The experiment check (ADR 016 decision 4) joins `lesson-pages` when
   F117 delivers the entry points; no lesson declares one today.
6. **The agent workflow on the tiers.** `scripts/finish-feature.sh`,
   `scripts/review-feature.sh`, and `scripts/apply-triage.sh` gate on
   `./scripts/verify.sh --reuse --targeted` and record the tier, its pass,
   the base, and the selection (the commit message's "Verification" lines,
   which the pull request carries). `scripts/run-feature.sh` repeats a
   failed verification with the same tier. `scripts/triage-review.sh`
   writes the tier rule into follow-up Issues. `AGENTS.md` ("Definition of
   Done"), `.agents/prompts/implementer.md`, and
   `.agents/prompts/triage-implementer.md` state the three tiers and the
   change types of each. The self-tests of the scripts cover the recorded
   lines. Template-synced files are changed in the smallest way (see
   "For the pull request").
7. **Documentation and ADR statuses.** `docs/development.md`
   ("Verification": the three tiers, the division of `integration`, no
   preview walkthrough), `docs/authoring.md` ("Check it": the targeted run
   and the single-page render), `docs/workflow.md` (the `verify.sh`
   column), `docs/deployment.md` (the jobs), `docs/project-map.md` (the new
   script), `docs/architecture.md` ("Inside one verification run", "CI
   pipeline and time budget", the section under review, invariant I8,
   "Repository state"), `docs/verification-audit.md` (what F119 applied),
   and the statuses of ADR 003, ADR 005, ADR 012 (the amendment by ADR 017
   decision 7 on acceptance), ADR 014 (what was applied to decisions 3, 8,
   10, 11's count), ADR 017 (applied by F119).
8. **Measurement, after the merge.** Three consecutive one-lesson pull
   requests against the 20-minute budget with the 15-minute target (ADR
   015) and one full run on `main`, recorded in `docs/release-readiness.md`
   with the critical path of `integration` before and after. This step
   needs the merged workflow and cannot run in the implementer's session.
9. Records: handoff, completion, summary; the verification last.

## For the pull request (the owner's approval)

Everything here is High: the CI workflow, the protected script
`scripts/verify.sh`, the ADRs, the prompts, and the meaning of a feature's
local verification change.

**Security and coverage summary.**

- Permissions of `ci.yml` are unchanged: `contents: read` at the top,
  `actions: read` only on `build` and `e2e`, writes only on `deploy`. The
  three `integration-*` jobs have no `permissions` block and run
  `./scripts/verify.sh --all --only <group>` like the job they replace;
  `verify` needs them. No path filter, no check declared in the workflow.
- No scientific check leaves `scripts/verify.conf`. Removed: one test,
  `test_a_second_build_gives_byte_identical_previews`, whose comparison
  (the names and bytes of `previews/`) the determinism check makes over the
  whole tree under the same build conditions; the regression test shows a
  differing, missing, or extra preview still fails `verify`. Executions
  per lesson in a full run: four before, three after.
- The check identity loses `tests/integration` and nothing else; a test
  shows that no check a base reduces reads it. Every other input, and any
  input a classification does not name, still invalidates every reused
  result.
- The targeted run is a local tier only. CI builds and validates the site
  on every pull request and push as before; `./scripts/verify.sh` without
  options runs everything; a targeted run never records a pass that
  `--reuse` without `--targeted` would take for a full one.
- `scripts/fetch-base.sh` accepts the same provenance (a `push` run on
  `main` of this repository whose `verify` succeeded, the digest of the
  download, a safe archive) on a developer's machine; a missing login or
  repository gives "No base", never a wrong selection.

**Template-synced files changed** (`paths:` of `.agents/template.conf`;
carry these to the template repository, or `sync-template.sh` brings the
old behaviour back): `AGENTS.md`, `.agents/prompts/implementer.md`,
`.agents/prompts/triage-implementer.md`, `scripts/verify.sh`,
`scripts/finish-feature.sh`, `scripts/review-feature.sh`,
`scripts/apply-triage.sh`, `scripts/triage-review.sh`,
`scripts/run-feature.sh`, `scripts/lib/verification.sh`,
`scripts/verify-workflow.conf`, `tests/verify-test.sh`,
`tests/finish-feature-test.sh`, `tests/review-feature-test.sh`,
`docs/development.md`, `docs/workflow.md`, `docs/project-map.md`,
`.github/workflows/ci.yml`. Project-only files (`scripts/verify.conf`,
`scripts/fetch-base.sh`, `scripts/check-lesson-pages.sh`, the Python
package, the pytest tests, `docs/architecture.md`, the ADRs) are not
synced.
