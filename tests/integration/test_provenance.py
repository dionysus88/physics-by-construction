"""The provenance of a chain of verified bases (ADR 017 decisions 1, 2, 3,
and 5), prototyped by F120 in ``pbc.authoring.provenance``.

Every case is one record: the run that uploaded a base decides whether it
can be inherited from, never the artifact's name or contents; an inherited
result keeps its origin through a chain; the environment identity and the
bounds of the chain fail closed.
"""

import json
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from support.paths import REPO_ROOT

from pbc.authoring import provenance

REPO = "owner/repo"
LESSONS = ["site/lessons/s/01-one", "site/lessons/s/02-two", "site/lessons/s/03-three"]
T0 = datetime(2026, 10, 16, 8, 0, tzinfo=UTC)
RUNNER = {
    "image": "ubuntu-24.04",
    "image_version": "20261012.334.1",
    "locale": "C.UTF-8",
    "time_zone": "UTC",
    "cpu_model": "AMD EPYC 7763 64-Core Processor",
    "cpu_flags": "fma avx2",
    "runner_version": "2.337.0",
}


def run_record(number: int, **record) -> dict:
    return {
        "id": number,
        "commit": f"c{number:08d}",
        "event": "push",
        "head_branch": "main",
        "repository": REPO,
        "head_repository": REPO,
        "path": ".github/workflows/ci.yml",
        "conclusion": "success",
        "verify": "success",
    } | record


def selection(execute: list[str], reuse: list[str]) -> dict:
    return {
        "format": 1,
        "mode": "selective" if reuse else "full",
        "lessons": sorted(execute + reuse),
        "execute": execute,
        "reuse": reuse,
    }


@pytest.fixture
def pins(tmp_path: Path) -> Path:
    root = tmp_path / "root"
    for name in provenance.PINS:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{name}\n", encoding="utf-8")
    return root


@pytest.fixture
def environment(pins: Path) -> dict:
    return provenance.environment_identity(RUNNER, pins)


def complete(number: int, environment: dict, at: datetime) -> dict:
    """The base of a run that executed every lesson."""
    return provenance.derive(
        None, selection(LESSONS, []), run_record(number), environment, at
    )


def accepted(
    base: dict,
    number: int,
    environment: dict,
    at: datetime,
    previous: dict | None = None,
    lessons: list[str] = LESSONS,
    **record,
):
    return provenance.accept(
        base,
        run_record(number, **record),
        repository=REPO,
        environment=environment,
        now=at,
        lessons=lessons,
        previous=previous,
    )


def incremental(previous: dict, number: int, environment: dict, at: datetime) -> dict:
    """The base of a run that executed the first lesson and inherited the rest."""
    return provenance.derive(
        previous,
        selection([LESSONS[0]], LESSONS[1:]),
        run_record(number),
        environment,
        at,
    )


# -- what is accepted as a base ---------------------------------------------


def test_the_base_of_a_verified_push_run_on_main_is_accepted(environment):
    base = complete(1, environment, T0)
    assert accepted(base, 1, environment, T0 + timedelta(hours=1)) is None


@pytest.mark.parametrize(
    ("record", "why"),
    [
        ({"event": "pull_request"}, "pull_request run, not a push run"),
        ({"event": "workflow_dispatch"}, "not a push run"),
        ({"head_branch": "feature/x"}, "not main"),
        ({"head_repository": "fork/repo"}, "another repository"),
        ({"repository": "other/repo"}, "another repository"),
        ({"path": ".github/workflows/other.yml"}, "not ci.yml"),
        ({"conclusion": "failure"}, "concluded with failure"),
        ({"conclusion": None}, "no result"),
        ({"verify": "failure"}, "verify concluded with failure"),
        ({"verify": None}, "verify concluded with no result"),
    ],
    ids=lambda value: next(iter(value)) if isinstance(value, dict) else value,
)
def test_a_run_that_is_not_a_verified_push_run_on_main_is_rejected(
    environment, record, why
):
    # The record inside the base says "push on main": it decides nothing.
    base = complete(1, environment, T0)
    reason = accepted(base, 1, environment, T0, **record)
    assert reason and why in reason


