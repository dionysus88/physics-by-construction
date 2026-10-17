"""The experiment of "An experimental design agent" (agents-llm 04)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.mechanics.experiments.experimental_design_agent"
PAGE = "agents-llm/04-an-experimental-design-agent"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("experimental_design_agent")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_a_spread_of_start_speeds_is_the_best_design_by_far(results):
    _, found = results
    lines = found["outputs"]["three-designs"].splitlines()
    threshold = float(lines[-1].split(": ")[1])
    low, times, speeds = (float(line.rsplit("score ", 1)[1]) for line in lines[:-1])

    assert low < threshold
    assert speeds > 10 * max(low, times, threshold)


def test_a_fifth_reading_raises_the_score(results):
    _, found = results
    four, five = (
        float(line.split()[1])
        for line in found["outputs"]["a-fifth-reading"].splitlines()
    )

    assert five > four
