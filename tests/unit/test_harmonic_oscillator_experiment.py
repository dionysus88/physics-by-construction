"""The experiment of "The harmonic oscillator" (mechanics 04)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.mechanics.experiments.harmonic_oscillator"
PAGE = "mechanics/04-harmonic-oscillator"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("harmonic_oscillator")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_the_energy_grows_by_the_derived_factor_at_every_step(results):
    _, found = results
    numbers = found["numbers"]

    assert float(numbers["deviation"]) < 1e-12
    assert numbers["final-energy"] == numbers["predicted-energy"]
    assert float(numbers["plane-deviation"]) < 1e-12


def test_the_logarithm_of_the_growth_is_first_order(results):
    _, found = results
    last = found["tables"]["energy-growth"]["rows"][-1]

    assert float(last[4]) == pytest.approx(1.0, abs=0.01)


def test_ten_periods_stay_within_one_per_cent(results):
    _, found = results

    assert 0 < float(found["numbers"]["growth-percent"]) <= 1.0
