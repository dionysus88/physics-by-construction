"""The experiment of the lesson "Kinetic theory of gases".

The speeds of the discs of the gas of the agent-based lesson
(``pbc.abm.gas``) against the Maxwell distribution in two dimensions
(``pbc.thermodynamics.kinetic``), at the temperature each run measured.
Run it as a program to write the figure and numbers of the page:

    uv run --locked --no-dev \\
        python -m pbc.thermodynamics.experiments.kinetic_theory_of_gases out
"""

from functools import partial

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from pbc.abm.gas import SPEED, mean_and_error, measure
from pbc.experiment import Experiment, main
from pbc.thermodynamics.kinetic import (
    fractions_below,
    mean_speed,
    most_probable_speed,
    speed_cdf,
    speed_quantile,
)

# region: setup
MASS = 1.0  # the mass of a disc in pbc.abm.gas, kg
SEEDS = range(6)
PROBABILITIES = np.array([0.1, 0.25, 0.5, 0.75, 0.9])
# endregion: setup


def quantile_check(experiment: Experiment):
    """Six runs of the gas, and the fraction of their speeds below the
    quantile speeds of the Maxwell distribution; record the table and return
    the measurements and the distances in standard errors."""
    measurements = [measure(seed) for seed in SEEDS]
    fractions = np.array(
        [
            fractions_below(m.speeds, speed_quantile(PROBABILITIES, m.kt, MASS))
            for m in measurements
        ]
    )
    means = fractions.mean(axis=0)
    errors = fractions.std(axis=0, ddof=1) / np.sqrt(len(measurements))
    distances = np.abs(means - PROBABILITIES) / errors

    experiment.table(
        "quantile-check",
        list(zip(PROBABILITIES, means, errors, distances, strict=True)),
        [
            ("predicted fraction", "", ".2f"),
            ("measured fraction", "", ".3f"),
            ("standard error", "", ".3f"),
            ("difference", "standard errors", ".1f"),
        ],
        "The fraction of the speeds below the quantile speed of the Maxwell "
        "distribution at the temperature of each run, averaged over six runs, at "
        "five predicted fractions.",
    )
    return measurements, distances


def wrong_temperature(experiment: Experiment, measurements):
    """The same comparison at a temperature ten per cent too high; record the
    table and return the distances in standard errors."""
    scale = 1.1
    wrong = np.array(
        [
            fractions_below(m.speeds, speed_quantile(PROBABILITIES, scale * m.kt, MASS))
            for m in measurements
        ]
    )
    wrong_means = wrong.mean(axis=0)
    wrong_errors = wrong.std(axis=0, ddof=1) / np.sqrt(len(measurements))
    wrong_distances = np.abs(wrong_means - PROBABILITIES) / wrong_errors

    experiment.table(
        "wrong-temperature",
        list(zip(PROBABILITIES, wrong_means, wrong_distances, strict=True)),
        [
            ("predicted fraction", "", ".2f"),
            ("measured fraction", "", ".3f"),
            ("difference", "standard errors", ".1f"),
        ],
        "The same comparison against the distribution at a temperature ten per "
        "cent too high.",
    )
    return wrong_distances


def draw_speed_distribution(measurements) -> Figure:
    """The pooled speeds of the six runs against the Maxwell distribution."""
    pooled = np.concatenate([m.speeds.ravel() for m in measurements])
    kt = float(np.mean([m.kt for m in measurements]))
    v = np.linspace(0.0, pooled.max(), 300)

    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.plot(v, fractions_below(pooled, v), color="#00429d", label="gas")
    ax.plot(
        v,
        speed_cdf(v, kt, MASS),
        color="#93003a",
        linestyle="--",
        label="Maxwell distribution",
    )
    ax.set_xlabel("speed (m/s)")
    ax.set_ylabel("fraction of discs slower")
    ax.legend()
    return fig


def mean_speed_check(experiment: Experiment, measurements):
    """The two characteristic speeds at the mean temperature, and the ratio
    of the measured mean speed to the predicted one; record the table."""
    kt = float(np.mean([m.kt for m in measurements]))
    ratios = np.array(
        [np.mean(m.speeds) / mean_speed(m.kt, MASS) for m in measurements]
    )
    ratio_mean, ratio_error = mean_and_error(ratios)

    experiment.table(
        "mean-speed-check",
        [
            (
                mean_speed(kt, MASS),
                most_probable_speed(kt, MASS),
                ratio_mean,
                ratio_error,
                abs(ratio_mean - 1.0) / ratio_error,
            )
        ],
        [
            ("mean speed", "m/s", ".3f"),
            ("most probable speed", "m/s", ".3f"),
            ("measured mean / predicted mean", "", ".4f"),
            ("standard error", "", ".4f"),
            ("difference", "standard errors", ".1f"),
        ],
        "The two characteristic speeds at the mean temperature of the six runs, "
        "and the ratio of the measured mean speed to the predicted one.",
    )
    return ratio_mean, ratio_error


def hot_gas(experiment: Experiment, measurements) -> None:
    """Exercise 1: a gas started twice as fast; record the table."""
    hot = measure(0, speed=2.0 * SPEED)
    cold = measurements[0]
    median = speed_quantile(np.array([0.5]), hot.kt, MASS)
    experiment.table(
        "hot-gas",
        [(hot.kt / cold.kt, fractions_below(hot.speeds, median)[0])],
        [
            ("temperature ratio", "", ".2f"),
            ("fraction below the predicted median", "", ".3f"),
        ],
        "The temperature of the hot gas in units of that of the first gas, and the "
        "fraction of its speeds below the median of the model at its own "
        "temperature.",
    )


def before_relaxation(experiment: Experiment) -> None:
    """Exercise 2: a gas measured during its first half second; record the
    table."""
    start = measure(0, relax=0.0, duration=0.5)
    raw = fractions_below(start.speeds, speed_quantile(PROBABILITIES, start.kt, MASS))
    experiment.table(
        "before-relaxation",
        list(zip(PROBABILITIES, raw, strict=True)),
        [("predicted fraction", "", ".2f"), ("measured fraction", "", ".3f")],
        "The fraction of the speeds below each quantile of the model, for a gas "
        "measured during its first half second.",
    )


def run() -> Experiment:
    """Everything the lesson's page shows."""
    experiment = Experiment()
    measurements, distances = quantile_check(experiment)
    experiment.number("largest-distance", distances.max(), ".1f")
    wrong_distances = wrong_temperature(experiment, measurements)
    experiment.number("wrong-failures", int((wrong_distances > 4.0).sum()))
    experiment.number("wrong-largest", wrong_distances.max(), ".0f")
    experiment.figure(
        "fig-speed-distribution", partial(draw_speed_distribution, measurements)
    )
    ratio_mean, ratio_error = mean_speed_check(experiment, measurements)
    experiment.number("ratio-mean", ratio_mean, ".4f")
    experiment.number("ratio-distance", abs(ratio_mean - 1.0) / ratio_error, ".1f")
    hot_gas(experiment, measurements)
    before_relaxation(experiment)
    return experiment


if __name__ == "__main__":
    main(run)
