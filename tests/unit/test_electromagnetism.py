"""The fields of charges, charged-particle motion, and induction (lessons EM1,
EM2, EM3): each result is compared with a closed-form solution or a limiting
case, with a stated tolerance."""

import numpy as np
import pytest

from pbc.electromagnetism.fields import (
    COULOMB_CONSTANT,
    EPSILON_0,
    coulomb_field,
    coulomb_potential,
    dipole_field,
    dipole_potential,
    field_from_potential,
    sphere_flux,
)
from pbc.electromagnetism.induction import (
    Rectangle,
    emf,
    flux,
    flux_rate,
    flux_tube_fields,
    rotating_coil,
)
from pbc.electromagnetism.motion import (
    ELECTRON_CHARGE_TO_MASS,
    PROTON_CHARGE_TO_MASS,
    boris,
    boris_frequency,
    boris_radius,
    cyclotron_frequency,
    drift_velocity,
    euler_energy_factor,
    explicit_euler,
    fitted_radius,
    guiding_centre_velocity,
    larmor_radius,
    measured_angular_frequency,
)
from pbc.verification.estimates import fitted_order

CHARGE = 1e-9  # C
SEPARATION = 0.01  # m
PAIR = np.array([[0.0, 0.0, SEPARATION / 2], [0.0, 0.0, -SEPARATION / 2]])
SIGNS = np.array([CHARGE, -CHARGE])
DIRECTIONS = np.array(
    [[1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 0.6, 0.8], [1.0, 1.0, 1.0] / np.sqrt(3)]
)


def relative(a, b):
    return np.linalg.norm(a - b, axis=-1) / np.linalg.norm(b, axis=-1)


# EM1: the fields of charges


def test_the_field_of_one_charge_falls_with_the_inverse_square_and_points_away():
    points = np.array([[0.1, 0.0, 0.0], [0.0, -0.2, 0.0], [0.0, 0.0, 0.4]])
    field = coulomb_field(points, [CHARGE], [[0.0, 0.0, 0.0]])
    r = np.linalg.norm(points, axis=-1)
    expected = COULOMB_CONSTANT * CHARGE / r**2
    np.testing.assert_allclose(np.linalg.norm(field, axis=-1), expected, rtol=1e-14)
    np.testing.assert_allclose(
        field / expected[:, None], points / r[:, None], atol=1e-14
    )


def test_the_field_of_several_charges_is_the_sum_of_their_fields():
    charges = np.array([1e-9, -2e-9, 0.5e-9])
    positions = np.array([[0.0, 0.0, 0.0], [0.1, 0.0, 0.0], [0.0, 0.1, 0.05]])
    points = np.array([[0.3, 0.2, -0.1], [-0.05, 0.02, 0.07]])
    single = sum(
        coulomb_field(points, [q], [p]) for q, p in zip(charges, positions, strict=True)
    )
    np.testing.assert_allclose(
        coulomb_field(points, charges, positions), single, rtol=1e-13
    )


def test_the_field_is_minus_the_gradient_of_the_potential_with_order_two():
    point = np.array([[0.03, 0.01, 0.02]])
    exact = coulomb_field(point, SIGNS, PAIR)
    steps = [1e-3, 5e-4, 2.5e-4, 1.25e-4]
    errors = [
        relative(
            field_from_potential(lambda p: coulomb_potential(p, SIGNS, PAIR), point, h),
            exact,
        )[0]
        for h in steps
    ]
    assert fitted_order(steps, errors) == pytest.approx(2.0, abs=0.05)
    assert errors[-1] < 1e-4


def test_the_field_of_a_pair_approaches_the_dipole_field_as_the_square_of_d_over_r():
    distances = np.array([0.4, 0.2, 0.1, 0.05])
    moment = [0.0, 0.0, CHARGE * SEPARATION]
    gaps = [
        np.max(
            relative(
                coulomb_field(r * DIRECTIONS, SIGNS, PAIR),
                dipole_field(r * DIRECTIONS, moment),
            )
        )
        for r in distances
    ]
    # the gap falls as (d/r)^2: as r^-2, so its order in d/r is two
    assert fitted_order(SEPARATION / distances[::-1], gaps[::-1]) == pytest.approx(
        2.0, abs=0.05
    )
    assert gaps[0] < 1e-3


