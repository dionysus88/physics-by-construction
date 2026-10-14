from itertools import pairwise
from math import comb, log

import numpy as np
import pytest

from pbc.abm.gas import mean_and_error
from pbc.thermodynamics import diffusion, entropy, kinetic

# --- diffusion -----------------------------------------------------------------


def test_random_walks_are_a_function_of_the_seed():
    first = diffusion.random_walks(20, 30, 0.1, np.random.default_rng(3))
    again = diffusion.random_walks(20, 30, 0.1, np.random.default_rng(3))
    other = diffusion.random_walks(20, 30, 0.1, np.random.default_rng(4))
    np.testing.assert_array_equal(first, again)
    assert not np.array_equal(first, other)
    assert first.shape == (31, 20, 2)
    np.testing.assert_array_equal(first[0], 0.0)


def test_every_step_has_the_stated_length():
    paths = diffusion.random_walks(50, 40, 0.25, np.random.default_rng(0))
    lengths = np.hypot(*np.diff(paths, axis=0).transpose(2, 0, 1))
    np.testing.assert_allclose(lengths, 0.25)
    line = diffusion.random_walks(50, 40, 0.25, np.random.default_rng(0), dimension=1)
    np.testing.assert_allclose(np.abs(np.diff(line, axis=0)), 0.25)


@pytest.mark.parametrize("dimension", [1, 2])
def test_the_measured_diffusion_coefficient_matches_the_random_walk_prediction(
    dimension,
):
    step, tau, n_steps = 0.1, 0.5, 200
    times = tau * np.arange(n_steps + 1)
    estimates = []
    for seed in range(6):
        paths = diffusion.random_walks(
            500, n_steps, step, np.random.default_rng(seed), dimension
        )
        msd = diffusion.mean_squared_displacement(paths)
        estimates.append(diffusion.diffusion_coefficient(times, msd, dimension))
    mean, error = mean_and_error(np.array(estimates))
    predicted = diffusion.predicted_diffusion_coefficient(step, tau, dimension)
    assert abs(mean - predicted) <= 4.0 * error
    # The tolerance is not so wide that a wrong prediction passes.
    assert abs(mean - 2.0 * predicted) > 4.0 * error


def test_the_mean_squared_displacement_of_one_known_path():
    paths = np.array([[[0.0, 0.0]], [[3.0, 4.0]]])
    np.testing.assert_allclose(diffusion.mean_squared_displacement(paths), [0.0, 25.0])
    # <r²> = 4 D t in the plane: D = 25 / (4 * 5) at t = 5 s.
    assert diffusion.diffusion_coefficient(
        np.array([0.0, 5.0]), np.array([0.0, 25.0])
    ) == (pytest.approx(25.0 / 20.0))


def test_the_fraction_within_a_radius_follows_the_gaussian_prediction():
    step, tau, n_steps = 0.1, 0.5, 100
    d = diffusion.predicted_diffusion_coefficient(step, tau)
    t = tau * n_steps
    radius = np.sqrt(4.0 * d * t * log(2.0))  # the median distance
    assert diffusion.predicted_fraction_within(radius, d, t) == pytest.approx(0.5)
    fractions = [
        diffusion.fraction_within(
            diffusion.random_walks(2000, n_steps, step, np.random.default_rng(s))[-1],
            radius,
        )
        for s in range(6)
    ]
    mean, error = mean_and_error(np.array(fractions))
    assert abs(mean - 0.5) <= 4.0 * error


def test_random_walks_refuse_bad_arguments():
    rng = np.random.default_rng(0)
    with pytest.raises(ValueError):
        diffusion.random_walks(0, 10, 1.0, rng)
    with pytest.raises(ValueError):
        diffusion.random_walks(10, 10, 1.0, rng, dimension=3)


# --- kinetic -------------------------------------------------------------------


def test_the_quantile_inverts_the_distribution_function():
    p = np.linspace(0.05, 0.95, 10)
    v = kinetic.speed_quantile(p, 0.7, 2.0)
    np.testing.assert_allclose(kinetic.speed_cdf(v, 0.7, 2.0), p)


def test_the_distribution_has_the_stated_moments():
    rng = np.random.default_rng(0)
    kt, mass = 0.8, 1.5
    velocities = rng.normal(0.0, np.sqrt(kt / mass), size=(400_000, 2))
    speeds = np.hypot(*velocities.T)
    assert speeds.mean() == pytest.approx(kinetic.mean_speed(kt, mass), rel=5e-3)
    counts, edges = np.histogram(speeds, bins=200)
    peak = 0.5 * (edges[np.argmax(counts)] + edges[np.argmax(counts) + 1])
    assert peak == pytest.approx(kinetic.most_probable_speed(kt, mass), abs=0.05)


def test_the_empirical_distribution_function():
    assert list(
        kinetic.fractions_below(
            np.array([1.0, 2.0, 3.0, 4.0]), np.array([0.5, 2.5, 9.0])
        )
    ) == [
        0.0,
        0.5,
        1.0,
    ]


