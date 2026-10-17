"""The experiment of "The double pendulum and chaos" (mechanics 13)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.mechanics.experiments.double_pendulum_chaos"
PAGE = "mechanics/13-double-pendulum-chaos"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("double_pendulum_chaos")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_the_normal_modes_have_their_closed_form_periods(results):
    _, found = results

    for _, analytic, simulated in found["tables"]["modes-and-energy"]["rows"]:
        assert float(simulated) == pytest.approx(float(analytic), rel=1e-3)


def test_only_the_chaotic_start_has_a_positive_exponent(results):
    _, found = results
    rows = {row[0]: row for row in found["tables"]["lyapunov-table"]["rows"]}

    assert float(rows["chaotic"][3]) > 1.0
    assert float(rows["regular"][3]) < 0.1


def test_the_estimator_finds_a_known_exponent(results):
    _, found = results
    (row,) = found["tables"]["known-exponent"]["rows"]

    assert float(row[2]) < 1e-2
