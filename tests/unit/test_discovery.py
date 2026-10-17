"""pbc.discovery: the hidden truth stays hidden, the baselines recover a law
or say they cannot, and the protocol's score is recomputed from a trace."""

import ast
import json
import math
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from pbc.agents import ModelMessage, ToolCall, replay, run
from pbc.discovery import (
    CONDITIONS,
    ENVIRONMENTS,
    PROMPT_VERSION,
    CentralForceEnvironment,
    CostRecord,
    OscillatorEnvironment,
    ProjectileEnvironment,
    Protocol,
    TraceInfo,
    comparison,
    environment_allowlist,
    grid_probe,
    least_squares,
    load_trace,
    prompt_sha,
    prompts,
    random_probe,
    run_baselines,
    save_trace,
    score_transcript,
    sparse_identification,
)
from pbc.discovery.environment import Control, library

SOURCES = sorted((Path(__file__).parents[2] / "src/pbc/discovery").glob("*.py"))
# Hidden values chosen to be recognisable if they ever appear in an output.
HIDDEN = {
    "projectile": {"gravity": 3.7123},
    "oscillator": {"stiffness": 6.2345},
    "central-force": {"strength": 20.4567, "exponent": 2.5432},
}


def make(name, **kw):
    return ENVIRONMENTS[name](**HIDDEN[name], **kw)


def numbers(value):
    if isinstance(value, bool):
        return
    if isinstance(value, int | float):
        yield float(value)
    elif isinstance(value, dict):
        for item in value.values():
            yield from numbers(item)
    elif isinstance(value, list | tuple):
        for item in value:
            yield from numbers(item)
    elif hasattr(value, "__dict__"):
        yield from numbers(vars(value))


def hidden_numbers(name):
    values = list(HIDDEN[name].values())
    if name == "oscillator":
        values.append(math.sqrt(HIDDEN[name]["stiffness"]))  # omega
    return values


@pytest.mark.parametrize("name", sorted(ENVIRONMENTS))
def test_no_public_attribute_or_method_returns_the_truth(name):
    env = make(name)
    seen = []
    for attribute in dir(env):
        if attribute.startswith("_"):
            continue
        value = getattr(env, attribute)
        if attribute == "measure":
            continue
        if callable(value):
            try:
                value = value()  # the no-argument methods
            except TypeError, ValueError:
                continue
        seen += list(numbers(value))
    for hidden in hidden_numbers(name):
        assert not any(math.isclose(hidden, s, rel_tol=1e-9) for s in seen)
    assert "Environment" in repr(env) and "4567" not in repr(env)


@pytest.mark.parametrize("name", sorted(ENVIRONMENTS))
def test_the_tools_cannot_reach_the_truth(name):
    env = make(name)
    allowlist = environment_allowlist(env)
    assert [t.name for t in allowlist.tools] == ["measure", "submit"]
    # Names that would reach the truth are not tools.
    for sneaky in ("_law", "_truth", "held_out_error", "score_predictor", "predict"):
        result = allowlist.dispatch(ToolCall("x", sneaky, {}))
        assert not result.ok and "not an allowed tool" in result.content["error"]
    # Extra arguments are refused, so no argument selects another function.
    extra = {c.name: c.low for c in env.controls} | {"world": 1}
    assert not allowlist.dispatch(ToolCall("x", "measure", extra)).ok
    # Everything the tools and their descriptions say is free of the hidden values.
    text = json.dumps([s.__dict__ for s in allowlist.specs()], default=str)
    out = [
        allowlist.dispatch(
            ToolCall(
                "c", "measure", {c.name: (c.low + c.high) / 2 for c in env.controls}
            )
        ).content,
        allowlist.dispatch(
            ToolCall("c", "submit", {c.name: (c.low + c.high) / 2 for c in env.claim})
        ).content,
    ]
    assert all(set(o) <= {env.observation.name, "submitted"} for o in out)
    for hidden in hidden_numbers(name):
        assert f"{hidden:g}" not in text
        assert not any(
            math.isclose(hidden, n, rel_tol=1e-9) for o in out for n in numbers(o)
        )


