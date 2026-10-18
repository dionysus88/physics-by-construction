"""The budget of a lesson: the default, the one exception, and the agreement of
the shell check with the tests (scripts/lesson-budgets.conf)."""

import re
import subprocess

import pytest
from support import lesson_checks
from support.budgets import (
    BUDGETS_FILE,
    DEFAULT_BUDGET_SECONDS,
    budget_seconds,
    read_budgets,
)
from support.paths import REPO_ROOT, SCRIPTS, SITE_SOURCE

MONTE_CARLO = "lessons/agents-abm/01-particles-in-a-box"
SCRIPT = SCRIPTS / "check-lesson-pages.sh"
LESSONS = [
    page.parent.relative_to(SITE_SOURCE).as_posix()
    for page in lesson_checks.lesson_pages(REPO_ROOT)
]


def shell_budget(lesson: str, budgets_file=BUDGETS_FILE) -> int:
    """The budget the shell check computes: its own function, run alone."""
    function = re.search(
        r"^budget_of\(\) \{\n.*?^\}\n", SCRIPT.read_text(), re.M | re.S
    )
    assert function, "the check has no budget_of function"
    script = (
        f"default_budget_seconds={DEFAULT_BUDGET_SECONDS}\n"
        f"budgets_file='{budgets_file}'\n{function.group(0)}"
        f'budget_of "$1"\n'
    )
    result = subprocess.run(
        ["bash", "-c", script, "bash", lesson],
        capture_output=True,
        text=True,
        check=True,
    )
    return int(result.stdout)


def test_the_default_budget_is_30_seconds():
    assert DEFAULT_BUDGET_SECONDS == 30
    assert (
        budget_seconds("lessons/mechanics/01-kinematics-as-a-program/index.html") == 30
    )


def test_only_the_monte_carlo_lesson_has_a_larger_budget_and_it_has_a_reason():
    assert MONTE_CARLO in LESSONS
    assert {lesson: seconds for lesson, (seconds, _) in read_budgets().items()} == {
        MONTE_CARLO: 60
    }
    assert "#206" in read_budgets()[MONTE_CARLO][1]
    for lesson in LESSONS:
        assert budget_seconds(lesson + "/index.html") == (
            60 if lesson == MONTE_CARLO else 30
        )


@pytest.mark.parametrize("lesson", LESSONS)
def test_the_shell_check_and_the_tests_agree(lesson: str):
    # The shell check names a lesson by its directory below the repository.
    assert shell_budget("site/" + lesson) == budget_seconds(lesson + "/index.html")


def test_the_shell_check_keeps_the_default_for_a_lesson_not_listed(tmp_path):
    table = tmp_path / "budgets.conf"
    table.write_text("# a comment\n\nlessons/a/b | 45 | because\n")
    assert shell_budget("site/lessons/a/b", table) == 45
    assert shell_budget("site/lessons/a/c", table) == 30
    assert shell_budget("site/lessons/a/bb", table) == 30


def test_a_lesson_over_its_budget_still_fails_each_check():
    # The exception only replaces the number; both checks still compare the
    # seconds with it and fail when they are not under it.
    assert re.search(r'-lt "\$budget_seconds" \]\]', SCRIPT.read_text())
    e2e = (REPO_ROOT / "tests/e2e/test_lessons.py").read_text()
    assert e2e.count("assert seconds < budget_seconds(lesson)") == 2
