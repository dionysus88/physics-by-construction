"""The experiment of "An agent runs an experiment" (agents-llm 01)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.mechanics.experiments.agent_experiment"
PAGE = "agents-llm/01-an-agent-runs-an-experiment"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("agent_experiment")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_only_the_well_formed_call_runs(results):
    _, found = results
    outcomes = [row[3] for row in found["tables"]["misbehaving-calls"]["rows"]]

    assert outcomes[0] == "ran"
    assert all(outcome != "ran" for outcome in outcomes[1:])


def test_the_replay_runs_without_a_model_and_catches_a_changed_ball(results):
    _, found = results

    assert "This build did not call a model." in found["displays"]["run"]
    assert found["outputs"]["rough-ball"].strip()


def test_the_scan_confirms_the_agent_s_bracket(results):
    _, found = results
    numbers = found["numbers"]

    assert float(numbers["bracket-low"]) <= float(numbers["best-angle"])
    assert float(numbers["best-angle"]) <= float(numbers["bracket-high"])
