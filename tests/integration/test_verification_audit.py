"""The facts of the verification audit hold in the repository (F118).

``docs/verification-audit.md`` states what a full run executes and compares,
that the third build duplicates the determinism check, which inputs the check
identity has and which domain each affects, and how ``integration`` divides
into parts that run every test once. These tests read the code and the
document and fail when the two disagree, so the audit cannot go stale
unnoticed. They run no lesson and no browser.
"""

import ast
import re
import subprocess
import sys

import pytest
from support import lesson_checks, second_build, verify_conf
from support.paths import REPO_ROOT, SCRIPTS

from pbc.authoring import digest
from pbc.authoring import selection as selecting
from pbc.authoring import store as storing

AUDIT = REPO_ROOT / "docs" / "verification-audit.md"
READINESS = REPO_ROOT / "docs" / "release-readiness.md"
PREVIEW_TEST = "test_a_second_build_gives_byte_identical_previews"
# What the second build of both comparisons leaves out of the copy.
COPY_LEAVES_OUT = {"_site", ".quarto", "_freeze", "_digests.json", "_timings.json"}


def _section(heading: str) -> str:
    """The text of a section of the audit, from its heading to the next of
    the same or a higher level."""
    text = AUDIT.read_text(encoding="utf-8")
    start = re.search(rf"^(#+) {re.escape(heading)}\s*$", text, re.MULTILINE)
    assert start, f"the audit has no section {heading!r}"
    level = len(start.group(1))
    rest = text[start.end() :]
    end = re.search(rf"^#{{1,{level}}} ", rest, re.MULTILINE)
    return rest[: end.start()] if end else rest


def _rows(section: str) -> list[list[str]]:
    """The cells of the table rows of a section, without header and rule."""
    rows = []
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", cell) for cell in cells):
            continue
        rows.append(cells)
    return rows[1:]  # the header


def _names(cell: str) -> list[str]:
    return re.findall(r"`([^`]+)`", cell)


# The call graph: what each build does and how often a lesson executes.


def test_the_comparisons_that_need_the_machine_of_the_build_are_in_its_group():
    groups = verify_conf.groups()
    assert {name for name, group in groups.items() if group == "build"} == {
        "lean-build",
        "site-build",
        "determinism",
        "site-checks-reproduction",
    }
    # The three checks of the built site that read the artifact run in groups
    # of their own and execute no lesson: none of them builds.
    for name in ("site-checks-pages-1", "site-checks-pages-2", "site-checks-other"):
        assert groups[name].startswith("e2e-")
        assert "build-site" not in verify_conf.command(name)


def test_the_audit_names_every_check_of_the_group_build_and_the_e2e_groups():
    graph = _section("Call graph")
    for name, group in verify_conf.groups().items():
        if group == "build" or group.startswith("e2e-"):
            assert f"`{name}`" in graph, f"the call graph does not name {name}"


def test_a_lesson_executes_four_times_in_a_full_run():
    # build 1 is site-build, build 2 is determinism, build 3 is the preview
    # test, and the fourth execution is the reproduction of the lesson.
    commands = verify_conf.checks()
    assert commands["site-build"] == "./scripts/build-site.sh"
    assert commands["determinism"] == "./scripts/check-determinism.sh"
    assert "-m same_machine" in commands["site-checks-reproduction"]
    determinism = (SCRIPTS / "check-determinism.sh").read_text(encoding="utf-8")
    assert '"$root/scripts/build-site.sh" "$tmp/site"' in determinism

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/e2e",
            "-m",
            "same_machine",
            "--collect-only",
            "-q",
            "-p",
            "no:cacheprovider",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    collected = [line for line in result.stdout.splitlines() if "::" in line]
    reproductions = [line for line in collected if "reproduce_commands" in line]
    previews = [line for line in collected if PREVIEW_TEST in line]
    assert len(previews) == 1
    # One reproduction per lesson, and nothing else compares bytes on the
    # machine of the build.
    assert len(reproductions) + len(previews) == len(collected)
    assert len(reproductions) == len(lesson_checks.lesson_pages(REPO_ROOT))

    # The reproduction renders in a clone, which holds no store and no
    # selection, so it executes the lesson itself.
    source = (REPO_ROOT / "tests" / "e2e" / "test_lessons.py").read_text("utf-8")
    body = source[source.index("def test_reproduce_commands_regenerate") :]
    body = body[: body.index("\ndef test_format_2_lessons")]
    assert "PBC_STORE_SELECTION" not in body and "_freeze" not in body


