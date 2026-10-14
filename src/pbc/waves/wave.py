"""The one-dimensional wave equation, u_tt = c^2 u_xx, on a finite line.

The solver is the leapfrog scheme: centred differences in time and in space.
One step is

    u[n+1] = 2 u[n] - u[n-1] + C^2 (u[n, i+1] - 2 u[n, i] + u[n, i-1]),

with the Courant number C = c dt / dx. The scheme is stable for C <= 1 and
second-order accurate; at C = 1 it is exact on the grid. Each end of the
line is either ``fixed`` (u = 0, a string held at the end, or the open end
of a pipe for the pressure) or ``free`` (du/dx = 0, a string on a sliding
ring, or the closed end of a pipe for the pressure).

Quantities are in SI units: lengths in m, times in s, the speed in m/s. The
unit of the field u does not matter, the equation is linear.
"""

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray

Array = NDArray[np.float64]

ENDS = ("fixed", "free")


@dataclass(frozen=True)
class Solution:
    """The field on the grid at the recorded steps.

    ``u[j]`` is the field at the time ``t[j]``, with one column per node
    ``x[i]``.
    """

    x: Array
    t: Array
    u: Array


def courant_number(c: float, dt: float, dx: float) -> float:
    """The Courant number c dt / dx: the fraction of a grid cell that a wave
    crosses in one time step."""
    if c <= 0 or dt <= 0 or dx <= 0:
        raise ValueError(f"c, dt, and dx must be positive, got {c}, {dt}, {dx}")
    return c * dt / dx


def grid(length: float, n_cells: int) -> Array:
    """The ``n_cells + 1`` nodes of a line of ``length`` m, ends included."""
    if length <= 0 or n_cells < 2:
        raise ValueError("the line needs a positive length and at least 2 cells")
    return np.linspace(0.0, length, n_cells + 1)


def _laplacian(u: Array, left: str, right: str) -> Array:
    """The second difference of ``u`` at every node, in units of u / dx^2,
    with the condition of each end applied: a fixed end is held at zero, and
    a free end has a mirror image of the node next to it behind the end."""
    padded = np.empty(u.size + 2)
    padded[1:-1] = u
    padded[0] = u[1] if left == "free" else 0.0
    padded[-1] = u[-2] if right == "free" else 0.0
    second = padded[2:] - 2.0 * padded[1:-1] + padded[:-2]
    if left == "fixed":
        second[0] = 0.0
    if right == "fixed":
        second[-1] = 0.0
    return second


def solve(
    u0: ArrayLike,
    v0: ArrayLike,
    *,
    c: float,
    dx: float,
    dt: float,
    n_steps: int,
    left: str = "fixed",
    right: str = "fixed",
    every: int = 1,
    forcing: Callable[[float], ArrayLike] | None = None,
) -> Solution:
    """Advance the initial shape ``u0`` and the initial velocity ``v0``
    (arrays on the grid) by ``n_steps`` steps of ``dt`` seconds.

    ``forcing``, if given, is a function of the time that returns the
    acceleration, u_tt - c^2 u_xx, that an outside force adds at every node
    (in units of u per s^2); the nodes of a fixed end stay at zero.

    The field is recorded at the start and after every ``every`` steps, and
    always after the last one. The first step uses the Taylor expansion
    u1 = u0 + dt v0 + (C^2 / 2) (second difference of u0), which is accurate
    to the order of the scheme. A Courant number above one is not refused:
    lesson W1 shows what happens then.
    """
    if left not in ENDS or right not in ENDS:
        raise ValueError(f"an end is one of {ENDS}, got {left!r} and {right!r}")
    if n_steps < 1 or every < 1:
        raise ValueError("n_steps and every must be at least 1")
    previous = np.array(u0, dtype=float)
    velocity = np.asarray(v0, dtype=float)
    if previous.ndim != 1 or velocity.shape != previous.shape:
        raise ValueError("u0 and v0 must be arrays of the same length")
    x = dx * np.arange(previous.size)
    c2 = courant_number(c, dt, dx) ** 2
    if left == "fixed":
        previous[0] = 0.0
        velocity = velocity.copy()
        velocity[0] = 0.0
    if right == "fixed":
        previous[-1] = 0.0
        velocity = velocity.copy()
        velocity[-1] = 0.0

    def pushed(time: float) -> Array | float:
        if forcing is None:
            return 0.0
        push = np.array(forcing(time), dtype=float)
        if left == "fixed":
            push[0] = 0.0
        if right == "fixed":
            push[-1] = 0.0
        return dt * dt * push

    current = (
        previous
        + dt * velocity
        + 0.5 * c2 * _laplacian(previous, left, right)
        + 0.5 * pushed(0.0)
    )
    times = [0.0]
    records = [previous.copy()]
    if every == 1 or n_steps == 1:
        times.append(dt)
        records.append(current.copy())
    for step in range(2, n_steps + 1):
        following = (
            2.0 * current
            - previous
            + c2 * _laplacian(current, left, right)
            + pushed((step - 1) * dt)
        )
        previous, current = current, following
        if step % every == 0 or step == n_steps:
            times.append(step * dt)
            records.append(current.copy())
    return Solution(x=x, t=np.array(times), u=np.array(records))


