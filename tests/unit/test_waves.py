"""The wave solver, the modes, and sound (lessons W1, W2, W9): each result is
compared with a closed-form solution or a limiting case, with a stated
tolerance."""

import numpy as np
import pytest

from pbc.waves.modes import (
    centroid,
    measured_frequency,
    spectrum_peaks,
    string_frequency,
    triangle,
    triangle_mode_amplitude,
    two_source_amplitude,
    two_source_pattern,
    wave_packet,
)
from pbc.waves.sound import (
    SPEED_OF_SOUND,
    emission_time,
    observer_shift,
    pipe_frequency,
    received_signal,
    source_shift,
)
from pbc.waves.wave import (
    amplitude_growth,
    courant_number,
    driven_mode_amplitude,
    error_norm,
    grid,
    growth_factor,
    numerical_angular_frequency,
    numerical_group_velocity,
    observed_order,
    reflected_pulse,
    solve,
    standing_mode,
    zigzag_run,
)

LENGTH = 1.0
C = 2.0


def mode_error(n_cells: int, courant: float, n: int = 2, time: float = 0.85) -> float:
    dx = LENGTH / n_cells
    dt = courant * dx / C
    n_steps = round(time / dt)
    x = grid(LENGTH, n_cells)
    result = solve(
        standing_mode(x, 0.0, length=LENGTH, n=n, c=C),
        np.zeros_like(x),
        c=C,
        dx=dx,
        dt=dt,
        n_steps=n_steps,
        every=n_steps,
    )
    exact = standing_mode(x, result.t[-1], length=LENGTH, n=n, c=C)
    return error_norm(result.u[-1], exact)


# --- The solver ------------------------------------------------------------------


def test_the_error_of_a_standing_mode_falls_with_the_second_power_of_the_spacing():
    cells = np.array([25, 50, 100, 200])
    errors = [mode_error(n, 0.5) for n in cells]
    # The scheme is second order: the observed order is two within 0.05.
    assert observed_order(LENGTH / cells, errors) == pytest.approx(2.0, abs=0.05)


def test_at_a_courant_number_of_one_the_scheme_is_exact_on_the_grid():
    assert mode_error(50, 1.0) < 1e-12


def test_a_pulse_returns_inverted_from_a_fixed_end_and_upright_from_a_free_end():
    def shape(s):
        return np.exp(-(((s - 0.3) / 0.05) ** 2))

    n_cells = 400
    dx = LENGTH / n_cells
    x = grid(LENGTH, n_cells)
    for ends, sign in (("fixed", -1.0), ("free", 1.0)):
        # After the time it takes to go to the end at x = L and back to 0.3
        # + 2 (L - 0.3) = 1.7 ... the pulse is at 1.7 - L from the far end.
        time = (LENGTH - 0.3) * 2.0 / C
        dt = 1.0 * dx / C
        result = solve(
            shape(x),
            np.zeros_like(x),
            c=C,
            dx=dx,
            dt=dt,
            n_steps=round(time / dt),
            left=ends,
            right=ends,
        )
        exact = reflected_pulse(shape, x, result.t[-1], length=LENGTH, c=C, ends=ends)
        # The pulse of the field has split in two halves; both are exact at C = 1.
        assert error_norm(result.u[-1], exact) < 1e-10
        # The half that travelled right and back has the sign of the end.
        assert sign * result.u[-1][np.argmax(np.abs(result.u[-1]))] > 0.0


def test_the_solution_is_linear_in_the_initial_state():
    x = grid(LENGTH, 100)
    a = np.sin(np.pi * x)
    b = np.exp(-(((x - 0.4) / 0.05) ** 2))
    kwargs = dict(c=C, dx=0.01, dt=0.004, n_steps=120, every=120)
    together = solve(a + 3.0 * b, np.zeros_like(x), **kwargs).u[-1]
    apart = solve(a, np.zeros_like(x), **kwargs).u[-1]
    apart += 3.0 * solve(b, np.zeros_like(x), **kwargs).u[-1]
    assert error_norm(together, apart) < 1e-12


