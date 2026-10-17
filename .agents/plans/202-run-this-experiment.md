# Plan: F117, "Run this experiment": learner instructions without a website build (Issue #202)

Implements ADR 016. Source: Issue #202 (the authority on what is
delivered), ADR 016 decisions 1 to 6, ADR 014 decisions 1, 3 and 9, ADR
012 decision 4, ADR 002, ADR 004, ADR 011 decision 3, ADR 017 decision 7.

## Current state (inspected at 18a2d19)

- Thirty-two lessons under `site/lessons/<strand>/<NN-slug>/index.qmd`;
  every figure is a `plt.show()` in a labelled cell, captured by the
  Jupyter inline backend in Quarto's `retina` format: the figure's dpi is
  96 (`figure.dpi`, set by Quarto's kernel setup with `figure.figsize`
  (7, 5)), the PNG is written at 192 dpi with `bbox_inches="tight"` and
  Matplotlib's `Software` text chunk, and the page shows it at half its
  pixel size (`width`, `height` of the `img`). About 74 figures, 150 result
  tables, and inline numbers in `{python}` expressions.
- The footer is `reproduce_this(code=..., tests=...)`
  (`src/pbc/authoring/reproduce.py`), a marker that the post-render step
  (`site/context.py`, ADR 014 decision 9) turns into the section
  `reproduce-this`; its last command is `quarto render`.
- The page reproduction is `test_reproduce_commands_regenerate_the_page_within_the_time_budget`
  in `tests/e2e/test_lessons.py`, marked `same_machine`, run by
  `site-checks-reproduction` and deselected by `tests/e2e/conftest.py`
  for the lessons a selective run did not execute.
- The digest (`src/pbc/authoring/digest.py`) follows the imports of the
  page's cells through `pbc` modules transitively, so a module under
  `src/pbc` that the cells import is an input of the lesson.