def standing_mode(
    x: ArrayLike, t: ArrayLike, *, length: float, n: int, c: float
) -> Array:
    """The exact mode ``n`` of a line with two fixed ends,

        u(x, t) = sin(n pi x / L) cos(n pi c t / L),

    which starts at rest. ``x`` and ``t`` broadcast against each other."""
    k = n * np.pi / length
    return np.sin(k * np.asarray(x)) * np.cos(k * c * np.asarray(t))


def reflected_pulse(
    shape: Callable[[Array], Array],
    x: ArrayLike,
    t: float,
    *,
    length: float,
    c: float,
    ends: str,
) -> Array:
    """The exact field at time ``t`` of a pulse that starts at rest with the
    ``shape`` (a function that is zero near the ends), on a line whose two
    ends are both ``fixed`` or both ``free``.

    By d'Alembert, u = (F(x - ct) + F(x + ct)) / 2, where F continues the
    shape beyond the line by reflection in each end: with a minus sign at a
    fixed end, with a plus sign at a free end. The continuation repeats
    after 2 L.
    """
    if ends not in ENDS:
        raise ValueError(f"the ends are one of {ENDS}, got {ends!r}")
    sign = -1.0 if ends == "fixed" else 1.0

    def continued(s: Array) -> Array:
        s = np.mod(s, 2.0 * length)
        outside = s > length
        return np.where(outside, sign * shape(2.0 * length - s), shape(s))

    x = np.asarray(x, dtype=float)
    return 0.5 * (continued(x - c * t) + continued(x + c * t))


def error_norm(computed: ArrayLike, exact: ArrayLike) -> float:
    """The largest absolute difference between two fields on the grid."""
    return float(np.max(np.abs(np.asarray(computed) - np.asarray(exact))))


def observed_order(spacings: ArrayLike, errors: ArrayLike) -> float:
    """The order p of an error that behaves as error = a * spacing^p: the
    slope of the least-squares line through log(error) against
    log(spacing)."""
    spacings = np.asarray(spacings, dtype=float)
    errors = np.asarray(errors, dtype=float)
    if spacings.shape != errors.shape or spacings.size < 2:
        raise ValueError("need at least two spacings with one error each")
    if np.any(spacings <= 0) or np.any(errors <= 0):
        raise ValueError("spacings and errors must be positive")
    return float(np.polyfit(np.log(spacings), np.log(errors), 1)[0])


def growth_factor(courant: float) -> float:
    """The largest factor by which one step of the scheme multiplies a mode
    of the grid, at the Courant number ``courant``.

    A mode that varies as lambda^n in time satisfies, with s = sin(k dx / 2),
    lambda + 1 / lambda = 2 - 4 C^2 s^2. For C <= 1 both roots lie on the
    unit circle for every s. Above C = 1 the zigzag mode, s = 1, has
    2 - 4 C^2 < -2 and one root of modulus above one, which is returned.
    """
    if courant <= 0:
        raise ValueError(f"the Courant number must be positive, got {courant}")
    b = 4.0 * courant**2 - 2.0
    if b <= 2.0:
        return 1.0
    return float((b + np.sqrt(b * b - 4.0)) / 2.0)


