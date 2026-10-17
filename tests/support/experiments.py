"""Helpers for the unit tests of the lessons' experiments (``pbc.experiment``)."""

import importlib
import json
import re
from html import unescape
from pathlib import Path

from pbc.experiment import RESULTS_FILE, main
from support.paths import REPO_ROOT

_FIGURE_LABEL = re.compile(r"^#\|\s*label:\s*(fig-[a-z0-9-]+)\s*$", re.MULTILINE)
_NAMED = re.compile(
    r"""result(?:\.table|\.show|\.widget|\.output|\.display)?[\[(]["']([a-z0-9-]+)["'][\])]"""
)


def run_entry_point(module: str, directory: Path) -> dict:
    """Run the experiment ``module`` as the learner's command does, into
    ``directory``, and return its results file."""
    main(importlib.import_module(module).run, [str(directory)])
    return json.loads((directory / RESULTS_FILE).read_text(encoding="utf-8"))


def page_of(lesson: str) -> str:
    """The source of the lesson page ``lesson``, such as
    ``mechanics/01-kinematics-as-a-program``."""
    return (REPO_ROOT / "site" / "lessons" / lesson / "index.qmd").read_text(
        encoding="utf-8"
    )


def figure_labels(page: str) -> set[str]:
    """The labels of the figure cells of a page."""
    return set(_FIGURE_LABEL.findall(page))


def names_the_page_reads(page: str) -> set[str]:
    """The numbers, tables, and figures a page reads from its ``result``."""
    return set(_NAMED.findall(page))


def assert_the_page_and_the_results_agree(lesson: str, directory: Path, found: dict):
    """The command wrote one file per figure of the page, and its results hold
    exactly the numbers, tables, and figures the page reads."""
    page = page_of(lesson)
    labels = figure_labels(page)
    assert labels, f"{lesson} labels no figure"
    assert {f"{label}.png" for label in labels} == set(found["figures"])
    for label in labels:
        assert (directory / f"{label}.png").read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    recorded = (
        set(found["numbers"])
        | set(found["tables"])
        | {name.removesuffix(".png") for name in found["figures"]}
        | {name.removesuffix(".json") for name in found["widgets"]}
        | set(found["outputs"])
        | set(found["displays"])
    )
    assert names_the_page_reads(page) == recorded


# --- The experiment against the built page (ADR 016 decision 4) ---------------

_TAG = re.compile(r"<[^>]+>")
_TABLE = re.compile(r"<table\b.*?</table>", re.DOTALL)
_CAPTION = re.compile(r"<caption>(.*?)</caption>", re.DOTALL)
_CELL = re.compile(r"<t([hd])\b[^>]*>(.*?)</t[hd]>", re.DOTALL)
_ROW = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.DOTALL)
_OUTPUT = re.compile(
    r'<div class="cell-output cell-output-stdout">\s*'
    r"<pre[^>]*><code>(.*?)</code></pre>",
    re.DOTALL,
)
# A number of a display, without the Markdown and the quoting around it.
_WORD = re.compile(r"[^\s*`_|()\[\]{},;:\"'<>]*\d[^\s*`_|()\[\]{},;:\"'<>]*")


def _text(html: str) -> str:
    """The text of an HTML fragment, with white space collapsed."""
    return " ".join(unescape(_TAG.sub(" ", html)).split())


def _tables(html: str) -> dict[str, tuple[list[str], list[list[str]]]]:
    """Every table of a page with a caption: its header and its rows."""
    found = {}
    for table in _TABLE.findall(html):
        caption = _CAPTION.search(table)
        if caption is None:
            continue
        header, rows = [], []
        for row in _ROW.findall(table):
            cells = _CELL.findall(row)
            if cells and all(kind == "h" for kind, _ in cells):
                header = [_text(cell) for _, cell in cells]
            elif cells:
                rows.append([_text(cell) for _, cell in cells])
        found[_text(caption.group(1))] = (header, rows)
    return found


