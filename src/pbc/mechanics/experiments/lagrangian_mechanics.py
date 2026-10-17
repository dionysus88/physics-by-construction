"""The experiment of the lesson "Lagrangian mechanics".

Equations of motion from a Lagrangian by differentiation
(``pbc.mechanics.lagrangian``), checked against Newton's law for the
pendulum and two coupled springs, against Kepler for a planet in polar
coordinates, and against the closed form of the double pendulum. Run it as a
program to write the figure and numbers of the page:

    uv run --locked --no-dev \\
        python -m pbc.mechanics.experiments.lagrangian_mechanics out
"""

from functools import partial

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from scipy.constants import g

from pbc.authoring import FIGURE_COLOURS
from pbc.experiment import Experiment, main
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

# region: setup
mass, length = 1.0, 1.0
from_lagrangian = euler_lagrange(pendulum_lagrangian(mass, length))
newtonian = newton(mass, pendulum_force(mass, length))
# endregion: setup
# region: double-pendulum
masses, lengths = (1.0, 2.0), (1.0, 0.7)
closed_form = double_pendulum(*masses, *lengths)
# endregion: double-pendulum


def pendulum_check(experiment: Experiment) -> list:
    """The acceleration of the pendulum bob along the arc at four angles,
    from Newton's law and from the Lagrangian; record the table and return
    its rows."""
    rows = []
    for angle in (0.1, 1.0, 2.0, 3.0):
        theta, rate = np.array([angle]), np.array([0.7])
        a_lagrange = length * from_lagrangian(0.0, theta, rate)[0]
        a_newton = newtonian(0.0, length * theta, rate)[0]
        rows.append((angle, a_newton, a_lagrange, abs(a_lagrange / a_newton - 1.0)))

    experiment.table(
        "pendulum-check",
        rows,
        columns=[
            ("angle", "rad", ".1f"),
            ("acceleration along the arc, Newton", "m/s²", ".5f"),
            ("from the Lagrangian", "m/s²", ".5f"),
            ("relative difference", "", ".1e"),
        ],
        caption="Acceleration of the pendulum bob along the arc at four angles, "
        "from the tangential weight and from the Euler-Lagrange equation, with "
        "the relative difference.",
    )
    return rows


def pendulum_period_check(experiment: Experiment):
    """The period of the Lagrangian pendulum at a large amplitude, from a
    quarter swing; record the table."""
    amplitude = 1.5  # rad
    dt = 0.01  # s
    swing = simulate(
        State(0.0, [amplitude], [0.0]), from_lagrangian, dt, 400, step=rk4_step
    )
    below = np.where((swing.x[:-1, 0] > 0) & (swing.x[1:, 0] <= 0))[0][0]
    quarter = (
        swing.t[below]
        + swing.x[below, 0] / (swing.x[below, 0] - swing.x[below + 1, 0]) * dt
    )

    experiment.table(
        "pendulum-period",
        [(amplitude, pendulum_period(length, amplitude), 4 * quarter)],
        columns=[
            ("amplitude", "rad", ".1f"),
            ("period, elliptic integral", "s", ".5f"),
            ("period, simulation", "s", ".5f"),
        ],
        caption="Period of the Lagrangian pendulum at a large amplitude, from the "
        "closed form and from the simulation, to five decimals.",
    )
    return amplitude, quarter


def coupled_springs() -> float:
    """Ten seconds of the coupled springs from the Lagrangian against Newton's
    law; the largest difference of the paths, in m."""
    m_spring, k_wall, k_mid = 0.5, 4.0, 1.5
    springs = euler_lagrange(coupled_springs_lagrangian(m_spring, k_wall, k_mid))

    wall = spring(k_wall)

    def between(t, x, v):
        return k_mid * np.array([-(x[0] - x[1]), x[0] - x[1]])

    newtonian_springs = newton(m_spring, wall, between)
    start = State(0.0, [0.3, -0.1], [0.2, 0.5])
    by_lagrange = simulate(start, springs, 0.01, 1000, step=rk4_step)
    by_newton = simulate(start, newtonian_springs, 0.01, 1000, step=rk4_step)
    return np.max(np.abs(by_lagrange.x - by_newton.x))


