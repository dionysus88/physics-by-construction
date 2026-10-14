# Plan: Issue #170, F71 — Waves and optics: the wave equation, interference, sound

- Issue: #170 (source: `docs/roadmap.md`, F71)
- Branch: `feature/170-waves-and-optics-the`
- Base commit: `1f2c083`
- Risk: Medium (physics content; run time against the 30 s page budget)
- Governing documents: `docs/architecture.md` (lesson model), `docs/authoring.md`, ADR 013
- Written by the implementer: no plan existed when the feature started.

## Design

The first lesson feature of the `waves` course: it creates the strand directory
`site/lessons/waves/` and the package `src/pbc/waves/`. Three lessons, one
slot each.

| Lesson | Slot | Code | Checks |
|---|---|---|---|
| `wave-equation` (order 1) | W1 | `wave.py`: leapfrog `solve`, exact `standing_mode` and `reflected_pulse`, `observed_order`, `growth_factor`, `zigzag_run` | convergence order two measured on a pulse and a mode; zigzag growth above C = 1 against the formula; exact at C = 1 |
| `interference-and-resonance` (order 2) | W2 | `modes.py`: `string_frequency`, `triangle`, `spectrum_peaks`, `two_source_*`, `wave_packet`; `wave.py`: `forcing`, `driven_mode_amplitude`, `numerical_angular_frequency`, `numerical_group_velocity` | linearity to round-off; plucked-string peaks against n c / 2L; driven mode against the exact amplitude; dispersion and group velocity of the grid; two-source pattern against cos^2 |
| `sound-and-the-doppler-effect` (order 3) | W9 | `sound.py`: `pipe_frequency`, `emission_time` (bisection on the retarded time), `received_signal`, the two shift formulas | open and closed pipe resonances; a driven sweep; Doppler shift of a moving source and of a moving listener, counted from zero crossings of the computed signal |

## Decisions

| Decision | Reason |
|---|---|
| Sound is the wave equation for the pressure; open end = fixed, closed end = free | One solver serves W1, W2, W9 |
| The Doppler shift is computed from the emission time, not on the grid | Independent of the formulas and of the scheme; a moving source on a grid needs an interpolated source. Stated under the limits of W9 |
| Standing mode checked at a time where its phase is not a multiple of pi | At a multiple the first-order phase error cancels and the measured order is four, not two (found while writing the test) |
| Frequencies read from a Hann-windowed, zero-padded spectrum with parabolic refinement; tolerances stated as chosen | Peaks agree with the grid's own frequencies to 1e-5 |
| No change to the architecture, ADRs, curriculum file, or CI | The lessons fit the format 2 as is; slots W1, W2, W9 exist in `site/curriculum.yaml` |
| `tests/unit/test_curriculum.py` updated | The published lessons that carry a slot, and the planned courses, changed by this feature |

## Verification

- `tests/unit/test_waves.py`: each result against a closed form or a limit.
- `tests/lessons`, `tests/e2e`, the determinism build: the lesson rule.
- `./scripts/verify.sh`.
