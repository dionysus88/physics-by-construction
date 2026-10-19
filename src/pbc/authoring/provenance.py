"""The provenance of a chain of verified bases (ADR 017 decisions 1, 2, 3, and
5), specified and prototyped by F120. Nothing of the workflow calls it: a
push to ``main`` still executes every lesson (ADR 014 decision 4), and F121
would wire it in if the owner accepts ADR 017.

A base of ``main`` today is ``digests.json``, ``pages.json``, and
``freeze/``. This module adds a fourth file, ``provenance.json``:

- ``run``: the run that made the base (id, commit, event, branch,
  repository, the conclusion of its job ``verify``, when it ran), as the
  runs API records it, never as the artifact names it;
- ``environment``: the execution-environment identity of that run
  (``environment_identity``): the part that is required equal for reuse
  (``enforced``) and the part that is recorded for the audit (``recorded``);
- ``derived_from``: the base this one inherited from (its run and the
  digest of its provenance record), or None for a complete execution;
- ``chain``: the depth since the last run that executed every lesson and
  the run that started the chain;
- ``lessons``: per lesson, the ``origin`` of its results (the run and commit
  that executed it, the identity of that run's environment, the depth at
  which it was executed, and when), and whether this run executed it.

A base is accepted only by ``accept``: a ``push`` run on ``main`` of this
repository whose ``verify`` concluded with success, a record of the current
format, an enforced environment identity that is complete (every enforced
runner fact reported) and equal to this run's, a complete
and consistent record (an origin for exactly the lessons of the base, a
chain that starts at a complete execution or continues, by the digest
named in ``derived_from``, the record of the base it was derived from), and
a chain within the proposed bounds. Anything else gives a complete execution with
the reason, as ``pbc.authoring.selection`` does for the digests. A pull
request artifact, a run that was green but did not run ``verify``, a fork,
and a record of another format are never accepted, whatever they hold.

The site's provenance record (``site_record``) lists, per lesson, "executed
in this run" or "inherited from run R at commit C", beside the checksums of
the built site (ADR 012 decision 6).
"""

import argparse
import hashlib
import json
import sys
from collections.abc import Iterable
from datetime import UTC, datetime, timedelta
from pathlib import Path

from pbc.authoring.repository import REPOSITORY_ROOT

FORMAT = 1
PROVENANCE = "provenance.json"
WORKFLOW = ".github/workflows/ci.yml"

# The bounds of a chain, proposed by F120 for the owner's approval (ADR 017
# decision 5): no inherited result older than the artifact retention, and no
# chain deeper than ten bases.
MAX_AGE = timedelta(days=30)
MAX_DEPTH = 10