def _widget(html: str, page_dir: Path, name: str) -> object | None:
    """The data of the widget ``name`` as the page carries it: in the page,
    or as its on-demand file."""
    embedded = re.search(
        rf'<script type="application/json" id="{re.escape(name)}-data">(.*?)</script>',
        html,
        re.DOTALL,
    )
    if embedded is not None:
        return json.loads(embedded.group(1))
    asset = page_dir / "index_files" / "figure-html" / f"{name}.json"
    return json.loads(asset.read_text(encoding="utf-8")) if asset.is_file() else None


def compare_with_page(results: Path, page: Path) -> list[str]:
    """What the experiment wrote into ``results`` that the built ``page`` does
    not show: a figure file that is not the page's byte for byte, a number,
    a table cell, a printed line, a display, or the data of a widget that
    differs at the precision the page shows. Empty when they agree."""
    problems = []
    if not (results / RESULTS_FILE).is_file():
        return [f"the experiment wrote no {RESULTS_FILE}"]
    found = json.loads((results / RESULTS_FILE).read_text(encoding="utf-8"))
    html = page.read_text(encoding="utf-8")
    main = html[html.find("<main") : html.find("</main>")]
    text = _text(main)
    for name in found["figures"]:
        shown = (
            page.parent
            / "index_files"
            / "figure-html"
            / name.replace(".png", "-output-1.png")
        )
        written = results / name
        if not written.is_file():
            problems.append(f"the experiment wrote no {name}")
        elif not shown.is_file():
            problems.append(f"the page shows no figure {name}")
        elif written.read_bytes() != shown.read_bytes():
            problems.append(f"the figure {name} is not the page's, byte for byte")
    for name, value in found["numbers"].items():
        # A whole token of the page: 9.8 is not shown by 9.80665.
        shown = re.escape(" ".join(value.split()))
        if not re.search(rf"(?<![\w.]){shown}(?!\w|\.\d)", text):
            problems.append(f"the number {name} = {value!r} is not on the page")
    tables = _tables(main)
    for name, table in found["tables"].items():
        caption = " ".join(table["caption"].split())
        if caption not in tables:
            problems.append(f"the page shows no table {name} ({caption!r})")
            continue
        header, rows = tables[caption]
        if header != table["columns"]:
            problems.append(f"the header of the table {name} differs: {header}")
        if rows != table["rows"]:
            problems.append(f"the cells of the table {name} differ from the page's")
    printed = [unescape(block) for block in _OUTPUT.findall(main)]
    for name, value in found["outputs"].items():
        if value.rstrip("\n") not in (block.rstrip("\n") for block in printed):
            problems.append(f"the page does not print the output {name}")
    words = set(_WORD.findall(text))
    for name, value in found["displays"].items():
        missing = [word for word in _WORD.findall(value) if word not in words]
        if missing:
            problems.append(f"the display {name} shows what the page lacks: {missing}")
    for name in found["widgets"]:
        stem = name.removesuffix(".json")
        data = json.loads((results / name).read_text(encoding="utf-8"))
        if _widget(html, page.parent, stem) != data:
            problems.append(f"the data of the widget {stem} is not the page's")
    return problems


def split_footer_commands(commands: list[str]) -> tuple[str | None, list[str]]:
    """The experiment command of a page's footer and the commands after it
    that check proofs. A proof-only Lean lesson computes nothing: its footer
    has no ``uv sync``, so there is no experiment command (None) and all the
    commands after the clone are Lean's."""
    if "uv sync --locked --no-dev" not in commands:
        start = next(
            (i for i, c in enumerate(commands) if c == "cd lean"), len(commands)
        )
        return None, [c for c in commands[start:] if c != "cd lean"]
    setup = commands.index("uv sync --locked --no-dev")
    lean = [c for c in commands[setup + 2 :] if c != "cd lean"]
    return commands[setup + 1], lean
