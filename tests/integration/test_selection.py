"""The selection of a run against a base (ADR 014 decisions 2 to 5, F61).

The selection names what a run executes. The tests run on a small repository
written to a temporary directory, with a base made from it, and change one
input at a time. ``scripts/verify.sh --base`` is exercised on the same
repository with a stub for ``uv``.
"""

import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import pytest
from support.paths import REPO_ROOT
from test_lesson_digest import FILES, LESSON, _lesson, _write

from pbc.authoring import selection as selecting
from pbc.authoring.digest import CHECK_DIRECTORIES, CHECK_FILES, render

LESSON_TWO = "site/lessons/s/02-two"
CHECK_INPUTS = [
    "scripts/verify.sh",
    "scripts/verify.conf",
    "scripts/build-site.sh",
    "scripts/check-determinism.sh",
    "tests/e2e/shards.json",
    "tests/e2e/test_one.py",
    "tests/support/helper.py",
    "tests/integration/test_two.py",
    "pyproject.toml",
    "uv.lock",
    ".github/actions/prepare/action.yml",
]


def make_base(root: Path, base: Path) -> Path:
    """A base of the tree at ``root``: its digests and a store entry per lesson."""
    base.mkdir(parents=True, exist_ok=True)
    (base / "digests.json").write_text(render(root), encoding="utf-8")
    for lesson in (LESSON, LESSON_TWO):
        out = base / "freeze" / Path(lesson).relative_to("site") / "index"
        (out / "execute-results").mkdir(parents=True, exist_ok=True)
        (out / "execute-results" / "html.json").write_text("{}", encoding="utf-8")
    return base


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    for name, text in FILES.items():
        _write(root, name, text)
    _write(root, "src/pbc/data/__init__.py", 'SAMPLES_DIR = "data/samples"\n')
    _write(root, f"{LESSON}/index.qmd", _lesson("from pbc.mech.top import VALUE\n"))
    for name in CHECK_INPUTS:
        _write(root, name, "check\n")
    return root


@pytest.fixture
def base(repository: Path, tmp_path: Path) -> Path:
    return make_base(repository, tmp_path / "base")


def append(root: Path, name: str) -> None:
    path = root / name
    path.write_text(path.read_text(encoding="utf-8") + "\n# changed\n", "utf-8")


def chosen(root: Path, base: Path | None) -> dict:
    return selecting.select(root, base)


def test_an_unchanged_tree_executes_nothing(repository, base):
    result = chosen(repository, base)
    assert result["mode"] == "selective"
    assert result["execute"] == []
    assert result["reuse"] == [LESSON, LESSON_TWO]


def test_the_selection_names_exactly_the_lessons_whose_digest_differs(repository, base):
    append(repository, f"{LESSON}/index.qmd")
    result = chosen(repository, base)
    assert (result["execute"], result["reuse"]) == ([LESSON], [LESSON_TWO])


def test_a_new_lesson_is_executed(repository, base):
    _write(
        repository,
        "site/lessons/s/03-three/index.qmd",
        "---\ntitle: T\n---\n\n```{python}\nx = 1\n```\n",
    )
    assert chosen(repository, base)["execute"] == ["site/lessons/s/03-three"]


def test_retitling_a_lesson_does_not_select_the_others(repository, base):
    _write(
        repository,
        f"{LESSON_TWO}/index.qmd",
        "---\ntitle: Renamed\n---\n\n```{python}\nx = 1\n```\n",
    )
    assert chosen(repository, base)["execute"] == [LESSON_TWO]


@pytest.mark.parametrize(
    "name",
    [
        "uv.lock",
        "pyproject.toml",
        ".python-version",
        "src/pbc/authoring/__init__.py",
        "site/_quarto.yml",
        "site/_filters/f.lua",
        "site/assets/a.css",
        "site/index.qmd",
        "site/glossary.yaml",
        "lean/lean-toolchain",
        "lean/lake-manifest.json",
    ],
)
def test_a_changed_shared_input_selects_every_lesson(repository, base, name):
    append(repository, name)
    result = chosen(repository, base)
    if name in {"uv.lock", "pyproject.toml"}:
        assert result["mode"] == "full"  # also a check input
    assert result["execute"] == [LESSON, LESSON_TWO]
    assert result["reuse"] == []


