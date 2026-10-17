"""The experiment of "Verifying scientific code" (mechanics 09)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.mechanics.experiments.verifying_scientific_code"
PAGE = "mechanics/09-verifying-scientific-code"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("verifying_scientific_code")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_the_correct_steppers_pass_every_check_they_claim(results):
    _, found = results

    assert "FAIL" not in found["outputs"]["correct"]


def test_every_faulty_stepper_fails_a_check(results):
    _, found = results
    matrix = found["outputs"]["gallery"].split("\n\n")[0].splitlines()[1:]

    assert matrix
    assert all("FAIL" in line for line in matrix)


def test_only_the_true_order_of_verlet_passes(results):
    _, found = results
    lines = found["outputs"]["claimed-orders"].splitlines()

    assert [line.split(":")[1].split()[0] for line in lines] == ["FAIL", "pass", "FAIL"]
