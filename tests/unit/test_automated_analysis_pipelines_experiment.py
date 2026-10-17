"""The experiment of "Automated analysis pipelines" (mechanics 10)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.mechanics.experiments.automated_analysis_pipelines"
PAGE = "mechanics/10-automated-analysis-pipelines"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("automated_analysis_pipelines")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_both_reports_match_their_committed_expectations(results):
    _, found = results

    assert found["numbers"]["report-differences"] == "0"
    assert found["outputs"]["flume-expectation"].strip().endswith(": 0")


def test_the_propagated_uncertainty_matches_the_monte_carlo_spread(results):
    _, found = results
    (row,) = found["tables"]["monte-carlo-check"]["rows"]

    # Within the uncertainty of a standard deviation from the samples.
    assert abs(float(row[2])) <= float(found["numbers"]["spread-uncertainty"])


def test_halving_the_speed_uncertainty_halves_the_range_uncertainty(results):
    _, found = results

    assert found["outputs"]["halved-speed-uncertainty"].strip().endswith("ratio 0.50")
