"""The experiment of "Resonance" (mechanics 16)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.mechanics.experiments.resonance"
PAGE = "mechanics/16-resonance"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("resonance")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_the_simulation_follows_the_exact_driven_motion(results):
    _, found = results

    assert float(found["numbers"]["largest"]) < 1e-6
    for row in found["tables"]["resonance-curve"]["rows"]:
        assert float(row[2]) == pytest.approx(float(row[1]), rel=1e-2)


def test_the_peak_lies_below_the_natural_frequency(results):
    _, found = results

    assert float(found["numbers"]["w-peak"]) < float(found["numbers"]["w0"])


def test_doubling_the_damping_about_halves_the_peak(results):
    _, found = results

    assert float(found["numbers"]["height-ratio"]) == pytest.approx(0.5, abs=0.05)
