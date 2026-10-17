"""The experiment of the lesson "The harmonic oscillator".

A mass on a spring simulated with explicit Euler (``pbc.mechanics.dynamics``)
against the exact motion (``pbc.mechanics.oscillator``): the growth of its
energy by a fixed factor per step, a damped spring, and an orbit in a plane.
Run it as a program to write the figures and numbers of the page:

    uv run --locked --no-dev \\
        python -m pbc.mechanics.experiments.harmonic_oscillator out
"""

from functools import partial

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.patches import Ellipse

from pbc.authoring import FIGURE_COLOURS
from pbc.authoring.design import PAGE
from pbc.authoring.diagrams import INK, arrow, canvas, circle, text
from pbc.experiment import Experiment, main
from pbc.mechanics.drag import linear_drag
from pbc.mechanics.dynamics import State, Trajectory, newton, simulate
from pbc.mechanics.oscillator import (
    angular_frequency,
    energy,
    euler_energy_growth,
    harmonic_motion,
    spring,
)

# region: setup
mass = 0.5  # kg
k = 2.0  # spring constant, N/m
omega = angular_frequency(mass, k)
period = 2 * np.pi / omega
released = State(t=0.0, x=1.0, v=0.0)  # pulled out 1 m and let go
oscillator = newton(mass, spring(k))

steps_per_period = 64
dt = period / steps_per_period
n_periods = 3
# endregion: setup


def draw_oscillator_energy_ellipse() -> Figure:
    """The orbit of constant energy in phase space, as a sketch."""
    fig, ax = canvas(6.4, 4.4, (-5.8, 7.4), (-3.4, 3.9))
    arrow(ax, (-5.2, 0.0), (6.9, 0.0), colour=PAGE["muted"])
    arrow(ax, (-5.2, 0.0), (-5.2, 3.6), colour=PAGE["muted"])
    text(ax, (6.9, -0.18), "position $x$", colour=PAGE["muted"], ha="right")
    text(ax, (-5.1, 3.6), "velocity $v$", colour=PAGE["muted"], ha="left")
    ax.add_patch(
        Ellipse(
            (0, 0), 6.4, 4.4, fill=False, edgecolor=FIGURE_COLOURS[0], linewidth=1.6
        )
    )
    arrow(ax, (-0.6, 2.2), (0.6, 2.2), colour=FIGURE_COLOURS[0])
    arrow(ax, (0.6, -2.2), (-0.6, -2.2), colour=FIGURE_COLOURS[0])
    for point in ((3.2, 0.0), (0.0, 2.2), (-3.2, 0.0), (0.0, -2.2)):
        circle(ax, point, 0.12, colour=INK, filled=True)
    text(
        ax, (3.6, 0.7), "turning point:\nall energy in the spring", ha="left", colour=1
    )
    text(ax, (0.0, 2.75), "passing the centre: all energy in motion", colour=1)
    text(ax, (-1.2, -1.2), "one orbit,\none energy", colour=0)
    return fig


