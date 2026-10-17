"""The experiment of "Numerical integrators" (mechanics 05)."""

import json
from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.mechanics.experiments.numerical_integrators"
PAGE = "mechanics/05-numerical-integrators"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("numerical_integrators")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_each_method_converges_at_its_order(results):
    _, found = results
    last = found["tables"]["error-orders"]["rows"][-1]

    # (error, order) per method after the step count: Euler, symplectic
    # Euler, velocity Verlet, Runge-Kutta 4.
    observed = [float(last[i]) for i in (2, 4, 6, 8)]
    assert observed == pytest.approx([1, 1, 2, 4], abs=0.1)


def test_the_symplectic_methods_keep_their_modified_energy(results):
    _, found = results
    rows = {row[0]: row for row in found["tables"]["energy-formulas"]["rows"]}

    assert float(rows["symplectic Euler"][4]) < 1e-10
    assert float(rows["velocity Verlet"][4]) < 1e-10


def test_the_explorer_data_is_written_for_the_widget(results):
    directory, found = results

    assert found["widgets"] == ["integrator-explorer.json"]
    explorer = json.loads((directory / "integrator-explorer.json").read_text())
    assert [run["name"] for run in explorer["integrators"]] == [
        "explicit Euler",
        "symplectic Euler",
        "velocity Verlet",
        "Runge-Kutta 4",
    ]
