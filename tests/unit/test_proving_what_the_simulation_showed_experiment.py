"""The experiment of "Proving what the simulation showed" (lean 01)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.mechanics.experiments.proving_what_the_simulation_showed"
PAGE = "lean/01-proving-what-the-simulation-showed"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("proving_what_the_simulation_showed")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_the_identity_holds_on_the_exact_motion_to_round_off(results):
    _, found = results

    assert found["numbers"]["exact-residual"] == "below 1e-12"


def test_the_euler_residual_is_the_derived_one(results):
    _, found = results

    for _, residual, predicted in found["tables"]["euler-residual"]["rows"]:
        assert residual == predicted


def test_the_energy_follows_the_proved_factor(results):
    _, found = results

    assert found["numbers"]["relative"] == "below 1e-12"
    for _, measured, proved in found["tables"]["energy-factor"]["rows"]:
        assert measured == proved
