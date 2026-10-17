"""The experiment of "Kinetic theory of gases" (thermodynamics 02)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.thermodynamics.experiments.kinetic_theory_of_gases"
PAGE = "thermodynamics/02-kinetic-theory-of-gases"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("kinetic_theory_of_gases")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_the_speeds_follow_the_maxwell_distribution_at_the_measured_temperature(
    results,
):
    _, found = results

    assert float(found["numbers"]["largest-distance"]) < 4.0
    assert float(found["numbers"]["ratio-distance"]) < 4.0


def test_a_wrong_temperature_is_rejected(results):
    _, found = results

    assert int(found["numbers"]["wrong-failures"]) >= 1
