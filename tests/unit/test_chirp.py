"""The Newtonian chirp: closed forms against an independent integration."""

import numpy as np
import pytest

from pbc.mechanics import chirp


def test_the_chirp_mass_of_equal_masses_is_a_fixed_fraction_of_the_total():
    assert chirp.chirp_mass(10.0, 10.0) == pytest.approx(10.0 * 2 ** (-0.2))


def test_the_chirp_mass_needs_positive_masses():
    with pytest.raises(ValueError, match="positive"):
        chirp.chirp_mass(0.0, 1.0)


def test_kepler_third_law_round_trip():
    a = chirp.separation_from_frequency(100.0, 65.0)
    assert chirp.frequency_from_separation(a, 65.0) == pytest.approx(100.0, rel=1e-12)


def test_the_closed_form_matches_the_numerical_inspiral():
    m1, m2, f0 = 36.0, 29.0, 35.0
    mc = chirp.chirp_mass(m1, m2)
    tau = chirp.time_to_coalescence(f0, mc)
    t = np.linspace(0.0, 0.95 * tau, 200)
    _, f_numeric = chirp.inspiral_frequency(t, m1, m2, f0)
    f_closed = chirp.chirp_frequency(t, mc, tau)
    assert np.max(np.abs(f_numeric / f_closed - 1.0)) < 1e-6


def test_the_rate_follows_from_the_frequency_by_differentiating():
    mc, t_c = 30.0, 0.1
    t = np.array([-0.2, -0.1, -0.05])
    h = 1e-7
    numeric = (
        chirp.chirp_frequency(t + h, mc, t_c) - chirp.chirp_frequency(t - h, mc, t_c)
    ) / (2 * h)
    formula = chirp.chirp_rate(chirp.chirp_frequency(t, mc, t_c), mc)
    assert numeric == pytest.approx(formula, rel=1e-5)


def test_the_chirp_mass_is_recovered_from_a_frequency_and_its_rate():
    f = 80.0
    assert chirp.chirp_mass_from_rate(f, chirp.chirp_rate(f, 28.1)) == pytest.approx(
        28.1
    )


def test_the_phase_derivative_is_the_wave_angular_frequency():
    mc, t_c = 30.0, 0.1
    t = np.array([-0.15, -0.05])
    h = 1e-7
    omega = (chirp.chirp_phase(t + h, mc, t_c) - chirp.chirp_phase(t - h, mc, t_c)) / (
        2 * h
    )
    assert omega == pytest.approx(
        2 * np.pi * chirp.chirp_frequency(t, mc, t_c), rel=1e-6
    )


def test_the_frequency_is_undefined_from_the_coalescence_time_on():
    f = chirp.chirp_frequency(np.array([0.0, 0.1, 0.2]), 30.0, 0.1)
    assert np.isfinite(f[0]) and np.isnan(f[1]) and np.isnan(f[2])
    assert np.all(chirp.chirp_waveform(np.array([0.1, 0.2]), 30.0, 0.1) == 0.0)


def test_the_separation_at_the_end_is_inside_a_few_horizon_radii():
    # A reason the model stops: at 150 Hz the bodies of the example nearly touch.
    a = chirp.separation_from_frequency(150.0, 65.0)
    assert a < 2 * chirp.schwarzschild_radius(65.0)
