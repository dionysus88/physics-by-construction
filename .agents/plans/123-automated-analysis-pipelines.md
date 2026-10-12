# Plan: F47 automated analysis pipelines (Issue #123)

Source: Issue #123, roadmap F47, F51 plan (`102-*`), ADR 002 and ADR 007,
docs/authoring.md "Measured data".

## Layout
- `src/pbc/data/pipeline.py` (a tool module of `pbc.data`, listed in
  `TOOLS` of `tests/support/data_use.py`): `sweep` over one parameter,
  `estimate` (mean and standard error of repetitions), `Report` of
  quantities rendered at a stated precision, and `check_report`, which
  compares the rendering with a committed expectation line by line.
- `src/pbc/mechanics/analysis.py`: the simulated problem. Range of a
  projectile with drag against the launch angle, the first-order propagated
  uncertainty of the launch speed, a seeded Monte Carlo check.
- `src/pbc/data/flume_analysis.py` (a reader-side module, so a source for the
  figure-dataset check): the measured problem. Five repetitions of gauge 5 of
  the committed flume sample, wave height statistics and period per
  repetition, mean with standard error, a sweep of the window, comparison
  with the three modelled references.
- `src/pbc/data/reports.py`: registry of the two reports and
  `python -m pbc.data.reports [--update]`.
- `reports/expected/*.txt`: the committed expectations. Outside `site/` and
  `src/`, because a lesson directory holds only its page.
- `site/lessons/mechanics/10-automated-analysis-pipelines/index.qmd`: format 2
  lesson; the build regenerates both reports and fails on a difference at the
  displayed precision.
- Tests: `tests/unit/test_pipeline.py`, report tests including the expectation.
- Docs: `docs/authoring.md` (pipeline helper), `docs/project-map.md`.

## Decisions
- The expectation is compared as rendered text: that is "displayed precision".
  Precision is chosen well above round-off so another machine gets the same text.
- No change to `scripts/verify.conf`, ADRs, or workflows.
