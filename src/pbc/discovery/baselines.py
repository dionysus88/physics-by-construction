"""Baselines without an agent, on the same environment with the same budget.

Each baseline probes the environment through ``measure`` only, as an agent
would, and then fits. A baseline reports ``success`` only when its fit is
consistent with the noise (``FIT_SIGMAS``, as in ``pbc.agents.design``) and
its parameters are determined; otherwise it reports the reason, and the
claim it ends with is not a result.
"""

import itertools
import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from pbc.data.fit import fit_curve
from pbc.discovery.environment import Environment, library

Array = NDArray[np.float64]
# Chi-square within this many standard deviations of its expectation fits.
FIT_SIGMAS = 3.0


@dataclass(frozen=True)
class Dataset:
    """What a probing strategy measured."""

    settings: tuple[Mapping[str, float], ...]
    values: Array
    sigma: float


@dataclass(frozen=True)
class BaselineResult:
    """The outcome of one baseline. ``claim`` is ``None`` when it found none;
    ``held_out_error`` is the judge's score of it."""

    name: str
    probes: int
    success: bool
    claim: Mapping[str, float] | None
    held_out_error: float
    reason: str


def _probe(
    environment: Environment, settings: Sequence[Mapping[str, float]]
) -> Dataset:
    environment.reset()
    values = [environment.measure(**s)[environment.observation.name] for s in settings]
    return Dataset(tuple(settings), np.array(values), environment.observation.sigma)


def random_probe(environment: Environment, seed: int = 0) -> Dataset:
    """Spend the whole budget at settings drawn uniformly within the bounds."""
    rng = np.random.default_rng(seed)
    settings = [
        {c.name: float(rng.uniform(c.low, c.high)) for c in environment.controls}
        for _ in range(environment.budget)
    ]
    return _probe(environment, settings)


def grid_probe(environment: Environment) -> Dataset:
    """Spend the whole budget on a regular grid over the bounds: as many points
    per control as the budget allows, then the remainder on distinct points of
    the next finer grids, spread evenly over each."""
    controls = environment.controls
    n = max(1, int(environment.budget ** (1 / len(controls)) + 1e-9))

    def grid(points: int) -> list[tuple[float, ...]]:
        axes = [np.linspace(c.low, c.high, points) for c in controls]
        return [tuple(map(float, p)) for p in itertools.product(*axes)]

    base = grid(n)
    for points in itertools.count(n + 1):
        need = environment.budget - len(base)
        if need <= 0:
            break
        fresh = [
            p
            for p in grid(points)
            if not any(np.allclose(p, q, rtol=0, atol=1e-12) for q in base)
        ]
        # Evenly spaced indices are distinct when at least ``need`` are on offer.
        picks = (
            np.linspace(0, len(fresh) - 1, min(need, len(fresh))).round().astype(int)
        )
        base += [fresh[i] for i in picks]
    names = [c.name for c in controls]
    settings = [dict(zip(names, p, strict=True)) for p in base]
    return _probe(environment, settings)


def consistent(chi2: float, dof: int) -> bool:
    """Is the chi-square what the noise alone gives, for ``dof`` degrees of
    freedom?"""
    return dof > 0 and chi2 <= dof + FIT_SIGMAS * math.sqrt(2 * dof)


def _failed(name: str, data: Dataset, reason: str) -> BaselineResult:
    return BaselineResult(name, len(data.settings), False, None, math.inf, reason)


def least_squares(
    environment: Environment, data: Dataset, name: str = "least-squares"
) -> BaselineResult:
    """Fit the environment's public family to ``data`` with
    ``pbc.data.fit.fit_curve``, from each of its starts, and keep the best."""
    names = tuple(c.name for c in environment.claim)
    bounds = (
        [c.low for c in environment.claim],
        [c.high for c in environment.claim],
    )
    if len(data.settings) <= len(names):
        return _failed(name, data, "fewer probes than parameters")

    def curve(index: Array, *params: float) -> Array:
        claim = dict(zip(names, params, strict=True))
        return np.array(
            [environment.predict(claim, data.settings[int(i)]) for i in index]
        )

    best = None
    for start in environment.starts:
        try:
            fit = fit_curve(
                curve,
                np.arange(len(data.values), dtype=float),
                data.values,
                start,
                sigma=data.sigma,
                names=names,
                bounds=bounds,
            )
        except ValueError:
            continue
        if best is None or fit.chi2 < best.chi2:
            best = fit
    if best is None:
        return _failed(name, data, "no fit could be made")
    claim = dict(zip(names, map(float, best.params), strict=True))
    error = environment.held_out_error(claim)
    if not consistent(best.chi2, best.dof):
        reason = (
            f"chi-square {best.chi2:.3g} for {best.dof} degrees of freedom: the"
            " family does not describe the measurements"
        )
    elif not all(best.identifiable):
        reason = "the data do not determine the parameters separately"
    else:
        reason = ""
    return BaselineResult(name, len(data.settings), not reason, claim, error, reason)


def sparse_identification(
    environment: Environment,
    data: Dataset,
    library: Mapping[str, Callable[[Mapping[str, float]], float]],
    threshold: float = 0.2,
    name: str = "sparse-identification",
) -> BaselineResult:
    """Sequentially thresholded least squares over a library of terms: fit the
    coefficients, drop those smaller than ``threshold`` times the largest, and
    fit the rest again.

    It finds a law only if the law is a sum of the library's terms; for one
    that is not, the best sparse sum does not fit and the result says so."""
    if not library:
        return _failed(name, data, "the environment has no library of terms")
    terms = list(library)
    design = (
        np.array([[library[t](s) for t in terms] for s in data.settings]) / data.sigma
    )
    target = data.values / data.sigma
    active = np.ones(len(terms), dtype=bool)
    coefficients = np.zeros(len(terms))
    for _ in range(10):
        if not active.any():
            break
        coefficients[:] = 0.0
        coefficients[active], *_ = np.linalg.lstsq(
            design[:, active], target, rcond=None
        )
        small = active & (np.abs(coefficients) < threshold * np.abs(coefficients).max())
        if not small.any():
            break
        active &= ~small
    coefficients[~active] = 0.0
    chi2 = float(np.sum((target - design @ coefficients) ** 2))
    dof = len(target) - int(active.sum())
    claim = {t: float(c) for t, c in zip(terms, coefficients, strict=True) if c != 0.0}

    def predict(settings: Mapping[str, float]) -> float:
        return sum(c * library[t](settings) for t, c in claim.items())

    error = environment.score_predictor(predict)
    reason = ""
    if not claim:
        reason = "no term of the library survives the threshold"
    elif not consistent(chi2, dof):
        reason = (
            f"chi-square {chi2:.3g} for {dof} degrees of freedom: no sparse sum"
            " of the library's terms describes the measurements"
        )
    return BaselineResult(
        name, len(data.settings), not reason, claim or None, error, reason
    )


def run_baselines(
    environment: Environment, seed: int = 0
) -> tuple[BaselineResult, ...]:
    """Every baseline on ``environment`` with its budget: least squares on a
    grid and on random probes, and sparse identification on the grid."""
    grid = grid_probe(environment)
    scattered = random_probe(environment, seed)
    terms = library(environment)
    results = (
        least_squares(environment, grid, "grid + least squares"),
        least_squares(environment, scattered, "random + least squares"),
        sparse_identification(
            environment, grid, terms, name="grid + sparse identification"
        ),
    )
    environment.reset()
    return results