- The gate of the switch is met: the owner's interim full-run timeout (60
  minutes for the `build` job, up to 45 lessons) is recorded in the status
  of ADR 014 (2026-10-15), and F119 (#185) is applied as well.
- F115 (editorial pilot, mechanics 01 to 05) has no Issue yet; F117 goes
  first (owner's sequencing on the Issue) and F115 rebases onto the moved
  cells. F72, F73, F66, F67 merge after F117 and build to this contract.

## The entry-point contract (fixed once, step 1)

1. **Location.** A lesson whose methods are not Lean only has one module
   `pbc.<course>.experiments.<name>` under `src/pbc/<course>/experiments/`,
   where `<course>` is the lesson's `course` and `<name>` its `id` with
   hyphens as underscores (`kinematics`, `particles_in_a_box`). It imports
   the lesson's authoritative implementation from `src/pbc` and holds the
   experiment: the computations whose numbers the page shows, and one
   figure-writing function per figure. The page's cells import it, so the
   digest follows it (ADR 014 decision 1 as implemented); nothing goes into
   the lesson directory.
2. **Declaration.** The front matter declares it: `lesson.experiment` is
   the module name, or `./scripts/check-lean.sh` for a lesson whose
   methods are `[lean]` only and that draws no figure (ADR 016 decision 2,
   the Lean kind). A Lean-only lesson that draws a figure declares its
   module; its proof check comes from `lesson.lean-modules` and its footer
   lists both. The lesson source check (`check_experiments` in
   `tests/support/lesson_checks.py`) validates a declaration from step 1
   on (the module follows the rule of 1, exists, is imported by an executed
   cell of the page, and has its unit test
   `tests/unit/test_<name>_experiment.py`; the Lean value only for a
   Lean-only lesson without a figure); it requires the declaration from the
   switch on (`required=True`), and the heading of the last section by kind.
3. **Interface.** The module defines `run() -> pbc.experiment.Experiment`
   and ends with `if __name__ == "__main__": main()` through
   `pbc.experiment.main`. `run()` computes everything and records, by
   name: numbers with the format the page shows them in
   (`Experiment.number`), result tables (`Experiment.table`, the columns of
   `pbc.authoring.table`), and figures (`Experiment.figure(label, draw)`,
   where `label` is the cell's `fig-` label and `draw` a module function
   that returns a Matplotlib figure).
4. **The command.** `uv run --locked --no-dev python -m <module> <output
   directory>` from the root of a clone (`results` in the footers). It writes `<label>.png` for every
   figure and `results.json` with every number and table cell as the text
   the page shows (displayed precision), and nothing else. It needs the
   project's dependencies only: `uv sync --locked --no-dev`. An agent
   lesson's command replays the recorded run without a credential; its
   live run is a separate command behind the `openai` extra (`uv sync
   --locked --no-dev --extra openai`) and the credential, named by its
   footer. No other learner group or extra is needed by the lessons as
   they are; a lesson kind that needs one declares it in `pyproject.toml`
   and its footer names it.
5. **One encoder.** `pbc.experiment.encode(draw)` draws the figure under
   fixed Matplotlib settings (Matplotlib's defaults with the two values
   Quarto's kernel sets for HTML: `figure.figsize` (7, 5) and `figure.dpi`
   96, so that a figure keeps its size on the page), writes a PNG at 192
   dpi (fixed, never the figure's own dpi, which a screen backend such as
   macOS's doubles) with `bbox_inches="tight"`, the figure's face and edge
   colours, and no `Software` metadata, and closes the figure; the program
   forces the `agg` backend. The entry
   point writes those bytes to the file; the page's cell shows the same
   bytes (`Experiment.show(label)`, a display object with the PNG and its
   width and height at half the pixel size, the retina form of today), so
   the inline backend never encodes a lesson figure and the figure file
   of the built page holds the writer's bytes. The figure is still
   produced by an executed cell of the build and no image is committed
   (ADR 002); the cell keeps its label, so the preview of F63 finds it.
6. **The page.** One hidden cell runs `result = experiment.run()`; the
   cells that showed code show the experiment's functions by `excerpt`
   (displayed code by reference, ADR 002); tables are
   `result.table(name)`, inline numbers `{python} result[name]`, figures
   `result.show(label)` in the labelled cell. Exercise solutions that
   compute what they show do so through functions of the module as well,
   shown by `excerpt`, so that no scientific logic exists twice.
7. **Figure kinds.** Each kind is verified on its first migrated lesson:
   the page's figure file must equal the entry point's byte for byte (the
   same encoder produces both), and the re-encoded figure must equal the
   figure of the base build as an image at the page's rendered size
   (pixels identical or the difference recorded below). Kinds: Matplotlib
   plot (mechanics 01), conceptual diagram (`pbc.authoring.diagrams`,
   mechanics 01), measured-data plot (mechanics 10), agent replay plot
   (agents-llm 01), Lean lesson plot (lean 01). A kind that cannot reach
   byte identity is compared as an image at the rendered size plus the
   numbers, and recorded here per kind.
8. **Tests.** One unit test file per entry point: the command writes
   every figure the page labels and a `results.json` with the expected
   names, and at least one assertion of the lesson's science on the
   result. `tests/unit/test_experiment.py` covers the encoder (deterministic
   bytes, no metadata, settings independent of the caller's rcParams,
   rendered size) and the results file. For a Lean-only lesson the test is
   the Lean build and the exercise pairing check of ADR 011 decision 3.
9. **The experiment check** (switch, step 8): a test marked `same_machine`
   in `tests/e2e/test_lessons.py`
   (`test_the_experiment_regenerates_the_figures_and_numbers_of_the_page`),
   run by `site-checks-reproduction`, so the selection of
   `tests/e2e/conftest.py` applies unchanged. A session-scoped fixture
   makes one clone of the working tree and one learner environment in it
   (`uv sync --locked --no-dev`, outside the budget, without the variables
   that point uv at the checkout); per lesson it runs the footer's
   experiment command against that environment with `UV_NO_SYNC=1`, within
   30 seconds, then the footer's `lake build` of a Lean lesson (Mathlib
   shared from the checkout), and compares with the built page
   (`support.experiments.compare_with_page`): every `<label>.png` byte for
   byte with the page's figure file, every number as a whole token of the
   page's text, every table by its caption cell by cell, every printed
   output, the numbers of every display, and the data of every widget. The
   targeted tier (`scripts/check-lesson-pages.sh`) runs the selected
   lessons' experiments the same way, against the page it rendered alone.
10. **The footer** (`pbc.authoring.reproduce`): kind from the methods
   (`[lean]` only: proof; `llm-agents`: replay; else run); commands
   clone, cd, checkout, `uv sync --locked --no-dev`, the experiment, and
   for a lesson with `lean-modules` `cd lean`, `lake exe cache get`, `lake
   build <modules>` (elan alone: not `./scripts/check-lean.sh`, which runs
   `uv run --locked` and needs `jq`); the live run of an agent lesson in a
   separate "not verified" block naming `OPENAI_API_KEY` and the extra
   `openai`, from the experiment module's `LIVE`. The learning path links
   the section by its heading.

## Steps (each a reviewed pull request, partial until the last)

1. **Contract and pilot.** `src/pbc/experiment.py` (encoder, `Experiment`,
   `main`), its tests; the optional key `experiment` in the lesson format
   (`tests/support/lesson_checks.py`, `pbc.authoring.path`) with its
   check; mechanics 01 migrated (`pbc.mechanics.experiments.kinematics`,
   `tests/unit/test_kinematics_experiment.py`); the image comparison of
   its three figures recorded below; `docs/authoring.md` gains the section
   on writing an entry point; `docs/project-map.md` names the new files.
2. **Mechanics 02 to 09** (simulation kind), behind the unchanged footer.
3. **Mechanics 10 to 16** (measured-data kind first verified on 10).
4. **Thermodynamics 01 to 03, waves 01 to 03, agents-abm 01.**
5. **Agents-llm 01 to 04** (replay kind; live run named, not run).
6. **Lean 01 to 05** (`./scripts/check-lean.sh` declared; the figures of
   the Lean lessons get their module under `pbc.mechanics.experiments`).
7. **Setup page and documents.** `site/reproduce.qmd` by activity;
   `tests/integration/test_setup_page.py` performs the Python-only
   commands in a fresh clone, asserts no `dev` package, runs one
   experiment per non-Lean kind, drops the equality with `ci.yml`;
   `README.md`, `CONTRIBUTING.md`, `docs/development.md`,
   `docs/authoring.md`, `docs/lesson-template.qmd`, `site/contribute.qmd`,
   `site/index.qmd`, `docs/instructor-packs/`, `docs/architecture.md`; the
   test over the guides (criterion 1).
8. **The switch.** The footer by kind ("Run this experiment", "Replay this
   experiment", "Check this proof", identifier `reproduce-this` kept, no
   render command); the lesson source check requires the declaration; the
   experiment check of contract 9 with a test per failing case (changed
   result, changed entry point, missing entry point) and the selection
   test; the page reproduction test reads the new footer. The pull request
   names the gate (the owner's 60-minute timeout of 2026-10-15).
9. **After the merge (owner).** One full run on `main` measured against
   the 60-minute timeout, recorded in `docs/release-readiness.md` with the
   executions per lesson before and after; the status line of ADR 016
   records the delivery (an ADR change, which the owner approves).

## State (2026-10-16)

Steps 1 to 8 are done in this branch, in one session; the owner may publish
them as one pull request or split them. Step 9 is the owner's: the full run
on `main` after the merge, measured against the 60-minute timeout and
recorded in `docs/release-readiness.md` with the executions per lesson
before (three) and after (four: build, determinism build, page
reproduction, experiment), and the status line of ADR 016. The Issue's
owner note says F117 touches no ADR and asks to stop and report if it must;
criterion 6 asks for the status line of ADR 016, so that line is left to
the owner. Criterion 7 (a reviewer who did not write the page follows it on
a clean machine for one simulation, one agent, and one Lean lesson) is
recorded on the pull request by that reviewer.

## Verification per step

`./scripts/verify.sh --targeted` reports a full run whenever a test or
`src/pbc/authoring` changes; the full `./scripts/verify.sh` is then the
tier. Before it, per migrated lesson: render the page before and after
and compare the page's text (tables, numbers, prose) and each figure as an
image at the rendered size (scratch script, result in the pull request).

## Record of the figure kinds

Method: the page is rendered alone before and after the migration
(`quarto render` of the page, scratch copies); the text of `<main>`
without code listings and the footer is compared, each figure is compared
as decoded pixels with the base, and the entry point is run with `uv run
--locked --no-dev` in a separate environment and its PNGs compared byte
for byte with the page's figure files.

| Kind | Lesson | Page = entry point (bytes) | Pixels = base build | Text = base |
|---|---|---|---|---|
| Matplotlib plot (line, log-log) | mechanics 01 | yes (2 figures) | identical (1078x654, 1110x658) | identical |
| Conceptual diagram (`pbc.authoring.diagrams`) | mechanics 01 | yes | identical (990x362) | identical |
| Plots, diagrams, multi-panel figures | mechanics 02 to 09 | yes (31 figures) | identical | identical, printed output identical |
| Measured-data plot (`pbc.data.plotting`, dataset cards) | mechanics 10 to 12 | yes (8 figures) | identical | identical |
| Widget's static figure and data (`widget`) | mechanics 05, 11 | yes | identical | identical; the on-demand file of 11 is unchanged |
| Plots | mechanics 13 to 16 | yes (6 figures) | identical | identical |
| Plots of thermodynamics, waves, agents-abm | 7 lessons | yes (14 figures) | identical | identical |
| Agent replay (displays of the replayed run, diagrams, plots) | agents-llm 01 to 04 | yes (6 figures) | identical | identical; displays as `Experiment.display` |
| Lean lesson plots | lean 01 to 05 | yes (6 figures) | identical | identical apart from the commit of the base copy in the Lean evidence |

Every figure kind reached byte identity between the page and the entry
point, so no figure kind needs the image comparison fallback of ADR 016
decision 2.

Only the PNG metadata changes (the `Software` text chunk is gone), so the
file bytes differ from the base build and the decoded images do not.

## Additions to the contract found on the way

- `Experiment.widget(name, data)`: the data of an interactive figure,
  written as `<name>.json` (mechanics 05, 11).
- `Experiment.capture(name)` and `output(name)`: what a function prints, for
  pages that show printed results (mechanics 09 to 12).
- `excerpt(module, region=...)`: the values an experiment starts from are
  top-level names between `# region:` markers; the built-site excerpt check
  (`_source_of` in `tests/support/site_checks.py`) follows.
- The dataset rule of format 2 (`support.data_use`) decides whether a
  figure of the show form is made from data by the expression its
  experiment records it with (`ExperimentFigures`); the record of the
  experiment is inert, so passing it to a function does not make its
  results data.

## Defects of the pages found by the comparison (not fixed: outside F117)

Five result tables were never displayed, because the `table()` call was not
the last expression of its cell, although the prose of three refers to
them: mechanics 10 (the angle sweep), mechanics 14 (the modes of the
coupled springs), mechanics 15 (the Legendre transform), agents-abm 01 (the
six runs), agents-llm 01 (the agent's ranges). The pages stay as they were
and the experiments record only what the pages show, so the results file
holds no table the page lacks. Showing these tables is a change of the
pages for a follow-up Issue (owner's decision).

## Open questions

1. ADR 016's status line (criterion 6): the owner's note on the Issue says
   F117 touches no ADR and to stop and report if it must. The line is left
   to the owner, with the merge or after the measurement of step 9.
2. Delivery: the Issue asks for reviewed steps per strand; this branch holds
   steps 1 to 8. The owner decides whether to review and merge it as one
   pull request or to split it.
