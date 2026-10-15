"""The learning path is derived from lesson front matter, validated, and
rendered with links that work from the page it is shown on."""

import json
import re
import subprocess
from pathlib import Path

import pytest

from pbc.authoring import (
    COURSES,
    DIFFICULTIES,
    METHODS,
    STRANDS,
    LearningPath,
    learning_path,
)
from pbc.authoring.glossary import Entry, Glossary
from pbc.authoring.path import (
    PATH_PAGE,
    Lesson,
    LessonHeader,
    PathOverview,
    lesson_header,
    problems,
    read_lessons,
)


def lesson(
    id: str,
    strand: str = "mechanics",
    order: int = 1,
    prerequisites: tuple[str, ...] = (),
    difficulty: int = 1,
    outside: tuple[str, ...] = (),
    methods: tuple[str, ...] = ("simulation",),
    related: tuple[str, ...] = (),
) -> Lesson:
    return Lesson(
        page=f"lessons/{strand}/{order:02d}-{id}/index.qmd",
        id=id,
        title=id.capitalize(),
        description="",
        strand=strand,
        order=order,
        difficulty=difficulty,
        prerequisites=prerequisites,
        outside=outside,
        course="mechanics",
        methods=methods,
        outcomes=(f"Do the first thing of {id}", f"Do the second thing of {id}"),
        related=related,
    )


def messages(lessons: list[Lesson]) -> list[str]:
    return [f"{problem.page}: {problem.message}" for problem in problems(lessons)]


# Lessons in two strands, given out of path order.
KINEMATICS = lesson("kinematics")
NEWTON = lesson("newton", order=2, prerequisites=("kinematics",), difficulty=2)
ENERGY = lesson("energy", order=3, prerequisites=("newton",), difficulty=2)
PROOF = lesson(
    "proof",
    strand="lean",
    order=1,
    prerequisites=("energy",),
    difficulty=3,
    methods=("lean",),
)
LESSONS = [PROOF, ENERGY, KINEMATICS, NEWTON]


def test_the_courses_and_methods_are_defined_once():
    assert [course.id for course in COURSES] == [
        "mechanics",
        "thermodynamics",
        "waves",
        "electromagnetism",
        "fluids",
        "quantum",
        "astrophysics",
        "materials",
    ]
    assert [method.id for method in METHODS] == [
        "simulation",
        "llm-agents",
        "abm",
        "lean",
        "measured-data",
        "coding-agents",
    ]
    assert all(item.title and item.description for item in (*COURSES, *METHODS))


def test_the_strands_and_the_scale_are_defined_once_in_order():
    assert [strand.id for strand in STRANDS] == [
        *(course.id for course in COURSES),
        "agents-llm",
        "agents-abm",
        "lean",
    ]
    assert [difficulty.level for difficulty in DIFFICULTIES] == [1, 2, 3]
    assert all(
        difficulty.title and difficulty.description for difficulty in DIFFICULTIES
    )


# --- Order ---------------------------------------------------------------------


@pytest.fixture
def site(tmp_path: Path) -> Path:
    """A website project with the lessons above as pages."""
    site = tmp_path / "site"
    (site / "_quarto.yml").parent.mkdir()
    (site / "_quarto.yml").write_text("project:\n  type: website\n")
    for item in LESSONS:
        write_lesson(site, item)
    return site


def write_lesson(site: Path, item: Lesson, **front_matter: str) -> Path:
    page = site / item.page
    page.parent.mkdir(parents=True, exist_ok=True)
    lessons = ", ".join(item.prerequisites)
    outside = ", ".join(f'"{text}"' for text in item.outside)
    outcomes = "".join(f'    - "{text}"\n' for text in item.outcomes)
    page.write_text(
        f'---\ntitle: "{item.title}"\n'
        + (f'description: "{item.description}"\n' if item.description else "")
        + f"lesson:\n  id: {item.id}\n  strand: {item.strand}\n"
        f"  order: {item.order}\n  difficulty: {item.difficulty}\n"
        f"  course: {item.course}\n  methods: [{', '.join(item.methods)}]\n"
        f"  outcomes:\n{outcomes}  related: [{', '.join(item.related)}]\n"
        f"  prerequisites:\n    lessons: [{lessons}]\n    outside: [{outside}]\n"
        + "".join(f"{key}: {value}\n" for key, value in front_matter.items())
        + "---\n\nIntroduction.\n"
    )
    return page


