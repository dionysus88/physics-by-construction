# Instructor pack: Numerical integrators

For the lesson
[Numerical integrators](https://taspinar.github.io/physics-by-construction/lessons/mechanics/05-numerical-integrators/).
The pack is free to use and adapt. The block between the markers below is
written from the lesson's front matter and from `CITATION.cff` by
`python -m pbc.authoring.educators`; do not edit it by hand, a test fails when
it differs. Everything outside the block is written by hand.

<!-- pack:start (written by pbc.authoring.educators) -->
Lesson: **Numerical integrators** (`numerical-integrators`, mechanics lesson 5). Difficulty 2: Intermediate.

### Learning objectives

After the lesson a student can:

- Step a system with explicit Euler, symplectic Euler, velocity Verlet, and Runge-Kutta 4 behind one interface
- Compare integrators for accuracy, energy behaviour, and cost
- Choose an integrator for what a simulation has to be trusted for

### Prerequisites

- Lesson: The harmonic oscillator
- Outside the site: Complex numbers: modulus, argument, and the exponential of an imaginary number
- Outside the site: Calculus: Taylor expansion to fourth order
- Outside the site: Linear algebra: the determinant and the trace of a two-by-two matrix

### Citation

Cite the project as:

> Taspinar, A. "Physics by Construction". https://taspinar.github.io/physics-by-construction/
<!-- pack:end -->

## Approximate time

- Reading the lesson and running its listings: 90 minutes.
- The assignment below: 60 to 90 minutes.
- As a 2-hour session: 30 minutes of discussion of the stability limits and the
  energy behaviour, then the assignment in pairs.

## Lecturer guide

The lesson answers one question: which fixed-step method should a simulation
use, given what it has to be trusted for. Three ideas carry it.

1. **Order** says how fast the error shrinks with the step. The observed order
   is the base-two logarithm of the ratio of two errors for step sizes a factor
   two apart. Have students predict 1, 1, 2, 4 before measuring.
2. **Energy over a long run** is a different question from accuracy over a short
   one. Explicit Euler multiplies the energy by `1 + ω²Δt²` every step.
   Symplectic Euler and velocity Verlet keep it in a band. Runge-Kutta 4 drains
   it slowly.
3. **Cost** is counted in calls to the acceleration, not in seconds, so the
   comparison does not depend on the machine.

Common difficulties: students read "stable" as "accurate" (the lesson's first
exercise shows Runge-Kutta stable but nearly drained at 3.5 steps per period);
they compare methods at equal step instead of equal cost; they measure the
error of the position at one instant, which hides a phase error at a turning
point, so the assignment uses the error in the phase plane.

Suggested sequence: the explanation section, the four-methods worked example,
then the assignment. The lesson's exercises are a source of further questions.

## Assignment

The oscillator of the lesson: mass 0.5 kg, spring constant 2 N/m, released at
rest from 1 m. Use the four methods of `pbc.mechanics.integrators.INTEGRATORS`.

1. **Order.** For each method simulate two periods with 80, 160, and 320 steps
   per period. Measure the largest distance to the exact motion
   (`pbc.mechanics.oscillator.harmonic_motion`) in the phase plane (ωx, v), and
   report the observed order. Say which of the four are as the lesson states.
2. **Equal cost.** Give each method 200 calls to the acceleration per period.
   Simulate 100 periods and report the energy at the end relative to the start.
3. **Recommendation.** In at most five sentences, recommend a method for
   (a) the position after two periods and (b) the energy after one hundred
   periods, and justify each with your measurements.

## Rubric

| Criterion | Full marks | Partial | None |
|---|---|---|---|
| Order measured (4) | All four orders from three step sizes, error measured against the exact motion | Orders from two step sizes, or a measure that hides phase error | No measurement |
| Equal cost (3) | Steps per period 200, 200, 100, 50 for the four methods, energy ratio reported | Equal step instead of equal cost | Not done |
| Reading the result (2) | Notes that only explicit Euler leaves the energy band and that Runge-Kutta 4 drains slowly | One of the two | Neither |
| Recommendation (3) | Different methods may be chosen for (a) and (b); each justified by a number from the student's own run | Recommendation without a number | No recommendation |

## Reference solution

The reference solution is code that the build runs:
[`tests/unit/test_instructor_pack_numerical_integrators.py`](../../tests/unit/test_instructor_pack_numerical_integrators.py).
It asserts the figures below, so the pack cannot say something the code no
longer does.

- Observed orders: about 1.1 (explicit Euler), 1.0 (symplectic Euler), 2.0
  (velocity Verlet), 4.0 (Runge-Kutta 4). Explicit Euler is nearer to 1 the
  smaller the step; at 20 steps per period it reads 1.6, which is why the
  assignment starts at 80.
- Energy after 100 periods at 200 calls per period, relative to the start:
  explicit Euler above 10⁶; symplectic Euler within 0.1 per cent; velocity
  Verlet within 0.002 per cent; Runge-Kutta 4 at 0.9997.
- Recommendation: Runge-Kutta 4 for (a), velocity Verlet for (b). A student who
  chooses Runge-Kutta 4 for (b) with the number 0.9997 has a defensible answer
  for 100 periods; the ranking changes for longer runs.

## Accessibility notes

- Lesson text, code, and equations (MathML) are readable with JavaScript
  turned off. Figures have a caption and a text alternative that states what
  they show; the four methods are told apart by line style and marker as well
  as by colour. The interactive visualization is optional.
- The assignment needs a terminal and a text editor; no mouse-only step. A
  student who cannot use the interactive widget misses nothing the assignment
  needs.
- The longest run of the assignment is 20 000 steps; it takes seconds, so no
  student needs a fast machine.

## Pathway without AI

The assignment needs no AI tool and no account. Everything runs from a clone of
the repository, set up as the lesson's "Reproduce this" section describes.
Students who use an assistant should state where; the rubric rewards the
student's own numbers and reading of them, which an assistant cannot supply
without running the code.

## Reuse and citation

- Lesson text, figures, and this pack are under
  [CC BY 4.0](https://github.com/taspinar/physics-by-construction/blob/main/LICENSE-CONTENT);
  code is under the
  [MIT licence](https://github.com/taspinar/physics-by-construction/blob/main/LICENSE).
  Give credit, link to the licence, and indicate changes.
- Cite as in the block above.
- The project makes no claim about who uses it. Use needs no registration and
  no contact.

## Suggest an improvement

Open an Issue in the
[repository](https://github.com/taspinar/physics-by-construction/issues/new/choose)
with the **Scientific correction** form for a wrong statement or number, or the
**Bug** form for a listing or solution that does not run. Say which part of the
pack is concerned. No form asks for contact details.
