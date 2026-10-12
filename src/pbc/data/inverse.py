"""Inverse problems: recover parameters, say how sure, say when a fit is not evidence.

Three tools on top of ``pbc.data.fit.fit_curve``:

* ``recover`` fits many synthetic data sets made from known parameters and
  reports the bias, the scatter, and how often the stated interval holds the
  truth. A fit helper that is not checked against known answers is not a
  measurement tool.
* ``profile`` scans one parameter and refits the others at every value. A
  parameter that the data determine gives a bowl; one that they do not gives
  a profile that never rises, and the result says so.
* ``residual_autocorrelation`` and ``verdict`` collect the reasons not to
  believe a fit that converged: structure left in the residuals, a
  chi-square far from its expectation, parameters tied together.
"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy import optimize

from pbc.data.fit import FitResult, fit_curve

Array = NDArray[np.float64]
Model = Callable[..., Array]

# Change of the chi-square from its minimum that bounds a 68 % interval of
# one parameter when the others are refitted.
DELTA_CHI2 = 1.0
# A lag-1 autocorrelation of the residuals beyond this many times its
# standard deviation for independent residuals, 1/sqrt(n), is structure.
STRUCTURE_SIGMAS = 3.0
MIN_RESIDUALS = 8


@dataclass(frozen=True)
class Recovery:
    names: tuple[str, ...]
    truth: Array
    mean: Array  # mean estimate over the identified trials
    bias: Array  # mean minus truth
    rms_error: Array  # root mean square of the error of one estimate
    mean_stderr: Array  # mean stated standard error
    coverage: Array  # fraction of the trials whose 95 % interval holds the truth
    trials: int
    unidentified: int  # trials in which the fit reported a parameter as not determined
    failed: int  # trials in which the optimiser did not converge

    def recovered(self, rel_tol: float, *, coverage: float = 0.85) -> bool:
        """Estimates within ``rel_tol`` of the truth, and honest intervals."""
        scale = np.where(self.truth != 0, np.abs(self.truth), 1.0)
        return bool(
            np.all(np.abs(self.bias) <= rel_tol * scale)
            and np.all(self.rms_error <= rel_tol * scale)
            and np.all(self.coverage >= coverage)
            and self.unidentified == 0
            and self.failed == 0
        )


def recover(
    model: Model,
    x: Array,
    truth: Sequence[float],
    *,
    sigma: float,
    trials: int = 200,
    seed: int = 0,
    names: Sequence[str] | None = None,
    start_spread: float = 0.2,
    bounds: tuple = (-np.inf, np.inf),
) -> Recovery:
    """Fit ``trials`` noisy copies of ``model(x, *truth)`` and compare with the truth.

    The noise is Gaussian with standard deviation ``sigma``. Each fit starts
    from the truth changed by a random relative amount of up to
    ``start_spread``, so that the fit has to find the answer.
    """
    x = np.asarray(x, dtype=float)
    truth_array = np.asarray(truth, dtype=float)
    clean = model(x, *truth_array)
    rng = np.random.default_rng(seed)
    estimates, stderrs, inside = [], [], []
    unidentified = failed = 0
    for _ in range(trials):
        y = clean + rng.normal(0.0, sigma, size=x.shape)
        start = truth_array * (
            1 + rng.uniform(-start_spread, start_spread, truth_array.shape)
        )
        fit = fit_curve(model, x, y, start, sigma=sigma, names=names, bounds=bounds)
        if any("did not converge" in w for w in fit.warnings):
            failed += 1
            continue
        if not all(fit.identifiable):
            unidentified += 1
            continue
        low, high = np.array([fit.interval(n) for n in fit.names]).T
        estimates.append(fit.params)
        stderrs.append(fit.stderr)
        inside.append((low <= truth_array) & (truth_array <= high))
    if not estimates:
        raise ValueError("no trial gave an identified fit")
    est = np.array(estimates)
    error = est - truth_array
    return Recovery(
        names=fit.names,
        truth=truth_array,
        mean=est.mean(axis=0),
        bias=error.mean(axis=0),
        rms_error=np.sqrt((error**2).mean(axis=0)),
        mean_stderr=np.array(stderrs).mean(axis=0),
        coverage=np.array(inside).mean(axis=0),
        trials=trials,
        unidentified=unidentified,
        failed=failed,
    )


@dataclass(frozen=True)
class Profile:
    name: str
    grid: Array
    chi2: Array  # minimum over the other parameters at each grid value
    best: float  # grid value of the lowest chi-square
    low: float  # end of the 68 % interval; the grid end if the profile stays low
    high: float
    open_low: bool  # the profile does not rise by DELTA_CHI2 on this side
    open_high: bool

    @property
    def bounded(self) -> bool:
        """The data bound the parameter from both sides inside the grid."""
        return not (self.open_low or self.open_high)


def _edge(grid: Array, chi2: Array, best: int, step: int) -> tuple[float, bool]:
    level = chi2[best] + DELTA_CHI2
    k = best
    while 0 <= k + step < len(grid):
        if chi2[k + step] > level:
            g0, g1, c0, c1 = grid[k], grid[k + step], chi2[k], chi2[k + step]
            return float(g0 + (level - c0) * (g1 - g0) / (c1 - c0)), False
        k += step
    return float(grid[k]), True


def profile(
    model: Model,
    x: Array,
    y: Array,
    p0: Sequence[float],
    name: str,
    grid: Array,
    *,
    sigma: float,
    names: Sequence[str],
    bounds: tuple = (-np.inf, np.inf),
) -> Profile:
    """Chi-square as a function of one parameter, the others refitted at each value.

    The interval is where the profile is within ``DELTA_CHI2`` of its
    minimum. When it is not, on one side or on both, the data do not bound
    the parameter there and the result is marked open.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    names = list(names)
    index = names.index(name)
    grid = np.asarray(grid, dtype=float)
    others = [k for k in range(len(names)) if k != index]
    lower = np.broadcast_to(bounds[0], len(names))
    upper = np.broadcast_to(bounds[1], len(names))
    values = np.empty(len(grid))
    centre = int(np.argmin(np.abs(grid - np.asarray(p0, dtype=float)[index])))
    # Walk away from the starting value in both directions, each fit starting
    # from the previous one: a distant start can end in another minimum.
    for order in (range(centre, len(grid)), range(centre - 1, -1, -1)):
        start = np.asarray(p0, dtype=float)[others]
        for k in order:

            def residual(free, fixed=grid[k]):
                full = np.empty(len(names))
                full[index], full[others] = fixed, free
                return (y - model(x, *full)) / sigma

            fit = optimize.least_squares(
                residual, start, bounds=(lower[others], upper[others]), x_scale="jac"
            )
            values[k] = float(np.sum(fit.fun**2))
            start = fit.x
    best = int(np.argmin(values))
    low, open_low = _edge(grid, values, best, -1)
    high, open_high = _edge(grid, values, best, +1)
    return Profile(
        name, grid, values, float(grid[best]), low, high, open_low, open_high
    )


