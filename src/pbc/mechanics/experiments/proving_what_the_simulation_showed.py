"""The experiment of the lesson "Proving what the simulation showed".

The numbers behind two Lean theorems: Torricelli's identity along the exact
motion and its residual on the explicit Euler fall
(``pbc.mechanics.kinematics``), and the growth of the energy of the
oscillator by a fixed factor per explicit Euler step
(``pbc.mechanics.oscillator``). The theorems themselves are checked by the
Lean build, ``./scripts/check-lean.sh``. Run it as a program to write the
figures and numbers of the page:

    uv run --locked --no-dev \\
        python -m pbc.mechanics.experiments.proving_what_the_simulation_showed out
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from pbc.authoring import diagrams
from pbc.experiment import Experiment, main
from pbc.mechanics import kinematics
from pbc.mechanics.dynamics import State, newton, simulate
from pbc.mechanics.oscillator import angular_frequency, energy, spring

# region: throw
FLOOR = 1e-12  # m^2/s^2, far above the round-off of this arithmetic
a = -9.81  # m/s^2
start = kinematics.State(t=0.0, x=0.0, v=20.0)
times = np.linspace(0.0, 4.0, 9)
# endregion: throw
# region: oscillator
mass = 0.5  # kg
k = 2.0  # N/m
period = 2 * np.pi / angular_frequency(mass, k)
released = State(t=0.0, x=1.0, v=0.0)
oscillator = newton(mass, spring(k))

steps_per_period = 64
n_steps = 3 * steps_per_period
dt = period / steps_per_period
# endregion: oscillator


def draw_theorem_pipeline() -> Figure:
    """From a statement to the page, as a sketch."""
    fig, ax = diagrams.canvas(6.4, 2.6, (-0.2, 12.8), (-1.2, 2.4))
    steps = ("statement", "hypotheses", "Lean", "CI record", "page")
    for i, name in enumerate(steps):
        x = 1.1 + 2.6 * i
        diagrams.state_box(
            ax, (x, 1.2), name, width=2.0, height=0.9, colour=0 if i < 2 else 1
        )
        if i:
            diagrams.arrow(ax, (x - 2.6 + 1.05, 1.2), (x - 1.05, 1.2), colour="#57606a")
    diagrams.line(ax, [(0.0, 0.3), (0.0, 0.0), (4.8, 0.0), (4.8, 0.3)], colour=0)
    diagrams.text(ax, (2.4, -0.45), "judged by a person", colour=0)
    diagrams.line(ax, [(5.3, 0.3), (5.3, 0.0), (10.0, 0.0), (10.0, 0.3)], colour=1)
    diagrams.text(ax, (7.65, -0.45), "checked by a machine", colour=1)
    fig.tight_layout()
    return fig


def shown(value):
    """A residual as a number, or as the bound it is below."""
    return f"{value:.1e}" if abs(value) > FLOOR else f"below {FLOOR:.0e}"


def exact_residual(experiment: Experiment):
    """The residual of Torricelli's identity along the exact motion; record
    the table."""
    exact = kinematics.constant_acceleration(start, a, times)

    residual = exact.v**2 - start.v**2 - 2 * a * (exact.x - start.x)
    experiment.table(
        "exact-residual",
        [
            (t, x, v, shown(r))
            for t, x, v, r in zip(times, exact.x, exact.v, residual, strict=True)
        ],
        [
            ("t", "s", ".2f"),
            ("x", "m", ".2f"),
            ("v", "m/s", ".2f"),
            ("v^2 - v0^2 - 2 a (x - x0)", "m^2/s^2", ""),
        ],
        "The residual of Torricelli's identity along the exact motion of a throw "
        "upward at 20 m/s.",
    )
    return residual


def euler_residual(experiment: Experiment):
    """The residual of the identity on the explicit Euler fall against the
    derivation; record the table."""
    fall_dt = 0.25  # s
    fall = kinematics.simulate(start, lambda t: a, fall_dt, 16)
    residual = fall.v**2 - start.v**2 - 2 * a * (fall.x - start.x)
    predicted = a**2 * fall.t * fall_dt

    experiment.table(
        "euler-residual",
        list(zip(fall.t, residual, predicted, strict=True))[::4],
        [
            ("t", "s", ".2f"),
            ("residual on the simulated motion", "m^2/s^2", ".3f"),
            ("a^2 t dt", "m^2/s^2", ".3f"),
        ],
        "The residual of the identity on the explicit Euler fall, and the value the "
        "derivation gives, to three decimals.",
    )
    return len(fall.t), np.max(np.abs(residual - predicted))


def energy_factor(experiment: Experiment):
    """The energy of the oscillator after whole periods against the theorem;
    record the table."""
    simulated = simulate(released, oscillator, dt, n_steps)
    measured = energy(simulated, mass, k)
    factor = 1 + k / mass * dt**2
    proved = factor ** np.arange(n_steps + 1) * measured[0]

    relative = np.abs(measured / proved - 1)
    rows = [
        (n, measured[n], proved[n]) for n in range(0, n_steps + 1, steps_per_period)
    ]
    experiment.table(
        "energy-factor",
        rows,
        [
            ("steps", "", "d"),
            ("energy measured", "J", ".4f"),
            ("energy from the theorem", "J", ".4f"),
        ],
        "The energy of the simulated oscillator after whole periods, and the energy "
        "the theorem predicts, to four decimals.",
    )
    return factor, relative


def draw_proved_energy_growth() -> Figure:
    """The simulated energy and the theorem at three steps."""
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    for n, colour in ((32, "#93003a"), (64, "#00429d"), (128, "#555555")):
        step = period / n
        steps = 3 * n
        simulated = energy(simulate(released, oscillator, step, steps), mass, k)
        theorem = (1 + k / mass * step**2) ** np.arange(steps + 1) * simulated[0]
        time = step * np.arange(steps + 1)
        ax.semilogy(
            time,
            simulated / simulated[0],
            color=colour,
            linestyle="-",
            linewidth=3,
            label=f"simulated, {n} steps per period",
        )
        ax.semilogy(
            time,
            theorem / simulated[0],
            color="white",
            linestyle="--",
            linewidth=1.2,
            label="_nolegend_",
        )
    ax.set_xlabel("time (s)")
    ax.set_ylabel("energy / initial energy")
    ax.legend(loc="upper left")
    return fig


def symplectic_step(x, v):
    v_new = v - k / mass * x * dt
    return x + dt * v_new, v_new


def spring_energy(x, v):
    return 0.5 * mass * v**2 + 0.5 * k * x**2


def symplectic_ratios(experiment: Experiment, factor) -> None:
    """Exercise: the ratio of the energies after and before a step for
    symplectic Euler over one period, and for explicit Euler; record the
    table."""
    x, v = 1.0, 0.0
    ratios = []
    for _ in range(steps_per_period):
        x_new, v_new = symplectic_step(x, v)
        ratios.append(spring_energy(x_new, v_new) / spring_energy(x, v))
        x, v = x_new, v_new

    experiment.table(
        "symplectic-ratios",
        [
            ("symplectic Euler, smallest over one period", min(ratios)),
            ("symplectic Euler, largest over one period", max(ratios)),
            ("explicit Euler, at every step", factor),
        ],
        [("rule", "", ""), ("energy after a step / energy before", "", ".4f")],
        "The ratio of the energies after and before a step for the two rules, to "
        "four decimals.",
    )


def run() -> Experiment:
    """Everything the lesson's page shows."""
    experiment = Experiment()
    experiment.figure("fig-theorem-pipeline", draw_theorem_pipeline)
    residual = exact_residual(experiment)
    experiment.number("exact-residual", shown(np.max(np.abs(residual))))
    instants, largest = euler_residual(experiment)
    experiment.number("instants", instants)
    experiment.number("euler-residual-gap", shown(largest))
    factor, relative = energy_factor(experiment)
    experiment.number("factor", factor, ".6f")
    experiment.number("relative", shown(np.max(relative)))
    experiment.figure("fig-proved-energy-growth", draw_proved_energy_growth)
    symplectic_ratios(experiment, factor)
    return experiment


if __name__ == "__main__":
    main(run)