def test_recording_every_few_steps_keeps_the_first_and_the_last_step():
    x = grid(LENGTH, 20)
    result = solve(
        np.sin(np.pi * x), np.zeros_like(x), c=C, dx=0.05, dt=0.01, n_steps=7, every=3
    )
    np.testing.assert_allclose(result.t, [0.0, 0.03, 0.06, 0.07])
    assert result.u.shape == (4, 21)


def test_a_solution_that_starts_with_velocity_moves_by_that_velocity_at_first():
    x = grid(LENGTH, 20)
    result = solve(
        np.zeros_like(x),
        np.sin(np.pi * x),
        c=C,
        dx=0.05,
        dt=1e-4,
        n_steps=1,
    )
    np.testing.assert_allclose(result.u[1], 1e-4 * np.sin(np.pi * x), atol=1e-12)


def test_the_conditions_at_the_ends_hold():
    x = grid(LENGTH, 50)
    result = solve(
        np.exp(-(((x - 0.5) / 0.1) ** 2)),
        np.zeros_like(x),
        c=C,
        dx=0.02,
        dt=0.005,
        n_steps=200,
        left="fixed",
        right="free",
    )
    assert np.all(result.u[:, 0] == 0.0)
    # A free end has no slope: the node beyond it mirrors the node inside.
    assert np.max(np.abs(result.u[:, -1] - result.u[:, -2])) < 0.1 * np.max(
        np.abs(result.u)
    )


@pytest.mark.parametrize(
    "arguments, message",
    [
        (dict(left="open"), "end is one of"),
        (dict(n_steps=0), "at least 1"),
        (dict(every=0), "at least 1"),
    ],
)
def test_a_bad_call_is_rejected(arguments, message):
    x = grid(LENGTH, 10)
    kwargs = dict(c=C, dx=0.1, dt=0.01, n_steps=2) | arguments
    with pytest.raises(ValueError, match=message):
        solve(x, np.zeros_like(x), **kwargs)


def test_a_courant_number_needs_positive_inputs():
    assert courant_number(2.0, 0.01, 0.05) == pytest.approx(0.4)
    with pytest.raises(ValueError):
        courant_number(2.0, 0.0, 0.05)
    with pytest.raises(ValueError):
        grid(1.0, 1)


def test_mismatched_initial_arrays_are_rejected():
    with pytest.raises(ValueError, match="same length"):
        solve(np.zeros(5), np.zeros(6), c=C, dx=0.1, dt=0.01, n_steps=2)


def test_observed_order_recovers_a_known_power_and_rejects_bad_input():
    h = np.array([0.1, 0.05, 0.025])
    assert observed_order(h, 7.0 * h**3) == pytest.approx(3.0)
    with pytest.raises(ValueError):
        observed_order(h, [1.0, 0.5])
    with pytest.raises(ValueError):
        observed_order(h, [1.0, 0.0, 0.1])


# --- The CFL limit -----------------------------------------------------------------


@pytest.mark.parametrize("courant", [1.02, 1.1, 1.5])
def test_above_the_cfl_limit_the_zigzag_grows_by_the_predicted_factor(courant):
    assert amplitude_growth(zigzag_run(courant)) == pytest.approx(
        growth_factor(courant), rel=2e-3
    )


@pytest.mark.parametrize("courant", [0.3, 0.9, 1.0])
def test_up_to_the_cfl_limit_the_zigzag_does_not_grow(courant):
    assert growth_factor(courant) == 1.0
    # Forty steps from a start of 1e-10 stay of that size: nothing grows.
    assert np.max(np.abs(zigzag_run(courant).u)) < 2e-10


def test_growth_factor_rejects_a_courant_number_that_is_not_positive():
    with pytest.raises(ValueError):
        growth_factor(0.0)


# --- Modes and dispersion ------------------------------------------------------------


def test_numerical_frequency_equals_the_exact_one_at_courant_one_and_is_lower_below():
    k = np.array([5.0, 20.0, 60.0])
    exact = C * k
    np.testing.assert_allclose(
        numerical_angular_frequency(k, c=C, dx=0.01, dt=0.005), exact
    )
    below = numerical_angular_frequency(k, c=C, dx=0.01, dt=0.0025)
    assert np.all(below < exact)
    assert below[0] / exact[0] == pytest.approx(1.0, abs=1e-4)
    with pytest.raises(ValueError, match="too large"):
        numerical_angular_frequency(300.0, c=C, dx=0.01, dt=0.01)


