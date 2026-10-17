"""The experiment of the lesson "What symplectic Euler conserves".

The numbers behind the Lean theorem that symplectic Euler keeps a modified
energy of the oscillator exactly (``pbc.mechanics.integrators``): the energy
of the spring and the modified energy over a run, explicit Euler against
it, and the step at which the modified energy stops being positive. The
theorem itself is checked by the Lean build, ``./scripts/check-lean.sh``.
Run it as a program to write the figure and numbers of the page:

    uv run --locked --no-dev \\
        python -m pbc.mechanics.experiments.symplectic_euler_conserved_energy out
"""

from functools import partial

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from pbc.experiment import Experiment, main
from pbc.mechanics.dynamics import State, euler_step, newton, simulate
from pbc.mechanics.integrators import symplectic_euler_step
from pbc.mechanics.oscillator import angular_frequency, energy, spring

# region: setup
mass = 0.5  # kg
k = 2.0  # N/m
period = 2 * np.pi / angular_frequency(mass, k)
steps_per_period = 16
dt = period / steps_per_period
n_steps = 3 * steps_per_period
# endregion: setup


def modified_energy(trajectory):
    """The energy of the spring minus k dt x v / 2, at every instant (J)."""
    cross = np.sum(trajectory.x * trajectory.v, axis=1)
    return energy(trajectory, mass, k) - 0.5 * k * dt * cross


def three_periods(experiment: Experiment):
    """Three periods with symplectic Euler: the energy of the spring and the
    modified energy; record the table."""
    symplectic = simulate(
        State(t=0.0, x=1.0, v=0.0),
        newton(mass, spring(k)),
        dt,
        n_steps,
        step=symplectic_euler_step,
    )
    spring_energy = energy(symplectic, mass, k)
    modified = modified_energy(symplectic)
    drift = np.max(np.abs(modified / modified[0] - 1))
    swing = spring_energy.max() / spring_energy.min() - 1

    experiment.table(
        "three-periods",
        [
            ("energy of the spring", spring_energy.min(), spring_energy.max()),
            ("modified energy", modified.min(), modified.max()),
        ],
        [("quantity", "", ""), ("smallest", "J", ".4f"), ("largest", "J", ".4f")],
        "The energy of the spring and the modified energy over the run, symplectic "
        "Euler.",
    )
    return symplectic, spring_energy, modified, drift, swing


def draw_modified_energy(symplectic, spring_energy, modified) -> Figure:
    """The energy of the spring and the modified energy against time."""
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.plot(symplectic.t, spring_energy, color="#93003a", label="energy of the spring")
    ax.plot(
        symplectic.t, modified, color="#00429d", linestyle="--", label="modified energy"
    )
    ax.set_xlabel("time (s)")
    ax.set_ylabel("energy (J)")
    ax.legend()
    return fig


def explicit_euler():
    """Exercise 1: the modified energy along explicit Euler."""
    explicit = simulate(
        State(t=0.0, x=1.0, v=0.0),
        newton(mass, spring(k)),
        dt,
        n_steps,
        step=euler_step,
    )
    explicit_modified = modified_energy(explicit)
    growth = explicit_modified[-1] / explicit_modified[0]
    print(
        "modified energy after three periods of explicit Euler, relative to the"
        f" start: {growth:.2f}"
    )


def positive_or_not(experiment: Experiment) -> None:
    """Exercise 2: the smallest modified energy on the unit circle for four
    steps; record the table."""
    angles = np.linspace(0, 2 * np.pi, 3601)
    rows = []
    for per_period in (64, 16, 4, 3):
        step = period / per_period
        x, v = np.cos(angles), np.sin(angles)
        value = 0.5 * mass * v**2 + 0.5 * k * x**2 - 0.5 * k * step * x * v
        rows.append((per_period, k * step**2 / (4 * mass), value.min()))

    experiment.table(
        "positive-or-not",
        rows,
        [
            ("steps per period", "", "d"),
            ("k dt^2 / 4m", "", ".3f"),
            ("smallest modified energy on the circle", "J", ".4f"),
        ],
        "The smallest value of the modified energy on the unit circle in position "
        "and velocity, for four step sizes.",
    )


def quantity(x, v, c):
    return 0.5 * mass * v**2 + 0.5 * k * x**2 + c * x * v


def the_value_of_c():
    """Exercise 3: the value of c, checked on a random state."""
    rng = np.random.default_rng(3)
    x0, v0 = rng.normal(size=2)
    v1 = v0 - k / mass * x0 * dt
    x1 = x0 + dt * v1
    c = -0.5 * k * dt
    print(
        "change of the quantity over a step with c = -k dt / 2: "
        f"{quantity(x1, v1, c) - quantity(x0, v0, c):.1e}"
    )


def fewest_steps():
    """Exercise 4: the bound on the steps per period."""
    print(f"pi = {np.pi:.4f}: the number of steps per period must exceed it")


def run() -> Experiment:
    """Everything the lesson's page shows."""
    experiment = Experiment()
    symplectic, spring_energy, modified, drift, swing = three_periods(experiment)
    experiment.number("drift", drift, ".0e")
    experiment.number("swing", swing, ".2f")
    experiment.figure(
        "fig-modified-energy",
        partial(draw_modified_energy, symplectic, spring_energy, modified),
    )
    with experiment.capture("explicit-euler"):
        explicit_euler()
    positive_or_not(experiment)
    with experiment.capture("the-value-of-c"):
        the_value_of_c()
    with experiment.capture("fewest-steps"):
        fewest_steps()
    return experiment


if __name__ == "__main__":
    main(run)
