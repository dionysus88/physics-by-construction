"""The experiment of the lesson template (docs/lesson-template.qmd)."""

import json
from pathlib import Path

from support.experiments import figure_labels, names_the_page_reads, run_entry_point
from support.paths import REPO_ROOT

MODULE = "pbc.mechanics.experiments.lesson_template"
TEMPLATE = REPO_ROOT / "docs" / "lesson-template.qmd"


def test_the_command_writes_what_the_template_shows(tmp_path: Path):
    found = run_entry_point(MODULE, tmp_path)
    page = TEMPLATE.read_text(encoding="utf-8")

    assert [f"{label}.png" for label in figure_labels(page)] == found["figures"]
    assert names_the_page_reads(page) == (
        set(found["numbers"]) | set(found["outputs"]) | figure_labels(page)
    )
    results = json.loads((tmp_path / "results.json").read_text())
    # The braking cart stops after two seconds, two metres on: Euler's
    # position lags the exact one, which the exercise measures.
    assert results["numbers"]["exact-position"] == "2.000"
    assert results["outputs"]["largest-error"].startswith("largest error: 0.")
