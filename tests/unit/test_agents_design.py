"""The experimental design agent: the score of a design, the assessment of its
measurements, and the boundary of its allowlist (Issue #128, ADR 004)."""

from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from pbc.agents import Allowlist, ModelMessage, Step, ToolCall, ToolResult, Transcript
from pbc.agents.design import (
    DISCRIMINATED,
    INCONCLUSIVE,
    design_score,
    judge,
    measurements,
)
from pbc.agents.design_lab import (
    BUDGET,
    HIDDEN_C,
    MASS,
    NOISE,
    RESULT,
    RIGS,
    TOOL,
    linear,
    quadratic,
    reading,
    replay_rig,
    tools,
)
from pbc.agents.display import AssessmentDisplay
from pbc.mechanics.drag import quadratic_drag
from pbc.mechanics.dynamics import State, simulate
from pbc.mechanics.integrators import INTEGRATORS

LESSON = (
    Path(__file__).parents[2]
    / "site"
    / "lessons"
    / "agents-llm"
    / "04-an-experimental-design-agent"
)
FULL = RIGS["full"].design
SLOW = RIGS["slow"].design
GOOD = [(20, 3, 1), (10, 3, 1), (5, 3, 1), (2, 3, 1)]
WEAK = [(1, 0.5, 1), (1, 1, 1), (1, 2, 1), (1, 3, 1), (1, 0.2, 1)]


def call(arguments, id="c"):
    return ToolCall(id=id, name=TOOL, arguments=arguments)


def arguments(v0, t, repeat=1):
    return {"initial_speed": v0, "time": t, "repeat": repeat}


def transcript_of(*experiments, text="done"):
    """A transcript whose accepted calls are ``experiments``. The recorded
    results are lies: the judge must not read them."""
    calls = tuple(call(arguments(*e), id=str(i)) for i, e in enumerate(experiments))
    results = tuple(
        ToolResult(str(i), TOOL, True, {RESULT: 0.0}) for i in range(len(calls))
    )
    return Transcript(
        model="m",
        system="s",
        task="t",
        steps=(Step(ModelMessage(text, calls), results),),
        finished=True,
    )


# --- the instrument and the models --------------------------------------------


def test_the_closed_form_of_quadratic_drag_is_the_motion_under_the_course_force():
    """The law the instrument uses is the motion under the quadratic drag force
    of the course, integrated by the velocity Verlet stepper of the course."""
    step = next(i.step for i in INTEGRATORS if i.name == "velocity Verlet")
    force = quadratic_drag(HIDDEN_C)

    def acceleration(t, x, v):
        return force(t, x, v) / MASS

    trajectory = simulate(
        State(0.0, [0.0], [10.0]), acceleration, 0.001, 5000, step=step
    )
    assert trajectory.v[-1, 0] == pytest.approx(
        quadratic(10.0, 5.0, HIDDEN_C / MASS), rel=1e-3
    )


def test_the_reading_is_a_function_of_its_arguments_and_noisy():
    assert reading(5.0, 2.0, 1) == reading(5.0, 2.0, 1)
    assert reading(5.0, 2.0, 1) != reading(5.0, 2.0, 2)
    values = [reading(5.0, 2.0, r) for r in (1, 2, 3)]
    assert max(values) - min(values) < 6 * NOISE
    assert abs(np.mean(values) - quadratic(5.0, 2.0, HIDDEN_C / MASS)) < 3 * NOISE


# --- the allowlist of the rig ---------------------------------------------------


def test_a_valid_measurement_runs():
    result = tools().dispatch(call(arguments(10, 2)))
    assert result.ok
    assert 0 < result.content[RESULT] < 10


@pytest.mark.parametrize(
    "bad",
    [
        arguments(0.1, 2),
        arguments(21, 2),
        arguments(10, 0),
        arguments(10, 11),
        arguments(10, 2, 0),
        arguments(10, 2, 4),
        arguments(10, 2, 1.5),
        arguments(10, float("nan")),
        arguments(10, "2"),
        {**arguments(10, 2), "code": "1 + 1"},
        {"initial_speed": 10, "time": 2},
        [],
    ],
)
def test_a_call_outside_the_bounds_is_rejected_and_costs_nothing(bad):
    allowlist = tools()
    assert not allowlist.dispatch(call(bad)).ok
    for number in range(BUDGET):
        assert allowlist.dispatch(
            call(arguments(10, 2, 1 + number % 3), str(number))
        ).ok


def test_the_slow_rig_refuses_a_fast_start():
    allowlist = tools(RIGS["slow"].maximum_speed)
    assert not allowlist.dispatch(call(arguments(10, 2))).ok
    assert allowlist.dispatch(call(arguments(2, 2))).ok


def test_the_budget_refuses_the_measurement_beyond_it():
    allowlist = tools()
    outcomes = [
        allowlist.dispatch(call(arguments(1 + n, 2), str(n))).ok
        for n in range(BUDGET + 2)
    ]
    assert outcomes == [True] * BUDGET + [False] * 2


# --- the score of a design --------------------------------------------------------


def points(experiments):
    return [
        dict(zip(("initial_speed", "time", "repeat"), e, strict=True))
        for e in experiments
    ]


def test_a_design_that_varies_the_start_speed_scores_high():
    assert design_score(FULL, points(GOOD)) > 10 * FULL.threshold


def test_a_design_at_one_low_speed_scores_nearly_zero():
    assert design_score(FULL, points(WEAK)) < 0.5