def residual_autocorrelation(residuals: Array) -> tuple[float, float]:
    """Lag-1 autocorrelation of the residuals, and its size in standard deviations.

    Residuals that are noise alone are uncorrelated, and the autocorrelation
    of ``n`` of them has a standard deviation of about ``1/sqrt(n)``. A fit
    whose residuals still carry a slow trend or a missing oscillation has a
    value far outside that.

    Only originally adjacent finite samples are paired, so a gap does not
    join its two sides. The result is ``(nan, nan)`` when too few finite
    residuals remain or they are constant: the diagnostic is then invalid.
    """
    r = np.asarray(residuals, dtype=float).ravel()
    finite = np.isfinite(r)
    pairs = finite[1:] & finite[:-1]
    n = int(finite.sum())
    if n < MIN_RESIDUALS or int(pairs.sum()) < MIN_RESIDUALS - 1:
        return float("nan"), float("nan")
    centred = r - r[finite].mean()
    denominator = float(np.sum(centred[finite] ** 2))
    if not denominator > 0.0 or np.ptp(r[finite]) <= 1e-12 * np.max(np.abs(r[finite])):
        return float("nan"), float("nan")
    rho = float(np.sum(centred[1:][pairs] * centred[:-1][pairs]) / denominator)
    return rho, rho * np.sqrt(n)


def verdict(result: FitResult) -> list[str]:
    """The reasons not to take the fit as evidence for its model; empty if none.

    A converged fit is not one: the optimiser stops at a minimum of a model
    that may be wrong, or that the data cannot pin down.
    """
    reasons = list(result.warnings)
    rho, z = residual_autocorrelation(result.residuals)
    if not np.isfinite(z):
        reasons.append(
            "the residual autocorrelation could not be calculated (too few"
            " finite residuals, or they are constant): the fit cannot be"
            " checked for leftover structure"
        )
    elif abs(z) > STRUCTURE_SIGMAS:
        reasons.append(
            f"the residuals are correlated (lag-1 autocorrelation {rho:.2f},"
            f" {abs(z):.0f} standard deviations from independent noise):"
            " the model leaves structure, or the noise is not independent"
        )
    return reasons
