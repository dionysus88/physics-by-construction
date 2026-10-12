"""The processing and the fit of the gravitational-wave lab, on the committed sample."""

import numpy as np
import pytest

from pbc.data import SAMPLES_DIR, gwstrain
from pbc.data.gwosc import FILES, read_strain
from pbc.data.gwstrain import (
    correlation_with_control,
    cut_segment,
    fit_chirp,
    make_whitener,
    noise_sigma,
)
from pbc.mechanics.chirp import chirp_waveform

BAND = (35.0, 350.0)


@pytest.fixture(scope="module")
def strains():
    return {
        n: read_strain(SAMPLES_DIR / "gw150914-strain" / f) for n, f in FILES.items()
    }


def test_the_segment_is_centred_on_the_event(strains):
    seg = cut_segment(strains["H1"], 2.0)
    assert seg.time[0] == pytest.approx(-2.0, abs=1 / 4096)
    assert len(seg.strain) == 2 * 2 * 4096
    assert seg.detector == "H1"


def test_whitened_noise_has_one_level_across_the_quiet_segment(strains):
    seg = cut_segment(strains["H1"], 2.0)
    white = make_whitener(strains["H1"], seg, BAND)(seg.strain)
    early = noise_sigma(white, seg.time, (0.5, 1.0))
    late = noise_sigma(white, seg.time, (1.0, 1.6))
    assert early == pytest.approx(late, rel=0.3)


def test_the_whitener_is_linear(strains):
    seg = cut_segment(strains["H1"], 0.75)
    white = make_whitener(strains["H1"], seg, BAND)
    x, y = seg.strain, np.sin(np.arange(len(seg.strain)))
    np.testing.assert_allclose(
        white(2 * x + y),
        2 * white(x) + white(y),
        rtol=0,
        atol=1e-9 * np.max(np.abs(white(y))),
    )


def test_the_detectors_correlate_at_the_event_and_not_away_from_it(strains):
    segs = {n: cut_segment(s, 2.0) for n, s in strains.items()}
    white = {
        n: make_whitener(strains[n], segs[n], BAND)(segs[n].strain) for n in strains
    }
    out = correlation_with_control(white["H1"], white["L1"], segs["H1"].time, 4096.0)
    assert abs(out["lag"]) < 0.010
    assert out["correlation"] < 0  # the detectors answer with opposite signs
    assert abs(out["correlation"]) > 2 * out["controls"].max()
    assert len(out["controls"]) >= 6


def test_the_fit_recovers_the_parameters_of_an_injected_chirp(strains):
    # Control: a known chirp, whitened like the data, in Gaussian noise of unit
    # standard deviation, is recovered inside its stated interval.
    seg = {n: cut_segment(s, 0.75) for n, s in strains.items()}
    white = {n: make_whitener(strains[n], seg[n], BAND) for n in strains}
    time = seg["H1"].time
    truth_mc, truth_tc = 30.0, 0.03
    rng = np.random.default_rng(7)
    data = {}
    for n in strains:
        template = white[n](chirp_waveform(time, truth_mc, truth_tc, 1.0, 0.4))
        data[n] = 6.0 * template / np.max(np.abs(template)) + rng.normal(size=time.size)
    fit = fit_chirp(
        time,
        data,
        white,
        {"H1": 0.0, "L1": 0.0},
        window=(-0.2, 0.0),
        sigma=1.0,
        mc_grid=np.arange(24.0, 40.0, 1.0),
    )
    assert fit.mc == pytest.approx(truth_mc, abs=1.5)
    assert fit.t_c == pytest.approx(truth_tc, abs=3e-3)
    assert not fit.at_edge