def test_the_frequencies_of_a_plucked_string_are_those_of_its_modes():
    n_cells = 200
    dx = LENGTH / n_cells
    dt = 0.5 * dx / C
    x = grid(LENGTH, n_cells)
    result = solve(
        triangle(x, length=LENGTH, at=0.3),
        np.zeros_like(x),
        c=C,
        dx=dx,
        dt=dt,
        n_steps=20000,
    )
    probe = round(0.45 * n_cells)
    found = spectrum_peaks(result.u[:, probe], dt, count=5)
    expected = [string_frequency(n, length=LENGTH, c=C) for n in (1, 2, 3, 4, 5)]
    np.testing.assert_allclose(found, expected, rtol=3e-3)


def test_a_mode_with_a_node_at_the_pluck_is_absent():
    amplitudes = [
        triangle_mode_amplitude(n, length=LENGTH, at=LENGTH / 3) for n in (1, 2, 3)
    ]
    assert abs(amplitudes[2]) < 1e-12
    assert abs(amplitudes[0]) > abs(amplitudes[1]) / 2.0


def test_the_sine_series_of_the_triangle_adds_up_to_the_triangle():
    x = np.linspace(0.0, LENGTH, 201)
    series = sum(
        triangle_mode_amplitude(n, length=LENGTH, at=0.3) * np.sin(n * np.pi * x)
        for n in range(1, 400)
    )
    assert error_norm(series, triangle(x, length=LENGTH, at=0.3)) < 2e-3


def test_string_frequency_and_triangle_reject_bad_input():
    assert string_frequency(3, length=1.0, c=2.0) == pytest.approx(3.0)
    with pytest.raises(ValueError):
        string_frequency(0, length=1.0, c=2.0)
    with pytest.raises(ValueError):
        triangle(np.zeros(3), length=1.0, at=1.0)


# --- Interference ---------------------------------------------------------------


def test_summed_waves_of_two_sources_match_the_far_field_pattern():
    angle = np.linspace(-0.2, 0.2, 401)
    summed = two_source_amplitude(
        angle, separation=5.0, wavelength=1.0, distance=20000.0
    )
    pattern = two_source_pattern(angle, separation=5.0, wavelength=1.0)
    # Normalise by one source at the same distance: |exp(ikr) / r| = 1 / r.
    intensity = (summed * 20000.0) ** 2
    np.testing.assert_allclose(intensity, pattern, atol=2e-3)


def test_the_bright_fringes_lie_where_the_path_difference_is_whole_wavelengths():
    separation, wavelength = 5.0, 1.0
    angle = np.arcsin(np.arange(0, 3) * wavelength / separation)
    np.testing.assert_allclose(
        two_source_pattern(angle, separation=separation, wavelength=wavelength), 4.0
    )
    dark = np.arcsin((np.arange(0, 3) + 0.5) * wavelength / separation)
    np.testing.assert_allclose(
        two_source_pattern(dark, separation=separation, wavelength=wavelength),
        0.0,
        atol=1e-12,
    )


def test_spectrum_peaks_finds_two_tones_to_a_small_fraction_of_a_bin():
    t = np.arange(4096) * 1e-3
    tone = np.sin(2 * np.pi * 37.3 * t) + 0.5 * np.sin(2 * np.pi * 91.1 * t)
    np.testing.assert_allclose(
        spectrum_peaks(tone, 1e-3, count=2), [37.3, 91.1], rtol=1e-3
    )


# --- Sound -----------------------------------------------------------------------


def test_the_resonances_of_open_and_closed_pipes():
    assert pipe_frequency(1, length=0.5, c=340.0, closed_end=False) == pytest.approx(
        340.0
    )
    assert pipe_frequency(2, length=0.5, c=340.0, closed_end=False) == pytest.approx(
        680.0
    )
    # Closed at one end: the odd harmonics of c / (4 L).
    assert pipe_frequency(1, length=0.5, c=340.0, closed_end=True) == pytest.approx(
        170.0
    )
    assert pipe_frequency(2, length=0.5, c=340.0, closed_end=True) == pytest.approx(
        510.0
    )
    with pytest.raises(ValueError):
        pipe_frequency(0, length=0.5, c=340.0, closed_end=True)


