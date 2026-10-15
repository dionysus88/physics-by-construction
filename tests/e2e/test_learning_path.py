"""Required checks on the learning path of the built site (architecture,
"Lesson model"): the path page and every lesson header are generated from
the lesson front matter, and a learner reaches every lesson from the home
page without JavaScript.

The expected order, neighbours, and prerequisites are read from the lesson
sources with the same module that generates the pages; that the module
orders and validates correctly is covered by tests/unit/test_learning_path.py.
"""

from collections import deque
from pathlib import Path
from urllib.parse import urldefrag, urljoin

import pytest
from playwright.sync_api import Browser, BrowserContext, Locator, Page
from support.paths import SITE_SOURCE
from support.site_checks import DESKTOP, PHONE
from support.site_server import SiteServer

from pbc.authoring import DIFFICULTIES, METHODS, LearningPath
from pbc.authoring.glossary import Glossary
from pbc.authoring.path import PATH_PAGE, Lesson

PATH = Path(PATH_PAGE).with_suffix(".html").as_posix()
LESSON_PATH = LearningPath.read(SITE_SOURCE)
GLOSSARY = Glossary.read(SITE_SOURCE)


def built(lesson: Lesson) -> str:
    return Path(lesson.page).with_suffix(".html").as_posix()


@pytest.fixture
def without_scripts(browser: Browser) -> BrowserContext:
    context = browser.new_context(viewport=DESKTOP, java_script_enabled=False)
    yield context
    context.close()


def test_the_site_has_lessons_and_a_path_page(site_dir: Path):
    # Guards the tests below: without lessons they would check nothing, and
    # the checks every page gets (accessibility, widths) must see the path.
    assert LESSON_PATH.lessons
    assert (site_dir / PATH).is_file()


def test_every_lesson_is_reached_from_the_home_page_without_javascript(
    without_scripts: BrowserContext, server: SiteServer
):
    page = without_scripts.new_page()
    visited: set[str] = set()
    queue = deque(["index.html"])
    while queue:
        name = queue.popleft()
        if name in visited:
            continue
        visited.add(name)
        page.goto(server.url + name, wait_until="load")
        for href in page.locator("a[href]").evaluate_all(
            "links => links.map(a => a.getAttribute('href'))"
        ):
            target = urldefrag(urljoin(server.url + name, href)).url
            if target.startswith(server.url) and target.endswith(".html"):
                queue.append(target[len(server.url) :])

    assert PATH in visited
    assert {built(lesson) for lesson in LESSON_PATH.lessons} <= visited


def _plain(text: str) -> str:
    # The build turns apostrophes into typographic ones.
    return text.replace("\u2019", "'")


def _hrefs(page: Page, selector: str) -> list[str]:
    return page.locator(selector).evaluate_all("links => links.map(a => a.href)")


def test_path_page_explains_the_difficulty_scale(
    without_scripts: BrowserContext, server: SiteServer
):
    page = without_scripts.new_page()
    page.goto(server.url + PATH, wait_until="load")

    scale = page.locator("main #difficulty").inner_text()
    for difficulty in DIFFICULTIES:
        assert difficulty.title.lower() in scale.lower()
        assert difficulty.description in scale


def _expand(scope: Locator) -> None:
    """Open every disclosure of ``scope`` the way a reader does, by its
    summary: the courses first, then the details of the lessons in them."""
    for selector in ("details.course-lessons", "details.lesson-details"):
        for details in scope.locator(selector).all():
            if details.get_attribute("open") is None:
                details.locator("> summary").click()