def test_the_potential_of_a_pair_approaches_the_dipole_potential():
    moment = [0.0, 0.0, CHARGE * SEPARATION]
    points = 0.5 * DIRECTIONS
    np.testing.assert_allclose(
        coulomb_potential(points, SIGNS, PAIR),
        dipole_potential(points, moment),
        rtol=5e-4,
    )


def test_the_flux_through_a_sphere_is_the_enclosed_charge_over_epsilon_0():
    charges = np.array([1e-9, 2e-9, -0.5e-9, 3e-9])
    positions = np.array(
        [[0.1, 0.0, 0.0], [0.0, 0.2, 0.1], [-0.3, 0.0, 0.0], [2.0, 0.0, 0.0]]
    )
    inside = charges[:3].sum()
    found = sphere_flux(lambda p: coulomb_field(p, charges, positions), radius=1.0)
    assert found * EPSILON_0 / inside == pytest.approx(1.0, abs=1e-10)


def test_a_charge_outside_the_sphere_gives_no_net_flux():
    found = sphere_flux(
        lambda p: coulomb_field(p, [1e-9], [[0.0, 0.0, 3.0]]), radius=1.0
    )
    assert abs(found) * EPSILON_0 / 1e-9 < 1e-12


def test_a_field_at_a_charge_is_refused():
    with pytest.raises(ValueError):
        coulomb_field([[0.0, 0.0, 0.0]], [CHARGE], [[0.0, 0.0, 0.0]])


# EM2: charged particles in fields

OMEGA = cyclotron_frequency(PROTON_CHARGE_TO_MASS, 1.0)
SPEED = 1e5  # m/s
PERIOD = 2 * np.pi / OMEGA


def gyration(steps_per_period: int, periods: int = 10, push=boris):
    dt = PERIOD / steps_per_period
    return dt, push(
        [0.0, 0.0, 0.0],
        [SPEED, 0.0, 0.0],
        q_over_m=PROTON_CHARGE_TO_MASS,
        electric=[0.0, 0.0, 0.0],
        magnetic=[0.0, 0.0, 1.0],
        dt=dt,
        n_steps=periods * steps_per_period,
    )


def test_the_boris_frequency_is_its_closed_form_and_converges_with_order_two():
    steps, errors = [], []
    for n in (20, 40, 80, 160):
        dt, run = gyration(n)
        found = measured_angular_frequency(run.t, run.v)
        assert found == pytest.approx(boris_frequency(OMEGA, dt), rel=1e-12)
        steps.append(dt)
        errors.append(abs(found / OMEGA - 1.0))
    assert fitted_order(steps, errors) == pytest.approx(2.0, abs=0.02)
    # to the lowest order the gap is (omega dt)^2 / 12
    assert errors[-1] == pytest.approx((OMEGA * steps[-1]) ** 2 / 12, rel=1e-3)


def test_the_boris_radius_is_its_closed_form_and_converges_to_the_larmor_radius():
    exact = larmor_radius(PROTON_CHARGE_TO_MASS, 1.0, SPEED)
    steps, errors = [], []
    for n in (20, 40, 80, 160):
        dt, run = gyration(n)
        radius = fitted_radius(run.x)
        assert radius == pytest.approx(boris_radius(OMEGA, dt, SPEED), rel=1e-10)
        steps.append(dt)
        errors.append(abs(radius / exact - 1.0))
    assert fitted_order(steps, errors) == pytest.approx(2.0, abs=0.02)


def test_boris_keeps_the_speed_and_euler_grows_the_energy_as_predicted():
    dt, run = gyration(40)
    speeds = np.linalg.norm(run.v, axis=1)
    assert np.max(np.abs(speeds / SPEED - 1.0)) < 1e-13
    _, euler = gyration(40, push=explicit_euler)
    energy = np.sum(euler.v**2, axis=1)
    steps = len(energy) - 1
    assert energy[-1] / energy[0] == pytest.approx(
        euler_energy_factor(OMEGA, dt) ** steps, rel=1e-10
    )


