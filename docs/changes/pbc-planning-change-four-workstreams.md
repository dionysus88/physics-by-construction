# Planning change: editorial voice, learner instructions, 20-minute PR budget, and verification simplification

**Date:** 2026-10-14  
**Type:** Combined planning change request  
**Owner decisions:** Introduce the proposed editorial pilot; remove all learner/contributor website-rebuilding instructions rather than relocate them; adopt 20 minutes as the current warm-cache typical-PR budget instead of 12; stop further implementation of F113 pending the planning decision and pursue a simpler verification architecture with evidence-based acceptance gates.

```bash
./scripts/start-planning.sh pbc-voice-learner-instructions-budget --change /absolute/path/to/pbc-voice-learner-instructions-budget.md --grill
```

This document requests planning changes, not immediate implementation or automatic merging. Reconcile against current main and active features before assigning work. Do not interrupt or duplicate an active feature. Use existing feature identifiers where appropriate; the F1–F3 labels in the editorial proposal below are local proposal labels, not repository feature numbers.

## Change 1 — Editorial voice and pedagogical storytelling

### Original editorial proposal

## Context

Physics by Construction currently prioritizes scientific correctness, reproducibility, and rigorous verification. These are essential strengths and must be preserved.

However, the lessons frequently read like technical specifications rather than engaging explanations written by a curious physicist.

The educational writing style should draw inspiration from the author's earlier technical articles at ataspinar.com, especially their curiosity-driven introductions, intuitive explanations, exploratory experiments, natural transitions, and personal interpretations of unexpected results.

## Objective

Develop a recognizable editorial voice for Physics by Construction that combines:

- The curiosity and accessibility of a personal technical blog.
- The mathematical rigor of a university-level physics textbook.
- The reproducibility and verification standards of the existing project.

The objective is better teaching and more engaging writing, not artificial optimization against AI-content detectors.

## Proposed Features

### F1 — Establish an Editorial Style Guide

Create editorial principles for lesson openings, intuition, mathematical derivations, computational experiments, results interpretation, transitions, and conclusions.

Include concrete before-and-after examples using existing Physics by Construction lessons and earlier ataspinar.com articles.

Identify recurring problems such as boilerplate introductions, excessive repetition, unnecessarily defensive wording, monotonous sentence structures, and conclusions that fail to interpret the significance of results.

Preserve all existing requirements concerning scientific accuracy, verification, assumptions, and reproducibility.

### F2 — Pilot the Style on Mechanics Lessons 01–05

Apply the new principles to the first five mechanics lessons.

Prefer targeted editorial changes over wholesale regeneration.

Improve the narrative while preserving technical content and the existing lesson contracts.

Review the lessons both individually and as a connected learning sequence.

Document successful changes, unsuccessful changes, and necessary adjustments to the style guide.

Require human approval of the pilot before expanding the changes to the remaining curriculum.

### F3 — Integrate Editorial Standards into Authoring and Review

Update the existing authoring guide and lesson template to incorporate the approved editorial principles.

Ensure future lesson implementations and reviews explicitly consider narrative quality and learner engagement.

Introduce a qualitative editorial review rubric with concrete evidence and actionable feedback.

Preserve the existing required lesson section identifiers and verification guarantees.

Avoid introducing an unnecessarily rigid narrative template or a mandatory additional agent.

## Acceptance Criteria

1. The project has a documented, reusable editorial style guide.
2. The guide includes examples demonstrating the desired changes.
3. Mechanics lessons 01–05 have undergone an editorial pilot.
4. All existing technical verification requirements continue to pass.
5. No scientific claim, result, formula, or verified artifact is silently changed merely for stylistic reasons.
6. The revised lessons retain meaningful differences in structure and narrative appropriate to their subjects.
7. The editorial review process identifies specific weaknesses rather than relying solely on numerical scores.
8. Future lessons inherit the approved writing principles through the normal authoring workflow.
9. Expansion beyond the pilot requires explicit review and approval.

## Non-goals