def test_prompts_carry_nothing_of_the_world():
    for name in ENVIRONMENTS:
        env = make(name)
        for condition in CONDITIONS:
            system, task = prompts(env, condition)
            for hidden in hidden_numbers(name):
                assert f"{hidden:g}" not in system + task
    with pytest.raises(ValueError):
        prompts(make("projectile"), "some")


def test_budget_bounds_and_determinism():
    env = make("central-force", budget=2, seed=3)
    first = env.measure(distance=2.0, mass=1.0)
    assert (
        env.measure(distance=2.0, mass=1.0) == first
    )  # noise depends on the arguments
    with pytest.raises(RuntimeError, match="spent"):
        env.measure(distance=2.0, mass=1.0)
    env.reset()
    assert env.remaining == 2
    with pytest.raises(ValueError, match="between"):
        env.measure(distance=9.0, mass=1.0)  # beyond the bounds: held out
    with pytest.raises(ValueError, match="unknown"):
        env.measure(distance=2.0, mass=1.0, extra=1.0)
    assert env.remaining == 2  # a refused probe costs nothing
    other = make("central-force", seed=4).measure(distance=2.0, mass=1.0)
    assert other != first
    with pytest.raises(ValueError):
        CentralForceEnvironment(budget=0)


def test_held_out_settings_are_outside_the_bounds():
    for name in ENVIRONMENTS:
        env = make(name)
        for settings in env._held_out:
            assert any(not c.low <= settings[c.name] <= c.high for c in env.controls), (
                name
            )


def test_the_observation_matches_the_law_within_the_noise():
    env = make("oscillator", seed=1)
    reads = [
        env.measure(amplitude=1.0, time=t)["displacement"]
        for t in np.linspace(0, 3, 30)
    ]
    expected = np.cos(math.sqrt(6.2345) * np.linspace(0, 3, 30))
    assert abs(np.mean(np.array(reads) - expected)) < 0.02


# --- baselines -------------------------------------------------------------


@pytest.mark.parametrize(
    ("name", "key", "truth", "tolerance"),
    [
        ("projectile", "g", 3.7123, 0.05),
        ("oscillator", "omega", math.sqrt(6.2345), 0.01),
    ],
)
def test_least_squares_recovers_a_parameter(name, key, truth, tolerance):
    env = make(name, seed=2)
    result = least_squares(env, grid_probe(env))
    assert result.success, result.reason
    assert abs(result.claim[key] - truth) / truth < tolerance
    assert result.held_out_error < 0.1


def test_least_squares_recovers_the_modified_central_law():
    env = make("central-force", seed=5, budget=60)
    result = least_squares(env, grid_probe(env))
    assert result.success, result.reason
    assert result.claim["exponent"] == pytest.approx(2.5432, abs=0.05)
    assert result.held_out_error < 0.1
    scattered = least_squares(env, random_probe(env, seed=1))
    assert scattered.success and abs(scattered.claim["exponent"] - 2.5432) < 0.1


def test_sparse_identification_recovers_an_integer_law_and_fails_on_a_modified_one():
    easy = CentralForceEnvironment(strength=20.0, exponent=2.0, seed=1, budget=60)
    found = sparse_identification(easy, grid_probe(easy), library(easy))
    assert found.success, found.reason
    assert set(found.claim) == {"mass*distance^-2"}
    assert found.claim["mass*distance^-2"] == pytest.approx(20.0, rel=0.02)
    hard = make("central-force", seed=1, budget=60)
    failed = sparse_identification(hard, grid_probe(hard), library(hard))
    assert not failed.success
    assert "sparse sum" in failed.reason


class Screened(CentralForceEnvironment):
    """A law outside the family: a screened force, exp(-r / 2) / r**2."""

    def _law(self, settings):
        return (
            20.0
            * settings["mass"]
            * math.exp(-settings["distance"] / 2)
            / settings["distance"] ** 2
        )


def test_least_squares_reports_failure_when_the_family_cannot_fit():
    env = Screened(seed=1, budget=60)
    result = least_squares(env, grid_probe(env))
    assert not result.success
    assert "does not describe" in result.reason


def test_a_budget_below_the_parameters_is_a_failure_not_a_result():
    env = CentralForceEnvironment(budget=2)
    result = least_squares(env, random_probe(env))
    assert not result.success and result.claim is None
    assert result.held_out_error == math.inf


