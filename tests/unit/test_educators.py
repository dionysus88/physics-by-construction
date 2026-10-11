"""Instructor packs match their lessons and the citation file."""

import re
from pathlib import Path

import pytest
import yaml
from support.paths import REPO_ROOT, SITE_SOURCE

from pbc.authoring import LearningPath
from pbc.authoring.educators import (
    BLOCK,
    PACKS_DIRECTORY,
    citation_text,
    forms_list,
    generated_block,
    pack_lessons,
    pack_path,
    packs_list,
    sync_pack,
)

PATH = LearningPath.read(SITE_SOURCE)
PACKS = pack_lessons(PATH)


def section(text: str, heading: str) -> list[str]:
    """The bullet items under a ``### heading`` of the generated block."""
    body = re.search(rf"^### {heading}\n(.*?)(?=^### |\Z)", text, re.M | re.S)
    assert body, heading
    return [line[2:] for line in body.group(1).splitlines() if line.startswith("- ")]


def test_there_is_a_pack_for_the_default_lesson_m5():
    assert [lesson.id for lesson in PACKS] == ["numerical-integrators"]


def test_every_file_in_the_packs_directory_belongs_to_a_lesson():
    files = {p.stem for p in (REPO_ROOT / PACKS_DIRECTORY).glob("*.md")}
    assert files <= {lesson.id for lesson in PATH.lessons}


@pytest.mark.parametrize("lesson", PACKS, ids=lambda lesson: lesson.id)
def test_the_pack_objectives_and_prerequisites_equal_the_lesson_metadata(lesson):
    text = pack_path(lesson).read_text(encoding="utf-8")
    assert section(text, "Learning objectives") == list(lesson.outcomes)
    expected = [f"Lesson: {PATH.lesson(i).title}" for i in lesson.prerequisites] + [
        f"Outside the site: {outside}" for outside in lesson.outside
    ]
    assert section(text, "Prerequisites") == expected
    assert f"Difficulty {lesson.difficulty}:" in text


@pytest.mark.parametrize("lesson", PACKS, ids=lambda lesson: lesson.id)
def test_the_generated_block_is_current(lesson):
    text = pack_path(lesson).read_text(encoding="utf-8")
    assert sync_pack(text, lesson, PATH) == text, (
        "run: uv run python -m pbc.authoring.educators"
    )


def test_a_changed_outcome_makes_a_pack_stale():
    lesson = PACKS[0]
    text = pack_path(lesson).read_text(encoding="utf-8")
    changed = lesson.__class__(**{**lesson.__dict__, "outcomes": ("Something else",)})
    assert sync_pack(text, changed, PATH) != text


@pytest.mark.parametrize("lesson", PACKS, ids=lambda lesson: lesson.id)
def test_the_pack_citation_equals_citation_cff(lesson):
    text = pack_path(lesson).read_text(encoding="utf-8")
    block = BLOCK.search(text)
    assert block
    quoted = [line[2:] for line in block.group(0).splitlines() if line.startswith("> ")]
    cff = yaml.safe_load((REPO_ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    assert quoted == [citation_text()]
    assert cff["title"] in quoted[0] and cff["url"] in quoted[0]
    assert cff["authors"][0]["family-names"] in quoted[0]


def test_the_citation_text_follows_a_changed_citation_file(tmp_path: Path):
    changed = tmp_path / "CITATION.cff"
    changed.write_text(
        'title: "Other"\nurl: "https://example.org/"\nauthors:\n'
        "  - family-names: Doe\n    given-names: Jane\n",
        encoding="utf-8",
    )
    assert citation_text(changed) == 'Doe, J. "Other". https://example.org/'
    assert citation_text(changed) != citation_text()


def test_the_educators_page_lists_every_pack_and_links_existing_forms():
    listing = packs_list(PATH)
    for lesson in PACKS:
        assert f"[{lesson.title}]" in listing and f"{lesson.id}.md" in listing
    templates = {
        p.stem for p in (REPO_ROOT / ".github" / "ISSUE_TEMPLATE").glob("*.yml")
    }
    for name in re.findall(r"template=([\w-]+)\.yml", forms_list()):
        assert name in templates


def test_a_pack_states_the_parts_an_educator_needs():
    text = pack_path(PACKS[0]).read_text(encoding="utf-8")
    for heading in (
        "Approximate time",
        "Lecturer guide",
        "Assignment",
        "Rubric",
        "Reference solution",
        "Accessibility notes",
        "Pathway without AI",
        "Reuse and citation",
        "Suggest an improvement",
    ):
        assert f"\n## {heading}\n" in text, heading
    assert generated_block(PACKS[0], PATH) in text
