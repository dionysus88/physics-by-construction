"""The experiment of "Particles in a box" (agents-abm 01).

The deterministic invariants of the page come first: the command writes what
the page shows, a seed reproduces its run, and the verdicts of the table
follow from its numbers by the rule. The statistical checks follow, by the
rule of the lesson (``pbc.abm.acceptance``): twelve independent runs, a
tolerance of a stated allowance plus t standard errors, a false-failure
probability of at most one in a thousand per check. They run on the page's
seeds and on an independent second block of seeds, because a machine whose
floating-point libraries round differently draws, in effect, another sample.
"""

from pathlib import Path

import numpy as np
import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

from pbc.abm.acceptance import FALSE_FAILURE, agreement, t_factor
from pbc.abm.gas import N_DISCS, measure, speed_ratio, virial_correction
from pbc.thermodynamics.experiments.particles_in_a_box import (
    PRESSURE_ALLOWANCE,
    SEEDS,
    TIME_STEP_SHIFT,
    WALL_SHIFT,
    next_virial_term,
    ratio_allowance,
)

MODULE = "pbc.thermodynamics.experiments.particles_in_a_box"
PAGE = "agents-abm/01-particles-in-a-box"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("particles_in_a_box")
    return directory, run_entry_point(MODULE, directory)


def rows_of(found: dict) -> dict[str, list[str]]:
    return {row[0]: row[1:] for row in found["tables"]["kinetic-theory-check"]["rows"]}


# Deterministic invariants.


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_a_seed_reproduces_its_run(results):
    _, found = results

    assert [row[1] for row in found["tables"]["same-seed"]["rows"]] == ["yes", "no"]


def test_the_verdicts_of_the_table_follow_from_its_numbers(results):
    """Each row's verdict is |difference| <= tolerance, and the tolerance is
    the allowance plus t standard errors, to the displayed rounding."""
    _, found = results
    t = t_factor(len(SEEDS))
    allowances = {
        "moment ratio": ratio_allowance(N_DISCS),
        "P / P_ideal": PRESSURE_ALLOWANCE,
        "P / P_ideal against the ideal gas law alone": PRESSURE_ALLOWANCE,
    }

    for name, (mean, error, theory, difference, tolerance, within) in rows_of(
        found
    ).items():
        assert float(difference) == pytest.approx(
            float(mean) - float(theory), abs=1.5e-3
        )
        assert float(tolerance) == pytest.approx(
            allowances[name] + t * float(error), abs=1.5e-3
        )
        assert within == ("yes" if abs(float(difference)) <= float(tolerance) else "no")


def test_the_allowance_covers_its_stated_parts():
    # The allowance is conservative, not proved: the parts are point
    # estimates, so it must stay above their sum with a margin.
    phi = 0.032  # the packing fraction of the page, to its displayed digits
    parts = TIME_STEP_SHIFT + next_virial_term(phi) + WALL_SHIFT

    assert next_virial_term(phi) == pytest.approx(3.128 * phi**2, rel=1e-3)
    assert parts <= PRESSURE_ALLOWANCE
    assert PRESSURE_ALLOWANCE - parts >= 0.002


# Statistical checks on the page's sample, seeds 0 to 11.


def test_the_gas_settles_before_the_measurement(results):
    _, found = results

    assert float(found["numbers"]["settled"]) < float(found["numbers"]["relax"])


def test_the_page_states_the_rule_it_applies(results):
    _, found = results

    assert len(SEEDS) == 12
    assert int(found["numbers"]["n-runs"]) == len(SEEDS)
    assert int(found["numbers"]["false-failure"]) == round(1 / FALSE_FAILURE)


def test_the_relaxed_gas_agrees_with_kinetic_theory_by_the_rule(results):
    _, found = results
    rows = rows_of(found)

    assert rows["moment ratio"][-1] == "yes"
    # The check can tell the relaxed gas from its start of nearly one speed.
    assert float(found["numbers"]["first-ratio"]) < 1.2
    assert float(rows["moment ratio"][4]) < 2.0 - 1.2
    assert rows["P / P_ideal"][-1] == "yes"
    # The correction is real: the ideal gas law alone is outside the rule.
    assert rows["P / P_ideal against the ideal gas law alone"][-1] == "no"
    assert float(rows["P / P_ideal against the ideal gas law alone"][3]) > 0


