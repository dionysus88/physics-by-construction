"""Parameter recovery, profiles, and the reasons not to believe a fit."""

import numpy as np
import pytest

from pbc.data import inverse
from pbc.data.fit import fit_curve
from pbc.data.inverse import profile, recover, residual_autocorrelation, verdict


def damped(t, amplitude, rate, omega, phase):
    return amplitude * np.exp(-rate * t) * np.cos(omega * t + phase)


def spring_mass(t, k, m):
    """Free oscillation of a mass on a spring: only k/m reaches the motion."""
    return np.cos(np.sqrt(k / m) * t)


T = np.linspace(0.0, 6.0, 120)
TRUTH = [1.0, 0.35, 5.0, 0.4]
NAMES = ["amplitude", "rate", "omega", "phase"]


def test_recover_finds_the_parameters_of_a_damped_oscillation_with_honest_intervals():
    out = recover(damped, T, TRUTH, sigma=0.05, trials=60, seed=3, names=NAMES)
    assert out.recovered(0.06)
    # The stated standard error is the actual scatter, not a flattering number.
    assert out.mean_stderr == pytest.approx(out.rms_error, rel=0.4)


@pytest.mark.filterwarnings("ignore:invalid value:RuntimeWarning")
def test_recover_reports_a_non_identifiable_model_instead_of_numbers():
    # k and m only appear through k/m, so no data can tell them apart.
    with pytest.raises(ValueError, match="no trial gave an identified fit"):
        recover(spring_mass, T, [4.0, 1.0], sigma=0.05, trials=10, names=["k", "m"])


def test_recover_counts_unidentified_trials():
    out = recover(
        lambda t, a, b: a * np.exp(-b * t),
        T,
        [1.0, 1e-9],
        sigma=0.05,
        trials=5,
        names=["a", "b"],
    )
    assert out.unidentified + out.failed <= out.trials


def test_profile_is_a_bowl_for_a_determined_parameter():
    rng = np.random.default_rng(1)
    y = damped(T, *TRUTH) + rng.normal(0, 0.05, T.size)
    grid = np.linspace(4.9, 5.1, 21)
    out = profile(damped, T, y, TRUTH, "omega", grid, sigma=0.05, names=NAMES)
    assert out.bounded
    assert out.low < 5.0 < out.high
    assert out.high - out.low < 0.05


def test_profile_refuses_a_refit_that_did_not_converge(monkeypatch):
    y = damped(T, *TRUTH) + np.random.default_rng(1).normal(0, 0.05, T.size)
    grid = np.linspace(4.9, 5.1, 21)
    solve = inverse.optimize.least_squares
    calls = []

    def gives_up_once(*args, **kwargs):
        result = solve(*args, **kwargs)
        calls.append(result)
        if len(calls) == 5:
            result.success = False
            result.message = "the limit of evaluations was reached"
        return result

    monkeypatch.setattr(inverse.optimize, "least_squares", gives_up_once)

    with pytest.raises(inverse.ProfileError, match="did not converge"):
        profile(damped, T, y, TRUTH, "omega", grid, sigma=0.05, names=NAMES)
    assert len(calls) == 5, "the profile went on after a refit that did not converge"


def test_profile_of_a_non_identifiable_parameter_is_open():
    y = spring_mass(T, 4.0, 1.0) + np.random.default_rng(2).normal(0, 0.05, T.size)
    grid = np.linspace(2.0, 8.0, 25)
    out = profile(
        spring_mass,
        T,
        y,
        [4.0, 1.0],
        "k",
        grid,
        sigma=0.05,
        names=["k", "m"],
        bounds=([1e-3, 1e-3], [np.inf, np.inf]),
    )
    assert out.open_low and out.open_high
    assert not out.bounded
    assert out.chi2.max() - out.chi2.min() < 1.0


def test_the_fit_helper_flags_the_tied_parameters_and_the_verdict_says_so():
    y = spring_mass(T, 4.0, 1.0) + np.random.default_rng(2).normal(0, 0.05, T.size)
    fit = fit_curve(spring_mass, T, y, [4.5, 1.1], sigma=0.05, names=["k", "m"])
    assert not any(fit.identifiable)
    assert any("separately" in reason for reason in verdict(fit))


def test_a_wrong_model_leaves_structure_in_the_residuals():
    # Control: data with a second oscillation, fitted with one. The fit
    # converges and the parameters have small errors, and the verdict objects.
    rng = np.random.default_rng(5)
    y = damped(T, *TRUTH) + 0.4 * np.cos(2.1 * 5.0 * T) + rng.normal(0, 0.05, T.size)
    fit = fit_curve(damped, T, y, TRUTH, sigma=0.05, names=NAMES)
    assert verdict(fit)


def test_a_right_model_has_no_reasons_against():
    rng = np.random.default_rng(6)
    y = damped(T, *TRUTH) + rng.normal(0, 0.05, T.size)
    fit = fit_curve(damped, T, y, TRUTH, sigma=0.05, names=NAMES)
    assert verdict(fit) == []


def test_residual_autocorrelation_is_small_for_noise_and_large_for_a_trend():
    noise = np.random.default_rng(0).normal(size=400)
    assert abs(residual_autocorrelation(noise)[1]) < 3
    assert residual_autocorrelation(np.sin(np.linspace(0, 6, 400)))[0] > 0.9


def test_residual_autocorrelation_is_invalid_for_constant_short_or_gapped_residuals():
    for bad in (np.ones(50), np.arange(3.0), np.full(50, np.nan)):
        assert np.isnan(residual_autocorrelation(bad)[1])
    gapped = np.sin(np.linspace(0, 6, 40))
    gapped[1::2] = np.nan
    assert np.isnan(residual_autocorrelation(gapped)[1])
    assert np.isfinite(residual_autocorrelation(np.sin(np.linspace(0, 6, 40)))[1])
    fit = fit_curve(damped, T, damped(T, *TRUTH), TRUTH, sigma=0.05, names=NAMES)
    fit.residuals[:] = 0.0
    assert any("could not be calculated" in r for r in verdict(fit))