def three_periods(experiment: Experiment) -> tuple[Trajectory, Trajectory]:
    """Three periods with explicit Euler and the exact motion at the same
    instants; record the table of every half period."""
    euler = simulate(released, oscillator, dt, n_periods * steps_per_period)
    exact = harmonic_motion(released, mass, k, euler.t)

    experiment.table(
        "three-periods",
        [
            (
                euler.t[i],
                euler.x[i, 0],
                exact.x[i, 0],
                euler.v[i, 0],
                exact.v[i, 0],
            )
            for i in range(steps_per_period // 8, len(euler.t), steps_per_period // 2)
        ],
        columns=[
            ("t", "s", ".2f"),
            ("x Euler", "m", ".3f"),
            ("x exact", "m", ".3f"),
            ("v Euler", "m/s", ".3f"),
            ("v exact", "m/s", ".3f"),
        ],
        caption="Position and velocity of the mass on the spring, simulated and "
        "exact, every half period; to three decimals.",
    )
    return euler, exact


def draw_oscillator_position(euler: Trajectory) -> Figure:
    """The position against time, explicit Euler against exact."""
    fine = np.linspace(0.0, euler.t[-1], 1001)

    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.plot(
        fine,
        harmonic_motion(released, mass, k, fine).x[:, 0],
        color="#00429d",
        label="exact",
    )
    ax.plot(
        euler.t,
        euler.x[:, 0],
        color="#93003a",
        linestyle="--",
        label=f"explicit Euler, {steps_per_period} steps per period",
    )
    ax.set_xlabel("time (s)")
    ax.set_ylabel("position (m)")
    ax.legend(loc="upper left")
    return fig


def draw_oscillator_phase_space(euler: Trajectory, exact: Trajectory) -> Figure:
    """The orbit in phase space, explicit Euler against exact."""
    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    ax.plot(exact.x[:, 0], exact.v[:, 0], color="#00429d", label="exact")
    ax.plot(
        euler.x[:, 0],
        euler.v[:, 0],
        color="#93003a",
        linestyle="--",
        label="explicit Euler",
    )
    ax.plot(
        released.x[0],
        released.v[0],
        color="#555555",
        marker="o",
        linestyle="none",
        label="start",
    )
    ax.set_xlabel("position (m)")
    ax.set_ylabel("velocity (m/s)")
    ax.set_aspect(1 / omega)
    ax.legend(loc="upper left")
    return fig


def energy_ratios(euler: Trajectory):
    """The energy at every step, the ratio of successive energies, the
    derived factor, and the largest deviation of a ratio from it."""
    energies = energy(euler, mass, k)
    ratios = energies[1:] / energies[:-1]
    factor = euler_energy_growth(mass, k, dt)

    deviation = np.max(np.abs(ratios - factor))
    return energies, ratios, factor, deviation


def draw_oscillator_energy_growth(initial_energy: float) -> Figure:
    """The energy over three periods for three time steps, on a log axis."""
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    for n, style in ((32, "-"), (64, "--"), (128, ":")):
        run = simulate(released, oscillator, period / n, n_periods * n)
        growth = energy(run, mass, k) / initial_energy
        ax.semilogy(
            run.t,
            growth,
            color="#93003a",
            linestyle=style,
            label=f"{n} steps per period",
        )
    ax.set_xlabel("time (s)")
    ax.set_ylabel("energy / initial energy")
    ax.legend(loc="upper left")
    return fig


def energy_growth(experiment: Experiment):
    """The energy growth over three periods for each time step and the
    observed order of its logarithm; record the table."""
    step_counts = [32 * 2**i for i in range(8)]
    growths = []
    for n in step_counts:
        run = simulate(released, oscillator, period / n, n_periods * n)
        end = energy(run, mass, k)
        growths.append(end[-1] / end[0])
    log_growths = np.log(growths)
    orders = np.log2(log_growths[:-1] / log_growths[1:])

    experiment.table(
        "energy-growth",
        [
            (
                n,
                2 * np.pi / n,
                growths[i],
                log_growths[i],
                orders[i - 1] if i else None,
            )
            for i, n in enumerate(step_counts)
        ],
        columns=[
            ("steps per period", "", "d"),
            ("omega dt", "", ".5f"),
            ("energy growth", "", ".4f"),
            ("ln(growth)", "", ".5f"),
            ("observed order", "", ".3f"),
        ],
        caption="Energy growth over three periods for each time step, its "
        "logarithm, and the observed order of that logarithm against the step.",
    )
    return step_counts, growths


def one_per_cent():
    """Exercise 1: the steps per period that hold the energy within one per
    cent over ten periods, and the growth with them, in per cent."""
    largest_omega_dt = np.log(1.01) / (20 * np.pi)
    needed = int(np.ceil(2 * np.pi / largest_omega_dt))
    run = simulate(released, oscillator, period / needed, 10 * needed)
    end = energy(run, mass, k)
    growth_percent = 100 * (end[-1] / end[0] - 1)
    return needed, growth_percent


# Exercise 2: a drag that takes out what the method puts in.
# region: damped
b = k * dt  # drag constant, kg/s
damped = newton(mass, spring(k), linear_drag(b))
gamma = b / (2 * mass)
omega_damped = np.sqrt(omega**2 - gamma**2)
decay = np.exp(-gamma * period)
# endregion: damped


def damped_motion(t):
    """The exact position of the damped oscillator released from 1 m."""
    damping = np.exp(-gamma * t)
    return damping * (
        np.cos(omega_damped * t) + gamma / omega_damped * np.sin(omega_damped * t)
    )


def largest_excursions(x, per_period):
    """The largest |x| in each of five periods, with that many samples per period."""
    return [
        np.max(np.abs(x[i * per_period : (i + 1) * per_period + 1])) for i in range(5)
    ]


def amplitudes(steps):
    """The largest excursion in each of five periods, with that many steps
    per period."""
    run = simulate(released, damped, period / steps, 5 * steps)
    return largest_excursions(run.x[:, 0], steps)


def damped_excursions(experiment: Experiment):
    """Exercise 2: the excursions of the simulated damped oscillator for three
    time steps and of the exact motion; record the table."""
    fine = np.linspace(0.0, 5 * period, 5 * 4096 + 1)
    real = largest_excursions(damped_motion(fine), 4096)

    simulated = [amplitudes(64), amplitudes(128), amplitudes(256)]

    experiment.table(
        "damped-excursions",
        [
            (i + 1, simulated[0][i], simulated[1][i], simulated[2][i], real[i])
            for i in range(5)
        ],
        columns=[
            ("period", "", "d"),
            ("64 steps", "m", ".3f"),
            ("128 steps", "m", ".3f"),
            ("256 steps", "m", ".3f"),
            ("real motion", "m", ".3f"),
        ],
        caption="Largest excursion in each of five periods of the simulated "
        "damped oscillator for three time steps, and of the exact motion.",
    )
    return simulated, real


def in_a_plane(factor):
    """Exercise 3: an orbit in a plane; the exact orbit, the largest deviation
    of an energy ratio from ``factor``, and the largest distance from the
    exact position, in m."""
    in_plane = State(t=0.0, x=[1.0, 0.0], v=[0.0, 1.0])
    run = simulate(in_plane, oscillator, dt, 2 * steps_per_period)
    plane_exact = harmonic_motion(in_plane, mass, k, run.t)
    plane_energies = energy(run, mass, k)
    plane_ratios = plane_energies[1:] / plane_energies[:-1]

    plane_deviation = np.max(np.abs(plane_ratios - factor))
    plane_gap = np.max(np.linalg.norm(run.x - plane_exact.x, axis=1))
    return plane_exact, plane_deviation, plane_gap


def run() -> Experiment:
    """Everything the lesson's page shows."""
    experiment = Experiment()
    experiment.figure("fig-oscillator-energy-ellipse", draw_oscillator_energy_ellipse)

    euler, exact = three_periods(experiment)
    experiment.number("omega", omega, ".1f")
    experiment.number("period", period, ".4f")
    experiment.number("dt", dt, ".4f")
    experiment.number("omega-dt", omega * dt, ".4f")
    experiment.number(
        "last-excursion", np.max(np.abs(euler.x[-steps_per_period:, 0])), ".2f"
    )
    experiment.figure(
        "fig-oscillator-position", partial(draw_oscillator_position, euler)
    )
    experiment.figure(
        "fig-oscillator-phase-space",
        partial(draw_oscillator_phase_space, euler, exact),
    )

    energies, ratios, factor, deviation = energy_ratios(euler)
    experiment.number("ratio-count", n_periods * steps_per_period)
    experiment.number("initial-energy", energies[0], ".4f")
    experiment.number("first-ratios", ", ".join(f"{ratio:.6f}" for ratio in ratios[:6]))
    experiment.number("factor", factor, ".6f")
    experiment.number("deviation", deviation, ".1e")
    experiment.number("n-periods", n_periods)
    experiment.number("final-energy", energies[-1] / energies[0], ".3f")
    experiment.number("predicted-energy", factor ** len(ratios), ".3f")
    experiment.figure(
        "fig-oscillator-energy-growth",
        partial(draw_oscillator_energy_growth, energies[0]),
    )

    step_counts, growths = energy_growth(experiment)
    experiment.number("finest-steps", step_counts[-1])
    experiment.number("finest-growth", 100 * (growths[-1] - 1), ".1f")

    needed, growth_percent = one_per_cent()
    experiment.number("needed", needed)
    experiment.number("growth-percent", growth_percent, ".3f")
    experiment.number("needed-in-all", 10 * needed)

    simulated, real = damped_excursions(experiment)
    experiment.number("b", b, ".4f")
    experiment.number("decay", decay, ".3f")
    experiment.number(
        "largest-departure", 100 * max(abs(a - 1) for a in simulated[0]), ".1f"
    )
    experiment.number("last-real", real[-1], ".2f")

    plane_exact, plane_deviation, plane_gap = in_a_plane(factor)
    experiment.number("semi-axis-x", np.max(plane_exact.x[:, 0]), ".3f")
    experiment.number("semi-axis-y", np.max(plane_exact.x[:, 1]), ".3f")
    experiment.number("plane-deviation", plane_deviation, ".1e")
    experiment.number("plane-gap", plane_gap, ".3f")
    return experiment


if __name__ == "__main__":
    main(run)