def test_every_baseline_runs_on_the_same_budget_and_resets():
    env = make("projectile", seed=1)
    results = run_baselines(env, seed=1)
    assert results[0].name == "grid + least squares"
    assert all(r.probes <= env.budget for r in results)
    assert env.used == 0
    assert any(r.success for r in results)


# --- the protocol ----------------------------------------------------------

PROTOCOL = Protocol(
    version="1",
    environment="central-force",
    world=HIDDEN["central-force"],
    budget=12,
    seeds=(0, 1),
    tolerance=0.05,
    max_steps=20,
)


class Scripted:
    """A model that probes a few distances and submits a claim."""

    model = "scripted-model"
    secrets = ()

    def __init__(self, claim):
        calls = [
            ToolCall(f"c{i}", "measure", {"distance": d, "mass": 1.0})
            for i, d in enumerate([1.0, 1.5, 2.0, 3.0, 4.0])
        ]
        calls.append(ToolCall("bad", "measure", {"distance": 99.0, "mass": 1.0}))
        self.messages = [
            ModelMessage("probing", tuple(calls[:4])),
            ModelMessage("more", tuple(calls[4:])),
            ModelMessage("claim", (ToolCall("s", "submit", claim),)),
            ModelMessage("done"),
        ]

    def complete(self, *args):
        return self.messages.pop(0)


GOOD = {"strength": 20.4567, "exponent": 2.5432}
BAD = {"strength": 20.0, "exponent": 2.0}


def transcript(claim, seed=0):
    env = PROTOCOL.make(seed)
    system, task = prompts(env, "full")
    return run(Scripted(claim), environment_allowlist(env), system, task, 10)


def info(seed=0):
    system, task = prompts(PROTOCOL.make(seed), "full")
    return TraceInfo(
        "1", "central-force", "full", seed, PROMPT_VERSION, prompt_sha(system, task),
        "scripted-model", "2026-10-13", CostRecord(4, 6, 1200, 300, 0.01),
    )  # fmt: skip


def test_score_is_recomputed_and_deterministic():
    good, bad = transcript(GOOD), transcript(BAD)
    score = score_transcript(PROTOCOL, good, 0)
    assert score == score_transcript(PROTOCOL, good, 0)
    assert (score.probes, score.refused) == (5, 1)
    assert score.recovered and score.outcome == "recovered"
    worse = score_transcript(PROTOCOL, bad, 0)
    assert not worse.recovered and worse.held_out_error > score.held_out_error
    assert worse.outcome == "not recovered"


def test_score_ignores_what_the_agent_wrote_and_what_was_recorded():
    from dataclasses import replace

    t = transcript(BAD)
    steps = tuple(
        replace(
            s,
            message=replace(s.message, text="I found the exact law"),
            results=tuple(replace(r, content={"force": 0.0}) for r in s.results),
        )
        for s in t.steps
    )
    assert score_transcript(PROTOCOL, replace(t, steps=steps), 0) == score_transcript(
        PROTOCOL, t, 0
    )


def test_a_run_without_a_claim_or_beyond_the_budget_is_scored_as_such():
    t = transcript(GOOD)
    from dataclasses import replace

    no_claim = replace(t, steps=t.steps[:2])
    assert score_transcript(PROTOCOL, no_claim, 0).outcome == "no claim"
    tight = replace(PROTOCOL, budget=3)
    score = score_transcript(tight, t, 0)
    assert score.probes == 3 and score.refused == 3  # two probes and the bad one


def test_an_unfinished_run_is_never_a_recovery():
    from dataclasses import replace

    t = transcript(GOOD)
    assert score_transcript(PROTOCOL, t, 0).recovered
    stopped = score_transcript(PROTOCOL, replace(t, finished=False), 0)
    assert stopped.claim is not None and not stopped.recovered
    assert stopped.outcome == "not recovered"


