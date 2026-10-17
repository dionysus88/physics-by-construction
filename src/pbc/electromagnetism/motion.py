"""A charged particle in given electric and magnetic fields: the Lorentz
force, the Boris pusher, and the closed forms it is compared with.

The particle moves under m dv/dt = q (E + v x B), slower than light, and
its own field is ignored. The fields are given: a constant vector, or a
function of the position (3,) in m and the time in s. Quantities are in SI
units: E in V/m, B in T, ``q_over_m`` in C/kg.

The Boris pusher keeps the position at whole steps and the velocity at half
steps. A magnetic field only turns the velocity, and the pusher turns it by
an exact rotation, so it keeps the speed to round-off; its angle per step
is 2 arctan(omega dt / 2), not omega dt, which gives it a frequency and a
radius of its own that converge to the true ones with order two.
"""

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray

Array = NDArray[np.float64]
Field = Callable[[Array, float], Array]

__all__ = [
    "ELECTRON_CHARGE_TO_MASS",
    "PROTON_CHARGE_TO_MASS",
    "Trajectory",
    "boris",
    "boris_frequency",
    "boris_radius",
    "cyclotron_frequency",
    "drift_velocity",
    "euler_energy_factor",
    "explicit_euler",
    "fitted_radius",
    "guiding_centre_velocity",
    "larmor_radius",
    "measured_angular_frequency",
]

PROTON_CHARGE_TO_MASS = 1.602176634e-19 / 1.67262192369e-27  # C/kg (CODATA 2018)
ELECTRON_CHARGE_TO_MASS = -1.602176634e-19 / 9.1093837015e-31  # C/kg (CODATA 2018)


@dataclass(frozen=True)
class Trajectory:
    """Times ``t`` (n + 1,) in s, positions ``x`` (n + 1, 3) in m, and
    velocities ``v`` (n + 1, 3) in m/s. For the Boris pusher ``v[k]`` is the
    velocity at ``t[k] - dt / 2``, half a step before the position."""

    t: Array
    x: Array
    v: Array


def _as_field(field: ArrayLike | Field) -> Field:
    if callable(field):
        return field
    value = np.asarray(field, dtype=float)
    if value.shape != (3,):
        raise ValueError("a constant field is a vector of three components")
    return lambda x, t: value


def boris(
    x0: ArrayLike,
    v0: ArrayLike,
    *,
    q_over_m: float,
    electric: ArrayLike | Field,
    magnetic: ArrayLike | Field,
    dt: float,
    n_steps: int,
) -> Trajectory:
    """The motion from ``x0`` (m) with the velocity ``v0`` (m/s) half a step
    before the start, by the Boris pusher with the step ``dt`` (s).

    Each step is a half kick by the electric field, a rotation by the
    magnetic field, a second half kick, and a drift of the position with
    the new velocity.
    """
    if dt <= 0 or n_steps < 1:
        raise ValueError("need a positive step and at least one step")
    electric, magnetic = _as_field(electric), _as_field(magnetic)
    t = np.arange(n_steps + 1) * dt
    x = np.empty((n_steps + 1, 3))
    v = np.empty((n_steps + 1, 3))
    x[0], v[0] = np.asarray(x0, dtype=float), np.asarray(v0, dtype=float)
    half = 0.5 * q_over_m * dt
    for n in range(n_steps):
        kick = half * electric(x[n], t[n])
        # region: rotation
        turn = half * magnetic(x[n], t[n])
        scale = 2.0 / (1.0 + turn @ turn)
        minus = v[n] + kick
        prime = minus + np.cross(minus, turn)
        plus = minus + scale * np.cross(prime, turn)
        # endregion: rotation
        v[n + 1] = plus + kick
        x[n + 1] = x[n] + dt * v[n + 1]
    return Trajectory(t=t, x=x, v=v)


def explicit_euler(
    x0: ArrayLike,
    v0: ArrayLike,
    *,
    q_over_m: float,
    electric: ArrayLike | Field,
    magnetic: ArrayLike | Field,
    dt: float,
    n_steps: int,
) -> Trajectory:
    """The motion by explicit Euler: the position and the velocity each
    advanced with the rate at the start of the step. ``v[k]`` is the
    velocity at ``t[k]``. In a magnetic field it does not keep the speed."""
    if dt <= 0 or n_steps < 1:
        raise ValueError("need a positive step and at least one step")
    electric, magnetic = _as_field(electric), _as_field(magnetic)
    t = np.arange(n_steps + 1) * dt
    x = np.empty((n_steps + 1, 3))
    v = np.empty((n_steps + 1, 3))
    x[0], v[0] = np.asarray(x0, dtype=float), np.asarray(v0, dtype=float)
    for n in range(n_steps):
        force = q_over_m * (electric(x[n], t[n]) + np.cross(v[n], magnetic(x[n], t[n])))
        x[n + 1] = x[n] + dt * v[n]
        v[n + 1] = v[n] + dt * force
    return Trajectory(t=t, x=x, v=v)


