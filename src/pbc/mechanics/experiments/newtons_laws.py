"""The experiment of the lesson "Newton's laws".

A particle falling with linear drag and a throw with linear drag, simulated
with explicit Euler (``pbc.mechanics.dynamics``) and compared with the exact
solution (``pbc.mechanics.drag``). Run it as a program to write the figures
and numbers of the page:

    uv run --locked --no-dev python -m pbc.mechanics.experiments.newtons_laws out
"""

from functools import partial

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from scipy.constants import g  # standard gravity, m/s^2

from pbc.authoring.diagrams import INK, arrow, canvas, circle, text
from pbc.experiment import Experiment, main
from pbc.mechanics.drag import fall_with_linear_drag, linear_drag
from pbc.mechanics.dynamics import State, Trajectory, newton, simulate, weight

# region: setup
mass = 0.5  # kg
b = 0.25  # drag constant, kg/s
tau = mass / b  # time constant, s
terminal_speed = g * tau  # m/s
down = [g]  # the gravitational acceleration, on a line with down positive

rest = State(t=0.0, x=0.0, v=0.0)
falling = newton(mass, weight(mass, down), linear_drag(b))
dt = 0.1  # time step, s
n_steps = 100
# endregion: setup

duration = dt * n_steps
step_counts = [n_steps * 2**k for k in range(6)]


def draw_forces_on_a_falling_particle() -> Figure:
    """The forces on a falling particle at three moments, as a sketch."""
    weight_colour, drag_colour, velocity_colour = 0, 1, 2
    fig, ax = canvas(6.4, 3.8, (0, 10), (-0.1, 5.6))
    moments = (
        (1.8, "just released", 0.0),
        (5.0, "speeding up", 0.5),
        (8.2, "terminal speed", 1.0),
    )
    for x, moment, share in moments:
        circle(ax, (x, 3.2), 0.12, colour=INK, filled=True)
        text(ax, (x, 5.2), moment)
        arrow(ax, (x, 3.0), (x, 1.4), colour=weight_colour)
        if share:
            arrow(
                ax, (x, 3.4), (x, 3.4 + 1.6 * share), colour=drag_colour, linestyle="--"
            )
            arrow(
                ax,
                (x + 0.6, 3.2),
                (x + 0.6, 3.2 - 1.6 * share),
                colour=velocity_colour,
                linestyle=":",
            )
    text(ax, (1.8, 1.05), "weight", colour=weight_colour)
    text(ax, (4.7, 4.75), "drag", colour=drag_colour, ha="right")
    text(ax, (5.8, 2.9), "velocity", colour=velocity_colour, ha="left")
    text(
        ax,
        (5.0, 0.3),
        "weight (solid) is the same every time; drag (dashed) grows with the"
        " velocity (dotted)",
    )
    return fig


def falling_particle(experiment: Experiment) -> tuple[Trajectory, Trajectory]:
    """Simulate the particle released from rest and evaluate the exact
    solution at the same instants; record the table of every tenth step."""
    euler = simulate(rest, falling, dt, n_steps)
    exact = fall_with_linear_drag(rest, mass, b, down, euler.t)

    experiment.table(
        "falling-particle",
        [
            (euler.t[i], euler.v[i, 0], exact.v[i, 0], euler.x[i, 0], exact.x[i, 0])
            for i in range(0, n_steps + 1, 10)
        ],
        columns=[
            ("t", "s", ".1f"),
            ("v Euler", "m/s", ".3f"),
            ("v exact", "m/s", ".3f"),
            ("x Euler", "m", ".3f"),
            ("x exact", "m", ".3f"),
        ],
        caption="Velocity and distance fallen, simulated and exact, every tenth "
        "step; to three decimals.",
    )
    return euler, exact