def test_calls_beyond_the_limit_of_a_message_are_refused_as_the_loop_refused_them():
    """The loop runs at most MAX_CALLS_PER_MESSAGE calls of a message; the
    score must count what the loop ran, not every call the model wrote."""
    from dataclasses import replace

    from pbc.agents.loop import MAX_CALLS_PER_MESSAGE, Step

    t = transcript(GOOD)
    first = t.steps[0]
    extra = ToolCall("x", "measure", {"distance": 2.5, "mass": 1.0})
    crowded = Step(
        replace(first.message, tool_calls=(*first.message.tool_calls, extra)),
        first.results,
    )
    assert len(crowded.message.tool_calls) == MAX_CALLS_PER_MESSAGE + 1
    before = score_transcript(PROTOCOL, t, 0)
    after = score_transcript(PROTOCOL, replace(t, steps=(crowded, *t.steps[1:])), 0)
    assert (after.probes, after.refused) == (before.probes, before.refused + 1)
    late_claim = Step(
        ModelMessage(
            "claim", (*first.message.tool_calls, ToolCall("s", "submit", BAD))
        ),
        (),
    )
    assert score_transcript(PROTOCOL, replace(t, steps=(late_claim,)), 0).claim is None


def test_a_cost_record_without_token_counts_round_trips(tmp_path):
    from dataclasses import replace

    unknown = replace(info(), cost=CostRecord(3, 5, None, None, None))
    save_trace(tmp_path, transcript(GOOD), unknown)
    assert load_trace(tmp_path)[1] == unknown


def test_the_grid_spends_the_whole_budget_on_distinct_points():
    env = make("central-force", budget=30)
    data = grid_probe(env)
    assert len(data.settings) == 30
    assert len({tuple(s.values()) for s in data.settings}) == 30


def test_the_grid_spends_the_whole_budget_with_three_controls():
    class ThreeControls:
        controls = tuple(Control(n, "1", 0.0, 1.0, n) for n in "xyz")
        budget = 26
        observation = SimpleNamespace(name="y", sigma=1.0)

        def reset(self):
            pass

        def measure(self, **settings):
            return {"y": sum(settings.values())}

    data = grid_probe(ThreeControls())
    assert len(data.settings) == 26
    assert len({tuple(s.values()) for s in data.settings}) == 26


def test_a_frozen_trace_replays_without_credentials_and_scores_again(
    tmp_path, monkeypatch
):
    for key in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    t = transcript(GOOD)
    save_trace(tmp_path / "trace", t, info())
    recording, loaded = load_trace(tmp_path / "trace")
    assert loaded == info() and loaded.cost.cost_usd == 0.01
    env = PROTOCOL.make(0)
    system, task = prompts(env, "full")
    replayed = replay(
        recording,
        environment_allowlist(env),
        system=system,
        task=task,
        tolerance=PROTOCOL.replay_tolerance,
        max_steps=PROTOCOL.max_steps,
        rerecord="uv run python -m the-lab --record",
    )
    assert score_transcript(PROTOCOL, replayed, 0) == score_transcript(PROTOCOL, t, 0)
    assert "OPENAI" not in (tmp_path / "trace" / "replay.json").read_text()


def test_a_trace_missing_a_field_is_rejected(tmp_path):
    save_trace(tmp_path, transcript(GOOD), info())
    path = tmp_path / "trace.json"
    data = json.loads(path.read_text())
    del data["cost"]["input_tokens"]
    path.write_text(json.dumps(data))
    with pytest.raises(TypeError):
        load_trace(tmp_path)


def test_the_comparison_keeps_failures_beside_the_agent():
    env = PROTOCOL.make(0)
    rows = comparison(
        (score_transcript(PROTOCOL, transcript(GOOD), 0),),
        run_baselines(env),
        PROTOCOL.tolerance,
    )
    assert rows[0]["who"] == "agent, seed 0" and rows[0]["recovered"]
    failed = [r for r in rows if not r["recovered"]]
    assert any("sparse" in r["who"] for r in failed)  # the library cannot hold p=2.54


def test_the_oscillator_and_projectile_environments_are_in_the_protocol():
    for cls in (OscillatorEnvironment, ProjectileEnvironment):
        env = cls(seed=1)
        assert env.name in ENVIRONMENTS and env.family and env.starts


# --- the package does not execute model output ---------------------------


@pytest.mark.parametrize("source", SOURCES, ids=lambda p: p.name)
def test_discovery_has_no_dangerous_import_or_call(source):
    tree = ast.parse(source.read_text())
    banned = {"subprocess", "os", "socket", "http", "urllib", "pickle", "importlib"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert not banned & {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            assert node.module.split(".")[0] not in banned
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in {"eval", "exec", "compile", "__import__", "open"}