# The inputs of the environment identity that pins fix (ADR 017 decision 3):
# the Python, uv, Quarto, Lean, and Mathlib versions and the runner
# preparation, by the content of the files that pin them.
PINS = (
    ".python-version",
    "pyproject.toml",
    "uv.lock",
    "lean/lean-toolchain",
    "lean/lake-manifest.json",
    ".github/actions/prepare/action.yml",
)
# What the runner itself reports. The first group is required equal: the image
# label and version, the locale and the time zone, and (the owner's amendment
# of 2026-10-16 to ADR 017) the CPU model and the instruction-set flags. The
# second group is recorded with the origin of every result and not enforced.
# F120 found the CPU model and flags in no log today, so F121 has to record
# them: a run that does not report an enforced fact has an unknown identity,
# and ``accept`` reuses nothing for it or from it (fail closed).
ENFORCED_RUNNER = (
    "image",
    "image_version",
    "locale",
    "time_zone",
    "cpu_model",
    "cpu_flags",
)
RECORDED_RUNNER = ("runner_version",)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _digest(value: object) -> str:
    return _sha(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def environment_identity(runner: dict[str, str], root: Path = REPOSITORY_ROOT) -> dict:
    """The environment identity of a run: the pins of ``root`` and what the
    ``runner`` reports (``image``, ``image_version``, ``locale``,
    ``time_zone``, ``cpu_model``, ``cpu_flags``, ``runner_version``). Every
    component is recorded; all but ``runner_version`` are enforced.

    A pin that is missing, and a runner fact that is not reported, are
    recorded as such (None). A missing pin is a fact of the commit: two runs
    that both lack it are equal. A runner fact that is not reported is
    unknown: ``accept`` rejects an identity that lacks one, so two runs that
    both omit, say, the CPU model never count as equal.
    """
    pins = {}
    for name in PINS:
        path = root / name
        pins[name] = _sha(path.read_bytes()) if path.is_file() else None
    enforced = {
        "pins": pins,
        "runner": {name: runner.get(name) for name in ENFORCED_RUNNER},
    }
    recorded = {name: runner.get(name) for name in RECORDED_RUNNER}
    return {
        "format": FORMAT,
        "identity": _digest(enforced),
        "enforced": enforced,
        "recorded": recorded,
    }


def _run_problem(run: dict, repository: str) -> str | None:
    """Why ``run`` (the record of the runs API, with the conclusion of its job
    ``verify`` under ``verify``) cannot have made a base, or None."""
    if not isinstance(run, dict):
        return "the run record is not an object"
    if run.get("event") != "push":
        return f"the run is a {run.get('event') or 'unknown'} run, not a push run"
    if run.get("head_branch") != "main":
        return (
            f"the run is on the branch {run.get('head_branch') or 'unknown'}, not main"
        )
    if run.get("repository") != repository or run.get("head_repository") != repository:
        return "the run is of another repository"
    if run.get("path") != WORKFLOW:
        return f"the run is of the workflow {run.get('path') or 'unknown'}, not ci.yml"
    if run.get("conclusion") != "success":
        return f"the run concluded with {run.get('conclusion') or 'no result'}"
    if run.get("verify") != "success":
        return f"the job verify concluded with {run.get('verify') or 'no result'}"
    if not isinstance(run.get("id"), int) or not isinstance(run.get("commit"), str):
        return "the run record names no run id and commit"
    return None


def _environment_problem(environment: object, whose: str) -> str | None:
    """Why ``environment`` (the identity recorded by ``whose``) is incomplete,
    inconsistent, or unknown, or None. An enforced runner fact that is not
    reported as a non-empty string makes the identity unknown."""
    if not isinstance(environment, dict) or environment.get("format") != FORMAT:
        return f"{whose} records no environment identity"
    enforced = environment.get("enforced")
    if (
        not isinstance(enforced, dict)
        or set(enforced) != {"pins", "runner"}
        or not isinstance(enforced["pins"], dict)
        or set(enforced["pins"]) != set(PINS)
        or not all(
            value is None or isinstance(value, str)
            for value in enforced["pins"].values()
        )
        or not isinstance(enforced["runner"], dict)
        or not set(enforced["runner"]) <= set(ENFORCED_RUNNER)
        or environment.get("identity") != _digest(enforced)
    ):
        return f"the environment identity of {whose} is incomplete or inconsistent"
    unknown = [
        name
        for name in ENFORCED_RUNNER
        if not isinstance(enforced["runner"].get(name), str)
        or not enforced["runner"][name].strip()
    ]
    if unknown:
        return (
            f"the environment identity of {whose} is unknown: the runner does not "
            f"report {', '.join(unknown)}"
        )
    return None


def _time(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def _entry_problem(
    lesson: str, entry: object, run: dict, depth: int, identity: str
) -> str | None:
    """Why the record of ``lesson`` in a base of ``run`` at chain ``depth``,
    whose environment identity is ``identity``, is incomplete or
    inconsistent, or None."""
    if not isinstance(entry, dict) or not isinstance(entry.get("executed"), bool):
        return f"the base's provenance record is incomplete for {lesson}"
    origin = entry.get("origin")
    if not isinstance(origin, dict):
        return f"the base records no origin for {lesson}"
    if (
        not isinstance(origin.get("run"), int)
        or not isinstance(origin.get("commit"), str)
        or not isinstance(origin.get("depth"), int)
        or not isinstance(origin.get("enforced"), dict)
        or origin.get("environment") != _digest(origin["enforced"])
    ):
        return f"the base's provenance record is incomplete for {lesson}"
    if _time(origin.get("time")) is None:
        return f"the base records no time of execution for {lesson}"
    # Every link of a chain required the enforced identity equal, so an
    # executed result and an inherited one alike name the base's.
    if origin["environment"] != identity:
        return (
            f"the base's record of {lesson} names another environment than "
            "the run that produced the base"
        )
    if entry["executed"]:
        if (origin["run"], origin["commit"], origin["depth"]) != (
            run["id"],
            run["commit"],
            depth,
        ):
            return f"the base's record of {lesson} is not the result of this run"
    elif origin["run"] == run["id"] or not 0 <= origin["depth"] < depth:
        return f"the base's record of {lesson} is not an inherited result"
    return None


def _chain_problem(
    provenance: dict, run: dict, lessons: set[str], previous: dict | None
) -> str | None:
    """Why the lessons, the chain, and the derivation of ``provenance`` (the
    record of a base of ``run`` holding ``lessons``) are incomplete or
    inconsistent, or None. A base derived from another is checked against
    ``previous``, the record of that base, and is rejected without it."""
    chain = provenance.get("chain")
    entries = provenance.get("lessons")
    if not isinstance(chain, dict) or not isinstance(entries, dict) or not entries:
        return "the base's provenance record is incomplete"
    if set(entries) != lessons:
        missing = sorted(lessons - set(entries))
        extra = sorted(set(entries) - lessons)
        return (
            "the base's provenance record does not cover exactly the base's "
            f"lessons (missing {missing}, not in the base {extra})"
        )
    depth = chain.get("depth")
    if not isinstance(depth, int) or depth < 0:
        return "the base's provenance record has no depth"
    if not isinstance(chain.get("start"), int):
        return "the base's provenance record names no start of its chain"
    for lesson, entry in sorted(entries.items()):
        problem = _entry_problem(
            lesson, entry, run, depth, provenance["environment"]["identity"]
        )
        if problem:
            return problem
    inherited = {
        lesson: entry["origin"]
        for lesson, entry in entries.items()
        if not entry["executed"]
    }
    derived_from = provenance.get("derived_from")
    if depth == 0:
        if derived_from is not None or inherited or chain["start"] != run["id"]:
            return "the base's chain of depth 0 is not a complete execution"
        return None
    if (
        not inherited
        or chain["start"] == run["id"]
        or not isinstance(derived_from, dict)
        or not isinstance(derived_from.get("run"), int)
        or derived_from["run"] == run["id"]
        or not isinstance(derived_from.get("provenance"), str)
    ):
        return "the base's derivation is incomplete or inconsistent with its chain"
    if not isinstance(previous, dict):
        return (
            f"the base it was derived from (run {derived_from['run']}) is not "
            "given, so the derivation cannot be checked"
        )
    if _digest(previous) != derived_from["provenance"]:
        return "the base's derivation names another provenance record"
    previous_chain = previous.get("chain")
    previous_run = previous.get("run")
    previous_lessons = previous.get("lessons")
    if (
        not isinstance(previous_run, dict)
        or previous_run.get("id") != derived_from["run"]
        or not isinstance(previous_chain, dict)
        or previous_chain.get("start") != chain["start"]
        or previous_chain.get("depth") != depth - 1
        or not isinstance(previous_lessons, dict)
    ):
        return "the base's chain does not continue the base it was derived from"
    for lesson, origin in sorted(inherited.items()):
        entry = previous_lessons.get(lesson)
        if not isinstance(entry, dict) or entry.get("origin") != origin:
            return (
                f"the inherited result of {lesson} is not the one of the base "
                "it was derived from"
            )
    return None


def accept(
    provenance: dict,
    run: dict,
    *,
    repository: str,
    environment: dict,
    now: datetime,
    lessons: Iterable[str],
    previous: dict | None = None,
) -> str | None:
    """Why the base whose record is ``provenance`` cannot be inherited from by
    a run in ``environment`` at ``now``, or None when it can.

    ``run`` is the record of the run that uploaded the base, read from the
    runs API by the caller, as ``scripts/fetch-base.sh`` reads it; the
    record inside the base is checked against it and decides nothing by
    itself. ``lessons`` are the lessons the base holds (those of its
    ``digests.json``): the record must give the origin of each, and of no
    other. ``previous`` is the record of the base this one was derived
    from: a derived base is accepted only when its derivation names that
    record's digest, continues its chain, and inherited exactly its origins.
    """
    problem = _run_problem(run, repository)
    if problem:
        return problem
    if not isinstance(provenance, dict) or provenance.get("format") != FORMAT:
        return "the base's provenance record is of another format"
    recorded = provenance.get("run")
    if not isinstance(recorded, dict) or recorded.get("id") != run["id"]:
        return (
            "the base's provenance record names another run than the one that "
            "uploaded it"
        )
    if recorded.get("commit") != run["commit"]:
        return "the base's provenance record names another commit than its run"
    problem = _environment_problem(
        provenance.get("environment"), "the base"
    ) or _environment_problem(environment, "this run")
    if problem:
        return problem
    if provenance["environment"]["identity"] != environment["identity"]:
        return "the environment identity differs from the base's"
    problem = _chain_problem(provenance, run, set(lessons), previous)
    if problem:
        return problem
    if provenance["chain"]["depth"] + 1 > MAX_DEPTH:
        return f"the chain would be deeper than {MAX_DEPTH} bases"
    for lesson, entry in sorted(provenance["lessons"].items()):
        if now - _time(entry["origin"]["time"]) > MAX_AGE:
            return f"the result of {lesson} is older than {MAX_AGE.days} days"
    return None


def derive(
    previous: dict | None,
    selection: dict,
    run: dict,
    environment: dict,
    now: datetime,
) -> dict:
    """The provenance record of the base this run leaves.

    ``selection`` is what ``pbc.authoring.selection`` wrote: the lessons the
    run executed and the lessons it reused from ``previous`` (the accepted
    base's record, None for a complete execution). An inherited result keeps
    its origin; an executed one gets this run as its origin.
    """
    reuse = selection.get("reuse", []) if previous is not None else []
    if previous is not None and selection.get("mode") != "selective":
        reuse = []
    inherited = {}
    for lesson in reuse:
        entry = previous["lessons"].get(lesson) if previous else None
        if not isinstance(entry, dict) or "origin" not in entry:
            raise ValueError(f"the base has no origin for the reused lesson {lesson}")
        inherited[lesson] = entry["origin"]
    if inherited:
        depth = previous["chain"]["depth"] + 1
        start = previous["chain"]["start"]
        derived_from = {"run": previous["run"]["id"], "provenance": _digest(previous)}
    else:
        depth = 0
        start = run["id"]
        derived_from = None
    this = {
        "run": run["id"],
        "commit": run["commit"],
        "environment": environment["identity"],
        "enforced": environment.get("enforced", {}),
        "recorded": environment.get("recorded", {}),
        "depth": depth,
        "time": now.astimezone(UTC).isoformat(),
    }
    lessons = {}
    for lesson in selection["lessons"]:
        if lesson in inherited:
            lessons[lesson] = {"executed": False, "origin": inherited[lesson]}
        else:
            lessons[lesson] = {"executed": True, "origin": this}
    return {
        "format": FORMAT,
        "run": {
            "id": run["id"],
            "commit": run["commit"],
            "event": run.get("event"),
            "branch": run.get("head_branch"),
            "repository": run.get("repository"),
            "verify": run.get("verify"),
            "time": this["time"],
        },
        "environment": environment,
        "derived_from": derived_from,
        "chain": {"depth": depth, "start": start},
        "lessons": lessons,
    }


def site_record(provenance: dict) -> dict:
    """The provenance record the published site carries beside its checksums
    (ADR 017 decision 2): per lesson, executed in this run or inherited."""
    run = provenance["run"]
    lessons = {}
    for lesson, entry in provenance["lessons"].items():
        origin = entry["origin"]
        if entry["executed"]:
            lessons[lesson] = {"status": f"executed in this run ({run['id']})"}
        else:
            lessons[lesson] = {
                "status": (
                    f"inherited from run {origin['run']} at commit {origin['commit']}"
                ),
                "run": origin["run"],
                "commit": origin["commit"],
                "environment": origin["environment"],
                "depth": origin["depth"],
            }
    return {
        "format": FORMAT,
        "run": run["id"],
        "commit": run["commit"],
        "chain": provenance["chain"],
        "lessons": lessons,
    }


def read(directory: Path) -> dict | None:
    """The provenance record of the base at ``directory``, or None."""
    try:
        data = json.loads((directory / PROVENANCE).read_text(encoding="utf-8"))
    except OSError:
        return None
    except ValueError:
        return None
    return data if isinstance(data, dict) and data.get("format") == FORMAT else None


def write(directory: Path, provenance: dict) -> Path:
    path = directory / PROVENANCE
    path.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", "utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Describe the provenance of a base: per lesson, its origin."
    )
    parser.add_argument("base", type=Path, help="the directory of the base")
    arguments = parser.parse_args(argv)
    provenance = read(arguments.base)
    if provenance is None:
        print(f"{arguments.base} holds no provenance record of format {FORMAT}.")
        return 1
    record = site_record(provenance)
    print(
        f"run {record['run']} at commit {record['commit']}, "
        f"chain depth {record['chain']['depth']}"
    )
    for lesson, entry in sorted(record["lessons"].items()):
        print(f"  {lesson}: {entry['status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