def formula_gap(euler: Trajectory) -> float:
    """The largest difference between the simulated velocity and the
    formula for explicit Euler's v_n, in m/s."""
    n = np.arange(n_steps + 1)
    predicted = terminal_speed * (1 - (1 - dt / tau) ** n)
    return np.max(np.abs(euler.v[:, 0] - predicted))


def draw_fall_with_linear_drag(euler: Trajectory) -> Figure:
    """The velocity of the falling particle, explicit Euler against exact."""
    fine = np.linspace(0.0, euler.t[-1], 201)

    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.axhline(terminal_speed, color="#555555", linestyle=":", label="terminal speed")
    ax.plot(
        fine,
        fall_with_linear_drag(rest, mass, b, down, fine).v[:, 0],
        color="#00429d",
        label="exact",
    )
    ax.plot(
        euler.t,
        euler.v[:, 0],
        color="#93003a",
        linestyle="--",
        marker="o",
        markersize=3,
        label=f"explicit Euler, time step {dt} s",
    )
    ax.set_xlabel("time (s)")
    ax.set_ylabel("velocity (m/s)")
    ax.legend()
    return fig


def final_errors(n):
    """Errors of the last simulated velocity and position, for n steps."""
    end = simulate(rest, falling, duration / n, n)
    reference = fall_with_linear_drag(rest, mass, b, down, end.t[-1])
    return end.v[-1, 0] - reference.v[0, 0], end.x[-1, 0] - reference.x[0, 0]


def convergence(experiment: Experiment) -> np.ndarray:
    """The errors of the final velocity and position for each time step and
    the observed order of the position error; record their table."""
    errors = np.array([final_errors(n) for n in step_counts])
    orders = np.log2(errors[:-1, 1] / errors[1:, 1])

    experiment.table(
        "convergence",
        [
            (
                n,
                duration / n,
                errors[i, 0],
                errors[i, 1],
                orders[i - 1] if i else None,
            )
            for i, n in enumerate(step_counts)
        ],
        columns=[
            ("steps", "", "d"),
            ("time step", "s", ".6f"),
            ("v error", "m/s", ".6f"),
            ("x error", "m", ".6f"),
            ("observed order", "", ".3f"),
        ],
        caption="Error of the final velocity and position of the falling "
        "particle for each time step, and the observed order of the position "
        "error.",
    )
    return orders


def on_the_ground(state):
    return state.x[1] < 0.0


def throw():
    """A throw in the vertical plane with linear drag: the simulated flight,
    the exact one, the flight without drag, and the largest distance between
    the simulated and the exact position."""
    start = State(t=0.0, x=[0.0, 0.0], v=[12.0, 15.0])
    plane = [0.0, -g]
    thrown = newton(mass, weight(mass, plane), linear_drag(b))

    flight = simulate(start, thrown, 0.01, 10_000, until=on_the_ground)
    exact_flight = fall_with_linear_drag(start, mass, b, plane, flight.t)
    # The drag-free motion over its own, longer flight: back at the ground when
    # the vertical velocity has reversed, at t = 2 v_y / g.
    free_time = np.linspace(0.0, 2 * start.v[1] / g, 200)[:, None]
    without_drag = start.x + start.v * free_time + 0.5 * np.array(plane) * free_time**2

    largest_gap = np.max(np.linalg.norm(flight.x - exact_flight.x, axis=1))
    return flight, exact_flight, without_drag, largest_gap


def draw_throw_with_linear_drag(flight, exact_flight, without_drag) -> Figure:
    """The path of the throw with and without linear drag."""
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.plot(
        without_drag[:, 0],
        without_drag[:, 1],
        color="#555555",
        linestyle=":",
        label="without drag",
    )
    ax.plot(
        exact_flight.x[:, 0],
        exact_flight.x[:, 1],
        color="#00429d",
        label="linear drag, exact",
    )
    ax.plot(
        flight.x[::10, 0],
        flight.x[::10, 1],
        color="#93003a",
        linestyle="none",
        marker="o",
        markersize=3,
        label="linear drag, explicit Euler",
    )
    ax.set_ylim(bottom=0.0)
    ax.set_xlabel("horizontal distance (m)")
    ax.set_ylabel("height (m)")
    ax.legend()
    return fig


