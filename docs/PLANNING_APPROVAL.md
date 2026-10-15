# Planning Approval

Status: Approved
Approved at: 2026-10-15T12:29:51Z
Planning branch: planning/pbc-planning-change-four-workstreams
Change request: docs/changes/pbc-planning-change-four-workstreams.md
Final review: round 10, PASS, by claude (sonnet)
Planning fingerprint: 60a0c5055926ab52be02110741fbc5f4bdf6f90c

Recorded by `scripts/finish-planning.sh`. The approval covers these planning
documents. A change to the description, the requirements, a change request, or the
roadmap makes it stale; the architecture and the ADRs may be updated by features
(`./scripts/finish-planning.sh --check`):

- `docs/PROJECT_DESCRIPTION.md`
- `docs/changes`
- `docs/PROJECT_REQUIREMENTS.md`
- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/decisions`

## Updates by merged work

These commits changed the architecture or the ADRs between approvals, each
under its own review. This approval covers the documents including them.

- 09a1050 F28 — Lesson format 2, the reference register, and the M1 pilot (Issue #52; review: round 2 (changes since round 1 only), PASS, by codex (gpt-6-luna); triage published on #52)
- 89647be F50 — Experimental dataset registry and feasibility gate (Issue #51; review: round 1, PASS WITH MINOR FINDINGS, by codex (gpt-6-luna); triage published on #51)
- 192ab2b F25 — Homepage narrative: Construct, Investigate, Verify (Issue #56; review: round 1, PASS, by codex (gpt-6-luna))
- 575441f F26 — Generated prerequisite graph (Issue #53; review: round 1, PASS WITH MINOR FINDINGS, by codex (gpt-6-luna); triage published on #53)
- 9dda90c F41 — Self-hosted search (Issue #55; review: round 1, PASS, by codex (gpt-6-luna))
- 51f4af7 F42 — Before you begin, and the glossary (Issue #58; review: round 1, PASS, by codex (gpt-6-luna))
- 49b227b F46 — Scientific code verification and debugging (Issue #62; review: round 3 (changes since round 2 only), PASS, by codex (gpt-6-luna); triage published on #62)
- 7ec0cd0 Leave code and printed output out of the search index
- e357f11 Measure the page payload reliably and raise its limit to 3 MB
- 7c97567 F13 — Self-check quizzes and browser-local progress (Issue #89; review: round 2 (changes since round 1 only), PASS, by codex (gpt-6-luna); triage published on #89)
- bcca871 F18 — Multi-agent scientific review (Issue #88; review: round 2 (changes since round 1 only), PASS, by codex (gpt-6-luna); triage published on #88)
- 704b905 F14 — Adaptive recommendations (Issue #94; review: round 1, PASS, by codex (gpt-6-luna))
- c8b7cbc F21 — Interactive Lean exercises (Issue #90; review: round 2 (changes since round 1 only), PASS, by codex (gpt-6-luna); triage published on #90)
- b0eb183 Raise the budget of the search index to 1 MB
- 3e41817 F51 — Experimental methods and visualization foundations (Issue #102; review: round 2 (changes since round 1 only), PASS, by codex (gpt-6-luna); triage published on #102)
- 787f1ad F51 follow-up — the dataset check of a figure cannot be bypassed (Issue #115; review: round 3 (changes since round 2 only), PASS, by codex (gpt-6-luna); triage published on #115)
- add23db F19 — Scientific evidence map (Issue #111; review: round 3 (changes since round 2 only), PASS, by codex (gpt-6-luna); triage published on #111)
- 2be53d4 Record the raised limit in the test and the architecture
- 48e95dc F43 — Science-first visualization components (Issue #121; review: round 2 (changes since round 1 only), PASS, by codex (gpt-6-luna); triage published on #121)
- 893320f F20 — Autonomous experimental design (Issue #128; review: round 1, PASS, by codex (gpt-6-luna))
- 42397f5 Run verification in parallel CI jobs behind one required check (F58, step 3) (Issue #130; review: round 4 (changes since round 3 only), PASS, by codex (gpt-6-astra); triage published on #130)
- d77d976 Record the measured run times of the parallel jobs (F58, step 4) (Issue #130)
- 8968711 Make the timeout and the measured state consistent across the records
- 7ae72f2 F62 — Eight courses and the reference curriculum (Issue #148; review: round 2 (changes since round 1 only), PASS, by codex (gpt-6-luna); triage published on #148)
- fd47641 F63 — Verified lesson previews (Issue #153; review: round 2 (changes since round 1 only), PASS, by codex (gpt-6-luna); triage published on #153)
- d9a2d9f CI workflow with a verified base artifact, and documentation (F61, steps 7 and 8 of 9, partial) (Issue #147; review: no independent review (low risk: partial delivery, steps 7 and 8 of 9, approved by the owner on 2026-10-14; independent review round 1 found only M1 (AC1, AC2, AC9 need the measurements of step 9) and M2 (AC4 and AC8 need the merged workflow and live evidence), both open by design, and no finding on the workflow itself; the complete feature gets the full independent review at the end))
- abef2a3 F70 — Thermodynamics and statistical physics: random walks, kinetic theory, entropy (T1, T2, T3) (Issue #169; review: round 5, PASS, by codex (gpt-6-luna); triage published on #169)
- 3121b52 F68 — Advanced mechanics: chaos, Lagrangian and Hamiltonian mechanics, resonance (M9 to M12) (Issue #168; review: round 6, PASS, by codex (gpt-6-luna); triage published on #168)
- 3743037 F64 — Learning Path redesign: course-first, compact, accessible (partial: criteria 6 and 8 are manual verifications) (Issue #167; review: no independent review (low risk: partial delivery of F64 (variant B of the owner, 2026-10-14): an independent review was run and its only open findings M1 (criterion 6, screen reader pass) and M2 (criterion 8, visual review) are the manual verifications the owner decided to keep open; M3 (what the reader builds) was fixed; the Issue stays open until both verifications are recorded on it))

## Review rounds

- Round 1: CHANGES REQUIRED, 4 finding(s), by codex (gpt-6-astra)
- Round 2: CHANGES REQUIRED, 7 finding(s), by claude (fable)
- Round 3: PASS WITH MINOR FINDINGS, 2 finding(s), by claude (fable)
- Round 4: PASS WITH MINOR FINDINGS, 5 finding(s), by claude (fable)
- Round 5: PASS WITH MINOR FINDINGS, 3 finding(s), by claude (fable)
- Round 6: PASS WITH MINOR FINDINGS, 2 finding(s), by claude (fable)
- Round 7: PASS WITH MINOR FINDINGS, 3 finding(s), by claude (fable)
- Round 8: PASS WITH MINOR FINDINGS, 5 finding(s), by claude (fable)
- Round 9: PASS WITH MINOR FINDINGS, 2 finding(s), by claude (sonnet)
- Round 10: PASS, 0 finding(s), by claude (sonnet)

## Escalations confirmed as resolved

- Round 7: MIN2 The approved requirements' decision 33 names "ADR 003's and ADR 014's reproduce checks" as the contracts to supersede, but the learner-facing reproduction contract lives in ADR 002, which is what ADR 016 supersedes
- Round 8: MIN1 Still open in the approved requirements (escalated in review 07): decision 33 names "ADR 003's and ADR 014's reproduce checks" as the contracts to supersede, but the learner-facing reproduction contract is ADR 002's consequence, which ADR 016 supersedes

## Findings that were not adopted

- Round 7, ESCALATE: MIN2 [minor] The approved requirements' decision 33 names "ADR 003's and ADR 014's reproduce checks" as the contracts to supersede, but the learner-facing reproduction contract lives in ADR 002, which is what ADR 016 supersedes. The finding is correct: PROJECT_REQUIREMENTS.md decision 33 (line 968) names "ADR 003's and ADR 014's reproduce checks", but ADR 003 holds no reproduction contract; the learner-facing "Reproduce this" contract is ADR 002's consequence and ADR 014 decision 9, which is what ADR 016's status supersedes and amends. The planning already points at the right records, so no architecture, roadmap, or ADR change resolves this. The misnaming is in the approved requirements, which the planner may not edit; the owner should amend decision 33 to read "ADR 002's and ADR 014's reproduce contracts" (or name ADR 002's consequence, the F39 setup-page rule, and ADR 014 decision 9) at the next requirements edit.
- Round 8, ESCALATE: MIN1 [minor] Still open in the approved requirements (escalated in review 07): decision 33 names "ADR 003's and ADR 014's reproduce checks" as the contracts to supersede, but the learner-facing reproduction contract is ADR 002's consequence, which ADR 016 supersedes. Confirmed unchanged: docs/PROJECT_REQUIREMENTS.md decision 33 (lines 967 to 971) still names "ADR 003's and ADR 014's reproduce checks", while ADR 003's decisions hold no learner reproduction contract; the contract ADR 016 supersedes is ADR 002's consequence, the F39 setup-page rule, and ADR 014 decision 9. The planning already supersedes the right records, so there is nothing for the planner to change, and the misnaming lives in the approved requirements, which the planner may not edit. The round-07 revision record already escalated this; it stays escalated for the owner to correct at the next requirements edit (suggested wording: "the reproduce contract of ADR 002, the F39 setup-page rule, and ADR 014 decision 9").
