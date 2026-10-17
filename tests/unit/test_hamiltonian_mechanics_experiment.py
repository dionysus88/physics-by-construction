"""The experiment of "Hamiltonian mechanics" (mechanics 15)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

from pbc.mechanics.experiments import hamiltonian_mechanics

MODULE = "pbc.mechanics.experiments.hamiltonian_mechanics"
PAGE = "mechanics/15-hamiltonian-mechanics"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("hamiltonian_mechanics")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_the_legendre_transform_gives_the_energy_in_the_momenta():
    # The experiment asserts that both forms agree within the bound it returns.
    assert hamiltonian_mechanics.legendre() == 1e-12


def test_only_the_symplectic_steps_keep_the_area_of_phase_space(results):
    _, found = results
    determinants = {row[0]: row[1:] for row in found["tables"]["determinants"]["rows"]}

    assert determinants["symplectic Euler"] == ["below 1e-8", "below 1e-8"]
    assert determinants["velocity Verlet"] == ["below 1e-8", "below 1e-8"]
    assert "below" not in determinants["explicit Euler"][0]


def test_the_modified_energy_is_conserved_to_round_off(results):
    _, found = results

    for row in found["tables"]["modified-oscillator"]["rows"]:
        assert row[2] == "below 1e-12"
