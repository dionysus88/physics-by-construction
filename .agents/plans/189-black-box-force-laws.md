# Plan: F66 — Law discovery lessons: black-box force laws (Issue #189)

- Issue: #189 (source: `docs/roadmap.md`, F66); lesson list and conditions
  approved by the owner on 2026-10-15 (comment on the Issue).
- Branch: `feature/189-black-box-force-laws`; base `18a2d19`.
- Written by the implementer: no plan existed when the feature started.

## Design

Three format 2 lessons in `agents-llm` with `course: mechanics`, methods
`simulation` and `llm-agents`, on the F65 package `pbc.discovery`:

| Dir | Id | Slot | Environment and condition |
|---|---|---|---|
| `05-discovering-a-force-law` | `black-box-force-law` | D1 | central force, `partial`, one trace |
| `06-prior-knowledge-in-discovery` | `prior-knowledge-in-discovery` | D2 | oscillator (Hooke's law seen through the motion), `full`, `partial`, `none`: three traces under one protocol |
| `07-a-modified-force-law` | `modified-force-law` | D3 | central force with a modified exponent, `partial`, one trace, and the familiar inverse-square law fitted as a baseline |

- **Module `pbc.discovery.force_lab`**: the three protocols (fixed before any
  recording: budget 20, at most 12 model messages, seed 0, tolerance 0.05 on
  the held-out error), the trace of each run (`TraceInfo` constants), the
  replay of a fixture with the recomputed `Score`, the familiar-law baseline
  (least squares with the exponent held at 2), and a live `main()` with
  `--record` as in the other agent lessons.
- **Fixtures**: `replay.json` (D1, D3) and `replay-full.json`,
  `replay-partial.json`, `replay-none.json` (D2) next to the pages.
- **D2 fairness** (owner's condition): one `Protocol` object for the three
  conditions, so model, tools, budget, step limit, seed, and held-out settings
  are equal; only the task text differs. A test asserts it.
- **D3** (owner's condition): the baseline's recovery is computed; the agent's
  score is reported as the build recomputes it, a failure as a failure.

## Decisions

- **No `trace.json` in a lesson directory.** ADR 002 (decision on replay
  fixtures) and the committed-files check allow only `replay.json` or
  `replay-<name>.json` there; the trace's version record (protocol, condition,
  seed, prompt version and SHA, model, date, cost) is kept as `TraceInfo` in
  `force_lab`, and a test checks it against the fixture. The authoring guide
  and the protocol document say so.
- **Recording.** No provider key is available to the implementer. As for the
  fixtures of AI0 (accepted by the human on 2026-10-08), the runs are recorded
  by a Claude model (`claude-sonnet-5-5`) in a Claude Code session: a fresh
  sub-agent per run, given only the system prompt, the task, and the tool
  specifications, choosing every call after reading the harness's results; the
  harness computed every result. The fixture's `model` field and the page say
  so. A maintainer may replace them with `--record`.
- **Worlds** (judge configuration, never on a page): D1 strength 20,
  exponent 2; D2 stiffness 3; D3 strength 12, exponent 2.5. Observed while
  choosing: sparse identification (F65) fails on strength 9, exponent 2,
  because its relative threshold drops the right term from a nearly
  collinear library; D1 does not use that world, and the limit is stated on
  the page as a property of the baseline.

## Discoveries during the work

- **The score counted calls the loop refused.** `score_transcript` (F65)
  dispatched every call of a message, while the loop runs at most four; a
  refused fifth call became a probe in the score. Fixed in
  `pbc.discovery.protocol` with a test; the protocol document says so.
- **A Claude Code session reports no token counts.** `CostRecord` takes
  `None` for the token counts, and the pages say they were not reported.
- **Recording.** Five runs on 2026-10-16, each a fresh sub-agent; the harness
  ran every call and the session relayed the results. A first D1 attempt was
  discarded because its reply was a summary instead of the JSON message; the
  kept D1 run received one extra harness message before its first reply
  (deliver the reply through the hand-back), which the page states.
- **Results, reported as scored.** D1 recovered with four probes and round
  numbers; D2 full recovered, partial and none did not, while a fit to each
  run's own readings recovers in all three; D3 recovered (exponent within one
  standard error of its readings, strength many standard errors off). The
  familiar inverse-square fit is rejected by the chi-square on the grid and on
  the agent's four readings; sparse identification is consistent in-sample and
  fails on the held-out settings.

## Steps

1. `force_lab` and its unit tests.
2. Record the five runs; commit the fixtures.
3. The three lessons.
4. Docs: authoring "Discovery lessons", `docs/discovery-protocol.md` (trace
   record of a lesson), `docs/project-map.md`, architecture layout note;
   curriculum test of the filled slots. The roadmap's state tables are records
   of the planning cycle and are not edited by a feature.
5. Adapt to the F117 contract (ADR 016; review finding M1, the Issue's
   sequencing decision): one experiment per lesson,
   `pbc.mechanics.experiments.black_box_force_law`,
   `prior_knowledge_in_discovery`, and `modified_force_law`, declared as
   `lesson.experiment`, holding every computation and figure the page shows
   (`draw_*` functions encoded once by `pbc.experiment`); the pages show
   excerpts of it and read `result`; the footer is "Replay this experiment";
   `LIVE` names the live run with its arguments (`pbc.discovery.force_lab
   <run>...`, which now takes several runs, so D2 runs its three conditions
   in one command); a unit test per experiment
   (`tests/unit/test_<name>_experiment.py`).
6. Verification: `./scripts/verify.sh --base` (new lessons).
