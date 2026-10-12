"""Processing of the GW150914 strain for the gravitational-wave lab.

Everything here starts from the calibrated strain of ``pbc.data.gwosc`` and
says what it does: a Welch estimate of the noise spectrum, whitening by it,
a band-pass, a cross-correlation of the two detectors with an off-source
control, and a least-squares fit of the Newtonian chirp of
``pbc.mechanics.chirp`` to the whitened strain. A whitened series is a
processed series, not a measurement; a fitted waveform is a model, drawn apart.
"""

from collections.abc import Mapping
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy import optimize, signal

from pbc.data.fit import FitResult, fit_curve
from pbc.data.gwosc import EVENT_GPS, Strain
from pbc.mechanics.chirp import chirp_waveform

Array = NDArray[np.float64]

MAX_LAG = 0.010  # s, the light travel time between the two sites, as an upper bound
T_C_EDGE = (
    0.055  # s, a coalescence time this late is the end of the search, not a result
)
HALF_WIDTH = 2.0  # s, the default segment around the event that is whitened


@dataclass(frozen=True)
class Segment:
    """A stretch of strain around the event, with time measured from the event."""

    detector: str
    time: Array  # s since EVENT_GPS
    strain: Array  # dimensionless
    sample_rate: float


def cut_segment(strain: Strain, half_width: float = HALF_WIDTH) -> Segment:
    """The ``2 * half_width`` seconds of strain centred on the catalogue event time."""
    time = strain.time - EVENT_GPS
    keep = np.abs(time) < half_width
    return Segment(strain.detector, time[keep], strain.strain[keep], strain.sample_rate)


def amplitude_spectrum(strain: Strain, seconds: float = 4.0) -> tuple[Array, Array]:
    """Welch estimate of the amplitude spectral density, in 1/sqrt(Hz).

    Averages the periodograms of overlapping stretches of ``seconds`` seconds
    over the whole 32 s of the file, which includes the event: the signal is
    a tiny part of the 32 s, so the estimate is the detector noise.
    """
    freqs, psd = signal.welch(
        strain.strain, strain.sample_rate, nperseg=int(seconds * strain.sample_rate)
    )
    return freqs, np.sqrt(psd)


@dataclass(frozen=True)
class Whitener:
    """Divides the spectrum of a segment by the noise spectrum, then band-passes.

    The operation is linear, so a model can be passed through the same filter
    as the data, which is how the fit compares them.
    """

    amplitude: Array  # noise amplitude spectral density on the rfft grid of the segment
    window: Array
    sos: Array
    sample_rate: float
    band: tuple[float, float]

    def __call__(self, x: Array) -> Array:
        spectrum = np.fft.rfft(np.asarray(x) * self.window)
        white = np.fft.irfft(spectrum / self.amplitude, n=np.shape(x)[-1])
        out = signal.sosfiltfilt(self.sos, white)
        return out * np.sqrt(2.0 / self.sample_rate)


def make_whitener(
    strain: Strain, segment: Segment, band: tuple[float, float]
) -> Whitener:
    """A whitener for ``segment`` from the noise spectrum of the whole ``strain``."""
    n = len(segment.strain)
    freqs, asd = amplitude_spectrum(strain)
    grid = np.fft.rfftfreq(n, 1.0 / segment.sample_rate)
    sos = signal.butter(4, band, btype="bandpass", fs=segment.sample_rate, output="sos")
    return Whitener(
        amplitude=np.interp(grid, freqs, asd),
        window=signal.windows.tukey(n, alpha=0.1),
        sos=sos,
        sample_rate=segment.sample_rate,
        band=band,
    )


def noise_sigma(whitened: Array, time: Array, quiet: tuple[float, float]) -> float:
    """Standard deviation of a whitened segment where ``quiet[0] < |t| < quiet[1]``.

    Choose the range away from the event and from the tapered edges of the
    segment; it estimates the noise of one whitened sample.
    """
    keep = (np.abs(time) > quiet[0]) & (np.abs(time) < quiet[1])
    return float(np.std(whitened[keep]))


def correlation(a: Array, b: Array) -> float:
    """Pearson correlation of two equally long series."""
    a = a - a.mean()
    b = b - b.mean()
    return float(a @ b / np.sqrt((a @ a) * (b @ b)))


