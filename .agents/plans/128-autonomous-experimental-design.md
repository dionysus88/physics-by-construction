# Plan: Issue #128, F20 — Autonomous experimental design

- Issue: #128 (source: `docs/roadmap.md`, F20)
- Branch: `feature/128-autonomous-experimental-design`
- Risk: Medium
- Governing documents: ADR 004 (harness, replay), ADR 002 (replay fixture),
  `docs/validation-contract.md`, `docs/authoring.md` (claim types)
- Written by the implementer: no plan existed when the feature started.

## Design

| Piece | Where | Decision |
|---|---|---|
| Question | `pbc.agents.design.ExperimentalDesign` | Two one-parameter models, the instrument noise, nominal parameters of each model for the score, a chi-square threshold of 25, a budget of 8 |
| Score | `design.design_score` | From the arguments alone: noise-free values of one model at the design points fitted by the other (`fit_curve`); the smaller of the two directions. No reading is used |
| Assessment | `design.judge` | Reruns each distinct accepted call from its arguments; fits both models; `discriminated` only if the better model fits within 3 sigma of its chi-square and the other is worse by the threshold, with an identified parameter; otherwise `inconclusive`, no claim type |
| Instrument | `design_lab.reading` | Simulated quadratic drag of a 2 kg block with a hidden constant plus Gaussian noise seeded from the arguments (`repeat` gives independent readings) |
| Rigs | `design_lab.RIGS` | `full` (start up to 20 m/s: discriminated) and `slow` (up to 2 m/s: inconclusive); the bound is the allowlist |
| Lesson | `site/lessons/agents-llm/04-an-experimental-design-agent/` | Format 1, two authored fixtures, as plan 87 |

## Decisions

- Competing models are the linear and quadratic drag of `pbc.mechanics.drag`
  (closed forms for a block on a table; a test checks the closed form against
  the course's integrator). The F23 helper `fit_curve` is used directly; `profile`
  and `recover` are not needed for one-parameter models.
- No live key: fixtures are authored examples labelled as such (as plans 24, 87).
- The threshold and nominal parameters are fixed in the code before the runs.
- The optional prose of the agent is never read; a test covers a boasting agent
  and forged stored results.

## Verification

`tests/unit/test_agents_design.py`, `tests/integration/test_agent_replay.py`
(replay without network or key, fixtures free of credentials, lesson directory),
the existing scan of `src/pbc/agents/` in `test_agents_boundary.py`, and
`./scripts/verify.sh`.
