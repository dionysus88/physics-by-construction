"""The experiment of the lesson "Energy conservation".

The pendulum at large amplitudes (``pbc.mechanics.pendulum``): its period
against the elliptic integral and the series, the energy of the four
integrators over twenty swings, the order of the drift, the energy gained in
one explicit Euler step, the lag of the symplectic methods, and a release
near the top. Run it as a program to write the figures and numbers of the
page:

    uv run --locked --no-dev \\
        python -m pbc.mechanics.experiments.energy_conservation out
"""

from functools import partial

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from scipy.constants import g
from scipy.optimize import brentq

from pbc.authoring import FIGURE_COLOURS, diagrams
from pbc.experiment import Experiment, main
from pbc.mechanics.drag import linear_drag
from pbc.mechanics.dynamics import State, newton, simulate
from pbc.mechanics.energy import energy_drift, mechanical_energy
from pbc.mechanics.integrators import INTEGRATORS
from pbc.mechanics.pendulum import (
    pendulum_force,
    pendulum_period,
    pendulum_potential,
    small_angle_period,
)

# region: setup
mass = 1.0  # kg
length = 1.0  # m
pendulum = newton(mass, pendulum_force(mass, length))
potential = pendulum_potential(mass, length)
t0 = small_angle_period(length)
euler, symplectic_euler, verlet, rk4 = INTEGRATORS
# endregion: setup

# region: example
amplitude = 120  # degrees
swing = pendulum_period(length, np.radians(amplitude))
# endregion: example
# region: step-counts
step_counts = [50, 100, 200, 400]
# endregion: step-counts


def draw_energy_bands() -> Figure:
    """Drift, band, and slow loss of the energy, as a sketch."""
    t = np.linspace(0.0, 10.0, 400)
    fig, ax = diagrams.canvas(6.4, 3.2, (-1.4, 15.6), (-2.6, 2.8))
    ax.set_aspect("auto")
    ax.fill_between([0, 10], [-0.5, -0.5], [0.5, 0.5], color="#eaecf0", zorder=0)
    diagrams.arrow(ax, (0, -2.2), (0, 2.6), colour="#1f2328", width=1.0)
    diagrams.arrow(ax, (0, -2.2), (10.8, -2.2), colour="#1f2328", width=1.0)
    diagrams.line(ax, [(0, 0), (10, 0)], colour="#57606a", linestyle=":", width=1.0)
    diagrams.text(ax, (10.9, -2.2), "time", ha="left")
    diagrams.text(ax, (-0.2, 2.65), "energy minus its start", ha="left", va="bottom")
    ax.plot(t, 0.22 * t, color=FIGURE_COLOURS[0], linestyle="-", linewidth=1.6)
    ax.plot(
        t,
        0.36 * np.sin(2.3 * t),
        color=FIGURE_COLOURS[1],
        linestyle="--",
        linewidth=1.6,
    )
    ax.plot(t, -0.09 * t, color=FIGURE_COLOURS[2], linestyle="-.", linewidth=1.6)
    diagrams.text(
        ax, (10.3, 2.2), "drift: grows with\nthe length of the run", ha="left", colour=0
    )
    diagrams.text(
        ax, (10.3, 0.4), "band: oscillates,\ndoes not grow", ha="left", colour=1
    )
    diagrams.text(ax, (10.3, -1.0), "slow loss", ha="left", colour=2)
    diagrams.text(
        ax,
        (0.2, -1.5),
        "grey band: where the energy of a bounded method stays",
        ha="left",
        colour="#57606a",
    )
    return fig


def released(degrees):
    """At rest at the given angle from the vertical."""
    return State(t=0.0, x=[length * np.radians(degrees)], v=[0.0])


def run_swings(integrator, degrees, steps_per_period, n_swings):
    """n_swings of the pendulum released at the angle, with the small-angle
    period divided into steps_per_period steps."""
    swing = pendulum_period(length, np.radians(degrees))
    n_steps = round(n_swings * swing / t0 * steps_per_period)
    return simulate(
        released(degrees),
        pendulum,
        t0 / steps_per_period,
        n_steps,
        step=integrator.step,
    )


def forward_crossings(trajectory):
    """The times at which the bob passes the bottom moving forward."""
    s, t = trajectory.x[:, 0], trajectory.t
    before = np.where((s[:-1] < 0) & (s[1:] >= 0))[0]
    fraction = -s[before] / (s[before + 1] - s[before])
    return t[before] + fraction * (t[before + 1] - t[before])