# The verdict on the third build.


def _determinism_leaves_out() -> set[str]:
    script = (SCRIPTS / "check-determinism.sh").read_text(encoding="utf-8")
    removed = set()
    for line in script.splitlines():
        if line.startswith("rm -"):
            removed |= {
                token.removeprefix('"$tmp/site/').removesuffix('"')
                for token in line.split()
                if token.startswith('"$tmp/site/')
            }
    return removed


def test_both_second_builds_start_from_a_copy_without_the_same_state():
    assert _determinism_leaves_out() == COPY_LEAVES_OUT
    source = (REPO_ROOT / "tests" / "support" / "second_build.py").read_text("utf-8")
    patterns = ast.literal_eval(
        "(" + source.split("ignore_patterns(")[1].split(")")[0] + ")"
    )
    assert set(patterns) == COPY_LEAVES_OUT


def test_a_selection_that_is_not_selective_restores_nothing(tmp_path):
    # The determinism check hands the selection file to its build whatever the
    # mode, and the preview test only when it is selective; the two agree
    # because a build restores nothing for any other mode.
    site = tmp_path / "site"
    site.mkdir()
    assert storing.prepare(site, None) == []
    assert storing.prepare(site, {"mode": "full"}) == []
    root = tmp_path / "root"
    named = selecting.write(
        root, {"format": selecting.SELECTION_FORMAT, "mode": "full"}
    )
    assert second_build.selection_environment(root) == {}
    selecting.write(root, {"format": selecting.SELECTION_FORMAT, "mode": "selective"})
    assert second_build.selection_environment(root) == {
        "PBC_STORE_SELECTION": str(named)
    }
    script = (SCRIPTS / "check-determinism.sh").read_text(encoding="utf-8")
    assert "selection.json" in script and "PBC_STORE_SELECTION" in script


def test_the_preview_test_compares_only_what_the_determinism_check_compares():
    script = (SCRIPTS / "check-determinism.sh").read_text(encoding="utf-8")
    # Every file of the first build, names and bytes.
    assert 'diff -r "$first" "$tmp/second"' in script
    source = (REPO_ROOT / "tests" / "e2e" / "test_lessons.py").read_text("utf-8")
    start = source.index(f"def {PREVIEW_TEST}")
    body = source[start:]
    # The files of previews/ and nothing else.
    assert '(site_dir / "previews").glob("*")' in body
    assert body.count("site_dir /") == body.count('site_dir / "previews"')
    assert "second_build.build_copy(SITE_SOURCE, second, tmp_path)" in body


@pytest.mark.parametrize("difference", ["bytes", "missing", "extra"])
def test_the_comparison_of_the_determinism_check_fails_on_a_differing_preview(
    tmp_path, difference
):
    # The property the regression test of F119 needs: with the comparison the
    # script makes, a preview that differs between two builds fails, by bytes,
    # by a missing file, or by an extra file, and the output names the file.
    first, second = tmp_path / "first", tmp_path / "second"
    for tree in (first, second):
        (tree / "previews").mkdir(parents=True)
        (tree / "previews" / "a.png").write_bytes(b"one")
        (tree / "index.html").write_text("page")
    same = subprocess.run(["diff", "-r", str(first), str(second)], capture_output=True)
    assert same.returncode == 0
    if difference == "bytes":
        (second / "previews" / "a.png").write_bytes(b"two")
    elif difference == "missing":
        (second / "previews" / "a.png").unlink()
    else:
        (second / "previews" / "b.png").write_bytes(b"one")
    result = subprocess.run(
        ["diff", "-rq", str(first), str(second)], capture_output=True, text=True
    )
    assert result.returncode != 0
    assert ".png" in result.stdout


# The validity domains of the check identity.