def test_the_simulated_gas_follows_the_analytic_distribution_at_its_temperature():
    from pbc.abm.gas import measure, temperature

    probabilities = np.array([0.1, 0.25, 0.5, 0.75, 0.9])
    deviations = []
    for seed in range(6):
        m = measure(seed)
        v = kinetic.speed_quantile(probabilities, temperature(m.speeds, 1.0), 1.0)
        deviations.append(kinetic.fractions_below(m.speeds, v) - probabilities)
    mean = np.mean(deviations, axis=0)
    error = np.std(deviations, axis=0, ddof=1) / np.sqrt(6)
    assert np.all(np.abs(mean) <= 4.0 * error)


# --- entropy -------------------------------------------------------------------


def test_log_multiplicity_equals_the_log_of_the_binomial_coefficient():
    n = np.arange(0, 11)
    np.testing.assert_allclose(
        entropy.log_multiplicity(10, n), [log(comb(10, int(k))) for k in n]
    )
    assert entropy.log_multiplicity(10, np.array(3)).shape == (1,)


def test_stirling_approaches_the_exact_multiplicity():
    for n in (10, 100, 1000):
        exact = entropy.log_multiplicity(n, np.array([n // 2]))[0]
        assert abs(entropy.stirling_log_multiplicity_half(n) - exact) < 1.0 / n


def test_the_ensemble_starts_where_it_is_told_and_moves_one_particle_a_step():
    counts = entropy.ehrenfest_ensemble(20, 50, 100, np.random.default_rng(0))
    assert np.all(counts[0] == 20)
    assert set(np.abs(np.diff(counts, axis=0)).ravel()) == {0, 1}
    assert counts.min() >= 0 and counts.max() <= 20
    again = entropy.ehrenfest_ensemble(20, 50, 100, np.random.default_rng(0))
    np.testing.assert_array_equal(counts, again)


def test_the_ensemble_mean_follows_the_exact_formula():
    n, members, steps = 50, 4000, 120
    counts = entropy.ehrenfest_ensemble(n, members, steps, np.random.default_rng(1))
    exact = entropy.mean_left(n, n, np.arange(steps + 1))
    sem = counts.std(axis=1, ddof=1) / np.sqrt(members)
    # Each time is a separate comparison: allow five standard errors.
    assert np.all(np.abs(counts.mean(axis=1) - exact) <= 5.0 * sem + 1e-12)


def test_the_gibbs_entropy_of_equilibrium_is_n_ln_2():
    n = 12
    binomial = np.array([comb(n, k) for k in range(n + 1)]) / 2**n
    assert entropy.gibbs_entropy(binomial, n) == pytest.approx(
        entropy.equilibrium_entropy(n)
    )
    # The Shannon entropy of the macrostate alone is smaller.
    assert entropy.shannon_entropy(binomial) < entropy.equilibrium_entropy(n)


def test_the_gibbs_entropy_of_a_single_macrostate_is_its_boltzmann_entropy():
    n = 12
    p = np.zeros(n + 1)
    p[4] = 1.0
    assert entropy.gibbs_entropy(p, n) == pytest.approx(log(comb(n, 4)))
    p = np.zeros(n + 1)
    p[n] = 1.0
    assert entropy.gibbs_entropy(p, n) == pytest.approx(0.0)


def test_the_exact_gibbs_entropy_never_decreases_under_the_dynamics():
    n = 10
    rows = entropy.exact_distribution(n, n, 300)
    values = [entropy.gibbs_entropy(row, n) for row in rows]
    assert values[0] == pytest.approx(0.0)
    assert all(b >= a - 1e-12 for a, b in pairwise(values))
    assert values[-1] == pytest.approx(entropy.equilibrium_entropy(n), rel=1e-3)
    np.testing.assert_allclose(rows.sum(axis=1), 1.0)


def test_the_exact_distribution_has_the_exact_mean_and_the_binomial_limit():
    n = 10
    rows = entropy.exact_distribution(n, n, 400)
    means = rows @ np.arange(n + 1)
    np.testing.assert_allclose(means, entropy.mean_left(n, n, np.arange(401)))
    binomial = np.array([comb(n, k) for k in range(n + 1)]) / 2**n
    np.testing.assert_allclose(rows[-1], binomial, atol=1e-6)


def test_the_plug_in_estimate_of_the_equilibrium_entropy_is_low_by_the_stated_bias():
    n, members = 12, 20000
    raw, corrected = [], []
    for seed in range(6):
        counts = entropy.ehrenfest_ensemble(
            n, members, 12 * n, np.random.default_rng(seed)
        )
        p = entropy.distribution(counts[-1], n)
        raw.append(entropy.gibbs_entropy(p, n))
        corrected.append(raw[-1] + entropy.plug_in_bias(p, members))
    exact = entropy.equilibrium_entropy(n)
    mean, error = mean_and_error(np.array(corrected))
    assert abs(mean - exact) <= 4.0 * error
    raw_mean, raw_error = mean_and_error(np.array(raw))
    assert exact - raw_mean > 4.0 * raw_error


def test_plug_in_bias_counts_the_observed_macrostates():
    assert entropy.plug_in_bias(np.array([0.5, 0.5, 0.0]), 100) == pytest.approx(
        1 / 200
    )


def test_ehrenfest_refuses_bad_arguments():
    rng = np.random.default_rng(0)
    with pytest.raises(ValueError):
        entropy.ehrenfest_ensemble(0, 10, 10, rng)
    with pytest.raises(ValueError):
        entropy.ehrenfest_ensemble(10, 10, 10, rng, n_start=11)
