"""The Maxwell distribution of speeds at the temperature of a simulated gas.

The gas is the model of ``pbc.abm.gas``: discs that move, bounce, and collide.
This module holds the analytic distribution of the two-dimensional gas that the
lesson compares the simulated speeds with. With ``kt`` the energy k_B T (J) and
``mass`` the mass of a disc (kg), each velocity component is Gaussian of
variance kt / mass, and the speed follows the Rayleigh distribution.
"""

import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.float64]


def speed_cdf(speed: Array, kt: float, mass: float) -> Array:
    """The probability 1 - exp(-m v² / (2 k_B T)) that a disc is slower than
    ``speed`` (m/s)."""
    v = np.asarray(speed, dtype=np.float64)
    return 1.0 - np.exp(-mass * v**2 / (2.0 * kt))


def speed_quantile(probability: Array, kt: float, mass: float) -> Array:
    """The speed (m/s) that a fraction ``probability`` of the discs is slower
    than: the inverse of ``speed_cdf``, sqrt(-2 k_B T ln(1 - p) / m)."""
    p = np.asarray(probability, dtype=np.float64)
    return np.sqrt(-2.0 * kt * np.log1p(-p) / mass)


def mean_speed(kt: float, mass: float) -> float:
    """The mean speed sqrt(pi k_B T / (2 m)) (m/s) of the two-dimensional gas."""
    return float(np.sqrt(np.pi * kt / (2.0 * mass)))


def most_probable_speed(kt: float, mass: float) -> float:
    """The speed sqrt(k_B T / m) (m/s) at which the density of the speed peaks."""
    return float(np.sqrt(kt / mass))


def fractions_below(speeds: Array, thresholds: Array) -> Array:
    """The fraction of ``speeds`` below each of the ``thresholds``: the
    empirical distribution function at those speeds."""
    s = np.sort(np.asarray(speeds, dtype=np.float64).ravel())
    return np.searchsorted(s, np.asarray(thresholds), side="left") / s.size