def test_the_simulated_pipe_resonates_at_the_analytic_frequencies():
    c, length = SPEED_OF_SOUND, 0.8
    n_cells = 160
    dx = length / n_cells
    dt = 0.5 * dx / c
    x = grid(length, n_cells)
    # A short pulse near the closed end drives many resonances.
    pulse = np.exp(-(((x - 0.05) / 0.02) ** 2))
    result = solve(
        pulse,
        np.zeros_like(x),
        c=c,
        dx=dx,
        dt=dt,
        n_steps=30000,
        left="free",
        right="fixed",
    )
    found = spectrum_peaks(result.u[:, 0], dt, count=4)
    expected = [
        pipe_frequency(n, length=length, c=c, closed_end=True) for n in (1, 2, 3, 4)
    ]
    np.testing.assert_allclose(found, expected, rtol=5e-3)


def approaching(speed, start):
    def path(t):
        return start + speed * np.asarray(t)

    return path


def at(position):
    def path(t):
        return np.full(np.shape(t), position)

    return path


F0 = 440.0


def heard(source, observer, samples=100000, c=SPEED_OF_SOUND):
    t = np.linspace(1.5, 2.0, samples)
    return measured_frequency(received_signal(t, F0, source, observer, c), t)


@pytest.mark.parametrize("speed", [-60.0, -10.0, 10.0, 60.0, 120.0])
def test_the_heard_frequency_of_a_moving_source_follows_the_formula(speed):
    # The observer is at the origin; the source is far to the left, moving
    # right with the given speed (towards the observer when positive).
    source = approaching(speed, -300.0)
    assert heard(source, at(0.0)) == pytest.approx(
        source_shift(F0, SPEED_OF_SOUND, speed), rel=1e-4
    )


@pytest.mark.parametrize("speed", [-60.0, -10.0, 10.0, 60.0, 120.0])
def test_the_heard_frequency_of_a_moving_observer_follows_the_formula(speed):
    # The source is at the origin; the observer is far to the right and moves
    # towards it when the speed is positive.
    observer = approaching(-speed, 300.0)
    assert heard(at(0.0), observer) == pytest.approx(
        observer_shift(F0, SPEED_OF_SOUND, speed), rel=1e-4
    )


def test_a_source_and_an_observer_at_the_same_speed_hear_different_shifts():
    f_source = source_shift(F0, SPEED_OF_SOUND, 100.0)
    f_observer = observer_shift(F0, SPEED_OF_SOUND, 100.0)
    assert f_source > f_observer
    # The two agree to first order in v / c: the difference is of order (v/c)^2.
    ratio = (f_source - f_observer) / F0
    assert ratio == pytest.approx(
        (100.0 / SPEED_OF_SOUND) ** 2 / (1 - 100.0 / SPEED_OF_SOUND), rel=1e-9
    )


def test_with_no_motion_the_tone_arrives_unchanged_and_delayed():
    t = np.array([1.0, 2.0])
    tau = emission_time(t, at(0.0), at(343.0), SPEED_OF_SOUND)
    np.testing.assert_allclose(tau, t - 1.0, atol=1e-9)


def test_a_time_before_the_first_signal_arrives_is_refused():
    # The observer is 343 m away: nothing arrives before t = 1 s.
    with pytest.raises(ValueError, match="no signal"):
        emission_time(np.array([0.5, 2.0]), at(0.0), at(343.0), SPEED_OF_SOUND)
    with pytest.raises(ValueError, match="no signal"):
        emission_time(np.array([-1.0]), at(0.0), at(0.0), SPEED_OF_SOUND)
    tau = emission_time(np.array([1.0]), at(0.0), at(343.0), SPEED_OF_SOUND)
    np.testing.assert_allclose(tau, [0.0], atol=1e-9)


def test_supersonic_motion_and_a_short_signal_are_refused():
    with pytest.raises(ValueError):
        source_shift(F0, SPEED_OF_SOUND, SPEED_OF_SOUND)
    with pytest.raises(ValueError):
        observer_shift(F0, SPEED_OF_SOUND, -400.0)
    with pytest.raises(ValueError, match="crossings"):
        measured_frequency(np.array([1.0, 2.0, 3.0]), np.arange(3.0))