def test_a_base_that_names_another_run_than_the_one_that_uploaded_it_is_rejected(
    environment,
):
    base = complete(1, environment, T0)
    reason = accepted(base, 2, environment, T0)
    assert reason and "another run" in reason


def test_a_base_of_another_format_is_rejected(environment):
    base = complete(1, environment, T0)
    for damaged in ({**base, "format": 0}, {**base, "format": "1"}, {"format": 1}, []):
        reason = accepted(damaged, 1, environment, T0)
        assert reason, damaged
    assert "another format" in accepted({**base, "format": 0}, 1, environment, T0)
    assert "incomplete" in accepted({**base, "chain": None}, 1, environment, T0)


# -- the environment identity ------------------------------------------------


def test_a_differing_environment_identity_is_rejected(environment, pins):
    base = complete(1, environment, T0)
    for name, value in (
        ("image_version", "20261004.327.1"),
        ("image", "ubuntu-22.04"),
        ("locale", "en_US.UTF-8"),
        ("time_zone", "Europe/Amsterdam"),
    ):
        other = provenance.environment_identity(RUNNER | {name: value}, pins)
        reason = accepted(base, 1, other, T0)
        assert reason and "environment identity differs" in reason, name


@pytest.mark.parametrize("pin", provenance.PINS)
def test_a_changed_pin_changes_the_identity(environment, pins, pin):
    base = complete(1, environment, T0)
    (pins / pin).write_text("changed\n", encoding="utf-8")
    other = provenance.environment_identity(RUNNER, pins)
    assert other["identity"] != environment["identity"]
    assert "environment identity differs" in accepted(base, 1, other, T0)


def test_a_missing_pin_is_recorded_and_differs_from_a_present_one(environment, pins):
    (pins / "uv.lock").unlink()
    other = provenance.environment_identity(RUNNER, pins)
    assert other["enforced"]["pins"]["uv.lock"] is None
    assert other["identity"] != environment["identity"]
    # Two runs that both lack it are equal.
    assert (
        provenance.environment_identity(RUNNER, pins)["identity"] == other["identity"]
    )


def test_the_cpu_model_and_flags_are_enforced_and_stay_with_the_origin(
    environment, pins
):
    # The owner's amendment of 2026-10-16 to ADR 017: the CPU model and the
    # relevant instruction-set flags are part of the enforced identity, so a
    # base made on another CPU is not reused. The origin of every result
    # keeps the identity components, and the runner version is recorded only.
    base = complete(1, environment, T0)
    for name, value in (
        ("cpu_model", "Intel Xeon Platinum 8370C"),
        ("cpu_flags", "avx512f"),
    ):
        other = provenance.environment_identity(RUNNER | {name: value}, pins)
        assert other["identity"] != environment["identity"], name
        reason = accepted(base, 1, other, T0)
        assert reason and "environment identity differs" in reason, name
    newer = provenance.environment_identity(
        RUNNER | {"runner_version": "2.999.0"}, pins
    )
    assert newer["identity"] == environment["identity"]
    assert accepted(base, 1, newer, T0) is None
    origin = base["lessons"][LESSONS[0]]["origin"]
    assert origin["recorded"]["runner_version"] == RUNNER["runner_version"]
    assert origin["enforced"]["runner"]["cpu_model"] == RUNNER["cpu_model"]


