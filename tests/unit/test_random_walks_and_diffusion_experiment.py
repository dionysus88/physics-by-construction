"""The experiment of "Random walks and diffusion" (thermodynamics 01)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.thermodynamics.experiments.random_walks_and_diffusion"
PAGE = "thermodynamics/01-random-walks-and-diffusion"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("random_walks_and_diffusion")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_the_measured_coefficient_tells_the_step_rule_from_a_wrong_one(results):
    _, found = results

    assert float(found["numbers"]["off"]) < 3.0
    assert float(found["numbers"]["wrong"]) > 10.0


def test_doubling_the_step_quadruples_the_coefficient(results):
    _, found = results
    ((measured, predicted, error),) = found["tables"]["doubled-step"]["rows"]

    assert abs(float(measured) - float(predicted)) < 3 * float(error)