def planet_lagrangian(gm, m):
    """Polar coordinates (r, phi): L = m (r'^2 + r^2 phi'^2) / 2 + G M m / r."""

    def lagrangian(q, qdot):
        return 0.5 * m * (qdot[0] ** 2 + q[0] ** 2 * qdot[1] ** 2) + gm * m / q[0]

    return lagrangian


def planet(experiment: Experiment):
    """One orbit of a planet from its Lagrangian in polar coordinates, with
    its angular momentum and energy; record the table and return the run,
    the momenta, and the turns of the angle."""
    gm, m_planet = 4.0, 1.0
    r0, speed = 1.0, 1.5
    orbit = euler_lagrange(planet_lagrangian(gm, m_planet))
    planet_energy = 0.5 * m_planet * speed**2 - gm * m_planet / r0
    semi_major = -gm * m_planet / (2.0 * planet_energy)
    orbital_period = 2.0 * np.pi * np.sqrt(semi_major**3 / gm)

    start = State(0.0, [r0, 0.0], [0.0, speed / r0])
    steps = round(orbital_period / 0.005)
    orbit_run = simulate(start, orbit, orbital_period / steps, steps, step=rk4_step)
    lagr = planet_lagrangian(gm, m_planet)
    momentum = np.array(
        [
            generalised_momentum(lagr, x, v)[1]
            for x, v in zip(orbit_run.x, orbit_run.v, strict=True)
        ]
    )
    energies = np.array(
        [
            energy_function(lagr, x, v)
            for x, v in zip(orbit_run.x, orbit_run.v, strict=True)
        ]
    )
    turns = (orbit_run.x[-1, 1] - orbit_run.x[0, 1]) / (2 * np.pi)

    experiment.table(
        "planet",
        [
            (
                "angular momentum",
                momentum[0],
                np.max(np.abs(momentum / momentum[0] - 1.0)),
            ),
            ("energy", energies[0], np.max(np.abs(energies / energies[0] - 1.0))),
        ],
        columns=[
            ("quantity", "", ""),
            ("start", "", ".5f"),
            ("largest relative change", "", ".1e"),
        ],
        caption="Angular momentum and energy of the planet over one orbit, from "
        "the Lagrangian, at the start and the largest relative change.",
    )
    return orbit_run, momentum, turns


def draw_planet_orbit(orbit_run) -> Figure:
    """The orbit in the plane."""
    x_plane = orbit_run.x[:, 0] * np.cos(orbit_run.x[:, 1])
    y_plane = orbit_run.x[:, 0] * np.sin(orbit_run.x[:, 1])
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.plot(x_plane, y_plane, color=FIGURE_COLOURS[0], linestyle="-", label="orbit")
    ax.plot(
        [0.0],
        [0.0],
        marker="*",
        color=FIGURE_COLOURS[1],
        linestyle="",
        markersize=10,
        label="centre",
    )
    ax.plot(
        [x_plane[0]],
        [y_plane[0]],
        marker="o",
        color=FIGURE_COLOURS[2],
        linestyle="",
        label="start",
    )
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.legend(loc="upper right")
    return fig


def double_pendulum_check(experiment: Experiment) -> None:
    """The double pendulum from its Lagrangian against the closed form, at
    two hundred random states and along one regular motion; record the
    table."""
    derived = euler_lagrange(double_pendulum_lagrangian(*masses, *lengths))

    rng = np.random.default_rng(7)
    worst = 0.0
    for _ in range(200):
        q, qdot = rng.uniform(-3.0, 3.0, 2), rng.uniform(-3.0, 3.0, 2)
        a_closed, a_derived = closed_form(0.0, q, qdot), derived(0.0, q, qdot)
        worst = max(
            worst, np.max(np.abs(a_derived - a_closed) / (1.0 + np.abs(a_closed)))
        )

    regular = State(0.0, [0.3, 0.2], [0.0, 0.0])
    path_closed = simulate(regular, closed_form, 0.01, 1000, step=rk4_step)
    path_derived = simulate(regular, derived, 0.01, 1000, step=rk4_step)
    path_difference = np.max(np.abs(path_closed.x - path_derived.x))

    experiment.table(
        "double-pendulum-check",
        [(worst, path_difference)],
        columns=[
            ("largest relative difference of the accelerations", "", ".1e"),
            ("largest difference of the angles over ten seconds", "rad", ".1e"),
        ],
        caption="The equations of the double pendulum from the Lagrangian against "
        "the closed form of the previous lesson, at two hundred random states and "
        "along one regular motion.",
    )