@pytest.mark.parametrize(
    "name", ["src/pbc/mech/top.py", "src/pbc/mech/middle.py", "src/pbc/mech/bottom.py"]
)
def test_a_changed_module_selects_the_lessons_that_import_it(repository, base, name):
    append(repository, name)
    assert chosen(repository, base)["execute"] == [LESSON]


def test_a_module_nobody_imports_selects_nothing(repository, base):
    append(repository, "src/pbc/mech/other.py")
    assert chosen(repository, base)["execute"] == []


def test_a_module_whose_importers_cannot_be_followed_selects_every_lesson(
    repository, base
):
    _write(repository, "src/pbc/mech/other.py", "import importlib\nimportlib.x\n")
    assert chosen(repository, base)["execute"] == [LESSON, LESSON_TWO]


def test_a_lesson_without_a_digest_selects_every_lesson(repository, base):
    _write(
        repository,
        LESSON_TWO + "/index.qmd",
        "---\ntitle: Two\n---\n\n```{python}\n__import__('os')\n```\n",
    )
    result = chosen(repository, base)
    assert result["mode"] == "full"
    assert "no input digest" in result["reason"]
    assert result["execute"] == [LESSON, LESSON_TWO]


def test_no_base_selects_every_lesson(repository):
    result = chosen(repository, None)
    assert result["mode"] == "full"
    assert result["execute"] == [LESSON, LESSON_TWO]
    assert result["base"] is None


def break_missing(base: Path) -> None:
    shutil.rmtree(base)


