"""Superposition, standing waves, modes, and interference.

A string of length L with two fixed ends has the modes sin(n pi x / L) with
the frequencies f_n = n c / (2 L). A pluck is a sum of modes; the spectrum
of a recorded signal shows which. Two coherent sources add their waves, and
the intensity follows the sum, not the sum of the intensities.

Quantities are in SI units; frequencies are in Hz.
"""

import numpy as np
from numpy.typing import ArrayLike, NDArray

Array = NDArray[np.float64]


def string_frequency(n: int, *, length: float, c: float) -> float:
    """The frequency f_n = n c / (2 L) in Hz of mode ``n`` of a string of
    ``length`` m with two fixed ends (or two free ends) and wave speed
    ``c`` m/s."""
    if n < 1 or length <= 0 or c <= 0:
        raise ValueError("need a mode n >= 1, a positive length, and a positive speed")
    return n * c / (2.0 * length)


def triangle(x: ArrayLike, *, length: float, at: float, height: float = 1.0) -> Array:
    """A string plucked at ``at`` m: zero at both ends, ``height`` at the
    pluck, straight lines between."""
    x = np.asarray(x, dtype=float)
    if not 0.0 < at < length:
        raise ValueError("the pluck must lie inside the string")
    return height * np.where(x <= at, x / at, (length - x) / (length - at))


def triangle_mode_amplitude(n: int, *, length: float, at: float) -> float:
    """The amplitude of mode ``n`` in the sine series of ``triangle`` with
    unit height,

        b_n = 2 L^2 sin(n pi a / L) / (n^2 pi^2 a (L - a)),

    which vanishes for a mode with a node at the pluck."""
    a = at
    return float(
        2.0
        * length**2
        * np.sin(n * np.pi * a / length)
        / (n**2 * np.pi**2 * a * (length - a))
    )


def spectrum_peaks(
    signal: ArrayLike, dt: float, *, count: int, floor: float = 0.01
) -> Array:
    """The frequencies (Hz) of the ``count`` strongest peaks of the spectrum
    of ``signal`` sampled every ``dt`` seconds, lowest first.

    The signal is multiplied by a Hann window, zero-padded to eight times
    its length, and transformed; each peak is refined by the parabola
    through the logarithm of its magnitude and its two neighbours. A peak
    below ``floor`` times the strongest one is not a peak.
    """
    signal = np.asarray(signal, dtype=float)
    size = 8 * signal.size
    window = np.hanning(signal.size)
    magnitude = np.abs(np.fft.rfft((signal - signal.mean()) * window, size))
    df = 1.0 / (size * dt)
    inner = magnitude[1:-1]
    is_peak = (inner > magnitude[:-2]) & (inner >= magnitude[2:])
    index = np.nonzero(is_peak & (inner > floor * magnitude.max()))[0] + 1
    strongest = index[np.argsort(magnitude[index])[::-1][:count]]
    refined = []
    for i in np.sort(strongest):
        a, b, c = np.log(magnitude[i - 1 : i + 2])
        shift = 0.5 * (a - c) / (a - 2.0 * b + c)
        refined.append((i + shift) * df)
    return np.array(refined)


def two_source_amplitude(
    angle: ArrayLike, *, separation: float, wavelength: float, distance: float
) -> Array:
    """The amplitude on a screen at the ``distance`` m from two coherent
    point sources ``separation`` m apart, in phase, summed wave by wave.

    The sources lie on the x axis at plus and minus half the separation.
    Each gives a wave exp(i k r) / r with k = 2 pi / wavelength, at its
    distance r from the point of the screen that lies at the ``angle`` (rad)
    from the y axis, seen from the middle between the sources. The two complex waves
    are added, and the modulus is returned. The sum is the superposition
    principle; no formula for the pattern is used.
    """
    angle = np.asarray(angle, dtype=float)
    k = 2.0 * np.pi / wavelength
    px = distance * np.sin(angle)
    py = distance * np.cos(angle)
    total = np.zeros(angle.shape, dtype=complex)
    for source in (-separation / 2.0, separation / 2.0):
        r = np.hypot(px - source, py)
        total += np.exp(1j * k * r) / r
    return np.abs(total)


def two_source_pattern(
    angle: ArrayLike, *, separation: float, wavelength: float
) -> Array:
    """The far-field intensity of two equal coherent sources, relative to
    the intensity of one source, cos^2(pi d sin(theta) / lambda), times
    four (the two amplitudes add before they are squared)."""
    angle = np.asarray(angle, dtype=float)
    return 4.0 * np.cos(np.pi * separation * np.sin(angle) / wavelength) ** 2


def measured_frequency(signal: ArrayLike, t: ArrayLike) -> float:
    """The frequency (Hz) of a tone, from its rising zero crossings: the
    number of periods between the first and the last crossing, divided by
    the time between them. A crossing is placed by linear interpolation
    between the two samples around it."""
    signal = np.asarray(signal, dtype=float)
    t = np.asarray(t, dtype=float)
    up = np.nonzero((signal[:-1] < 0.0) & (signal[1:] >= 0.0))[0]
    if up.size < 2:
        raise ValueError("fewer than two rising zero crossings in the signal")
    fraction = -signal[up] / (signal[up + 1] - signal[up])
    crossings = t[up] + fraction * (t[up + 1] - t[up])
    return float((up.size - 1) / (crossings[-1] - crossings[0]))


def wave_packet(x: ArrayLike, *, centre: float, width: float, k: float) -> Array:
    """A packet: the carrier cos(k (x - centre)) under a Gaussian envelope
    exp(-((x - centre) / width)^2)."""
    x = np.asarray(x, dtype=float)
    return np.exp(-(((x - centre) / width) ** 2)) * np.cos(k * (x - centre))


def centroid(x: ArrayLike, field: ArrayLike) -> float:
    """The position (m) of the centre of the energy of a field: the average
    of x weighted by the square of the field."""
    x = np.asarray(x, dtype=float)
    weight = np.asarray(field, dtype=float) ** 2
    return float(np.sum(x * weight) / np.sum(weight))
