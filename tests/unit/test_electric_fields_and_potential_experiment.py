"""The experiment of "Electric fields, superposition, and the potential"
(electromagnetism 01)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

from pbc.electromagnetism.experiments import electric_fields_and_potential
from pbc.experiment import encode

MODULE = "pbc.electromagnetism.experiments.electric_fields_and_potential"
PAGE = "electromagnetism/01-electric-fields-and-potential"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("electric_fields_and_potential")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_the_figure_file_is_the_bytes_of_the_one_encoder(results):
    directory, found = results
    experiment = electric_fields_and_potential.run()

    for name in found["figures"]:
        label = name.removesuffix(".png")
        assert (directory / name).read_bytes() == encode(experiment.figures[label])


def test_the_field_is_minus_the_gradient_and_the_pair_becomes_a_dipole(results):
    _, found = results
    numbers = found["numbers"]

    # Both differences fall as the square: of the step, and of d over r.
    assert float(numbers["gradient-order"]) == pytest.approx(2.0, abs=0.05)
    assert float(numbers["dipole-order"]) == pytest.approx(2.0, abs=0.05)
    gaps = [float(row[2]) for row in found["tables"]["dipole-run"]["rows"]]
    assert gaps == sorted(gaps, reverse=True)


def test_the_flux_counts_the_charge_inside(results):
    _, found = results

    for _, inside, flux in found["tables"]["gauss-run"]["rows"]:
        assert flux == inside


def test_the_dipole_field_on_its_axis_is_twice_the_field_across(results):
    _, found = results
    numbers = found["numbers"]

    assert float(numbers["axis-ratio"]) == pytest.approx(2.0, rel=1e-3)
    assert numbers["zero-at"] == numbers["balance"] == "0.2000"