- Rewriting the entire curriculum in one feature.
- Making every lesson conversational or informal.
- Adding jokes or personal anecdotes artificially.
- Relaxing scientific standards.
- Imposing an identical narrative structure on every lesson.
- Replacing the existing verification pipeline.
- Adding extra AI agents without demonstrated benefit.

## Success Definition

Physics by Construction should retain the precision of a scientific textbook while gaining the curiosity, clarity, and recognizable authorial voice of an excellent technical educator.

## Change 2 — Remove website-rebuilding instructions and provide experiment execution instructions

### Owner decision

Remove instructions for rebuilding or previewing the website locally from all maintained documentation, including the public setup page, lesson footers, README, development/contributor documentation, authoring guidance, and templates that generate such instructions. Do not relocate them to contributor documentation.

Readers should be able to read lessons, run and modify Python experiments, and optionally check Lean proofs. None of these learner activities should require rebuilding the website.

### Required behavior

- Rewrite the public setup route around running experiments. Do not present the full `verify.sh` pipeline, Quarto rendering, or website preview as required learner setup.
- Replace learner-facing “Reproduce this” website-rendering instructions with “Run this experiment” instructions, or an equivalent clear label.
- Retain repository clone/download guidance, the required Python environment, exact experiment commands, relevant source paths, source revision information, and instructions to regenerate numerical results and figures without generating HTML.
- Where a lesson's runnable experiment currently exists only in `.qmd` cells, provide a runnable entry point or suitable notebook/script that uses the authoritative lesson implementation. Do not merely delete render commands and leave an incomplete workflow. Avoid duplicated scientific logic.
- Keep optional Lean setup and proof/exercise checking instructions. Clearly distinguish these from Python-only setup. Python learners must not need elan, Mathlib, browser-test installations, workflow tools, or LLM credentials unless their selected activity needs them.
- Distinguish replaying recorded agent experiments from live provider calls. Live calls require explicitly documented credentials and dependencies; ordinary reproduction must not unexpectedly call a paid model.
- Remove website-rendering and preview instructions from maintained non-public documentation too. Technical references to internal build behavior, script names, architecture, and verification evidence may remain where necessary; remove instructional walkthroughs for rebuilding the website.
- Keep internal website generation, publishing, Lean verification, scientific tests, and provenance mechanisms operational.

### Verification changes and boundaries

Existing requirements and tests currently tie learner instructions to rebuilding a page. Identify and explicitly supersede these contracts through the project's ADR process. Update setup-page tests, footer generation, authoring templates, and reproduction tests as required. Do not silently weaken scientific reproducibility: verify that the new experiment commands reproduce the intended numerical results and figures. Internal tests may still render pages and compare website artifacts; users no longer receive instructions to do so.

Historical decision records and completed feature records remain history. Mark superseded decisions and remove obsolete walkthroughs from current guides; do not falsify past acceptance evidence. Apply new wording to active requirements and future acceptance criteria, recording the narrow amendments needed for this change.

### Acceptance criteria

1. No maintained user, contributor, development, or authoring guide instructs a reader to rebuild or preview the website locally; the instructions have not been relocated.
2. Every affected lesson provides usable experiment execution instructions with no required HTML rendering.
3. Python-only setup does not require Lean or the full site verification environment.
4. Lean users can still check proofs and complete exercises locally without a website build.
5. The new experiment commands are exercised by meaningful verification and regenerate the relevant results/figures.
6. Internal build, publication, provenance, accessibility, and scientific correctness guarantees remain operational; any necessary contract amendment is explicit.
7. Relevant README text, setup pages, lesson generators, templates, current requirements, and tests are consistent.

## Change 3 — The budget of a typical pull request is 20 minutes

**Decision of the project owner (2026-10-14):** the wall-clock budget of a typical pull request with warm caches is **20 minutes**, in place of 12.

### Why

