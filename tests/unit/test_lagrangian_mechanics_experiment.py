"""The experiment of "Lagrangian mechanics" (mechanics 14)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.mechanics.experiments.lagrangian_mechanics"
PAGE = "mechanics/14-lagrangian-mechanics"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("lagrangian_mechanics")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_the_lagrangian_gives_newton_s_equations(results):
    _, found = results

    assert float(found["numbers"]["pendulum-difference"]) < 1e-6
    assert float(found["numbers"]["path-gap"]) < 1e-9


def test_the_planet_keeps_its_angular_momentum_and_closes_its_orbit(results):
    _, found = results

    assert float(found["numbers"]["momentum-change"]) < 1e-6
    assert float(found["numbers"]["turns"]) == pytest.approx(1.0, abs=1e-3)


def test_the_double_pendulum_matches_the_closed_form(results):
    _, found = results
    ((accelerations, angles),) = found["tables"]["double-pendulum-check"]["rows"]

    assert float(accelerations) < 1e-5
    assert float(angles) < 1e-5