def test_path_is_read_from_the_front_matter_of_the_lesson_pages(site: Path):
    path = LearningPath.read(site)

    assert [item.id for item in path.lessons] == [
        "kinematics",
        "newton",
        "energy",
        "proof",
    ]
    assert path.lesson("newton") == NEWTON
    assert path.at_page(NEWTON.page) == NEWTON


def test_description_is_read_when_a_lesson_has_one(site: Path):
    item = lesson("drag", order=4, prerequisites=("energy",))
    write_lesson(site, item, description='"Motion with air drag."')

    assert LearningPath.read(site).lesson("drag").description == "Motion with air drag."


def test_previous_and_next_follow_the_path_across_strands(site: Path):
    path = LearningPath.read(site)

    assert path.previous(KINEMATICS) is None
    assert path.next(KINEMATICS) == NEWTON
    assert path.previous(PROOF) == ENERGY
    assert path.next(PROOF) is None


def test_only_strands_with_a_lesson_are_part_of_the_path(site: Path):
    path = LearningPath.read(site)

    assert [strand.id for strand in path.strands] == ["mechanics", "lean"]
    assert path.in_strand(path.strands[0]) == (KINEMATICS, NEWTON, ENERGY)


def test_a_site_without_lessons_has_an_empty_path(tmp_path: Path):
    (tmp_path / "_quarto.yml").write_text("project:\n  type: website\n")

    assert LearningPath.read(tmp_path).lessons == ()


@pytest.mark.parametrize(
    "text",
    [
        "No front matter.\n",
        "---\ntitle: Lesson\n---\n\nNo lesson mapping.\n",
        "---\ntitle: Lesson\nlesson:\n  id: x\n  strand: mechanics\n---\n",
        "---\ntitle: Lesson\nlesson: [not, a, mapping]\n---\n",
    ],
    ids=["no-front-matter", "no-lesson-key", "missing-fields", "not-a-mapping"],
)
def test_page_outside_the_lesson_format_is_rejected(site: Path, text: str):
    (site / "lessons/mechanics/04-broken").mkdir()
    (site / "lessons/mechanics/04-broken/index.qmd").write_text(text)

    with pytest.raises(ValueError, match="04-broken"):
        read_lessons(site)


@pytest.mark.parametrize(
    "item, expected",
    [
        (lesson("optics", strand="optics", order=1), "not a strand"),
        (lesson("hard", order=4, difficulty=4), "not on the scale"),
    ],
    ids=["unknown-strand", "difficulty-off-the-scale"],
)
def test_strand_and_difficulty_outside_the_definitions_are_rejected(
    site: Path, item: Lesson, expected: str
):
    write_lesson(site, item)

    with pytest.raises(ValueError, match=expected):
        read_lessons(site)


# --- Validation ----------------------------------------------------------------


def test_a_consistent_set_of_lessons_has_no_problem():
    assert problems(LESSONS) == []


def test_duplicate_id_is_reported_on_the_later_lesson():
    duplicate = lesson("kinematics", strand="lean", order=2, prerequisites=("proof",))

    assert messages([*LESSONS, duplicate]) == [
        f"{duplicate.page}: lesson id 'kinematics' is already used by {KINEMATICS.page}"
    ]


def test_unknown_prerequisite_is_reported():
    orphan = lesson("orbit", order=4, prerequisites=("gravity",))

    assert messages([*LESSONS, orphan]) == [
        f"{orphan.page}: prerequisite 'gravity' is not the id of any lesson"
    ]


def test_prerequisite_later_in_the_path_is_reported():
    # Nothing depends on the first lesson, so this is not a cycle.
    early = lesson("kinematics", prerequisites=("newton",))
    second = lesson("newton", order=2)

    assert messages([early, second, ENERGY, PROOF]) == [
        f"{early.page}: prerequisite 'newton' does not come earlier in its strand"
        " 'mechanics'"
    ]


def test_cycle_is_reported_once_with_its_members():
    first = lesson("kinematics", prerequisites=("energy",))
    found = messages([first, NEWTON, ENERGY, PROOF])

    assert (
        f"{first.page}: prerequisites form a cycle: kinematics -> energy -> newton"
        " -> kinematics"
    ) in found
    assert sum("cycle" in message for message in found) == 1


