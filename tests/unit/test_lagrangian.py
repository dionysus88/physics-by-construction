import numpy as np
import pytest
from scipy.constants import g

from pbc.mechanics.chaos import double_pendulum
from pbc.mechanics.dynamics import State, newton, simulate
from pbc.mechanics.integrators import rk4_step
from pbc.mechanics.lagrangian import (
    coupled_springs_lagrangian,
    double_pendulum_lagrangian,
    energy_function,
    euler_lagrange,
    generalised_momentum,
    pendulum_lagrangian,
)
from pbc.mechanics.oscillator import spring
from pbc.mechanics.pendulum import pendulum_force, pendulum_period

MASS, LENGTH = 1.0, 1.0


def test_a_particle_in_a_spring_gives_newtons_second_law():
    def lagrangian(q, qdot):
        return 0.5 * 2.0 * float(qdot @ qdot) - 0.5 * 3.0 * float(q @ q)

    acceleration = euler_lagrange(lagrangian)(0.0, np.array([0.4]), np.array([1.1]))
    assert acceleration[0] == pytest.approx(-3.0 * 0.4 / 2.0, rel=1e-6)


@pytest.mark.parametrize("angle", [0.1, 1.0, 2.5, -2.0])
def test_the_pendulum_lagrangian_gives_the_tangential_weight(angle):
    # The Newtonian form: the force along the arc, m a = -m g sin(theta).
    from_lagrangian = euler_lagrange(pendulum_lagrangian(MASS, LENGTH))(
        0.0, np.array([angle]), np.array([0.7])
    )
    force = pendulum_force(MASS, LENGTH)(
        0.0, np.array([LENGTH * angle]), np.array([0.0])
    )
    assert LENGTH * from_lagrangian[0] == pytest.approx(force[0] / MASS, rel=1e-6)


def test_the_simulated_pendulum_has_the_period_of_the_elliptic_integral():
    amplitude = 1.5
    run = simulate(
        State(t=0.0, x=[amplitude], v=[0.0]),
        euler_lagrange(pendulum_lagrangian(MASS, LENGTH)),
        0.01,
        400,
        step=rk4_step,
    )
    below = np.where((run.x[:-1, 0] > 0) & (run.x[1:, 0] <= 0))[0][0]
    fraction = run.x[below, 0] / (run.x[below, 0] - run.x[below + 1, 0])
    quarter = run.t[below] + fraction * 0.01
    assert 4 * quarter == pytest.approx(pendulum_period(LENGTH, amplitude), rel=1e-5)


def test_coupled_springs_have_the_normal_mode_frequencies():
    mass, k, coupling = 0.5, 4.0, 1.5
    acceleration = euler_lagrange(coupled_springs_lagrangian(mass, k, coupling))
    # In phase the coupling spring is not stretched; out of phase it is twice.
    for mode, stiffness in (([1.0, 1.0], k), ([1.0, -1.0], k + 2 * coupling)):
        q = np.array(mode) * 0.3
        a = acceleration(0.0, q, np.zeros(2))
        assert a == pytest.approx(-stiffness / mass * q, rel=1e-6)


def test_coupled_springs_match_newtons_laws_for_the_forces():
    mass, k, coupling = 0.5, 4.0, 1.5
    q, qdot = np.array([0.3, -0.1]), np.array([0.2, 0.5])
    from_lagrangian = euler_lagrange(coupled_springs_lagrangian(mass, k, coupling))(
        0.0, q, qdot
    )
    wall = spring(k)(0.0, q, qdot)
    between = coupling * np.array([-(q[0] - q[1]), q[0] - q[1]])
    expected = newton(mass, lambda t, x, v: wall + between)(0.0, q, qdot)
    assert from_lagrangian == pytest.approx(expected, rel=1e-6)


def test_the_lagrangian_double_pendulum_is_the_closed_form():
    masses, lengths = (1.0, 2.0), (1.0, 0.7)
    from_lagrangian = euler_lagrange(double_pendulum_lagrangian(*masses, *lengths))
    closed_form = double_pendulum(*masses, *lengths)
    rng = np.random.default_rng(1)
    for _ in range(10):
        q, qdot = rng.uniform(-3, 3, 2), rng.uniform(-3, 3, 2)
        assert from_lagrangian(0.0, q, qdot) == pytest.approx(
            closed_form(0.0, q, qdot), rel=1e-5, abs=1e-5
        )


def test_the_momentum_of_a_cyclic_coordinate_is_conserved():
    # A free particle on a line: x does not appear in L, so p = m v is constant.
    def lagrangian(q, qdot):
        return 0.5 * 2.0 * float(qdot @ qdot)

    p = generalised_momentum(lagrangian, np.array([3.0]), np.array([1.5]))
    assert p[0] == pytest.approx(3.0)


def test_the_energy_function_is_kinetic_plus_potential():
    q, qdot = np.array([0.8]), np.array([1.2])
    energy = energy_function(pendulum_lagrangian(MASS, LENGTH), q, qdot)
    # The potential of this Lagrangian is -m g L cos(theta): the energy of
    # lesson M6 less the constant m g L.
    expected = 0.5 * MASS * LENGTH**2 * qdot[0] ** 2 - MASS * g * LENGTH * np.cos(q[0])
    assert energy == pytest.approx(expected, rel=1e-6)
