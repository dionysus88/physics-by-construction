"""The experiment of "Three reviewers" (agents-llm 03)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.mechanics.experiments.scientific_review"
PAGE = "agents-llm/03-three-reviewers"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("scientific_review")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_the_faulty_piece_gains_energy(results):
    _, found = results

    assert float(found["numbers"]["growth"]) > 1.0


def test_a_boasting_reviewer_is_judged_by_what_it_ran(results):
    _, found = results

    assert "FAILED" in found["outputs"]["boasting-reviewer"]


def test_only_the_faulty_piece_fails_a_check(results):
    _, found = results
    lines = found["outputs"]["every-check"].splitlines()

    assert all("FAIL" not in line for line in lines if line.startswith("piece 1"))
    assert any("FAIL" in line for line in lines if line.startswith("piece 2"))
