"""The double pendulum, and the Lyapunov exponent as the measure of chaos.

Two rigid, massless rods hang one from the other, the second from the end of
the first, and the two bobs swing in a vertical plane under their weights.
Two angles, measured from the downward vertical, describe it, so the state of
the ``pbc.mechanics.dynamics`` interface has two positions (the angles, rad)
and two velocities (the angular velocities, rad/s), and every stepper of the
course applies. The equations of motion are the ones the Lagrangian lesson
derives; ``pbc.mechanics.lagrangian`` checks them against that derivation.

For small angles the motion is a sum of two normal modes and regular. For
large angles it is chaotic: two starts that differ by a tiny amount separate
exponentially, at a rate the largest Lyapunov exponent measures. The estimate
here follows two nearby trajectories and rescales their separation before it
grows out of the linear regime (the method of Benettin and others).

Quantities are in SI units: lengths in metres, masses in kilograms, angles in
radians, energies in joules, exponents in 1/s.
"""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.constants import g as STANDARD_GRAVITY  # 9.80665 m/s²

from pbc.mechanics.dynamics import Acceleration, State, Stepper, Vector
from pbc.mechanics.integrators import rk4_step


def double_pendulum(
    m1: float, m2: float, l1: float, l2: float, g: float = STANDARD_GRAVITY
) -> Acceleration:
    """The angular accelerations (rad/s²) of a double pendulum with the bob
    masses ``m1`` and ``m2`` (kg) on rods of length ``l1`` and ``l2`` (m).

    The position is the pair of angles of the rods from the downward vertical,
    the velocity the pair of angular velocities. The equations come from the
    Lagrangian; the denominator is the determinant of the mass matrix, which
    never vanishes for positive masses.
    """
    if min(m1, m2, l1, l2, g) <= 0:
        raise ValueError("masses, lengths, and g must be positive")

    def acceleration(t: float, x: Vector, v: Vector) -> Vector:
        delta = x[0] - x[1]
        sin_d, cos_d = np.sin(delta), np.cos(delta)
        den = 2.0 * m1 + m2 - m2 * np.cos(2.0 * delta)
        a1 = (
            -g * (2.0 * m1 + m2) * np.sin(x[0])
            - m2 * g * np.sin(x[0] - 2.0 * x[1])
            - 2.0 * sin_d * m2 * (v[1] ** 2 * l2 + v[0] ** 2 * l1 * cos_d)
        ) / (l1 * den)
        a2 = (
            2.0
            * sin_d
            * (
                v[0] ** 2 * l1 * (m1 + m2)
                + g * (m1 + m2) * np.cos(x[0])
                + v[1] ** 2 * l2 * m2 * cos_d
            )
        ) / (l2 * den)
        return np.array([a1, a2])

    return acceleration


def double_pendulum_energy(
    x: NDArray[np.float64],
    v: NDArray[np.float64],
    m1: float,
    m2: float,
    l1: float,
    l2: float,
    g: float = STANDARD_GRAVITY,
) -> NDArray[np.float64]:
    """The energy in J of a double pendulum at every row of the angles ``x``
    (rad) and angular velocities ``v`` (rad/s), arrays of shape (n, 2).

    The kinetic energy has a cross term of the two angular velocities, so it
    is not the sum of two single-pendulum energies.
    """
    x, v = np.atleast_2d(x), np.atleast_2d(v)
    kinetic = (
        0.5 * (m1 + m2) * l1**2 * v[:, 0] ** 2
        + 0.5 * m2 * l2**2 * v[:, 1] ** 2
        + m2 * l1 * l2 * v[:, 0] * v[:, 1] * np.cos(x[:, 0] - x[:, 1])
    )
    potential = -(m1 + m2) * g * l1 * np.cos(x[:, 0]) - m2 * g * l2 * np.cos(x[:, 1])
    return kinetic + potential


@dataclass(frozen=True)
class LyapunovEstimate:
    """The largest Lyapunov exponent of a run, with how it was reached."""

    exponent: float  # 1/s, over the whole run
    t: NDArray[np.float64]  # s, the time of each rescaling
    running: NDArray[np.float64]  # 1/s, the estimate over the run so far


def lyapunov_exponent(
    initial: State,
    acceleration: Acceleration,
    dt: float,
    n_steps: int,
    separation: float = 1e-8,
    rescale_every: int = 10,
    step: Stepper = rk4_step,
) -> LyapunovEstimate:
    """Estimate the largest Lyapunov exponent (1/s) of the motion from
    ``initial`` by following a second trajectory that starts ``separation``
    away in phase space.

    The distance is the Euclidean norm of the difference of the combined
    vector of positions (rad) and velocities (rad/s), with equal weight, so
    the metric implicitly measures time in units of 1 s: a velocity
    difference of 1 rad/s counts as much as an angle difference of 1 rad.
    The exponent does not depend on this choice, but the finite-time
    separation does. Every ``rescale_every`` steps of
    length ``dt`` (s) the logarithm of the growth of the distance is added up
    and the second trajectory is pulled back to ``separation`` along the
    direction it has grown in, so the separation stays small enough to follow
    the linearised motion. The exponent is the sum of the logarithms divided
    by the time. For a regular motion the estimate falls towards zero as the
    run gets longer; for a chaotic one it settles at a positive value.
    """
    if separation <= 0 or rescale_every < 1 or n_steps < rescale_every:
        raise ValueError("need a positive separation and n_steps >= rescale_every >= 1")
    n = len(initial.x)
    first = initial
    direction = np.ones(2 * n) / np.sqrt(2 * n)
    second = State(
        t=initial.t,
        x=initial.x + separation * direction[:n],
        v=initial.v + separation * direction[n:],
    )
    total, times, running = 0.0, [], []
    for i in range(1, n_steps + 1):
        first = step(first, acceleration, dt)
        second = step(second, acceleration, dt)
        if i % rescale_every == 0:
            gap = np.concatenate([second.x - first.x, second.v - first.v])
            distance = float(np.linalg.norm(gap))
            total += np.log(distance / separation)
            gap *= separation / distance
            second = State(t=second.t, x=first.x + gap[:n], v=first.v + gap[n:])
            times.append(first.t - initial.t)
            running.append(total / (first.t - initial.t))
    return LyapunovEstimate(
        exponent=running[-1], t=np.array(times), running=np.array(running)
    )
