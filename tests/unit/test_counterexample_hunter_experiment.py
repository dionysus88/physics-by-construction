"""The experiment of "A counterexample hunter" (agents-llm 02)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.mechanics.experiments.counterexample_hunter"
PAGE = "agents-llm/02-a-counterexample-hunter"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("counterexample_hunter")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_only_the_valid_experiment_runs(results):
    _, found = results
    lines = found["outputs"]["bounds"].splitlines()

    assert lines[0].startswith("a valid experiment: 0.")
    assert len(lines) == 7


def test_the_judge_decides_from_the_results_not_the_words(results):
    _, found = results
    said = found["outputs"]["what-the-agent-says"].splitlines()

    assert said[0].endswith("counterexample")
    assert not said[1].endswith(": counterexample")
    assert "counterexample" not in found["outputs"]["forged-results"].split(":")[1]