def _identity_rows() -> dict[str, dict]:
    rows = {}
    for cells in _rows(_section("Classification of the inputs")):
        names = _names(cells[0])
        assert len(names) == 1, cells
        rows[names[0]] = {
            "domains": [d for d, mark in zip("SRVB", cells[1:5], strict=True) if mark],
            "verdict": cells[5],
        }
    return rows


def test_every_input_of_the_check_identity_is_classified_in_the_audit():
    inputs = set(digest.CHECK_FILES) | set(digest.CHECK_DIRECTORIES)
    classified = set(_identity_rows())
    assert inputs - classified == set(), (
        "an input of the check identity that the audit does not classify "
        "belongs to every domain (ADR 014 decision 10): classify it"
    )
    assert classified - inputs == set(), "the audit classifies an input that is gone"


def test_the_verdict_of_an_input_agrees_with_its_domains():
    for name, row in _identity_rows().items():
        if row["verdict"].startswith("every domain"):
            assert len(row["domains"]) >= 2, name
        else:
            assert row["verdict"].startswith("V only"), name
            assert row["domains"] == ["V"], name


def test_no_check_that_a_base_reduces_reads_the_integration_tests():
    # What the audit says makes tests/integration splittable from the
    # identity with a complete-input test: the builds, the reproductions, and
    # the per-page checks neither read nor import it. The only mentions are
    # comments and docstrings, the check that runs it, and the identity.
    allowed = {
        "tests/support/site_checks.py",
        "tests/support/lesson_checks.py",
        "scripts/verify.conf",
        "src/pbc/authoring/digest.py",
    }
    mentions = set()
    for directory in ("tests/e2e", "tests/support", "scripts", "src", ".github"):
        for path in (REPO_ROOT / directory).rglob("*"):
            if not path.is_file() or path.suffix not in {".py", ".sh", ".yml", ".conf"}:
                continue
            if "tests/integration" in path.read_text(encoding="utf-8"):
                mentions.add(path.relative_to(REPO_ROOT).as_posix())
    assert mentions <= allowed, sorted(mentions - allowed)
    for path in [
        *(REPO_ROOT / "tests" / "e2e").glob("*.py"),
        *(REPO_ROOT / "tests" / "support").glob("*.py"),
    ]:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported = {
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        } | {
            a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names
        }
        assert not [m for m in imported if m.split(".")[0] == "integration"], path


# The division of integration.


def _parts() -> tuple[list[str], list[str]]:
    rows = _rows(
        _section("Division into independent parts").split("What it would shorten")[0]
    )
    named = {int(cells[0]): _names(cells[1]) for cells in rows}
    return named[1], named[2]


def _collect(*arguments: str) -> list[str]:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--collect-only",
            "-q",
            "-p",
            "no:cacheprovider",
            *arguments,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return [line for line in result.stdout.splitlines() if "::" in line]


def test_the_proposed_parts_of_integration_run_every_test_exactly_once():
    first, second = _parts()
    here = REPO_ROOT / "tests" / "integration"
    present = sorted(p.name for p in here.glob("test_*.py"))
    named = [*first, *second]
    assert len(named) == len(set(named)), "a file is named in two parts"
    assert set(named) <= set(present), sorted(set(named) - set(present))
    rest = [name for name in present if name not in named]
    assert rest and "test_verification_audit.py" in rest

    directory = "tests/integration"
    whole = _collect(directory)
    one = _collect(*[f"{directory}/{name}" for name in first])
    two = _collect(*[f"{directory}/{name}" for name in second])
    three = _collect(directory, *[f"--ignore={directory}/{name}" for name in named])
    assert whole and one and two and three
    assert sorted(one + two + three) == sorted(whole)
    assert len(set(whole)) == len(whole)


# The record of the measurements.


def test_the_runs_the_audit_cites_are_recorded_with_the_measurements():
    cited = set(re.findall(r"\b3[0-9]{10}\b", AUDIT.read_text(encoding="utf-8")))
    readiness = READINESS.read_text(encoding="utf-8")
    assert cited
    assert {run for run in cited if run not in readiness} == set()
    section = readiness[readiness.index("(F118), measured 2026-10-15") :]
    assert "ADR 015" in section and "15-minute target" in section
    assert "projection" in section.lower()
