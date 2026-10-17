"""The experiment of "Unlearning a familiar law: a modified force" (agents-llm 07)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.mechanics.experiments.modified_force_law"
PAGE = "agents-llm/07-a-modified-force-law"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("modified_force_law")
    return directory, run_entry_point(MODULE, directory)


def _rows(found: dict, name: str) -> dict[str, list[str]]:
    return {row[0]: row[1:] for row in found["tables"][name]["rows"]}


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_the_familiar_law_is_rejected_and_least_squares_recovers_the_modified_one(
    results,
):
    _, found = results
    baselines = _rows(found, "d3-baselines")

    assert _rows(found, "d3-familiar")["verdict"] == ["rejected"]
    assert baselines["grid + least squares"][3] == "yes"
    assert baselines["random + least squares"][3] == "yes"
    assert baselines["grid + inverse-square law"][3] == "no"
    assert _rows(found, "d3-agent-familiar")[
        "the agent's readings, inverse-square law"
    ][0] == ("rejected")


def test_the_agent_is_reported_as_scored_and_its_strength_departs_from_its_readings(
    results,
):
    _, found = results
    score = _rows(found, "d3-score")
    readings = _rows(found, "d3-agent-readings")

    assert found["numbers"]["outcome"] == score["outcome"][0]
    assert score["claimed exponent"] != ["2"]
    exponent = "agent's claimed exponent minus fit, in standard errors"
    strength = "agent's claimed strength minus fit, in standard errors"
    assert abs(float(readings[exponent][0])) < 1
    assert abs(float(readings[strength][0])) > 3


def test_the_chi_square_sees_a_modification_before_the_held_out_error_does(results):
    _, found = results
    rows = found["tables"]["small-modifications"]["rows"]

    assert any(test == "rejected" and within == "yes" for _, test, _, within in rows)
