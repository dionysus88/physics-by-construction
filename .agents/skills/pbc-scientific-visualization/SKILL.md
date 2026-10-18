---
name: pbc-scientific-visualization
description: "Physics by Construction's own rules for a scientific figure: choosing the visual, axes, units, uncertainty, captions, accessible encodings, comparing numerical, analytic, and measured results, reproducible Python generation, and keeping illustration apart from validated results. Use when a feature plan selects it for a new or substantially revised figure, plot, data panel, preview, or animation."
license: "Project-owned"
---

# PBC Scientific Visualization

The project's skill for scientific figures. It supplements, and never
overrides, the rules it points to; when this file and one of them disagree,
the rule wins and this file is wrong:

- `docs/authoring.md`: "Figures", "Visual design" (figure colours,
  conceptual diagrams, payload), "Lesson format 2" (figure status, lesson
  preview, numbers in prose, claim labels), "Measured data" (the page
  pattern), and the widget rules;
- `docs/validation-contract.md`: what a check may claim, and what it does
  not;
- the checks of `scripts/verify.conf` that read figures (`lesson-checks`,
  the built-site checks);
- the design specification of F123, once it exists.

A figure that follows this skill is not thereby correct. The checks and the
independent review decide that.

## 1. Choose the visual

| The reader should see | Use | Status (`fig-status`) |
|---|---|---|
| An idea, a setup, a mechanism | Conceptual diagram, `pbc.authoring.diagrams` (and the Diagram Design skill) | `conceptual` |
| What a model or a method computes | Analytic or numerical plot from the verified code | `simulated` |
| A measurement | Data plot with its uncertainty, `pbc.data.plotting` | `measured`, `calibrated`, or `processed`, from the card's artifact |
| Model against measurement | `measured_vs_model`: both, apart, with residuals | from the measurement |
| How an error behaves | Convergence (log-log, reference slopes) or a conserved quantity over time | `simulated` |
| Order or accumulation in time | A static sequence first; an animation only if the order is the point | as its content |
| An interface or a page | Interface illustration: not a result, never captioned as one | `conceptual` |

Draw only when the figure answers a question the prose raises; a table or a
sentence is often better. The figure the reader recognises the lesson by is
the one `lesson.preview` names.

## 2. Make it readable

- **Axes and units.** Every axis names the quantity and its unit:
  `"time step (s)"` in a lesson figure, `[unit]` where `check_figure`
  reads it (the `pbc.data.plotting` figures). Dimensionless: say so.
- **Scales.** Log scales where the claim is a power law or spans decades
  (convergence, spectra, a profile in chi-square); say "log-log" in the alt
  text. Do not choose a scale that hides the part the caption talks about.
- **Symbols and legends.** The symbols and names of the prose (the same
  method names, the same letters). A legend names every series and nothing
  else; it covers no data.
- **Colour.** From `pbc.authoring.FIGURE_COLOURS` (the data figures of
  `pbc.data.plotting` use its own palette); never new hex values in a
  lesson. Colour is never the only encoding: vary line style, marker, or
  direct labels as well. A sequential or signed colour map has a colour bar,
  is centred on zero when the sign matters (`signed_image`), and says
  "false colour" where it is.
- **Uncertainty.** A measurement shows its uncertainty as a band or bars,
  and the caption or legend says what it is (one standard deviation, the
  noise of the data, a lower bound). No band where none is known; say so
  instead. A fitted parameter that is not identified is reported as such.
- **Caption and alt text.** The status word comes first (the build adds
  it). The caption states the conclusion, not only the content. `fig-alt`
  describes the kind of plot, the axes, and what the curves do, for a
  reader who cannot see it, with no computed values; a number in a caption
  or alt text comes from an inline expression or is marked given. The
  sentence after the figure says what it shows, where the data come from,
  and what it does not show.

## 3. Compare results honestly

- Numerical against analytic: the exact solution is the reference, the
  error is plotted against the step, and the expected order is a reference
  line labelled as such, not a fit. Say where the straight line stops
  holding (round-off at fine steps, stability at coarse ones).
- Conserved quantities: plot the drift of the energy (or momentum, or the
  invariant of the problem) over many periods, relative to its start;
  distinguish bounded oscillation from secular drift.
- Model against measurement: the measurement solid with its band, models
  dashed and drawn apart, never merged; the residual panel below on the
  same time axis; the fit window shaded; the processing disclosed; the
  card's attribution on the figure (`add_credit`).
