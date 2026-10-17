"""The experiment of the lesson "Particles in a box".

A gas of hard discs in a box (``pbc.abm.gas``): how it relaxes to the
Maxwell distribution, and its temperature, pressure, and speeds against
kinetic theory. Run it as a program to write the figures and numbers of the
page:

    uv run --locked --no-dev \\
        python -m pbc.thermodynamics.experiments.particles_in_a_box out
"""

from functools import partial

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from pbc.abm import gas
from pbc.abm.acceptance import FALSE_FAILURE, agreement, t_factor
from pbc.abm.gas import (
    DT,
    EVERY,
    N_DISCS,
    RADIUS,
    RELAX,
    SIDE,
    SPEED,
    initial_gas,
    measure,
    rayleigh_pdf,
    speed_ratio,
    temperature,
    virial_correction,
)
from pbc.abm.gas import run as run_gas
from pbc.experiment import Experiment, main

# region: setup
SEEDS = range(12)  # twelve independent runs, fixed before they are made
THRESHOLD = 1.9  # the ratio that counts as settled; the Maxwell value is 2
# The systematic difference allowed between the model and 1 + 2 phi, on top
# of the statistical tolerance: the time step places collisions late and
# lowers the pressure, the series stops at its first correction, and the
# walls of a small box thin the gas in the middle a little.
PRESSURE_ALLOWANCE = 0.015
# endregion: setup

# The parts of the allowance, measured once with many more seeds and smaller
# steps than the page runs (Issue #206). Over 240 seeds at the lesson's step,
# P / P_ideal is 1.0542 with a spread of 0.0089 between runs, 0.0091 below
# 1 + 2 phi = 1.0633; at dt = 1 ms it is 1.0612 (100 seeds) and at 0.5 ms
# 1.0596 (60 seeds). The parts add up to about 0.012, and the allowance
# rounds that up. More runs do not reduce any of them.
TIME_STEP_SHIFT = 0.007  # pressure lost because collisions are placed late
# Hard discs crowd along a wall, so the middle of the box holds about
# (8/3) n (2r)^3 / L = 0.16 % fewer discs per area than N / A.
WALL_SHIFT = 0.002


def next_virial_term(packing_fraction: float) -> float:
    """The term after 1 + 2 phi in the virial series of hard discs,
    4 (4/3 - sqrt(3)/pi) phi^2, from the third virial coefficient
    B_3 = (4/3 - sqrt(3)/pi) B_2^2; the prediction of the page leaves it
    out."""
    return 4.0 * (4.0 / 3.0 - np.sqrt(3.0) / np.pi) * packing_fraction**2


def ratio_allowance(n: int) -> float:
    """The systematic difference allowed between the moment ratio and the
    Maxwell value two: a gas of ``n`` discs whose energy is fixed has the
    ratio 2 n / (n + 1), not two, because one disc cannot take more than
    the energy of all of them; the difference is 2 / (n + 1)."""
    return 2.0 / (n + 1)


def relaxation_history(experiment: Experiment):
    """Twelve runs from equal speeds, and the ratio of the moments of the speed
    over time; record the table of three moments."""
    histories = []
    for seed in SEEDS:
        start = initial_gas(N_DISCS, RADIUS, SIDE, SPEED, np.random.default_rng(seed))
        recorded = run_gas(start, 1.5, DT, EVERY)
        histories.append([speed_ratio(row) for row in recorded.speeds])
    times = recorded.times
    ratio_history = np.mean(histories, axis=0)

    assert (ratio_history > THRESHOLD).any(), "the ratio never reached the threshold"
    settled = times[np.argmax(ratio_history > THRESHOLD)]
    assert settled < RELAX, "the gas settled after the relaxation time"

    experiment.table(
        "relaxation-history",
        [
            ("start", times[0], ratio_history[0]),
            (
                "first above the threshold",
                settled,
                ratio_history[np.argmax(ratio_history > THRESHOLD)],
            ),
            ("end of the run", times[-1], ratio_history[-1]),
        ],
        [("moment", "", ""), ("time", "s", ".2f"), ("ratio of the moments", "", ".2f")],
        "The ratio of the fourth moment of the speed to the square of the second, "
        "averaged over twelve runs, at three moments of the relaxation.",
    )
    return times, ratio_history, settled


def draw_relaxation(times, ratio_history) -> Figure:
    """The ratio of the moments against time."""
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.plot(
        times, ratio_history, color="#00429d", marker="o", markersize=3, label="gas"
    )
    ax.axhline(2.0, color="#93003a", linestyle="--", label="Maxwell distribution")
    ax.set_xlabel("time (s)")
    ax.set_ylabel(r"$\langle v^4\rangle / \langle v^2\rangle^2$")
    ax.legend()
    return fig


def kinetic_theory_check(experiment: Experiment):
    """Twelve measured runs, and the rule of the lesson for their moment
    ratio and pressure against kinetic theory; record the table."""
    measurements = [measure(seed) for seed in SEEDS]

    ratio = agreement(
        [speed_ratio(m.speeds) for m in measurements],
        2.0,
        ratio_allowance(N_DISCS),
    )
    pressures = [m.pressure / m.ideal_pressure for m in measurements]
    pressure = agreement(
        pressures,
        virial_correction(measurements[0].packing_fraction),
        PRESSURE_ALLOWANCE,
    )
    ideal = agreement(pressures, 1.0, PRESSURE_ALLOWANCE)

    experiment.table(
        "kinetic-theory-check",
        [
            (
                name,
                a.mean,
                a.error,
                a.theory,
                a.difference,
                a.tolerance,
                "yes" if a.agrees else "no",
            )
            for name, a in (
                ("moment ratio", ratio),
                ("P / P_ideal", pressure),
                ("P / P_ideal against the ideal gas law alone", ideal),
            )
        ],
        [
            ("quantity", "", ""),
            ("mean over twelve runs", "", ".3f"),
            ("standard error", "", ".3f"),
            ("theory", "", ".3f"),
            ("difference", "", "+.3f"),
            ("tolerance", "", ".3f"),
            ("within the tolerance", "", ""),
        ],
        "Each quantity averaged over twelve runs, with its standard error, the "
        "theory, the difference, and the tolerance of the rule: the allowance "
        "plus the t factor times the standard error.",
    )
    return measurements, ratio, pressure, ideal


