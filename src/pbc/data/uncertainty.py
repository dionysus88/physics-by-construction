"""Noise and uncertainty: what the data say about their own scatter.

Uncertainties here are standard uncertainties (one standard deviation) unless
a name says otherwise. Propagation is first order and treats the inputs as
independent; a result that depends on correlated inputs needs its covariance.
"""

from collections.abc import Callable, Sequence

import numpy as np

MAD_TO_SIGMA = 1.4826  # for normally distributed noise
K95 = 1.959964  # coverage factor of a normal distribution at 95 %


def robust_sigma(x: np.ndarray) -> float:
    """Noise standard deviation from the median absolute deviation.

    Ignores NaN and is little affected by a signal that is much smaller in
    extent than the noise record.
    """
    values = np.asarray(x, dtype=float)
    values = values[np.isfinite(values)]
    return float(MAD_TO_SIGMA * np.median(np.abs(values - np.median(values))))


def standard_error(repetitions: np.ndarray, axis: int = 0) -> np.ndarray:
    """Standard uncertainty of the mean of ``n`` repetitions along ``axis``."""
    n = repetitions.shape[axis]
    if n < 2:
        raise ValueError("at least two repetitions are needed")
    return np.std(repetitions, axis=axis, ddof=1) / np.sqrt(n)


def quadrature(*sigmas: np.ndarray | float) -> np.ndarray | float:
    """Combine independent standard uncertainties."""
    return np.sqrt(sum(np.square(s) for s in sigmas))


def standard_from_expanded(expanded: np.ndarray | float, k: float = K95):
    """Standard uncertainty from an expanded one with coverage factor ``k``."""
    return np.asarray(expanded) / k


def propagate(
    func: Callable[..., np.ndarray],
    values: Sequence[np.ndarray | float],
    sigmas: Sequence[np.ndarray | float],
) -> tuple[np.ndarray, np.ndarray]:
    """Value and standard uncertainty of ``func(*values)`` for independent inputs.

    The derivative with respect to each input is a central difference with a
    step of 1e-6 of the input's scale, so ``func`` must be smooth there.
    """
    if len(values) != len(sigmas):
        raise ValueError("one uncertainty for each value")
    arrays = [np.asarray(v, dtype=float) for v in values]
    result = np.asarray(func(*arrays), dtype=float)
    variance = np.zeros_like(result)
    for k, sigma in enumerate(sigmas):
        step = 1e-6 * np.maximum(np.abs(arrays[k]), 1.0)
        up = list(arrays)
        down = list(arrays)
        up[k] = arrays[k] + step
        down[k] = arrays[k] - step
        slope = (np.asarray(func(*up)) - np.asarray(func(*down))) / (2 * step)
        variance = variance + (slope * np.asarray(sigma, dtype=float)) ** 2
    return result, np.sqrt(variance)


def normalised_difference(a, sigma_a, b, sigma_b) -> np.ndarray:
    """``(a - b)`` in units of its combined standard uncertainty.

    Two values agree within their uncertainties where the magnitude is below
    the coverage factor (about 2).
    """
    return (np.asarray(a) - np.asarray(b)) / quadrature(sigma_a, sigma_b)
