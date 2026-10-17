"""The experiment of "What symplectic Euler conserves" (lean 03)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.mechanics.experiments.symplectic_euler_conserved_energy"
PAGE = "lean/03-what-symplectic-euler-conserves"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("symplectic_euler_conserved_energy")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_the_modified_energy_is_kept_while_the_energy_swings(results):
    _, found = results

    assert float(found["numbers"]["drift"]) < 1e-12
    assert float(found["numbers"]["swing"]) > 0.1
    _, modified = found["tables"]["three-periods"]["rows"]
    assert modified[1] == modified[2]


def test_the_modified_energy_turns_negative_only_for_very_large_steps(results):
    _, found = results
    smallest = [float(row[2]) for row in found["tables"]["positive-or-not"]["rows"]]

    assert all(value > 0 for value in smallest[:3])
