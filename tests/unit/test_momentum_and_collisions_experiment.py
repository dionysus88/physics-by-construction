"""The experiment of "Momentum and collisions" (mechanics 07)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.mechanics.experiments.momentum_and_collisions"
PAGE = "mechanics/07-momentum-and-collisions"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("momentum_and_collisions")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_every_method_keeps_the_momentum_of_the_pair(results):
    _, found = results

    for row in found["tables"]["pair-conservation"]["rows"]:
        assert row[3:] == ["yes", "yes"]


def test_soft_spheres_approach_the_elastic_formula(results):
    _, found = results
    hard, soft = found["tables"]["head-on"]["rows"]

    assert abs(float(soft[1]) - float(hard[1])) < 1e-2
    assert abs(float(soft[2]) - float(hard[2])) < 1e-2


def test_the_energy_transfer_follows_the_formula(results):
    _, found = results

    for row in found["tables"]["energy-transfer"]["rows"]:
        assert float(row[1]) == pytest.approx(float(row[2]), abs=2e-3)
