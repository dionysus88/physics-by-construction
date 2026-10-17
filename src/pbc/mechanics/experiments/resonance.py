"""The experiment of the lesson "Resonance".

The driven, damped oscillator (``pbc.mechanics.resonance``): its transient
against the exact motion, its resonance curve and phase lag, the peak and
the width of the resonance, and the time it takes to settle. Run it as a
program to write the figures and numbers of the page:

    uv run --locked --no-dev python -m pbc.mechanics.experiments.resonance out
"""

from functools import partial

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from pbc.authoring import FIGURE_COLOURS
from pbc.experiment import Experiment, main
from pbc.mechanics.drag import linear_drag
from pbc.mechanics.dynamics import State, newton, simulate
from pbc.mechanics.integrators import rk4_step
from pbc.mechanics.oscillator import spring
from pbc.mechanics.resonance import (
    damping_rate,
    driven_motion,
    driving_force,
    half_power_width,
    measured_resonance_curve,
    natural_frequency,
    peak_frequency,
    quality_factor,
    steady_state_amplitude,
    steady_state_phase,
)

# region: setup
mass, k, b, force = 1.0, 4.0, 0.4, 2.0
w0 = natural_frequency(mass, k)
q = quality_factor(mass, k, b)
gamma = damping_rate(mass, b)
start = State(t=0.0, x=[0.0], v=[0.0])
# endregion: setup


def closed_form_check(experiment: Experiment):
    """Forty seconds of the oscillator driven at 1.7 rad/s from rest against
    its exact solution; record the table and return the run, the exact
    motion, the largest difference, and the steady-state amplitude."""
    omega = 1.7  # rad/s
    oscillator = newton(mass, spring(k), linear_drag(b), driving_force(force, omega))
    driven = simulate(start, oscillator, 0.005, 8000, step=rk4_step)
    exact = driven_motion(start, mass, k, b, force, omega, driven.t)
    largest = np.max(np.abs(driven.x - exact.x))
    steady = float(steady_state_amplitude(mass, k, b, force, omega))

    experiment.table(
        "closed-form-check",
        [(np.max(np.abs(driven.x)), steady, largest)],
        columns=[
            ("largest displacement of the run", "m", ".4f"),
            ("steady-state amplitude", "m", ".4f"),
            ("largest difference from the exact motion", "m", ".1e"),
        ],
        caption="The simulated motion of the driven oscillator from rest for forty "
        "seconds against its exact solution, with the transient.",
    )
    return driven, exact, largest, steady


def draw_transient(driven, exact) -> Figure:
    """The displacement from rest, simulated and exact."""
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.plot(
        driven.t,
        driven.x[:, 0],
        color=FIGURE_COLOURS[0],
        linestyle="-",
        label="simulation",
    )
    ax.plot(
        driven.t, exact.x[:, 0], color=FIGURE_COLOURS[1], linestyle="--", label="exact"
    )
    ax.set_xlabel("time (s)")
    ax.set_ylabel("displacement (m)")
    ax.legend(loc="upper right")
    return fig


def resonance_curve(experiment: Experiment):
    """The amplitude and phase lag of the steady state over the driving
    frequency, simulated and closed form; record the table of every third
    frequency."""
    omegas = np.concatenate(
        [
            np.arange(0.4, 1.2, 0.2),
            np.arange(1.2, 2.85, 0.05),
            np.arange(3.0, 4.01, 0.2),
        ]
    )
    measured, phase = measured_resonance_curve(
        mass, k, b, force, omegas, decay_times=8.0
    )
    analytic = steady_state_amplitude(mass, k, b, force, omegas)
    analytic_phase = steady_state_phase(mass, k, b, omegas)

    pick = np.arange(0, len(omegas), 3)
    experiment.table(
        "resonance-curve",
        [
            (omegas[i], analytic[i], measured[i], analytic_phase[i], phase[i])
            for i in pick
        ],
        columns=[
            ("driving frequency", "rad/s", ".2f"),
            ("amplitude, closed form", "m", ".4f"),
            ("amplitude, simulation", "m", ".4f"),
            ("phase lag, closed form", "rad", ".3f"),
            ("phase lag, simulation", "rad", ".3f"),
        ],
        caption="Amplitude and phase lag of the driven oscillator at a third of the "
        "frequencies of the curve: the closed form and the simulation, to four "
        "and three decimals.",
    )
    return omegas, measured, phase, analytic, analytic_phase