def period_table(experiment: Experiment) -> list:
    """The period for five amplitudes from the elliptic integral, from a
    simulation, and from the series; record the table and return its rows."""
    rows = []
    for degrees in (10, 45, 90, 135, 170):
        angle = np.radians(degrees)
        exact = pendulum_period(length, angle)
        measured = np.mean(np.diff(forward_crossings(run_swings(rk4, degrees, 200, 3))))
        rows.append(
            (
                degrees,
                exact,
                exact / t0,
                measured,
                t0 * (1 + angle**2 / 16),
                t0 * (1 + angle**2 / 16 + 11 * angle**4 / 3072),
            )
        )

    experiment.table(
        "period-table",
        rows,
        columns=[
            ("amplitude", "degrees", "d"),
            ("exact period", "s", ".4f"),
            ("T / T0", "", ".4f"),
            ("simulated period", "s", ".4f"),
            ("one-term series", "s", ".4f"),
            ("two-term series", "s", ".4f"),
        ],
        caption="Period of the pendulum from the elliptic integral, from a "
        "simulation, and from the series, to four decimals.",
    )
    return rows


def draw_pendulum_swings() -> Figure:
    """Three swings at three amplitudes, the angle over the amplitude."""
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    for degrees, style in ((10, "-"), (120, "--"), (170, ":")):
        trajectory = run_swings(rk4, degrees, 200, 3)
        ax.plot(
            trajectory.t / t0,
            np.degrees(trajectory.x[:, 0] / length) / degrees,
            color="#00429d",
            linestyle=style,
            label=f"released at {degrees}°",
        )
    ax.set_xlabel("time (small-angle periods)")
    ax.set_ylabel("angle / amplitude")
    ax.legend(loc="upper right")
    return fig


def twenty_swings(experiment: Experiment) -> dict:
    """Twenty swings at the amplitude of the example with each method;
    record the table of the energy drift and return the runs."""
    runs = {
        integrator.name: run_swings(integrator, amplitude, 100, 20)
        for integrator in INTEGRATORS
    }

    rows = []
    for integrator in INTEGRATORS:
        energies = mechanical_energy(runs[integrator.name], mass, potential)
        rows.append(
            (integrator.name, energy_drift(energies), energies[-1] / energies[0])
        )

    experiment.table(
        "twenty-swings",
        rows,
        columns=[
            ("method", "", ""),
            ("energy drift", "", ".1e"),
            ("energy at the end / initial", "", ".4f"),
        ],
        caption="Drift of the energy over twenty swings at the amplitude of the "
        "example, and the energy at the end relative to the start.",
    )
    return runs


def draw_pendulum_energy(runs: dict) -> Figure:
    """The energy over twenty swings for each method."""
    fig, axes = plt.subplots(2, 2, figsize=(6.4, 5.6), sharex=True)
    for ax, integrator in zip(axes.flat, INTEGRATORS, strict=True):
        trajectory = runs[integrator.name]
        energies = mechanical_energy(trajectory, mass, potential)
        ax.plot(
            trajectory.t / swing, energies / energies[0], color="#93003a", linewidth=0.8
        )
        if integrator.name == "explicit Euler":
            ax.set_yscale("log")
        ax.set_title(integrator.name, fontsize=10)
    for ax in axes[1]:
        ax.set_xlabel("time (swings)")
    for ax in axes[:, 0]:
        ax.set_ylabel("energy / initial energy")
    fig.tight_layout()
    return fig


def drift_orders(experiment: Experiment) -> dict:
    """The energy drift over twenty swings for each method and step count,
    with the observed order; record the table and return the drifts."""
    drifts = {
        integrator.name: np.array(
            [
                energy_drift(
                    mechanical_energy(
                        run_swings(integrator, amplitude, n, 20), mass, potential
                    )
                )
                for n in step_counts
            ]
        )
        for integrator in INTEGRATORS
    }

    rows = []
    columns = [("steps per T0", "", "d")]
    for integrator in INTEGRATORS:
        columns += [(f"{integrator.name}: drift", "", ".1e"), ("order", "", ".2f")]
    for i, n in enumerate(step_counts):
        row = [n]
        for integrator in INTEGRATORS:
            drift = drifts[integrator.name]
            row += [drift[i], np.log2(drift[i - 1] / drift[i]) if i else None]
        rows.append(row)

    experiment.table(
        "drift-orders",
        rows,
        columns=columns,
        caption="Energy drift over twenty swings against the number of steps per "
        "small-angle period, with the observed order, to two significant digits.",
    )
    return drifts


