"""The experiment check reports an experiment whose output is not the page's
(ADR 016 decision 4, F117).

The check of the built site runs every selected lesson's experiment with the
reader's commands and compares what it wrote with the built page
(``support.experiments.compare_with_page``). Here a page is built by hand from
what the experiment of the lesson template writes, so the two agree; each
case then changes one thing on one side, and the comparison must say so. A
lesson without an experiment fails the lesson source checks, which
test_lesson_checks.py shows.
"""

import json
import shutil
from html import escape
from pathlib import Path

import pytest
from support.experiments import compare_with_page, run_entry_point

MODULE = "pbc.mechanics.experiments.lesson_template"


def _page(results: Path, page: Path) -> None:
    """A built page that shows everything the experiment recorded."""
    found = json.loads((results / "results.json").read_text())
    figures = page.parent / "index_files" / "figure-html"
    figures.mkdir(parents=True)
    for name in found["figures"]:
        shutil.copy(results / name, figures / name.replace(".png", "-output-1.png"))
    numbers = "".join(f"<p>It is {escape(v)} m.</p>" for v in found["numbers"].values())
    printed = "".join(
        '<div class="cell-output cell-output-stdout">'
        f"<pre><code>{escape(text)}</code></pre></div>"
        for text in found["outputs"].values()
    )
    page.write_text(f"<html><body><main>{numbers}{printed}</main></body></html>")


@pytest.fixture
def lesson(tmp_path: Path) -> tuple[Path, Path]:
    results = tmp_path / "results"
    run_entry_point(MODULE, results)
    page = tmp_path / "site" / "index.html"
    page.parent.mkdir()
    _page(results, page)
    return results, page


def _change(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    assert old in text
    path.write_text(text.replace(old, new))


def test_an_experiment_that_agrees_with_its_page_passes(lesson):
    assert compare_with_page(*lesson) == []


def test_a_changed_number_fails(lesson):
    results, page = lesson
    _change(results / "results.json", '"2.000"', '"2.001"')

    assert compare_with_page(results, page) == [
        "the number exact-position = '2.001' is not on the page"
    ]


def test_a_changed_figure_fails(lesson):
    results, page = lesson
    figure = results / "fig-replace-with-a-name.png"
    figure.write_bytes(figure.read_bytes() + b"\0")

    problems = compare_with_page(results, page)

    assert problems == [
        "the figure fig-replace-with-a-name.png is not the page's, byte for byte"
    ]


def test_changed_printed_output_fails(lesson):
    results, page = lesson
    _change(page, "largest error: 0.", "largest error: 9.")

    assert compare_with_page(results, page) == [
        "the page does not print the output largest-error"
    ]


def test_a_changed_table_cell_fails(lesson):
    results, page = lesson
    found = json.loads((results / "results.json").read_text())
    found["tables"]["errors"] = {
        "caption": "Errors.",
        "columns": ["t (s)", "error (m)"],
        "rows": [["0.5", "0.125"]],
    }
    (results / "results.json").write_text(json.dumps(found))
    table = (
        "<table><caption>Errors.</caption><thead><tr><th>t (s)</th>"
        "<th>error (m)</th></tr></thead><tbody><tr><td>0.5</td><td>0.126</td>"
        "</tr></tbody></table>"
    )
    _change(page, "</main>", f"{table}</main>")

    assert compare_with_page(results, page) == [
        "the cells of the table errors differ from the page's"
    ]


def test_an_experiment_that_wrote_nothing_fails(lesson, tmp_path: Path):
    _, page = lesson

    assert compare_with_page(tmp_path / "nothing", page) == [
        "the experiment wrote no results.json"
    ]


def test_a_proof_only_footer_has_no_experiment_to_run():
    from support.experiments import split_footer_commands

    proof = [
        "git clone https://example.org/r.git",
        "cd r",
        "git checkout abc",
        "cd lean",
        "lake exe cache get",
        "lake build PBC.Lesson",
    ]
    assert split_footer_commands(proof) == (
        None,
        ["lake exe cache get", "lake build PBC.Lesson"],
    )
    both = [
        *proof[:3],
        "uv sync --locked --no-dev",
        "uv run --locked --no-dev python -m m results",
        *proof[3:],
    ]
    assert split_footer_commands(both) == (
        "uv run --locked --no-dev python -m m results",
        ["lake exe cache get", "lake build PBC.Lesson"],
    )
