import numpy as np
import pytest

from pbc.mechanics.drag import linear_drag
from pbc.mechanics.dynamics import State, newton, simulate
from pbc.mechanics.integrators import rk4_step
from pbc.mechanics.oscillator import spring
from pbc.mechanics.resonance import (
    damping_rate,
    driven_motion,
    driving_force,
    fit_amplitude,
    half_power_width,
    measured_resonance_curve,
    natural_frequency,
    peak_frequency,
    quality_factor,
    steady_state_amplitude,
    steady_state_phase,
)

# The oscillator of lesson M12: one kilogram, ω₀ = 2 rad/s, Q = 5.
MASS, K, B, FORCE = 1.0, 4.0, 0.4, 2.0
W0 = natural_frequency(MASS, K)


def test_the_amplitude_far_below_resonance_is_the_static_displacement():
    assert steady_state_amplitude(MASS, K, B, FORCE, 1e-6) == pytest.approx(FORCE / K)


def test_the_amplitude_at_the_natural_frequency_is_the_quality_factor_times_it():
    q = quality_factor(MASS, K, B)
    assert q == pytest.approx(5.0)
    assert steady_state_amplitude(MASS, K, B, FORCE, W0) == pytest.approx(q * FORCE / K)


def test_the_phase_lag_goes_from_zero_through_a_quarter_turn_to_a_half_turn():
    low, mid, high = steady_state_phase(MASS, K, B, np.array([1e-6, W0, 1e3]))
    assert low == pytest.approx(0.0, abs=1e-6)
    assert mid == pytest.approx(np.pi / 2)
    assert high == pytest.approx(np.pi, abs=1e-3)


def test_the_peak_is_where_the_amplitude_is_largest():
    omegas = np.linspace(0.5, 3.0, 200001)
    amplitudes = steady_state_amplitude(MASS, K, B, FORCE, omegas)
    assert omegas[np.argmax(amplitudes)] == pytest.approx(
        peak_frequency(MASS, K, B), abs=1e-4
    )
    assert peak_frequency(MASS, K, B) < W0
    assert peak_frequency(MASS, 4.0, 3.0) == 0.0


def test_the_closed_form_motion_satisfies_the_initial_state():
    initial = State(t=1.0, x=[0.3], v=[-0.2])
    motion = driven_motion(initial, MASS, K, B, FORCE, 1.7, [1.0])
    assert motion.x[0, 0] == pytest.approx(0.3)
    assert motion.v[0, 0] == pytest.approx(-0.2)


def test_the_simulation_follows_the_closed_form_motion_with_its_transient():
    omega = 1.7
    initial = State(t=0.0, x=[0.3], v=[-0.2])
    run = simulate(
        initial,
        newton(MASS, spring(K), linear_drag(B), driving_force(FORCE, omega)),
        0.005,
        4000,
        step=rk4_step,
    )
    exact = driven_motion(initial, MASS, K, B, FORCE, omega, run.t)
    assert np.max(np.abs(run.x - exact.x)) < 1e-8
    assert np.max(np.abs(run.v - exact.v)) < 1e-8


def test_the_closed_form_motion_follows_a_simulation_started_at_a_later_time():
    omega = 1.7
    initial = State(t=2.5, x=[0.3], v=[-0.2])
    run = simulate(
        initial,
        newton(MASS, spring(K), linear_drag(B), driving_force(FORCE, omega)),
        0.005,
        4000,
        step=rk4_step,
    )
    exact = driven_motion(initial, MASS, K, B, FORCE, omega, run.t)
    assert exact.t == pytest.approx(run.t)
    assert np.max(np.abs(run.x - exact.x)) < 1e-8
    assert np.max(np.abs(run.v - exact.v)) < 1e-8


def test_the_fit_recovers_amplitude_and_phase_of_the_steady_state():
    omega = 2.3
    t = np.linspace(0.0, 40.0, 4001)
    amplitude = float(steady_state_amplitude(MASS, K, B, FORCE, omega))
    delta = float(steady_state_phase(MASS, K, B, omega))
    motion = driven_motion(
        State(0.0, [amplitude * np.cos(delta)], [amplitude * omega * np.sin(delta)]),
        MASS,
        K,
        B,
        FORCE,
        omega,
        t,
    )
    fitted = fit_amplitude(motion, omega, after=0.0)
    assert fitted[0] == pytest.approx(amplitude, rel=1e-9)
    assert fitted[1] == pytest.approx(delta, rel=1e-9)


def test_the_measured_resonance_curve_matches_the_amplitude_formula():
    omegas = np.linspace(0.4, 4.0, 12)
    measured, phase = measured_resonance_curve(MASS, K, B, FORCE, omegas)
    exact = steady_state_amplitude(MASS, K, B, FORCE, omegas)
    assert np.max(np.abs(measured / exact - 1.0)) < 2e-3
    assert np.max(np.abs(phase - steady_state_phase(MASS, K, B, omegas))) < 2e-3


def test_the_half_power_width_is_the_damping_over_the_mass():
    omegas = np.linspace(0.2, 4.0, 4001)
    amplitudes = steady_state_amplitude(MASS, K, B, FORCE, omegas)
    width = half_power_width(omegas, amplitudes)
    assert width == pytest.approx(B / MASS, rel=0.02)
    assert W0 / width == pytest.approx(quality_factor(MASS, K, B), rel=0.02)
    assert damping_rate(MASS, B) == pytest.approx(0.2)


def test_invalid_input_is_rejected():
    with pytest.raises(ValueError):
        driven_motion(State(0.0, [0.0], [0.0]), MASS, K, 4.0, FORCE, 1.0, [0.0])
    with pytest.raises(ValueError):
        half_power_width([1.0, 2.0, 3.0], [1.0, 2.0, 1.9])
    with pytest.raises(ValueError):
        steady_state_amplitude(-1.0, K, B, FORCE, 1.0)
