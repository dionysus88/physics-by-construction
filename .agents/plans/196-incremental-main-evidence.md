# Plan: F120, incremental `main`: the staged evidence and the decision record (Issue #196)

Produces the evidence that ADR 017 (proposed) needs before the owner decides
question 9 of the requirements, without changing what `main` executes:
`.github/workflows/ci.yml`, `scripts/verify.sh`, `scripts/verify.conf`, and
the scripts that make and take the base are not changed. The evidence is
recorded in `docs/incremental-main-evidence.md`, the chain's provenance is
specified and prototyped in `src/pbc/authoring/provenance.py` with its
tests, ADR 017 is completed with the evidence and the mitigations with
values, and the owner is asked on the Issue. The owner's decision, and its
recording in the statuses of ADR 017 and ADR 014, come after this plan.

## Goal

Acceptance criteria 1 to 7 of Issue #196, in its words:

1. The same-commit comparison is recorded with the commit, both runs or
   builds, every differing file with its classification, and the statement
   that it shows the selective site equals the full site when the inherited
   results are valid, not that they are valid.
2. Each fail-closed case is demonstrated by a named test or a recorded run,
   including a changed shared input, a changed check, and a changed
   environment identity; the full-run fallback finished under the approved
   timeout in a recorded run.
3. The chain's provenance format is specified and prototyped with the tests
   named in the Issue; no pull request artifact or unverified run is
   accepted as a base (tests).
4. The one-production-build evidence names the tests.
5. The environment identity record lists what varied across the named runs,
   the byte comparison across runners for identical inputs with its result,
   and the classification into enforceable, recorded, and residual.
6. The costs are recorded with measurements and labelled projections,
   against the 20-minute budget and the 15-minute target.
7. ADR 017 carries the evidence and the mitigations with values and was
   presented to the owner; the owner's decision is recorded in its status
   and in ADR 014's, with the next step named; the proposal for Issue #150
   is on that Issue.

## Current state, found on 2026-10-16 at `4894c4b` (the base of the branch)

- F61 is delivered (ADR 014 decisions 1 to 10 accepted 2026-10-15): a pull
  request selects against the base of the latest successful push run on
  `main` (`scripts/fetch-base.sh`, `pbc.authoring.selection`,
  `pbc.authoring.digest`), a push to `main` never receives a base and
  publishes one after `verify` passed (`scripts/collect-base.sh`, the jobs
  `build` and `base` of `ci.yml`). The base is `digests.json` (format 1, the
  check identity, the input digest of every lesson), `pages.json` (the
  checksum of every built file with the commit normalised), and `freeze/`.
- F118 and F119 are merged (ADR 017 decisions 7 and 8 accepted and applied):
  the full run executes a lesson three times, `integration` runs in three
  parts, `tests/integration` left the check identity, the targeted run
  exists. The interim full-run gate is a 60-minute `build` timeout approved
  for up to 45 lessons (ADR 014 status, 2026-10-15).
- The F61 suites already cover most fail-closed cases:
  `tests/integration/test_fetch_base.py` (a pull request run, a fork, a
  failed run, a run without `verify`, an expired artifact, a differing
  archive digest, an archive with a link or an unsafe path),
  `tests/integration/test_selection.py` (a base that is missing, truncated,
  of another format, without an identity, with a damaged store; a changed
  shared input; a changed check of each validity domain; an input no
  classification names; a lesson without a digest), the `verify.sh` tests
  of `tests/verify-test.sh`. The environment identity does not exist, so no
  test covers it: the prototype adds it.
- The base artifacts of eleven push runs on `main` from 2026-10-14 to
  2026-10-16 are retained (30 days), and each of those runs executed every
  lesson: they are the source of the byte comparison across runners for
  identical inputs. Their build logs record the runner image and its
  version, the runner version, and the provisioner version; they record no
  CPU model, flags, locale, or time zone.
- The run on `main` of the branch's base commit `4894c4b` (run 38876222290)
  started while this plan was written. Its site, its record, and its base
  are the full-verification side of the same-commit comparison; the
  selective side is a local `./scripts/verify.sh --base` on the same commit
  against that base.
