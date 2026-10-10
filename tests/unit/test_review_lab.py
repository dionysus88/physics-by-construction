"""The review agents of lesson A2: tools over the checks of the contract, and
verdicts read from recomputed results, never from the words of a model."""

import ast
from pathlib import Path

import pytest

from pbc.agents import ModelMessage, ToolCall, run
from pbc.agents.review_lab import (
    CANDIDATES,
    CHECKS,
    MAX_STEPS,
    REVIEWERS,
    ReviewDisplay,
    Verdict,
    _reproduce,
    resolve,
    verdicts,
)

ROOT = Path(__file__).parents[2]
BY_ID = {reviewer.id: reviewer for reviewer in REVIEWERS}


class Scripted:
    model = "scripted-model"
    secrets = ()

    def __init__(self, *messages):
        self.messages = list(messages)

    def complete(self, system, conversation, tools):
        return self.messages.pop(0)


def play(reviewer, *messages):
    return run(
        Scripted(*messages), reviewer.allowlist, reviewer.system, reviewer.task, 6
    )


def call(name, **arguments):
    return ToolCall("c", name, arguments)


def test_there_are_three_reviewers_with_different_allowlists():
    assert [r.id for r in REVIEWERS] == ["physics", "numerics", "evidence"]
    names = [{t.name for t in r.allowlist.tools} for r in REVIEWERS]
    assert names[0] == {"check_limits", "check_bounded_energy"}
    assert names[1] == {"check_clock", "check_purity", "check_convergence_order"}
    assert names[2] == {"reproduce_check", "oscillator_error"}


def test_the_reviewers_between_them_run_every_check_of_the_contract():
    physics_and_numerics = {
        t.name.removeprefix("check_").replace("_", "-")
        for r in REVIEWERS[:2]
        for t in r.allowlist.tools
    }
    assert physics_and_numerics == set(CHECKS)


def test_no_prompt_or_task_says_which_piece_is_wrong():
    for reviewer in REVIEWERS:
        text = (reviewer.system + reviewer.task).lower()
        for word in ("faulty", "wrong sign", "explicit euler", "symplectic"):
            assert word not in text


@pytest.mark.parametrize("candidate", [0, 3, 1.5, "1", True])
def test_a_candidate_outside_the_two_is_refused_before_it_runs(candidate):
    result = BY_ID["physics"].allowlist.dispatch(
        call("check_limits", candidate=candidate)
    )
    assert not result.ok


def test_reproduce_check_refuses_a_check_outside_the_contract():
    allowlist = BY_ID["evidence"].allowlist
    assert not allowlist.dispatch(call("reproduce_check", check=6, candidate=1)).ok
    assert not allowlist.dispatch(call("reproduce_check", check=0, candidate=1)).ok
    assert allowlist.dispatch(call("reproduce_check", check=1, candidate=1)).ok


def test_a_tool_returns_the_form_of_rule_3_as_numbers():
    result = BY_ID["physics"].allowlist.dispatch(call("check_limits", candidate=1))
    assert set(result.content) == {"measured", "tolerance", "passed"}
    assert result.content["passed"] == 1.0


def test_reproduce_check_gives_the_same_evidence_as_the_named_tool():
    named = {
        "clock": (BY_ID["numerics"], "check_clock"),
        "limits": (BY_ID["physics"], "check_limits"),
        "bounded-energy": (BY_ID["physics"], "check_bounded_energy"),
    }
    for number, name in enumerate(CHECKS, start=1):
        if name in named:
            reviewer, tool = named[name]
            for candidate in CANDIDATES:
                direct = reviewer.allowlist.dispatch(call(tool, candidate=candidate))
                assert dict(direct.content) == _reproduce(number, candidate)


def test_the_two_pieces_differ_on_bounded_energy_only():
    outcome = {
        candidate: [_reproduce(n, candidate)["passed"] for n in range(1, 6)]
        for candidate in CANDIDATES
    }
    assert outcome[1] == [1.0] * 5
    assert outcome[2] == [1.0, 1.0, 1.0, 1.0, 0.0]