def large_steps(experiment: Experiment) -> None:
    """Exercise 1: ten steps of 3 s and of 5 s; record their velocities."""
    runs = {step: simulate(rest, falling, step, 10) for step in (3.0, 5.0)}
    experiment.table(
        "large-step-velocity",
        [(i, runs[3.0].v[i, 0], runs[5.0].v[i, 0]) for i in range(11)],
        columns=[
            ("step", "", "d"),
            ("v, time step 3 s", "m/s", ".1f"),
            ("v, time step 5 s", "m/s", ".1f"),
        ],
        caption="Computed velocity of the falling particle for two large time steps.",
    )


def time_to_terminal_speed():
    """Exercise 2: the time to 99 per cent of the terminal speed, exact and
    from a simulation with a step of 1 ms, in s."""
    predicted = tau * np.log(100)
    fine_fall = simulate(rest, falling, 0.001, 12_000)
    reached = fine_fall.t[np.argmax(fine_fall.v[:, 0] >= 0.99 * terminal_speed)]
    return predicted, reached


# Exercise 3: a spring instead of the drag.
# region: spring
k = 2.0  # spring constant, N/m
omega = np.sqrt(k / mass)
period = 2 * np.pi / omega
# endregion: spring


def spring(t, x, v):
    return -k * x


def one_period():
    """Exercise 3: one period of the spring with a time step of 10 ms."""
    released = State(t=0.0, x=1.0, v=0.0)
    return simulate(released, newton(mass, spring), 0.01, round(period / 0.01))


def run() -> Experiment:
    """Everything the lesson's page shows."""
    experiment = Experiment()
    experiment.number("exp-3", np.exp(-3), ".3f")
    experiment.number("exp-5", np.exp(-5), ".4f")
    experiment.figure(
        "fig-forces-on-a-falling-particle", draw_forces_on_a_falling_particle
    )

    euler, _ = falling_particle(experiment)
    experiment.number("tau", tau, ".1f")
    experiment.number("terminal-speed", terminal_speed, ".3f")
    experiment.number("per-cent-left", 100 * np.exp(-5), ".1f")
    experiment.number("euler-factor", 1 - dt / tau, ".2f")
    experiment.number("exact-factor", np.exp(-dt / tau), ".4f")
    experiment.number("formula-gap", formula_gap(euler), ".1e")
    experiment.figure(
        "fig-fall-with-linear-drag", partial(draw_fall_with_linear_drag, euler)
    )

    orders = convergence(experiment)
    experiment.number("last-order", orders[-1], ".3f")

    flight, exact_flight, without_drag, largest_gap = throw()
    experiment.number("flight-time", flight.t[-1], ".2f")
    experiment.number("flight-range", flight.x[-1, 0], ".2f")
    experiment.number("largest-gap", largest_gap, ".3f")
    experiment.figure(
        "fig-throw-with-linear-drag",
        partial(draw_throw_with_linear_drag, flight, exact_flight, without_drag),
    )

    experiment.number("tau-whole", tau, ".0f")
    large_steps(experiment)

    predicted, reached = time_to_terminal_speed()
    experiment.number("predicted", predicted, ".3f")
    experiment.number("reached", reached, ".3f")

    oscillation = one_period()
    end = oscillation.t[-1]
    experiment.number("period", period, ".3f")
    experiment.number("end", end, ".2f")
    experiment.number("end-position", oscillation.x[-1, 0], ".4f")
    experiment.number("exact-end-position", np.cos(omega * end), ".4f")
    experiment.number("largest-excursion", np.max(np.abs(oscillation.x[:, 0])), ".4f")
    return experiment


if __name__ == "__main__":
    main(run)