def test_cycle_reachable_from_a_lesson_outside_it_is_reported():
    first = lesson("kinematics", prerequisites=("newton",))
    newton = lesson("newton", order=2, prerequisites=("energy",))
    energy = lesson("energy", order=3, prerequisites=("newton",))
    found = messages([first, newton, energy, PROOF])

    assert any(
        message.endswith("prerequisites form a cycle: newton -> energy -> newton")
        for message in found
    )
    assert sum("cycle" in message for message in found) == 1


def test_cycles_sharing_lessons_are_all_reported():
    first = lesson("kinematics", prerequisites=("newton", "energy"))
    newton = lesson("newton", order=2, prerequisites=("kinematics",))
    energy = lesson("energy", order=3, prerequisites=("newton", "kinematics"))
    found = messages([first, newton, energy, PROOF])

    assert any("kinematics -> newton -> kinematics" in m for m in found)
    assert any("kinematics -> energy -> kinematics" in m for m in found)


def test_gap_in_the_order_of_a_strand_is_reported():
    late = lesson("orbit", order=5, prerequisites=("energy",))

    assert messages([*LESSONS, late]) == [
        f"{late.page}: 'lesson.order' is 5, but strand 'mechanics' has no lesson"
        " with order 4"
    ]


def test_strand_that_does_not_start_at_one_is_reported():
    assert messages([NEWTON]) == [
        f"{NEWTON.page}: 'lesson.order' is 2, but strand 'mechanics' has no lesson"
        " with order 1",
        f"{NEWTON.page}: prerequisite 'kinematics' is not the id of any lesson",
    ]


def test_duplicate_order_in_a_strand_is_reported():
    twin = Lesson(**{**NEWTON.__dict__, "id": "forces", "page": "lessons/x/index.qmd"})

    assert messages([*LESSONS, twin]) == [
        f"{twin.page}: 'lesson.order' 2 is already used by {NEWTON.page}"
    ]


def replaced(item: Lesson, **changes) -> Lesson:
    return Lesson(**{**item.__dict__, **changes})


@pytest.mark.parametrize(
    "changes, expected",
    [
        ({"course": "optics"}, "'lesson.course' 'optics' is not a course"),
        ({"methods": ()}, "'lesson.methods' names no method"),
        ({"methods": ("magic",)}, "'magic', which is not a method"),
        ({"methods": ("lean", "lean")}, "names a method twice"),
        ({"outcomes": ("Only one",)}, "has 1 outcomes; a lesson states 2 to 5"),
        ({"outcomes": tuple("abcdef")}, "has 6 outcomes; a lesson states 2 to 5"),
        ({"related": ("gravity",)}, "related lesson 'gravity' is not the id"),
        ({"related": ("newton",)}, "lists itself as related"),
        ({"related": ("energy", "energy")}, "names a lesson twice"),
    ],
    ids=[
        "unknown-course",
        "no-method",
        "unknown-method",
        "method-twice",
        "one-outcome",
        "six-outcomes",
        "related-does-not-exist",
        "related-is-itself",
        "related-twice",
    ],
)
def test_facets_outside_the_rules_are_reported(changes: dict, expected: str):
    bad = replaced(NEWTON, **changes)

    found = messages([KINEMATICS, bad, ENERGY, PROOF])

    assert len(found) == 1 or "twice" in expected
    assert any(expected in message and bad.page in message for message in found)


def test_related_lesson_that_is_a_prerequisite_is_reported():
    bad = replaced(NEWTON, related=("kinematics",))

    assert messages([KINEMATICS, bad, ENERGY, PROOF]) == [
        f"{bad.page}: related lesson 'kinematics' is already a prerequisite; a"
        " prerequisite is linked as one, not as related"
    ]


def test_related_lesson_from_the_prerequisite_side_is_accepted():
    # Related links run one way: the lesson that is built on links its
    # extension; the extension keeps the lesson as a prerequisite.
    linking = replaced(KINEMATICS, related=("proof",))

    assert problems([linking, NEWTON, ENERGY, PROOF]) == []


def test_reading_a_site_with_a_lesson_that_lacks_a_facet_fails(site: Path):
    page = write_lesson(site, lesson("drag", order=4, prerequisites=("energy",)))
    page.write_text(page.read_text().replace("  course: mechanics\n", ""))

    with pytest.raises(ValueError, match="drag"):
        read_lessons(site)


