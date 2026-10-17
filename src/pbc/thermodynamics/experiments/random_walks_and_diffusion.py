"""The experiment of the lesson "Random walks and diffusion".

Walkers that take steps of a fixed length in random directions
(``pbc.thermodynamics.diffusion``): their mean squared displacement, the
diffusion coefficient it gives against the step rule, and the Gaussian
spread of their positions. Run it as a program to write the figure and
numbers of the page:

    uv run --locked --no-dev \\
        python -m pbc.thermodynamics.experiments.random_walks_and_diffusion out
"""

from functools import partial

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from pbc.abm.gas import mean_and_error
from pbc.experiment import Experiment, main
from pbc.thermodynamics.diffusion import (
    diffusion_coefficient,
    fraction_within,
    mean_squared_displacement,
    predicted_diffusion_coefficient,
    predicted_fraction_within,
    random_walks,
)

# region: setup
STEP = 0.1  # step length, m
TAU = 0.5  # time between steps, s
N_WALKERS = 500
N_STEPS = 200
SEEDS = range(6)

times = TAU * np.arange(N_STEPS + 1)
predicted_d = predicted_diffusion_coefficient(STEP, TAU)
# endregion: setup


def msd_run(experiment: Experiment):
    """Six runs of the walkers, their mean squared displacement, and the
    table of three times against the step rule."""
    runs = [
        random_walks(N_WALKERS, N_STEPS, STEP, np.random.default_rng(seed))
        for seed in SEEDS
    ]
    msds = np.array([mean_squared_displacement(paths) for paths in runs])
    msd = msds.mean(axis=0)

    checkpoints = [N_STEPS // 4, N_STEPS // 2, N_STEPS]
    experiment.table(
        "msd-run",
        [(n, times[n], msd[n], 4.0 * predicted_d * times[n]) for n in checkpoints],
        [
            ("steps", "", "d"),
            ("time", "s", ".1f"),
            ("measured <r²>", "m²", ".3f"),
            ("predicted 4 D t", "m²", ".3f"),
        ],
        "The mean squared displacement averaged over six runs of the walkers, at "
        "three times, against the prediction of the step rule.",
    )
    return runs, msds, msd


def draw_msd(msd) -> Figure:
    """The mean squared displacement against time, with the step rule."""
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.plot(times, msd, color="#00429d", label="walkers")
    ax.plot(
        times,
        4.0 * predicted_d * times,
        color="#93003a",
        linestyle="--",
        label="step rule: 4 D t",
    )
    ax.set_xlabel("time (s)")
    ax.set_ylabel(r"$\langle r^2\rangle$ (m$^2$)")
    ax.legend()
    return fig


def diffusion_check(experiment: Experiment, msds):
    """The diffusion coefficient of each run, their mean, and its distance in
    standard errors from the step rule and from a wrong prediction; record
    the table of the runs."""
    estimates = np.array([diffusion_coefficient(times, row) for row in msds])
    mean_d, error_d = mean_and_error(estimates)
    off = abs(mean_d - predicted_d) / error_d
    wrong = abs(mean_d - 2.0 * predicted_d) / error_d

    experiment.table(
        "diffusion-check",
        list(zip(SEEDS, estimates, strict=True)),
        [("seed", "", "d"), ("D", "m²/s", ".5f")],
        "The diffusion coefficient measured in each of the six runs.",
    )
    return mean_d, error_d, off, wrong


def diffusion_summary(experiment: Experiment, mean_d, error_d, off, wrong) -> None:
    """Record the table of the mean coefficient against the two
    predictions."""
    experiment.table(
        "diffusion-summary",
        [
            ("step rule", mean_d, error_d, predicted_d, off),
            ("a coefficient twice as large", mean_d, error_d, 2.0 * predicted_d, wrong),
        ],
        [
            ("compared with", "", ""),
            ("mean D", "m²/s", ".5f"),
            ("standard error", "m²/s", ".5f"),
            ("prediction", "m²/s", ".5f"),
            ("difference", "standard errors", ".1f"),
        ],
        "The mean of the six measured coefficients, its standard error, and its "
        "distance in standard errors from the step rule and from a wrong "
        "prediction.",
    )


def radial_check(experiment: Experiment, runs) -> list:
    """The fraction of walkers within three radii after the last step against
    the Gaussian prediction; record the table and return its rows."""
    t_end = times[-1]
    radii = np.sqrt(
        4.0 * predicted_d * t_end * -np.log(1.0 - np.array([0.25, 0.5, 0.75]))
    )
    rows = []
    for radius in radii:
        measured = np.array([fraction_within(paths[-1], radius) for paths in runs])
        mean_f, error_f = mean_and_error(measured)
        predicted_f = predicted_fraction_within(radius, predicted_d, t_end)
        rows.append(
            (radius, mean_f, error_f, predicted_f, abs(mean_f - predicted_f) / error_f)
        )

    experiment.table(
        "radial-check",
        rows,
        [
            ("radius", "m", ".2f"),
            ("measured fraction", "", ".3f"),
            ("standard error", "", ".3f"),
            ("predicted fraction", "", ".3f"),
            ("difference", "standard errors", ".1f"),
        ],
        "The fraction of walkers within three radii after the last step, over six "
        "runs, against the Gaussian prediction.",
    )
    return rows


def doubled_step(experiment: Experiment, mean_d) -> None:
    """Exercise 1: the diffusion coefficient of the doubled step in units of
    the first; record the table."""
    doubled = [
        random_walks(N_WALKERS, N_STEPS, 2.0 * STEP, np.random.default_rng(seed))
        for seed in SEEDS
    ]
    doubled_d = np.array(
        [diffusion_coefficient(times, mean_squared_displacement(p)) for p in doubled]
    )
    mean_2, error_2 = mean_and_error(doubled_d)
    experiment.table(
        "doubled-step",
        [(mean_2 / mean_d, 4.0, error_2 / mean_d)],
        [
            ("measured ratio", "", ".2f"),
            ("predicted ratio", "", ".1f"),
            ("standard error of the ratio", "", ".2f"),
        ],
        "The measured diffusion coefficient of the doubled step in units of the "
        "first, with the predicted ratio.",
    )


def on_a_line(experiment: Experiment) -> None:
    """Exercise 2: the diffusion coefficient of walkers on a line; record the
    table."""
    line = [
        diffusion_coefficient(
            times,
            mean_squared_displacement(
                random_walks(
                    N_WALKERS, N_STEPS, STEP, np.random.default_rng(seed), dimension=1
                )
            ),
            dimension=1,
        )
        for seed in SEEDS
    ]
    mean_1, error_1 = mean_and_error(np.array(line))
    predicted_1 = predicted_diffusion_coefficient(STEP, TAU, dimension=1)
    experiment.table(
        "on-a-line",
        [(mean_1, error_1, predicted_1, abs(mean_1 - predicted_1) / error_1)],
        [
            ("measured D", "m²/s", ".5f"),
            ("standard error", "m²/s", ".5f"),
            ("predicted D", "m²/s", ".5f"),
            ("difference", "standard errors", ".1f"),
        ],
        "The diffusion coefficient of walkers on a line, over six runs, against "
        "the prediction.",
    )


def run() -> Experiment:
    """Everything the lesson's page shows."""
    experiment = Experiment()
    runs, msds, msd = msd_run(experiment)
    experiment.figure("fig-msd", partial(draw_msd, msd))
    mean_d, error_d, off, wrong = diffusion_check(experiment, msds)
    diffusion_summary(experiment, mean_d, error_d, off, wrong)
    experiment.number("mean-d", mean_d, ".5f")
    experiment.number("error-d", error_d, ".5f")
    experiment.number("off", off, ".1f")
    experiment.number("predicted-d", predicted_d, ".5f")
    experiment.number("wrong", wrong, ".0f")
    rows = radial_check(experiment, runs)
    experiment.number("largest-difference", max(row[4] for row in rows), ".1f")
    doubled_step(experiment, mean_d)
    on_a_line(experiment)
    return experiment


if __name__ == "__main__":
    main(run)
