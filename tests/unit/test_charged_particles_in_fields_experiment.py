"""The experiment of "Charged particles in electric and magnetic fields"
(electromagnetism 02)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

from pbc.electromagnetism.experiments import charged_particles_in_fields
from pbc.experiment import encode

MODULE = "pbc.electromagnetism.experiments.charged_particles_in_fields"
PAGE = "electromagnetism/02-charged-particles-in-fields"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("charged_particles_in_fields")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_the_figure_files_are_the_bytes_of_the_one_encoder(results):
    directory, found = results
    experiment = charged_particles_in_fields.run()

    for name in found["figures"]:
        label = name.removesuffix(".png")
        assert (directory / name).read_bytes() == encode(experiment.figures[label])


def test_the_orbit_converges_to_the_cyclotron_frequency_with_order_two(results):
    _, found = results

    assert float(found["numbers"]["frequency-order"]) == pytest.approx(2.0, abs=0.02)
    rows = found["tables"]["cyclotron-run"]["rows"]
    # The measured frequency is the pusher's own, and approaches qB/m.
    for _, measured, predicted, _ in rows:
        assert measured == predicted
    for column in (1, 3):
        gaps = [abs(float(row[column]) - 1.0) for row in rows]
        assert gaps == sorted(gaps, reverse=True)
        assert gaps[-1] < 1e-4


def test_euler_gains_the_predicted_energy_and_boris_keeps_it(results):
    _, found = results
    boris, euler = found["tables"]["energy-run"]["rows"]

    assert boris[1] == "below 1e-12"
    assert euler[1] == euler[2]
    assert float(euler[1]) > 1.0


def test_both_charges_drift_with_e_over_b(results):
    _, found = results

    for row in found["tables"]["drift-run"]["rows"]:
        assert row[3] == row[4] == "10000.000"


def test_the_helix_advances_by_the_speed_along_the_field_times_the_period(results):
    _, found = results
    numbers = found["numbers"]

    assert numbers["pitch-mm"] == numbers["expected-pitch-mm"]
