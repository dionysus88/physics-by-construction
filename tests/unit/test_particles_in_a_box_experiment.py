"""The experiment of "Particles in a box" (agents-abm 01)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.thermodynamics.experiments.particles_in_a_box"
PAGE = "agents-abm/01-particles-in-a-box"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("particles_in_a_box")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_the_gas_settles_before_the_measurement(results):
    _, found = results

    assert float(found["numbers"]["settled"]) < float(found["numbers"]["relax"])


def test_the_pressure_needs_the_area_of_the_discs(results):
    _, found = results

    assert float(found["numbers"]["pressure-distance"]) < 3.0
    assert float(found["numbers"]["ideal-distance"]) > 3.0


def test_a_seed_reproduces_its_run(results):
    _, found = results

    assert [row[1] for row in found["tables"]["same-seed"]["rows"]] == ["yes", "no"]
