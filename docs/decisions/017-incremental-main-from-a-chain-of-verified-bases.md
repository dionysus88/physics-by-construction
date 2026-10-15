# ADR 017: Incremental verification on `main` from a chain of verified bases, with an exceptional full run (proposed)

## Status

Proposed by the planning of the change cycle
`pbc-planning-change-four-workstreams` (requirements decision 35;
`docs/changes/pbc-planning-change-four-workstreams.md`, change 4).
**Not accepted by the approval of that planning.** This is the decision
record that decision 35 requires and that unresolved question 9 of the
requirements names: the project owner accepts or rejects it on the staged
evidence that F118 and F120 produce, after reading "The weaker guarantee"
below. Until the owner accepts it, every push to `main` executes and
checks every lesson
([ADR 014](014-verification-proportional-to-the-change.md) decision 4),
ADR 014 decision 11 (the lesson shards and the assembly, F113) is paused,
and nothing of this record is implemented. If accepted, this record
supersedes ADR 014 decision 11 and amends ADR 014 decisions 2, 4, 7, and
10 as stated below, and F121 delivers it. If rejected, this record is
marked rejected, and the owner decides between resuming F113 and the
raised full-run timeout of question 10.

**Decisions 7 and 8 are separable from decisions 1 to 6.** They do not
depend on incremental `main`: decision 7 (proportional local
verification) and decision 8 (removals by coverage only) rest on the
audit of F118 alone, as requirements decision 35 allows, and the owner
may accept them on F118's evidence before deciding on decisions 1 to 6,
which wait for F120's evidence as well. F119 delivers decisions 7 and 8
once accepted; F121 delivers decisions 1 to 6 and 9. A partial acceptance
is recorded in this status as a dated line that names the accepted
decisions and the evidence it rests on (the F118 record, by Issue and
pull request), as ADR 014's status records its staged delivery; the
remaining decisions stay proposed, and the heading of this record stays
"(proposed)" until the owner has decided on all of them. Decision 9
follows decisions 1 to 6.