@pytest.mark.parametrize(
    "absent",
    [{"cpu_model"}, {"cpu_flags"}, {"cpu_model", "cpu_flags"}, {"image_version"}],
    ids=lambda absent: "+".join(sorted(absent)),
)
def test_an_enforced_runner_fact_that_is_not_reported_is_never_equal(pins, absent):
    # Two runs that both omit the CPU facts get the same digest, but the
    # identity is unknown, so neither the base nor this run passes.
    runner = {name: value for name, value in RUNNER.items() if name not in absent}
    unknown = provenance.environment_identity(runner, pins)
    assert (
        unknown["identity"] == provenance.environment_identity(runner, pins)["identity"]
    )
    base = complete(1, unknown, T0)
    reason = accepted(base, 1, unknown, T0)
    assert reason and "the base is unknown" in reason
    for name in absent:
        assert name in reason
    empty = provenance.environment_identity(
        RUNNER | {name: " " for name in absent}, pins
    )
    reason = accepted(complete(1, empty, T0), 1, empty, T0)
    assert reason and "unknown" in reason


def test_this_run_with_an_unknown_identity_inherits_from_no_base(environment, pins):
    base = complete(1, environment, T0)
    runner = {name: value for name, value in RUNNER.items() if name != "cpu_model"}
    reason = accepted(base, 1, provenance.environment_identity(runner, pins), T0)
    assert reason and "this run is unknown" in reason and "cpu_model" in reason


@pytest.mark.parametrize(
    ("damage", "why"),
    [
        (lambda e: e.update(identity="0" * 64), "incomplete or inconsistent"),
        (lambda e: e["enforced"].pop("pins"), "incomplete or inconsistent"),
        (lambda e: e["enforced"]["pins"].pop("uv.lock"), "incomplete or inconsistent"),
        (lambda e: e.update(format=0), "no environment identity"),
    ],
    ids=["identity not its components", "no pins", "a pin absent", "format"],
)
def test_an_inconsistent_environment_record_is_rejected(environment, damage, why):
    base = json.loads(json.dumps(complete(1, environment, T0)))
    damage(base["environment"])
    reason = accepted(base, 1, environment, T0)
    assert reason and why in reason


def test_a_result_that_claims_another_environment_than_its_run_is_rejected(
    environment, pins
):
    # The executed lesson's origin is self-consistent (its environment is the
    # digest of its components) but names another CPU than the base's run.
    other = provenance.environment_identity(
        RUNNER | {"cpu_model": "Intel Xeon Platinum 8370C"}, pins
    )
    base = complete(1, environment, T0)
    origin = base["lessons"][LESSONS[1]]["origin"]
    base["lessons"][LESSONS[1]]["origin"] = origin | {
        "environment": other["identity"],
        "enforced": other["enforced"],
    }
    reason = accepted(base, 1, environment, T0)
    assert reason and "another environment" in reason and LESSONS[1] in reason


def test_an_inherited_result_from_another_environment_is_rejected(environment, pins):
    other = provenance.environment_identity(RUNNER | {"cpu_flags": "avx512f"}, pins)
    first = complete(1, other, T0)
    # A derived base that inherits results made in another environment: no
    # accepted link of a chain could have produced it.
    second = incremental(first, 2, environment, T0 + timedelta(hours=1))
    reason = accepted(second, 2, environment, T0 + timedelta(hours=2), previous=first)
    assert reason and "another environment" in reason and LESSONS[1] in reason


def test_a_base_without_an_environment_identity_is_rejected(environment):
    base = complete(1, environment, T0)
    del base["environment"]
    assert "no environment identity" in accepted(base, 1, environment, T0)


# -- the chain -----------------------------------------------------------------


