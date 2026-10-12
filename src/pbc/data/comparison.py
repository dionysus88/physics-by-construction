"""The data of the waveform comparator, a browser component of the labs.

The component draws a measured series against a family of model profiles and
reads out the error metrics of each. It computes nothing: this module computes
both, from the lab's own code, and the page embeds the result as JSON. The
measured series is stored as it is given (rounded to ``DECIMALS`` places, far
below the noise), never smoothed or resampled.
"""

from collections.abc import Mapping, Sequence

import numpy as np
from numpy.typing import NDArray

from pbc.data.gwstrain import ModelAtMass

Array = NDArray[np.float64]

DECIMALS = 5  # places kept of a whitened sample, whose noise is of order one
SCHEMA = "waveform-comparison-1"


def _round(values: Array) -> list[float]:
    return [float(v) for v in np.round(values, DECIMALS)]


def waveform_comparison(
    time: Array,
    measured: Array,
    models: Sequence[ModelAtMass],
    detector: str,
    *,
    sigma: float,
    window: tuple[float, float],
    show: tuple[float, float],
    quantity: str,
    unit: str,
    best: float,
) -> Mapping[str, object]:
    """The comparison of ``measured`` with each of ``models`` for the
    detector ``detector``, over the times ``show``.

    ``window`` is the part the models were fitted to, and ``best`` the trial
    value of the parameter (a mass) of the overall best fit. The metrics are
    those of ``ModelAtMass``, over both detectors, as the fit sees them.
    """
    keep = (time >= show[0]) & (time <= show[1])
    return {
        "schema": SCHEMA,
        "detector": detector,
        "quantity": quantity,
        "unit": unit,
        "time_unit": "s",
        "sigma": round(sigma, DECIMALS),
        "window": list(window),
        "best_parameter": best,
        "parameter": {"name": "chirp mass, detector frame", "unit": "solar masses"},
        "time": _round(time[keep]),
        "measured": _round(measured[keep]),
        "models": [
            {
                "parameter": round(m.mc, 3),
                "coalescence_time": round(m.t_c, 5),
                "metrics": {
                    "chi2": round(m.chi2, 2),
                    "reduced_chi2": round(m.reduced_chi2, 3),
                    "rms_residual": round(m.rms_residual, 4),
                    "correlation": round(m.correlation, 4),
                },
                "values": _round(m.model[detector][keep]),
                "residual": _round((measured - m.model[detector])[keep]),
            }
            for m in models
        ],
    }