def numerical_angular_frequency(k: ArrayLike, *, c: float, dx: float, dt: float):
    """The angular frequency (rad/s) with which the scheme oscillates the
    mode of wavenumber ``k`` (rad/m) on a grid: from

        sin(omega dt / 2) = C sin(k dx / 2)

    the frequency is omega = (2 / dt) arcsin(C sin(k dx / 2)). It
    approaches c k as dx and dt go to zero, and equals it at C = 1.
    """
    courant = courant_number(c, dt, dx)
    argument = courant * np.sin(np.asarray(k) * dx / 2.0)
    if np.any(np.abs(argument) > 1.0):
        raise ValueError("the Courant number is too large: the mode does not oscillate")
    return 2.0 / dt * np.arcsin(argument)


def zigzag_run(
    courant: float, *, n_cells: int = 60, n_steps: int = 40, size: float = 1e-10
) -> Solution:
    """The scheme run from a tiny zigzag, the shape +size, -size, +size, ...
    of neighbouring nodes, on a line of unit length and wave speed one, with
    two free ends, at the given Courant number.

    The zigzag is the mode that the scheme amplifies first when the Courant
    number is above one; a size at the level of round-off shows how little
    it takes.
    """
    x = grid(1.0, n_cells)
    dx = 1.0 / n_cells
    return solve(
        size * (-1.0) ** np.arange(x.size),
        np.zeros_like(x),
        c=1.0,
        dx=dx,
        dt=courant * dx,
        n_steps=n_steps,
        left="free",
        right="free",
    )


def amplitude_growth(solution: Solution, window: int = 10) -> float:
    """The factor per step by which the largest value of the field grows
    over the last ``window`` steps of a solution recorded at every step.

    A mode that oscillates in time passes its peak between steps, so the
    value is a good estimate only when the field grows by a large factor
    over the window."""
    size = np.max(np.abs(solution.u), axis=1)
    return float((size[-1] / size[-1 - window]) ** (1.0 / window))


def driven_mode_amplitude(
    t: ArrayLike, *, length: float, n: int, c: float, drive: float
) -> Array:
    """The exact amplitude a(t) of mode ``n`` of a line with two fixed ends,
    started at rest, when the force adds the acceleration
    sin(n pi x / L) cos(Omega t) with Omega = ``drive`` (rad/s).

    The amplitude obeys a'' + w^2 a = cos(Omega t), with w = n pi c / L, so

        a(t) = (cos(Omega t) - cos(w t)) / (w^2 - Omega^2),

    and, at resonance, Omega = w, a(t) = t sin(w t) / (2 w): the amplitude
    grows in proportion to the time without limit.
    """
    t = np.asarray(t, dtype=float)
    w = n * np.pi * c / length
    if np.isclose(drive, w, rtol=1e-12):
        return t * np.sin(w * t) / (2.0 * w)
    return (np.cos(drive * t) - np.cos(w * t)) / (w * w - drive * drive)


def numerical_group_velocity(k: ArrayLike, *, c: float, dx: float, dt: float):
    """The speed (m/s) at which the envelope of a packet of wavenumber ``k``
    (rad/m) travels on the grid, d omega / d k of the dispersion relation of
    ``numerical_angular_frequency``:

        c cos(k dx / 2) / sqrt(1 - C^2 sin^2(k dx / 2)).

    It is below ``c`` for every k at C < 1 and falls to zero at the shortest
    wave the grid holds, k dx = pi."""
    courant = courant_number(c, dt, dx)
    half = np.asarray(k) * dx / 2.0
    root = 1.0 - (courant * np.sin(half)) ** 2
    if np.any(root <= 0.0):
        raise ValueError("the Courant number is too large: the mode does not oscillate")
    return c * np.cos(half) / np.sqrt(root)
