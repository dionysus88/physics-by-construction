"""The experiment of "Projectile motion with drag" (mechanics 03)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.mechanics.experiments.projectile_with_drag"
PAGE = "mechanics/03-projectile-motion-with-drag"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("projectile_with_drag")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_drag_shortens_the_throw_and_flattens_the_best_angle(results):
    _, found = results
    rows = {row[0]: row for row in found["tables"]["longest-throws"]["rows"]}

    assert float(rows["with drag"][1]) < float(rows["without drag"][1])
    assert float(rows["with drag"][2]) < 45.0
    assert float(rows["without drag"][2]) == pytest.approx(45.0, abs=0.1)


def test_the_range_converges_at_first_order(results):
    _, found = results

    assert float(found["numbers"]["last-order"]) == pytest.approx(1.0, abs=0.02)


def test_the_refinement_ends_below_a_millimetre(results):
    _, found = results
    last = found["tables"]["refinement"]["rows"][-1]

    assert float(last[2]) < 0.001
