"""The search index check and the script that prepares the index
(site/search-index.py), on small sites built to violate one rule."""

import importlib.util
import json
from pathlib import Path

from support import site_checks

SCRIPT = Path(__file__).resolve().parents[2] / "site" / "search-index.py"


def _script():
    spec = importlib.util.spec_from_file_location("search_index_script", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write(site: Path, entries: list[dict]) -> None:
    (site / "search.json").write_text(json.dumps(entries), encoding="utf-8")


def test_an_index_above_the_budget_is_a_violation(tmp_path: Path):
    _write(tmp_path, [{"href": "a/index.html", "text": "x"}])
    assert not site_checks.check_search_index(tmp_path)
    _write(
        tmp_path,
        [{"href": "a/index.html", "text": "x" * site_checks.SEARCH_INDEX_BUDGET}],
    )
    violations = site_checks.check_search_index(tmp_path)
    assert [v.rule for v in violations] == ["search-index"]
    assert "budget" in violations[0].detail


def test_the_budget_is_three_and_a_half_megabytes():
    assert site_checks.SEARCH_INDEX_BUDGET == 3_500_000


def test_an_entry_of_the_learning_path_page_is_a_violation(tmp_path: Path):
    _write(tmp_path, [{"href": "path/index.html#step-1", "text": "summary"}])
    violations = site_checks.check_search_index(tmp_path)
    assert [v.page for v in violations] == ["path/index.html#step-1"]


def test_the_script_drops_the_learning_path_and_keeps_the_lessons(
    tmp_path: Path, monkeypatch
):
    for page in ("path", "lessons/a"):
        (tmp_path / page).mkdir(parents=True)
        (tmp_path / page / "index.html").write_text("<p>eccentricity</p>")
    _write(
        tmp_path,
        [
            {"href": "path/index.html", "text": "eccentricity"},
            {"href": "path/index.html#a", "text": "eccentricity"},
            {"href": "lessons/a/index.html#orbit", "text": "the eccentricity"},
        ],
    )
    monkeypatch.setenv("QUARTO_PROJECT_OUTPUT_DIR", str(tmp_path))
    _script().main()
    entries = json.loads((tmp_path / "search.json").read_text(encoding="utf-8"))
    assert [e["href"] for e in entries] == ["lessons/a/index.html#orbit"]
    assert "eccentricity" in entries[0]["text"]
    assert not site_checks.check_search_index(tmp_path)
