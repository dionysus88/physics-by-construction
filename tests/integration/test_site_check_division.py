"""The checks of the built site are divided, and the division loses nothing.

``scripts/verify.conf`` declares the checks of the built site as several
checks, so that CI can run them side by side (docs/development.md, "The
checks of the built site"). These tests collect what each of them would run,
without a browser and without a built site, and compare it with everything
in ``tests/e2e``.
"""

import shlex
import subprocess
import sys

import pytest
from support import verify_conf
from support.checks import output, run_check
from support.paths import REPO_ROOT

PREFIX = "site-checks-"

# The checks of verify.conf before the checks of the built site were divided.
# Each still exists; 'site-checks' is now the checks named 'site-checks-*'.
ORIGINAL = [
    "preflight",
    "preflight-test",
    "lint",
    "format",
    "unit-tests",
    "dataset-checks",
    "lean-build",
    "check-tests",
    "lesson-checks",
    "site-build",
    "site-checks",
    "determinism",
    "template-structure",
    "shell-syntax",
    "docs-scripts",
    "docs-references",
    "documentation",
]


def _collected(result: subprocess.CompletedProcess[str]) -> list[str]:
    assert result.returncode == 0, output(result)
    return [line for line in result.stdout.splitlines() if "::" in line]


@pytest.fixture(scope="module")
def parts() -> dict[str, list[str]]:
    names = [name for name in verify_conf.checks() if name.startswith(PREFIX)]
    return {name: _collected(run_check(name, "--collect-only", "-q")) for name in names}


@pytest.fixture(scope="module")
def everything() -> list[str]:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/e2e", "--collect-only", "-q"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return _collected(result)


def test_the_parts_together_are_every_test_of_the_built_site(parts, everything):
    together = [test for tests in parts.values() for test in tests]
    assert sorted(together) == sorted(everything)


def test_no_test_runs_in_two_parts(parts):
    seen: dict[str, str] = {}
    for name, tests in parts.items():
        for test in tests:
            assert test not in seen, f"{test} runs in {seen[test]} and in {name}"
            seen[test] = name


def test_no_part_is_empty(parts):
    assert len(parts) >= 2
    for name, tests in parts.items():
        assert tests, f"{name} runs no test"


def test_every_part_is_pytest_on_the_built_site_checks():
    # A part that ran something else would not be part of this division.
    for name, command in verify_conf.checks().items():
        if name.startswith(PREFIX):
            words = shlex.split(command)
            assert words[:4] == ["uv", "run", "--locked", "pytest"], name
            assert words[4].startswith("tests/e2e"), name


def test_every_check_from_before_the_division_is_still_a_check():
    names = list(verify_conf.checks())
    divided = [name for name in names if name.startswith(PREFIX)]
    assert "site-checks" not in names
    undivided = [name for name in names if not name.startswith(PREFIX)]
    assert sorted([*undivided, "site-checks"]) == sorted(ORIGINAL)
    assert len(names) == len(set(names)) and divided


def test_every_part_has_a_group_of_its_own():
    groups = verify_conf.groups()
    own = [groups[name] for name in groups if name.startswith(PREFIX)]
    assert len(own) == len(set(own))
    others = {groups[name] for name in groups if not name.startswith(PREFIX)}
    assert not others & set(own)
    assert verify_conf.DEFAULT_GROUP not in own


def test_every_check_has_one_group_and_verify_sh_lists_those_groups():
    # verify.sh runs a group with --only; a group it does not list could not
    # be run, and a check in no listed group would run in no job of a CI
    # that runs each group.
    result = subprocess.run(
        ["./scripts/verify.sh", "--groups"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, output(result)
    listed = result.stdout.split()
    assert len(listed) == len(set(listed))
    groups = verify_conf.groups()
    assert set(groups) == set(verify_conf.checks())
    # The workflow self-tests have no group of their own: they are 'default'.
    assert set(listed) == set(groups.values()) | {verify_conf.DEFAULT_GROUP}


def test_one_test_can_be_selected_from_a_part(parts):
    # Rerunning one failing test with the command of its check works: what the
    # selection leaves out is not reported as missing from the division.
    for name in ("site-checks-lessons-2", "site-checks-pages-2"):
        test = parts[name][0]
        file = test.split("::")[0]
        command = verify_conf.command(name).replace(f" {file} ", f" '{test}' ")
        assert command != verify_conf.command(name)
        result = subprocess.run(
            ["bash", "-c", f"{command} --collect-only -q"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert _collected(result) == [test]


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        (["tests/e2e/test_lessons.py", "--shard", "3/2"], "expected <part>/<parts>"),
        (["tests/e2e/test_lessons.py", "--shard", "1/3"], "divided in 2 parts"),
        (["tests/e2e/test_home.py", "--shard", "1/2"], "has no division"),
    ],
)
def test_a_division_that_does_not_exist_is_an_error_and_runs_nothing(
    arguments, message
):
    result = subprocess.run(
        [sys.executable, "-m", "pytest", *arguments, "--collect-only", "-q"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 4, output(result)
    assert message in output(result)
