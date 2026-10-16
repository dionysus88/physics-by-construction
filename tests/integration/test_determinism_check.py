"""The determinism check fails on any file that differs between two builds,
the previews included (F119; the audit of F118, "Redundancy verdict").

The regression test the audit asked for before the preview test's third
build was removed: two trees built by ``scripts/build-site.sh`` that differ
in one byte of one file under ``previews/``, in a missing preview, or in an
extra one make ``scripts/check-determinism.sh`` fail and name the file, in a
full run and in a selective run, and identical trees pass. The check runs
here with a fake ``scripts/build-site.sh`` that writes a fixture tree, so no
lesson executes.
"""

import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest
from support.checks import output
from support.paths import SCRIPTS

from pbc.authoring import selection as selecting

# What the second build of the determinism check leaves out of its copy of
# the sources: the first build and every file of a base.
COPY_LEAVES_OUT = {"_site", ".quarto", "_freeze", "_digests.json", "_timings.json"}

FAKE_BUILD = """#!/usr/bin/env bash
# build-site.sh <source> <output>: records what it was given and the names in
# <source>, and writes the fixture $FAKE_SECOND_BUILD as the build.
set -euo pipefail
{
  echo "source=$1"
  echo "output=$2"
  echo "selection=${PBC_STORE_SELECTION:-}"
  echo "names=$(ls -A "$1" | sort | tr '\\n' ' ')"
} >>"$FAKE_BUILD_LOG"
mkdir -p "$2"
cp -R "$FAKE_SECOND_BUILD"/. "$2"/
"""


def tree(directory: Path) -> Path:
    """A built site with one page and one preview."""
    (directory / "previews").mkdir(parents=True)
    (directory / "previews" / "a.png").write_bytes(b"one")
    (directory / "index.html").write_text("page")
    return directory


@pytest.fixture
def root(tmp_path: Path) -> Path:
    """A repository with the real determinism check, the fake build, the
    sources (with the state a build leaves behind), and a first build."""
    root = tmp_path / "root"
    scripts = root / "scripts"
    scripts.mkdir(parents=True)
    shutil.copy(SCRIPTS / "check-determinism.sh", scripts / "check-determinism.sh")
    build = scripts / "build-site.sh"
    build.write_text(FAKE_BUILD)
    build.chmod(build.stat().st_mode | stat.S_IXUSR)
    site = root / "site"
    site.mkdir()
    (site / "_quarto.yml").write_text("project:\n  type: website\n")
    (site / "lessons").mkdir()
    for name in COPY_LEAVES_OUT:
        if name.endswith(".json"):
            (site / name).write_text("{}")
        else:
            (site / name).mkdir()
    tree(site / "_site")
    return root


def check(root: Path, second: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(root / "scripts" / "check-determinism.sh")],
        cwd=root,
        env={
            **os.environ,
            "FAKE_SECOND_BUILD": str(second),
            "FAKE_BUILD_LOG": str(root / "build.log"),
        },
        capture_output=True,
        text=True,
        check=False,
    )


def selective(root: Path) -> None:
    selecting.write(
        root,
        {
            "format": selecting.SELECTION_FORMAT,
            "mode": "selective",
            "execute": ["site/lessons/s/01-one"],
            "reuse": [],
        },
    )


def differ(second: Path, difference: str) -> str:
    """Make the second tree differ from the first; return the file named."""
    if difference == "bytes":
        (second / "previews" / "a.png").write_bytes(b"two")
        return "previews/a.png"
    if difference == "missing":
        (second / "previews" / "a.png").unlink()
        return "previews/a.png"
    if difference == "extra":
        (second / "previews" / "b.png").write_bytes(b"one")
        return "previews/b.png"
    (second / "index.html").write_text("page ")
    return "index.html"


@pytest.mark.parametrize("run", ["full", "selective"])
def test_identical_builds_pass(root: Path, tmp_path: Path, run: str):
    if run == "selective":
        selective(root)
    result = check(root, tree(tmp_path / "second"))
    assert result.returncode == 0, output(result)
    assert "byte-identical (2 files)" in result.stdout


@pytest.mark.parametrize("run", ["full", "selective"])
@pytest.mark.parametrize("difference", ["bytes", "missing", "extra", "page"])
def test_a_differing_file_fails_the_check_and_is_named(
    root: Path, tmp_path: Path, run: str, difference: str
):
    if run == "selective":
        selective(root)
    second = tree(tmp_path / "second")
    named = differ(second, difference)
    result = check(root, second)
    assert result.returncode != 0, output(result)
    assert "two builds of the same sources differ" in result.stderr
    assert Path(named).name in result.stderr


@pytest.mark.parametrize("run", ["full", "selective"])
def test_the_second_build_starts_from_a_copy_without_the_first_build(
    root: Path, tmp_path: Path, run: str
):
    # Without the first build, the project cache, and the store: the copy is
    # the sources, and with a selection the second build gets it, so the
    # changed lessons execute twice and the unchanged ones are restored again
    # (ADR 014 decision 3).
    if run == "selective":
        selective(root)
    assert check(root, tree(tmp_path / "second")).returncode == 0
    log = dict(
        line.split("=", 1) for line in (root / "build.log").read_text().splitlines()
    )
    assert log["source"] != str(root / "site")
    assert Path(log["source"]).name == "site"
    names = set(log["names"].split())
    assert names == {"_quarto.yml", "lessons"}
    assert not names & COPY_LEAVES_OUT
    if run == "selective":
        assert log["selection"] == str(root / selecting.SELECTION_FILE)
    else:
        assert log["selection"] == ""


def test_without_a_first_build_the_check_fails(root: Path, tmp_path: Path):
    shutil.rmtree(root / "site" / "_site")
    result = check(root, tree(tmp_path / "second"))
    assert result.returncode != 0
    assert "no first build" in result.stderr
    assert not (root / "build.log").exists()
