# Plan: F65 — Physics environments and the discovery evaluation protocol (Issue #154)

## Design

- **Package `pbc.discovery`** on the harness of ADR 004 (`pbc.agents`), no new dependency.
  - `environment.py`: `Environment` (controls with bounds and units, one noisy
    observation, a budget, reset, hidden `_law`, held-out settings outside the
    control bounds, `held_out_error` as the only judge call). Noise is a hash of
    seed and controls, so a replay is exact. Worked environments: projectile
    (hidden gravity), oscillator (hidden stiffness), central force (hidden
    modified exponent). The N-body world waits for F69.
  - `tools.py`: `environment_allowlist` gives `measure` and `submit` only.
  - `baselines.py`: random and grid probing, least squares (`pbc.data.fit`),
    sparse identification (STLSQ, pure NumPy); each reports failure with a reason.
    No locked discovery library (PySR needs Julia; none added).
  - `protocol.py`: `Protocol`, prompts per condition (full, partial, none),
    `score_transcript` (tool calls run again on a fresh environment), frozen trace
    (`replay.json` + `trace.json` with prompt version and SHA, model, cost record),
    `comparison` table.
- **Docs**: `docs/discovery-protocol.md` (new), `docs/project-map.md`, the
  "Discovery lessons" section of `docs/authoring.md`. `docs/evaluation.md` and the
  ADRs are unchanged.

## Tests

`tests/unit/test_discovery.py`: truth unreachable (public attributes, tools, specs,
prompts), budget and bounds, each baseline recovers a known law and fails on one it
cannot, scoring deterministic and independent of recorded text, trace round trip and
replay without credentials, no dangerous import or call.

## Decisions

- Held-out settings lie outside the control bounds, so the agent cannot probe them.
- The oscillator error is relative to the amplitude (the displacement crosses zero).
- Sparse threshold is relative to the largest coefficient (an absolute one kept
  collinear spurious terms).
