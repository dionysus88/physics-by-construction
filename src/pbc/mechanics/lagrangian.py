"""Lagrangian mechanics: the equations of motion from one function.

A system with generalised coordinates ``q`` (angles, lengths, displacements,
whatever describes the configuration without the constraints) has a
Lagrangian L(q, q̇) = T - U, the kinetic minus the potential energy. The
Euler-Lagrange equations

    d/dt (∂L/∂q̇_i) = ∂L/∂q_i

are the equations of motion, and they give Newton's second law for a particle
in Cartesian coordinates and the right equations in any other coordinates,
with the forces of constraint absent. Expanding the time derivative gives a
linear system for the accelerations,

    (∂²L/∂q̇∂q̇) q̈ = ∂L/∂q - (∂²L/∂q̇∂q) q̇,

which ``euler_lagrange`` solves, with the derivatives of L taken by central
differences, so that a lesson can write down a Lagrangian and simulate it
without deriving anything by hand. The result plugs into the steppers of
``pbc.mechanics.integrators`` as an acceleration, with the generalised
coordinates as the position and their rates as the velocity.

Quantities are in SI units; with an angle as coordinate the "velocity" is in
rad/s. A Lagrangian here is a function ``L(q, qdot)`` of two vectors that
returns joules.
"""

from collections.abc import Callable

import numpy as np
from numpy.typing import NDArray
from scipy.constants import g as STANDARD_GRAVITY  # 9.80665 m/s²

from pbc.mechanics.dynamics import Acceleration, Vector

# L(q, qdot) in J for the coordinates q and their rates qdot.
type Lagrangian = Callable[[Vector, Vector], float]

# The step of the central differences, in the units of the coordinates: a
# compromise between the truncation error of a second difference (it falls
# as the square of the step) and its round-off (it grows as the inverse
# square). Near this value the accelerations of the double pendulum agree
# with the closed form to a relative 1e-6.
DIFFERENCE_STEP = 1e-3


def _unit(n: int, i: int) -> Vector:
    e = np.zeros(n)
    e[i] = 1.0
    return e


def _derivatives(
    lagrangian: Lagrangian, q: Vector, qdot: Vector, h: float
) -> tuple[Vector, Vector, NDArray[np.float64], NDArray[np.float64]]:
    """∂L/∂q, ∂L/∂q̇, ∂²L/∂q̇∂q̇, and ∂²L/∂q̇∂q by central differences."""
    n = len(q)
    dq = np.array([_unit(n, i) * h for i in range(n)])
    force = np.array(
        [
            (lagrangian(q + dq[i], qdot) - lagrangian(q - dq[i], qdot)) / (2 * h)
            for i in range(n)
        ]
    )
    momentum = np.array(
        [
            (lagrangian(q, qdot + dq[i]) - lagrangian(q, qdot - dq[i])) / (2 * h)
            for i in range(n)
        ]
    )
    mass = np.empty((n, n))
    mixed = np.empty((n, n))
    for i in range(n):
        for j in range(n):
            mass[i, j] = (
                lagrangian(q, qdot + dq[i] + dq[j])
                - lagrangian(q, qdot + dq[i] - dq[j])
                - lagrangian(q, qdot - dq[i] + dq[j])
                + lagrangian(q, qdot - dq[i] - dq[j])
            ) / (4 * h * h)
            mixed[i, j] = (
                lagrangian(q + dq[j], qdot + dq[i])
                - lagrangian(q - dq[j], qdot + dq[i])
                - lagrangian(q + dq[j], qdot - dq[i])
                + lagrangian(q - dq[j], qdot - dq[i])
            ) / (4 * h * h)
    return force, momentum, mass, mixed


def euler_lagrange(lagrangian: Lagrangian, h: float = DIFFERENCE_STEP) -> Acceleration:
    """The accelerations a(t, q, qdot) that the Euler-Lagrange equations of
    ``lagrangian`` give, as an acceleration for the steppers.

    ``h`` is the step of the central differences, in the units of the
    coordinates. The Lagrangian must be quadratic enough that the matrix of
    its second derivatives in the rates is invertible (the mass matrix).
    """

    def acceleration(t: float, q: Vector, qdot: Vector) -> Vector:
        force, _, mass, mixed = _derivatives(lagrangian, q, qdot, h)
        return np.linalg.solve(mass, force - mixed @ qdot)

    return acceleration


def generalised_momentum(
    lagrangian: Lagrangian, q: Vector, qdot: Vector, h: float = DIFFERENCE_STEP
) -> Vector:
    """The momenta p = ∂L/∂q̇ conjugate to the coordinates ``q``.

    For a Cartesian coordinate it is the momentum m v; for an angle it is the
    angular momentum. A coordinate that L does not contain (a cyclic one) has
    a momentum that the motion keeps constant.
    """
    n = len(q)
    return np.array(
        [
            (
                lagrangian(q, qdot + _unit(n, i) * h)
                - lagrangian(q, qdot - _unit(n, i) * h)
            )
            / (2 * h)
            for i in range(n)
        ]
    )


def energy_function(
    lagrangian: Lagrangian, q: Vector, qdot: Vector, h: float = DIFFERENCE_STEP
) -> float:
    """The energy E = p·q̇ - L in J that a time-independent Lagrangian
    conserves; it is the kinetic plus the potential energy when L = T - U and
    T is quadratic in the rates."""
    return float(
        generalised_momentum(lagrangian, q, qdot, h) @ qdot - lagrangian(q, qdot)
    )


def pendulum_lagrangian(
    mass: float, length: float, g: float = STANDARD_GRAVITY
) -> Lagrangian:
    """The Lagrangian of a pendulum, with the angle θ from the downward
    vertical as the only coordinate: the rod's constraint is built in, and its
    tension appears nowhere."""

    def lagrangian(q: Vector, qdot: Vector) -> float:
        return float(
            0.5 * mass * length**2 * qdot[0] ** 2 + mass * g * length * np.cos(q[0])
        )

    return lagrangian


def coupled_springs_lagrangian(mass: float, k: float, coupling: float) -> Lagrangian:
    """The Lagrangian of two equal masses (kg) between two walls, each held
    by a spring ``k`` (N/m) and joined to the other by a spring ``coupling``
    (N/m); the coordinates are the two displacements from rest."""

    def lagrangian(q: Vector, qdot: Vector) -> float:
        kinetic = 0.5 * mass * float(qdot @ qdot)
        potential = 0.5 * k * float(q @ q) + 0.5 * coupling * float((q[0] - q[1]) ** 2)
        return kinetic - potential

    return lagrangian


def double_pendulum_lagrangian(
    m1: float, m2: float, l1: float, l2: float, g: float = STANDARD_GRAVITY
) -> Lagrangian:
    """The Lagrangian of the double pendulum, with the two rod angles from the
    downward vertical as coordinates.

    It is written from the Cartesian positions of the two bobs, and their
    velocities follow from the chain rule, so nothing is derived by hand.
    """

    def lagrangian(q: Vector, qdot: Vector) -> float:
        vx1 = l1 * np.cos(q[0]) * qdot[0]
        vy1 = l1 * np.sin(q[0]) * qdot[0]
        vx2 = vx1 + l2 * np.cos(q[1]) * qdot[1]
        vy2 = vy1 + l2 * np.sin(q[1]) * qdot[1]
        kinetic = 0.5 * m1 * (vx1**2 + vy1**2) + 0.5 * m2 * (vx2**2 + vy2**2)
        height1 = -l1 * np.cos(q[0])
        height2 = height1 - l2 * np.cos(q[1])
        return float(kinetic - m1 * g * height1 - m2 * g * height2)

    return lagrangian
