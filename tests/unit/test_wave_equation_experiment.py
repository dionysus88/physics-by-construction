"""The experiment of "The wave equation" (waves 01)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.waves.experiments.wave_equation"
PAGE = "waves/01-the-wave-equation"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("wave_equation")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_the_scheme_is_second_order(results):
    _, found = results

    assert float(found["numbers"]["pulse-order"]) == pytest.approx(2.0, abs=0.1)
    assert float(found["numbers"]["mode-order"]) == pytest.approx(2.0, abs=0.1)


def test_above_the_limit_the_zigzag_grows_as_predicted(results):
    _, found = results

    for row in found["tables"]["cfl-run"]["rows"]:
        if row[2]:
            assert float(row[2]) == pytest.approx(float(row[3]), rel=0.01)


def test_a_free_end_returns_the_pulse_upright(results):
    _, found = results

    assert float(found["numbers"]["returned-min"]) >= 0.0
