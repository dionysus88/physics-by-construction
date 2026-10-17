"""The experiment of "Energy conservation" (mechanics 06)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.mechanics.experiments.energy_conservation"
PAGE = "mechanics/06-energy-conservation"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("energy_conservation")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_the_simulated_period_is_the_elliptic_integral(results):
    _, found = results

    for row in found["tables"]["period-table"]["rows"]:
        assert row[3] == row[1]


def test_the_drift_falls_at_the_order_of_each_method(results):
    _, found = results
    last = found["tables"]["drift-orders"]["rows"][-1]

    # Explicit Euler and the two symplectic methods: the energy error of
    # their order; Runge-Kutta 4 at its order or beyond.
    assert float(last[2]) == pytest.approx(1.0, abs=0.15)
    assert float(last[6]) == pytest.approx(2.0, abs=0.1)
    assert float(last[8]) >= 3.5


def test_explicit_euler_carries_the_pendulum_over_the_top(results):
    _, found = results
    rows = {row[0]: row for row in found["tables"]["near-the-top"]["rows"]}

    assert float(rows["explicit Euler"][2]) > 1.0
    assert float(rows["velocity Verlet"][2]) < 1.0