- Error sources and stability: name them in the caption or the sentence
  after it (time step, truncation, noise, calibration, the window); a
  tolerance is the one the check states, never a looser one for the figure.
- A figure supports a claim only through the claim's evidence: the cell
  label in the claim's `evidence` is what the lesson checks follow.

## 4. Generate it reproducibly

- Drawn by an executed cell, in a `draw_` function of the lesson's
  experiment, shown with `result.show(label)`; no image file in a lesson,
  and nothing generated is committed.
- From authoritative inputs: the values come from the verified
  implementation in `src/pbc`, the register, or a dataset card with a
  `go`; never typed into the cell, never from a model's answer.
- Deterministic: every random draw takes a fixed seed; `figsize` set; two
  builds give the same bytes (previews included).
- Sources retained: the code that draws the figure is the source; for a
  measurement, the committed sample, the card, and the dossier;
  `#| fig-dataset:` (or `fig-artifact:`, `fig-model-of:`) names it.

## 5. Keep illustration apart from results

A conceptual diagram, an interface illustration, a preview card, or a
decorative image is labelled `conceptual` and shows no result. A final
figure carries no invented result, equation, or datum: a curve that is
"what it should look like", a fabricated data point, an equation that the
code does not compute, a smoothed measurement shown as raw, or a model
drawn as if measured are all refused (`measured_vs_model` raises for a
model that is not `simulated` and for a simulated measurement; a series
changed by `smooth` or `select` becomes `processed`). When a sketch shows a computed curve, it is drawn by the
verified code.

## 6. Accessible and light

- A static equivalent of everything that moves; an animation or widget
  stops under `prefers-reduced-motion: reduce` and has controls.
- Contrast follows the design tokens (`tests/unit/test_design.py`).
- No unnecessary browser payload: a static figure before a widget; each
  page within its budget (`docs/authoring.md`, "Payload").

## Examples from the lessons

**Convergence, M5** (`site/lessons/mechanics/05-numerical-integrators/index.qmd`,
cell `fig-integrators-convergence`, drawn by `draw_integrators_convergence`
of `pbc.mechanics.experiments.numerical_integrators`).
Good: log-log error against step for four methods, told apart by marker
and line style in one colour, dotted reference slopes one, two, and four
labelled "slope N"; the caption gives the conclusion in words; the sentence
after it says the reference lines are for comparison and where they stop
holding. Bad: the same four series in four colours with no other
difference; a fitted slope printed as the order; a caption "Error against
step size".

**Measured against model with residuals, M16**
(`site/lessons/mechanics/11-gravitational-wave-strain/index.qmd`, cell
`fig-measured-vs-model`, `fig-status: processed`,
`fig-dataset: gw150914-strain`, drawn by `draw_measured_vs_model` of
`pbc.mechanics.experiments.gravitational_wave_strain` with
`pbc.data.plotting.measured_vs_model`). Good: whitened strain solid with
the one-sigma noise band, the fitted chirp dashed and apart, residuals
below on the same time axis, the fit window shaded, the GWOSC attribution
on the figure, the processing stated on the page. Bad: the chirp drawn over
the data in the same style; per-sample error bars where the card says no
per-sample uncertainty is released; the status `measured` for whitened and
band-passed data.

**Conceptual diagram, F32** (`fig-forces-on-a-falling-particle` in
`site/lessons/mechanics/02-newtons-laws/index.qmd`; also
`fig-state-and-update`, `fig-drag-against-speed`,
`fig-oscillator-energy-ellipse` in mechanics 01, 03, 04). Good: drawn by
`pbc.authoring.diagrams`, `conceptual`, weight, drag, and velocity told
apart by line style, the alt text conveys the insight, and the text says
it is a sketch. Bad: a hand-drawn image file; a diagram that shows a
trajectory nobody computed.

**Preview, F63** (`src/pbc/authoring/previews.py`, `site/lesson-previews.py`;
for example `lesson.preview: fig-integrators-phase-space` in M5).
Good: the lesson's own verified figure, scaled by the build, with its
status in the alt text; the fallback card is `conceptual` and shows no
result. Bad: a preview cropped or drawn by hand, or a decorative picture
standing in for a result.

Record in the completion evidence that this skill was applied, at the
digest of `PROVENANCE.yaml`, and which figure cells it shaped.
