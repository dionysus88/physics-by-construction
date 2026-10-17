"""The experiment of "Newton's laws" (mechanics 02)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.mechanics.experiments.newtons_laws"
PAGE = "mechanics/02-newtons-laws"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("newtons_laws")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_the_simulation_follows_the_formula_of_the_method(results):
    _, found = results

    # Explicit Euler's v_n is exactly the derived formula, up to round-off.
    assert float(found["numbers"]["formula-gap"]) < 1e-12
    # The position error is first order.
    assert float(found["numbers"]["last-order"]) == pytest.approx(1.0, abs=0.01)


def test_a_step_above_twice_the_time_constant_is_unstable(results):
    _, found = results
    rows = found["tables"]["large-step-velocity"]["rows"]
    terminal = float(found["numbers"]["terminal-speed"])

    settling = [abs(float(row[1]) - terminal) for row in rows[1:]]
    growing = [abs(float(row[2]) - terminal) for row in rows[1:]]
    assert settling[-1] < settling[0]
    assert growing[-1] > growing[0]


def test_the_simulation_reaches_the_terminal_speed_slightly_early(results):
    _, found = results

    assert float(found["numbers"]["reached"]) <= float(found["numbers"]["predicted"])
