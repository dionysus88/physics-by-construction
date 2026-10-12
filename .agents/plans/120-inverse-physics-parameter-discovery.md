# Plan: F23 inverse physics, parameter discovery with uncertainty (Issue #120)

## Approach
- `src/pbc/data/inverse.py` on top of `fit_curve`: `recover` (many synthetic
  data sets, bias, scatter, coverage), `profile` (chi-square over one parameter,
  others refitted, warm-started walk; an interval that does not close is marked
  open), `residual_autocorrelation` and `verdict` (reasons not to believe a fit).
- `src/pbc/data/gwinjection.py`: a known chirp, whitened like the data, added to
  off-source stretches of the GW150914 file and fitted with `fit_chirp`.
- Lesson `site/lessons/mechanics/12-inverse-physics-parameter-discovery`
  (format 2; simulation and measured-data; prerequisites harmonic-oscillator and
  gravitational-wave-strain): recovery of a damped oscillation, k and m tied in a
  free oscillation, a wrong model seen in the residuals, then the measured chirp
  mass with the injection scatter and the spread over bands.
- Tests: `tests/unit/test_inverse.py`, one injection test in `test_gwstrain.py`.

## Decisions
- Measured case is the F60 lab (met dependency), not a new dataset.
- `inverse.py` is added to `TOOLS` of `tests/support/data_use.py`: it computes
  and reads no data, so figures made with it are not figures of a dataset.
- The lag-1 autocorrelation of whitened, band-passed strain is high (band-pass),
  so the verdict's structure reason is not by itself a model error; the lesson
  measures it on noise away from the event and says so.
- The optional bounded agent is not built (the Issue says optional); stated in the
  lesson limits.