def draw_speeds(measurements) -> Figure:
    """The pooled speeds of the twelve runs against the Maxwell distribution."""
    pooled = np.concatenate([m.speeds.ravel() for m in measurements])
    kt = temperature(pooled, 1.0)
    v = np.linspace(0.0, pooled.max(), 200)

    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.hist(pooled, bins=40, density=True, color="#9ecae1", label="gas")
    ax.plot(
        v,
        rayleigh_pdf(v, kt, 1.0),
        color="#93003a",
        linestyle="--",
        label="Maxwell distribution",
    )
    ax.set_xlabel("speed (m/s)")
    ax.set_ylabel("probability density (s/m)")
    ax.legend()
    return fig


def denser_gas(experiment: Experiment) -> None:
    """Exercise 1: a gas at a packing fraction of five per cent; record the
    table."""
    free = SIDE - 2.0 * RADIUS
    n_dense = round(0.05 * free**2 / (np.pi * RADIUS**2))
    dense = measure(0, n=n_dense)
    experiment.table(
        "denser-gas",
        [
            (
                n_dense,
                dense.packing_fraction,
                virial_correction(dense.packing_fraction),
                dense.pressure / dense.ideal_pressure,
            )
        ],
        [
            ("discs", "", "d"),
            ("packing fraction", "", ".3f"),
            ("predicted P / P_ideal", "", ".3f"),
            ("measured P / P_ideal", "", ".3f"),
        ],
        "The denser gas of one seed: the number of discs, the packing fraction, and "
        "the predicted and measured pressure.",
    )


def final_speeds(seed):
    gas0 = initial_gas(N_DISCS, RADIUS, SIDE, SPEED, np.random.default_rng(seed))
    return run_gas(gas0, 0.5, DT, 250).speeds[-1]


def same_seed(experiment: Experiment) -> None:
    """Exercise 2: whether two runs of one seed, and of two seeds, end with
    identical speeds; record the table."""
    first, again, other = final_speeds(0), final_speeds(0), final_speeds(1)
    experiment.table(
        "same-seed",
        [
            ("seed 0 twice", "yes" if np.array_equal(first, again) else "no"),
            ("seed 0 against seed 1", "yes" if np.array_equal(first, other) else "no"),
        ],
        [("comparison", "", ""), ("identical final speeds", "", "")],
        "Whether the final speeds of two runs are identical.",
    )


def run() -> Experiment:
    """Everything the lesson's page shows."""
    experiment = Experiment()
    experiment.number("n-discs", gas.N_DISCS)
    experiment.number("radius-mm", gas.RADIUS * 1000, ".0f")
    experiment.number("side", gas.SIDE, ".0f")
    experiment.number("speed", gas.SPEED, ".0f")
    experiment.number("dt-ms", gas.DT * 1000, ".0f")
    experiment.number(
        "diameters-per-step", gas.SPEED * gas.DT / (2 * gas.RADIUS), ".2f"
    )
    experiment.number(
        "packing-fraction",
        gas.initial_gas(
            gas.N_DISCS, gas.RADIUS, gas.SIDE, gas.SPEED, np.random.default_rng(0)
        ).packing_fraction,
        ".3f",
    )

    times, ratio_history, settled = relaxation_history(experiment)
    experiment.figure("fig-relaxation", partial(draw_relaxation, times, ratio_history))
    experiment.number("threshold", THRESHOLD)
    experiment.number("first-ratio", ratio_history[0], ".2f")
    experiment.number("settled", settled, ".2f")
    experiment.number("relax", RELAX, ".1f")
    experiment.number("duration", gas.DURATION, ".1f")

    measurements, ratio, pressure, ideal = kinetic_theory_check(experiment)
    experiment.number("n-runs", len(SEEDS))
    experiment.number("false-failure", round(1 / FALSE_FAILURE))
    experiment.number("t-factor", t_factor(len(SEEDS)), ".2f")
    experiment.number("ratio-allowance", ratio_allowance(N_DISCS), ".3f")
    experiment.number("pressure-allowance", PRESSURE_ALLOWANCE, ".3f")
    experiment.number("time-step-shift", TIME_STEP_SHIFT, ".3f")
    experiment.number(
        "virial-term", next_virial_term(measurements[0].packing_fraction), ".3f"
    )
    experiment.number("wall-shift", WALL_SHIFT, ".3f")
    experiment.number("ratio-mean", ratio.mean, ".3f")
    experiment.number("ratio-error", ratio.error, ".3f")
    experiment.number("ratio-tolerance", ratio.tolerance, ".3f")
    experiment.number("pressure-mean", pressure.mean, ".3f")
    experiment.number("predicted", pressure.theory, ".3f")
    experiment.number("pressure-difference", abs(pressure.difference), ".3f")
    experiment.number("pressure-tolerance", pressure.tolerance, ".3f")
    experiment.number("ideal-difference", ideal.difference, ".3f")
    experiment.number("ideal-tolerance", ideal.tolerance, ".3f")
    experiment.figure("fig-speeds", partial(draw_speeds, measurements))

    denser_gas(experiment)
    same_seed(experiment)
    return experiment


if __name__ == "__main__":
    main(run)
