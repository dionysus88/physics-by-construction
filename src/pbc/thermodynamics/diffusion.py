"""Random walks and the diffusion they give rise to.

A walker takes a step of fixed length ``step_length`` (m) in a direction
chosen uniformly at random every ``tau`` seconds, independently of every
earlier step. Nothing in the rule mentions diffusion. The mean squared
displacement of many walkers grows linearly in time, and the slope defines the
diffusion coefficient D: <r²> = 2 d D t in d dimensions.

All randomness comes from a ``numpy.random.Generator`` that the caller creates
from a seed, so a walk is a function of its inputs. Quantities are in SI units;
the walk is in the plane unless ``dimension`` says otherwise.
"""

import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.float64]


def random_walks(
    n_walkers: int,
    n_steps: int,
    step_length: float,
    rng: np.random.Generator,
    dimension: int = 2,
) -> Array:
    """The positions (m) of ``n_walkers`` walkers that start at the origin,
    after 0, 1, ..., ``n_steps`` steps: an array of shape
    ``(n_steps + 1, n_walkers, dimension)``.

    Each step has length ``step_length`` and a direction uniform on the circle
    (``dimension`` 2) or on the line (``dimension`` 1, a step left or right).
    """
    if n_walkers < 1 or n_steps < 1 or step_length <= 0:
        raise ValueError(
            "n_walkers and n_steps must be at least 1, step_length positive"
        )
    if dimension == 1:
        steps = rng.choice([-1.0, 1.0], size=(n_steps, n_walkers, 1))
    elif dimension == 2:
        angles = rng.uniform(0.0, 2.0 * np.pi, size=(n_steps, n_walkers))
        steps = np.stack([np.cos(angles), np.sin(angles)], axis=-1)
    else:
        raise ValueError("dimension must be 1 or 2")
    paths = np.zeros((n_steps + 1, n_walkers, dimension))
    paths[1:] = np.cumsum(step_length * steps, axis=0)
    return paths


def mean_squared_displacement(paths: Array) -> Array:
    """<r²> (m²) over the walkers at every step: one value per row of ``paths``."""
    return np.mean(np.sum(paths**2, axis=-1), axis=1)


def diffusion_coefficient(times: Array, msd: Array, dimension: int = 2) -> float:
    """The diffusion coefficient D (m²/s) from <r²> = 2 d D t: the slope of the
    least-squares line through the origin, divided by 2 d."""
    t = np.asarray(times, dtype=np.float64)
    slope = float(np.sum(t * msd) / np.sum(t * t))
    return slope / (2.0 * dimension)


def predicted_diffusion_coefficient(
    step_length: float, tau: float, dimension: int = 2
) -> float:
    """D = l² / (2 d tau) (m²/s) for steps of length l every tau seconds: the
    steps are independent with mean square l², so <r²> = n l² after n steps,
    that is l² t / tau."""
    return step_length**2 / (2.0 * dimension * tau)


def fraction_within(paths_row: Array, radius: float) -> float:
    """The fraction of the walkers of one row of ``paths`` (one time) that are
    at a distance of at most ``radius`` (m) from the origin."""
    return float(np.mean(np.hypot(*np.asarray(paths_row).T) <= radius))


def predicted_fraction_within(radius: float, d: float, t: float) -> float:
    """The probability 1 - exp(-R² / (4 D t)) that a walker of the plane is
    within ``radius`` of the origin after ``t`` seconds, for diffusion
    coefficient ``d``: the integral of the Gaussian of variance 2 D t per
    coordinate over the disc."""
    return float(1.0 - np.exp(-(radius**2) / (4.0 * d * t)))