def step_energy_gain(experiment: Experiment) -> list:
    """The energy one explicit Euler step gains at three angles and three
    steps, against the formula; record the table and return its rows."""
    dt = t0 / 100
    total = mass * g * length * (1 - np.cos(np.radians(amplitude)))  # J
    rows = []
    for degrees in (amplitude, 60, 0):
        theta = np.radians(degrees)
        speed = np.sqrt(2 * (total - mass * g * length * (1 - np.cos(theta))) / mass)
        state = State(t=0.0, x=[length * theta], v=[speed])
        acceleration = -g * np.sin(theta)
        curvature = mass * g / length * np.cos(theta)  # U'' in J/m^2
        row = [degrees, speed]
        for step in (dt, dt / 2, dt / 4):
            gain = mechanical_energy(
                simulate(state, pendulum, step, 1, step=euler.step), mass, potential
            )
            formula = 0.5 * step**2 * (mass * acceleration**2 + curvature * speed**2)
            row += [gain[1] - gain[0], (gain[1] - gain[0]) / formula - 1]
        rows.append(row)

    experiment.table(
        "step-energy-gain",
        rows,
        columns=[("angle", "degrees", "d"), ("speed", "m/s", ".3f")]
        + [
            (f"gain at {label}", "J", ".3e")
            if k == 0
            else (f"difference at {label}", "", ".1e")
            for label in ("the step", "half", "a quarter")
            for k in (0, 1)
        ],
        caption="Energy gained in one explicit Euler step, and its relative "
        "difference from the formula, at the step, half of it, and a quarter "
        "of it.",
    )
    return rows


def period_lag(experiment: Experiment, runs: dict) -> list:
    """The lag of the bob behind the exact period at its forward passages
    for the methods after explicit Euler; record the table and return its
    rows."""
    rows = []
    for integrator in INTEGRATORS[1:]:
        trajectory = runs[integrator.name]
        crossings = forward_crossings(trajectory)
        lag = crossings - (crossings[0] + np.arange(len(crossings)) * swing)
        drift = energy_drift(mechanical_energy(trajectory, mass, potential))
        rows.append(
            (integrator.name, drift, 1e3 * lag[5], 1e3 * lag[10], 1e3 * lag[19])
        )

    experiment.table(
        "period-lag",
        rows,
        columns=[
            ("method", "", ""),
            ("energy drift", "", ".1e"),
            ("lag after 5 swings", "ms", ".2f"),
            ("lag after 10 swings", "ms", ".2f"),
            ("lag after 19 swings", "ms", ".2f"),
        ],
        caption="Time by which the bob is behind (positive) or ahead of "
        "(negative) the exact period at its forward passages through the "
        "bottom, with the energy drift of the run.",
    )
    return rows


def near_the_top(experiment: Experiment):
    """Three swings of the pendulum released at 170 degrees with explicit
    Euler and velocity Verlet; record the table and return the runs, its
    rows, and the energy of the top, in J."""
    separatrix = 2 * mass * g * length  # the energy at the top, J
    runs = {
        integrator.name: run_swings(integrator, 170, 200, 3)
        for integrator in (euler, verlet)
    }

    rows = []
    for integrator in (euler, verlet):
        trajectory = runs[integrator.name]
        energies = mechanical_energy(trajectory, mass, potential)
        largest_angle = np.degrees(np.max(np.abs(trajectory.x[:, 0])) / length)
        rows.append(
            (
                integrator.name,
                energies[0] / separatrix,
                np.max(energies) / separatrix,
                largest_angle,
            )
        )

    experiment.table(
        "near-the-top",
        rows,
        columns=[
            ("method", "", ""),
            ("initial energy / top", "", ".4f"),
            ("largest energy / top", "", ".4f"),
            ("largest angle", "degrees", ".0f"),
        ],
        caption="The energy, in units of the energy of the top, and the largest "
        "angle that each method reaches in three swings of the pendulum "
        "released near the top.",
    )
    return runs, rows, separatrix


def over_the_top(runs: dict, separatrix: float):
    """When explicit Euler's energy passes the top and when its angle does,
    in s."""
    euler_energies = mechanical_energy(runs["explicit Euler"], mass, potential)
    trajectory = runs["explicit Euler"]
    crossed = trajectory.t[np.argmax(euler_energies > separatrix)]
    past_top = trajectory.t[np.argmax(np.abs(trajectory.x[:, 0]) / length > np.pi)]
    return crossed, past_top