def test_reading_a_site_with_too_few_outcomes_fails_with_the_problem(site: Path):
    write_lesson(site, replaced(lesson("drag", order=4), outcomes=("One",)))

    with pytest.raises(ValueError, match="has 1 outcomes"):
        LearningPath.read(site)


def test_only_courses_and_methods_with_a_lesson_are_part_of_the_path(
    path: LearningPath,
):
    assert [course.id for course in path.courses] == ["mechanics"]
    assert [method.id for method in path.methods] == ["simulation", "lean"]
    assert path.using(path.methods[1]) == (PROOF,)
    assert path.in_course(path.courses[0]) == path.lessons


def test_reading_an_inconsistent_site_fails_with_every_problem(site: Path):
    write_lesson(site, lesson("orbit", order=5, prerequisites=("gravity",)))

    with pytest.raises(ValueError) as failure:
        LearningPath.read(site)

    assert "no lesson with order 4" in str(failure.value)
    assert "'gravity' is not the id" in str(failure.value)


# --- Rendering -----------------------------------------------------------------


@pytest.fixture
def path(site: Path) -> LearningPath:
    return LearningPath.read(site)


def test_header_shows_course_methods_outcomes_prerequisites_and_neighbours(
    path: LearningPath,
):
    shown = LessonHeader(path, NEWTON).markdown()

    assert (
        "Course\n:   [Classical mechanics](../../../path/index.html#course-mechanics),"
        " lesson 2 of 4" in shown
    )
    assert (
        "Methods\n:   [Simulation](../../../path/index.html#method-simulation)" in shown
    )
    assert "[Intermediate, level 2 of 3](../../../path/index.html#difficulty)" in shown
    assert (
        "What you'll learn\n:   \n    - Do the first thing of newton\n"
        "    - Do the second thing of newton\n" in shown
    )
    assert "Prerequisites\n:   [Kinematics](../01-kinematics/index.html)" in shown
    assert "Related\n:   none" in shown
    assert "Previous\n:   [Kinematics](../01-kinematics/index.html)" in shown
    assert "Next\n:   [Energy](../03-energy/index.html)" in shown


def test_header_renders_the_outcomes_as_a_list_in_its_row(path: LearningPath):
    blocks = pandoc_blocks(LessonHeader(path, NEWTON).markdown())

    # The header, then the raw block of the learner-state script.
    div, script = blocks
    assert script["t"] == "RawBlock" and "learner-state-data" in script["c"][1]
    definitions = dict(
        (inlines_text(term), items) for term, items in div["c"][1][0]["c"]
    )
    (outcomes,) = definitions["What you'll learn"]
    assert [block["t"] for block in outcomes] == ["BulletList"]
    assert len(outcomes[0]["c"]) == 2


def inlines_text(inlines: list[dict]) -> str:
    # Pandoc's smart typography turns the apostrophe into a curly one.
    text = "".join(i["c"] if i["t"] == "Str" else " " for i in inlines)
    return text.replace("\u2019", "'")


def test_header_links_related_lessons_and_methods():
    item = lesson("kinematics", methods=("simulation", "lean"), related=("proof",))
    path = LearningPath((item, PROOF))

    shown = LessonHeader(path, item).markdown()

    assert (
        "[Simulation](../../../path/index.html#method-simulation), [Formal proofs]"
        in shown
    )
    assert "Related\n:   [Proof](../../lean/01-proof/index.html)" in shown


def test_header_states_the_ends_of_the_path(path: LearningPath):
    first = LessonHeader(path, KINEMATICS).markdown()
    last = LessonHeader(path, PROOF).markdown()

    assert "Previous\n:   none; this is the first lesson" in first
    assert "Next\n:   [Newton](../02-newton/index.html)" in first
    assert "Previous\n:   [Energy](../../mechanics/03-energy/index.html)" in last
    assert "Next\n:   none yet; this is the last lesson" in last
    assert "lesson 4 of 4" in last


def test_header_names_the_outside_prerequisites(path: LearningPath):
    item = lesson("drag", order=4, prerequisites=("newton",), outside=("Calculus",))
    path = LearningPath((*path.lessons, item))

    shown = LessonHeader(path, item).markdown()

    assert "[Newton](../02-newton/index.html). Also assumed: Calculus." in shown


