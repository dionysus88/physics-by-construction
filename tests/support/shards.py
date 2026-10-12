"""Divide the checks of the built site over several runs of pytest.

``pytest tests/e2e/<file> --shard i/n`` runs part ``i`` of ``n`` of a test
file. Which test belongs to which part is written in ``tests/e2e/shards.json``
and never follows from the order of collection, so the parts together are the
file and no test runs twice (docs/development.md, "The checks of the built
site").

A file is divided in one of two ways:

- ``"by": "lesson"``: a test that is run once per lesson belongs to the part
  that lists its lesson. A lesson that no part lists belongs to the part that
  a checksum of its path selects, so a new lesson runs without a change here,
  in the same part on every machine. Tests that are not about one lesson run
  in part 1.
- ``"by": "test"``: a test belongs to the part that lists its name, and to
  part 1 when no part does, so a new test runs without a change here.

An entry that names a lesson or a test that does not exist is an error too:
the file then no longer describes the division.
"""

import json
import re
import zlib
from collections.abc import Iterable, Mapping
from pathlib import Path

from support.paths import REPO_ROOT

SHARDS_FILE = REPO_ROOT / "tests" / "e2e" / "shards.json"


class ShardError(Exception):
    """The division asked for cannot be made."""


def parse(option: str) -> tuple[int, int]:
    """Read ``i/n`` and return ``(i, n)``."""
    match = re.fullmatch(r"([1-9][0-9]*)/([1-9][0-9]*)", option)
    if match is None or int(match.group(1)) > int(match.group(2)):
        raise ShardError(f"--shard {option}: expected <part>/<parts>, as in 1/2")
    return int(match.group(1)), int(match.group(2))


def table(path: Path = SHARDS_FILE) -> dict[str, dict]:
    return json.loads(path.read_text())


def part_of(
    file: str,
    tests: Iterable[tuple[str, str | None]],
    table: Mapping[str, Mapping],
    parts: int,
    known: Mapping[str, Iterable[str]],
) -> list[int]:
    """Return the part, counted from 1, of every test of one file.

    ``tests`` holds, per test, its name without parameters and the lesson it
    is run for, or ``None``. They may be a selection of the file, for example
    one test by its node ID. ``known`` holds everything that exists, whether
    selected or not: under ``"lesson"`` every lesson, under ``"test"`` every
    test of the file.
    """
    tests = list(tests)
    entry = table.get(file)
    if entry is None:
        raise ShardError(f"--shard: {file} has no division in tests/e2e/shards.json")
    lists = entry["shards"]
    if len(lists) != parts:
        raise ShardError(
            f"--shard: {file} is divided in {len(lists)} parts, not in {parts}"
        )
    by = entry["by"]
    if by not in ("lesson", "test"):
        raise ShardError(f"--shard: {file} is divided by {by!r}, which is unknown")

    where: dict[str, int] = {}
    for number, keys in enumerate(lists, start=1):
        for key in keys:
            if key in where:
                raise ShardError(f"--shard: {file} lists {key} more than once")
            where[key] = number

    stale = sorted(set(where) - set(known[by]))
    if stale:
        raise ShardError(
            f"--shard: tests/e2e/shards.json lists for {file} what does not"
            f" exist: {', '.join(stale)}"
        )
    if by == "lesson":
        return [
            1 if lesson is None else where.get(lesson, unlisted(lesson, parts))
            for _, lesson in tests
        ]
    return [where.get(name, 1) for name, _ in tests]


def unlisted(lesson: str, parts: int) -> int:
    """Return the part of a lesson that no part lists.

    A checksum of the path, not Python's ``hash``: that one differs per run.
    """
    return zlib.crc32(lesson.encode()) % parts + 1
