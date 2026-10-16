"""The check site-checks-reproduction on the selections a run can make
(issue 200, a regression of F119).

A pull request that changes no lesson, such as one that changes only the
documentation, makes a selective run that executes no lesson: there is no
reproduction to run, and the check passes. A selection that executes a lesson
still runs that lesson's reproduction and fails when it does not reproduce,
and a run without a selection still fails when it selects no test.

The command of the check runs, as verify.sh runs it, in a clone of the
working tree that holds the selection of each case and no built site, so no
lesson executes.
"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest
from support import lesson_checks, verify_conf
from support.checks import output
from support.paths import REPO_ROOT, SITE_SOURCE

from pbc.authoring import selection as selecting

CHECK = "site-checks-reproduction"
REPRODUCTION = "test_reproduce_commands_regenerate_the_page_within_the_time_budget"


@pytest.fixture(scope="module")
def clone(tmp_path_factory: pytest.TempPathFactory) -> Path:
    target = tmp_path_factory.mktemp("clone")
    for file in lesson_checks.committed_files(REPO_ROOT):
        if file.as_posix() == selecting.SELECTION_FILE:
            continue
        (target / file).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / file, target / file)
    return target


def lessons() -> list[str]:
    return [
        page.parent.relative_to(REPO_ROOT).as_posix()
        for page in lesson_checks.lesson_pages(REPO_ROOT)
    ]


def select(clone: Path, execute: list[str] | None) -> None:
    """Write the selective run that executes ``execute``, or no selection
    for None (a run without a base)."""
    path = clone / selecting.SELECTION_FILE
    path.unlink(missing_ok=True)
    if execute is None:
        return
    every = lessons()
    selecting.write(
        clone,
        {
            "format": selecting.SELECTION_FORMAT,
            "mode": "selective",
            "reason": "",
            "base": {"id": "test"},
            "lessons": every,
            "execute": execute,
            "reuse": [lesson for lesson in every if lesson not in execute],
            "new": [],
        },
    )


def run_check(clone: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    command = verify_conf.command(CHECK)
    return subprocess.run(
        ["bash", "-eo", "pipefail", "-c", " ".join([command, *extra])],
        cwd=clone,
        # The environment of this checkout, as the reproduction itself uses.
        env={**os.environ, "UV_PROJECT": str(REPO_ROOT)},
        capture_output=True,
        text=True,
        check=False,
    )


def test_the_check_runs_the_reproductions_with_pytest():
    # What the cases below rely on: the entry is the pytest run of the
    # reproductions, whose empty selection tests/e2e/conftest.py decides.
    assert (
        verify_conf.command(CHECK) == "uv run --locked pytest tests/e2e -m same_machine"
    )


def test_a_selection_that_executes_no_lesson_passes(clone: Path):
    select(clone, [])

    result = run_check(clone)

    assert result.returncode == 0, output(result)
    assert "no reproduction to run" in result.stdout
    assert " deselected / 0 selected" in result.stdout


def test_a_run_without_a_selection_that_selects_no_test_still_fails(clone: Path):
    # Every lesson is selected without a base; an empty run then means the
    # tests are missing, which pytest's status 5 reports.
    select(clone, None)

    result = run_check(clone, "-k", "no_test_has_this_name")

    assert result.returncode == pytest.ExitCode.NO_TESTS_COLLECTED, output(result)
    assert "no reproduction to run" not in result.stdout


def test_a_selection_of_one_lesson_runs_its_reproduction(clone: Path):
    lesson = lessons()[0]
    select(clone, [lesson])

    result = run_check(clone, "--collect-only", "-q")

    assert result.returncode == 0, output(result)
    collected = [line for line in result.stdout.splitlines() if "::" in line]
    page = Path(lesson).relative_to(SITE_SOURCE.name).as_posix() + "/index.html"
    assert collected == [f"tests/e2e/test_lessons.py::{REPRODUCTION}[{page}]"]


def test_a_selection_of_one_lesson_fails_when_it_does_not_reproduce(clone: Path):
    # The clone has no built site to compare with: the one reproduction
    # cannot reproduce it, and the check fails instead of passing empty.
    select(clone, [lessons()[0]])

    result = run_check(clone)

    assert result.returncode == pytest.ExitCode.TESTS_FAILED, output(result)
    assert "1 error" in result.stdout or "1 failed" in result.stdout
    assert "no reproduction to run" not in result.stdout
