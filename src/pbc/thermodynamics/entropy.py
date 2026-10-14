"""Entropy from ensembles: the Ehrenfest urn.

``n_particles`` distinguishable particles sit in the left or the right half of
a box. A microstate says which half each particle is in; a macrostate says only
how many, n, are on the left. There are C(N, n) microstates in the macrostate
n. One step of the dynamics picks a particle uniformly at random and puts it in
the left or the right half with probability one half each, wherever it was. (A
step that always moved the particle to the other half would make n alternate
between even and odd, and the ensemble would never reach equilibrium.) All
entropies are in units of k_B (nats), so S = ln(number).

An ensemble is many independent copies of the box, each started the same way.
"""

from math import lgamma, log

import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.float64]


def log_multiplicity(n_particles: int, n_left: Array) -> Array:
    """ln C(N, n): the Boltzmann entropy S / k_B of the macrostate with
    ``n_left`` particles on the left, from the log-gamma function so that a
    large N does not overflow."""
    n = np.atleast_1d(np.asarray(n_left, dtype=np.float64))
    total = lgamma(n_particles + 1.0)
    return np.array(
        [total - lgamma(k + 1.0) - lgamma(n_particles - k + 1.0) for k in n]
    )


def stirling_log_multiplicity_half(n_particles: int) -> float:
    """The Stirling approximation N ln 2 - ln(pi N / 2) / 2 to ln C(N, N/2)."""
    return n_particles * log(2.0) - 0.5 * log(np.pi * n_particles / 2.0)


def ehrenfest_ensemble(
    n_particles: int,
    n_members: int,
    n_steps: int,
    rng: np.random.Generator,
    n_start: int | None = None,
) -> NDArray[np.int64]:
    """The number of particles on the left for ``n_members`` boxes after 0,
    1, ..., ``n_steps`` steps: an array of shape ``(n_steps + 1, n_members)``.

    Every box starts with ``n_start`` particles on the left (all of them by
    default). A step re-places a uniformly chosen particle in a random half,
    so n falls by one with probability n / (2 N), rises by one with probability
    (N - n) / (2 N), and stays otherwise.
    """
    if n_particles < 1 or n_members < 1 or n_steps < 1:
        raise ValueError("n_particles, n_members, and n_steps must be at least 1")
    start = n_particles if n_start is None else n_start
    if not 0 <= start <= n_particles:
        raise ValueError("n_start must be between 0 and n_particles")
    counts = np.empty((n_steps + 1, n_members), dtype=np.int64)
    counts[0] = start
    draws = rng.random((n_steps, n_members))
    for k in range(n_steps):
        down = draws[k] < counts[k] / (2.0 * n_particles)
        up = draws[k] > 1.0 - (n_particles - counts[k]) / (2.0 * n_particles)
        counts[k + 1] = counts[k] - down + up
    return counts


def mean_left(n_particles: int, n_start: int, steps: Array) -> Array:
    """The exact ensemble mean of n after ``steps`` steps:
    N/2 + (n_start - N/2) (1 - 1/N)^steps. A step changes the mean by
    (N - 2 <n>) / (2 N), so the distance from N/2 shrinks by the factor 1 - 1/N."""
    t = np.asarray(steps, dtype=np.float64)
    half = n_particles / 2.0
    return half + (n_start - half) * (1.0 - 1.0 / n_particles) ** t


def distribution(counts_row: Array, n_particles: int) -> Array:
    """The empirical probability of n = 0, ..., N from one row of the ensemble."""
    return np.bincount(np.asarray(counts_row), minlength=n_particles + 1) / len(
        counts_row
    )


def shannon_entropy(p: Array) -> float:
    """-sum p ln p (nats) of a probability vector; zero entries count as zero."""
    q = np.asarray(p, dtype=np.float64)
    q = q[q > 0.0]
    return float(-np.sum(q * np.log(q)) + 0.0)  # + 0.0: no negative zero


def gibbs_entropy(p_macro: Array, n_particles: int) -> float:
    """The entropy S / k_B of an ensemble whose macrostate n has probability
    ``p_macro[n]``, with every microstate of a macrostate equally likely:
    -sum_n p_n ln(p_n / C(N, n)). It is the Shannon entropy of the microstates.
    At equilibrium, p_n = C(N, n) / 2^N, it is N ln 2."""
    p = np.asarray(p_macro, dtype=np.float64)
    omega = log_multiplicity(n_particles, np.arange(n_particles + 1))
    mask = p > 0.0
    return float(-np.sum(p[mask] * (np.log(p[mask]) - omega[mask])) + 0.0)


def equilibrium_entropy(n_particles: int) -> float:
    """N ln 2: the entropy S / k_B of the ensemble in which every one of the
    2^N microstates is equally likely."""
    return n_particles * log(2.0)


def plug_in_bias(p_macro: Array, n_members: int) -> float:
    """The amount (nats) by which the entropy of an ensemble of ``n_members``
    copies, estimated from the observed frequencies ``p_macro``, falls short of
    the entropy of the distribution the copies were drawn from, to first order:
    (K - 1) / (2 M), with K the number of macrostates that were observed and M
    the number of copies (the correction of Miller and Madow). It is an
    estimate of a bias, valid when every macrostate that matters is observed
    many times."""
    return (np.count_nonzero(np.asarray(p_macro)) - 1.0) / (2.0 * n_members)


def exact_distribution(n_particles: int, n_start: int, steps: int) -> Array:
    """The exact probability of n = 0, ..., N after ``steps`` steps of the urn
    (rows are the probabilities after 0, 1, ..., ``steps`` steps), from the
    transition probabilities of one step: n falls by one with probability
    n / (2 N), rises by one with probability (N - n) / (2 N), and stays with
    probability one half."""
    n = n_particles
    k = np.arange(n + 1)
    matrix = np.zeros((n + 1, n + 1))
    matrix[k[1:], k[1:] - 1] = k[1:] / (2.0 * n)
    matrix[k[:-1], k[:-1] + 1] = (n - k[:-1]) / (2.0 * n)
    matrix[k, k] = 0.5
    rows = np.zeros((steps + 1, n + 1))
    rows[0, n_start] = 1.0
    for s in range(steps):
        rows[s + 1] = rows[s] @ matrix
    return rows
