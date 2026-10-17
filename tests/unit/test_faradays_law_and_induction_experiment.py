"""The experiment of "Faraday's law and induction" (electromagnetism 03)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

from pbc.electromagnetism.experiments import faradays_law_and_induction
from pbc.experiment import encode

MODULE = "pbc.electromagnetism.experiments.faradays_law_and_induction"
PAGE = "electromagnetism/03-faradays-law-and-induction"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("faradays_law_and_induction")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_the_figure_files_are_the_bytes_of_the_one_encoder(results):
    directory, found = results
    experiment = faradays_law_and_induction.run()

    for name in found["figures"]:
        label = name.removesuffix(".png")
        assert (directory / name).read_bytes() == encode(experiment.figures[label])


def test_the_emf_of_every_loop_is_minus_the_rate_of_its_flux(results):
    _, found = results
    tables = found["tables"]

    for _, _, along, from_flux in tables["moving-loop-run"]["rows"]:
        assert along == from_flux
    for _, along, from_flux, _ in tables["tube-run"]["rows"]:
        assert along == from_flux
    for _, along, from_flux, _ in tables["further-out"]["rows"]:
        assert along == from_flux


def test_the_turning_coil_follows_the_generator_formula(results):
    _, found = results
    along, from_flux, formula = found["tables"]["coil-run"]["rows"]

    assert along[1:] == from_flux[1:] == formula[1:]
    assert float(formula[1]) == pytest.approx(float(found["numbers"]["peak"]), abs=1e-4)


def test_the_sliding_bar_gives_b_l_v(results):
    _, found = results
    numbers = found["numbers"]

    assert numbers["bar-emf-mv"] == numbers["rails-rate-mv"] == "-" + numbers["blv-mv"]