def test_header_with_a_glossary_lists_what_to_know_before_beginning(path: LearningPath):
    item = lesson(
        "drag",
        order=4,
        prerequisites=("newton",),
        outside=("Calculus: the chain rule",),
    )
    path = LearningPath((*path.lessons, item))
    glossary = Glossary((Entry("Calculus", "A definition.", ""),))

    shown = LessonHeader(path, item, glossary).markdown()

    assert "Prerequisites\n:   [Newton](../02-newton/index.html).\n" in shown
    assert (
        "Before you begin\n:   \n"
        "    - [Calculus](../../../glossary.html#calculus): the chain rule\n"
    ) in shown


def test_overview_lists_courses_with_their_lessons_then_methods_and_the_rest(
    path: LearningPath,
):
    shown = str(PathOverview(path, PATH_PAGE))

    assert "## Difficulty {#difficulty}" in shown
    for difficulty in DIFFICULTIES:
        assert difficulty.description in shown
    headings = [line for line in shown.splitlines() if line.startswith("#")]
    assert headings == [
        "## Courses {#courses}",
        "### Classical mechanics {#course-mechanics}",
        "## Methods {#methods}",
        "### Simulation {#method-simulation}",
        "### Formal proofs {#method-lean}",
        "## Difficulty {#difficulty}",
        "## Order {#order}",
        "## Your progress {#your-progress}",
        "## Prerequisite graph {#graph}",
    ]
    assert "LLM agents" not in shown and "Agent-based" not in shown
    cards = re.findall(r'<h(\d) class="lesson-card-title"><a href="([^"]+)"', shown)
    kinematics = "../lessons/mechanics/01-kinematics/index.html"
    newton = "../lessons/mechanics/02-newton/index.html"
    energy = "../lessons/mechanics/03-energy/index.html"
    proof = "../lessons/lean/01-proof/index.html"
    # One row per lesson, under its course, in the teaching order.
    assert cards == [("4", kinematics), ("4", newton), ("4", energy), ("4", proof)]
    # Under a method a lesson is a link, not a row.
    links = re.findall(r'<a class="lesson-link" href="([^"]+)"', shown)
    assert links == [kinematics, newton, energy, proof]  # simulation, then lean
    # The level links to the legend with its definition as the title.
    assert (
        f'<a href="index.html#difficulty" title="{DIFFICULTIES[2].description}">'
        "Advanced, level 3 of 3</a>" in shown
    )
    assert f'Prerequisites</dt><dd><a href="{energy}">Energy</a>.</dd>' in shown


def test_a_course_is_a_panel_with_its_lessons_behind_a_closed_disclosure(
    path: LearningPath,
):
    shown = str(PathOverview(path, PATH_PAGE))

    assert '<div class="course-panel" data-course="mechanics">' in shown
    assert "4 published lessons." in shown
    assert "Start with Kinematics" in shown
    # Native disclosure, closed by default: no ``open`` attribute anywhere.
    assert '<details class="course-lessons" id="course-mechanics-lessons">' in shown
    assert "<details open" not in shown and " open>" not in shown
    # Each lesson has its own nested disclosure with the facts.
    assert shown.count('<details class="lesson-details">') == 4
    assert shown.count("<dt>") == 4 * 6
    # The lessons of the course are the lessons of the page, none twice.
    assert shown.count('<li class="path-card" data-lesson-id=') == 4


def test_the_details_of_a_lesson_say_what_the_reader_builds_from_its_description():
    item = Lesson(
        **{**lesson("a", order=1).__dict__, "description": "Build a < b & check it."}
    )

    shown = str(PathOverview(LearningPath((item,)), PATH_PAGE))

    assert "<dt>What you build</dt><dd>Build a &lt; b &amp; check it.</dd>" in shown


def test_overview_escapes_what_the_front_matter_says_in_a_card():
    item = Lesson(**{**lesson("tricky", order=9).__dict__, "title": "A < B & C"})
    shown = str(PathOverview(LearningPath((item,)), PATH_PAGE))

    assert "A &lt; B &amp; C" in shown
    assert "A < B" not in shown


