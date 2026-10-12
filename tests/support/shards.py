"""Divide a test file of the built-site checks over several runs of pytest.

``pytest tests/e2e/<file> --shard i/n`` runs part ``i`` of ``n`` of a test
file. Which test belongs to which part is written in ``tests/e2e/shards.json``
and never follows from the order of collection, so the parts together are the
file and no test runs twice (docs/development.md, "The checks of the built
site").

A test belongs to the part that lists its name, and to part 1 when no part
does, so a new test runs without a change here. An entry that names a test
that does not exist is an error: the file then no longer describes the
division.
"""

import json
import re
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


def table(path: Path = SHARDS_FILE) -> dict[str, list[list[str]]]:
    return json.loads(path.read_text())


def part_of(
    file: str,
    tests: Iterable[str],
    table: Mapping[str, list[list[str]]],
    parts: int,
    known: Iterable[str],
) -> list[int]:
    """Return the part, counted from 1, of every test of one file.

    ``tests`` holds the name, without parameters, of every test to divide.
    They may be a selection of the file, for example one test by its node ID.
    ``known`` holds the name of every test of the file, selected or not.
    """
    lists = table.get(file)
    if lists is None:
        raise ShardError(f"--shard: {file} has no division in tests/e2e/shards.json")
    if len(lists) != parts:
        raise ShardError(
            f"--shard: {file} is divided in {len(lists)} parts, not in {parts}"
        )

    where: dict[str, int] = {}
    for number, names in enumerate(lists, start=1):
        for name in names:
            if name in where:
                raise ShardError(f"--shard: {file} lists {name} more than once")
            where[name] = number

    stale = sorted(set(where) - set(known))
    if stale:
        raise ShardError(
            f"--shard: tests/e2e/shards.json lists for {file} what does not"
            f" exist: {', '.join(stale)}"
        )
    return [where.get(name, 1) for name in tests]
