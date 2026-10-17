"""The experiment of the lesson template, ``docs/lesson-template.qmd``.

A new lesson copies this module to ``pbc.<course>.experiments.<name>``, where
``<name>`` is its ``id`` with hyphens as underscores, and replaces the example:
a cart that brakes, simulated with explicit Euler and compared with the exact
motion. Run it as a program to write the figure and numbers of the template:

    uv run --locked --no-dev \\
        python -m pbc.mechanics.experiments.lesson_template out
"""

from functools import partial

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from pbc.experiment import Experiment, main
from pbc.mechanics.kinematics import State, Trajectory, constant_acceleration, simulate

# region: setup
start = State(t=0.0, x=0.0, v=2.0)
dt = 0.25  # time step, s
# endregion: setup


def braking(t):
    return -1.0


def braking_cart() -> tuple[Trajectory, Trajectory]:
    """Simulate the cart and evaluate the exact motion at the same instants."""
    computed = simulate(start, braking, dt, n_steps=8)
    exact = constant_acceleration(start, -1.0, computed.t)
    print(f"position after {computed.t[-1]:.1f} s: {computed.x[-1]:.3f} m")
    return computed, exact


def draw_replace_with_a_name(computed: Trajectory, exact: Trajectory) -> Figure:
    """One function per figure: it draws the figure and returns it."""
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.plot(computed.t, exact.x, color="#00429d", label="exact")
    ax.plot(
        computed.t,
        computed.x,
        color="#93003a",
        linestyle="--",
        marker="o",
        label="computed",
    )
    ax.set_xlabel("time (s)")
    ax.set_ylabel("position (m)")
    ax.legend()
    return fig


def largest_error(computed: Trajectory, exact: Trajectory) -> None:
    """The solution of the exercise: the largest error of the position."""
    print(f"largest error: {np.max(np.abs(computed.x - exact.x)):.3f} m")


def run() -> Experiment:
    """Everything the lesson's page shows."""
    experiment = Experiment()
    with experiment.capture("braking-cart"):
        computed, exact = braking_cart()
    experiment.number("exact-position", exact.x[-1], ".3f")
    experiment.figure(
        "fig-replace-with-a-name", partial(draw_replace_with_a_name, computed, exact)
    )
    with experiment.capture("largest-error"):
        largest_error(computed, exact)
    return experiment


if __name__ == "__main__":
    main(run)
