"""Calibration and mask handling for measured arrays.

A mask says which samples hold no measurement. These helpers turn the ways a
source writes one (a sentinel such as 0 in processed PIV fields, NaN in a text
column, an explicit flag array) into NaN, so every later step sees one rule,
and they report how much of a record is valid so that the page can say so.
"""

import numpy as np

from pbc.data.uncertainty import propagate


def mask_to_nan(
    values: np.ndarray,
    *,
    sentinel: float | None = None,
    invalid: np.ndarray | None = None,
) -> np.ndarray:
    """Copy of ``values`` as floats with masked samples set to NaN.

    ``sentinel`` marks samples equal to it; ``invalid`` is a boolean array that
    is true where the sample is missing. Existing NaN stays NaN.
    """
    out = np.array(values, dtype=float)
    if sentinel is not None:
        out[out == sentinel] = np.nan
    if invalid is not None:
        if invalid.shape != out.shape:
            raise ValueError("the flag array must have the shape of the values")
        out[invalid] = np.nan
    return out


def valid_fraction(values: np.ndarray) -> float:
    """Fraction of finite samples."""
    return float(np.isfinite(values).mean())


def apply_gain_offset(
    counts: np.ndarray | float,
    gain: float,
    offset: float = 0.0,
    sigma_gain: float = 0.0,
    sigma_offset: float = 0.0,
    sigma_counts: np.ndarray | float = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    """``gain * counts + offset`` with the standard uncertainty it inherits."""
    return propagate(
        lambda c, g, o: g * c + o,
        [counts, gain, offset],
        [sigma_counts, sigma_gain, sigma_offset],
    )