def test_a_verdict_comes_from_the_recomputed_result_not_from_the_words():
    reviewer = BY_ID["physics"]
    boasting = ModelMessage(
        "Piece 2 passes every check with flying colours.",
        (call("check_bounded_energy", candidate=2),),
    )
    transcript = play(reviewer, boasting, ModelMessage("Piece 2 is fine."))
    (verdict,) = verdicts(reviewer, transcript)
    assert (verdict.check, verdict.candidate, verdict.passed) == (
        "bounded-energy",
        2,
        False,
    )


def test_a_refused_call_and_a_raw_measurement_give_no_verdict():
    reviewer = BY_ID["evidence"]
    transcript = play(
        reviewer,
        ModelMessage(
            "",
            (
                call("reproduce_check", check=9, candidate=1),
                call("oscillator_error", candidate=1, steps_per_period=50),
                call("os.system", command="echo hello"),
            ),
        ),
        ModelMessage("done"),
    )
    assert verdicts(reviewer, transcript) == []


def test_reproduce_check_names_the_check_by_its_place_in_the_contract():
    reviewer = BY_ID["evidence"]
    transcript = play(
        reviewer,
        ModelMessage("", (call("reproduce_check", check=5, candidate=2),)),
        ModelMessage("done"),
    )
    assert [v.check for v in verdicts(reviewer, transcript)] == ["bounded-energy"]


def verdict(reviewer, candidate, check, passed):
    return Verdict(reviewer, candidate, check, 0.0, 1.0, passed)


def test_a_failed_check_stands_against_a_reviewer_that_did_not_run_it():
    found = [
        verdict("physics", 2, "bounded-energy", False),
        verdict("numerics", 2, "clock", True),
        verdict("numerics", 2, "purity", True),
    ]
    resolution = resolve(found, 2)
    assert resolution.rejected
    assert resolution.failed == ("bounded-energy",)
    assert resolution.flagged_by == ("physics",)
    assert resolution.clear_by == ("numerics",)
    assert resolution.disagreement
    assert resolution.not_covered == ("limits", "convergence-order")
    assert resolution.conflicts == ()


def test_passes_alone_do_not_reject_and_say_what_was_not_run():
    resolution = resolve([verdict("numerics", 1, "clock", True)], 1)
    assert not resolution.rejected and not resolution.disagreement
    assert resolution.not_covered == CHECKS[1:]


def test_two_reviewers_with_different_outcomes_for_one_check_are_a_conflict():
    found = [
        verdict("physics", 1, "limits", True),
        verdict("evidence", 1, "limits", False),
    ]
    assert resolve(found, 1).conflicts == ("limits",)


def test_only_the_verdicts_of_the_candidate_count():
    assert not resolve([verdict("physics", 2, "limits", False)], 1).rejected


def test_the_display_builds_from_findings_and_holds_no_model_text():
    transcripts = {}
    for reviewer in REVIEWERS:
        calls = tuple(
            call("check_limits", candidate=c)
            for c in (1, 2)
            if reviewer.id == "physics"
        )
        transcripts[reviewer.id] = play(
            reviewer,
            ModelMessage("INJECTED TEXT", calls),
            ModelMessage("INJECTED TEXT"),
        )
    shown = ReviewDisplay(transcripts)._repr_markdown_()
    assert "INJECTED" not in shown
    assert "`limits` passed" in shown


# --- The boundary of ADR 004 and the loop run three times. ---


def test_the_module_uses_the_harness_loop_and_adds_no_orchestration():
    source = (ROOT / "src/pbc/agents/review_lab.py").read_text()
    tree = ast.parse(source)
    imported = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert "pbc.agents.loop" in imported
    # No framework, no threads, no processes, no extra loop of agents.
    for forbidden in ("langchain", "autogen", "crewai", "asyncio", "threading"):
        assert forbidden not in source
    assert MAX_STEPS >= 5  # the evidence reviewer needs five messages