def best_lag(
    h1: Array, l1: Array, time: Array, centre: float, half: float, rate: float
) -> tuple[float, float]:
    """Lag of L1 against H1 that maximises ``|correlation|`` and its value.

    ``l1`` is shifted by up to ``MAX_LAG`` either way. The window is
    ``centre +- half`` in ``time``. Returns ``(lag, correlation)`` with the
    lag in seconds; a negative lag means the feature is seen in L1 first.
    """
    steps = round(MAX_LAG * rate)
    lo = np.searchsorted(time, centre - half)
    hi = lo + round(2 * half * rate)
    best = (0.0, 0.0)
    for k in range(-steps, steps + 1):
        c = correlation(h1[lo:hi], l1[lo + k : hi + k])
        if abs(c) > abs(best[1]):
            best = (k / rate, c)
    return best


def correlation_with_control(
    h1: Array,
    l1: Array,
    time: Array,
    rate: float,
    *,
    half: float = 0.1,
    event_centre: float = 0.0,
) -> dict:
    """The H1-L1 correlation at the event and in every off-source window.

    Each window is ``2 * half`` long and gets the same search over lags. The
    off-source windows tile the quiet part of the segment (away from the
    event and from the edges of the filter), so their correlations say how
    large a chance correlation of two noise streams is under this procedure.
    """
    lag, value = best_lag(h1, l1, time, event_centre, half, rate)
    centres = np.arange(-1.5 + half, 1.5 - half, 2 * half)
    controls = [
        best_lag(h1, l1, time, c, half, rate)[1] for c in centres if abs(c) > 0.5 + half
    ]
    return {
        "lag": lag,
        "correlation": value,
        "controls": np.abs(np.array(controls)),
        "window": 2 * half,
    }


@dataclass(frozen=True)
class ChirpFit:
    """Result of fitting the Newtonian chirp to the whitened H1 and L1 segments."""

    mc: float  # solar masses, detector frame
    mc_low: float  # lower end of the 68 % interval from the profile
    mc_high: float
    t_c: float
    fit: FitResult
    profile_mc: Array
    profile_chi2: Array
    reduced_chi2: float
    n_samples: int
    models: Mapping[str, Array]  # whitened best-fit model per detector, whole segment
    window: tuple[float, float]
    band: tuple[float, float]
    at_edge: bool  # the minimum sits at the edge of the search: not determined

    @property
    def interval(self) -> tuple[float, float]:
        return (self.mc_low, self.mc_high)


def _design(
    time: Array,
    whiteners: Mapping[str, Whitener],
    delays: Mapping[str, float],
    mc: float,
    t_c: float,
) -> dict[str, Array]:
    """Whitened cosine and sine templates, columns, of each detector."""
    out = {}
    for name, white in whiteners.items():
        t_c_here = t_c + delays[name]
        both = np.stack(
            [
                chirp_waveform(time, mc, t_c_here, 1.0, 0.0),
                chirp_waveform(time, mc, t_c_here, 0.0, 1.0),
            ]
        )
        out[name] = white(both).T
    return out


def _solve(
    design: Mapping[str, Array],
    data: Mapping[str, Array],
    keep: NDArray[np.bool_],
) -> dict[str, Array]:
    """Best amplitude pair of each detector; the projection of the linear part."""
    return {
        name: np.linalg.lstsq(design[name][keep], data[name][keep], rcond=None)[0]
        for name in design
    }


