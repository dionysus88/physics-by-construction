"""Hamiltonian mechanics: phase space, the Legendre transform, and what a
symplectic step preserves.

From a Lagrangian L(q, q̇) the momenta p = ∂L/∂q̇ and the energy
H = p·q̇ - L, written as a function of (q, p), give Hamilton's equations
q̇ = ∂H/∂p, ṗ = -∂H/∂q. The flow of these equations preserves the area of
any region of phase space (Liouville's theorem), and a symplectic method
preserves the area of the map from one step to the next exactly, whatever
the step. That is the reason such a method has a modified energy that it
conserves, as the lessons on numerical integrators and on symplectic Euler
show for the oscillator; here the same is measured for a general potential.

Quantities are in SI units as in ``pbc.mechanics.dynamics``. Phase space is
the plane of a position and its velocity for a unit mass matrix, or of the
position and the momentum; the determinant of a step is the same in both.
"""

from collections.abc import Callable

import numpy as np
from numpy.typing import NDArray

from pbc.mechanics.dynamics import Acceleration, State, Stepper, Trajectory, Vector
from pbc.mechanics.energy import Potential, mechanical_energy
from pbc.mechanics.lagrangian import (
    DIFFERENCE_STEP,
    Lagrangian,
    _derivatives,
    generalised_momentum,
)

# H(q, p) in J for the coordinates q and the momenta p.
type Hamiltonian = Callable[[Vector, Vector], float]


def legendre_hamiltonian(
    lagrangian: Lagrangian, h: float = DIFFERENCE_STEP
) -> Hamiltonian:
    """The Hamiltonian H(q, p) = p·q̇ - L of a ``lagrangian`` that is
    quadratic in the rates q̇ (as T - U is), by the Legendre transform.

    The momentum is p = W q̇ + p₀ with the mass matrix W and the momentum p₀
    at q̇ = 0 (zero for L = T - U); the transform solves it for q̇.
    """

    def hamiltonian(q: Vector, p: Vector) -> float:
        zero = np.zeros_like(q)
        _, _, mass, _ = _derivatives(lagrangian, q, zero, h)
        p0 = generalised_momentum(lagrangian, q, zero, h)
        qdot = np.linalg.solve(mass, p - p0)
        return float(p @ qdot - lagrangian(q, qdot))

    return hamiltonian


def step_jacobian(
    step: Stepper,
    state: State,
    acceleration: Acceleration,
    dt: float,
    h: float = 1e-6,
) -> NDArray[np.float64]:
    """The Jacobian matrix of one step of ``step`` of length ``dt`` (s), as a
    map from (x, v) at the start to (x, v) at the end, by central differences
    of size ``h`` at ``state``.

    Its determinant is the factor by which the step scales the area of a
    small region of phase space: one for the exact flow of a Hamiltonian
    system and for a symplectic method, and not one for the others.
    """
    n = len(state.x)
    z = np.concatenate([state.x, state.v])

    def advance(vector: Vector) -> Vector:
        end = step(State(state.t, vector[:n], vector[n:]), acceleration, dt)
        return np.concatenate([end.x, end.v])

    jacobian = np.empty((2 * n, 2 * n))
    for j in range(2 * n):
        e = np.zeros(2 * n)
        e[j] = h
        jacobian[:, j] = (advance(z + e) - advance(z - e)) / (2 * h)
    return jacobian


def loop_area(x: NDArray[np.float64], v: NDArray[np.float64]) -> float:
    """The area enclosed by the closed polygon through the points (x, v), by
    the shoelace formula, as a positive number. One degree of freedom."""
    return float(0.5 * abs(np.dot(x, np.roll(v, -1)) - np.dot(v, np.roll(x, -1))))


def symplectic_euler_modified_energy(
    trajectory: Trajectory,
    mass: float,
    potential: Potential,
    gradient: Callable[[Vector], Vector],
    dt: float,
) -> NDArray[np.float64]:
    """The modified energy of symplectic Euler, in J, to first order in the
    step ``dt`` (s): E - (dt / 2) ∇U(x)·v at every instant of ``trajectory``.

    ``gradient`` is ∇U, the gradient of the ``potential`` in N. For the
    harmonic oscillator this is the quantity of lesson L3 and is conserved to
    round-off; for any other potential it is conserved up to terms of second
    order in the step.
    """
    cross = np.array(
        [gradient(x) @ v for x, v in zip(trajectory.x, trajectory.v, strict=True)]
    )
    return mechanical_energy(trajectory, mass, potential) - 0.5 * dt * cross


def verlet_oscillator_modified_energy(
    trajectory: Trajectory, mass: float, k: float, dt: float
) -> NDArray[np.float64]:
    """The modified energy of velocity Verlet on the harmonic oscillator, in
    J: ½ m (v² + ω² (1 - ω² dt² / 4) x²), conserved to round-off (lesson M5)."""
    omega2 = k / mass
    x, v = trajectory.x[:, 0], trajectory.v[:, 0]
    return 0.5 * mass * (v**2 + omega2 * (1.0 - omega2 * dt**2 / 4.0) * x**2)
