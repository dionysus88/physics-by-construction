"""Sound in a pipe and the Doppler shift.

Sound is a pressure wave, and in a uniform medium the pressure obeys the
wave equation with the speed of sound c. In a pipe the ends decide the
resonances: an open end holds the pressure at its ambient value (a fixed end
of the field, p = 0), a closed end has no flow through it, which makes the
slope of the pressure zero (a free end).

The Doppler shift is computed from the moment of emission: a signal that
leaves the source at the time tau reaches the observer at the time t when
t - tau = |x_o(t) - x_s(tau)| / c. Nothing here uses the formulas of the
shift; they are in this module only to be compared with.

Quantities are in SI units; ``SPEED_OF_SOUND`` is in m/s.
"""

from collections.abc import Callable

import numpy as np
from numpy.typing import ArrayLike, NDArray

from pbc.waves.modes import measured_frequency

Array = NDArray[np.float64]
Path = Callable[[Array], Array]

__all__ = [
    "SPEED_OF_SOUND",
    "emission_time",
    "measured_frequency",
    "observer_shift",
    "pipe_frequency",
    "received_signal",
    "source_shift",
]

SPEED_OF_SOUND = 343.0  # air at 20 degrees Celsius, m/s


def pipe_frequency(n: int, *, length: float, c: float, closed_end: bool) -> float:
    """The frequency in Hz of resonance ``n`` (1, 2, ...) of a pipe of
    ``length`` m.

    Open at both ends: f_n = n c / (2 L), every harmonic. Closed at one end
    and open at the other: f_n = (2 n - 1) c / (4 L), the odd harmonics of
    the fundamental c / (4 L). The end correction of a real open end is not
    included (see the limits of lesson W9).
    """
    if n < 1 or length <= 0 or c <= 0:
        raise ValueError("need a resonance n >= 1, a positive length and speed")
    if closed_end:
        return (2 * n - 1) * c / (4.0 * length)
    return n * c / (2.0 * length)


def source_shift(f0: float, c: float, v_source: float) -> float:
    """The frequency heard by an observer at rest from a source that moves
    towards the observer with the speed ``v_source`` (negative: away),
    f0 c / (c - v_source)."""
    if abs(v_source) >= c:
        raise ValueError("the source must move slower than the sound")
    return f0 * c / (c - v_source)


def observer_shift(f0: float, c: float, v_observer: float) -> float:
    """The frequency heard by an observer who moves towards a source at rest
    with the speed ``v_observer`` (negative: away), f0 (c + v_observer) / c."""
    if abs(v_observer) >= c:
        raise ValueError("the observer must move slower than the sound")
    return f0 * (c + v_observer) / c


def emission_time(
    t: ArrayLike, source: Path, observer: Path, c: float, *, t_start: float = 0.0
) -> Array:
    """The time tau at which the signal that the observer receives at each
    time ``t`` left the source: the root of t - tau = |x_o(t) - x_s(tau)| / c.

    ``source`` and ``observer`` give the position (m) on the line at an
    array of times. Both must move slower than ``c``, and the signal must
    have left at or after ``t_start``. The root is found by bisection, which
    needs only that the left side minus the right side falls as tau
    increases, true for a source slower than the sound. A time before the
    first signal can arrive (including any ``t`` before ``t_start``) has no
    such root and raises ``ValueError``.
    """
    t = np.asarray(t, dtype=float)
    position = observer(t)
    first = source(np.full(t.shape, t_start))
    if np.any((t - t_start) - np.abs(position - first) / c < 0.0):
        raise ValueError(
            "no signal has arrived yet at some receive time: it is before t_start"
            " plus the travel time from the source"
        )
    low = np.full(t.shape, t_start)
    high = t.copy()
    for _ in range(80):
        middle = 0.5 * (low + high)
        # t - middle is the travel time available; the signal needs the
        # distance divided by c. Early tau leaves too little time to spare.
        spare = (t - middle) - np.abs(position - source(middle)) / c
        low = np.where(spare > 0.0, middle, low)
        high = np.where(spare > 0.0, high, middle)
    return 0.5 * (low + high)


def received_signal(
    t: ArrayLike,
    f0: float,
    source: Path,
    observer: Path,
    c: float,
    *,
    t_start: float = 0.0,
) -> Array:
    """The tone sin(2 pi f0 tau) that the source emits, as the observer
    receives it at the times ``t``. The amplitude is not changed by the
    distance."""
    tau = emission_time(t, source, observer, c, t_start=t_start)
    return np.sin(2.0 * np.pi * f0 * tau)
