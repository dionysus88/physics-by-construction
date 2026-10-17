"""The experiment of the lesson "The chirp law, proved".

The identities of the Lean theorems about the chirp of two orbiting bodies,
evaluated with the functions of the gravitational-wave lab
(``pbc.mechanics.chirp``), and the countdown to coalescence they imply. The
theorems themselves are checked by the Lean build,
``./scripts/check-lean.sh``. Run it as a program to write the figure and
numbers of the page:

    uv run --locked --no-dev python -m pbc.mechanics.experiments.chirp_law_proved out
"""

from functools import partial

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from pbc.experiment import Experiment, main
from pbc.mechanics import chirp

# region: example
m1, m2, f0 = 36.0, 29.0, 35.0  # solar masses, Hz: the example of the lab
mc = chirp.chirp_mass(m1, m2)
# endregion: example


def identities(experiment: Experiment) -> None:
    """The three identities of the theorems at the start of the example;
    record the table."""
    omega = np.pi * f0
    omega_dot = np.pi * float(chirp.chirp_rate(f0, mc))
    gmc = mc * chirp.GM_SUN_OVER_C3  # G Mc / c^3, in seconds

    cube_lhs = omega_dot**3
    cube_rhs = (96 / 5) ** 3 * gmc**5 * omega**11
    mc_back = float(chirp.chirp_mass_from_rate(f0, omega_dot / np.pi))
    tau_countdown = 3 * omega / (8 * omega_dot)
    tau_lab = chirp.time_to_coalescence(f0, mc)

    experiment.table(
        "identities",
        [
            (
                "(omega')^3 against (96/5)^3 (G Mc/c^3)^5 omega^11",
                cube_lhs / cube_rhs - 1,
            ),
            ("chirp mass from the rate against the chirp mass", mc_back / mc - 1),
            (
                "3 omega / (8 omega') against the time to coalescence",
                tau_countdown / tau_lab - 1,
            ),
        ],
        [("identity of the theorems", "", ""), ("relative difference", "", ".1e")],
        "The identities of the theorems, evaluated with the functions of the lab.",
    )


def energy_balance():
    """The rate of change of the orbit's energy from the shrink rate of the
    program, over minus the radiated power."""
    a = float(chirp.separation_from_frequency(f0, m1 + m2))
    m1_kg, m2_kg = m1 * chirp.M_SUN, m2 * chirp.M_SUN

    def orbit_energy(separation):
        return -chirp.G * m1_kg * m2_kg / (2 * separation)

    power = (
        32
        / 5
        * chirp.G**4
        * m1_kg**2
        * m2_kg**2
        * (m1_kg + m2_kg)
        / (chirp.C**5 * a**5)
    )
    da_dt = float(chirp.shrink_rate(a, m1, m2))
    h = 1e-3 * a
    d_energy = (orbit_energy(a + h) - orbit_energy(a - h)) / (2 * h) * da_dt
    ratio = -d_energy / power
    print(
        "d(energy)/dt over minus the power, from the shrink rate of the program:"
        f" {ratio:.6f}"
    )


def countdown():
    """The countdown 3 omega / (8 omega') along the integrated inspiral, and
    its slope against time."""
    tau0 = chirp.time_to_coalescence(f0, mc)
    times = np.linspace(0.0, 0.9 * tau0, 300)
    _, f_num = chirp.inspiral_frequency(times, m1, m2, f0)
    left = 3 * f_num / (8 * chirp.chirp_rate(f_num, mc))
    slope = np.polyfit(times, left, 1)[0]
    return tau0, times, left, slope


def draw_countdown(tau0, times, left) -> Figure:
    """The time left and the countdown against time."""
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.plot(times, tau0 - times, color="#93003a", label="time left")
    ax.plot(times, left, color="#00429d", linestyle="--", label="3 omega / (8 omega')")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("seconds")
    ax.legend()
    return fig


def exponent_of_the_rate():
    """Exercise 1."""
    print("the exponent of a in the rate is that of the power, plus two")


def exponent_of_the_countdown():
    """Exercise 2."""
    print(f"3/8 * (1 - 11/3) = {3 / 8 * (1 - 11 / 3):.1f}")


def run() -> Experiment:
    """Everything the lesson's page shows."""
    experiment = Experiment()
    identities(experiment)
    with experiment.capture("energy-balance"):
        energy_balance()
    tau0, times, left, slope = countdown()
    experiment.figure("fig-countdown", partial(draw_countdown, tau0, times, left))
    experiment.number("slope", slope, ".4f")
    with experiment.capture("exponent-of-the-rate"):
        exponent_of_the_rate()
    with experiment.capture("exponent-of-the-countdown"):
        exponent_of_the_countdown()
    return experiment


if __name__ == "__main__":
    main(run)
