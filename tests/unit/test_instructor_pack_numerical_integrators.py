"""The reference solution of the assignment in the instructor pack of the
lesson "Numerical integrators" (docs/instructor-packs/numerical-integrators.md).

The pack's assignment asks for the observed order of each method and for the
energy after 100 periods at a budget of 200 calls to the acceleration per
period. This file is the solution; the pack states the figures it asserts, so
a change in a method that would make the pack wrong fails here.
"""

import numpy as np

from pbc.mechanics.dynamics import State, newton, simulate
from pbc.mechanics.integrators import INTEGRATORS
from pbc.mechanics.oscillator import angular_frequency, energy, harmonic_motion, spring

MASS = 0.5  # kg
K = 2.0  # N/m
OMEGA = angular_frequency(MASS, K)
PERIOD = 2 * np.pi / OMEGA
RELEASED = State(t=0.0, x=[1.0], v=[0.0])
OSCILLATOR = newton(MASS, spring(K))
BUDGET = 200  # calls to the acceleration per period


def part_one_orders() -> dict[str, float]:
    """Observed order: the error over two periods at 80, 160, and 320 steps per
    period, in the phase plane (omega x, v), and the mean of the two ratios."""
    orders = {}
    for integrator in INTEGRATORS:
        errors = []
        for per_period in (80, 160, 320):
            run = simulate(
                RELEASED,
                OSCILLATOR,
                PERIOD / per_period,
                2 * per_period,
                step=integrator.step,
            )
            exact = harmonic_motion(RELEASED, MASS, K, run.t)
            distance = np.hypot(OMEGA * (run.x - exact.x), run.v - exact.v)
            errors.append(float(np.max(distance)))
        orders[integrator.name] = float(
            np.mean(np.log2(np.array(errors[:-1]) / errors[1:]))
        )
    return orders


def part_two_energy() -> dict[str, float]:
    """Energy after 100 periods over the initial energy, equal cost."""
    ratios = {}
    for integrator in INTEGRATORS:
        per_period = BUDGET // integrator.evaluations
        run = simulate(
            RELEASED,
            OSCILLATOR,
            PERIOD / per_period,
            100 * per_period,
            step=integrator.step,
        )
        relative = energy(run, MASS, K) / energy(run, MASS, K)[0]
        ratios[integrator.name] = float(relative[-1])
    return ratios


def test_part_one_orders_are_the_orders_the_lesson_states():
    orders = part_one_orders()
    for integrator in INTEGRATORS:
        assert abs(orders[integrator.name] - integrator.order) < 0.3, integrator.name


def test_part_two_only_explicit_euler_leaves_the_energy_band():
    ratios = part_two_energy()
    # Explicit Euler feeds energy in at every step: by many orders of magnitude.
    assert ratios["explicit Euler"] > 1e6
    # The symplectic methods stay in a band around the initial energy.
    assert abs(ratios["symplectic Euler"] - 1) < 1e-3
    assert abs(ratios["velocity Verlet"] - 1) < 2e-5
    # Runge-Kutta 4 drains energy slowly, and is the most accurate of the four
    # after two periods, which is the trade the recommendation turns on.
    # The pack states 0.9997, so the figure is checked to its displayed precision.
    assert abs(ratios["Runge-Kutta 4"] - 0.9997) < 5e-5
