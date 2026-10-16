"""The single-page render of the targeted run (ADR 017 decision 7, F119).

``scripts/check-lesson-pages.sh`` renders each lesson the targeted run
selected, alone, in a clone of the working tree, and never builds the site.
It runs here on a copy of this repository's committed files, so a broken page
and a changed proof can be made without touching the checkout, and the
checkout's own site is never built. Each render executes a real lesson.
"""

import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest
from support import lesson_checks
from support.checks import output
from support.paths import REPO_ROOT, SCRIPTS

from pbc.authoring import selection as selecting

KINEMATICS = "site/lessons/mechanics/01-kinematics-as-a-program"
LEAN_LESSON = "site/lessons/lean/01-proving-what-the-simulation-showed"
# A fake Lean build: it records where it ran.
FAKE_LEAN = '#!/usr/bin/env bash\npwd >>"$FAKE_LEAN_LOG"\nexit 0\n'


@pytest.fixture(scope="module")
def pristine(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """A repository of the committed files of this checkout, on main."""
    root = tmp_path_factory.mktemp("pristine") / "repo"
    for file in lesson_checks.committed_files(REPO_ROOT):
        (root / file).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / file, root / file)
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "-C", root]
    subprocess.run([*git, "init", "-q", "-b", "main"], check=True)
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-qm", "The committed files"], check=True)
    return root


@pytest.fixture
def tree(pristine: Path, tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    shutil.copytree(pristine, root, symlinks=True)
    fake = root / "scripts" / "check-lean.sh"
    fake.write_text(FAKE_LEAN)
    fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
    return root


def select(root: Path, lessons: list[str], tier: str | None) -> None:
    data = {
        "format": selecting.SELECTION_FORMAT,
        "mode": "selective",
        "execute": lessons,
        "reuse": [],
    }
    if tier:
        data["tier"] = tier
    selecting.write(root, data)


def check(root: Path, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCRIPTS / "check-lesson-pages.sh"), str(root)],
        cwd=root,
        env={
            **os.environ,
            "UV_PROJECT": str(REPO_ROOT),
            "FAKE_LEAN_LOG": str(tmp_path / "lean.log"),
        },
        capture_output=True,
        text=True,
        check=False,
    )


def lean_runs(tmp_path: Path) -> list[str]:
    log = tmp_path / "lean.log"
    return log.read_text().splitlines() if log.exists() else []


def test_without_a_selection_there_is_nothing_to_render(tree, tmp_path):
    result = check(tree, tmp_path)
    assert result.returncode == 0, output(result)
    assert "Nothing to render" in result.stdout
    assert lean_runs(tmp_path) == []


def test_a_run_that_builds_the_site_leaves_nothing_to_render(tree, tmp_path):
    # The selection of a run with --base: the build executes the lessons.
    select(tree, [KINEMATICS], None)
    result = check(tree, tmp_path)
    assert result.returncode == 0, output(result)
    assert "Nothing to render" in result.stdout
    assert "cover every lesson" in result.stdout


def test_the_selected_lesson_renders_alone_in_a_clone_and_no_site_is_built(
    tree, tmp_path
):
    select(tree, [KINEMATICS], "targeted")
    result = check(tree, tmp_path)
    assert result.returncode == 0, output(result)
    assert f"Rendered {KINEMATICS}/index.qmd in " in result.stdout
    assert "no site was built" in result.stdout
    # Rendered in a clone, which is gone: the tree holds no page and no build.
    assert not (tree / "site" / "_site").exists()
    assert not (tree / "site" / "_freeze").exists()
    assert not list((tree / "site").rglob("*.html"))
    # No proof changed and the lesson displays none: no Lean build.
    assert lean_runs(tmp_path) == []


def test_a_page_that_does_not_render_fails_the_check(tree, tmp_path):
    page = tree / KINEMATICS / "index.qmd"
    page.write_text(
        page.read_text() + "\n```{python}\nraise SystemExit('broken cell')\n```\n"
    )
    select(tree, [KINEMATICS], "targeted")
    result = check(tree, tmp_path)
    assert result.returncode != 0
    assert f"the page {KINEMATICS}/index.qmd does not render" in result.stderr
    assert "broken cell" in result.stderr


def test_a_changed_proof_runs_the_lean_build_of_the_checkout(tree, tmp_path):
    proof = next((tree / "lean" / "PhysicsByConstruction").rglob("*.lean"))
    proof.write_text(proof.read_text() + "\n-- a change\n")
    select(tree, [KINEMATICS], "targeted")
    result = check(tree, tmp_path)
    assert result.returncode == 0, output(result)
    assert "a file under lean/ differs from the base branch" in result.stdout
    assert lean_runs(tmp_path) == [str(tree.resolve())]


def test_a_lesson_that_displays_lean_gets_the_lean_build_in_the_clone(tree, tmp_path):
    # As the page's commands say: the Lean build first, in the clone, then
    # the render of the page.
    select(tree, [LEAN_LESSON], "targeted")
    result = check(tree, tmp_path)
    assert result.returncode == 0, output(result)
    assert "a selected lesson displays Lean modules" in result.stdout
    [where] = lean_runs(tmp_path)
    assert where != str(tree.resolve()) and "lesson-pages." in where
    assert result.stdout.index("Lean build in the clone") < result.stdout.index(
        f"Rendering {LEAN_LESSON}/index.qmd alone"
    )
    assert f"Rendered {LEAN_LESSON}/index.qmd in " in result.stdout


def test_the_check_needs_a_working_tree(tmp_path):
    (tmp_path / "plain").mkdir()
    result = check(tmp_path / "plain", tmp_path)
    assert result.returncode != 0
    assert "not a Git working tree" in result.stderr
