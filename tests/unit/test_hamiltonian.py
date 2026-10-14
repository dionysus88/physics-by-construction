import numpy as np
import pytest
from scipy.constants import g

from pbc.mechanics.dynamics import State, euler_step, newton, simulate
from pbc.mechanics.energy import mechanical_energy
from pbc.mechanics.hamiltonian import (
    legendre_hamiltonian,
    loop_area,
    step_jacobian,
    symplectic_euler_modified_energy,
    verlet_oscillator_modified_energy,
)
from pbc.mechanics.integrators import rk4_step, symplectic_euler_step, verlet_step
from pbc.mechanics.lagrangian import coupled_springs_lagrangian, pendulum_lagrangian
from pbc.mechanics.oscillator import spring
from pbc.mechanics.pendulum import pendulum_force, pendulum_potential

MASS, K = 0.5, 2.0
OSCILLATOR = newton(MASS, spring(K))
PERIOD = 2 * np.pi / np.sqrt(K / MASS)


def spread(values):
    return np.max(np.abs(values / values[0] - 1.0))


def test_the_legendre_transform_of_the_pendulum_is_its_energy():
    hamiltonian = legendre_hamiltonian(pendulum_lagrangian(1.0, 1.0))
    q, p = np.array([0.9]), np.array([1.3])  # p = m L^2 qdot
    expected = 0.5 * p[0] ** 2 - g * np.cos(q[0])
    assert hamiltonian(q, p) == pytest.approx(expected, rel=1e-6)


def test_the_legendre_transform_of_coupled_springs_is_kinetic_plus_potential():
    mass, k, coupling = 0.5, 4.0, 1.5
    hamiltonian = legendre_hamiltonian(coupled_springs_lagrangian(mass, k, coupling))
    q, p = np.array([0.3, -0.2]), np.array([0.4, 0.1])
    expected = (
        p @ p / (2 * mass) + 0.5 * k * q @ q + 0.5 * coupling * (q[0] - q[1]) ** 2
    )
    assert hamiltonian(q, p) == pytest.approx(expected, rel=1e-6)


@pytest.mark.parametrize(
    ("step", "determinant"),
    [(symplectic_euler_step, 1.0), (verlet_step, 1.0)],
)
def test_symplectic_steps_have_determinant_one_for_any_step(step, determinant):
    pendulum = newton(1.0, pendulum_force(1.0, 1.0))
    for dt in (0.05, 0.3):
        jacobian = step_jacobian(step, State(0.0, [1.1], [0.4]), pendulum, dt)
        assert np.linalg.det(jacobian) == pytest.approx(determinant, abs=1e-8)


def test_other_methods_change_the_phase_space_area():
    state = State(0.0, [1.1], [0.4])
    dt = 0.1
    explicit = np.linalg.det(step_jacobian(euler_step, state, OSCILLATOR, dt))
    assert explicit == pytest.approx(1 + (K / MASS) * dt**2, rel=1e-6)
    runge_kutta = np.linalg.det(step_jacobian(rk4_step, state, OSCILLATOR, dt))
    assert 0.0 < runge_kutta < 1.0


def test_the_area_of_a_circle_of_starts_is_kept_by_a_symplectic_method():
    angles = np.linspace(0, 2 * np.pi, 400, endpoint=False)
    x0, v0 = 0.05 * np.cos(angles), 0.05 * np.sin(angles)
    area0 = loop_area(x0, v0)
    assert area0 == pytest.approx(np.pi * 0.05**2, rel=1e-3)
    pendulum = newton(1.0, pendulum_force(1.0, 1.0))
    ends = [
        simulate(State(0.0, [1.0 + a], [b]), pendulum, 0.1, 200, step=verlet_step)
        for a, b in zip(x0, v0, strict=True)
    ]
    x1 = np.array([e.x[-1, 0] for e in ends])
    v1 = np.array([e.v[-1, 0] for e in ends])
    start_loop = loop_area(1.0 + x0, v0)
    assert loop_area(x1, v1) == pytest.approx(start_loop, rel=2e-2)


@pytest.mark.parametrize("steps_per_period", [8, 32])
def test_symplectic_euler_conserves_its_modified_energy_of_lesson_l3(steps_per_period):
    dt = PERIOD / steps_per_period
    run = simulate(
        State(0.0, [1.0], [0.0]),
        OSCILLATOR,
        dt,
        20 * steps_per_period,
        step=symplectic_euler_step,
    )
    modified = symplectic_euler_modified_energy(
        run, MASS, lambda x: 0.5 * K * float(x @ x), lambda x: K * x, dt
    )
    assert spread(modified) < 1e-12
    assert spread(mechanical_energy(run, MASS, lambda x: 0.5 * K * float(x @ x))) > 1e-3


def test_velocity_verlet_conserves_its_modified_energy_of_lesson_m5():
    dt = PERIOD / 16
    run = simulate(State(0.0, [1.0], [0.0]), OSCILLATOR, dt, 320, step=verlet_step)
    assert spread(verlet_oscillator_modified_energy(run, MASS, K, dt)) < 1e-12


def test_the_modified_energy_of_the_pendulum_is_better_by_a_factor_of_the_step():
    # For a nonlinear force the first-order modified energy is conserved only
    # to second order: its band falls as dt^2, the band of E as dt.
    potential = pendulum_potential(1.0, 1.0)
    pendulum = newton(1.0, pendulum_force(1.0, 1.0))
    bands = []
    for steps in (50, 100):
        dt = 2 * np.pi / np.sqrt(g) / steps
        run = simulate(
            State(0.0, [1.0], [0.0]),
            pendulum,
            dt,
            20 * steps,
            step=symplectic_euler_step,
        )
        gradient = lambda x: g * np.sin(x)  # noqa: E731
        modified = symplectic_euler_modified_energy(run, 1.0, potential, gradient, dt)
        energy = mechanical_energy(run, 1.0, potential)
        bands.append((np.ptp(energy), np.ptp(modified)))
    assert bands[0][0] / bands[1][0] == pytest.approx(2.0, rel=0.2)
    assert bands[0][1] / bands[1][1] == pytest.approx(4.0, rel=0.3)