def test_an_electron_turns_the_other_way_at_its_own_frequency():
    omega = cyclotron_frequency(ELECTRON_CHARGE_TO_MASS, 1e-3)
    dt = 2 * np.pi / omega / 200
    run = boris(
        [0.0, 0.0, 0.0],
        [SPEED, 0.0, 0.0],
        q_over_m=ELECTRON_CHARGE_TO_MASS,
        electric=[0.0, 0.0, 0.0],
        magnetic=[0.0, 0.0, 1e-3],
        dt=dt,
        n_steps=400,
    )
    # a negative charge turns counterclockwise about B: v_y grows at first
    assert run.v[1, 1] > 0
    assert measured_angular_frequency(run.t, run.v) == pytest.approx(
        boris_frequency(omega, dt), rel=1e-12
    )


def test_in_crossed_fields_the_centre_drifts_with_e_cross_b_over_b_squared():
    electric = np.array([0.0, 1e4, 0.0])
    magnetic = np.array([0.0, 0.0, 1.0])
    dt = PERIOD / 50
    run = boris(
        [0.0, 0.0, 0.0],
        [SPEED, 0.0, 2e4],
        q_over_m=PROTON_CHARGE_TO_MASS,
        electric=electric,
        magnetic=magnetic,
        dt=dt,
        n_steps=5000,
    )
    expected = drift_velocity(electric, magnetic)
    omega = measured_angular_frequency(run.t, run.v, drift=expected)
    found = guiding_centre_velocity(run.t, run.x, omega)
    np.testing.assert_allclose(found[:2], expected[:2], atol=1e-8 * SPEED)
    # along B nothing pushes, so the speed along it stays
    assert found[2] == pytest.approx(2e4, rel=1e-12)


# EM3: induction

BUMP = 0.05  # m
PEAK = 0.5  # T
SPEED_OF_LOOP = 2.0  # m/s


def bump(points):
    x = points[..., 0]
    return np.stack([0 * x, 0 * x, PEAK * np.exp(-(x**2) / BUMP**2)], axis=-1)


def moving_loop(t):
    return Rectangle(
        [SPEED_OF_LOOP * t - 0.02, -0.03, 0.0], [0.04, 0.0, 0.0], [0.0, 0.06, 0.0]
    )


def uniform(vector):
    return lambda points: np.broadcast_to(np.asarray(vector, dtype=float), points.shape)


def test_the_flux_of_a_uniform_field_is_the_field_times_the_projected_area():
    loop = Rectangle([0.0, 0.0, 0.0], [0.3, 0.0, 0.0], [0.0, 0.1, 0.2])
    field = np.array([0.1, -0.2, 0.7])
    assert flux(uniform(field), loop) == pytest.approx(
        field @ np.cross(loop.side_a, loop.side_b), rel=1e-13
    )


def test_a_field_with_no_curl_has_no_emf_around_a_loop():
    loop = Rectangle([0.2, -0.1, 0.05], [0.1, 0.05, 0.0], [-0.02, 0.04, 0.1])
    found = emf(loop, electric=lambda p: coulomb_field(p, [1e-9], [[0.0, 0.0, 0.0]]))
    scale = COULOMB_CONSTANT * 1e-9 / 0.2
    assert abs(found) < 1e-12 * scale


@pytest.mark.parametrize("t", [-0.04, -0.012, 0.007, 0.03])
def test_the_motional_emf_of_a_loop_in_a_non_uniform_field_is_minus_the_flux_rate(t):
    found = emf(
        moving_loop(t), magnetic=bump, velocity=uniform([SPEED_OF_LOOP, 0.0, 0.0])
    )
    rate = flux_rate(lambda s: flux(bump, moving_loop(s)), t, 1e-5)
    # the closed form: -v h (B(x_right) - B(x_left))
    right, left = SPEED_OF_LOOP * t + 0.02, SPEED_OF_LOOP * t - 0.02
    exact = (
        -SPEED_OF_LOOP
        * 0.06
        * PEAK
        * (np.exp(-(right**2) / BUMP**2) - np.exp(-(left**2) / BUMP**2))
    )
    assert found == pytest.approx(exact, rel=1e-12)
    assert found == pytest.approx(-rate, rel=1e-6)