def break_truncated(base: Path) -> None:
    text = (base / "digests.json").read_text(encoding="utf-8")
    (base / "digests.json").write_text(text[: len(text) // 2], encoding="utf-8")


def break_format(base: Path) -> None:
    data = json.loads((base / "digests.json").read_text(encoding="utf-8"))
    data["format"] = 0
    (base / "digests.json").write_text(json.dumps(data), encoding="utf-8")


def break_identity(base: Path) -> None:
    data = json.loads((base / "digests.json").read_text(encoding="utf-8"))
    del data["identity"]
    (base / "digests.json").write_text(json.dumps(data), encoding="utf-8")


def break_lessons(base: Path) -> None:
    data = json.loads((base / "digests.json").read_text(encoding="utf-8"))
    data["lessons"] = []
    (base / "digests.json").write_text(json.dumps(data), encoding="utf-8")


def break_store(base: Path) -> None:
    shutil.rmtree(base / "freeze" / "lessons" / "s" / "02-two")


def break_store_symlink(base: Path) -> None:
    entry = base / "freeze" / "lessons" / "s" / "02-two" / "index"
    (entry / "leak").symlink_to("/etc/hosts")


def break_store_result(base: Path) -> None:
    entry = base / "freeze" / "lessons" / "s" / "02-two" / "index"
    (entry / "execute-results" / "html.json").write_text("[1", encoding="utf-8")


@pytest.mark.parametrize(
    "damage",
    [
        break_store_symlink,
        break_store_result,
        break_missing,
        break_truncated,
        break_format,
        break_identity,
        break_lessons,
        break_store,
    ],
)
def test_a_base_that_cannot_be_used_selects_every_lesson(repository, base, damage):
    damage(base)
    result = chosen(repository, base)
    assert result["mode"] == "full"
    assert result["reason"]
    assert result["execute"] == [LESSON, LESSON_TWO]
    assert result["reuse"] == []


@pytest.mark.parametrize("name", CHECK_INPUTS)
def test_a_change_to_the_checks_makes_the_run_a_full_run(repository, base, name):
    append(repository, name)
    result = chosen(repository, base)
    assert result["mode"] == "full"
    assert "checks changed" in result["reason"]
    assert result["execute"] == [LESSON, LESSON_TWO]
    assert result["reuse"] == []


def test_every_input_of_the_identity_is_in_the_tested_list():
    declared = set(CHECK_FILES)
    assert declared <= set(CHECK_INPUTS)
    assert {Path(p).parts[:2] for p in CHECK_INPUTS if p.startswith("tests/")} == {
        tuple(Path(d).parts) for d in CHECK_DIRECTORIES
    }


def test_the_selection_is_written_where_the_checks_read_it(repository, base):
    selecting.write(repository, chosen(repository, base))
    assert selecting.read(repository)["mode"] == "selective"
    assert selecting.read(repository.parent) is None


# --- scripts/verify.sh ---------------------------------------------------


@pytest.fixture
def project(repository: Path, tmp_path: Path) -> Path:
    """The repository with the real verification script, a trivial check, and
    a stub for ``uv`` that runs this interpreter against this source tree."""
    for name in ("verify.sh", "lib/verification.sh", "lib/fingerprint.sh"):
        shutil.copy(REPO_ROOT / "scripts" / name, repository / "scripts" / name) if (
            repository / "scripts" / Path(name).parent
        ).is_dir() else (
            (repository / "scripts" / Path(name).parent).mkdir(parents=True),
            shutil.copy(REPO_ROOT / "scripts" / name, repository / "scripts" / name),
        )
    (repository / "scripts" / "verify.conf").write_text(
        "pass [one]: true\npass-too [two]: true\n", encoding="utf-8"
    )
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stub = bin_dir / "uv"
    stub.write_text(
        '#!/usr/bin/env bash\nwhile [[ "$1" != python ]]; do shift; done; shift\n'
        f'PYTHONPATH="{REPO_ROOT / "src"}" exec "{sys.executable}" "$@"\n',
        encoding="utf-8",
    )
    stub.chmod(stub.stat().st_mode | stat.S_IEXEC)
    return repository


def verify(project: Path, tmp_path: Path, *arguments: str | Path):
    env = {**os.environ, "PATH": f"{tmp_path / 'bin'}:{os.environ['PATH']}"}
    return subprocess.run(
        ["bash", "scripts/verify.sh", *map(str, arguments)],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_verify_without_a_base_runs_everything_and_writes_no_selection(
    project, tmp_path
):
    stale = project / selecting.SELECTION_FILE
    stale.parent.mkdir(parents=True, exist_ok=True)
    stale.write_text("{}", encoding="utf-8")
    outcome = verify(project, tmp_path)
    assert outcome.returncode == 0, outcome.stderr
    assert "Selection" not in outcome.stdout
    assert not stale.exists()


def test_verify_with_a_base_writes_the_selection_once_and_reports_it(project, tmp_path):
    made = make_base(project, tmp_path / "base")
    append(project, f"{LESSON}/index.qmd")
    outcome = verify(project, tmp_path, "--base", made)
    assert outcome.returncode == 0, outcome.stderr
    assert "selective run against base" in outcome.stdout
    assert "1 of 2 lessons executed" in outcome.stdout
    assert selecting.read(project)["execute"] == [LESSON]


def test_verify_combines_the_base_with_only(project, tmp_path):
    made = make_base(project, tmp_path / "base")
    outcome = verify(project, tmp_path, "--base", made, "--only", "one")
    assert outcome.returncode == 0, outcome.stderr
    assert "pass-too" not in outcome.stdout.split("Verification summary")[1]
    assert selecting.read(project)["mode"] == "selective"


def test_verify_with_a_base_that_is_missing_runs_in_full(project, tmp_path):
    outcome = verify(project, tmp_path, "--base", tmp_path / "nothing")
    assert outcome.returncode == 0, outcome.stderr
    assert selecting.read(project)["mode"] == "full"
    assert "no readable digests.json" in outcome.stdout


def test_a_failing_check_fails_a_run_with_a_base(project, tmp_path):
    made = make_base(project, tmp_path / "base")
    (project / "scripts" / "verify.conf").write_text("bad: false\n", encoding="utf-8")
    assert verify(project, tmp_path, "--base", made).returncode != 0


def test_base_cannot_be_combined_with_reuse_or_groups(project, tmp_path):
    made = make_base(project, tmp_path / "base")
    assert verify(project, tmp_path, "--base", made, "--reuse").returncode != 0
    assert verify(project, tmp_path, "--base", made, "--groups").returncode != 0


def test_the_module_imports_and_runs_as_a_command_on_the_pinned_python():
    done = subprocess.run(
        [sys.executable, "-m", "pbc.authoring.selection", "--help"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert done.returncode == 0, done.stderr
