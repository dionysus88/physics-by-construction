"""The site build and the determinism check fail on pages that violate them.

Each case is a minimal Quarto project in a temporary directory.
"""

from pathlib import Path

import pytest
from support.checks import output, run_check

from pbc.authoring import pages
from pbc.authoring import selection as selecting
from pbc.authoring.repository import build_commit

_CONFIG = """\
project:
  type: website
format:
  html:
    html-math-method: mathml
"""


@pytest.fixture
def site(tmp_path: Path) -> Path:
    source = tmp_path / "site"
    source.mkdir()
    (source / "_quarto.yml").write_text(_CONFIG)
    return source


def test_build_fails_on_an_equation_that_is_not_mathml(site: Path, tmp_path: Path):
    (site / "index.qmd").write_text(
        "---\ntitle: Equation\n---\n\nThe value $\\notacommand{x}$ is unknown.\n"
    )

    result = run_check("site-build", site, tmp_path / "out")

    assert result.returncode != 0
    assert "could not be converted to MathML" in output(result)


def test_build_fails_on_a_cell_that_raises(site: Path, tmp_path: Path):
    (site / "index.qmd").write_text(
        "---\ntitle: Cell\n---\n\n"
        '```{python}\nraise RuntimeError("the lesson code is broken")\n```\n'
    )

    result = run_check("site-build", site, tmp_path / "out")

    assert result.returncode != 0
    assert "the lesson code is broken" in output(result)


def test_determinism_fails_on_a_page_that_changes_between_builds(
    site: Path, tmp_path: Path
):
    (site / "index.qmd").write_text(
        "---\ntitle: Random\n---\n\n"
        "```{python}\nimport uuid\n\nprint(uuid.uuid4())\n```\n"
    )
    first = tmp_path / "first"
    build = run_check("site-build", site, first)
    assert build.returncode == 0, output(build)

    result = run_check("determinism", site, first)

    assert result.returncode != 0
    assert "index.html" in output(result) and "differ" in output(result)


def test_a_changed_style_sheet_alone_checks_the_pages_that_are_not_lessons(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    # The style sheet is linked without a checksum, so no page changes with
    # it (F61 follow-up M1): the record of the files that are not pages selects.
    site = tmp_path / "site"
    (site / "assets").mkdir(parents=True)
    (site / "lessons" / "s" / "01-one").mkdir(parents=True)
    (site / "_quarto.yml").write_text(_CONFIG + "    css: assets/site.css\n")
    (site / "assets" / "site.css").write_text("body { color: black; }\n")
    (site / "index.qmd").write_text("---\ntitle: Home\n---\n\nHome.\n")
    (site / "about.qmd").write_text("---\ntitle: About\n---\n\nAbout.\n")
    (site / "lessons" / "s" / "01-one" / "index.qmd").write_text(
        "---\ntitle: One\n---\n\nA lesson.\n"
    )
    build = run_check("site-build", site, tmp_path / "base-site")
    assert build.returncode == 0, output(build)
    base = tmp_path / "base"
    base.mkdir()
    (base / pages.PAGES).write_bytes((site / pages.BUILT_PAGES).read_bytes())
    (site / "assets" / "site.css").write_text("body { color: #222; }\n")
    build = run_check("site-build", site, tmp_path / "out")
    assert build.returncode == 0, output(build)
    selection = {
        "format": selecting.SELECTION_FORMAT,
        "mode": "selective",
        "base_directory": str(base),
        "execute": [],
        "reuse": [],
    }
    monkeypatch.setattr(selecting, "read", lambda root: selection)

    checked = pages.checked(tmp_path / "out")

    record = pages.read(base / pages.PAGES)
    assert pages.differing(tmp_path / "out", record, build_commit().sha) == []
    assert checked["assets"] == ["assets/site.css"]
    assert {"index.html", "about.html"} <= set(pages.selected(tmp_path / "out"))
    assert checked["pages"]["index.html"] == pages.ASSET
    assert checked["pages"]["about.html"] == pages.ASSET
