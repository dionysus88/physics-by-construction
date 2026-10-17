"""Magnetic flux through a loop and the electromotive force around it.

The two sides of Faraday's law are computed apart. The flux is a surface
integral of B over the flat rectangle the loop bounds; the electromotive
force (EMF) is a line integral, around the edge, of the force per unit
charge on a charge carried by the wire, E + u x B with u the velocity of
the wire. Neither uses the other, and -dPhi/dt is a central difference of
the flux in time. A point is an array whose last axis has three components
(m), B is in T, E in V/m, the flux in Wb and the EMF in V.
"""

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray

Array = NDArray[np.float64]
VectorField = Callable[[Array], Array]

__all__ = [
    "Rectangle",
    "emf",
    "flux",
    "flux_rate",
    "flux_tube_fields",
    "rotating_coil",
]


@dataclass(frozen=True)
class Rectangle:
    """A flat rectangular loop: the corner ``corner`` and the sides
    ``side_a`` and ``side_b`` (m), at right angles. The loop runs from the
    corner along ``side_a`` first, which makes it counterclockwise about
    the normal side_a x side_b: the sense of the EMF that Faraday's law
    pairs with the flux through the normal."""

    corner: Array
    side_a: Array
    side_b: Array

    def __post_init__(self) -> None:
        for name in ("corner", "side_a", "side_b"):
            object.__setattr__(self, name, np.asarray(getattr(self, name), dtype=float))
        if abs(self.side_a @ self.side_b) > 1e-12 * (
            np.linalg.norm(self.side_a) * np.linalg.norm(self.side_b)
        ):
            raise ValueError("the sides of a rectangle are at right angles")

    @property
    def area(self) -> float:
        return float(np.linalg.norm(np.cross(self.side_a, self.side_b)))

    @property
    def normal(self) -> Array:
        cross = np.cross(self.side_a, self.side_b)
        return cross / np.linalg.norm(cross)

    def surface(self, nodes: int) -> tuple[Array, Array]:
        """Gauss-Legendre points (nodes^2, 3) on the rectangle and their
        weights (m^2), which sum to the area."""
        s, w = np.polynomial.legendre.leggauss(nodes)
        s, w = 0.5 * (s + 1.0), 0.5 * w
        a, b = np.meshgrid(s, s, indexing="ij")
        points = (
            self.corner
            + a.reshape(-1, 1) * self.side_a
            + b.reshape(-1, 1) * self.side_b
        )
        return points, np.outer(w, w).reshape(-1) * self.area

    def edge(self, nodes: int) -> tuple[Array, Array]:
        """Gauss-Legendre points (4 nodes, 3) on the four sides, in the
        sense of the loop, and the element dl (4 nodes, 3) of each: the
        weight times the side."""
        s, w = np.polynomial.legendre.leggauss(nodes)
        s, w = 0.5 * (s + 1.0), 0.5 * w
        starts = [
            self.corner,
            self.corner + self.side_a,
            self.corner + self.side_a + self.side_b,
            self.corner + self.side_b,
        ]
        sides = [self.side_a, self.side_b, -self.side_a, -self.side_b]
        points = np.concatenate(
            [
                start + s[:, None] * side
                for start, side in zip(starts, sides, strict=True)
            ]
        )
        elements = np.concatenate([w[:, None] * side for side in sides])
        return points, elements


def flux(magnetic: VectorField, loop: Rectangle, *, nodes: int = 24) -> float:
    """The flux of ``magnetic`` (a function of the points) through ``loop``
    along its normal, by Gauss-Legendre in both directions: in Wb."""
    points, weights = loop.surface(nodes)
    return float(np.sum(weights * (magnetic(points) @ loop.normal)))


def emf(
    loop: Rectangle,
    *,
    electric: VectorField | None = None,
    magnetic: VectorField | None = None,
    velocity: VectorField | None = None,
    nodes: int = 24,
) -> float:
    """The EMF around ``loop`` in its sense, in V: the line integral of the
    force per unit charge E + u x B on a charge carried by the wire, where
    ``velocity`` gives the velocity u (m/s) of the wire at each of its
    points. A field that is not given is zero; a wire at rest feels only E.
    """
    points, elements = loop.edge(nodes)
    force = np.zeros_like(points)
    if electric is not None:
        force += electric(points)
    if magnetic is not None and velocity is not None:
        force += np.cross(velocity(points), magnetic(points))
    return float(np.sum(force * elements))


def flux_rate(flux_at: Callable[[float], float], t: float, h: float) -> float:
    """dPhi/dt at the time ``t`` by the central difference of step ``h``
    (s): (Phi(t + h) - Phi(t - h)) / (2 h), with an error of order h^2."""
    if h <= 0:
        raise ValueError(f"the step must be positive, got {h}")
    return (flux_at(t + h) - flux_at(t - h)) / (2.0 * h)


def flux_tube_fields(
    points: ArrayLike, *, strength: float, rate: float, width: float
) -> tuple[Array, Array]:
    """The induced electric field and the magnetic field (E, B) of a tube of
    flux along z: B = B0 exp(-r^2 / a^2) z, with B0 = ``strength`` (T)
    changing at ``rate`` (T/s) and a = ``width`` (m).

    Both come from the vector potential A = B0 a^2 (1 - exp(-r^2/a^2)) /
    (2 r) along phi: B = curl A, and the induced field E = -dA/dt, which
    is -rate a^2 (1 - exp(-r^2/a^2)) / (2 r) along phi. Neither uses
    Faraday's law.
    """
    points = np.asarray(points, dtype=float)
    x, y = points[..., 0], points[..., 1]
    r2 = x**2 + y**2
    profile = np.exp(-r2 / width**2)
    # (1 - exp(-r^2/a^2)) / r^2, which tends to 1/a^2 on the axis
    safe = np.where(r2 > 0.0, r2, 1.0)
    ratio = np.where(r2 > 0.0, -np.expm1(-r2 / width**2) / safe, 1.0 / width**2)
    # E_phi phi = E_phi / r (-y, x, 0)
    e_over_r = -0.5 * rate * width**2 * ratio
    electric = np.stack([-e_over_r * y, e_over_r * x, np.zeros_like(x)], axis=-1)
    magnetic = np.stack(
        [np.zeros_like(x), np.zeros_like(x), strength * profile], axis=-1
    )
    return electric, magnetic


def rotating_coil(
    t: float, *, angular_velocity: float, width: float, height: float
) -> Rectangle:
    """A coil of ``width`` by ``height`` (m) turning about the z axis
    through its centre at ``angular_velocity`` (rad/s): its normal is
    (cos wt, sin wt, 0), along x at the time zero."""
    angle = angular_velocity * t
    across = width * np.array([-np.sin(angle), np.cos(angle), 0.0])
    up = np.array([0.0, 0.0, height])
    return Rectangle(corner=-0.5 * (across + up), side_a=across, side_b=up)