@pytest.mark.parametrize("fault", ["not converged", "not finite"])
def test_the_fit_does_not_use_a_search_that_failed(strains, monkeypatch, fault):
    # Every bounded search fails and reports a time outside its bounds with a
    # chi-square that looks better than any grid point. The fit then rests on
    # the grid points alone and still finds the injected chirp.
    seg = {n: cut_segment(s, 0.75) for n, s in strains.items()}
    white = {n: make_whitener(strains[n], seg[n], BAND) for n in strains}
    time = seg["H1"].time
    truth_mc, truth_tc = 30.0, 0.03
    rng = np.random.default_rng(7)
    data = {}
    for n in strains:
        template = white[n](chirp_waveform(time, truth_mc, truth_tc, 1.0, 0.4))
        data[n] = 6.0 * template / np.max(np.abs(template)) + rng.normal(size=time.size)

    search = gwstrain.optimize.minimize_scalar

    def fails(function, **options):
        result = search(function, **options)
        result.x = options["bounds"][0] - 0.05
        if fault == "not converged":
            result.success = False
            result.fun = -1.0
        else:
            result.fun = float("-inf")
        return result

    monkeypatch.setattr(gwstrain.optimize, "minimize_scalar", fails)
    fit = fit_chirp(
        time,
        data,
        white,
        {"H1": 0.0, "L1": 0.0},
        window=(-0.2, 0.0),
        sigma=1.0,
        mc_grid=np.arange(24.0, 40.0, 1.0),
    )
    assert np.isfinite(fit.reduced_chi2) and fit.reduced_chi2 > 0
    assert fit.mc == pytest.approx(truth_mc, abs=1.5)
    assert fit.t_c == pytest.approx(truth_tc, abs=3e-3)


def test_the_fit_follows_the_delay_convention_of_the_lag(strains):
    # Control: L1 sees the injected wave 7 ms before H1, i.e. a lag of -7 ms in
    # the convention of best_lag; the fit recovers the shared parameters with
    # that delay and fits worse with the opposite sign.
    seg = {n: cut_segment(s, 0.75) for n, s in strains.items()}
    white = {n: make_whitener(strains[n], seg[n], BAND) for n in strains}
    time = seg["H1"].time
    truth_mc, truth_tc, lag = 30.0, 0.04, -0.007
    shift = {"H1": 0.0, "L1": lag}
    rng = np.random.default_rng(11)
    data = {}
    for n in strains:
        template = white[n](
            chirp_waveform(time, truth_mc, truth_tc + shift[n], 1.0, 0.4)
        )
        data[n] = 8.0 * template / np.max(np.abs(template)) + rng.normal(size=time.size)

    def run(delays):
        return fit_chirp(
            time,
            data,
            white,
            delays,
            window=(-0.2, 0.0),
            sigma=1.0,
            mc_grid=np.arange(24.0, 40.0, 1.0),
        )

    right = run(shift)
    wrong = run({"H1": 0.0, "L1": -lag})
    assert right.mc == pytest.approx(truth_mc, abs=1.5)
    assert right.t_c == pytest.approx(truth_tc, abs=3e-3)
    assert right.fit.chi2 < wrong.fit.chi2


def test_the_lab_fit_of_the_sample_is_inside_the_stated_range(strains):
    seg = {n: cut_segment(s, 0.75) for n, s in strains.items()}
    white = {n: make_whitener(strains[n], seg[n], BAND) for n in strains}
    data = {n: white[n](seg[n].strain) for n in strains}
    time = seg["H1"].time
    sigma = noise_sigma(data["H1"], time, (0.3, 0.65))
    fit = fit_chirp(
        time,
        data,
        white,
        {"H1": 0.0, "L1": -0.00732},  # L1 first, as best_lag reports
        window=(-0.2, 0.0),
        sigma=sigma,
        mc_grid=np.arange(22.0, 50.0, 1.0),
    )
    published = 28.6 * 1.09
    assert 1.0 < fit.mc / published < 1.4  # a Newtonian-order fit overestimates
    assert 0.7 < fit.reduced_chi2 < 1.3
    assert fit.mc_low <= fit.mc <= fit.mc_high + 1.0
    assert not fit.at_edge
