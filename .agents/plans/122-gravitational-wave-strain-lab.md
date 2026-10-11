# Plan: F60 gravitational-wave strain lab (Issue #122)

## Approach
- Physics in `src/pbc/mechanics/chirp.py` (Newtonian chirp from Kepler's third law
  and the quadrupole loss, closed forms, numerical inspiral as independent check).
- Processing and fit in `src/pbc/data/gwstrain.py` (Welch spectrum, whitening as a
  linear filter, cross-correlation with off-source control, variable-projection
  least squares with a profile over the chirp mass).
- Lesson `site/lessons/mechanics/10-gravitational-wave-strain` (format 2, methods
  measured-data and simulation, prerequisite kepler-orbit); M8 gains it under `related`.
- Tests: `tests/unit/test_chirp.py`, `tests/unit/test_gwstrain.py`.

## Decisions
- Estimate by fitting the whitened waveform, not a spectrogram ridge or zero
  crossings: both were tried and are too noisy (ridge fit ran to the bound).
- Uncertainty: profile interval (statistical) plus the spread over bands and windows.
  `fit_curve`'s covariance is not used for the mass (Mc and t_c are tied).
- Published value is cited via the dataset card name, not a new register entry
  (the register needs a human-reviewed source).
