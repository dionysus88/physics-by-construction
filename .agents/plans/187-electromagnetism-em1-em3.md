# Plan: Issue #187, F72 — Electromagnetism: fields, charged particles, induction

- Issue: #187 (source: `docs/roadmap.md`, F72)
- Branch: `feature/187-electromagnetism-em1-em3`
- Base commit: `18a2d19`
- Risk: Medium (physics content; first lesson feature of a course)
- Governing documents: `docs/architecture.md` (lesson model), `docs/authoring.md`, ADR 013
- Written by the implementer: no plan existed when the feature started.
- Sequencing (owner, on the Issue, 2026-10-16): implemented now, merged only
  after F117 (#202); then adapted to the entry-point contract of F117.
- F117 adaptation (2026-10-17, after #202 merged into this branch): each
  lesson has its experiment module under `src/pbc/electromagnetism/experiments/`
  (`electric_fields_and_potential`, `charged_particles_in_fields`,
  `faradays_law_and_induction`), declared as `lesson.experiment`, with one
  `draw_` function per figure and a unit test
  `tests/unit/test_<name>_experiment.py`; the pages show the experiment's
  functions with `excerpt` and its numbers, tables, and figures from `result`,
  and end in "Run this experiment".

## Design

The first lesson feature of the `electromagnetism` course: it creates the
strand directory `site/lessons/electromagnetism/` and the package
`src/pbc/electromagnetism/`. Three lessons, one slot each; 35 lessons after
it, within the interim gate of 45.

| Lesson | Slot | Code | Checks |
|---|---|---|---|
| `electric-fields-and-potential` (order 1) | EM1 | `fields.py`: `coulomb_field`, `coulomb_potential`, `field_from_potential`, `dipole_field`, `dipole_potential`, `sphere_flux` | superposition against minus the gradient of the potential (order two of the central difference); the field of a pair of charges against the closed form of a dipole, the gap falling as (d/r)^2; the flux through a sphere against the enclosed charge over epsilon_0 |
| `charged-particles-in-fields` (order 2) | EM2 | `motion.py`: `boris`, `explicit_euler`, `cyclotron_frequency`, `larmor_radius`, `boris_frequency`, `boris_radius`, `drift_velocity`, `measured_angular_frequency`, `fitted_radius`, `guiding_centre_velocity` | gyration frequency against qB/m and against the Boris map's own frequency, converging with order two; radius against m v/(qB); energy kept by Boris, grown by explicit Euler as the formula says; the E x B drift |
| `faradays-law-and-induction` (order 3) | EM3 | `induction.py`: `Rectangle`, `flux`, `emf`, `flux_rate`, `flux_tube_fields`, `rotating_coil` | the EMF of a loop moving through a non-uniform field (line integral of u x B) against -dPhi/dt; a rotating coil against both and against B A omega sin(omega t); a fixed loop at a changing flux tube (line integral of the induced E) against -dPhi/dt, inside and beside the tube |

## Decisions

| Decision | Reason |
|---|---|
| The EMF is computed as a line integral of the force per charge, the flux as a surface integral, by separate Gauss-Legendre rules, and -dPhi/dt by a central difference | The two sides of Faraday's law are computed independently, so the check is not a tautology |
| The induced field of the flux tube comes from a vector potential, E = -dA/dt, B = curl A, in closed form; the unit tests check the closed form against a numerical curl and time derivative | Independent of Faraday's law; the lesson then checks it for loops of another shape and place |
| Boris pusher for EM2, explicit Euler as the counter-example | Boris keeps the speed in a magnetic field and has a closed-form frequency and radius of its own, so the error can be predicted as well as measured |
| Orders fitted with `pbc.verification.estimates.fitted_order` | Reuse of the shared estimate, not a copy per course |
| Non-relativistic, SI units, CODATA constants | Stated under the assumptions and limits of the lessons |
| No change to the architecture, ADRs, curriculum file, or CI | The lessons fit the format 2 as is; slots EM1 to EM3 exist in `site/curriculum.yaml`, and the architecture already names `electromagnetism/` |
| `tests/unit/test_curriculum.py` updated | The published lessons that carry a slot, and the planned courses, change with this feature |

## Verification

- `tests/unit/test_electromagnetism.py`: each result against a closed form or a limit.
- `tests/unit/test_<name>_experiment.py`, one per lesson: the command writes
  what the page shows, the figure files are the encoder's bytes, and the
  lesson's science holds on the written results.
- `tests/lessons`, the single-page render of the three lessons: the lesson rule.
- `./scripts/verify.sh --base` (a new lesson changes what other pages show).