def draw_pendulum_over_the_top(runs: dict) -> Figure:
    """The angle against time near the top, explicit Euler and Verlet."""
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    for integrator, style in ((verlet, "-"), (euler, "--")):
        trajectory = runs[integrator.name]
        ax.plot(
            trajectory.t,
            np.degrees(trajectory.x[:, 0] / length),
            color="#00429d" if integrator is verlet else "#93003a",
            linestyle=style,
            label=integrator.name,
        )
    ax.axhline(180, color="#555555", linewidth=0.8, linestyle=":")
    ax.axhline(-180, color="#555555", linewidth=0.8, linestyle=":")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("angle (degrees)")
    ax.legend(loc="upper left")
    return fig


def one_per_cent_longer(experiment: Experiment):
    """Exercise 1: the amplitude at which the period is one per cent above
    the small-angle period, from the series, exactly, and simulated; record
    the table."""
    from_series = np.degrees(np.sqrt(0.16))
    two_terms = np.degrees(
        brentq(lambda a: a**2 / 16 + 11 * a**4 / 3072 - 0.01, 0.01, 1.0)
    )
    exact_amplitude = brentq(
        lambda angle: pendulum_period(length, angle) / t0 - 1.01, 0.01, 1.0
    )
    measured = np.mean(
        np.diff(forward_crossings(run_swings(rk4, np.degrees(exact_amplitude), 200, 3)))
    )

    experiment.table(
        "one-per-cent-longer",
        [
            ("one-term series", from_series, None),
            ("two-term series", two_terms, None),
            ("exact period", np.degrees(exact_amplitude), None),
            (
                "simulation at the exact amplitude",
                np.degrees(exact_amplitude),
                measured / t0,
            ),
        ],
        columns=[
            ("source", "", ""),
            ("amplitude", "degrees", ".2f"),
            ("period / T0", "", ".4f"),
        ],
        caption="Amplitude at which the period exceeds the small-angle period by "
        "one per cent, to two decimals, and the simulated period there.",
    )
    return from_series, two_terms, exact_amplitude


def damped_budget(experiment: Experiment, drifts: dict) -> None:
    """Exercise 2: the energy lost to a linear drag against the work the
    drag does over five swings; record the table."""
    b = 0.1  # kg/s
    damped = newton(mass, pendulum_force(mass, length), linear_drag(b))

    rows = []
    for n in step_counts[1:]:
        trajectory = simulate(
            released(amplitude),
            damped,
            t0 / n,
            round(5 * swing / t0 * n),
            step=verlet.step,
        )
        energies = mechanical_energy(trajectory, mass, potential)
        power = -b * np.sum(trajectory.v**2, axis=1)
        work = np.trapezoid(power, trajectory.t)
        rows.append(
            (
                n,
                energies[0] - energies[-1],
                -work,
                energies[0] - energies[-1] + work,
                drifts["velocity Verlet"][step_counts.index(n)],
            )
        )

    experiment.table(
        "damped-budget",
        rows,
        columns=[
            ("steps per T0", "", "d"),
            ("energy lost", "J", ".4f"),
            ("work by drag", "J", ".4f"),
            ("gap", "J", ".1e"),
            ("undamped drift", "", ".1e"),
        ],
        caption="Energy lost, work done by the drag, and the gap between them "
        "over five swings, with the drift of the undamped run at the same step.",
    )


def steps_for_a_drift(experiment: Experiment, drifts: dict) -> None:
    """Exercise 3: the steps per small-angle period that velocity Verlet
    needs for a drift of 1e-5 over fifty swings; record the table."""
    target = 1e-5
    needed = int(np.ceil(100 * np.sqrt(drifts["velocity Verlet"][1] / target)))
    trajectory = run_swings(verlet, amplitude, needed, 50)
    drift = energy_drift(mechanical_energy(trajectory, mass, potential))

    experiment.table(
        "steps-for-a-drift",
        [(needed, drift, len(trajectory.t) - 1)],
        columns=[
            ("steps per T0", "", "d"),
            ("drift over fifty swings", "", ".2e"),
            ("steps in the run", "", "d"),
        ],
        caption="The predicted number of steps per small-angle period, and the "
        "drift of the run that uses it.",
    )


