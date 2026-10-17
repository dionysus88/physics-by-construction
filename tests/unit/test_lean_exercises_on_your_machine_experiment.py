"""The experiment of "Lean exercises on your machine" (lean 04)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.mechanics.experiments.lean_exercises_on_your_machine"
PAGE = "lean/04-lean-exercises-on-your-machine"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("lean_exercises_on_your_machine")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_both_sides_of_each_statement_agree(results):
    _, found = results
    values = [
        float(line.split("=")[1].split()[0])
        for line in found["outputs"]["both-sides"].splitlines()
    ]

    # Equal to the four decimals printed, up to the rounding of the last one.
    for left, right in zip(values[::2], values[1::2], strict=True):
        assert left == pytest.approx(right, abs=1.5e-4)