def _check_items(
    items: Locator, lessons: tuple[Lesson, ...], server: SiteServer
) -> None:
    """Each row shows what the front matter of its lesson says."""
    assert items.count() == len(lessons)
    for item, lesson in zip(items.all(), lessons, strict=True):
        difficulty = DIFFICULTIES[lesson.difficulty - 1]
        heading = item.locator(".lesson-card-title")
        assert heading.count() == 1
        assert _plain(heading.inner_text()) == _plain(lesson.title)
        assert _hrefs(heading, "a") == [server.url + built(lesson)]
        if lesson.description:
            assert _plain(item.locator(".lesson-question").inner_text()) == _plain(
                " ".join(lesson.description.split())
            )
        # One thumbnail from the build, with alt text, never from outside.
        thumbnail = item.locator("img.lesson-thumbnail")
        assert thumbnail.count() == 1
        assert thumbnail.get_attribute("alt").startswith("Preview, ")
        assert thumbnail.get_attribute("src").startswith("../previews/")
        assert difficulty.title in item.locator(".level-badge").inner_text()

        facts = {
            term: item.locator(f"dt:text-is('{term}') + dd")
            for term in ("Course", "Methods", "Level", "What you\u2019ll learn")
        }
        # What the reader builds is the description of the lesson.
        what_built = item.locator("dt:text-is('What you build') + dd")
        assert what_built.count() == (1 if lesson.description else 0)
        if lesson.description:
            assert _plain(what_built.inner_text()) == _plain(
                " ".join(lesson.description.split())
            )
        assert facts["Course"].inner_text() == next(
            c.title for c in LESSON_PATH.courses if c.id == lesson.course
        )
        assert facts["Methods"].inner_text() == ", ".join(
            next(m.title for m in METHODS if m.id == method)
            for method in lesson.methods
        )
        # The level links to the legend and carries its definition on hover.
        assert difficulty.title in facts["Level"].inner_text()
        assert _hrefs(facts["Level"], "a") == [f"{server.url}{PATH}#difficulty"]
        assert facts["Level"].locator("a").get_attribute("title") == (
            difficulty.description
        )
        assert [
            _plain(text)
            for text in facts["What you\u2019ll learn"].locator("li").all_inner_texts()
        ] == list(lesson.outcomes)

        prerequisites = item.locator("dt:text-is('Prerequisites') + dd")
        assert _hrefs(prerequisites, "a") == [
            server.url + built(LESSON_PATH.lesson(item))
            for item in lesson.prerequisites
        ]
        assert all(outside in prerequisites.inner_text() for outside in lesson.outside)
        related = item.locator("dt:text-is('Related') + dd")
        assert _hrefs(related, "a") == [
            server.url + built(LESSON_PATH.lesson(item)) for item in lesson.related
        ]


def _published_rows(section: Locator) -> Locator:
    return section.locator("li.path-card")


def test_a_course_is_closed_until_opened_and_then_shows_its_lessons_without_javascript(
    without_scripts: BrowserContext, server: SiteServer
):
    page = without_scripts.new_page()
    page.goto(server.url + PATH, wait_until="load")

    for course in LESSON_PATH.courses:
        section = page.locator(f"main section#course-{course.id}")
        assert section.locator("h3").first.inner_text() == course.title
        lessons = LESSON_PATH.in_course(course)
        panel = section.locator(".course-panel")
        assert f"{len(lessons)} published" in panel.inner_text()
        assert panel.locator("img.course-thumbnail").get_attribute("alt")
        disclosure = section.locator("details.course-lessons")
        # Closed by default: no lesson row is visible before it is opened.
        assert disclosure.get_attribute("open") is None
        assert not _published_rows(section).first.is_visible()
        _expand(section)
        _check_items(_published_rows(section), lessons, server)
        # Every lesson of the course is listed, once, and a planned row is
        # never a link.
        planned = section.locator("li.planned-slot")
        assert planned.locator(".slot-label").all_inner_texts() == [
            slot.label for slot in LESSON_PATH.planned_in_course(course)
        ]
        assert planned.locator("a").count() == 0
        assert "planned" in planned.first.inner_text()
    # A course without a lesson has no panel; one sentence names it.
    assert page.locator("main section#courses > section.level3").count() == len(
        LESSON_PATH.courses
    )
    courses = page.locator("main section#courses").inner_text()
    for course in LESSON_PATH.planned_courses:
        assert _plain(course.title) in _plain(courses)
        assert page.locator(f"main section#course-{course.id}").count() == 0
    assert page.locator("main .slot-label:text-is('T0')").count() == 0


