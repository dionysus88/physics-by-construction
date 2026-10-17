"""No maintained guide tells anyone to rebuild or preview the website (ADR 016
decision 1, requirements decision 33, F117).

The instructions were removed, not moved: the instructional command blocks
and the imperative setup and footer sections of the guides, the home page,
the instructor packs, and the generated footers name no render or preview
command and no sentence tells the reader to render or preview the site, and
none names the superseded footer heading. A technical reference that names
in prose what `./scripts/verify.sh` or CI runs, such as the verification
section of `docs/development.md`, is not an instruction and is not checked
here; the full `./scripts/verify.sh` run that ADR 017 decision 7 asks of an
agent or developer for some changes is a verification tier, not a way to read
the site.
"""

import importlib
import re

import pytest
from support import lesson_checks
from support.paths import REPO_ROOT

from pbc.authoring.repository import BuildCommit
from pbc.authoring.reproduce import Reproduction, declaration

# The commands that render or preview the website.
RENDER_COMMANDS = ("quarto preview", "quarto render", "./scripts/build-site.sh")
# A sentence that tells the reader to render, rebuild, or preview the site or
# a page of it.
_IMPERATIVE = re.compile(
    r"(?:^|[.!?:;,]\s*|\b(?:then|and|or|to|please)\s+|\n\s*(?:[-*]|\d+\.)?\s*)"
    r"(?:render|re-render|rebuild|preview|build)\s+"
    r"(?:(?:the|this|that|a|every|one|your)\s+)?(?:\w+\s+)?"
    r"(?:site|website|page|pages|everything)\b",
    re.IGNORECASE,
)
SUPERSEDED_HEADING = "Reproduce this"

# A fenced block, also one indented in a list.
_FENCE = re.compile(r"^([ \t]*)(`{3,})[^\n]*\n(.*?)^\1\2\s*$", re.MULTILINE | re.DOTALL)
_HEADING = re.compile(r"^(#{2,3}) (.+)$", re.MULTILINE)


def _section(text: str, title: str) -> str:
    """The text under the heading ``title``, up to the next heading of the
    same or a higher level."""
    for match in _HEADING.finditer(text):
        if match.group(2).strip() == title:
            level = len(match.group(1))
            rest = text[match.end() :]
            end = re.search(rf"^#{{2,{level}}} ", rest, re.MULTILINE)
            return rest[: end.start()] if end else rest
    raise AssertionError(f"no section {title!r}")


def _blocks(text: str) -> list[str]:
    return [match.group(3) for match in _FENCE.finditer(text)]


def _read(name: str) -> str:
    return (REPO_ROOT / name).read_text(encoding="utf-8")


def _packs() -> list[str]:
    return sorted(
        path.relative_to(REPO_ROOT).as_posix()
        for path in (REPO_ROOT / "docs" / "instructor-packs").glob("*.md")
    )


def _footers() -> dict[str, str]:
    """The last section of every lesson, as the build writes it."""
    footers = {}
    for page in lesson_checks.lesson_pages(REPO_ROOT):
        experiment, kind, lean_modules = declaration(page)
        live = ""
        if kind == "replay":
            live = importlib.import_module(experiment).LIVE
        footers[page.relative_to(REPO_ROOT).as_posix()] = Reproduction(
            page=page.relative_to(REPO_ROOT).as_posix(),
            code=(),
            tests=(),
            commit=BuildCommit("0" * 40, False),
            repository="https://github.com/taspinar/physics-by-construction",
            experiment=experiment,
            kind=kind,
            lean_modules=lean_modules,
            live=live,
        ).markdown()
    return footers


# The instructional text of each maintained document: a whole document when
# all of it addresses a reader, the named section when only that part does.
INSTRUCTIONS = {
    "README.md": lambda text: _section(text, "Run an experiment"),
    "CONTRIBUTING.md": lambda text: text,
    # The place of the removed preview walkthrough, and the one-time setup.
    "docs/development.md": lambda text: (
        _section(text, "One-time setup")
        + _section(text, "Verification")
        .split("### The checks of the built site")[0]
        .split("Run one check on its own")[1]
    ),
    "docs/authoring.md": lambda text: (
        _section(text, "Create a lesson")
        + _section(text, "The experiment of a lesson")
        + _section(text, "The last section")
    ),
    "docs/lesson-template.qmd": lambda text: text,
    "docs/project-map.md": lambda text: text,
    "docs/editorial-voice.md": lambda text: text,
    "site/index.qmd": lambda text: text,
    "site/contribute.qmd": lambda text: text,
    "site/reproduce.qmd": lambda text: text,
}


def _documents() -> list[tuple[str, str]]:
    documents = [(name, pick(_read(name))) for name, pick in INSTRUCTIONS.items()]
    documents += [
        (name, _section(_read(name), "Pathway without AI")) for name in _packs()
    ]
    documents += list(_footers().items())
    return documents


DOCUMENTS = _documents()


def test_the_named_documents_are_all_checked():
    names = {name for name, _ in DOCUMENTS}
    assert {"README.md", "site/reproduce.qmd", "site/index.qmd"} <= names
    assert _packs() and set(_packs()) <= names
    assert len(_footers()) == len(lesson_checks.lesson_pages(REPO_ROOT))


@pytest.mark.parametrize(("name", "text"), DOCUMENTS, ids=[n for n, _ in DOCUMENTS])
def test_no_command_block_renders_or_previews_the_site(name: str, text: str):
    for block in _blocks(text):
        for command in RENDER_COMMANDS:
            assert command not in block, f"{name}: {command}"


@pytest.mark.parametrize(("name", "text"), DOCUMENTS, ids=[n for n, _ in DOCUMENTS])
def test_no_sentence_tells_the_reader_to_render_or_preview_the_site(
    name: str, text: str
):
    prose = _FENCE.sub("", text)
    found = [match.group(0).strip() for match in _IMPERATIVE.finditer(prose)]
    assert not found, f"{name}: {found}"
    for command in RENDER_COMMANDS:
        assert command not in prose, f"{name}: {command}"


@pytest.mark.parametrize(("name", "text"), DOCUMENTS, ids=[n for n, _ in DOCUMENTS])
def test_no_document_names_the_superseded_footer_heading(name: str, text: str):
    assert SUPERSEDED_HEADING not in text, name


@pytest.mark.parametrize(
    "sentence",
    [
        "Then preview the site with live reload.",
        "To rebuild everything on your own machine, render the site.",
        "1. Render the page alone to read it.",
    ],
)
def test_an_imperative_to_render_or_preview_is_recognised(sentence: str):
    assert _IMPERATIVE.search(sentence)


@pytest.mark.parametrize(
    "sentence",
    [
        "CI builds and validates the site on every pull request.",
        "The full run builds the site and checks the built pages.",
    ],
)
def test_a_statement_of_what_ci_runs_is_not_an_instruction(sentence: str):
    assert not _IMPERATIVE.search(sentence)
