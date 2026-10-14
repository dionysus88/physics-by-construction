import numpy as np
import pytest
from scipy.constants import g

from pbc.mechanics.chaos import (
    double_pendulum,
    double_pendulum_energy,
    lyapunov_exponent,
)
from pbc.mechanics.dynamics import State, simulate
from pbc.mechanics.integrators import rk4_step

# The double pendulum of lesson M9: unit masses on unit rods.
ACCELERATION = double_pendulum(1.0, 1.0, 1.0, 1.0)
DT = 0.01


def released(first: float, second: float) -> State:
    return State(t=0.0, x=[first, second], v=[0.0, 0.0])


def test_the_equations_reduce_to_the_single_pendulum_when_the_second_bob_is_light():
    # With a negligible second mass the first rod is a plain pendulum.
    light = double_pendulum(1.0, 1e-12, 1.0, 1.0)
    a = light(0.0, np.array([0.7, -0.2]), np.array([0.0, 0.0]))
    assert a[0] == pytest.approx(-g * np.sin(0.7))


@pytest.mark.parametrize(
    ("ratio", "factor"),
    [(np.sqrt(2.0), 2.0 - np.sqrt(2.0)), (-np.sqrt(2.0), 2.0 + np.sqrt(2.0))],
)
def test_small_oscillations_have_the_normal_mode_frequencies(ratio, factor):
    # Equal masses and rods: omega^2 = (g / L) (2 -+ sqrt 2). In the slow mode
    # the outer angle is sqrt 2 times the inner, in the fast mode minus that.
    start = State(t=0.0, x=[0.001, 0.001 * ratio], v=[0.0, 0.0])
    run = simulate(start, ACCELERATION, 0.002, 4000, step=rk4_step)
    omega = np.sqrt(g * factor)
    assert np.max(np.abs(run.x[:, 0] - 0.001 * np.cos(omega * run.t))) < 2e-6


def test_the_energy_is_kept_by_a_small_step():
    run = simulate(released(2.0, 2.0), ACCELERATION, DT, 2000, step=rk4_step)
    energy = double_pendulum_energy(run.x, run.v, 1.0, 1.0, 1.0, 1.0)
    assert np.max(np.abs(energy - energy[0])) / abs(energy[0]) < 1e-3


def test_the_estimator_recovers_the_exponent_of_a_hyperbolic_point():
    # a = lambda^2 x has the exponent lambda along the growing direction.
    rate = 1.3
    estimate = lyapunov_exponent(
        State(t=0.0, x=[0.0], v=[0.0]),
        lambda t, x, v: rate**2 * x,
        dt=0.01,
        n_steps=3000,
        separation=1e-6,
    )
    assert estimate.exponent == pytest.approx(rate, rel=3e-3)


def test_the_exponent_of_a_regular_motion_falls_towards_zero():
    estimate = lyapunov_exponent(released(0.2, 0.2), ACCELERATION, DT, 5000)
    half, full = (np.searchsorted(estimate.t, t) - 1 for t in (25.0, 50.0))
    assert estimate.exponent < 0.05
    assert estimate.running[full] < estimate.running[half]


def test_the_exponent_of_a_chaotic_motion_is_positive_and_settles():
    estimate = lyapunov_exponent(released(2.0, 2.0), ACCELERATION, DT, 5000)
    half = np.searchsorted(estimate.t, 25.0) - 1
    assert estimate.exponent > 0.5
    assert estimate.running[half] == pytest.approx(estimate.exponent, rel=0.2)


def test_the_estimator_rejects_a_run_shorter_than_one_rescaling():
    with pytest.raises(ValueError):
        lyapunov_exponent(released(1.0, 1.0), ACCELERATION, DT, 5, rescale_every=10)