def _check_links(items: Locator, lessons: tuple[Lesson, ...], server: SiteServer):
    """A path or a method lists each lesson once, as a link to its page."""
    assert items.count() == len(lessons)
    assert items.locator("a").evaluate_all("links => links.map(a => a.href)") == [
        server.url + built(lesson) for lesson in lessons
    ]
    # No lesson content is repeated: no heading, no facts, no thumbnail.
    assert items.locator("dl, h3, h4, img").count() == 0


def test_path_page_lists_the_lessons_of_each_method_as_links_in_path_order(
    without_scripts: BrowserContext, server: SiteServer
):
    page = without_scripts.new_page()
    page.goto(server.url + PATH, wait_until="load")

    for method in LESSON_PATH.methods:
        section = page.locator(f"main section#method-{method.id}")
        assert section.locator("h3").first.inner_text() == method.title
        _check_links(section.locator("li.path-link"), LESSON_PATH.using(method), server)
    # A method without a lesson has no section.
    assert page.locator("main section#methods > section.level3").count() == len(
        LESSON_PATH.methods
    )


def test_every_lesson_is_a_row_under_its_course_and_a_link_under_its_methods_and_path(
    without_scripts: BrowserContext, server: SiteServer
):
    # The page compared with the metadata, the other way round: for each
    # lesson, the one row is under its course; the sections that only link it
    # are exactly its methods and path.
    page = without_scripts.new_page()
    page.goto(server.url + PATH, wait_until="load")

    for lesson in LESSON_PATH.lessons:
        href = server.url + built(lesson)
        rows = page.locator("main section.level3").evaluate_all(
            "(sections, href) => sections"
            ".filter(s => [...s.querySelectorAll('li.path-card h4 > a')]"
            ".some(a => a.href === href)).map(s => s.id)",
            href,
        )
        links = page.locator("main section.level3").evaluate_all(
            "(sections, href) => sections"
            ".filter(s => [...s.querySelectorAll('li.path-link > a.lesson-link')]"
            ".some(a => a.href === href)).map(s => s.id)",
            href,
        )
        slot = LESSON_PATH.slot_of(lesson)
        assert rows == [f"course-{lesson.course}"], lesson.id
        assert sorted(links) == sorted(
            [f"method-{method}" for method in lesson.methods]
            + ([f"path-{slot.path}"] if slot and slot.path else [])
        ), lesson.id


def test_path_page_lists_each_method_path_with_its_planned_slots(
    without_scripts: BrowserContext, server: SiteServer
):
    # The curriculum file and the front matter, compared with the page: the
    # published lessons of a path in the order of its slots as links, and
    # every slot no lesson fills as a planned entry without a link.
    page = without_scripts.new_page()
    page.goto(server.url + PATH, wait_until="load")

    assert page.locator("main section#paths > section.level3").count() == len(
        LESSON_PATH.paths
    )
    for method_path in LESSON_PATH.paths:
        section = page.locator(f"main section#path-{method_path.id}")
        assert section.locator("h3").first.inner_text() == method_path.title
        _check_links(
            section.locator("li.path-link"), LESSON_PATH.in_path(method_path), server
        )
        published = len(LESSON_PATH.in_path(method_path))
        planned_count = len(LESSON_PATH.planned_in_path(method_path))
        expected = f"{published} published lesson{'s' if published != 1 else ''}"
        if planned_count:
            expected += f", {planned_count} planned"
        assert section.locator("p.path-count").inner_text() == expected
        assert section.locator("li.path-link").count() == published
        planned = section.locator("li.planned-slot")
        assert planned.locator(".slot-label").all_inner_texts() == [
            slot.label for slot in LESSON_PATH.planned_in_path(method_path)
        ]
        assert planned.locator("a").count() == 0


