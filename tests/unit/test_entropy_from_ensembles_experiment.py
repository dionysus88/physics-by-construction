"""The experiment of "Entropy from ensembles" (thermodynamics 03)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.thermodynamics.experiments.entropy_from_ensembles"
PAGE = "thermodynamics/03-entropy-from-ensembles"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("entropy_from_ensembles")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_the_two_ways_of_counting_agree(results):
    _, found = results

    for row in found["tables"]["counting"]["rows"]:
        assert row[2] == row[3]


def test_the_corrected_estimate_finds_the_equilibrium_entropy(results):
    _, found = results

    assert float(found["numbers"]["corrected-largest"]) < 3.0
    assert float(found["numbers"]["mean-distance"]) < 4.0
