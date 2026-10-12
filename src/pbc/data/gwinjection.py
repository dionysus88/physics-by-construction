"""Injection into off-source noise: the control for the chirp fit of the lab.

A known chirp is added, whitened like the data, to stretches of the strain
where no event is, and the fit of ``pbc.data.gwstrain`` is run on each. The
spread of the recovered chirp mass over the stretches is the scatter of the
method on this noise, to set against the interval the fit states.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from pbc.data.gwosc import EVENT_GPS, Strain
from pbc.data.gwstrain import (
    Segment,
    fit_chirp,
    make_whitener,
    noise_sigma,
)
from pbc.mechanics.chirp import chirp_waveform

Array = NDArray[np.float64]


@dataclass(frozen=True)
class Injection:
    centre: float  # s since the event time, the middle of the stretch used as noise
    mc: float  # recovered chirp mass
    low: float  # stated 68 % interval
    high: float
    at_edge: bool

    def covers(self, truth: float) -> bool:
        return self.low <= truth <= self.high


def off_source_segment(
    strain: Strain, centre: float, half_width: float = 0.75
) -> Segment:
    """``2 * half_width`` seconds around ``centre``, timed from ``centre``."""
    time = strain.time - EVENT_GPS - centre
    keep = np.abs(time) < half_width
    return Segment(strain.detector, time[keep], strain.strain[keep], strain.sample_rate)


def inject_and_fit(
    strains: Mapping[str, Strain],
    centres: Sequence[float],
    *,
    truth_mc: float,
    truth_tc: float,
    delays: Mapping[str, float],
    peak: Mapping[str, float],
    band: tuple[float, float],
    window: tuple[float, float] = (-0.2, 0.0),
    mc_grid: Array | None = None,
    phase: float = 0.4,
) -> list[Injection]:
    """Fit a chirp of known parameters added to the noise around each of ``centres``.

    ``peak`` is the largest whitened value of the injected model in each
    detector inside ``window``, in the units of the whitened data; the fitted
    model of the measurement gives the size of the real signal.
    """
    out = []
    grid = np.arange(24.0, 48.0, 1.0) if mc_grid is None else mc_grid
    for centre in centres:
        segments = {n: off_source_segment(s, centre) for n, s in strains.items()}
        whiteners = {n: make_whitener(strains[n], segments[n], band) for n in strains}
        name = next(iter(strains))
        time = segments[name].time
        data = {n: whiteners[n](segments[n].strain) for n in strains}
        sigma = noise_sigma(data[name], time, (0.3, 0.65))
        inside = (time >= window[0]) & (time <= window[1])
        for n in strains:
            template = whiteners[n](
                chirp_waveform(time, truth_mc, truth_tc + delays[n], 1.0, phase)
            )
            data[n] = data[n] + peak[n] * template / np.max(np.abs(template[inside]))
        fit = fit_chirp(
            time, data, whiteners, delays, window=window, sigma=sigma, mc_grid=grid
        )
        out.append(Injection(centre, fit.mc, fit.mc_low, fit.mc_high, fit.at_edge))
    return out
