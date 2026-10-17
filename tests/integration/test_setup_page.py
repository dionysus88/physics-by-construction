"""The setup page is tested by what it says and by what it installs (ADR 016
decision 5, F39, F117).

The page's Python-only commands are performed, from its text, in a fresh
clone of the working tree: the environment they produce holds the project's
packages and nothing of the `dev` group, and an experiment of each non-Lean
kind of lesson runs to completion in it. Every other command is either the
proof check, whose commands are the ones `./scripts/check-lean.sh` runs, or
sits in a "not verified" block that names what it needs. No command renders
or previews the website.
"""

import json
import os
import re
import shutil
import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path

import pytest
from support import lesson_checks
from support.paths import REPO_ROOT

PAGE = REPO_ROOT / "site" / "reproduce.qmd"
CHECK_LEAN = REPO_ROOT / "scripts" / "check-lean.sh"

_FENCE = re.compile(r"^```\{?\.?(bash)\b([^}]*)\}?\s*$")
_BARE_FENCE = re.compile(r"^```bash\s*$")
# What renders, previews, or verifies the website, or installs its tools; no
# instruction of the page names it (ADR 016 decision 1).
SITE_TOOLS = ("quarto", "build-site.sh", "verify.sh", "playwright", "preflight.sh")
# The variables that would point uv at the environment of this checkout.
_CHECKOUT_ENVIRONMENT = ("UV_PROJECT", "UV_PROJECT_ENVIRONMENT", "VIRTUAL_ENV")


@dataclass
class Block:
    classes: set[str]
    commands: list[str]  # without comments and blank lines
    lines: list[str]
    verified: bool  # not inside a ".not-verified" div
    section: str


def blocks() -> list[Block]:
    result: list[Block] = []
    lines = PAGE.read_text().splitlines()
    divs: list[bool] = []  # per open div: is it a not-verified div
    section = ""
    index = 0
    while index < len(lines):
        line = lines[index]
        index += 1
        if line.startswith("## ") or line.startswith("### "):
            section = line.lstrip("#").strip()
        elif line.startswith(":::"):
            if line.strip() == ":::":
                divs.pop()
            else:
                divs.append(".not-verified" in line)
        elif line.startswith("```"):
            match = _FENCE.match(line) or _BARE_FENCE.match(line)
            body: list[str] = []
            while not lines[index].startswith("```"):
                body.append(lines[index])
                index += 1
            index += 1
            if match is None:
                continue
            attributes = match.group(2) if match.groups() else ""
            result.append(
                Block(
                    classes=set(re.findall(r"\.([\w-]+)", attributes)),
                    commands=[
                        text
                        for text in (entry.strip() for entry in body)
                        if text and not text.startswith("#")
                    ],
                    lines=body,
                    verified=not any(divs),
                    section=section,
                )
            )
    return result


def _one(*classes: str) -> Block:
    found = [b for b in blocks() if set(classes) <= b.classes]
    assert len(found) == 1, f"expected one block with {classes}"
    return found[0]


def dev_packages() -> set[str]:
    """The names of the `dev` group of the project, normalised."""
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())
    return {
        re.split(r"[<>=!~\[ ;]", requirement, maxsplit=1)[0].lower().replace("_", "-")
        for requirement in pyproject["dependency-groups"]["dev"]
    }


def test_the_python_only_setup_is_git_and_uv_with_the_project_packages_alone():
    setup = _one("required-setup", "python-only")
    clone, cd, *rest = setup.commands

    assert clone.startswith("git clone https://github.com/")
    assert cd.startswith("cd ")
    assert rest == ["uv sync --locked --no-dev"]
    assert setup.section == "Run an experiment"


def test_every_command_is_the_setup_an_experiment_the_proof_check_or_marked():
    lean = CHECK_LEAN.read_text()
    unmarked = []
    for block in blocks():
        if {"required-setup"} & block.classes:
            continue
        if "experiment" in block.classes:
            assert block.verified
            for command in block.commands:
                assert command.startswith("uv run --locked --no-dev python -m ")
        elif "lean" in block.classes:
            # The proof check of a reader is what ./scripts/check-lean.sh runs.
            assert block.section.startswith("Optional: ")
            for command in block.commands:
                assert command.removeprefix("cd ") in lean, command
        elif block.verified:
            unmarked.append(block.commands)
    assert not unmarked, f"commands outside the verified kinds: {unmarked}"


