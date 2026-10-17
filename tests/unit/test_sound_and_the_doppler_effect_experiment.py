"""The experiment of "Sound and the Doppler effect" (waves 03)."""

from pathlib import Path

import pytest
from support.experiments import assert_the_page_and_the_results_agree, run_entry_point

MODULE = "pbc.waves.experiments.sound_and_the_doppler_effect"
PAGE = "waves/03-sound-and-the-doppler-effect"


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    directory = tmp_path_factory.mktemp("sound_and_the_doppler_effect")
    return directory, run_entry_point(MODULE, directory)


def test_the_command_writes_what_the_page_shows(results):
    assert_the_page_and_the_results_agree(PAGE, *results)


def test_a_closed_pipe_sounds_an_octave_lower_with_odd_harmonics(results):
    _, found = results
    numbers = found["numbers"]

    assert float(numbers["closed-lowest"]) == pytest.approx(
        float(numbers["open-lowest"]) / 2, rel=1e-2
    )
    assert numbers["closed-ratio"] == "3.00"


def test_a_moving_source_and_a_moving_listener_differ(results):
    _, found = results

    assert float(found["numbers"]["source-fastest"]) > float(
        found["numbers"]["observer-fastest"]
    )
