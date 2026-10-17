"""The experiment of "Discovering a force law with controlled probes"
(agents-llm 05)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.mechanics.experiments.black_box_force_law"
PAGE = "agents-llm/05-discovering-a-force-law"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("black_box_force_law")
    return directory, run_entry_point(MODULE, directory)


def _rows(found: dict, name: str) -> dict[str, list[str]]:
    return {row[0]: row[1:] for row in found["tables"][name]["rows"]}


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_the_replayed_claim_and_the_fit_to_its_readings_both_recover_the_law(
    results,
):
    _, found = results
    tolerance = float(found["numbers"]["tolerance"])
    fit = _rows(found, "d1-probe-fit")

    assert found["numbers"]["outcome"] == "recovered"
    assert float(fit["held-out error of this fit"][0]) <= tolerance
    # The fit has standard errors well above zero: the exact score came from
    # the agent's rounding, as the self-check says.
    assert float(fit["exponent"][1]) > 0


def test_sparse_identification_fails_on_a_collinear_library(results):
    _, found = results
    outcome = _rows(found, "own-box")

    assert outcome["grid + least squares"][0] == "yes"
    assert outcome["grid + sparse identification"][0] == "no"


def test_the_narrow_pair_of_distances_gives_the_smaller_error(results):
    _, found = results
    errors = _rows(found, "slope-errors")

    assert float(errors["1 m and 2 m"][0]) < float(errors["1 m and 4 m"][0])
