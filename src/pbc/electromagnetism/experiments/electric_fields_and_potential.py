"""The experiment of the lesson "Electric fields, superposition, and the potential".

The field of point charges by superposition of Coulomb's law
(``pbc.electromagnetism.fields``), checked against minus the gradient of the
potential, against the closed form of a dipole far away, and against Gauss's
law on spheres. Run it as a program to write the figures and numbers of the
page:

    uv run --locked --no-dev \\
        python -m pbc.electromagnetism.experiments.electric_fields_and_potential out
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from pbc.authoring import FIGURE_COLOURS
from pbc.electromagnetism.fields import (
    EPSILON_0,
    coulomb_field,
    coulomb_potential,
    dipole_field,
    field_from_potential,
    sphere_flux,
)
from pbc.experiment import Experiment, main
from pbc.verification.estimates import fitted_order

# region: gradient
charges = np.array([2e-9, -1e-9, 0.5e-9])  # C
positions = np.array([[0.0, 0.0, 0.0], [0.04, 0.0, 0.0], [0.0, 0.03, 0.02]])  # m
point = np.array([[0.03, 0.02, 0.01]])  # m
steps = 1e-3 / 2.0 ** np.arange(5)  # steps of the central difference, m
# endregion: gradient

# region: pair
Q = 1e-9  # C
D = 0.01  # m
pair = np.array([[0.0, 0.0, D / 2], [0.0, 0.0, -D / 2]])
signs = np.array([Q, -Q])
moment = np.array([0.0, 0.0, Q * D])
directions = np.array(
    [[1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 0.6, 0.8], [1.0, 1.0, 1.0] / np.sqrt(3)]
)
ratios = np.array([5.0, 10.0, 20.0, 40.0, 80.0])  # distance over separation
# endregion: pair

# region: gauss
gauss_charges = np.array([1e-9, 2e-9, -0.5e-9, 3e-9])  # C
gauss_positions = np.array(
    [[0.1, 0.0, 0.0], [0.0, 0.2, 0.09165], [-0.3, 0.0, 0.0], [2.0, 0.0, 0.0]]
)  # m
radii = np.array([0.05, 0.15, 0.25, 0.5, 1.0, 3.0])  # m
GAUSS_TOLERANCE = 1e-8  # a chosen tolerance, relative to the largest charge
# endregion: gauss


def relative_gap(a, b):
    return np.linalg.norm(a - b, axis=-1) / np.linalg.norm(b, axis=-1)


def gradient_run(experiment: Experiment) -> float:
    """The sum of the Coulomb fields against minus the numerical gradient of
    the potential, for each step; record the table, return the fitted order."""
    direct = coulomb_field(point, charges, positions)

    def potential(p):
        return coulomb_potential(p, charges, positions)

    gaps = np.array(
        [
            relative_gap(field_from_potential(potential, point, h), direct)[0]
            for h in steps
        ]
    )
    order = fitted_order(steps, gaps)
    assert abs(order - 2.0) < 0.05, "the central difference is not of order two"

    experiment.table(
        "gradient-run",
        [(h * 1e3, g) for h, g in zip(steps, gaps, strict=True)],
        [("step", "mm", ".4f"), ("relative difference", "", ".2e")],
        "The relative difference between minus the numerical gradient of the "
        "potential and the sum of the Coulomb fields, at one point, for each "
        "step of the central difference.",
    )
    return order


def dipole_run(experiment: Experiment) -> tuple[np.ndarray, float]:
    """The field of the pair against the field of the dipole at each distance,
    the largest gap over the directions; record the table, return the gaps and
    the fitted order in d/r."""
    gaps = np.array(
        [
            np.max(
                relative_gap(
                    coulomb_field(s * D * directions, signs, pair),
                    dipole_field(s * D * directions, moment),
                )
            )
            for s in ratios
        ]
    )
    # the order in d/r: from the largest d/r (nearest) to the smallest
    order = fitted_order(1.0 / ratios, gaps)
    assert abs(order - 2.0) < 0.05, "the gap does not fall as (d/r)^2"

    experiment.table(
        "dipole-run",
        [(s, 1.0 / s, g) for s, g in zip(ratios, gaps, strict=True)],
        [
            ("distance over separation", "", ".0f"),
            ("separation over distance", "", ".4f"),
            ("largest relative difference", "", ".2e"),
        ],
        "The largest relative difference, over four directions, between the "
        "field of a pair of opposite charges and the field of a dipole of the "
        "same moment, at each distance.",
    )
    return gaps, order


def draw_dipole_field() -> Figure:
    """The field lines and equipotentials of the pair, in a plane through
    both charges, computed by superposition."""
    span = 3.0 * D
    grid_x, grid_z = np.meshgrid(
        np.linspace(-span, span, 161), np.linspace(-span, span, 161)
    )
    plane = np.stack([grid_x, np.zeros_like(grid_x), grid_z], axis=-1)
    # a small shift keeps the grid points off the charges
    plane[..., 0] += 1e-6
    field_plane = coulomb_field(plane, signs, pair)
    potential_plane = coulomb_potential(plane, signs, pair)
    fig, ax = plt.subplots(figsize=(5.6, 5.6))
    ax.streamplot(
        grid_x * 100,
        grid_z * 100,
        field_plane[..., 0],
        field_plane[..., 2],
        color=FIGURE_COLOURS[0],
        density=1.2,
        linewidth=0.8,
        arrowsize=0.8,
    )
    levels = np.sort(
        np.concatenate([-np.geomspace(50, 3000, 7), np.geomspace(50, 3000, 7)])
    )
    ax.contour(
        grid_x * 100,
        grid_z * 100,
        potential_plane,
        levels=levels,
        colors=FIGURE_COLOURS[2],
        linewidths=0.6,
        linestyles="-",
    )
    ax.plot([0.0], [D / 2 * 100], "o", color=FIGURE_COLOURS[1], markersize=8)
    ax.plot([0.0], [-D / 2 * 100], "s", color=FIGURE_COLOURS[0], markersize=8)
    ax.text(0.15, D / 2 * 100 + 0.15, "+q")
    ax.text(0.15, -D / 2 * 100 - 0.35, "\N{MINUS SIGN}q")
    ax.set_aspect("equal")
    ax.set_xlabel("x (cm)")
    ax.set_ylabel("z (cm)")
    return fig


def gauss_run(experiment: Experiment) -> None:
    """The flux out through spheres about the origin against the charge
    inside each; record the table."""
    distances = np.linalg.norm(gauss_positions, axis=1)

    def field(p):
        return coulomb_field(p, gauss_charges, gauss_positions)

    rows = []
    worst = 0.0
    for radius in radii:
        inside = float(gauss_charges[distances < radius].sum())
        found = sphere_flux(field, radius=radius, nodes=64) * EPSILON_0
        worst = max(worst, abs(found - inside) / np.max(np.abs(gauss_charges)))
        rows.append((radius, inside * 1e9, found * 1e9))
    assert worst < GAUSS_TOLERANCE, "the flux does not count the charge inside"

    experiment.table(
        "gauss-run",
        rows,
        [
            ("radius", "m", ".2f"),
            ("charge inside", "nC", ".4f"),
            ("flux times the permittivity", "nC", ".4f"),
        ],
        "The flux of the field of four charges out through a sphere about the "
        "origin, times the vacuum permittivity, against the charge inside the "
        "sphere, for each radius, to four decimals.",
    )


def axis_and_across() -> tuple[float, float]:
    """Exercise 1: the strength of the field of the pair at 0.5 m on its axis
    and on the plane midway between the charges."""
    on_axis = np.linalg.norm(coulomb_field([[0.0, 0.0, 0.5]], signs, pair))
    across = np.linalg.norm(coulomb_field([[0.5, 0.0, 0.0]], signs, pair))
    return float(on_axis), float(across)


def where_the_field_vanishes() -> tuple[float, float]:
    """Exercise 2: the point between +4 nC and +1 nC, 0.3 m apart, where the
    field computed along the line changes sign, and the point of equal
    strength."""
    line = np.stack(
        [np.linspace(0.01, 0.29, 28_001), np.zeros(28_001), np.zeros(28_001)], axis=1
    )
    along = coulomb_field(line, [4e-9, 1e-9], [[0, 0, 0], [0.3, 0, 0]])[:, 0]
    zero_at = line[np.argmin(np.abs(along)), 0]
    balance = 0.3 * 2.0 / 3.0
    return float(zero_at), balance


def near_the_sphere(experiment: Experiment) -> list[float]:
    """Exercise 3: the flux through the unit sphere of a charge at 0.99 m,
    for each number of nodes; record the table."""
    near = [[0.99, 0.0, 0.0]]

    def near_field(p):
        return coulomb_field(p, [1e-9], near)

    node_counts = [16, 64, 200, 400, 800]
    near_flux = [
        sphere_flux(near_field, radius=1.0, nodes=n) * EPSILON_0 / 1e-9
        for n in node_counts
    ]
    experiment.table(
        "near-flux",
        list(zip(node_counts, near_flux, strict=True)),
        [
            ("nodes in the polar angle", "", "d"),
            ("flux over the charge over the permittivity", "", ".6f"),
        ],
        "The flux through the unit sphere of a charge just inside it, as a "
        "fraction of the charge over the vacuum permittivity, for each number "
        "of nodes of the quadrature, to six decimals.",
    )
    return near_flux


def run() -> Experiment:
    """Everything the lesson's page shows."""
    experiment = Experiment()

    experiment.number("gradient-order", gradient_run(experiment), ".3f")

    dipole_gaps, dipole_order = dipole_run(experiment)
    experiment.number("dipole-order", dipole_order, ".3f")
    experiment.number("gap-near", dipole_gaps[0] * 100, ".1f")
    experiment.number("gap-far", dipole_gaps[-1] * 100, ".4f")
    experiment.figure("fig-dipole-field", draw_dipole_field)

    gauss_run(experiment)
    experiment.number("gauss-tolerance", GAUSS_TOLERANCE, ".0e")

    on_axis, across = axis_and_across()
    experiment.number("on-axis", on_axis, ".4f")
    experiment.number("across", across, ".4f")
    experiment.number("axis-ratio", on_axis / across, ".4f")

    zero_at, balance = where_the_field_vanishes()
    experiment.number("zero-at", zero_at, ".4f")
    experiment.number("balance", balance, ".4f")

    near_flux = near_the_sphere(experiment)
    experiment.number("near-first", near_flux[0], ".4f")
    experiment.number("near-last", near_flux[-1], ".6f")
    return experiment


if __name__ == "__main__":
    main(run)
