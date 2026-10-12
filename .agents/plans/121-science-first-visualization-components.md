# Plan: F43 science-first visualization components (Issue #121)

## Approach
One component per lab that needs it; no component without a lab. The first lab
is F60 (gravitational-wave strain, lesson 11), which needs a comparison of the
whitened measurement with the model, so the first component is the
**waveform comparator**: measured series against model profiles (the chirp for
a range of chirp masses) with error metrics. The field viewer (F53), the
signal explorer, and the image comparator (F52) wait for their labs.

- Data: `pbc.data.gwstrain.models_at_masses` (best chirp and metrics at fixed
  masses) and `pbc.data.comparison.waveform_comparison` (JSON-ready payload).
- Delivery: `pbc.authoring.widget_asset` writes the payload beside the page
  (`index_files/figure-html/`), which Quarto publishes with the page.
- Component: `site/widgets/waveform-comparator.js`; button first, `fetch` of
  the own-origin file after the press, slider, readout, text export.
- Checks: `check_ondemand_budget`, `check_ondemand_loads_after_action`; the
  widget-source scan allows `fetch` (browser check proves "after an action").
- Tests: unit (`test_comparison.py`), integration (`test_site_checks.py`),
  e2e (`test_comparator.py`: fallback, keyboard, observed-value test, values
  against a fresh run of pbc, accessibility, reduced motion, budget).

## Decisions
- The residual is computed in Python and embedded; the browser draws and lists.
- The static figure of the lesson is the keyframe; nothing animates.
- Quarto publishes only its own supporting-file directory with a page rendered
  alone (the "Reproduce this" command), so the file goes into
  `index_files/figure-html/`; a `resources` glob in `_quarto.yml` was tried and
  rejected because a single-page render does not copy it.
- The coalescence time at each trial mass is searched on a fine grid around
  the fitted one and walked outward in mass: the chi-square has sharp minima
  in it, and a bounded search alone missed them.
