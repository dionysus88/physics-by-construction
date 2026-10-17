"""The acceptance rule of a statistical check of a random model against a
theory: a fixed number of independent seeded runs, and a tolerance stated
before the runs are made.

Each run gives one value of a quantity. With ``k`` runs the mean ``m`` and
its standard error ``e = s / sqrt(k)`` follow, ``s`` the sample standard
deviation. The check passes when

    |m - theory| <= allowance + t e,

with ``t`` the two-sided quantile of Student's t with ``k - 1`` degrees of
freedom at the false-failure probability ``alpha``, and ``allowance`` a
stated, conservative allowance for the systematic difference between the
model and the theory (the time step of a simulation, a truncated series),
which more runs do not reduce. If the mean of the model is within
``allowance`` of the theory and the run values are independent and close to
Gaussian, then
``|m - theory| > allowance + t e`` needs ``|m - mean of the model| > t e``,
which has probability ``alpha``: the check fails a correct model with a
probability of at most ``alpha``, whatever the seeds.

The seeds fix the runs on one machine. They do not fix a chaotic run across
machines, whose floating-point libraries round differently, so another
machine draws, in effect, another sample; the stated ``alpha`` is what
keeps the verdict the same there.
"""

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike
from scipy import stats

# The probability that the check fails a model that is correct within the
# allowance: one in a thousand.
FALSE_FAILURE = 0.001


def t_factor(k: int, alpha: float = FALSE_FAILURE) -> float:
    """The number of standard errors that chance alone exceeds with the
    probability ``alpha``, for a standard error estimated from ``k`` runs:
    the two-sided quantile of Student's t with ``k - 1`` degrees of
    freedom."""
    if k < 2:
        raise ValueError("a standard error needs at least two runs")
    if not 0.0 < alpha < 1.0:
        raise ValueError(f"alpha must be between 0 and 1, got {alpha}")
    return float(stats.t.ppf(1.0 - alpha / 2.0, k - 1))


@dataclass(frozen=True)
class Agreement:
    """The outcome of the rule for one quantity.

    ``mean`` and ``error`` are the mean of the runs and its standard error,
    ``difference`` is ``mean - theory``, ``tolerance`` is
    ``allowance + t error``, and ``agrees`` says whether the difference is
    within it.
    """

    mean: float
    error: float
    theory: float
    difference: float
    tolerance: float

    @property
    def agrees(self) -> bool:
        return abs(self.difference) <= self.tolerance


def agreement(
    values: ArrayLike,
    theory: float,
    allowance: float = 0.0,
    alpha: float = FALSE_FAILURE,
) -> Agreement:
    """The rule applied to the ``values`` of independent runs against the
    ``theory``, with the systematic ``allowance`` (same unit as the values)
    and the false-failure probability ``alpha``."""
    v = np.asarray(values, dtype=np.float64)
    if v.ndim != 1 or v.size < 2:
        raise ValueError("the rule needs the values of at least two runs")
    if allowance < 0:
        raise ValueError(f"the allowance must not be negative, got {allowance}")
    mean = float(v.mean())
    error = float(v.std(ddof=1) / np.sqrt(v.size))
    return Agreement(
        mean=mean,
        error=error,
        theory=float(theory),
        difference=mean - float(theory),
        tolerance=allowance + t_factor(v.size, alpha) * error,
    )