def test_the_emf_of_a_rotating_coil_is_b_a_omega_sin_omega_t():
    omega = 2 * np.pi * 50.0
    field = np.array([0.3, 0.0, 0.0])
    for t in (0.001, 0.0037, 0.012):
        coil = rotating_coil(t, angular_velocity=omega, width=0.1, height=0.2)
        found = emf(
            coil,
            magnetic=uniform(field),
            velocity=lambda p: np.cross([0.0, 0.0, omega], p),
        )
        rate = flux_rate(
            lambda s: flux(
                uniform(field),
                rotating_coil(s, angular_velocity=omega, width=0.1, height=0.2),
            ),
            t,
            1e-7,
        )
        expected = 0.3 * 0.02 * omega * np.sin(omega * t)
        assert found == pytest.approx(expected, rel=1e-12)
        assert -rate == pytest.approx(expected, rel=1e-6)


def test_the_flux_tube_fields_are_the_curl_and_minus_the_rate_of_their_potential():
    width, strength, rate = 0.02, 1.2, 10.0
    point = np.array([0.013, -0.007, 0.0])

    def potential(p, b0):
        r2 = p[0] ** 2 + p[1] ** 2
        magnitude = b0 * width**2 * (1 - np.exp(-r2 / width**2)) / (2 * r2)
        return magnitude * np.array([-p[1], p[0], 0.0])

    h = 1e-6
    # B_z = dA_y/dx - dA_x/dy
    dx, dy = np.array([h, 0, 0]), np.array([0, h, 0])
    curl_z = (
        (potential(point + dx, strength)[1] - potential(point - dx, strength)[1])
        - (potential(point + dy, strength)[0] - potential(point - dy, strength)[0])
    ) / (2 * h)
    electric, magnetic = flux_tube_fields(
        point, strength=strength, rate=rate, width=width
    )
    assert magnetic[2] == pytest.approx(curl_z, rel=1e-7)
    # E = -dA/dt, with B0 changing at the rate
    np.testing.assert_allclose(electric, -potential(point, rate), rtol=1e-12)
    on_axis, _ = flux_tube_fields(
        np.zeros(3), strength=strength, rate=rate, width=width
    )
    np.testing.assert_array_equal(on_axis, np.zeros(3))


@pytest.mark.parametrize(
    "loop",
    [
        Rectangle([-0.05, -0.04, 0.0], [0.09, 0.0, 0.0], [0.0, 0.07, 0.0]),
        Rectangle([0.04, -0.02, 0.0], [0.03, 0.0, 0.0], [0.0, 0.03, 0.0]),
        Rectangle([-0.01, -0.005, 0.0], [0.03, 0.0, 0.0], [0.0, 0.03, 0.0]),
    ],
    ids=["around", "beside", "across"],
)
def test_the_emf_at_a_changing_flux_tube_is_minus_the_flux_rate(loop):
    width, rate = 0.02, 10.0

    def field_at(t):
        return lambda p: flux_tube_fields(
            p, strength=1.0 + rate * t, rate=rate, width=width
        )[1]

    found = emf(
        loop,
        electric=lambda p: flux_tube_fields(p, strength=1.0, rate=rate, width=width)[0],
        nodes=48,
    )
    change = flux_rate(lambda t: flux(field_at(t), loop, nodes=48), 0.0, 1e-3)
    assert found == pytest.approx(-change, rel=1e-9, abs=1e-15)


def test_a_rectangle_with_sides_not_at_right_angles_is_refused():
    with pytest.raises(ValueError):
        Rectangle([0, 0, 0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0])
