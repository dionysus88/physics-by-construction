"""The electric field of point charges: Coulomb's law, superposition, the
potential, the dipole, and the flux through a sphere.

A point is an array whose last axis has three components, x, y, z in m;
any leading axes are kept, so a grid of points gives a grid of fields.
Charges are in C, fields in V/m, potentials in V, dipole moments in C m.
The field of several charges is the sum of the fields of each: nothing
here uses the closed form of the dipole or Gauss's law to compute a field;
those are in this module to be compared with.
"""

from collections.abc import Callable

import numpy as np
from numpy.typing import ArrayLike, NDArray

Array = NDArray[np.float64]
VectorField = Callable[[Array], Array]
ScalarField = Callable[[Array], Array]

__all__ = [
    "COULOMB_CONSTANT",
    "ELEMENTARY_CHARGE",
    "EPSILON_0",
    "coulomb_field",
    "coulomb_potential",
    "dipole_field",
    "dipole_potential",
    "field_from_potential",
    "sphere_flux",
]

EPSILON_0 = 8.8541878128e-12  # vacuum permittivity, F/m (CODATA 2018)
COULOMB_CONSTANT = 1.0 / (4.0 * np.pi * EPSILON_0)  # N m^2 / C^2
ELEMENTARY_CHARGE = 1.602176634e-19  # C, exact in the SI


def _separations(
    points: ArrayLike, charges: ArrayLike, positions: ArrayLike
) -> tuple[Array, Array, Array]:
    points = np.asarray(points, dtype=float)
    charges = np.atleast_1d(np.asarray(charges, dtype=float))
    positions = np.atleast_2d(np.asarray(positions, dtype=float))
    if points.shape[-1] != 3 or positions.shape != (charges.size, 3):
        raise ValueError("need points (..., 3) and one position (3,) per charge")
    r = points[..., None, :] - positions  # (..., charges, 3)
    distance = np.linalg.norm(r, axis=-1)  # (..., charges)
    if np.any(distance == 0.0):
        raise ValueError("the field of a point charge is not defined at the charge")
    return charges, r, distance


def coulomb_field(points: ArrayLike, charges: ArrayLike, positions: ArrayLike) -> Array:
    """The electric field at ``points`` of the point ``charges`` (C) at
    ``positions`` (m), by superposition of Coulomb's law:
    E = k sum_i q_i (r - r_i) / |r - r_i|^3, in V/m."""
    charges, r, distance = _separations(points, charges, positions)
    return COULOMB_CONSTANT * np.sum((charges / distance**3)[..., None] * r, axis=-2)


def coulomb_potential(
    points: ArrayLike, charges: ArrayLike, positions: ArrayLike
) -> Array:
    """The potential at ``points`` of the point ``charges`` at ``positions``,
    zero far away: V = k sum_i q_i / |r - r_i|, in V."""
    charges, _, distance = _separations(points, charges, positions)
    return COULOMB_CONSTANT * np.sum(charges / distance, axis=-1)


def field_from_potential(potential: ScalarField, points: ArrayLike, h: float) -> Array:
    """Minus the gradient of ``potential`` at ``points``, by central
    differences of step ``h`` (m) along each axis. The error of a central
    difference falls as h^2 while h is large against the round-off."""
    if h <= 0:
        raise ValueError(f"the step must be positive, got {h}")
    points = np.asarray(points, dtype=float)
    gradient = np.empty_like(points)
    for axis in range(3):
        step = np.zeros(3)
        step[axis] = h
        gradient[..., axis] = (potential(points + step) - potential(points - step)) / (
            2.0 * h
        )
    return -gradient


def dipole_field(points: ArrayLike, moment: ArrayLike) -> Array:
    """The field of an ideal dipole of ``moment`` p (C m) at the origin:
    E = k (3 (p . n) n - p) / r^3, with n the unit vector towards the
    point. A pair of charges +q and -q a distance d apart has p = q d and
    this field only far from the pair."""
    points = np.asarray(points, dtype=float)
    p = np.asarray(moment, dtype=float)
    r = np.linalg.norm(points, axis=-1, keepdims=True)
    if np.any(r == 0.0):
        raise ValueError("the field of a dipole is not defined at the dipole")
    n = points / r
    return (
        COULOMB_CONSTANT * (3.0 * np.sum(p * n, axis=-1, keepdims=True) * n - p) / r**3
    )


def dipole_potential(points: ArrayLike, moment: ArrayLike) -> Array:
    """The potential of an ideal dipole at the origin, V = k p . n / r^2."""
    points = np.asarray(points, dtype=float)
    r = np.linalg.norm(points, axis=-1)
    if np.any(r == 0.0):
        raise ValueError("the potential of a dipole is not defined at the dipole")
    return COULOMB_CONSTANT * (points @ np.asarray(moment, dtype=float)) / r**3


def sphere_flux(
    field: VectorField,
    *,
    radius: float,
    centre: ArrayLike = (0.0, 0.0, 0.0),
    nodes: int = 48,
) -> float:
    """The flux of ``field`` out through a sphere of ``radius`` (m) about
    ``centre``, in V m for an electric field.

    The surface integral is a product rule: Gauss-Legendre with ``nodes``
    points in cos(theta) and the trapezoidal rule, exact for a periodic
    function of its degree, with twice as many points in phi. A charge close
    to the sphere makes the integrand sharp and needs more nodes.
    """
    if radius <= 0 or nodes < 1:
        raise ValueError("need a positive radius and at least one node")
    mu, weight_mu = np.polynomial.legendre.leggauss(nodes)
    phi = np.arange(2 * nodes) * (np.pi / nodes)
    sin_theta = np.sqrt(1.0 - mu**2)
    normal = np.stack(
        [
            sin_theta[:, None] * np.cos(phi)[None, :],
            sin_theta[:, None] * np.sin(phi)[None, :],
            np.broadcast_to(mu[:, None], (nodes, 2 * nodes)),
        ],
        axis=-1,
    )
    points = np.asarray(centre, dtype=float) + radius * normal
    outward = np.sum(field(points) * normal, axis=-1)
    weights = weight_mu[:, None] * (np.pi / nodes) * radius**2
    return float(np.sum(weights * outward))