def draw_resonance_curve(omegas, measured) -> Figure:
    """The resonance curve, closed form and simulated."""
    dense = np.linspace(0.4, 4.0, 600)
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.plot(
        dense,
        steady_state_amplitude(mass, k, b, force, dense),
        color=FIGURE_COLOURS[0],
        linestyle="-",
        label="closed form",
    )
    ax.plot(
        omegas,
        measured,
        color=FIGURE_COLOURS[1],
        marker="o",
        linestyle="",
        markersize=4,
        label="simulation",
    )
    ax.axvline(w0, color="#57606a", linestyle=":", label="natural frequency")
    ax.set_xlabel("driving frequency (rad/s)")
    ax.set_ylabel("amplitude (m)")
    ax.legend(loc="upper right")
    return fig


def peak_and_width(experiment: Experiment, omegas, measured):
    """The peak and the width of the resonance, closed form and read from the
    simulated curve; record the table."""
    width = half_power_width(omegas, measured)
    w_peak = peak_frequency(mass, k, b)
    exact_peak = float(steady_state_amplitude(mass, k, b, force, w_peak))
    rows = [
        ("peak frequency", "rad/s", w_peak, omegas[np.argmax(measured)]),
        ("peak height", "m", exact_peak, np.max(measured)),
        ("full width at half power", "rad/s", b / mass, width),
        ("quality factor", "", q, w0 / width),
    ]
    experiment.table(
        "peak-and-width",
        rows,
        columns=[
            ("quantity", "", ""),
            ("unit", "", ""),
            ("closed form", "", ".3f"),
            ("from the simulated curve", "", ".3f"),
        ],
        caption="The peak frequency, height, width at half power, and quality "
        "factor of the resonance: the closed forms and the values read from the "
        "simulated curve, to three decimals.",
    )
    return width, w_peak, exact_peak


def settling(experiment: Experiment) -> list:
    """The time the transient takes to stay below one per cent of the steady
    state, for two quality factors; record the table and return its rows."""
    rows = []
    for factor in (1.0, 0.25):
        b_case = b * factor
        amplitude = float(steady_state_amplitude(mass, k, b_case, force, w0))
        delta = float(steady_state_phase(mass, k, b_case, w0))
        t = np.linspace(0.0, 400.0, 400001)
        motion = driven_motion(start, mass, k, b_case, force, w0, t)
        leftover = np.abs(motion.x[:, 0] - amplitude * np.cos(w0 * t - delta))
        settled = t[np.where(leftover > 0.01 * amplitude)[0][-1]]
        rows.append(
            (quality_factor(mass, k, b_case), settled, 1.0 / damping_rate(mass, b_case))
        )

    experiment.table(
        "settling",
        rows,
        columns=[
            ("quality factor", "", ".1f"),
            ("time to settle to one per cent", "s", ".1f"),
            ("decay time 1/gamma", "s", ".1f"),
        ],
        caption="The time after which the transient stays below one per cent of the "
        "steady-state amplitude, for two quality factors, with the decay time of "
        "the free motion.",
    )
    return rows


