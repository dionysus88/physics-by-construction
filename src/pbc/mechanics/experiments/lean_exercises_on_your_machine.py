"""The experiment of the lesson "Lean exercises on your machine".

The numbers behind the three Lean exercises: the two forms of the distance
and of the time under constant acceleration, and the momentum before and
after an impulse. The exercises and their checked solutions are built by
``./scripts/check-lean.sh``. Run it as a program to write the figure and
numbers of the page:

    uv run --locked --no-dev \\
        python -m pbc.mechanics.experiments.lean_exercises_on_your_machine out
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from pbc.experiment import Experiment, main

# region: throw
a, v0, x0, t = -9.81, 20.0, 0.0, 1.5  # m/s^2, m/s, m, s
# endregion: throw


def both_sides():
    """Both sides of the three statements, for a throw and for an impulse."""
    x = x0 + v0 * t + a * t**2 / 2
    v = v0 + a * t
    print(f"x - x0                 = {x - x0:.4f} m")
    print(f"(v^2 - v0^2) / (2 a)   = {(v**2 - v0**2) / (2 * a):.4f} m")
    print(f"t                      = {t:.4f} s")
    print(f"(v - v0) / a           = {(v - v0) / a:.4f} s")

    m1, m2, u1, u2, J = 0.5, 1.5, 2.0, -1.0, 0.8  # kg, kg, m/s, m/s, N s
    w1, w2 = u1 - J / m1, u2 + J / m2
    print(f"momentum before        = {m1 * u1 + m2 * u2:.4f} kg m/s")
    print(f"momentum after         = {m1 * w1 + m2 * w2:.4f} kg m/s")


def draw_two_sides() -> Figure:
    """The two sides of the first statement over three seconds."""
    times = np.linspace(0.0, 3.0, 61)
    distance = v0 * times + a * times**2 / 2
    speed = v0 + a * times
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    ax.plot(times, distance, color="#00429d", linewidth=3, label="x - x0")
    ax.plot(
        times,
        (speed**2 - v0**2) / (2 * a),
        color="white",
        linestyle="--",
        linewidth=1.2,
        label="(v^2 - v0^2) / (2 a)",
    )
    ax.set_xlabel("time (s)")
    ax.set_ylabel("distance (m)")
    ax.legend(loc="lower center")
    return fig


def run() -> Experiment:
    """Everything the lesson's page shows."""
    experiment = Experiment()
    with experiment.capture("both-sides"):
        both_sides()
    experiment.figure("fig-two-sides", draw_two_sides)
    return experiment


if __name__ == "__main__":
    main(run)