def test_an_inherited_result_keeps_its_origin_through_a_chain_of_three_bases(
    environment,
):
    one, two, three = LESSONS
    at = T0
    base_1 = complete(1, environment, at)
    chain = [base_1]
    # Three incremental bases: each executes one lesson and inherits the rest.
    for number, executed in ((2, two), (3, three), (4, two)):
        at += timedelta(hours=1)
        previous = chain[-1]
        before = chain[-2] if len(chain) > 1 else None
        assert (
            accepted(previous, previous["run"]["id"], environment, at, before) is None
        )
        chain.append(
            provenance.derive(
                previous,
                selection([executed], [x for x in LESSONS if x != executed]),
                run_record(number),
                environment,
                at,
            )
        )
    base_4 = chain[-1]
    assert base_4["chain"] == {"depth": 3, "start": 1}
    assert base_4["derived_from"] == {
        "run": 3,
        "provenance": provenance._digest(chain[2]),
    }
    # Lesson one was executed by run 1 only and kept that origin, at depth 0.
    origin_one = base_4["lessons"][one]["origin"]
    assert (origin_one["run"], origin_one["commit"], origin_one["depth"]) == (
        1,
        "c00000001",
        0,
    )
    assert origin_one["environment"] == environment["identity"]
    assert base_4["lessons"][one]["executed"] is False
    # Lesson three was executed by run 3, at depth 2, and inherited by run 4.
    assert base_4["lessons"][three]["origin"]["run"] == 3
    assert base_4["lessons"][three]["origin"]["depth"] == 2
    # Lesson two was executed again by run 4: a fresh origin.
    assert base_4["lessons"][two]["executed"] is True
    assert base_4["lessons"][two]["origin"]["run"] == 4
    # Every base names the base it was derived from, back to the complete one.
    assert [b["derived_from"] and b["derived_from"]["run"] for b in chain] == [
        None,
        1,
        2,
        3,
    ]


def test_a_complete_execution_starts_a_new_chain(environment):
    base_1 = complete(1, environment, T0)
    base_2 = provenance.derive(
        base_1, selection([LESSONS[0]], LESSONS[1:]), run_record(2), environment, T0
    )
    assert base_2["chain"]["depth"] == 1
    # A full selection (the checks changed) inherits nothing, whatever base
    # was given.
    base_3 = provenance.derive(
        base_2,
        selection(LESSONS, []) | {"mode": "full", "reason": "the checks changed"},
        run_record(3),
        environment,
        T0,
    )
    assert base_3["chain"] == {"depth": 0, "start": 3}
    assert base_3["derived_from"] is None
    assert all(
        e["executed"] and e["origin"]["run"] == 3 for e in base_3["lessons"].values()
    )


def test_a_chain_deeper_than_the_bound_is_rejected(environment):
    base, before = complete(1, environment, T0), None
    for number in range(2, 2 + provenance.MAX_DEPTH):
        assert accepted(base, base["run"]["id"], environment, T0, before) is None
        before, base = base, incremental(base, number, environment, T0)
    assert base["chain"]["depth"] == provenance.MAX_DEPTH
    reason = accepted(base, base["run"]["id"], environment, T0, before)
    assert reason and "deeper than" in reason


def test_a_result_older_than_the_bound_is_rejected(environment):
    base = complete(1, environment, T0)
    late = T0 + provenance.MAX_AGE + timedelta(seconds=1)
    reason = accepted(base, 1, environment, late)
    assert reason and "older than" in reason
    assert accepted(base, 1, environment, T0 + provenance.MAX_AGE) is None
    # The age is the age of the oldest inherited result, not of the base.
    newer = incremental(base, 2, environment, late - timedelta(days=1))
    reason = accepted(newer, 2, environment, late, base)
    assert reason and LESSONS[1] in reason


def test_a_record_that_does_not_cover_exactly_the_base_s_lessons_is_rejected(
    environment,
):
    base = complete(1, environment, T0)
    assert "incomplete" in accepted({**base, "lessons": {}}, 1, environment, T0)
    partial = {**base, "lessons": dict(list(base["lessons"].items())[:2])}
    reason = accepted(partial, 1, environment, T0)
    assert reason and "does not cover exactly" in reason and LESSONS[2] in reason
    extra = [*LESSONS, "site/lessons/s/04-four"]
    reason = accepted(base, 1, environment, T0, lessons=extra)
    assert reason and "does not cover exactly" in reason and extra[3] in reason