def free_decay(experiment: Experiment) -> float:
    """Exercise 1: the decay rate and the quality factor from the peaks of
    the free motion; record the table and return the decay rate, in 1/s."""
    free = simulate(
        State(0.0, [1.0], [0.0]),
        newton(mass, spring(k), linear_drag(b)),
        0.005,
        8000,
        step=rk4_step,
    )
    x = free.x[:, 0]
    peaks = np.where((x[1:-1] > x[:-2]) & (x[1:-1] >= x[2:]) & (x[1:-1] > 0))[0] + 1
    slope, _ = np.polyfit(free.t[peaks], np.log(x[peaks]), 1)
    rate = -slope
    q_free = w0 / (2.0 * rate)

    experiment.table(
        "free-decay",
        [(rate, gamma, q_free, q)],
        columns=[
            ("decay rate from the peaks", "1/s", ".4f"),
            ("b / 2m", "1/s", ".4f"),
            ("Q from the decay", "", ".3f"),
            ("Q from the parameters", "", ".3f"),
        ],
        caption="The decay rate and the quality factor read from the peaks of the "
        "free motion and from the parameters, to the precision shown.",
    )
    return rate


def doubled_damping(experiment: Experiment) -> list:
    """Exercise 2: the peak height for the damping constant and for twice it;
    record the table and return the heights, in m."""
    heights = []
    for factor in (1.0, 2.0):
        b_case = b * factor
        top = steady_state_amplitude(
            mass, k, b_case, force, peak_frequency(mass, k, b_case)
        )
        heights.append(float(top))

    experiment.table(
        "doubled-damping",
        [(1.0, heights[0], 1.0), (2.0, heights[1], heights[1] / heights[0])],
        columns=[
            ("damping, in units of b", "", ".1f"),
            ("peak height", "m", ".4f"),
            ("relative to the first", "", ".3f"),
        ],
        caption="The peak height of the resonance curve for the damping constant and "
        "for twice it, to four decimals, with the ratio.",
    )
    return heights


def run() -> Experiment:
    """Everything the lesson's page shows."""
    experiment = Experiment()
    driven, exact, largest, steady = closed_form_check(experiment)
    experiment.number("largest", largest, ".0e")
    experiment.number("steady", steady, ".2f")
    experiment.number("largest-displacement", np.max(np.abs(driven.x)), ".2f")
    experiment.figure("fig-transient", partial(draw_transient, driven, exact))

    omegas, measured, phase, analytic, analytic_phase = resonance_curve(experiment)
    experiment.figure(
        "fig-resonance-curve", partial(draw_resonance_curve, omegas, measured)
    )
    experiment.number(
        "amplitude-difference", np.max(np.abs(measured / analytic - 1.0)), ".0e"
    )
    experiment.number("phase-difference", np.max(np.abs(phase - analytic_phase)), ".0e")
    experiment.number("quarter-turn", np.pi / 2, ".3f")

    width, w_peak, exact_peak = peak_and_width(experiment, omegas, measured)
    experiment.number("w-peak", w_peak, ".3f")
    experiment.number("w0", w0, ".3f")
    experiment.number("sampled-peak", omegas[np.argmax(measured)], ".2f")
    experiment.number("weak-damping-height", q * force / k, ".3f")
    experiment.number(
        "weak-damping-error", abs(q * force / k / exact_peak - 1.0), ".1%"
    )
    experiment.number("width", width, ".3f")
    experiment.number("b-over-m", b / mass, ".3f")
    experiment.number("q-from-width", w0 / width, ".2f")
    experiment.number("q", q, ".2f")
    experiment.number("q-difference", abs(w0 / width / q - 1.0), ".0%")

    rows = settling(experiment)
    experiment.number("settling-decays-1", rows[0][1] / rows[0][2], ".1f")
    experiment.number("settling-decays-2", rows[1][1] / rows[1][2], ".1f")
    experiment.number("q-ratio", rows[1][0] / rows[0][0], ".0f")
    experiment.number("settling-ratio", rows[1][1] / rows[0][1], ".1f")

    rate = free_decay(experiment)
    experiment.number("rate-difference", abs(rate / gamma - 1.0), ".0e")
    heights = doubled_damping(experiment)
    experiment.number("height-ratio", heights[1] / heights[0], ".3f")
    return experiment


if __name__ == "__main__":
    main(run)