# region: atwood
m_heavy, m_light = 3.0, 1.0
# endregion: atwood


def atwood(q, qdot):
    return 0.5 * (m_heavy + m_light) * qdot[0] ** 2 + (m_heavy - m_light) * g * q[0]


def atwood_machine(experiment: Experiment) -> None:
    """Exercise 1: the acceleration of the Atwood machine from Newton's law
    and from the Lagrangian; record the table."""
    a_program = euler_lagrange(atwood)(0.0, np.array([0.0]), np.array([0.0]))[0]
    a_exact = (m_heavy - m_light) / (m_heavy + m_light) * g

    experiment.table(
        "atwood",
        [(a_exact, a_program, abs(a_program / a_exact - 1.0))],
        columns=[
            ("from Newton's law", "m/s²", ".5f"),
            ("from the Lagrangian", "m/s²", ".5f"),
            ("relative difference", "", ".1e"),
        ],
        caption="Acceleration of the Atwood machine from the tension of the rope "
        "and from the Lagrangian, to five decimals.",
    )


def difference_steps(experiment: Experiment) -> list:
    """Exercise 2: the accelerations of the double pendulum for five
    difference steps against the closed form; record the table and return
    its rows."""
    rows = []
    for h in (1e-1, 1e-2, 1e-3, 1e-4, 1e-5):
        candidate = euler_lagrange(double_pendulum_lagrangian(*masses, *lengths), h=h)
        rng = np.random.default_rng(7)
        worst_h = 0.0
        for _ in range(50):
            q, qdot = rng.uniform(-3.0, 3.0, 2), rng.uniform(-3.0, 3.0, 2)
            a_closed = closed_form(0.0, q, qdot)
            worst_h = max(
                worst_h,
                np.max(
                    np.abs(candidate(0.0, q, qdot) - a_closed)
                    / (1.0 + np.abs(a_closed))
                ),
            )
        rows.append((h, worst_h))

    experiment.table(
        "difference-steps",
        rows,
        columns=[
            ("difference step", "rad", ".0e"),
            ("largest relative difference", "", ".1e"),
        ],
        caption="Largest relative difference between the accelerations from the "
        "Lagrangian and the closed form, for five difference steps.",
    )
    return rows


def run() -> Experiment:
    """Everything the lesson's page shows."""
    experiment = Experiment()
    rows = pendulum_check(experiment)
    experiment.number("pendulum-difference", max(r[3] for r in rows), ".0e")
    amplitude, quarter = pendulum_period_check(experiment)
    experiment.number(
        "period-difference",
        abs(4 * quarter / pendulum_period(length, amplitude) - 1.0),
        ".0e",
    )
    experiment.number("path-gap", coupled_springs(), ".0e")

    orbit_run, momentum, turns = planet(experiment)
    experiment.number(
        "momentum-change", np.max(np.abs(momentum / momentum[0] - 1.0)), ".0e"
    )
    experiment.number("final-radius", orbit_run.x[-1, 0], ".5f")
    experiment.number("turns", turns, ".5f")
    experiment.figure("fig-planet-orbit", partial(draw_planet_orbit, orbit_run))

    double_pendulum_check(experiment)
    atwood_machine(experiment)
    experiment.number("tension", 2 * m_heavy * m_light / (m_heavy + m_light) * g, ".2f")
    rows = difference_steps(experiment)
    experiment.number("best-step", min(rows, key=lambda r: r[1])[0], ".0e")
    return experiment


if __name__ == "__main__":
    main(run)
