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
from pbc.abm.gas import (
    DT,
    EVERY,
    N_DISCS,
    RADIUS,
    RELAX,
    SIDE,
    SPEED,
    initial_gas,
    mean_and_error,
    measure,
    rayleigh_pdf,
    speed_ratio,
    temperature,
    virial_correction,
)
from pbc.abm.gas import run as run_gas
from pbc.experiment import Experiment, main

# region: setup
SEEDS = range(6)
THRESHOLD = 1.9  # the ratio that counts as settled; the Maxwell value is 2
# endregion: setup


def relaxation_history(experiment: Experiment):
    """Six runs from equal speeds, and the ratio of the moments of the speed
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
        "averaged over six runs, at three moments of the relaxation.",
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
    """Six measured runs and the means of their moment ratio and pressure
    against kinetic theory; record the table."""
    measurements = [measure(seed) for seed in SEEDS]

    ratio_mean, ratio_error = mean_and_error(
        np.array([speed_ratio(m.speeds) for m in measurements])
    )
    pressure_mean, pressure_error = mean_and_error(
        np.array([m.pressure / m.ideal_pressure for m in measurements])
    )
    predicted = virial_correction(measurements[0].packing_fraction)

    experiment.table(
        "kinetic-theory-check",
        [
            (
                "moment ratio",
                ratio_mean,
                ratio_error,
                2.0,
                abs(ratio_mean - 2.0) / ratio_error,
            ),
            (
                "P / P_ideal",
                pressure_mean,
                pressure_error,
                predicted,
                abs(pressure_mean - predicted) / pressure_error,
            ),
            (
                "P / P_ideal against the ideal gas law alone",
                pressure_mean,
                pressure_error,
                1.0,
                (pressure_mean - 1.0) / pressure_error,
            ),
        ],
        [
            ("quantity", "", ""),
            ("mean over six runs", "", ".3f"),
            ("standard error", "", ".3f"),
            ("theory", "", ".3f"),
            ("difference", "standard errors", ".1f"),
        ],
        "Each quantity averaged over six runs, with its standard error, the theory, "
        "and the difference between them in standard errors.",
    )
    return (
        measurements,
        (ratio_mean, ratio_error),
        (pressure_mean, pressure_error),
        predicted,
    )


def draw_speeds(measurements) -> Figure:
    """The pooled speeds of the six runs against the Maxwell distribution."""
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

    (
        measurements,
        (ratio_mean, ratio_error),
        (pressure_mean, pressure_error),
        predicted,
    ) = kinetic_theory_check(experiment)
    experiment.number("ratio-mean", ratio_mean, ".2f")
    experiment.number("ratio-error", ratio_error, ".2f")
    experiment.number("ratio-distance", abs(ratio_mean - 2.0) / ratio_error, ".1f")
    experiment.number("pressure-mean", pressure_mean, ".3f")
    experiment.number("predicted", predicted, ".3f")
    experiment.number(
        "pressure-distance", abs(pressure_mean - predicted) / pressure_error, ".1f"
    )
    experiment.number("ideal-distance", (pressure_mean - 1.0) / pressure_error, ".0f")
    experiment.figure("fig-speeds", partial(draw_speeds, measurements))

    denser_gas(experiment)
    same_seed(experiment)
    return experiment


if __name__ == "__main__":
    main(run)
