"""The experiment of "The Kepler orbit" (mechanics 08)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.mechanics.experiments.kepler_orbit"
PAGE = "mechanics/08-kepler-orbit"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("kepler_orbit")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_the_symplectic_methods_keep_the_angular_momentum(results):
    _, found = results
    rows = {row[0]: row for row in found["tables"]["four-methods-two-orbits"]["rows"]}

    assert rows["symplectic Euler"][3] == "below 1e-12"
    assert rows["velocity Verlet"][3] == "below 1e-12"


def test_kepler_s_third_law_holds_in_years_and_astronomical_units(results):
    _, found = results

    # T^2 / a^3 = 4 pi^2 / GM = 1 in these units.
    assert float(found["numbers"]["third-law-mean"]) == pytest.approx(1.0, abs=1e-3)


def test_the_two_bodies_agree_with_the_one_body_run(results):
    _, found = results
    rows = {row[0]: row for row in found["tables"]["two-body-simulation"]["rows"]}

    assert rows["drift of the centre of mass below the bound"][2] == "yes"
    assert rows["difference from the one-body run below the bound"][2] == "yes"