def fit_chirp(
    time: Array,
    data: Mapping[str, Array],
    whiteners: Mapping[str, Whitener],
    delays: Mapping[str, float],
    *,
    window: tuple[float, float],
    sigma: float,
    mc_grid: Array | None = None,
) -> ChirpFit:
    """Least-squares fit of ``chirp_waveform`` to the whitened detectors.

    The chirp mass and the coalescence time are common to the detectors; each
    detector has its own amplitude pair (the antenna pattern and the sign are
    not assumed) and its own arrival delay from ``delays`` (seconds, added to
    the coalescence time). This is the convention of ``best_lag``: the lag of
    L1 against H1, negative when L1 sees the wave first.
    Only samples inside ``window`` enter. ``sigma`` is the standard deviation
    of the noise of one whitened sample.

    The 68 % interval is where the profile ``chi2`` over the chirp mass, with
    the coalescence time minimised at each mass, is within one of its minimum.
    """
    keep = (time >= window[0]) & (time <= window[1])
    names = list(whiteners)
    y = np.concatenate([data[n][keep] for n in names])

    def predict(mc: float, t_c: float) -> dict[str, Array]:
        design = _design(time, whiteners, delays, mc, t_c)
        amplitudes = _solve(design, data, keep)
        return {n: design[n] @ amplitudes[n] for n in names}

    def chi2(mc: float, t_c: float) -> float:
        model = predict(mc, t_c)
        return float(sum(np.sum((data[n][keep] - model[n][keep]) ** 2) for n in names))

    t_grid = np.arange(0.010, 0.062, 0.002)

    def refine(mc: float, trial: Array) -> tuple[float, float]:
        coarse = [chi2(mc, t) for t in trial]
        k = int(np.argmin(coarse))
        lo, hi = trial[max(k - 1, 0)], trial[min(k + 1, len(trial) - 1)]
        found = optimize.minimize_scalar(
            lambda t: chi2(mc, t),
            bounds=(lo, hi),
            method="bounded",
            options={"xatol": 1e-5},
        )
        # A search that did not converge, or that ended above the grid point
        # it started from, is not used: the grid point stands.
        if found.success and np.isfinite(found.fun) and found.fun <= coarse[k]:
            return float(found.fun), float(found.x)
        return float(coarse[k]), float(trial[k])

    grid = np.arange(20.0, 56.0, 1.0) if mc_grid is None else np.asarray(mc_grid)
    # The best coalescence time has several local minima, so a first pass
    # searches the whole range at a few masses; the profile then walks away
    # from the best of them, each mass starting near the previous one.
    seeds = grid[:: max(1, len(grid) // 12)]
    seed_points = [(m, *refine(m, t_grid)) for m in seeds]
    start = int(np.argmin([p[1] for p in seed_points]))
    centre = int(np.argmin(np.abs(grid - seed_points[start][0])))
    points: list[tuple[float, float] | None] = [None] * len(grid)
    points[centre] = refine(grid[centre], t_grid)
    for order in (range(centre + 1, len(grid)), range(centre - 1, -1, -1)):
        previous = points[centre][1]
        for k in order:
            trial = np.arange(previous - 0.006, previous + 0.0061, 0.002)
            points[k] = refine(grid[k], trial)
            previous = points[k][1]
    profile = np.array([p[0] for p in points]) / sigma**2
    best = int(np.argmin(profile))

    def model_vector(_x, mc, t_c):
        model = predict(mc, t_c)
        return np.concatenate([model[n][keep] for n in names])

    result = fit_curve(
        model_vector,
        np.arange(y.size, dtype=float),
        y,
        [grid[best], points[best][1]],
        sigma=sigma,
        names=["chirp mass", "coalescence time"],
        bounds=([5.0, 0.0], [120.0, 0.1]),
    )
    mc, t_c = result.params
    low, high = _interval(grid, profile, best)
    full = predict(mc, t_c)
    return ChirpFit(
        mc=float(mc),
        mc_low=low,
        mc_high=high,
        t_c=float(t_c),
        fit=result,
        profile_mc=grid,
        profile_chi2=profile,
        reduced_chi2=result.reduced_chi2,
        n_samples=int(y.size),
        models=full,
        window=window,
        band=next(iter(whiteners.values())).band,
        at_edge=bool(best in (0, len(grid) - 1) or t_c > T_C_EDGE),
    )


def _crossing(g0: float, p0: float, g1: float, p1: float, level: float) -> float:
    """The mass where the line from ``(g0, p0)`` to ``(g1, p1)`` meets ``level``."""
    return g0 + (level - p0) * (g1 - g0) / (p1 - p0)


def _interval(grid: Array, profile: Array, best: int) -> tuple[float, float]:
    """Where the profile is within one of its minimum, by linear interpolation."""
    level = profile[best] + 1.0
    low = grid[0]
    for k in range(best, 0, -1):
        if profile[k - 1] > level:
            low = _crossing(grid[k], profile[k], grid[k - 1], profile[k - 1], level)
            break
    high = grid[-1]
    for k in range(best, len(grid) - 1):
        if profile[k + 1] > level:
            high = _crossing(grid[k], profile[k], grid[k + 1], profile[k + 1], level)
            break
    return float(low), float(high)


@dataclass(frozen=True)
class ModelAtMass:
    """The best chirp of one trial chirp mass, with the error metrics of its
    comparison with the whitened data inside the fit window."""

    mc: float  # solar masses, detector frame
    t_c: float  # s, the coalescence time that minimises the chi-square at this mass
    chi2: float  # whitened residuals over ``sigma``, both detectors
    reduced_chi2: float  # per sample of the window, both detectors
    rms_residual: float  # whitened units, both detectors
    correlation: float  # of data and model inside the window, both detectors
    model: Mapping[str, Array]  # whitened best-fit model per detector, whole segment


def models_at_masses(
    time: Array,
    data: Mapping[str, Array],
    whiteners: Mapping[str, Whitener],
    delays: Mapping[str, float],
    masses: Array,
    *,
    window: tuple[float, float],
    sigma: float,
    mc_start: float,
    t_c_start: float,
    t_c_reach: float = 0.003,
) -> list[ModelAtMass]:
    """The best-fit chirp at each of ``masses``, for comparison with the data.

    This is the model of ``fit_chirp`` with the chirp mass fixed: at each mass
    the amplitude pair of each detector is solved linearly and the coalescence
    time is the one that minimises the chi-square. The chi-square has a sharp
    minimum in the coalescence time and several of them, a period of the wave
    apart, so the search starts from the fitted pair (``mc_start``,
    ``t_c_start``) and walks outward in mass, each mass searching within
    ``t_c_reach`` of the time found at the nearest mass already done, on a
    fine grid and then by a bounded search. At the fitted mass it gives the
    chi-square of that fit.
    """
    keep = (time >= window[0]) & (time <= window[1])
    names = list(whiteners)

    def evaluate(mc: float, t_c: float):
        design = _design(time, whiteners, delays, mc, t_c)
        amplitudes = _solve(design, data, keep)
        model = {n: design[n] @ amplitudes[n] for n in names}
        chi2 = float(sum(np.sum((data[n][keep] - model[n][keep]) ** 2) for n in names))
        return chi2, model

    measured = np.concatenate([data[n][keep] for n in names])
    solved: dict[float, ModelAtMass] = {}
    anchors = {float(mc_start): t_c_start}
    for mc in sorted(np.asarray(masses, dtype=float), key=lambda m: abs(m - mc_start)):
        mc = float(mc)
        near = min(anchors, key=lambda a: abs(a - mc))
        trial = np.arange(
            anchors[near] - t_c_reach, anchors[near] + t_c_reach + 1e-9, 0.0001
        )
        coarse = [evaluate(mc, t)[0] for t in trial]
        k = int(np.argmin(coarse))
        found = optimize.minimize_scalar(
            lambda t_c, mc=mc: evaluate(mc, t_c)[0],
            bounds=(trial[max(k - 1, 0)], trial[min(k + 1, len(trial) - 1)]),
            method="bounded",
            options={"xatol": 1e-7},
        )
        # The grid point stands unless the bounded search succeeded, gave a
        # finite chi-square, and did not end above the point it started from.
        refined = found.success and np.isfinite(found.fun) and found.fun <= coarse[k]
        t_best = float(found.x) if refined else float(trial[k])
        chi2, model = evaluate(mc, t_best)
        modelled = np.concatenate([model[n][keep] for n in names])
        anchors[mc] = t_best
        solved[mc] = ModelAtMass(
            mc=mc,
            t_c=t_best,
            chi2=chi2 / sigma**2,
            reduced_chi2=chi2 / sigma**2 / measured.size,
            rms_residual=float(np.sqrt(chi2 / measured.size)),
            correlation=correlation(measured, modelled),
            model=model,
        )
    return [solved[float(m)] for m in np.asarray(masses, dtype=float)]
