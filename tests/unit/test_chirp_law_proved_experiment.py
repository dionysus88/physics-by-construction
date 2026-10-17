"""The experiment of "The chirp law, proved" (lean 05)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.mechanics.experiments.chirp_law_proved"
PAGE = "lean/05-the-chirp-law-proved"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("chirp_law_proved")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_the_identities_of_the_theorems_hold_for_the_lab(results):
    _, found = results

    for _, difference in found["tables"]["identities"]["rows"]:
        assert abs(float(difference)) < 1e-9


def test_the_countdown_falls_one_second_per_second(results):
    _, found = results

    assert float(found["numbers"]["slope"]) == pytest.approx(-1.0, abs=1e-3)
