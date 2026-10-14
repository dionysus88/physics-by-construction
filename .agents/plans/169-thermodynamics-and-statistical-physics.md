# Plan — Issue #169 (F70): thermodynamics and statistical physics, T1 to T3

Short plan. Governing: ADR 013 (decisions 6 and 8), `docs/authoring.md`, the F11 gas
lesson and `pbc.abm.gas`, `site/curriculum.yaml` (T0 to T3 and eight planned slots).

## Code (`src/pbc/thermodynamics/`, the first module of the course)

| Module | Contents | Closed-form check |
|---|---|---|
| `diffusion.py` | seeded random walks of equal steps in a random direction, mean squared displacement, fitted D, predicted D = l²/(2 d tau), the fraction of walkers within a radius | D against l²/(4 tau) in the plane; the radial fraction 1 - exp(-R²/4Dt) |
| `kinetic.py` | the Maxwell speed distribution at a measured temperature: CDF, quantiles, mean speed; the fraction of speeds below the quantiles of the model, built on `pbc.abm.gas.measure` | the measured speeds against the analytic CDF at the simulated k_B T |
| `entropy.py` | Ehrenfest urn ensemble, log multiplicity, Shannon and Gibbs entropy of an ensemble, the exact mean | Gibbs entropy at equilibrium = N ln 2; mean n(t) exact; Stirling |

## Lessons (strand `thermodynamics`, new directory)

T1 `01-random-walks-and-diffusion`, T2 `02-kinetic-theory-of-gases` (prerequisite
`particles-in-a-box`, T0, from a later strand), T3 `03-entropy-from-ensembles`.
T0: front matter `course: thermodynamics`, `slot: T0` in one change; address unchanged.

## Tests and docs
Unit tests of the three modules; `test_curriculum` (T0 course and slot), `test_learning_path`
(course counts), e2e addresses; docs: roadmap/architecture/README status where they count lessons.

## Steps
1. Modules and unit tests. 2. T0 re-home. 3. T1. 4. T2. 5. T3. 6. Tests and docs. 7. verify.

## Status: steps 1 to 6 done; step 7 is the last full run (evidence in the final message)

## Discoveries during implementation

| Finding | Resolution |
|---|---|
| The Ehrenfest urn that always moves the chosen particle to the other half has period two: n alternates between even and odd, the ensemble never reaches the uniform distribution, and the Gibbs entropy stops at (N - 1) ln 2 | The step re-places the chosen particle in a random half; the mean then relaxes by the factor 1 - 1/N, and the lesson says why (assumption 3 of T3) |
| The entropy estimated from the frequencies of a finite ensemble is low by about (K - 1) / (2 M); at equilibrium, where the entropy is maximal, the bias exceeds the standard error, so a plain comparison with N ln 2 fails | `plug_in_bias` (first-order correction); T3 shows the raw estimate failing and the corrected estimate agreeing, and says where the correction stops being reliable |
| Two `table()` calls in one cell show only the last table | One table per cell in the lessons |
| No `go-deeper` blocks | A reference-register entry needs a human to open the source (ADR 009); the lessons are complete without one |
| A lesson without prerequisite lessons is suggested on every page as "What to do next"; T3 made a second suggestion on `numerical-integrators`, and the key presses of `test_operating_the_widget_writes_no_cookie_and_nothing_to_browser_storage` reached its Ignore button, so the page wrote learner state that the baseline run did not | T1 requires `kinematics` (a random walk is a state with an update rule), T3 requires T1; the suggestions of a page are again those of before F70 |