def test_no_instruction_renders_previews_or_verifies_the_website():
    for block in blocks():
        for command in block.commands:
            assert not any(tool in command for tool in SITE_TOOLS), command


def test_the_python_only_path_names_no_lean_browser_jq_workflow_or_key():
    for block in blocks():
        if {"required-setup", "experiment"} & block.classes:
            text = "\n".join(block.lines)
            for word in ("elan", "lake", "Mathlib", "jq", "OPENAI", "gh "):
                assert word not in text, (word, block.commands)


def test_optional_commands_name_what_they_need():
    live = [b for b in blocks() if b.section == "Optional: a live run"]
    agent = [b for b in blocks() if b.section == "Optional: drive a coding agent"]
    lean = [b for b in blocks() if b.section == "Optional: check a proof"]
    assert len(live) == 1 and len(agent) == 1 and lean
    for block in (*live, *agent):
        assert not block.verified
        assert any(line.startswith("# needs: ") for line in block.lines)
    # The key goes to the environment, never into a file, and the live run
    # installs its own optional dependency.
    assert any(c.startswith('export OPENAI_API_KEY="..."') for c in live[0].commands)
    assert "uv sync --locked --no-dev --extra openai" in live[0].commands
    assert not any(line.startswith("# needs: ") for b in lean for line in b.lines)


def test_the_page_does_not_hold_a_key():
    text = PAGE.read_text()
    assert not re.search(r"sk-[A-Za-z0-9]{8,}", text)


def _run(command: str, cwd: Path, env: dict[str, str]) -> None:
    result = subprocess.run(
        ["bash", "-eo", "pipefail", "-c", command],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"{command}\n{result.stdout}{result.stderr}"


@pytest.fixture(scope="module")
def learner(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict[str, str]]:
    """The page's Python-only commands, performed in a fresh clone of the
    working tree: the files Git tracks or would add, and the page's setup
    after its 'git clone' and 'cd'."""
    clone = tmp_path_factory.mktemp("reader") / "physics-by-construction"
    for file in lesson_checks.committed_files(REPO_ROOT):
        (clone / file).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / file, clone / file)
    env = {k: v for k, v in os.environ.items() if k not in _CHECKOUT_ENVIRONMENT}
    for command in _one("required-setup", "python-only").commands[2:]:
        _run(command, clone, env)
    return clone, env


def test_the_environment_of_the_setup_holds_nothing_of_the_dev_group(learner):
    clone, env = learner
    listed = subprocess.run(
        ["uv", "pip", "list", "--format", "json", "--python", ".venv"],
        cwd=clone,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    installed = {
        package["name"].lower().replace("_", "-")
        for package in json.loads(listed.stdout)
    }

    assert "numpy" in installed and "pbc" in installed
    # No site generator, notebook kernel, browser, accessibility scan, or
    # quality tool, and nothing that only they bring.
    assert not installed & dev_packages()
    for prefix in ("quarto", "ipy", "jupyter", "nb", "playwright", "axe", "pytest"):
        assert not any(name.startswith(prefix) for name in installed), prefix


@pytest.mark.parametrize("kind", ["simulation", "measured-data", "agent-replay"])
def test_an_experiment_of_each_kind_runs_in_that_environment(learner, kind: str):
    clone, env = learner
    (command,) = _one("experiment", kind).commands
    shutil.rmtree(clone / "results", ignore_errors=True)

    _run(command, clone, {**env, "UV_NO_SYNC": "1"})

    found = json.loads((clone / "results" / "results.json").read_text())
    assert found["figures"]
    for figure in found["figures"]:
        assert (clone / "results" / figure).read_bytes()[:4] == b"\x89PNG"
