"""The experiment of "Full, partial, and no prior knowledge under one protocol"
(agents-llm 06)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.mechanics.experiments.prior_knowledge_in_discovery"
PAGE = "agents-llm/06-prior-knowledge-in-discovery"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("prior_knowledge_in_discovery")
    return directory, run_entry_point(MODULE, directory)


def _rows(found: dict, name: str) -> dict[str, list[str]]:
    return {row[0]: row[1:] for row in found["tables"][name]["rows"]}


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_only_the_task_text_differs_between_the_conditions(results):
    _, found = results
    shared = _rows(found, "d2-fairness")

    assert shared.pop("task text") == ["differs"]
    assert all(value == ["same"] for value in shared.values())


def test_the_conditions_are_scored_as_they_are_and_every_run_had_the_information(
    results,
):
    _, found = results
    tolerance = float(found["numbers"]["tolerance"])
    scores = _rows(found, "d2-scores")
    fits = _rows(found, "d2-probe-fits")

    assert {c: row[-1] for c, row in scores.items()} == {
        "full": "recovered",
        "partial": "not recovered",
        "none": "not recovered",
    }
    assert {row[0] for row in scores.values()} == {found["numbers"]["probes"]}
    assert all(float(row[4]) <= tolerance for row in fits.values())


def test_the_phase_shift_grows_with_the_time(results):
    _, found = results
    shift = _rows(found, "phase-shift")

    assert float(shift["9"][0]) > 2 * float(shift["3"][0])