# --- Forcing and the group velocity ---------------------------------------------


def driven_amplitude(drive: float, n_steps: int, n: int = 1):
    n_cells = 100
    dx = LENGTH / n_cells
    dt = 0.5 * dx / C
    x = grid(LENGTH, n_cells)
    shape = np.sin(n * np.pi * x / LENGTH)
    result = solve(
        np.zeros_like(x),
        np.zeros_like(x),
        c=C,
        dx=dx,
        dt=dt,
        n_steps=n_steps,
        forcing=lambda t: shape * np.cos(drive * t),
    )
    # The amplitude of the mode: the projection of the field on its shape.
    amplitude = result.u @ shape / (shape @ shape)
    return result.t, amplitude


def test_a_driven_mode_follows_the_exact_amplitude_off_resonance():
    omega1 = np.pi * C / LENGTH
    t, amplitude = driven_amplitude(0.7 * omega1, 800)
    exact = driven_mode_amplitude(t, length=LENGTH, n=1, c=C, drive=0.7 * omega1)
    assert np.max(np.abs(amplitude - exact)) < 3e-3 * np.max(np.abs(exact))


def test_at_resonance_the_amplitude_grows_in_proportion_to_the_time():
    omega1 = np.pi * C / LENGTH
    t, amplitude = driven_amplitude(omega1, 1600)
    exact = driven_mode_amplitude(t, length=LENGTH, n=1, c=C, drive=omega1)
    assert np.max(np.abs(amplitude - exact)) < 1e-2 * np.max(np.abs(exact))
    # The envelope t / (2 w) is reached at the peaks of the sine.
    assert np.max(np.abs(amplitude[-400:])) > 3.0 * np.max(np.abs(amplitude[:200]))


def test_a_force_does_not_move_a_fixed_end():
    x = grid(LENGTH, 20)
    result = solve(
        np.zeros_like(x),
        np.zeros_like(x),
        c=C,
        dx=0.05,
        dt=0.01,
        n_steps=30,
        forcing=lambda t: np.ones_like(x),
    )
    assert np.all(result.u[:, 0] == 0.0) and np.all(result.u[:, -1] == 0.0)
    assert np.max(np.abs(result.u)) > 0.0


def test_the_centre_of_a_packet_moves_at_the_group_velocity_of_the_grid():
    n_cells = 400
    dx = LENGTH / n_cells
    dt = 0.5 * dx / C
    x = grid(LENGTH, n_cells)
    k = 1.2 / dx
    # The Gaussian envelope of width 0.05 m holds only wavenumbers near k.
    packet = wave_packet(x, centre=0.25, width=0.05, k=k)
    n_steps = round(0.1 / dt)
    result = solve(
        packet,
        np.zeros_like(x),
        c=C,
        dx=dx,
        dt=dt,
        n_steps=n_steps,
        every=n_steps,
    )
    # A packet released at rest is two packets, one going each way: follow
    # the right-going half.
    right = result.u[-1] * (x > 0.3)
    distance = centroid(x, right) - 0.25
    speed = distance / result.t[-1]
    expected = numerical_group_velocity(k, c=C, dx=dx, dt=dt)
    assert speed == pytest.approx(expected, rel=0.02)
    assert expected < 0.9 * C


def test_the_group_velocity_equals_c_for_long_waves_and_at_the_limit():
    slow = numerical_group_velocity(1.0, c=C, dx=0.01, dt=0.0025)
    assert slow == pytest.approx(C, rel=1e-4)
    k = np.array([10.0, 100.0, 300.0])
    np.testing.assert_allclose(numerical_group_velocity(k, c=C, dx=0.01, dt=0.005), C)
    with pytest.raises(ValueError, match="too large"):
        numerical_group_velocity(300.0, c=C, dx=0.01, dt=0.01)


def test_centroid_and_packet_have_the_obvious_properties():
    x = np.linspace(0.0, 1.0, 1001)
    packet = wave_packet(x, centre=0.4, width=0.05, k=100.0)
    assert centroid(x, packet) == pytest.approx(0.4, abs=1e-6)
    assert packet[400] == pytest.approx(1.0)
