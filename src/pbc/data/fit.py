"""Curve fitting with the diagnostics that say whether the result means anything.

``fit_curve`` is a least-squares fit that returns the parameters with standard
errors, the residuals, the reduced chi-square, and a statement of which
parameters the data can tell apart. A fit that converges is not a fit that
identifies its parameters: two parameters that only ever appear as a product
fit perfectly and mean nothing separately.
"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass

import numpy as np
from scipy import optimize

# Relative singular value below which a combination of parameters is treated
# as not determined by the data (after scaling each parameter by its size).
SLOPPY_RATIO = 1e-4
# A parameter takes part in a sloppy combination when its weight in the
# corresponding singular vector exceeds this.
SLOPPY_WEIGHT = 0.1


@dataclass(frozen=True)
class FitResult:
    names: tuple[str, ...]
    params: np.ndarray
    stderr: np.ndarray  # inf for a parameter that is not identified
    covariance: np.ndarray
    correlation: np.ndarray
    residuals: np.ndarray  # data minus model, in the units of the data
    chi2: float  # of the residuals scaled by sigma (1 when sigma is unknown)
    dof: int
    reduced_chi2: float
    singular_ratio: float  # smallest over largest singular value, scaled Jacobian
    identifiable: tuple[bool, ...]
    warnings: tuple[str, ...]
    absolute_sigma: bool

    def interval(self, name: str, k: float = 1.959964) -> tuple[float, float]:
        """Approximate coverage interval ``value +/- k * stderr`` of a parameter."""
        i = self.names.index(name)
        return (
            float(self.params[i] - k * self.stderr[i]),
            float(self.params[i] + k * self.stderr[i]),
        )

    def value(self, name: str) -> float:
        return float(self.params[self.names.index(name)])

    @property
    def ok(self) -> bool:
        return all(self.identifiable) and not self.warnings


def fit_curve(
    model: Callable[..., np.ndarray],
    x: np.ndarray,
    y: np.ndarray,
    p0: Sequence[float],
    *,
    sigma: np.ndarray | float | None = None,
    names: Sequence[str] | None = None,
    bounds: tuple = (-np.inf, np.inf),
) -> FitResult:
    """Fit ``model(x, *params)`` to ``y``.

    With ``sigma`` (standard uncertainty of ``y``) the covariance is the
    absolute one and ``reduced_chi2`` tests the fit: near 1 is consistent, much
    above 1 means the model or the uncertainties are wrong. Without it, the
    scatter of the residuals sets the covariance, and ``reduced_chi2`` is 1.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    p0 = np.asarray(p0, dtype=float)
    names = (
        tuple(names) if names is not None else tuple(f"p{k}" for k in range(len(p0)))
    )
    if len(names) != len(p0):
        raise ValueError("one name for each parameter")
    finite = np.isfinite(x) & np.isfinite(y)
    weights = np.ones_like(y) if sigma is None else np.broadcast_to(sigma, y.shape)
    weights = np.asarray(weights, dtype=float)
    finite &= np.isfinite(weights) & (weights > 0)
    x, y, weights = x[finite], y[finite], weights[finite]
    if y.size <= p0.size:
        raise ValueError("fewer finite samples than parameters")

    def scaled(p):
        return (y - model(x, *p)) / weights

    fit = optimize.least_squares(scaled, p0, bounds=bounds, x_scale="jac")
    jac = fit.jac
    warnings: list[str] = []
    if not fit.success:
        warnings.append(f"the optimiser did not converge: {fit.message}")

    # Identifiability: scale each parameter by its size, so that the singular
    # values compare relative changes of the parameters.
    size = np.where(np.abs(fit.x) > 0, np.abs(fit.x), 1.0)
    _, singular, vt = np.linalg.svd(jac * size, full_matrices=False)
    ratio = float(singular[-1] / singular[0]) if singular[0] > 0 else 0.0
    sloppy = singular / singular[0] < SLOPPY_RATIO if singular[0] > 0 else singular < 1
    identifiable = np.ones(len(p0), dtype=bool)
    for k in np.flatnonzero(sloppy):
        identifiable &= np.abs(vt[k]) <= SLOPPY_WEIGHT
    if not identifiable.all():
        bad = [n for n, ok in zip(names, identifiable, strict=True) if not ok]
        warnings.append(
            "the data do not determine " + ", ".join(bad) + " separately"
            " (a combination of them is not constrained)"
        )

    dof = y.size - p0.size
    chi2 = float(np.sum(fit.fun**2))
    reduced = chi2 / dof
    absolute = sigma is not None
    inverse = np.linalg.pinv(jac.T @ jac, rcond=1e-12)
    # Scale of the covariance from the scatter when sigma is unknown.
    covariance = inverse if absolute else inverse * reduced
    stderr = np.sqrt(np.clip(np.diag(covariance), 0, None))
    stderr = np.where(identifiable, stderr, np.inf)
    with np.errstate(divide="ignore", invalid="ignore"):
        correlation = covariance / np.outer(stderr, stderr)
    correlation = np.where(np.isfinite(correlation), correlation, np.nan)
    if absolute and not 0.1 < reduced < 3.0:
        warnings.append(
            f"reduced chi-square {reduced:.2f}: the model or the uncertainties"
            " do not describe the scatter"
        )
    return FitResult(
        names=names,
        params=fit.x,
        stderr=stderr,
        covariance=covariance,
        correlation=correlation,
        residuals=y - model(x, *fit.x),
        chi2=chi2 if absolute else float(np.sum(fit.fun**2)),
        dof=dof,
        reduced_chi2=reduced if absolute else 1.0,
        singular_ratio=ratio,
        identifiable=tuple(bool(v) for v in identifiable),
        warnings=tuple(warnings),
        absolute_sigma=absolute,
    )
