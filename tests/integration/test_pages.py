"""Which pages a run with a base checks (ADR 014 decision 3, F61 step 6).

The checks of one page and the reproduction of a lesson read the selection the
run made. The tests use small built sites in a temporary directory and a
selection written by hand; ``test_selection.py`` shows how the selection is
made.
"""

import importlib.util
import json
import types
from pathlib import Path

import pytest
from support import site_checks
from support.paths import REPO_ROOT

from pbc.authoring import pages
from pbc.authoring import selection as selecting

BASE_COMMIT = "a" * 40
RUN_COMMIT = "b" * 40
LESSON_ONE = "lessons/s/01-one/index.html"
LESSON_TWO = "lessons/s/02-two/index.html"


def built(site: Path, commit: str, changed: dict[str, str] | None = None) -> Path:
    """A built site whose lesson pages name ``commit``."""
    files = {
        "index.html": "<p>Home</p>",
        LESSON_ONE: f"<p>One, built from {commit}.</p>",
        LESSON_TWO: f"<p>Two, built from {commit}.</p>",
        "lessons/s/01-one/index_files/fig.png": "figure",
        **(changed or {}),
    }
    for name, text in files.items():
        (site / name).parent.mkdir(parents=True, exist_ok=True)
        (site / name).write_text(text, encoding="utf-8")
    return site


@pytest.fixture
def base(tmp_path: Path) -> Path:
    """The record of the base: its site built from another commit."""
    site = built(tmp_path / "base-site", BASE_COMMIT)
    directory = tmp_path / "base"
    directory.mkdir()
    (directory / pages.PAGES).write_text(
        json.dumps(pages.record(site, BASE_COMMIT)), encoding="utf-8"
    )
    return directory


def selective(base: Path, execute: list[str]) -> dict:
    return {
        "format": selecting.SELECTION_FORMAT,
        "mode": "selective",
        "base_directory": str(base),
        "execute": execute,
        "reuse": [],
    }


@pytest.fixture
def chosen(monkeypatch: pytest.MonkeyPatch):
    """Make a selection the selection of the run, and the commit its own."""

    def make(selection: dict | None) -> None:
        monkeypatch.setattr(selecting, "read", lambda root=REPO_ROOT: selection)
        monkeypatch.setattr(
            pages, "build_commit", lambda: types.SimpleNamespace(sha=RUN_COMMIT)
        )

    return make


def test_the_commit_is_the_only_difference_between_pages_of_two_commits(
    tmp_path: Path, base: Path
):
    site = built(tmp_path / "site", RUN_COMMIT)
    record = pages.read(base / pages.PAGES)

    assert pages.differing(site, record, RUN_COMMIT) == []


@pytest.mark.parametrize(
    "change",
    [
        {LESSON_TWO: f"<p>Two changed, built from {RUN_COMMIT}.</p>"},
        {"index.html": "<p>Home, changed</p>"},
        {"new/index.html": "<p>New</p>"},
    ],
    ids=["a lesson page", "a page that is not a lesson", "a page the base lacks"],
)
def test_a_page_that_differs_from_the_base_is_checked_and_nothing_else_is(
    tmp_path: Path, base: Path, chosen, change
):
    site = built(tmp_path / "site", RUN_COMMIT, change)
    chosen(selective(base, execute=[]))

    selected = pages.selected(site)

    assert selected == sorted(name for name in change if name.endswith(".html"))


def test_a_lesson_the_run_executed_is_checked_even_when_its_page_is_the_same(
    tmp_path: Path, base: Path, chosen
):
    site = built(tmp_path / "site", RUN_COMMIT)
    chosen(selective(base, execute=["site/lessons/s/01-one"]))

    assert pages.selected(site) == [LESSON_ONE]


def test_a_changed_figure_of_a_lesson_does_not_hide_behind_an_equal_page(
    tmp_path: Path, base: Path, chosen
):
    # The page of an executed lesson is checked whatever its bytes are.
    site = built(
        tmp_path / "site", RUN_COMMIT, {"lessons/s/01-one/index_files/fig.png": "new"}
    )
    chosen(selective(base, execute=["site/lessons/s/01-one"]))

    assert LESSON_ONE in pages.selected(site)


