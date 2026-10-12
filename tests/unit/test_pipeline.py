"""Analysis pipelines (F47): the helpers, the two problems of the lesson, and
the committed expectations of their reports."""

import numpy as np
import pytest

from pbc.data import flume_analysis
from pbc.data.pipeline import (
    EXPECTED_DIR,
    Report,
    ReportMismatch,
    check_report,
    differences,
    estimate,
    sweep,
)
from pbc.data.reports import REPORTS
from pbc.mechanics import analysis


def test_sweep_tabulates_named_results_for_each_value():
    result = sweep("x", [1.0, 2.0, 3.0], lambda x: {"square": x * x, "cube": x**3})

    assert result.rows("square", "cube") == [
        (1.0, 1.0, 1.0),
        (2.0, 4.0, 8.0),
        (3.0, 9.0, 27.0),
    ]
    assert result.argmax("cube") == 3.0


def test_sweep_refuses_results_that_change_names_and_an_empty_grid():
    with pytest.raises(ValueError, match="different results"):
        sweep("x", [1, 2], lambda x: {"a": x} if x == 1 else {"b": x})
    with pytest.raises(ValueError, match="non-empty"):
        sweep("x", [], lambda x: {"a": x})


def test_sweep_accepts_the_same_names_in_a_different_order():
    def func(x):
        return {"a": x, "b": 2 * x} if x == 1 else {"b": 2 * x, "a": x}

    result = sweep("x", [1.0, 2.0], func)
    assert list(result.results) == ["a", "b"]
    assert result.results["a"].tolist() == [1.0, 2.0]
    assert result.results["b"].tolist() == [2.0, 4.0]


def test_estimate_is_the_mean_and_its_standard_error():
    result = estimate([1.0, 2.0, 3.0, 4.0])

    assert result.mean == 2.5
    assert result.sigma == pytest.approx(np.std([1, 2, 3, 4], ddof=1) / 2)
    assert result.n == 4
    with pytest.raises(ValueError):
        estimate([1.0])


def test_a_report_shows_each_quantity_at_its_precision():
    report = (
        Report("Title")
        .add("length", 1.23456, "m", sigma=0.0149, decimals=2)
        .add("count", 5, decimals=0)
    )

    assert report.render() == "Title\nlength: 1.23 +/- 0.01 m\ncount: 5\n"
    with pytest.raises(ValueError, match="already"):
        report.add("count", 6)


def test_a_difference_below_the_displayed_precision_is_not_a_difference():
    expected = Report("T").add("a", 1.2341, "m", decimals=2).render()

    assert differences(Report("T").add("a", 1.2349, "m", decimals=2), expected) == []
    problems = differences(Report("T").add("a", 1.2351, "m", decimals=2), expected)
    assert len(problems) == 1 and "line 2" in problems[0]


def test_a_missing_and_an_extra_line_are_reported(tmp_path):
    expected = Report("T").add("a", 1.0).add("b", 2.0).render()

    assert len(differences(Report("T").add("a", 1.0), expected)) == 1
    assert (
        len(
            differences(Report("T").add("a", 1.0).add("b", 2.0).add("c", 3.0), expected)
        )
        == 1
    )
    path = tmp_path / "r.txt"
    with pytest.raises(ReportMismatch, match="no committed expectation"):
        check_report(Report("T"), path)
    path.write_text(expected, encoding="utf-8")
    assert check_report(Report("T").add("a", 1.0).add("b", 2.0), path) == expected
    with pytest.raises(ReportMismatch, match="line 3"):
        check_report(Report("T").add("a", 1.0).add("b", 2.5), path)


@pytest.mark.parametrize("name", sorted(REPORTS))
def test_the_report_matches_its_committed_expectation(name):
    assert check_report(REPORTS[name](), EXPECTED_DIR / f"{name}.txt")


def test_without_drag_the_simulated_range_is_the_closed_form():
    from pbc.mechanics.projectile import drag_free_range

    for angle in (20.0, 45.0, 70.0):
        assert analysis.throw_range(analysis.SPEED, angle, 0.0) == pytest.approx(
            drag_free_range(analysis.SPEED, angle), rel=1e-4
        )


def test_the_propagated_uncertainty_agrees_with_a_monte_carlo_run():
    row = analysis.range_with_uncertainty(45.0)
    _, spread = analysis.monte_carlo(45.0, samples=400)

    assert row["range"] < row["no_drag"]
    assert spread == pytest.approx(row["sigma"], rel=0.15)


def test_drag_moves_the_best_angle_below_forty_five_degrees():
    assert analysis.fine_sweep().argmax("range") < 45.0


def test_the_window_sets_the_period_resolution_not_the_repetitions():
    experiment, _ = flume_analysis.load()
    rms, period = flume_analysis.repetition_results(experiment, flume_analysis.WINDOW)
    resolution = flume_analysis.period_resolution(
        estimate(period).mean, flume_analysis.WINDOW
    )

    assert np.ptp(period) < resolution
    assert estimate(rms).sigma < 0.1 * np.ptp(
        flume_analysis.window_sweep(experiment).results["rms"]
    )


def test_a_pure_tone_has_its_rms_and_period_recovered():
    time = np.arange(0.0, 20.0, 1 / 150)
    values = 0.01 * np.sin(2 * np.pi * time / 1.6)

    assert flume_analysis.rms_elevation(time, values, (5.0, 13.0)) == pytest.approx(
        0.01 / np.sqrt(2), rel=5e-3
    )
    assert flume_analysis.wave_period(time, values, (5.0, 13.0)) == pytest.approx(
        1.6, abs=0.02
    )


def test_what_the_lesson_says_of_the_runs_holds():
    experiment, models = flume_analysis.load()
    rms, period = flume_analysis.repetition_results(experiment, flume_analysis.WINDOW)
    measured = estimate(rms)
    resolution = flume_analysis.period_resolution(
        estimate(period).mean, flume_analysis.WINDOW
    )
    spread = np.ptp(flume_analysis.window_sweep(experiment).results["rms"])

    for run_rms, run_period in flume_analysis.model_results(models).values():
        assert run_rms < measured.mean
        assert measured.mean - run_rms < spread
        assert abs(run_period - estimate(period).mean) < resolution