def cyclotron_frequency(q_over_m: float, b: float) -> float:
    """The angular frequency |q| B / m (rad/s) of the gyration in a
    uniform magnetic field of strength ``b`` (T)."""
    return abs(q_over_m * b)


def larmor_radius(q_over_m: float, b: float, v_perpendicular: float) -> float:
    """The radius m v / (|q| B) (m) of the circle of a particle with the
    speed ``v_perpendicular`` (m/s) across a uniform field ``b`` (T)."""
    return abs(v_perpendicular) / cyclotron_frequency(q_over_m, b)


def boris_frequency(omega: float, dt: float) -> float:
    """The angular frequency of the gyration that the Boris pusher computes
    at the true frequency ``omega`` (rad/s) and the step ``dt`` (s):
    2 arctan(omega dt / 2) / dt, below omega by omega^3 dt^2 / 12 to the
    lowest order."""
    return 2.0 * np.arctan(0.5 * omega * dt) / dt


def boris_radius(omega: float, dt: float, v_perpendicular: float) -> float:
    """The radius of the circle on which the Boris positions lie:
    (v / omega) sqrt(1 + (omega dt / 2)^2). The positions are the corners of
    a regular polygon with the side v dt, turned by the angle of
    ``boris_frequency`` per step."""
    return abs(v_perpendicular) / omega * np.sqrt(1.0 + (0.5 * omega * dt) ** 2)


def euler_energy_factor(omega: float, dt: float) -> float:
    """The factor 1 + (omega dt)^2 by which one explicit Euler step in a
    magnetic field multiplies the kinetic energy of a particle moving
    across the field."""
    return 1.0 + (omega * dt) ** 2


def drift_velocity(electric: ArrayLike, magnetic: ArrayLike) -> Array:
    """The drift E x B / B^2 (m/s) of the centre of the circle in crossed
    uniform fields, valid while it is slower than light."""
    e = np.asarray(electric, dtype=float)
    b = np.asarray(magnetic, dtype=float)
    return np.cross(e, b) / (b @ b)


def measured_angular_frequency(
    t: ArrayLike, v: ArrayLike, *, drift: ArrayLike = (0.0, 0.0, 0.0)
) -> float:
    """The rate (rad/s) at which the velocity, less ``drift``, turns in the
    x-y plane: the slope of its unwrapped angle against the time, fitted by
    least squares. Positive whatever the sense of the turn."""
    t = np.asarray(t, dtype=float)
    u = np.asarray(v, dtype=float) - np.asarray(drift, dtype=float)
    angle = np.unwrap(np.arctan2(u[:, 1], u[:, 0]))
    return float(abs(np.polyfit(t, angle, 1)[0]))


def fitted_radius(x: ArrayLike) -> float:
    """The radius of the circle that fits the x-y components of the
    positions ``x`` (n, 3) best in the algebraic least-squares sense
    (x^2 + y^2 + D x + E y + F = 0). Exact for points on a circle."""
    x = np.asarray(x, dtype=float)
    a = np.column_stack([x[:, 0], x[:, 1], np.ones(len(x))])
    b = -(x[:, 0] ** 2 + x[:, 1] ** 2)
    d, e, f = np.linalg.lstsq(a, b, rcond=None)[0]
    return float(np.sqrt(0.25 * (d**2 + e**2) - f))


def guiding_centre_velocity(t: ArrayLike, x: ArrayLike, omega: float) -> Array:
    """The velocity of the centre of the circle: for each component, the
    slope c1 of the least-squares fit x = c0 + c1 t + c2 cos(omega t) +
    c3 sin(omega t), with ``omega`` the frequency of the gyration."""
    t = np.asarray(t, dtype=float)
    # the time is centred and scaled to [-1, 1] so that the columns of the
    # fit are of one size
    middle, half = 0.5 * (t[0] + t[-1]), 0.5 * (t[-1] - t[0])
    design = np.column_stack(
        [np.ones_like(t), (t - middle) / half, np.cos(omega * t), np.sin(omega * t)]
    )
    coefficients = np.linalg.lstsq(design, np.asarray(x, dtype=float), rcond=None)[0]
    return coefficients[1] / half