def test_the_score_uses_no_measured_value_and_no_fewer_points_than_parameters():
    assert design_score(FULL, points(GOOD)) == design_score(FULL, points(GOOD))
    assert design_score(FULL, points(GOOD[:1])) == 0.0


def test_the_score_of_the_models_is_that_of_the_worse_direction():
    """Models that agree at the calibration run stay close at points near it,
    and far apart at the points where their laws differ."""
    near = points([(10, 2, 1), (10, 2, 2), (10, 2, 3)])
    assert design_score(FULL, near) < 0.01


# --- the assessment -----------------------------------------------------------------


def test_a_design_that_separates_the_models_is_a_discrimination():
    run = transcript_of(*GOOD)
    assessment = judge(FULL, run, tools())
    assert assessment.outcome == DISCRIMINATED
    assert assessment.claim_type == "numerically-verified"
    assert assessment.preferred is not None
    assert assessment.preferred.model.name == "quadratic drag"
    assert assessment.preferred.fit.value("k") == pytest.approx(0.05, rel=0.2)


def test_a_weak_design_is_inconclusive_with_no_claim_type():
    run = transcript_of(*WEAK)
    assessment = judge(FULL, run, tools())
    assert assessment.outcome == INCONCLUSIVE
    assert assessment.claim_type is None
    assert assessment.preferred is None
    assert "less than" in assessment.reason


def test_too_few_measurements_are_inconclusive():
    assessment = judge(FULL, transcript_of(GOOD[0]), tools())
    assert assessment.outcome == INCONCLUSIVE
    assert assessment.fits is None
    assert "at least" in assessment.reason


def test_the_prose_of_the_agent_does_not_change_the_assessment():
    quiet = judge(FULL, transcript_of(*WEAK, text=""), tools())
    boasting = judge(
        FULL,
        transcript_of(*WEAK, text="Linear drag is rejected with a chi-square of 900."),
        tools(),
    )
    assert quiet.outcome == boasting.outcome == INCONCLUSIVE
    assert quiet.score == boasting.score


def test_stored_results_are_not_read():
    """The transcript holds a lie in every result; the assessment is that of
    the recomputed readings."""
    honest = judge(FULL, transcript_of(*GOOD), tools())
    assert honest.outcome == DISCRIMINATED
    assert [m.value for m in honest.measurements] == [
        reading(v, t, r) for v, t, r in GOOD
    ]


def test_a_repeated_measurement_counts_once():
    found = measurements(FULL, transcript_of(*GOOD, *GOOD), tools())
    assert len(found) == len(GOOD)


def test_a_call_outside_the_bounds_in_the_transcript_is_not_a_measurement():
    run = transcript_of((100, 3, 1), (10, 3, 1))
    assert len(measurements(FULL, run, tools())) == 1


def test_a_rejected_call_in_the_transcript_is_not_a_measurement():
    run = transcript_of(*GOOD)
    step = run.steps[0]
    refused = ToolResult("0", TOOL, False, {"error": "no"})
    run = replace(run, steps=(Step(step.message, (refused, *step.results[1:])),))
    assert len(measurements(FULL, run, tools())) == len(GOOD) - 1


def test_at_most_the_budget_of_measurements_count():
    many = [(1 + 0.5 * n, 3, 1) for n in range(BUDGET + 4)]
    assert len(measurements(FULL, transcript_of(*many), tools())) == BUDGET


def test_a_slow_rig_cannot_discriminate_with_the_best_eight_readings():
    best = [(2, 10, 1), (2, 10, 2), (2, 10, 3), (2, 6, 1), (2, 3, 1), (1, 10, 1)]
    run = transcript_of(*best)
    assessment = judge(SLOW, run, tools(2.0))
    assert assessment.outcome == INCONCLUSIVE
    assert assessment.score < SLOW.threshold


def test_a_model_that_does_not_fit_is_not_a_discrimination():
    """When neither model describes the readings, one being less bad is not a
    result. The instrument here follows neither law."""

    def other(initial_speed, time, repeat):
        return {RESULT: float(initial_speed * (1 + np.sin(3 * time)) / 2)}

    template = tools().tool(TOOL)
    allowlist = Allowlist((replace(template, function=other),), budget=BUDGET)
    run = transcript_of(*GOOD, (20, 9, 1), (5, 9, 1), (2, 7, 1), (10, 6, 1))
    assessment = judge(FULL, run, allowlist)
    assert assessment.outcome == INCONCLUSIVE
    assert assessment.claim_type is None


# --- the worked fixtures ------------------------------------------------------------


def test_the_two_fixtures_replay_to_the_expected_outcomes():
    for name, outcome in (("full", DISCRIMINATED), ("slow", INCONCLUSIVE)):
        _, run, assessment = replay_rig(name, LESSON)
        assert run.finished
        assert assessment.outcome == outcome


def test_the_display_labels_each_outcome():
    _, _, found = replay_rig("full", LESSON)
    _, _, open_ = replay_rig("slow", LESSON)
    text = AssessmentDisplay(found)._repr_markdown_()
    assert 'type="numerically-verified"' in text
    assert "recomputed by this build" in text
    other = AssessmentDisplay(open_)._repr_markdown_()
    assert "inconclusive" in other and "numerically-verified" not in other


def test_the_linear_model_is_the_exponential_of_the_start_speed():
    assert linear(10.0, 0.0, 0.3) == 10.0
    assert quadratic(10.0, 0.0, 0.05) == 10.0
    assert linear(10.0, 2.0, 0.3) == pytest.approx(10 * np.exp(-0.6))