@pytest.mark.parametrize(
    ("damage", "why"),
    [
        (lambda e: e.pop("executed"), "incomplete for"),
        (lambda e: e.update(executed="yes"), "incomplete for"),
        (lambda e: e.pop("origin"), "no origin for"),
        (lambda e: e["origin"].pop("run"), "incomplete for"),
        (lambda e: e["origin"].pop("commit"), "incomplete for"),
        (lambda e: e["origin"].pop("depth"), "incomplete for"),
        (lambda e: e["origin"].update(environment="0" * 64), "incomplete for"),
        (lambda e: e["origin"].pop("enforced"), "incomplete for"),
        (lambda e: e["origin"].update(time="yesterday"), "no time of execution"),
        (lambda e: e["origin"].update(run=7), "not the result of this run"),
        (
            lambda e: e["origin"].update(commit="c00000007"),
            "not the result of this run",
        ),
        (lambda e: e.update(executed=False), "not an inherited result"),
    ],
    ids=[
        "no executed",
        "executed not a boolean",
        "no origin",
        "no origin run",
        "no origin commit",
        "no origin depth",
        "environment not its components",
        "no enforced components",
        "no time",
        "executed by another run",
        "executed at another commit",
        "inherited in a complete execution",
    ],
)
def test_an_incomplete_or_inconsistent_lesson_entry_is_rejected(
    environment, damage, why
):
    base = json.loads(json.dumps(complete(1, environment, T0)))
    damage(base["lessons"][LESSONS[1]])
    reason = accepted(base, 1, environment, T0)
    assert reason and why in reason and LESSONS[1] in reason


@pytest.mark.parametrize(
    ("damage", "why"),
    [
        (lambda b: b["chain"].pop("start"), "no start of its chain"),
        (lambda b: b["chain"].update(start=None), "no start of its chain"),
        (lambda b: b["chain"].update(start=9), "not a complete execution"),
        (lambda b: b["chain"].update(depth=-1), "no depth"),
        (lambda b: b.update(derived_from={"run": 0, "provenance": "x"}), "depth 0"),
    ],
    ids=[
        "no start",
        "start not a run",
        "start another run",
        "negative depth",
        "complete execution derived from a base",
    ],
)
def test_a_complete_execution_with_an_inconsistent_chain_is_rejected(
    environment, damage, why
):
    base = json.loads(json.dumps(complete(1, environment, T0)))
    damage(base)
    reason = accepted(base, 1, environment, T0)
    assert reason and why in reason


def test_a_derived_base_is_accepted_only_against_the_base_it_was_derived_from(
    environment,
):
    base_1 = complete(1, environment, T0)
    base_2 = incremental(base_1, 2, environment, T0)
    assert accepted(base_2, 2, environment, T0, base_1) is None
    # Without the base it was derived from, the link cannot be checked.
    reason = accepted(base_2, 2, environment, T0)
    assert reason and "cannot be checked" in reason
    # Another base than the one whose digest it names.
    other = complete(9, environment, T0)
    reason = accepted(base_2, 2, environment, T0, other)
    assert reason and "another provenance record" in reason
    changed = json.loads(json.dumps(base_1))
    changed["lessons"][LESSONS[1]]["origin"]["commit"] = "c00000099"
    reason = accepted(base_2, 2, environment, T0, changed)
    assert reason and "another provenance record" in reason


@pytest.mark.parametrize(
    ("damage", "why"),
    [
        (lambda b: b.update(derived_from=None), "derivation is incomplete"),
        (lambda b: b["derived_from"].pop("provenance"), "derivation is incomplete"),
        (lambda b: b["derived_from"].update(run="1"), "derivation is incomplete"),
        (lambda b: b["derived_from"].update(run=2), "derivation is incomplete"),
        (lambda b: b["derived_from"].update(provenance="0" * 64), "another provenance"),
        (lambda b: b["chain"].update(start=2), "derivation is incomplete"),
        (lambda b: b["chain"].update(start=5), "does not continue"),
        (lambda b: b["chain"].update(depth=2), "not the result of this run"),
        (lambda b: b["derived_from"].update(run=5), "does not continue"),
    ],
    ids=[
        "no link",
        "no digest",
        "run not a number",
        "derived from itself",
        "another digest",
        "chain starts here",
        "another start",
        "another depth",
        "another run",
    ],
)
def test_a_malformed_derivation_link_is_rejected(environment, damage, why):
    base_1 = complete(1, environment, T0)
    base_2 = json.loads(json.dumps(incremental(base_1, 2, environment, T0)))
    damage(base_2)
    reason = accepted(base_2, 2, environment, T0, base_1)
    assert reason and why in reason


