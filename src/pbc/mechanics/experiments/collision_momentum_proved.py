"""The experiment of the lesson "Momentum in a collision, proved".

The numbers behind the Lean theorem that the collision rule keeps the total
momentum: the change of the momentum in random collisions
(``pbc.mechanics.particles``), and a rule with the wrong coefficients. The
theorem itself is checked by the Lean build, ``./scripts/check-lean.sh``.
Run it as a program to write the figure and numbers of the page:

    uv run --locked --no-dev \\
        python -m pbc.mechanics.experiments.collision_momentum_proved out
"""

from functools import partial

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from pbc.experiment import Experiment, main
from pbc.mechanics.particles import hard_sphere_collision

# region: example
m1, m2 = 1.0, 3.0  # kg
v1 = np.array([2.0, 0.5, 0.0])
v2 = np.array([-1.0, 0.0, 0.5])
n = np.array([1.0, 0.0, 0.0])
# endregion: example


def random_collisions(experiment: Experiment):
    """The change of the total momentum in six random collisions; record the
    table and return the generator, which the figure draws on."""
    rng = np.random.default_rng(7)
    rows = []
    for _sample in range(6):
        mass_1, mass_2 = rng.uniform(0.1, 10.0, size=2)
        velocity_1, velocity_2 = rng.normal(size=(2, 3))
        normal = rng.normal(size=3)
        normal /= np.linalg.norm(normal)
        w1, w2 = hard_sphere_collision(mass_1, velocity_1, mass_2, velocity_2, normal)
        before = mass_1 * velocity_1 + mass_2 * velocity_2
        after = mass_1 * w1 + mass_2 * w2
        rows.append(
            (mass_1, mass_2, np.max(np.abs(after - before)), np.linalg.norm(before))
        )

    experiment.table(
        "random-collisions",
        rows,
        [
            ("m1", "kg", ".2f"),
            ("m2", "kg", ".2f"),
            ("largest change of a momentum component", "kg m/s", ".1e"),
            ("size of the total momentum", "kg m/s", ".2f"),
        ],
        "The change of the total momentum in a collision, for six random draws.",
    )
    return rng


def momentum_residuals(rng):
    """The relative change of the momentum in two thousand collisions over
    six decades of the mass ratio, drawn from ``rng``."""
    ratio, change = [], []
    for _ in range(2000):
        mass_1, mass_2 = 10 ** rng.uniform(-3, 3, size=2)
        velocity_1, velocity_2 = rng.normal(size=(2, 3))
        normal = rng.normal(size=3)
        normal /= np.linalg.norm(normal)
        w1, w2 = hard_sphere_collision(mass_1, velocity_1, mass_2, velocity_2, normal)
        before = mass_1 * velocity_1 + mass_2 * velocity_2
        ratio.append(mass_1 / mass_2)
        change.append(
            np.linalg.norm(mass_1 * w1 + mass_2 * w2 - before) / np.linalg.norm(before)
        )
    return ratio, change


def draw_momentum_residual(ratio, change) -> Figure:
    """The relative change of the momentum against the mass ratio."""
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.loglog(ratio, np.maximum(change, 1e-18), ".", color="#00429d", markersize=3)
    ax.set_xlabel("mass ratio m1 / m2")
    ax.set_ylabel("relative change of the momentum")
    return fig


def two_rules(experiment: Experiment):
    """Exercise 1: the change of the momentum with equal coefficients and
    with the rule of the momentum lesson; record the table and return the
    velocities after the right rule."""
    approach = (v1 - v2) @ n

    wrong = (v1 - approach * n, v2 + approach * n)  # coefficient 1 for any masses
    right = hard_sphere_collision(m1, v1, m2, v2, n)
    before = m1 * v1 + m2 * v2

    rule_rows = [
        ("rule with equal coefficients", *(m1 * wrong[0] + m2 * wrong[1] - before)),
        ("rule of the momentum lesson", *(m1 * right[0] + m2 * right[1] - before)),
    ]
    experiment.table(
        "two-rules",
        rule_rows,
        [
            ("rule", "", ""),
            ("x", "kg m/s", ".1e"),
            ("y", "kg m/s", ".1e"),
            ("z", "kg m/s", ".1e"),
        ],
        "The change of the total momentum along each axis, for two rules.",
    )
    return right


def total_mass():
    """Exercise 2: the total mass the rule divides by."""
    total = m1 + m2
    print(f"the rule divides by m1 + m2 = {total:.1f} kg for the example masses")


def centre_of_mass_velocity(right):
    """Exercise 3: the change of the velocity of the centre of mass."""
    w1, w2 = right
    centre_before = (m1 * v1 + m2 * v2) / (m1 + m2)
    centre_after = (m1 * w1 + m2 * w2) / (m1 + m2)
    print(
        "largest change of the centre-of-mass velocity: "
        f"{np.max(np.abs(centre_after - centre_before)):.1e} m/s"
    )


def run() -> Experiment:
    """Everything the lesson's page shows."""
    experiment = Experiment()
    rng = random_collisions(experiment)
    ratio, change = momentum_residuals(rng)
    experiment.figure(
        "fig-momentum-residual", partial(draw_momentum_residual, ratio, change)
    )
    right = two_rules(experiment)
    with experiment.capture("total-mass"):
        total_mass()
    with experiment.capture("centre-of-mass-velocity"):
        centre_of_mass_velocity(right)
    return experiment


if __name__ == "__main__":
    main(run)