def run() -> Experiment:
    """Everything the lesson's page shows."""
    experiment = Experiment()
    experiment.figure("fig-energy-bands", draw_energy_bands)

    rows = period_table(experiment)
    experiment.number("t0", t0, ".4f")
    experiment.number("right-angle", pendulum_period(length, np.pi / 2) / t0, ".2f")
    experiment.number("largest-ratio", rows[-1][2], ".1f")
    experiment.number("one-term-gap", abs(rows[0][4] - rows[0][1]), ".1e")
    experiment.number("two-term-gap", abs(rows[0][5] - rows[0][1]), ".1e")
    experiment.figure("fig-pendulum-swings", draw_pendulum_swings)

    runs = twenty_swings(experiment)
    experiment.number("swing", swing, ".4f")
    experiment.number("swing-in-t0", swing / t0, ".4f")
    experiment.number("n-steps", len(runs["velocity Verlet"].t) - 1)
    experiment.number("step", t0 / 100, ".5f")
    experiment.figure("fig-pendulum-energy", partial(draw_pendulum_energy, runs))
    # region: euler-ratio
    euler_ratio = mechanical_energy(runs["explicit Euler"], mass, potential)
    euler_ratio = euler_ratio[-1] / euler_ratio[0]
    # endregion: euler-ratio
    experiment.number("euler-ratio", euler_ratio, ".1f")

    drifts = drift_orders(experiment)
    rk4_ratio = drifts["Runge-Kutta 4"][1] / drifts["Runge-Kutta 4"][2]
    experiment.number("rk4-ratio", rk4_ratio, ".0f")
    experiment.number("rk4-order", np.log2(rk4_ratio), ".1f")

    rows = step_energy_gain(experiment)
    experiment.number(
        "largest-difference",
        max(abs(r[k]) for r in rows for k in (3, 5, 7)),
        ".0e",
    )
    experiment.number("right-angle-difference", rows[1][3], ".1e")
    experiment.number("right-angle-difference-quarter", rows[1][7], ".1e")
    experiment.number("verlet-drift", drifts["velocity Verlet"][1], ".0e")

    lag_rows = period_lag(experiment, runs)
    # region: bottom-speed
    bottom_speed = np.sqrt(2 * g * length * (1 - np.cos(np.radians(amplitude))))
    # endregion: bottom-speed
    experiment.number(
        "symplectic-over-verlet",
        drifts["symplectic Euler"][1] / drifts["velocity Verlet"][1],
        ".0f",
    )
    experiment.number("symplectic-lag", lag_rows[0][4], ".1f")
    experiment.number("verlet-lead", -lag_rows[1][4], ".1f")
    experiment.number("bottom-speed", bottom_speed, ".1f")
    experiment.number(
        "lag-distance-cm", 100 * bottom_speed * abs(lag_rows[0][4]) * 1e-3, ".1f"
    )
    experiment.number(
        "release-170", potential(released(170).x) / (2 * mass * g * length), ".4f"
    )

    top_runs, top_rows, separatrix = near_the_top(experiment)
    # region: over-the-top
    crossed, past_top = over_the_top(top_runs, separatrix)
    swing_170 = pendulum_period(length, np.radians(170))
    # endregion: over-the-top
    experiment.number("crossed", crossed, ".2f")
    experiment.number("crossed-in-quarters", crossed / (swing_170 / 4), ".2f")
    experiment.number("past-top", past_top, ".2f")
    experiment.number("euler-largest-angle", top_rows[0][3], ".0f")
    experiment.figure(
        "fig-pendulum-over-the-top", partial(draw_pendulum_over_the_top, top_runs)
    )
    experiment.number("rk4-finest-drift", drifts["Runge-Kutta 4"][-1], ".1e")
    experiment.number(
        "rk4-finest-in-eps",
        drifts["Runge-Kutta 4"][-1] / np.finfo(float).eps,
        ".0e",
    )

    from_series, two_terms, exact_amplitude = one_per_cent_longer(experiment)
    experiment.number("exact-amplitude", np.degrees(exact_amplitude), ".0f")
    experiment.number(
        "one-term-excess", from_series - np.degrees(exact_amplitude), ".3f"
    )
    experiment.number("two-term-excess", two_terms - np.degrees(exact_amplitude), ".3f")
    damped_budget(experiment, drifts)
    steps_for_a_drift(experiment, drifts)
    return experiment


if __name__ == "__main__":
    main(run)
