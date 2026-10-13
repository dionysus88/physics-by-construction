# Planning Approval

Status: Approved
Approved at: 2026-10-13T04:47:03Z
Planning branch: planning/final-curriculum
Change request: docs/changes/final-curriculum.md
Final review: round 9, PASS, by claude (sonnet)
Planning fingerprint: 0b00c7bbf1ff0bf55156c2549c2932a074be647a

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

## Review rounds

- Round 1: CHANGES REQUIRED, 5 finding(s), by codex (gpt-6-astra)
- Round 2: CHANGES REQUIRED, 3 finding(s), by codex (gpt-6-astra)
- Round 3: CHANGES REQUIRED, 8 finding(s), by claude (fable)
- Round 4: CHANGES REQUIRED, 10 finding(s), by claude (fable)
- Round 5: PASS WITH MINOR FINDINGS, 5 finding(s), by claude (fable)
- Round 6: PASS WITH MINOR FINDINGS, 4 finding(s), by claude (fable)
- Round 7: PASS WITH MINOR FINDINGS, 1 finding(s), by claude (sonnet)
- Round 8: PASS WITH MINOR FINDINGS, 1 finding(s), by claude (sonnet)
- Round 9: PASS, 0 finding(s), by claude (sonnet)

## Escalations confirmed as resolved

- Round 4: MIN4 Concerns the approved requirements: 'no feature equals one slot' contradicts decision 31 and the roadmap's many one-slot features
- Round 5: S1 Concerns the approved requirements: the 'no feature equals one slot' sentence remains in the approved text; the owner's ruling is recorded only in the roadmap

## Findings that were not adopted

- Round 4, ESCALATE: MIN4 [minor] Concerns the approved requirements: 'no feature equals one slot' contradicts decision 31 and the roadmap's many one-slot features. Confirmed: docs/PROJECT_REQUIREMENTS.md line 193 ('no feature equals one slot') and decision 31 at line 806 ('no rule that a slot is a feature') disagree, and the change request (section 2, point 10: 'No rule that each curriculum slot must equal one feature') shows decision 31 is the intended meaning. The roadmap already follows decision 31 and the change request: F74, F80, F82 to F88, F97, F100, F102 to F108, F110, and F111 each deliver one slot, and the roadmap's definition-of-done block cites decision 31. Resolving the disagreement requires correcting the later-phases sentence of the approved requirements, which the planner may not edit, so the human must decide: either amend line 193 to 'no rule that a feature equals one slot' through the requirements process, or confirm that decision 31 governs and the roadmap's one-slot features stand. A note in the roadmap alone would not remove the contradiction inside the approved requirements, which is why this is escalated rather than adopted; once the human rules, the planner adds the roadmap note citing decision 31 if asked.
- Round 5, ESCALATE: S1 [suggestion] Concerns the approved requirements: the 'no feature equals one slot' sentence remains in the approved text; the owner's ruling is recorded only in the roadmap. The finding is correct that the approved requirements still read 'no feature equals one slot' at line 193 against decision 31 at line 806, and that the owner's ruling of 2026-10-13 is recorded only in the roadmap's Phase 4 preamble (lines 3181 to 3188). The reviewer asks for no planning change, and none is needed: the planning follows decision 31 with a traceable note. The only remaining action is to replace the line-193 sentence with the wording of decision 31, which is a change to the approved requirements that the planner may not make. This is the same item the owner already settled as MIN4 of round 4; no new decision is requested, only the requirements edit at the next Project Grill cycle, which the roadmap note already schedules.
