"""The experiment of "Interference and resonance" (waves 02)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.waves.experiments.interference_and_resonance"
PAGE = "waves/02-interference-and-resonance"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("interference_and_resonance")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_the_modes_of_the_plucked_string_are_where_the_formula_puts_them(results):
    _, found = results

    for row in found["tables"]["modes-run"]["rows"]:
        assert float(row[3]) < 0.2  # per cent


def test_driving_at_the_mode_frequency_makes_the_amplitude_grow(results):
    _, found = results

    assert float(found["numbers"]["growth"]) > 3.0


def test_the_short_waves_of_the_grid_fall_behind(results):
    _, found = results
    ratios = [float(row[5]) for row in found["tables"]["dispersion-run"]["rows"]]

    assert ratios == sorted(ratios, reverse=True)
    assert ratios[0] == pytest.approx(1.0, abs=1e-3)
