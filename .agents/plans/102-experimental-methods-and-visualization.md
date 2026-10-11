# Plan: F51 experimental methods and visualization foundations (Issue #102)

Source: Issue #102, ADR 007, docs/architecture.md "Measured-data lab", roadmap
F51, the dossiers in docs/datasets/, deferred Issue #66.

## Decisions taken
- **Touchstone reader (Issue #66): keep the in-repository parser.** It is 66
  lines, tested on the committed samples (passivity, reciprocity, cadence), and
  needs no licence, lock entry, or maintenance. A library such as scikit-rf
  pulls in a large dependency tree for a feature (two-port S2P) this project
  uses in one lab. Revisit when a lab needs n-port files, other parameter
  types, or noise data. Recorded in the NPL dossier.
- **No HDF5, MAT, or FITS reader, and so no new dependency.** The three go
  datasets are a GWOSC plain-text file, Touchstone files, and CSV. A lab with
  a go decision that needs another format adds its reader with that lab.
  `numpy`, `scipy`, `matplotlib` already carry the analysis and the plots.
- The page-side marker of a figure's data is a new cell option
  `#| fig-dataset: <dataset id>`; the lesson filter carries it to the status
  label as `data-dataset`; source check and built-site check compare the
  status with the artifact types of the card.

## Layout (`src/pbc/data/`)
- `series.py`: `Series` (values, uncertainty, artifact type, disclosed steps)
  with `select`, `smooth`, `interpolate_to`, `drop_masked`; its status follows
  from the artifact type and the steps, so smoothing cannot stay "raw".
- `uncertainty.py`: robust noise level, standard error of repetitions,
  quadrature, first-order propagation, expanded to standard uncertainty,
  normalised difference.
- `calibration.py`: sentinel to NaN masks, valid fraction, gain and offset
  with propagated uncertainty.
- `fit.py`: `fit_curve` (least squares, covariance, correlation, residuals,
  reduced chi-square, identifiability by the singular values of the scaled
  Jacobian).
- `plotting.py`: status label, credit line, measured-versus-model with residual
  panel, series with uncertainty band, signed colour scale, `check_figure`.
- `status.py`: artifact type to figure status, allowed statuses of a card.
- `pbc.authoring.datalab`: `data_card(dataset)` renders the card on the page.
- Reference figures use the helpers; each passes `check_figure`.

## Tests
- `tests/unit/test_data_*.py` for each module, on the committed samples and on
  synthetic data; parsing tests of the cards stay in `test_data_samples.py`.
- Source check (`tests/support/lesson_checks.py`) and built-site check
  (`tests/support/site_checks.py`) of `fig-dataset` against status.
- The measured-data pattern is exercised on `site/rendering-check.qmd`.
