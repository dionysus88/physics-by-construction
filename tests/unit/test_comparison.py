"""The data of the waveform comparator: the page embeds what the lab computed."""

import json

import numpy as np
import pytest

from pbc.authoring.widgets import widget_asset
from pbc.data import SAMPLES_DIR
from pbc.data.comparison import DECIMALS, SCHEMA, waveform_comparison
from pbc.data.gwosc import FILES, read_strain
from pbc.data.gwstrain import (
    cut_segment,
    fit_chirp,
    make_whitener,
    models_at_masses,
    noise_sigma,
)

BAND = (35.0, 350.0)
WINDOW = (-0.2, 0.0)
LAG = -0.00732


@pytest.fixture(scope="module")
def lab():
    strains = {
        n: read_strain(SAMPLES_DIR / "gw150914-strain" / f) for n, f in FILES.items()
    }
    seg = {n: cut_segment(s, 0.75) for n, s in strains.items()}
    white = {n: make_whitener(strains[n], seg[n], BAND) for n in strains}
    data = {n: white[n](seg[n].strain) for n in strains}
    time = seg["H1"].time
    sigma = noise_sigma(data["H1"], time, (0.3, 0.65))
    delays = {"H1": 0.0, "L1": LAG}
    fit = fit_chirp(
        time, data, white, delays, window=WINDOW, sigma=sigma,
        mc_grid=np.arange(22.0, 50.0, 2.0),
    )  # fmt: skip
    return time, data, white, delays, sigma, fit


def test_the_model_at_the_fitted_mass_reproduces_the_fit(lab):
    time, data, white, delays, sigma, fit = lab
    [at_best] = models_at_masses(
        time, data, white, delays, np.array([fit.mc]), window=WINDOW, sigma=sigma,
        mc_start=fit.mc, t_c_start=fit.t_c,
    )  # fmt: skip
    assert at_best.t_c == pytest.approx(fit.t_c, abs=2e-4)
    assert at_best.chi2 == pytest.approx(fit.fit.chi2, rel=2e-3)
    assert at_best.reduced_chi2 == pytest.approx(fit.reduced_chi2, rel=5e-2)
    for name in white:
        assert at_best.model[name] == pytest.approx(fit.models[name], abs=5e-2)


def test_the_metrics_rank_the_masses_as_the_profile_does(lab):
    time, data, white, delays, sigma, fit = lab
    masses = np.array([26.0, fit.mc, 44.0])
    models = models_at_masses(
        time, data, white, delays, masses, window=WINDOW, sigma=sigma,
        mc_start=fit.mc, t_c_start=fit.t_c,
    )  # fmt: skip
    assert min(models, key=lambda m: m.chi2).mc == pytest.approx(fit.mc)
    assert min(models, key=lambda m: m.rms_residual).mc == pytest.approx(fit.mc)
    assert max(models, key=lambda m: m.correlation).mc == pytest.approx(fit.mc)
    assert all(-1.0 <= m.correlation <= 1.0 for m in models)


def test_the_embedded_measured_series_is_the_data_to_the_stated_rounding(lab):
    time, data, white, delays, sigma, fit = lab
    models = models_at_masses(
        time, data, white, delays, np.array([fit.mc]), window=WINDOW, sigma=sigma,
        mc_start=fit.mc, t_c_start=fit.t_c,
    )  # fmt: skip
    payload = waveform_comparison(
        time, data["H1"], models, "H1", sigma=sigma, window=WINDOW,
        show=(-0.25, 0.05), quantity="whitened strain", unit="1", best=fit.mc,
    )  # fmt: skip
    assert payload["schema"] == SCHEMA
    shown = (time >= -0.25) & (time <= 0.05)
    # Nothing is smoothed or resampled: every sample is there, rounded only.
    assert np.array(payload["measured"]) == pytest.approx(
        data["H1"][shown], abs=0.5 * 10.0**-DECIMALS + 1e-12
    )
    assert np.array(payload["time"]) == pytest.approx(time[shown], abs=1e-5)
    assert np.array(payload["models"][0]["values"]) == pytest.approx(
        models[0].model["H1"][shown], abs=0.5 * 10.0**-DECIMALS + 1e-12
    )
    # The residual is the measurement minus the model, as plotted.
    assert np.array(payload["models"][0]["residual"]) == pytest.approx(
        (data["H1"] - models[0].model["H1"])[shown], abs=0.5 * 10.0**-DECIMALS + 1e-12
    )
    json.dumps(payload, allow_nan=False)


def test_an_on_demand_file_is_written_beside_the_page(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    url = widget_asset("example-data", {"a": [1.5, 2.0]})
    assert url == "index_files/figure-html/example-data.json"
    assert json.loads((tmp_path / url).read_text()) == {"a": [1.5, 2.0]}


@pytest.mark.parametrize("name", ["Upper", "a/b", "a b", "../x", ""])
def test_an_on_demand_file_name_is_a_plain_lower_case_word(tmp_path, monkeypatch, name):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError):
        widget_asset(name, {})


def test_an_on_demand_file_refuses_data_that_json_cannot_hold(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError):
        widget_asset("bad", {"x": float("nan")})
