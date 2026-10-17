"""The lessons D1 to D3 (F66): the protocols are fixed and fair, every frozen
run replays without a model or a network and is scored again, and the
baselines recover the laws they should and fail where they cannot."""

import json
import socket
from dataclasses import replace
from pathlib import Path

import pytest

from pbc.agents import load_recording
from pbc.discovery import prompt_sha
from pbc.discovery.force_lab import (
    FAMILIAR_EXPONENT,
    PROTOCOLS,
    RUNS,
    SEED,
    TOLERANCE,
    baselines,
    environment,
    familiar_law,
    recovered,
    replay_run,
    task_of,
)

LESSONS = Path(__file__).parents[2] / "site" / "lessons" / "agents-llm"
DIRECTORIES = {
    "black-box": LESSONS / "05-discovering-a-force-law",
    "prior-knowledge": LESSONS / "06-prior-knowledge-in-discovery",
    "modified": LESSONS / "07-a-modified-force-law",
}


def directory(name):
    return DIRECTORIES[RUNS[name].protocol]


@pytest.fixture
def offline(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError("the replay opened a network connection")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)
    for name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY"):
        monkeypatch.delenv(name, raising=False)


def test_every_protocol_has_the_same_budget_step_limit_seed_and_tolerance():
    for protocol in PROTOCOLS.values():
        assert protocol.budget == 20
        assert protocol.max_steps == 12
        assert protocol.seeds == (SEED,)
        assert protocol.tolerance == TOLERANCE


def test_the_three_conditions_of_d2_differ_only_in_the_task():
    """The owner's condition of 2026-10-15: model, information, probes, cost
    limit, and evaluation set are equal; only the prior knowledge differs."""
    runs = [RUNS[f"prior-{c}"] for c in ("full", "partial", "none")]
    assert {r.protocol for r in runs} == {"prior-knowledge"}
    assert [r.condition for r in runs] == ["full", "partial", "none"]
    assert len({r.info.model for r in runs}) == 1
    assert len({r.info.seed for r in runs}) == 1
    tasks = {task_of(r.protocol, r.condition) for r in runs}
    assert len({system for system, _ in tasks}) == 1
    assert len({task for _, task in tasks}) == 3
    # One environment, so one allowlist and one set of held-out settings.
    first, second = environment("prior-knowledge"), environment("prior-knowledge")
    assert first._held_out == second._held_out
    assert first.controls == second.controls and first.claim == second.claim


@pytest.mark.parametrize("name", sorted(RUNS))
def test_each_run_replays_offline_and_is_scored_again(name, offline):
    recording, transcript, score = replay_run(name, directory(name))
    assert not recording.placeholder
    assert transcript.finished
    assert score.claim is not None
    assert score.probes <= PROTOCOLS[RUNS[name].protocol].budget
    assert recording.model == RUNS[name].info.model


@pytest.mark.parametrize("name", sorted(RUNS))
def test_the_record_of_a_run_matches_its_fixture(name):
    entry = RUNS[name]
    recording = load_recording(directory(name) / entry.fixture)
    assert prompt_sha(recording.system, recording.task) == entry.info.prompt_sha256
    assert (recording.system, recording.task) == task_of(
        entry.protocol, entry.condition
    )
    assert entry.info.cost.model_calls == len(recording.steps)
    assert entry.info.cost.tool_calls == sum(
        len(s.message.tool_calls) for s in recording.steps
    )


def test_a_fixture_of_another_model_or_prompt_is_refused(tmp_path):
    entry = RUNS["black-box"]
    data = json.loads((directory("black-box") / entry.fixture).read_text())
    (tmp_path / entry.fixture).write_text(json.dumps({**data, "model": "another"}))
    with pytest.raises(ValueError, match="not the run recorded"):
        replay_run("black-box", tmp_path)
    (tmp_path / entry.fixture).write_text(json.dumps({**data, "task": "other"}))
    with pytest.raises(ValueError, match="another prompt"):
        replay_run("black-box", tmp_path)


def test_the_score_does_not_read_the_agents_words(offline):
    _, transcript, score = replay_run("modified", directory("modified"))
    from pbc.agents import ModelMessage, Step
    from pbc.discovery import score_transcript

    silent = replace(
        transcript,
        steps=tuple(
            Step(ModelMessage("", s.message.tool_calls), s.results)
            for s in transcript.steps
        ),
    )
    assert score_transcript(PROTOCOLS["modified"], silent, SEED) == score


def test_least_squares_recovers_each_law():
    for protocol in PROTOCOLS:
        found = {b.name: b for b in baselines(protocol)}
        assert recovered(found["grid + least squares"]), protocol
        assert recovered(found["random + least squares"]), protocol


def test_sparse_identification_fits_the_modified_law_but_does_not_recover_it():
    sparse = {b.name: b for b in baselines("modified")}["grid + sparse identification"]
    assert sparse.success  # consistent with the noise where it was probed
    assert sparse.held_out_error > TOLERANCE  # and wrong where it was not
    assert not recovered(sparse)


def test_the_familiar_law_fits_the_inverse_square_world_and_fails_the_modified_one():
    familiar = familiar_law("black-box")
    assert recovered(familiar)
    assert familiar.claim["exponent"] == FAMILIAR_EXPONENT
    modified = familiar_law("modified")
    assert not modified.success
    assert "inverse-square law does not describe" in modified.reason
    assert modified.held_out_error > TOLERANCE


def test_the_familiar_law_is_only_a_law_of_the_central_force():
    with pytest.raises(ValueError):
        familiar_law("prior-knowledge")


def test_the_lesson_directories_hold_only_the_page_and_the_fixtures():
    for name, path in DIRECTORIES.items():
        fixtures = {RUNS[k].fixture for k in RUNS if RUNS[k].protocol == name}
        kept = {
            p.name
            for p in path.iterdir()
            if p.name not in ("index_files", "index.html")
        }
        assert kept == {"index.qmd", *fixtures}