def test_the_page_discloses_by_keyboard(
    without_scripts: BrowserContext, server: SiteServer
):
    page = without_scripts.new_page()
    page.goto(server.url + PATH, wait_until="load")
    course = LESSON_PATH.courses[0]
    summary = page.locator(
        f"main section#course-{course.id} details.course-lessons > summary"
    )
    summary.focus()
    assert page.evaluate("document.activeElement.tagName") == "SUMMARY"
    page.keyboard.press("Enter")
    assert page.locator(
        f"main section#course-{course.id} li.path-card"
    ).first.is_visible()
    page.keyboard.press("Space")
    assert not page.locator(
        f"main section#course-{course.id} li.path-card"
    ).first.is_visible()


def test_the_page_reflows_at_320_pixels_without_two_way_scrolling(
    browser: Browser, server: SiteServer
):
    context = browser.new_context(viewport={"width": 320, "height": 800})
    page = context.new_page()
    page.goto(server.url + PATH, wait_until="load")
    for details in page.locator("main details.course-lessons").all():
        details.locator("> summary").click()
    assert page.evaluate("document.documentElement.scrollWidth") <= 320
    context.close()


def test_the_filters_hide_rows_and_store_nothing(browser: Browser, server: SiteServer):
    context = browser.new_context(viewport=DESKTOP)
    page = context.new_page()
    page.goto(server.url + PATH, wait_until="load")
    stored = page.evaluate("JSON.stringify({...window.localStorage})")
    form = page.locator("#path-filters form")
    form.locator("select[name=state]").select_option("planned")
    assert page.locator("li.path-card:visible").count() == 0
    assert page.locator("li.planned-slot:visible").count() > 0
    form.locator("button").click()
    assert page.locator("#path-filters [role=status]").inner_text() == ""
    # The filters wrote nothing: the storage is what it was before.
    assert page.evaluate("JSON.stringify({...window.localStorage})") == stored
    context.close()


def test_a_link_to_a_course_opens_its_lessons_with_scripts(
    browser: Browser, server: SiteServer
):
    context = browser.new_context(viewport=DESKTOP)
    page = context.new_page()
    course = LESSON_PATH.courses[0]
    page.goto(f"{server.url}{PATH}#course-{course.id}", wait_until="load")
    assert page.locator(f"#course-{course.id} li.path-card").first.is_visible()
    context.close()


def test_path_page_explains_previous_and_next(
    without_scripts: BrowserContext, server: SiteServer
):
    page = without_scripts.new_page()
    page.goto(server.url + PATH, wait_until="load")

    order = page.locator("main section#order").inner_text()
    assert "Previous and next" in order
    assert "course order" in order
    assert "prerequisites" in order


# Every lesson address that existed before the courses (F37): the address
# resolves to the lesson with this id.
PREVIOUS_ADDRESSES = {
    f"lessons/{directory}/index.html": lesson_id
    for directory, lesson_id in {
        "mechanics/01-kinematics-as-a-program": "kinematics",
        "mechanics/02-newtons-laws": "newtons-laws",
        "mechanics/03-projectile-motion-with-drag": "projectile-with-drag",
        "mechanics/04-harmonic-oscillator": "harmonic-oscillator",
        "mechanics/05-numerical-integrators": "numerical-integrators",
        "mechanics/06-energy-conservation": "energy-conservation",
        "mechanics/07-momentum-and-collisions": "momentum-and-collisions",
        "mechanics/08-kepler-orbit": "kepler-orbit",
        "agents-llm/01-an-agent-runs-an-experiment": "agent-experiment",
        "agents-abm/01-particles-in-a-box": "particles-in-a-box",
        "lean/01-proving-what-the-simulation-showed": (
            "proving-what-the-simulation-showed"
        ),
    }.items()
}


@pytest.mark.parametrize("address, lesson_id", PREVIOUS_ADDRESSES.items())
def test_every_previous_lesson_address_still_resolves_to_its_lesson(
    without_scripts: BrowserContext,
    server: SiteServer,
    site_dir: Path,
    address: str,
    lesson_id: str,
):
    assert (site_dir / address).is_file()
    lesson = LESSON_PATH.lesson(lesson_id)
    assert built(lesson) == address
    # The page served at the address is that lesson, not only a file there.
    page = without_scripts.new_page()
    page.goto(server.url + address, wait_until="load")
    assert _plain(page.locator("main h1").first.inner_text()) == _plain(lesson.title)


