"""The time budget of a lesson: 30 seconds, or the one that
scripts/lesson-budgets.conf gives it. scripts/check-lesson-pages.sh reads the
same file."""

from pathlib import Path, PurePosixPath

from support.paths import SCRIPTS

DEFAULT_BUDGET_SECONDS = 30
BUDGETS_FILE = SCRIPTS / "lesson-budgets.conf"


def read_budgets(path: Path = BUDGETS_FILE) -> dict[str, tuple[int, str]]:
    """The lessons with a budget of their own: directory below site/ to
    (seconds, reason)."""
    budgets = {}
    for line in path.read_text().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        lesson, seconds, reason = (field.strip() for field in line.split("|", 2))
        assert lesson not in budgets, f"{lesson} has two budgets"
        assert reason, f"the budget of {lesson} has no reason"
        budgets[lesson] = (int(seconds), reason)
    return budgets


def budget_seconds(lesson: str) -> int:
    """The budget of a lesson, given as the path of its built page
    ('lessons/<topic>/<lesson>/index.html') or as its directory."""
    path = PurePosixPath(lesson)
    directory = path.parent if path.suffix else path
    seconds, _ = read_budgets().get(str(directory), (DEFAULT_BUDGET_SECONDS, ""))
    return seconds