def test_overview_puts_every_lesson_in_one_row_with_its_facts():
    # A row is one list item: heading, the question when there is one, and
    # the facts in its details, so a reader gets the same structure for each
    # lesson.
    lessons = []
    for order in range(1, 12):
        earlier = ("l1",) if order > 1 else ()
        item = lesson(f"l{order}", order=order, prerequisites=earlier)
        description = f"About lesson {order},\nin two lines." if order % 2 else ""
        lessons.append(Lesson(**{**item.__dict__, "description": description}))

    shown = str(PathOverview(LearningPath(tuple(lessons)), PATH_PAGE))

    assert shown.count('<li class="path-card" data-lesson-id=') == 11
    # Six facts each, and the seventh, what the reader builds, for the six
    # lessons that have a description.
    assert shown.count("<dt>") == 11 * 6 + 6
    assert shown.count("<dt>What you build</dt>") == 6
    assert shown.count('<p class="lesson-question">') == 6  # lessons 1, 3, ... 11


def test_a_lesson_with_simulation_data_and_agents_gets_a_chip_for_each():
    base = lesson("a", order=1)
    helper = Lesson(**{**lesson("b", order=2).__dict__, "methods": ("llm-agents",)})
    main = Lesson(
        **{
            **base.__dict__,
            "methods": ("simulation", "measured-data"),
            "related": ("b",),
        }
    )

    shown = str(PathOverview(LearningPath((main, helper)), PATH_PAGE))
    chips = re.findall(r'<ul class="chips"[^>]*>(.*?)</ul>', shown)

    assert (
        chips[0]
        == "<li>Simulation</li><li>Experimental data</li><li>AI extensions</li>"
    )
    assert chips[1] == "<li>AI extensions</li>"


def test_a_site_with_a_preview_shows_one_thumbnail_with_alt_text_per_row(
    site: Path,
):
    shown = str(PathOverview(LearningPath.read(site), PATH_PAGE, site))

    thumbnails = re.findall(r'<img class="lesson-thumbnail"[^>]*>', shown)
    assert len(thumbnails) == 4
    for thumbnail in thumbnails:
        assert re.search(r'src="\.\./previews/[a-z0-9-]+\.svg"', thumbnail)
        assert re.search(r'alt="Preview, [^"]+"', thumbnail)
    # The panel shows the preview of its representative lesson.
    assert shown.count('<img class="course-thumbnail"') == 1
    assert "http" not in " ".join(re.findall(r'src="([^"]+)"', shown))


def test_overview_explains_what_previous_and_next_mean(path: LearningPath):
    section = str(PathOverview(path, PATH_PAGE)).split("## Order {#order}")[1]
    section = section.split("## Courses")[0]

    assert "Previous and next" in section
    assert "Classical mechanics, then Formal proofs" in section
    assert "course order" in section
    assert "prerequisites" in section


def test_overview_of_a_site_without_lessons_says_so():
    shown = str(PathOverview(LearningPath(()), PATH_PAGE))

    assert "No lesson has been published yet." in shown
    assert "{#courses}" not in shown and "{#methods}" not in shown
    assert "## Difficulty {#difficulty}" in shown


def pandoc_blocks(markdown: str) -> list[dict]:
    """The Pandoc document of ``markdown``, read by the Pandoc Quarto ships."""
    result = subprocess.run(
        ["quarto", "pandoc", "--from", "markdown", "--to", "json"],
        input=markdown,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)["blocks"]


# --- From the page being built --------------------------------------------------


def test_helpers_find_the_page_from_the_directory_the_cell_runs_in(
    site: Path, monkeypatch: pytest.MonkeyPatch
):
    (site / "path").mkdir()
    (site / PATH_PAGE).write_text("---\ntitle: Learning path\n---\n")
    (site / "glossary.yaml").write_text(
        "entries:\n  - term: Calculus\n    definition: A definition.\n"
    )

    monkeypatch.chdir(site / "lessons/mechanics/02-newton")
    header = lesson_header()
    assert header.lesson == NEWTON
    assert header.glossary is not None

    monkeypatch.chdir(site / "path")
    overview = learning_path()
    assert overview.page == PATH_PAGE
    assert 'href="../lessons/mechanics/02-newton/index.html"' in str(overview)


def test_header_outside_a_lesson_directory_is_an_error(
    site: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.chdir(site)

    with pytest.raises(LookupError, match="not a lesson"):
        lesson_header()


def test_helpers_outside_a_website_project_are_an_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FileNotFoundError, match="website project"):
        learning_path()