@pytest.mark.parametrize("lesson", LESSON_PATH.lessons, ids=lambda lesson: lesson.id)
def test_lesson_header_shows_the_facts_of_the_path_with_links(
    without_scripts: BrowserContext, server: SiteServer, lesson: Lesson
):
    page = without_scripts.new_page()
    page.goto(server.url + built(lesson), wait_until="load")
    header = page.locator("main .lesson-header")
    assert header.count() == 1
    # The header comes before the text of the lesson.
    assert page.locator("main > :not(header) .lesson-header").count() == 1
    first = page.locator("main > :not(header)").first
    assert first.locator(".lesson-header").count() == 1

    rows = dict(
        zip(
            [_plain(text) for text in header.locator("dt").all_inner_texts()],
            header.locator("dd").all(),
            strict=True,
        )
    )
    assert list(rows) == [
        "Course",
        *(["Slot"] if lesson.slot else []),
        "Methods",
        "Difficulty",
        "What you'll learn",
        "Prerequisites",
        "Before you begin",
        "Related",
        "Previous",
        "Next",
    ]

    course = next(c for c in LESSON_PATH.courses if c.id == lesson.course)
    in_course = LESSON_PATH.in_course(course)
    assert rows["Course"].inner_text() == (
        f"{course.title}, lesson {in_course.index(lesson) + 1} of {len(in_course)}"
    )
    assert _hrefs(rows["Course"], "a") == [f"{server.url}{PATH}#course-{course.id}"]

    methods = [next(m for m in METHODS if m.id == item) for item in lesson.methods]
    assert rows["Methods"].inner_text() == ", ".join(m.title for m in methods)
    assert _hrefs(rows["Methods"], "a") == [
        f"{server.url}{PATH}#method-{m.id}" for m in methods
    ]

    difficulty = DIFFICULTIES[lesson.difficulty - 1]
    assert difficulty.title in rows["Difficulty"].inner_text()
    assert _hrefs(rows["Difficulty"], "a") == [f"{server.url}{PATH}#difficulty"]

    assert [
        _plain(text)
        for text in rows["What you'll learn"].locator("li").all_inner_texts()
    ] == list(lesson.outcomes)

    assert _hrefs(rows["Prerequisites"], "a") == [
        server.url + built(LESSON_PATH.lesson(item)) for item in lesson.prerequisites
    ]

    # Each outside prerequisite is listed with its detail; its term links to
    # the entry of the glossary.
    begin = rows["Before you begin"]
    assert [_plain(text) for text in begin.locator("li").all_inner_texts()] == list(
        lesson.outside
    )
    assert _hrefs(begin, "a") == [
        f"{server.url}glossary.html#{GLOSSARY.entry(outside).anchor}"
        for outside in lesson.outside
    ]

    if lesson.related:
        assert _hrefs(rows["Related"], "a") == [
            server.url + built(LESSON_PATH.lesson(item)) for item in lesson.related
        ]
        assert rows["Related"].inner_text() == ", ".join(
            LESSON_PATH.lesson(item).title for item in lesson.related
        )
    else:
        assert rows["Related"].inner_text() == "none"
        assert _hrefs(rows["Related"], "a") == []

    for name, neighbour in (
        ("Previous", LESSON_PATH.previous(lesson)),
        ("Next", LESSON_PATH.next(lesson)),
    ):
        if neighbour is None:
            assert "none" in rows[name].inner_text()
            assert _hrefs(rows[name], "a") == [server.url + PATH + "#order"]
        else:
            assert rows[name].inner_text() == neighbour.title
            assert _hrefs(rows[name], "a") == [server.url + built(neighbour)]