# Statistical checks on an independent sample, seeds 12 to 23: the sample
# another machine might draw. Each agreement check (the moment ratio and the
# pressure) fails a correct model with a probability of at most one in a
# thousand; with two agreement checks on each of the two blocks (the page's
# sample and this one) the union bound is four in a thousand. The ideal-gas
# rejection is a power check, not a false-failure check.
SECOND_BLOCK = range(12, 24)


@pytest.fixture(scope="module")
def second_block():
    return [measure(seed) for seed in SECOND_BLOCK]


def test_an_independent_sample_reaches_the_same_verdicts(second_block):
    pressures = [m.pressure / m.ideal_pressure for m in second_block]
    predicted = virial_correction(second_block[0].packing_fraction)

    ratio = agreement(
        [speed_ratio(m.speeds) for m in second_block], 2.0, ratio_allowance(N_DISCS)
    )
    assert ratio.agrees
    assert agreement(pressures, predicted, PRESSURE_ALLOWANCE).agrees
    assert not agreement(pressures, 1.0, PRESSURE_ALLOWANCE).agrees


# Regression of the failure of Issue #206. The single runs of the pressure
# scatter around a mean that lies about one run's spread below 1 + 2 phi,
# because of the time step (measured over 240 seeds: mean 1.0542, spread
# 0.0089, prediction 1.0633). The old check, |mean - prediction| < 3
# standard errors of six runs with no allowance, then failed on about two
# samples in five, so its verdict changed with the machine. Synthetic samples
# with the measured mean and spread show the mechanism and that the rule
# removes it; the generator is seeded, so the counts are fixed.
MEASURED_MEAN, MEASURED_SPREAD, PREDICTED = 1.0542, 0.0089, 1.0633
TRIALS = 20_000


def synthetic_runs(mean: float, k: int) -> np.ndarray:
    rng = np.random.default_rng(206)
    return rng.normal(mean, MEASURED_SPREAD, size=(TRIALS, k))


def test_the_old_single_sample_threshold_fails_often_on_the_measured_offset():
    runs = synthetic_runs(MEASURED_MEAN, 6)
    mean = runs.mean(axis=1)
    error = runs.std(axis=1, ddof=1) / np.sqrt(6)

    failures = np.mean(np.abs(mean - PREDICTED) >= 3.0 * error)
    assert 0.3 < failures < 0.55


def agrees(runs: np.ndarray, theory: float) -> np.ndarray:
    """The pressure verdict of the rule for each row of ``runs`` at once; the
    same as ``agreement`` row by row, which is checked on the first rows."""
    k = runs.shape[1]
    mean = runs.mean(axis=1)
    error = runs.std(axis=1, ddof=1) / np.sqrt(k)
    verdicts = np.abs(mean - theory) <= PRESSURE_ALLOWANCE + t_factor(k) * error
    for row, verdict in zip(runs[:50], verdicts[:50], strict=True):
        assert agreement(row, theory, PRESSURE_ALLOWANCE).agrees == verdict
    return verdicts


def test_the_rule_passes_the_measured_offset_and_rejects_the_ideal_gas():
    runs = synthetic_runs(MEASURED_MEAN, len(SEEDS))

    assert agrees(runs, PREDICTED).all()
    assert not agrees(runs, 1.0).any()


def test_the_rule_fails_a_model_at_its_allowance_at_most_at_the_stated_rate():
    """A model whose mean is exactly the allowance away from the prediction is
    the worst case the rule still calls correct: it fails by chance in about
    alpha / 2 of the samples, below the stated alpha."""
    runs = synthetic_runs(PREDICTED - PRESSURE_ALLOWANCE, len(SEEDS))

    assert np.mean(~agrees(runs, PREDICTED)) <= FALSE_FAILURE


def test_the_rule_catches_a_model_wrong_by_more_than_the_tolerance():
    runs = synthetic_runs(PREDICTED - PRESSURE_ALLOWANCE - 0.03, len(SEEDS))

    assert np.mean(~agrees(runs, PREDICTED)) > 0.99