The owner-supplied measurements report that F61 (Issue #147) delivered selection against a verified base. Measured on 2026-10-14 (`docs/release-readiness.md`, “Selection against a base (F61)”): three pull requests that each change one lesson took 13 min 50 s to 14 min 43 s with twenty-two lessons, against 22 min 56 s and 25 min 00 s without a base. The remaining fixed costs include runner preparation of about 100 s in each of eight jobs, the full Lean build, and checks that are not per lesson. The owner accepts 20 minutes instead of paying for further workflow changes now. Retain 15 minutes as a non-blocking optimization target: a run above 15 but within 20 minutes meets the accepted budget. Record both the actual duration and whether the target was met.

The planning agent must reconcile these supplied facts with the current repository. Keep measurements as recorded; do not replace them with estimates.

### What changes

Only the budget number and its current statements change; no check is dropped and no guarantee changes:

- `docs/PROJECT_REQUIREMENTS.md`: the “Runtime and deployment constraints” paragraph stating “The budget of 12 minutes for a typical pull request holds at 110 lessons” (approximately line 503), and decision 30 (approximately line 800): change to 20 minutes.
- `docs/roadmap.md`: F61 and F113 blocks, the wave table, and statements of “within 12 minutes” referring to this same typical-PR budget (supplied approximate lines: 487, 1268, 3272, 3413, 3583, 3621, 5433). F61 acceptance criterion 1 becomes “three consecutive one-lesson pull requests finish within 20 minutes, recorded”.
- `docs/architecture.md`: the corresponding budget table (approximately lines 937 and 1052) and prose comparing with 12 minutes.
- ADR 003 decision 5 (typical-PR budget table row) and ADR 014 (context and decision 7): amend through a status line referencing the new decision; retain older wording as historical context.
- `docs/roadmap.md`, published-lesson inventory: the `agents-abm/01-particles-in-a-box` row reportedly still says F70 will set `slot: T0` and `course: thermodynamics`. F70 delivered on 2026-10-14 (PR #171, Issue #169 closed). Confirm the delivered state and update the row. Update current state counts from 22 to 25 where appropriate, accounting for T1, T2, and T3. Reconcile with current main rather than blindly replacing numbers.
- All locations are discovery hints; line numbers may have moved. Change anything quoting this same budget, not unrelated time limits.

For **Change 3 alone**, the **25-minute cold-cache budget** and **45-minute timeout per job** remain unchanged. Change 4 explicitly requests reconsideration of exceptional full-run timeouts; do not conflate a PR wall-clock budget with a per-job timeout.

### What stays

- F61 measurements in `docs/release-readiness.md` remain exactly as measured.
- This change does not accept unmeasured claims. Fork-PR retrieval of the verified base and the full run at 110 lessons (F113) remain to be measured.
- Fixed costs remain eligible for later optimization. A later owner decision may lower the budget again.
- The 20-minute budget has no automatic expiry or automatic return to 12 minutes. It is the current accepted budget until a later explicit decision changes it.

### Instructions to the planning agent

Change only the corresponding budget statements and associated current-state inventory corrections. Do not modify unrelated feature acceptance criteria under this budget change. Record the decision in a short ADR or an amendment of ADR 003 and ADR 014, following the repository convention. Coordinate with F113 if it is active; under Change 4 do not resume or merge it before the architecture decision. Do not restart or duplicate it.

### Acceptance criteria

1. All active statements of this typical-PR warm-cache budget consistently say 20 minutes.
2. The F61 criterion uses three consecutive one-lesson PRs within 20 minutes, with recorded evidence.
3. This budget adjustment itself does not change cold-cache budgets, job timeouts, checks, or verification guarantees; any such change must be justified and approved under Change 4.
4. Historical measurements and decisions are preserved with explicit supersession where needed.
5. Current published-lesson counts and the F70 mapping match verified repository state.
6. Unmeasured fork and 110-lesson cases remain explicitly outstanding.

## Change 4 — Simplify scientific verification, CI, and agent build obligations

### Owner direction and decision boundary

The owner wants to **pause F113 (Issue #150 / PR #175) and not merge it as currently designed**, pending a formal planning decision. This request is to **plan and critically review** a simpler F61-based architecture, **not** to immediately implement it or to declare selective publication equivalence already proven. Preserve the ability to inspect the F113 work until the replacement decision is accepted; resolve how to close or supersede its issue/PR through the normal process.

The preferred direction is that every published version has a complete, traceable verification basis **without requiring execution of every unchanged scientific lesson on every merge**. Treat this as a proposed revision to the current contract, not a claim of equivalence to running all lessons on HEAD.

This change is separate from Change 2: Change 2 removes **instructional walkthroughs for humans to rebuild the site** in maintained documentation. Change 4 reviews **agents' actual local verification obligations and the CI architecture**. Do not confuse either with removing the internal site-generation step required to publish the website.

### Why this is necessary

- F61 (Issue #147) selects changed lesson inputs against a trusted successful `main` base for PRs, but the existing `main` push workflow does not consume a base; it executes and checks the whole curriculum.
- F113 introduces lesson shards, artifacts and assembly to bound full-verification duration. Its complexity and value must be judged against the frequency of truly unavoidable full runs, not against a self-chosen 45-minute job timeout alone.
- The current full-verification pipeline may execute/render lessons multiple times. An independent review identified a potentially redundant complete preview-render test in addition to `check-determinism.sh`'s directory comparison. **Verify the actual commands, tested outputs and failure modes before deleting any check**.
- The current check identity potentially invalidates scientific execution results due to unrelated modifications (e.g. certain integration/e2e tests). Investigate whether independent execution and checker identities can safely reduce unnecessary full runs.
- Mandatory local full-site builds in agent implementation/review potentially repeat work that CI will perform. Replace blanket requirements with sufficient targeted checks while retaining CI build, publication and site validation.
- CI measurements to reconcile, not assume: three one-lesson selective PRs at 22 lessons took 13m50s–14m43s; complete `main` runs vary substantially with runner and cache state. A review reports a fast 32-lesson run with a roughly 21-minute build job, including approximately 11m13s lesson reproduction and separate expensive integration checks. All 125-lesson estimates are projections, not evidence.

### Requested architectural approach

**A. F61-based incremental verification on `main` (preferred, conditional)**

- Investigate extending trusted-base retrieval and selection to `push` on `main`, using a **previous successfully verified base** and content-addressed scientific results with proof of validity for the *current* commit. Never trust artifacts merely because they come from a previous PR, or because a former `main` run happened to be green.
- Detect changes to lesson inputs, shared dependencies, verification logic and the relevant environment. Where any required dependency or checker cannot be accounted for, **fail closed or run complete verification**; never silently reuse ambiguous results.
- Rebuild the publishable site and verify its actual output, navigation, provenance, rendered files and checksum record. Continue deploying **exactly the verified artifact**, never rebuilding independently in the deploy job.
- Explicitly analyze the shift from a base always originating in a full `main` run to a possible **chain of incremental `main` bases**. Define per-result provenance, validity, artifact retention/expiry, supersession and failure recovery; distinguish inherited scientific results from checks actually executed on the new commit.
- Include relevant execution-environment identity in reuse decisions. Evaluate runner image, pinned Python/uv/Quarto/Lean versions, fonts/system libraries, locale/timezone and CPU-dependent numerical behavior, distinguishing enforceable safeguards from difficult-to-detect drift.

**B. Exceptional full verification without default F113 sharding**

- Preserve a directly invocable full-verification path, and trigger it when safe reuse cannot be established or substantive shared scientific/runtime/toolchain changes demand it.
- A nightly, weekly or rotating full audit is **not authorized as a default requirement**. If the planning agent recommends one, identify the precise defect it detects, why event-driven checks cannot detect it, the cost and the residual risk; seek explicit owner approval.
- Evaluate a single-job full run with a higher timeout when necessary; do not promise performance at 125 lessons based only on measurements at 22–32 lessons. Assess real runner variability, job cancellation and recovery. Propose sharding only if demonstrably justified by measurements, reliability or an explicit full-run latency requirement.

**C. Remove unnecessary verification and local build obligations**

- Audit the full verification call graph to distinguish site render, determinism render, preview-byte comparison and lesson reproduction. If `test_a_second_build_gives_byte_identical_previews` duplicates `check-determinism.sh` with identical coverage, safely remove or consolidate the duplicate, with regression evidence. Do not remove independent scientific checks.
- Inspect `digest.check_identity` and split validity domains only where safe: changes affecting scientific execution, rendered output, or the verification rule itself need appropriate invalidation and independent tests. Avoid any optimization that permits outdated check logic to certify reused results.
- Audit agent instructions, plans, skills and verification scripts for blanket demands to rebuild the complete website during every implementation, review or feature finish. Remove unnecessary obligations, replacing them with targeted tests, lesson-specific execution/rendering where warranted, Lean checks for affected proofs, and CI-owned validation of the publishable site. Do not remove useful local checks for rendering/template/navigation changes.
- Investigate the integration-job critical path and whether its tests can be divided independently. Consider parallel lesson reproduction only after checking per-lesson execution budgets and resource contention; `pytest-xdist` is not an assumed solution.

### Required evidence and staged acceptance

1. **Before making `main` incremental:** demonstrate on the *same commit* that full and selective verification produce an equivalent publishable site (HTML, figures, scientific outputs, site metadata and checksums), allowing only explicitly documented provenance-specific differences. Report any cross-runner uncertainty; do not claim byte equivalence before evidence exists. A targeted comparison is preferred over three broad CI experiments.
2. Demonstrate safe fail-closed behavior when the base is missing, expired, invalid, stale or incompatible, and after changing shared inputs/check implementations. The full-run fallback must be able to finish under an explicitly approved and measured timeout.
3. Demonstrate that chained incremental bases preserve per-result origin, exact input/check identity and validation provenance, with no PR artifact or unverified run accepted as a trusted base.
4. Verify that the final deployment is the same build artifact validated by CI and that no second production build is introduced.
5. Confirm check redundancy by coverage before eliminating the extra preview render; preserve reproducibility and determinism coverage.
6. Inventory and remove only redundant agent-local *full-site build requirements*. Record which targeted tests replace them and which change types still require a local page/site render; ensure CI remains a functioning publication gate.
7. Measure the cost of one-lesson PRs and merges with warm caches, distinguish fixed preparation/integration cost from lesson-dependent time, and report a defensible full-run fallback at representative larger lesson counts. Keep the Change 3 **20-minute typical warm-cache PR budget**, **15-minute non-blocking target** and separate cold-cache target until explicitly amended.
8. Update current requirements and decision records explicitly, including requirement/decision 30, ADR 014, the relevant ADR 003 scheduling/verification statements, roadmap F61/F113 and the agent-workflow instructions. Preserve historical reasoning and measured evidence; do not rewrite history.
9. Present the owner with a short architectural decision record that states the **weaker/different guarantee** of trusted inherited results versus executing everything on the current commit, its scientific risks, and any minimum mitigation requiring approval.
10. No automatic scheduled audits, new sharding mechanism, or substantial infrastructure may be added without separate evidence and approval. The process for closing/superseding F113 must be explicit and non-destructive.

### Non-goals and guardrails

- No automatic implementation or merge of F113 or Change 4 through this request.
- Do not remove the internal CI site build, deployment verification, provenance, accessibility, scientific checks or the ability to perform complete verification.
- Do not confuse removal of human-facing site-building instructions (Change 2) with removing *internal* build steps or with removing targeted local checks by agents (Change 4).
- Do not assume a 125-lesson full-run duration or a full-run timeout without measurement; preserve a safe fallback if the proposed incremental path cannot be validated.
- Maintain changes as independently reviewable features; do not combine a risky CI redesign with the editorial pilot.

## Combined planning instructions

Treat the four changes as independently reviewable workstreams within one planning request. Identify existing features to amend and propose new features only where necessary. Preserve the editorial pilot's human approval gate. The budget/documentation work need not wait for approval to expand the editorial pilot. Enumerate affected requirements, ADRs, tests, templates, and active-feature conflicts before implementation. In particular, identify current F113 active work and do not merge/restart it or assume the replacement architecture has already been validated. Change 3 updates the PR budget; Change 4 independently revisits exceptional full-run timeouts and the evidence needed for site publication. Keep scientific claims and verified artifacts unchanged in purely editorial work; any code or verification changes belong to the appropriate scoped feature.