def test_glossary_page_defines_every_entry_and_links_the_lessons_without_javascript(
    without_scripts: BrowserContext, server: SiteServer
):
    page = without_scripts.new_page()
    page.goto(server.url + "glossary.html", wait_until="load")

    main = page.locator("main")
    for entry in GLOSSARY.entries:
        section = main.locator(f"section#{entry.anchor}")
        assert section.count() == 1, entry.term
        assert section.locator("h2").inner_text() == entry.term
        assert entry.definition in section.inner_text()
        users = [
            lesson
            for lesson in LESSON_PATH.lessons
            if any(GLOSSARY.entry(text) == entry for text in lesson.outside)
        ]
        assert users, f"no lesson assumes {entry.term}"
        assert [
            link.get_attribute("href")
            for link in section.locator("a").all()
            if link.inner_text() in {lesson.title for lesson in users}
        ] == [f"lessons/{built(lesson).split('lessons/')[1]}" for lesson in users]


def test_graph_and_its_text_alternative_are_present_without_javascript(
    without_scripts: BrowserContext, server: SiteServer
):
    page = without_scripts.new_page()
    page.goto(server.url + PATH, wait_until="load")

    # The map is optional: it is behind a disclosure, closed until opened.
    disclosure = page.locator("main details#dependency-map")
    assert disclosure.get_attribute("open") is None
    disclosure.locator("> summary").click()
    graph = disclosure.locator(".prerequisite-graph")
    assert graph.count() == 1
    svg = graph.locator("svg")
    assert svg.get_attribute("role") is None
    for name in svg.get_attribute("aria-labelledby").split():
        assert svg.locator(f"#{name}").count() == 1

    # Every lesson is a node that links to it, in path order.
    nodes = graph.locator("a").evaluate_all(
        "links => links.map("
        "a => new URL(a.getAttribute('href'), document.baseURI).href)"
    )
    assert nodes == [server.url + built(lesson) for lesson in LESSON_PATH.lessons]
    # The text list has one sentence for every edge of the front matter.
    edges = sum(
        len(lesson.prerequisites) + len(lesson.related)
        for lesson in LESSON_PATH.lessons
    )
    assert disclosure.locator("ol.visually-hidden > li").count() == edges
    legend = disclosure.locator(".graph-legend").inner_text()
    assert "Requires" in legend and "Related" in legend


def test_graph_nodes_are_reached_by_keyboard_in_path_order_with_visible_focus(
    without_scripts: BrowserContext, server: SiteServer
):
    page = without_scripts.new_page()
    page.goto(server.url + PATH, wait_until="load")
    # Opened by keyboard, so that the focus of the nodes is a keyboard focus.
    page.locator("main details#dependency-map > summary").focus()
    page.keyboard.press("Enter")
    nodes = page.locator("main details#dependency-map .prerequisite-graph a")
    nodes.first.focus()

    seen = []
    for _ in LESSON_PATH.lessons:
        seen.append(page.evaluate("document.activeElement.getAttribute('href')"))
        assert seen[-1]
        # The focused node has a thicker outline than the others.
        width = page.evaluate(
            "getComputedStyle(document.activeElement.querySelector('rect')).strokeWidth"
        )
        assert float(width.removesuffix("px")) >= 3
        page.keyboard.press("Tab")
    assert [urljoin(server.url + PATH, href) for href in seen] == [
        server.url + built(lesson) for lesson in LESSON_PATH.lessons
    ]


def test_graph_scrolls_inside_its_box_on_a_phone(browser: Browser, server: SiteServer):
    context = browser.new_context(viewport=PHONE, java_script_enabled=False)
    page = context.new_page()
    page.goto(server.url + PATH, wait_until="load")
    page.locator("main details#dependency-map > summary").click()

    box = page.locator("main details#dependency-map .prerequisite-graph")
    widths = box.evaluate("e => [e.clientWidth, e.scrollWidth]")
    assert widths[1] > widths[0]
    assert box.get_attribute("tabindex") == "0"
    assert page.evaluate("document.documentElement.scrollWidth") <= PHONE["width"]
    context.close()
