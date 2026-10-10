# Plan 88: F18 Multi-agent scientific review

Issue #88. Short plan. Written by the implementer: no plan existed.

## Design

- `pbc.agents.review_lab` (next to `projectile_lab`): the lesson's code.
  - Two candidate steppers behind blind numbers 1 and 2. Both claim first
    order and bounded oscillator energy: 1 is the course's symplectic Euler,
    2 is `explicit_euler_as_symplectic` (right order, energy not bounded).
  - Three reviewers, each one run of the unchanged ADR 004 loop with its own
    allowlist over the F46 checks (`pbc.verification.checks`):
    physics (`check_limits`, `check_bounded_energy`), numerics
    (`check_clock`, `check_purity`, `check_convergence_order`), evidence
    (`reproduce_check` for any of the five checks in contract order, and
    `oscillator_error` for a convergence table). A tool takes the candidate
    number and returns the finding of rule 3 as numbers: `measured`,
    `tolerance`, `passed`.
  - `verdicts(reviewer, transcript)` reads checks and verdicts from the
    recomputed tool results, never from the model's text. `resolve` combines
    them: a candidate is rejected when any recomputed finding failed, and the
    checks no reviewer ran are listed as not covered. Disagreement is two
    reviewers whose own verdicts on a candidate differ.
  - Live entry point with `--record`, one fixture per reviewer.
- Lesson `agents-llm/03-three-reviewers`: three replays, the disagreement
  table, the resolution, the ADR 004 boundary restated.
- Fixtures: `replay-physics.json`, `replay-numerics.json`,
  `replay-evidence.json` next to the page.

## Decisions

- No new orchestration: the reviewers are three calls of `pbc.agents.run`
  with different system prompts and allowlists; the evidence reviewer does
  not read the others' text (a static task), so each fixture replays alone.
- The faulty gallery rule "nothing in src imports it" gets one named
  exception, `review_lab`, because the live run needs the faulty candidate;
  the test and the gallery's docstring say so.
- The numerics reviewer cannot see bounded energy and passes both candidates;
  that is the intended disagreement, and the resolution is computed from the
  recomputed findings.
- Provenance of the fixtures: as for #24, the model messages are by Claude
  (`claude-sonnet-5-5`) in a Claude Code session, the harness computed the
  results; no human has accepted this yet (see the handoff note).

## Acceptance

| Criterion | Evidence |
|---|---|
| Each reviewer's tool results recomputed by the build | `replay` in the lesson page and `tests/integration/test_review_replay.py` |
| Faulty variant flagged through a recomputed check | `test_the_faulty_candidate_is_rejected_by_a_recomputed_check` |
| ADR 004 boundary holds | `tests/unit/test_agents_boundary.py` scans the new module |
| No new framework | three `run` calls; `tests/unit/test_review_lab.py` |
