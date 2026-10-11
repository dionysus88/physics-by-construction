"""A measured or modelled series that remembers what was done to it.

``Series`` carries the artifact type of its source and every step applied. Its
status is computed from both, so that smoothed or interpolated data cannot be
shown as raw: ``status`` turns ``measured`` into ``processed`` after the first
step, and ``disclosure`` lists the steps for the page and the figure.
"""

from dataclasses import dataclass, field, replace

import numpy as np

from pbc.data.status import status_of


@dataclass(frozen=True)
class Series:
    """``y`` (with optional standard uncertainty ``sigma``) against ``x``."""

    x: np.ndarray
    y: np.ndarray
    artifact: str
    sigma: np.ndarray | None = None
    x_name: str = "time"
    x_unit: str = "s"
    y_name: str = "value"
    y_unit: str = "1"
    steps: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self):
        if self.x.shape != self.y.shape:
            raise ValueError("x and y must have the same shape")
        if self.sigma is not None and self.sigma.shape != self.y.shape:
            raise ValueError("sigma and y must have the same shape")

    @property
    def status(self) -> str:
        return status_of(self.artifact, self.steps)

    @property
    def is_raw(self) -> bool:
        return not self.steps

    def disclosure(self) -> str:
        """The steps in plain words; empty for an untouched series."""
        return "; ".join(self.steps)

    def _derived(self, step: str, **changes) -> Series:
        return replace(self, steps=(*self.steps, step), **changes)

    def select(self, start: float, stop: float) -> Series:
        """The samples with ``start <= x <= stop``."""
        keep = (self.x >= start) & (self.x <= stop)
        sigma = None if self.sigma is None else self.sigma[keep]
        return self._derived(
            f"selected {start:g} to {stop:g} {self.x_unit}",
            x=self.x[keep],
            y=self.y[keep],
            sigma=sigma,
        )

    def drop_masked(self) -> Series:
        """Remove samples whose value is missing (NaN); say how many."""
        keep = np.isfinite(self.y)
        if keep.all():
            return self
        sigma = None if self.sigma is None else self.sigma[keep]
        return self._derived(
            f"removed {int((~keep).sum())} masked samples",
            x=self.x[keep],
            y=self.y[keep],
            sigma=sigma,
        )

    def smooth(self, width: int) -> Series:
        """Moving average over ``width`` samples (odd); uncertainty is dropped.

        The average correlates neighbouring samples, so the per-sample
        uncertainty no longer describes the result and is not carried over.
        """
        if width < 1 or width % 2 == 0:
            raise ValueError("width must be a positive odd number of samples")
        kernel = np.ones(width) / width
        smoothed = np.convolve(self.y, kernel, mode="same")
        edge = width // 2
        smoothed[:edge] = np.nan
        smoothed[len(smoothed) - edge :] = np.nan
        return self._derived(
            f"smoothed by a moving average of {width} samples", y=smoothed, sigma=None
        )

    def interpolate_to(self, x_new: np.ndarray) -> Series:
        """Linear interpolation onto ``x_new``; NaN outside the series.

        A value between two samples is ``(1 - a) y0 + a y1``. The samples are
        taken as independent, so its standard uncertainty is
        ``sqrt((1 - a)^2 s0^2 + a^2 s1^2)``: equal to the sample's own at a
        sample, and smaller in between. Samples that share an error (a common
        calibration offset, say) are correlated; for those this understates
        the uncertainty, by at most the difference to the linear interpolation
        of ``s0`` and ``s1``, and the lesson has to say so.
        """
        valid = np.isfinite(self.y)
        x, y_valid = self.x[valid], self.y[valid]
        x_new = np.asarray(x_new, dtype=float)
        y = np.interp(x_new, x, y_valid, left=np.nan, right=np.nan)
        sigma = None
        if self.sigma is not None:
            s = self.sigma[valid]
            if len(x) == 1:
                sigma = np.where(x_new == x[0], s[0], np.nan)
            else:
                upper = np.clip(np.searchsorted(x, x_new, side="right"), 1, len(x) - 1)
                lower = upper - 1
                a = (x_new - x[lower]) / (x[upper] - x[lower])
                sigma = np.sqrt(((1 - a) * s[lower]) ** 2 + (a * s[upper]) ** 2)
                sigma = np.where(np.isfinite(y), sigma, np.nan)
        return self._derived(
            "linearly interpolated onto a new grid",
            x=x_new,
            y=y,
            sigma=sigma,
        )