@pytest.mark.parametrize(
    "selection",
    [
        None,
        {"format": selecting.SELECTION_FORMAT, "mode": "full", "execute": []},
    ],
    ids=["no base", "a full run"],
)
def test_a_run_without_a_usable_base_checks_every_page(
    tmp_path: Path, chosen, selection
):
    chosen(selection)

    assert pages.selected(built(tmp_path / "site", RUN_COMMIT)) is None


@pytest.mark.parametrize(
    "damage",
    [
        lambda record: record.unlink(),
        lambda record: record.write_text("[1"),
        lambda record: record.write_text('{"format": 0, "files": {}}'),
        lambda record: record.write_text('{"format": 1, "files": {"a": 1}}'),
        lambda record: record.write_text("[1, 2]"),
        lambda record: record.write_text("7"),
        lambda record: record.write_text("null"),
    ],
    ids=[
        "missing",
        "truncated",
        "another format",
        "a checksum that is no text",
        "a list",
        "a number",
        "null",
    ],
)
def test_a_record_of_the_base_that_cannot_be_used_selects_every_page(
    tmp_path: Path, base: Path, chosen, damage
):
    damage(base / pages.PAGES)
    chosen(selective(base, execute=[]))

    assert pages.selected(built(tmp_path / "site", RUN_COMMIT)) is None


def test_the_checks_of_one_page_run_for_the_selected_pages_only(
    tmp_path: Path, base: Path, chosen, monkeypatch: pytest.MonkeyPatch
):
    site = built(
        tmp_path / "site",
        RUN_COMMIT,
        {LESSON_TWO: f"<p>Two changed, built from {RUN_COMMIT}.</p>"},
    )
    chosen(selective(base, execute=[]))
    monkeypatch.setattr(site_checks, "BUILT_SITE", site)

    names = [
        page.relative_to(site).as_posix() for page in site_checks.checked_pages(site)
    ]

    assert names == [LESSON_TWO]


def test_a_site_that_is_not_the_site_of_this_repository_is_checked_in_full(
    tmp_path: Path, base: Path, chosen
):
    site = built(tmp_path / "site", RUN_COMMIT)
    chosen(selective(base, execute=[]))

    assert len(site_checks.checked_pages(site)) == 3


# --- The reproduction of a lesson -------------------------------------------------


@pytest.fixture(scope="module")
def conftest():
    spec = importlib.util.spec_from_file_location(
        "e2e_conftest", REPO_ROOT / "tests" / "e2e" / "conftest.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reproduction(lesson: str, marked: bool = True):
    return types.SimpleNamespace(
        get_closest_marker=lambda name: object() if marked else None,
        callspec=types.SimpleNamespace(params={"lesson": lesson}),
    )


def test_the_reproduction_runs_for_the_lessons_the_run_executed(
    conftest, monkeypatch: pytest.MonkeyPatch
):
    items = [reproduction(LESSON_ONE), reproduction(LESSON_TWO)]
    selection = selective(Path("/base"), execute=["site/lessons/s/01-one"])
    monkeypatch.setattr(selecting, "read", lambda root: selection)

    skipped = conftest._reproductions_of_unchanged_lessons(items)

    assert skipped == [items[1]]


@pytest.mark.parametrize(
    "selection",
    [None, {"format": selecting.SELECTION_FORMAT, "mode": "full", "execute": []}],
    ids=["no base", "a full run"],
)
def test_the_reproduction_runs_for_every_lesson_without_a_usable_base(
    conftest, monkeypatch: pytest.MonkeyPatch, selection
):
    items = [reproduction(LESSON_ONE), reproduction(LESSON_TWO)]
    monkeypatch.setattr(selecting, "read", lambda root: selection)

    assert conftest._reproductions_of_unchanged_lessons(items) == []


def test_only_the_reproduction_of_a_lesson_is_left_out(
    conftest, monkeypatch: pytest.MonkeyPatch
):
    other = types.SimpleNamespace(
        get_closest_marker=lambda name: None,
        callspec=types.SimpleNamespace(params={"lesson": LESSON_TWO}),
    )
    unmarked = reproduction(LESSON_TWO, marked=False)
    selection = selective(Path("/base"), execute=[])
    monkeypatch.setattr(selecting, "read", lambda root: selection)

    assert conftest._reproductions_of_unchanged_lessons([other, unmarked]) == []


def test_the_build_script_records_the_pages_the_next_run_compares_with():
    script = (REPO_ROOT / "scripts" / "build-site.sh").read_text()

    assert "pbc.authoring.pages" in script and "_pages.json" in script