**What decision 7 amends on acceptance.** Decision 7 changes the accepted
meaning of a local verification and of the finish and review gate of the
agent workflow, and names what it amends:
[ADR 012](012-parallel-verification-jobs-behind-one-required-check.md)
decision 1 ("a run with `--only` verifies nothing by itself and records
nothing; only a run without it is a verification, and that is what a
developer and the review workflow run locally"),
[ADR 005](005-workflow-self-tests-run-locally-on-workflow-changes.md)
decision 3 ("locally, the product checks always run"), and
[ADR 003](003-single-verification-entry-point-and-ci-budget.md)
decision 1 as ADR 005 decision 5 restates it ("every product check runs
locally on every run"). On acceptance of decision 7 those decisions read:
a recorded targeted run, with its tier, its base, and its selection, is
the finish and review evidence of an ordinary change; only a run without
options is a verification of the content; and CI stays the publication
gate that runs every check. The statuses of ADR 003, ADR 005, and ADR 012
say that this record, proposed, would amend them; on acceptance they
record the amendment (F119 acceptance criterion 7). Decision 8 amends
nothing of those records: it removes a check only with the new decision
and the coverage evidence that ADR 003 decision 6 requires.

Date: 2026-10-15

## Context

F61 (Issue #147, ADR 014) made a pull request execute and check the
lessons whose input digest changed, against the verified base of the latest
successful run on `main`. A push to `main` consumes no base: it executes
every lesson, checks every page, and publishes the next base after `verify`
passed. F113 (Issue #150) was to bound that full run with same-machine
lesson shards and an assembly; its pull request #175 was closed on
2026-10-15, its branch is preserved, and the owner paused it: its
complexity is to be judged against how often a full run is unavoidable,
not against a self-chosen timeout.

Measured, as recorded and not estimated:

| Run | Lessons | Wall clock | `build` | `integration` | Slowest `e2e` |
|---|---|---|---|---|---|
| Three one-lesson pull requests with a base, 2026-10-14 (`docs/release-readiness.md`) | 22 | 13 min 50 s to 14 min 43 s | 7 min 31 s to 7 min 57 s | 10 min 48 s to 14 min 29 s | 5 min 49 s to 6 min 03 s |
| Push to `main`, run 38545077253, 2026-10-14 | 22 | 21 min 59 s | 15 min 42 s | 13 min 58 s | 5 min 25 s |
| Push to `main`, run 38527223459, cold caches, 2026-10-14 | 22 | 29 min 46 s | 23 min 05 s | 13 min 41 s | 6 min 05 s |
| Push to `main`, run 38607388478, 2026-10-14 | 28 | 34 min 01 s | 26 min 57 s | 13 min 33 s | 6 min 32 s |
| Push to `main`, run 38621916706, 2026-10-14 | 32 | 40 min 48 s (`deploy` 1 min 43 s) | 31 min 15 s | 16 min 08 s | 7 min 30 s |
| Push to `main`, run 38639021950, 2026-10-14 | 32 | 37 min 27 s | 30 min 32 s | 15 min 28 s | 6 min 26 s |
| Push to `main`, run 38659296393, 2026-10-15 | 32 | 27 min 20 s | 21 min 07 s | 12 min 08 s | 5 min 48 s |
| Push to `main`, run 38687330455, 2026-10-15 | 32 | 35 min 08 s | 27 min 58 s | 15 min 52 s | 6 min 44 s |

The runs at 28 and 32 lessons were read from the Actions API by this
planning on 2026-10-15 (job start to job end); their cache state was not
read from the logs. At 32 lessons the `build` job of a full run takes 21 to
31 minutes against the 35-minute planning budget of ADR 014 decision 7 and
the 45-minute timeout; the variation between runs of the same size is
larger than the growth from 28 to 32 lessons. Every duration at 110 or
125 lessons is a projection until measured.

What the `build` job of a full run does with every lesson, read from
`scripts/verify.conf` and the files it names: the site build executes it;
the determinism check (`scripts/check-determinism.sh`) builds a copy of
the sources a second time and compares every file of the two builds; the
test `test_a_second_build_gives_byte_identical_previews` in
`tests/e2e/test_lessons.py` builds another copy through the same helper
(`tests/support/second_build.py`) and compares the preview images; and
the reproduction runs each lesson's commands in a fresh clone. On a full
run that is four executions of every lesson where ADR 014 counts three.
Whether the preview test's build duplicates the determinism build with
identical coverage is to be verified by F118 before anything is removed.
Other observations for the audit, not conclusions: the `integration` job
is the longest fixed job (10 min 48 s to 16 min 08 s) and holds tests of
many kinds in one check; the check identity of ADR 014 decision 10
includes `tests/integration`, so a change to any integration test makes
every pull request a full run; the agent workflow runs `./scripts/verify.sh`
in full on every feature finish and review
(`scripts/finish-feature.sh`, `scripts/review-feature.sh`, through
`--reuse`), which repeats what CI then performs.

## Decision (proposed)

1. **A push to `main` may inherit a lesson's executed results from the
   previous successfully verified base of `main`**, per lesson, only when
   all of the following hold, established on the current commit: the
   lesson's input digest equals the base's (ADR 014 decision 1); the
   check identity equals the base's (ADR 014 decision 10); the
   execution-environment identity of decision 3 equals the base's; the
   base's provenance is a `push` run on `refs/heads/main` of this
   repository whose `verify` concluded with success, established from the
   producing run's record (ADR 014 decision 2); and the base is complete
   and of the current format. Any lesson for which one condition cannot be
   established is executed on this commit. A shared input, a lesson
   without a digest, a differing identity, or an unreadable base executes
   every lesson, as ADR 014 decision 4 says. Nothing is reused because it
   came from a pull request, because a run was green, or because an
   artifact is recent or so named.
2. **Per-result provenance, and a chain of bases.** The base records, for
   every lesson, the origin of its results: the run and the commit that
   executed it, the environment identity of that run, and the depth of
   the chain since the last run that executed every lesson. An inherited
   result keeps its origin; a result executed in this run gets this run
   as its origin. The published site carries a provenance record beside
   its checksums (ADR 012 decision 6) that lists, per lesson, "executed
   in this run" or "inherited from run R at commit C"; the commit a page
   names stays the current commit (ADR 014 decision 9), because the page
   was rendered and checked on it. Whether the page itself tells the
   reader that its figures were executed on an earlier commit is a
   mitigation for the owner to require or decline (see "The weaker
   guarantee").
3. **The execution environment is part of the reuse decision.** The base
   records an environment identity: the runner image and its version
   label, the pinned Python, uv, Quarto, Lean, and Mathlib versions, the
   browser build, the fonts and system libraries the render depends on
   as the preparation records them, the locale and time zone, and the CPU
   model and instruction-set flags of the runner. F120 establishes which
   of these the hosted runners vary and which affect bytes; what is
   enforceable (pins, image label, locale) is required equal; what is
   observed to vary without affecting bytes is recorded; what affects
   bytes and cannot be pinned (a CPU-dependent last digit) is named as
   residual risk in this record before acceptance, with the evidence.
4. **What always executes on `main`.** Every check that is not per lesson
   (lint, format, unit tests, the Lean build in full, the lesson source
   checks, the dataset checks, the integration tests, the workflow
   self-tests); the render of every page from the current tree and commit
   (ADR 014 decision 9); the second build for determinism; the checks of
   every page whose bytes differ from the base's; the checks of the site
   as a whole; the verification of the built site's output, navigation,
   provenance record, files, and checksums. A lesson whose results are
   inherited is rendered from the store and is neither executed nor
   reproduced on this commit, and its experiment is not re-run: the
   experiment check of ADR 016 decision 4 follows the same selection as
   the page reproduction, so an inherited lesson's experiment evidence
   (its entry point regenerated the figures and numbers of its page) is
   inherited with its result from the run that executed it, under the
   conditions of decision 1, and is re-established when the lesson next
   executes. `deploy` publishes exactly the artifact CI verified and
   builds nothing (ADR 003 decision 3).
5. **Retention, expiry, supersession, and recovery.** A base expires with
   the retention of its artifact (30 days today) and when the digest
   format, the check identity, or the environment identity changes. A
   chain restarts from a run that executed every lesson; the maximum age
   and depth of a chain are set by F120 from the evidence and approved
   with this record (the proposal, to be confirmed or changed by the
   owner: no inherited result older than the artifact retention, which
   forces a complete execution at least once per retention period by
   event, not by schedule). A failed run on `main` publishes nothing and
   the previous base stands; a run whose base cannot be accepted executes
   everything and, if it passes, starts a new chain. Supersession is
   explicit: a base names the base it was derived from.
6. **An exceptional full run is directly invocable and is automatic when
   reuse cannot be established.** The same workflow runs without a base
   on request (a manual dispatch of the workflow that passes no base and
   is recorded as a full run) and whenever decision 1 cannot be
   established for the tree (a change of a shared input, of the checks,
   of the toolchain pins, or of the runner image). It is one `build` job
   with a timeout the owner approves from measurements (requirements,
   unresolved question 10), measured at the lesson count of the day and
   restated as the count grows; lesson shards are proposed only if
   measurements, reliability, or an explicit full-run latency requirement
   demonstrably justify them. No scheduled full audit is part of this
   record (unresolved question 11).
7. **Agents verify in proportion to their change, and an ordinary change
   builds no site locally.** Before a pull request an agent runs the
   **targeted run** of the change: the unit tests and the lesson source
   checks it touches, the experiment check of the lessons it changed
   (the entry point in a fresh clone against the figures and numbers the
   run computed, ADR 016 decision 4), the single-page render of each
   changed lesson page (the render of that page alone, as the page
   reproduction performs it today, never a build of the site), the Lean
   build for affected proofs, and the computation of the selection CI
   will make, from a base fetched read-only from the latest successful
   run on `main`, which reports the lessons CI will execute and whether
   CI will be a full run. The targeted run is an option of
   `./scripts/verify.sh` (F119 names it): it runs the checks that need no
   site build and the per-lesson checks for the selected lessons, it
   performs no site build, no determinism build, and no built-site check,
   and without an acceptable base it does not guess: it reports that CI
   will be a full run and the agent runs the full `./scripts/verify.sh`.
   A local site build is required only for the change types the
   selection cannot bound to lessons, and the selection says which:
   when it names a full run (a shared input of ADR 014 decision 4
   changed, or the check identity of ADR 014 decision 10 differs, which
   covers the verification scripts and their configuration, the
   templates, filters, assets, and shared site files, the site
   configuration, the curriculum file, the shared authoring code, and the
   Python pins), the agent runs the full `./scripts/verify.sh`; when the
   change alters what other pages display of a lesson (the front-matter
   fields that form the learning path and the headers of neighbouring
   pages, or a new lesson), the agent runs `./scripts/verify.sh --base`,
   which renders every page from the base's results, executes the
   selected lessons, and checks the pages whose bytes differ. The full
   run for the listed change types is the local site render that the
   requirements' runtime constraints permit (the change types the
   decision record of decision 35 lists) and is not the instructional
   rebuild or preview walkthrough that the requirements' non-goal and
   ADR 016 decision 1 remove from the maintained documentation; the
   guides name it as a verification tier, never as the way to read,
   run, or check a lesson. The finish
   and the review of a feature record which of the three runs the change
   type required, its pass, and, for the two runs that use a base, the
   base and the selection; the recorded pass of the targeted run is the
   finish evidence of an ordinary change, and no finish or review step
   builds the site for it. CI stays the publication gate that builds and
   validates the publishable site on every pull request and push, and
   `./scripts/verify.sh` without options still runs everything. **This
   decision amends, on acceptance, ADR 012 decision 1, ADR 005 decision
   3, and ADR 003 decision 1 as ADR 005 decision 5 restates it** (see
   "Status"): today a partial run verifies nothing and records nothing,
   a run without options is what a developer and the review workflow
   run locally, and every product check runs locally on every run;
   `scripts/finish-feature.sh` and `scripts/review-feature.sh` gate on
   `./scripts/verify.sh --reuse` accordingly. Under this decision a
   recorded targeted run, with its tier, base, and selection, is the
   finish and review evidence of an ordinary change, while only a run
   without options is a verification of the content, and CI runs every
   check on every pull request and push.
8. **Redundant checks are removed only with coverage evidence.** The
   preview build of `test_a_second_build_gives_byte_identical_previews`
   is consolidated into the determinism check only if F118 shows that the
   determinism comparison covers every byte the test compares under the
   same build conditions, with a regression test that a differing preview
   still fails `verify`. The check identity is split into validity domains
   only where a test shows each domain's inputs complete, and anything a
   split does not classify belongs to every domain (ADR 014 decision 10);
   no change may let older check logic certify reused results. The
   `integration` job is divided only without dropping a test. No
   independent scientific check is removed.
9. **F113 is superseded non-destructively on acceptance.** Issue #150 is
   closed with a comment that names this record and the decision; the
   branch `feature/150-bounded-full-verification-same` and the closed pull
   request #175 stay as the inspectable record; nothing of it is merged,
   restarted, or duplicated. If this record is rejected, Issue #150 stays
   open for the owner's decision.

## The weaker guarantee, for the owner

Today a published site means: every lesson was executed on the published
commit, on the CI runner of that run, twice, and reproduced in a fresh
clone on the same machine; every page was checked on that commit.

Under this record a published site means: every page was rendered and
checked on the published commit, from results that were executed either on
this commit or on an earlier commit of `main` whose inputs for that lesson
were byte-identical, under the same checks and the same recorded
environment, in a run whose `verify` passed. That is weaker, and different:

- **An input the digest does not follow.** The digest follows names and
  files (ADR 014, "Consequences"). A behavioural dependency the analysis
  cannot see (a file read through a composed path, a dependency on the
  clock, on the environment, or on another lesson's output) is caught
  today at the latest by the full run on `main`; under this record it is
  caught when that lesson next executes. The known cases make a lesson
  unfollowable and force its execution; the unknown case is the residual
  risk.
- **Environment drift the identity does not capture.** A runner image
  that updates a library outside the pins, or a CPU whose arithmetic
  differs in the last digit, could make what this runner would compute
  differ from the inherited bytes. The published page then shows the
  base's bytes, which were verified when executed, so the artifact stays
  internally consistent and reproducible at displayed precision, but it
  is no longer "computed on this commit on this runner". Decision 3 makes
  the detectable part of this explicit; the undetectable part is the
  residual risk F120 quantifies on the hosted runners.
- **A chain propagates an error in acceptance.** A base wrongly accepted
  once feeds every later version until a complete execution. Decision 1
  accepts a base only by the producing run's record, decision 5 bounds
  the chain's age, and decision 6 keeps a full run one dispatch away.
- **Non-determinism in unchanged lessons goes unobserved longer.** The
  determinism build compares the bytes of executed lessons; an inherited
  lesson is not executed twice on this commit, and its experiment check
  is not re-run either (decision 4). The reproducibility of a lesson, by
  page and by experiment, is re-established when it next executes.
- **Not equivalence.** A selective run on `main` that passes is not
  evidence that a full run on the same commit would pass. The evidence
  F120 produces (a full and a selective verification of the same commit
  producing the same publishable site, HTML, figures, outputs, metadata,
  and checksums, except the documented provenance fields) shows that the
  selective site is the site the full run would publish when the
  inherited results are valid; it does not show that they are valid, which
  is what decisions 1 to 3 establish per lesson.

Minimum mitigations that need the owner's approval with this record: the
scope of the environment identity (decision 3) and the residual risk it
leaves; the maximum age and depth of a chain (decision 5); whether the
provenance of inherited results is shown on the page or only in the site's
provenance record (decision 2); the timeout and the trigger of the
exceptional full run (decision 6, unresolved question 10); and whether a
scheduled complete execution is wanted at all (unresolved question 11:
the defect it would detect is exactly the first two risks above, which no
event-driven check can detect because no recorded input changed; its cost
is one complete execution per period; its residual risk is the interval
between executions; this record does not recommend it and the owner
decides).

## Alternatives considered

- **Lesson shards and an assembly on every push (F113, ADR 014 decision
  11).** Every published commit executes every lesson, bounded. Cost: one
  runner per shard plus an assembly on the longest path of every run and
  of every full-run pull request, a matrix the workflow derives, and the
  assembly's cross-machine equality of pages, which the first CI run did
  not get to measure. Paused by the owner; kept inspectable; the fallback
  if this record is rejected.
- **One `build` job with a raised timeout for full runs** (the fallback
  ADR 014 decision 11 names). Simplest and complete per commit; the
  measured 21 to 31 minutes at 32 lessons leave 14 minutes to the 45-minute
  timeout; the growth per lesson is not separable from runner variance in
  the measured runs, and at 110 lessons the duration is a projection.
  This is the interim gate F118 asks the owner to set (unresolved
  question 10) whatever happens to this record, and the exceptional full
  run of decision 6 is this job.
- **A scheduled full audit** (nightly, weekly, rotating). Not authorised
  by the owner as a default; analysed above for the owner's decision.
- **Path filters, a dropped check, or a check moved to a schedule.**
  Rejected, as in ADR 003 and ADR 014: the selection is by content, in
  the verification script, and fails closed.
- **Reuse results across the environment identity with a tolerance.**
  Rejected: a tolerance in a comparison of bytes hides the drift it is
  meant to detect (ADR 012 decision 4, ADR 014 decision 11).

## Consequences, if accepted

- A push to `main` that merges a one-lesson pull request costs about what
  the pull request cost, plus the publication of the base and the
  provenance record; a push that changes a shared input, the checks, the
  pins, or the runner image is a complete execution in one job under the
  approved timeout.
- The base gains an environment identity, per-lesson origins, and a
  derivation link; its format changes, which itself forces one complete
  execution.
- The site gains a provenance record that an auditor can read to see
  which results were executed on which commit; the completion audit F112
  reads it for its sampled reproductions.
- The requirements' "Runtime and deployment constraints" and decision 30
  describe this state once the owner accepts the record; the planner
  does not edit them, the acceptance does, through the owner's approval
  recorded in this status.
- F113's work stays as a reference for a bounded complete execution,
  should measurements at a larger lesson count ever justify shards.
