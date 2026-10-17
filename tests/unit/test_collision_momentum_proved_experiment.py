"""The experiment of "Momentum in a collision, proved" (lean 02)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.mechanics.experiments.collision_momentum_proved"
PAGE = "lean/02-momentum-in-a-collision-proved"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("collision_momentum_proved")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_the_collision_keeps_the_momentum_to_round_off(results):
    _, found = results

    for row in found["tables"]["random-collisions"]["rows"]:
        assert float(row[2]) < 1e-12


def test_equal_coefficients_break_the_momentum(results):
    _, found = results
    wrong, right = found["tables"]["two-rules"]["rows"]

    assert float(wrong[1]) != 0.0
    assert all(abs(float(value)) < 1e-12 for value in right[1:])
