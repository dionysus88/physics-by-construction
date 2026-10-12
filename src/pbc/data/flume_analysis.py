"""An analysis pipeline for a measured problem: waves over a submerged bar.

Gauge 5 of wave condition 1 of the committed sample (dataset
``aalborg-submerged-bar``) holds five aligned repetitions of the surface
elevation, their mean, and three numerical runs of the same experiment. The
pipeline cuts the same window from every record, computes the RMS elevation
and the dominant wave period of each repetition, takes the mean of the
repetitions with its standard error, sweeps the end of the window to see how
much the result depends on that choice, and compares each run with the
measurement in units of the combined standard uncertainty.

Elevations are in m, times in s. The repetitions are the *processed-measured*
artifact of the card (aligned on gauge 1), the runs the *modelled-reference*
one; nothing here merges them.
"""

from pathlib import Path

import numpy as np

from pbc.data import SAMPLES_DIR
from pbc.data.flume import Elevation, read_elevation
from pbc.data.pipeline import Estimate, Report, Sweep, estimate, sweep
from pbc.data.uncertainty import normalised_difference

DATA_DIR = SAMPLES_DIR / "aalborg-submerged-bar"
GAUGE = 5
WINDOW = (5.0, 14.0)  # s; the steady wave train that the three runs also cover
EXPERIMENT = "Exp_WC1_gauge05_surfaceElevation.csv"
MODELS = {  # label: file of the committed sample
    "i-VoF (OpenFOAM)": "iVoF_WC1_gauge05_surfaceElevation_A.csv",
    "M-sigma (MIKE 3)": "Msigma_WC1_gauge05_surfaceElevation_A.csv",
    "D-SPH (DualSPHysics)": "DSPH_WC1_gauge05_surfaceElevation_A.csv",
}
REPETITIONS = tuple(f"rep {k}" for k in range(1, 6))
WINDOW_ENDS = (8.0, 10.0, 12.0, 14.0)  # s; the start is WINDOW[0]
PADDING = 2**16  # samples of the zero-padded spectrum


def rms_elevation(time: np.ndarray, values: np.ndarray, window: tuple[float, float]):
    """RMS of the elevation about its mean inside ``window`` (m); NaN is skipped."""
    inside = (time >= window[0]) & (time <= window[1]) & np.isfinite(values)
    x = values[inside]
    return float(np.sqrt(np.mean((x - x.mean()) ** 2)))


def wave_period(time: np.ndarray, values: np.ndarray, window: tuple[float, float]):
    """Period (s) of the strongest spectral line inside ``window``.

    A Hann window and a zero-padded spectrum, so that the line is placed
    between the bins of the raw spectrum; the resolution is still limited by
    the length of the window, about one over its length in frequency.
    """
    inside = (time >= window[0]) & (time <= window[1]) & np.isfinite(values)
    x = values[inside] - values[inside].mean()
    dt = float(np.median(np.diff(time[inside])))
    spectrum = np.abs(np.fft.rfft(x * np.hanning(x.size), n=PADDING))
    frequency = np.fft.rfftfreq(PADDING, dt)
    return float(1.0 / frequency[1:][np.argmax(spectrum[1:])])


def load(data_dir: Path = DATA_DIR) -> tuple[Elevation, dict[str, Elevation]]:
    """The experiment and the three numerical runs of the committed sample."""
    experiment = read_elevation(Path(data_dir) / EXPERIMENT)
    models = {k: read_elevation(Path(data_dir) / f) for k, f in MODELS.items()}
    return experiment, models


def period_resolution(period: float, window: tuple[float, float]) -> float:
    """Smallest difference of two periods that a window can tell apart (s).

    A window of length ``L`` resolves frequencies about ``1 / L`` apart; at
    the frequency ``1 / T`` that is ``T**2 / L`` in period.
    """
    return period**2 / (window[1] - window[0])


def repetition_results(experiment: Elevation, window: tuple[float, float]):
    """RMS and period of each of the five repetitions, as two lists."""
    records = [experiment.column(GAUGE, name) for name in REPETITIONS]
    rms = [rms_elevation(experiment.time, r, window) for r in records]
    period = [wave_period(experiment.time, r, window) for r in records]
    return rms, period


def window_sweep(experiment: Elevation) -> Sweep:
    """Mean RMS elevation of the repetitions for each end of the window."""

    def at(end: float) -> dict[str, float]:
        rms, period = repetition_results(experiment, (WINDOW[0], end))
        return {"rms": estimate(rms).mean, "period": estimate(period).mean}

    return sweep("window end", WINDOW_ENDS, at, unit="s")


def model_results(models: dict[str, Elevation]) -> dict[str, tuple[float, float]]:
    """RMS and period of each numerical run in the window."""
    out = {}
    for name, model in models.items():
        values = model.values[:, 0]
        out[name] = (
            rms_elevation(model.time, values, WINDOW),
            wave_period(model.time, values, WINDOW),
        )
    return out


def agreement(measured: Estimate, value: float) -> float:
    """``value - measured.mean`` in units of the standard uncertainty of the mean.

    The run is a single value without uncertainty of its own, so only the
    measurement's standard error enters.
    """
    return float(normalised_difference(value, 0.0, measured.mean, measured.sigma))


def build_report(data_dir: Path = DATA_DIR) -> Report:
    """The report of the measured problem, in the order of the lesson."""
    experiment, models = load(data_dir)
    rms, period = repetition_results(experiment, WINDOW)
    mean_rms, mean_period = estimate(rms), estimate(period)
    report = Report(f"Waves over a submerged bar, gauge {GAUGE}, wave condition 1")
    report = report.add("window", WINDOW[0], "s", decimals=1)
    report = report.add("window end", WINDOW[1], "s", decimals=1)
    report = report.add("repetitions", mean_rms.n, decimals=0)
    report = report.add(
        "RMS elevation, mean of repetitions",
        mean_rms.mean * 1e3,
        "mm",
        sigma=mean_rms.sigma * 1e3,
        decimals=2,
    )
    report = report.add(
        "wave period, mean of repetitions", mean_period.mean, "s", decimals=2
    )
    report = report.add(
        "period resolution of the window",
        period_resolution(mean_period.mean, WINDOW),
        "s",
        decimals=2,
    )
    scan = window_sweep(experiment)
    spread = float(scan.results["rms"].max() - scan.results["rms"].min())
    report = report.add(
        "RMS elevation, spread over the window ends", spread * 1e3, "mm", decimals=2
    )
    for end, value, period_value in scan.rows("rms", "period"):
        report = report.add(
            f"RMS elevation, window end {end:.0f} s", value * 1e3, "mm", decimals=2
        )
        report = report.add(
            f"wave period, window end {end:.0f} s", period_value, "s", decimals=2
        )
    for name, (model_rms, model_period) in model_results(models).items():
        report = report.add(f"{name}: RMS elevation", model_rms * 1e3, "mm", decimals=2)
        report = report.add(
            f"{name}: RMS elevation, model minus measurement",
            (model_rms - mean_rms.mean) * 1e3,
            "mm",
            decimals=2,
        )
        report = report.add(
            f"{name}: RMS elevation, model minus measurement in standard errors",
            agreement(mean_rms, model_rms),
            "",
            decimals=1,
        )
        report = report.add(f"{name}: wave period", model_period, "s", decimals=2)
    return report