- No plan existed when the feature was started; this plan is written by the
  implementer, as the plans of F61, F118, and F119 were.

## Affected components

- New: `docs/incremental-main-evidence.md` (the evidence record),
  `src/pbc/authoring/provenance.py` (the chain's provenance: format,
  acceptance, origins, site record), `tests/integration/test_provenance.py`.
- Changed: `docs/decisions/017-incremental-main-from-a-chain-of-verified-bases.md`
  (the evidence, the residual risks quantified, the mitigations with
  values, what is not shown; the status stays "proposed" until the owner
  decides), `docs/architecture.md` (the paragraph under "Verification
  simplification under review" names the evidence and the prototype),
  `docs/project-map.md` (the new document), `docs/release-readiness.md`
  (a pointer to the measurements of F120).
- Not changed: `ci.yml`, `scripts/verify.sh`, `scripts/verify.conf`,
  `scripts/fetch-base.sh`, `scripts/collect-base.sh`, `pbc.authoring.selection`,
  `pbc.authoring.digest`, ADR 014 (the owner records the decision there).
- Adding a module under `src/pbc/authoring` changes the input digest of
  every lesson (it is a shared input by design), so the pull request of
  this feature is a full run in CI and the local verification of the
  change is the full `./scripts/verify.sh`.

## Constraints

- ADR 017 (proposed) decisions 1 to 6 and 9 are not accepted; nothing of
  them runs on `main`. ADR 014 decision 4 stands: every push to `main`
  executes every lesson. The prototype is code and tests only; no script or
  workflow calls it.
- The owner's sequencing on the Issue (2026-10-16): the feature may be
  implemented and reviewed now but is not merged before the three one-lesson
  measurement pull requests of F119 and F61 have merged, and not without the
  owner's explicit word because it touches an ADR.
- A temporary workflow change is avoided altogether: the comparison uses
  the artifacts of CI and a local run.
- The implementer posts on Issue #196 and Issue #150 because the Issue's
  criterion 7 requires it (the precedent is F118 on Issue #180).

## Risk

Medium, as the Issue says: evidence, a prototype that nothing calls, tests,
and documents. No workflow change was needed.

## Steps

1. **The byte comparison across runners (criterion 5).** Download the
   `verification-base` artifact of every retained push run on `main`,
   group the runs whose lesson digests are equal, and compare the stored
   results of every such lesson byte for byte, with the random cell
   identifiers of the store normalised and counted apart; then compare the
   page records (`pages.json`, commit normalised) of the same runs to see
   which published files differ. Read the build logs of the named runs for
   what the runner setup records. Classify every item of ADR 017 decision 3
   into enforceable, recorded, and residual, with the evidence.
2. **The same-commit comparison (criterion 1).** On `4894c4b`: the full
   verification is run 38876222290 on `main` (its `github-pages` artifact,
   its `built-site-record`, its `verification-base`); the selective
   verification is `./scripts/verify.sh --base <that base>` on the same
   commit on the developer's machine, which inherits every lesson (every
   digest equals the base's) and renders every page. Compare the two sites
   file by file: HTML, figures, executed outputs, site metadata, the search
   index, the provenance region, and the checksums; list every differing
   file with its classification; report the cross-runner uncertainty (the
   render happened on another machine) instead of assuming it away. A
   second comparison against the base of the previous run (38868679531),
   which executes one lesson locally, shows what a locally executed lesson
   adds; it is recorded if it finishes in the session.
3. **The fail-closed table (criterion 2).** For each case of the Issue the
   test that demonstrates it, by file and name, or the recorded run; the
   environment identity by the tests of the prototype (step 4); the
   full-run fallback by the recorded run 38534115654 (the base rejected
   because the checks changed; every lesson executed) and the full runs on
   `main` under the 60-minute timeout (38868679531: 20 min 50 s;
   38876222290: 25 min 52 s).
4. **The chain's provenance (criterion 3).** Specify the format
   (`provenance.json` beside `digests.json` and `pages.json`): the run
   that made the base (run, commit, event, branch, repository, `verify`
   conclusion), the environment identity, the derivation link to the
   previous base (run and digest of its provenance record), the chain
   (depth since the last complete execution, the run that started it),
   and per lesson the origin of its results (run, commit, environment
   identity, depth). Prototype it in `src/pbc/authoring/provenance.py`:
   `environment_identity()` from the pins and the recorded runner facts,
   `accept()` (a base is accepted only from a `push` run on `main` of this
   repository whose `verify` succeeded, of the current format, with an
   equal environment identity, a complete and consistent record for
   exactly the base's lessons whose derivation link matches the record of
   the base it was derived from (triage of review 03, M1), and a chain
   within the proposed bounds),
   `derive()` (the provenance of the next base from the selection and the
   accepted previous base: inherited lessons keep their origin, executed
   lessons get this run, depth and age bounded), and `site_record()` (per
   lesson "executed in this run" or "inherited from run R at commit C").
   Tests in `tests/integration/test_provenance.py`: a pull request
   artifact, an unverified run, a failed run, a run of another repository,
   and a base of another format are rejected; a differing environment
   identity is rejected (fails closed); an inherited result keeps its
   origin through a chain of at least three bases; a chain beyond the
   maximum depth or age is rejected and the next run starts a new chain; a
   complete execution resets the depth; the site record names the origin
   of every lesson; the module is a command on the pinned Python.
5. **One production build (criterion 4).** Name the F58 and F61 tests:
   `tests/integration/test_ci_workflow.py::test_deploy_job_publishes_the_verified_artifact_and_builds_nothing`,
   `::test_the_site_is_built_in_one_job_and_uploaded_with_its_record`,
   `::test_a_job_that_checks_the_built_site_checks_the_one_that_was_built`,
   `::test_the_base_is_published_by_main_only_after_verify_passed`, and
   `tests/integration/test_ci_scripts.py::test_a_job_gets_the_site_that_was_built`,
   `::test_a_site_that_is_not_the_built_one_stops_the_job`,
   `::test_an_incomplete_hand_over_stops_the_job`.
6. **Costs (criterion 6).** From the Actions API: the one-lesson pull
   request after F119 (run 38874606240, 2026-10-16), the three one-lesson
   pull requests of F61, the full runs on `main` of F118 and of 2026-10-16;
   fixed and lesson-dependent cost separated; the one-lesson merge under
   incremental `main` estimated from them (labelled); the full-run fallback
   at 45, 64, and 110 lessons from F118's bounds (labelled).
7. **The decision record (criterion 7).** ADR 017: a section "Evidence
   (F120)" that summarises each item with its pointer, the residual risks
   quantified from step 1 and 2, the mitigations proposed with values
   (environment identity scope; chain maximum age 30 days and depth; the
   provenance on the page or in the record; the trigger and the 60-minute
   timeout of the exceptional full run), the explicit statement of what is
   not shown, and the analysis of a scheduled audit without a
   recommendation; a dated status line that the evidence was presented.
   Post the presentation on Issue #196 and the proposal for Issue #150 on
   Issue #150. The owner's decision and its recording in the statuses of
   ADR 017 and ADR 014 remain after this plan.
8. **Documents.** `docs/architecture.md`, `docs/project-map.md`,
   `docs/release-readiness.md` as listed above; the completion record, the
   handoff note, and the summary.

## Verification

- Unit and integration: `uv run --locked pytest tests/integration/test_provenance.py`
  while working; the lesson checks and the document checks through the
  tier at the end.
- The tier: the targeted run reports that CI will run everything (a module
  was added under `src/pbc/authoring`), so the last thing that touches the
  repository is the full `./scripts/verify.sh`.

## Context

Base commit `4894c4b` (merge of pull request #195), branch
`feature/196-incremental-main-evidence`, 2026-10-16.

## Open questions

- The owner's decision on ADR 017 decisions 1 to 6 and 9 (question 9), the
  mitigations' values, the scheduled audit (question 11), and the closure of
  Issue #150 (question 12): asked on the Issues by step 7; not for the
  implementer.

## Next action

Steps 1 to 8 are done (2026-10-16); the second comparison of step 2 was
not made in the session. What remains is the owner's decision on the
Issue and its recording in the statuses of ADR 017 and ADR 014 (step 7,
second half).