def test_an_inherited_result_that_is_not_the_previous_base_s_is_rejected(environment):
    base_1 = complete(1, environment, T0)
    base_2 = json.loads(json.dumps(incremental(base_1, 2, environment, T0)))
    # An origin rewritten to another, earlier run of the same chain.
    origin = base_2["lessons"][LESSONS[2]]["origin"]
    origin["time"] = (T0 - timedelta(hours=1)).isoformat()
    reason = accepted(base_2, 2, environment, T0, base_1)
    assert reason and "not the one of the base" in reason and LESSONS[2] in reason
    # A derived base that inherited nothing is not a derivation.
    executed_all = json.loads(json.dumps(incremental(base_1, 2, environment, T0)))
    for entry in executed_all["lessons"].values():
        entry["executed"] = True
        entry["origin"] = executed_all["lessons"][LESSONS[0]]["origin"]
    reason = accepted(executed_all, 2, environment, T0, base_1)
    assert reason and "derivation is incomplete" in reason


def test_a_reused_lesson_without_an_origin_cannot_be_inherited(environment):
    base = complete(1, environment, T0)
    del base["lessons"][LESSONS[1]]
    with pytest.raises(ValueError, match="no origin"):
        provenance.derive(
            base, selection([LESSONS[0]], LESSONS[1:]), run_record(2), environment, T0
        )


# -- the record of the published site -------------------------------------------


def test_the_site_record_names_the_origin_of_every_lesson(environment):
    base_1 = complete(1, environment, T0)
    base_2 = provenance.derive(
        base_1, selection([LESSONS[0]], LESSONS[1:]), run_record(2), environment, T0
    )
    record = provenance.site_record(base_2)
    assert record["run"] == 2 and record["commit"] == "c00000002"
    assert record["lessons"][LESSONS[0]] == {"status": "executed in this run (2)"}
    inherited = record["lessons"][LESSONS[1]]
    assert inherited["status"] == "inherited from run 1 at commit c00000001"
    assert (inherited["run"], inherited["commit"], inherited["depth"]) == (
        1,
        "c00000001",
        0,
    )
    assert inherited["environment"] == environment["identity"]


def test_the_record_is_written_and_read_back_and_another_format_is_not_read(
    environment, tmp_path
):
    base = complete(1, environment, T0)
    provenance.write(tmp_path, base)
    assert provenance.read(tmp_path) == json.loads(json.dumps(base))
    provenance.write(tmp_path, {**base, "format": 0})
    assert provenance.read(tmp_path) is None
    assert provenance.read(tmp_path / "missing") is None


def test_the_module_describes_a_base_as_a_command_on_the_pinned_python(
    environment, tmp_path
):
    base_1 = complete(1, environment, T0)
    base_2 = provenance.derive(
        base_1, selection([LESSONS[0]], LESSONS[1:]), run_record(2), environment, T0
    )
    provenance.write(tmp_path, base_2)
    result = subprocess.run(
        [sys.executable, "-m", "pbc.authoring.provenance", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, result.stderr
    assert "run 2 at commit c00000002, chain depth 1" in result.stdout
    assert f"{LESSONS[1]}: inherited from run 1 at commit c00000001" in result.stdout
    assert f"{LESSONS[0]}: executed in this run (2)" in result.stdout
    empty = subprocess.run(
        [sys.executable, "-m", "pbc.authoring.provenance", str(tmp_path / "none")],
        capture_output=True,
        text=True,
        check=False,
        cwd=REPO_ROOT,
    )
    assert empty.returncode == 1
