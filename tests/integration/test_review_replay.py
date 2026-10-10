"""The review lesson A2 is verified by replay: every tool result of every
reviewer is recomputed by the build, with no network and no credential
(ADR 004), and the faulty piece is rejected through a recomputed check."""

import re
import socket
from pathlib import Path

import pytest

from pbc.agents import ReplayMismatch, load_recording
from pbc.agents.review_lab import (
    RECORD_COMMAND,
    REVIEWERS,
    replay_fixtures,
    replay_reviewer,
    resolve,
    verdicts,
)

ROOT = Path(__file__).parents[2]
LESSON = ROOT / "site" / "lessons" / "agents-llm" / "02-three-reviewers"
CREDENTIAL = re.compile(
    r"sk-[A-Za-z0-9_-]{10,}|Bearer\s+\S+|api[_-]?key", re.IGNORECASE
)


@pytest.fixture(scope="module")
def replays():
    return replay_fixtures(LESSON)


def all_verdicts(replays):
    return [
        v for reviewer in REVIEWERS for v in verdicts(reviewer, replays[reviewer.id][1])
    ]


def test_the_reviews_replay_with_no_network_and_no_credential(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError("the replay opened a network connection")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)
    monkeypatch.setattr(socket, "getaddrinfo", refuse)
    for name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    assert set(replay_fixtures(LESSON)) == {r.id for r in REVIEWERS}


def test_every_reviewer_ran_checks_and_ended_its_run(replays):
    for reviewer in REVIEWERS:
        _, transcript = replays[reviewer.id]
        assert transcript.finished
        assert verdicts(reviewer, transcript)


def test_the_faulty_piece_is_rejected_by_a_recomputed_check(replays):
    found = all_verdicts(replays)
    assert resolve(found, 1).failed == ()
    faulty = resolve(found, 2)
    assert faulty.failed == ("bounded-energy",)
    # at least one reviewer flagged it through a check its tools recomputed
    assert faulty.flagged_by == ("evidence", "physics")


def test_the_reviewers_disagree_and_the_resolution_follows_the_findings(replays):
    faulty = resolve(all_verdicts(replays), 2)
    assert faulty.disagreement
    assert faulty.clear_by == ("numerics",)
    assert faulty.conflicts == ()
    assert resolve(all_verdicts(replays), 1).not_covered == ()


def test_a_change_of_the_code_fails_the_replay(replays, monkeypatch):
    """The page cannot keep numbers the code no longer produces."""
    from pbc.verification import checks

    monkeypatch.setattr(checks, "EXACT", 1e-30)
    reviewer = REVIEWERS[0]
    recording, _ = replays[reviewer.id]
    with pytest.raises(ReplayMismatch) as mismatch:
        replay_reviewer(reviewer, recording)
    assert RECORD_COMMAND in str(mismatch.value)


@pytest.mark.parametrize("reviewer", REVIEWERS, ids=lambda r: r.id)
def test_the_fixture_has_no_credential_and_names_model_and_date(reviewer):
    path = LESSON / reviewer.fixture
    assert not CREDENTIAL.search(path.read_text())
    recording = load_recording(path)
    assert recording.model.strip()
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", recording.recorded)
    assert not recording.placeholder


def test_the_lesson_holds_the_page_and_the_three_fixtures_only():
    kept = {p.name for p in LESSON.iterdir() if p.name != "index_files"}
    assert kept - {"index.html"} == {"index.qmd"} | {r.fixture for r in REVIEWERS}
