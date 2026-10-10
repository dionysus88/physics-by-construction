"""Required checks on adaptive recommendations (roadmap F14; architecture,
"Learner state"; docs/authoring.md, "Recommendations").

The rules of ``site/learner/recommend.js`` are run in the browser on fixed
paths and stored states, and the pages are driven as a reader would, with
the keyboard, while the requests are recorded.
"""

import json

import pytest
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Browser, Page
from support.site_checks import DESKTOP, WCAG_TAGS
from support.site_server import SiteServer

from pbc.authoring.progress import STORAGE_KEY

PATH_PAGE = "path/index.html"
LESSON = "lessons/mechanics/02-newtons-laws/index.html"
RULES = "learner/recommend.js"

# A path of four lessons: a and b are first, c needs both, d needs c.
PATH = [
    {"id": "a", "title": "A", "href": "a.html", "prerequisites": []},
    {"id": "b", "title": "B", "href": "b.html", "prerequisites": []},
    {"id": "c", "title": "C", "href": "c.html", "prerequisites": ["a", "b"]},
    {"id": "d", "title": "D", "href": "d.html", "prerequisites": ["c"]},
]

_RUN = """
async ([url, lessons, state]) => {
  const { recommend } = await import(url);
  return recommend(lessons, state).map(
    (item) => [item.lesson.id, item.kind, item.reason]
  );
}
"""


@pytest.fixture
def page(browser: Browser):
    context = browser.new_context(viewport=DESKTOP)
    yield context.new_page()
    context.close()


def rules(page: Page, server: SiteServer, state: dict | None, path=PATH) -> list:
    if "about.html" not in page.url:
        page.goto(server.url + "about.html", wait_until="load")
    return page.evaluate(_RUN, [server.url + RULES, path, state])


def lessons(**entries) -> dict:
    return {"version": 1, "lessons": entries}


DONE = {"completed": True}


def test_without_a_stored_result_there_is_nothing_to_recommend(
    page: Page, server: SiteServer
):
    assert rules(page, server, None) == []
    assert rules(page, server, lessons()) == []
    assert rules(page, server, lessons(unknown=DONE)) == []


def test_a_lesson_whose_prerequisites_are_completed_is_recommended_with_the_reason(
    page: Page, server: SiteServer
):
    found = rules(page, server, lessons(a=DONE))

    assert [item[:2] for item in found] == [["b", "next"]]
    assert found[0][2] == "It has no prerequisites, and you have not completed it."

    found = rules(page, server, lessons(a=DONE, b=DONE))
    assert [item[:2] for item in found] == [["c", "next"]]
    assert found[0][2] == "You completed A and B, which are its prerequisites."


def test_a_lesson_completed_without_its_prerequisite_recommends_the_prerequisite(
    page: Page, server: SiteServer
):
    found = rules(page, server, lessons(c=DONE))

    assert [item[:2] for item in found] == [
        ["a", "prerequisite"],
        ["b", "prerequisite"],
        ["d", "next"],
    ]
    assert "You completed C, which builds on this lesson" in found[0][2]


def test_a_self_check_tried_without_success_is_recommended_again_before_the_next_lesson(
    page: Page, server: SiteServer
):
    state = lessons(a=DONE, b={"selfCheck": {"done": False, "attempts": 2}})

    found = rules(page, server, state)

    assert [item[:2] for item in found] == [["b", "retry"]]
    assert "2 times" in found[0][2]
    once = lessons(a=DONE, b={"selfCheck": {"done": False, "attempts": 1}})
    assert "once" in rules(page, server, once)[0][2]


def test_a_lesson_is_recommended_once_and_at_most_three_are_given(
    page: Page, server: SiteServer
):
    many = [
        {"id": f"l{n}", "title": f"L{n}", "href": f"{n}.html", "prerequisites": []}
        for n in range(6)
    ]

    found = rules(page, server, lessons(l5=DONE), many)

    assert [item[0] for item in found] == ["l0", "l1", "l2"]
    twice = lessons(c={"completed": False, "selfCheck": {"done": False, "attempts": 1}})
    assert [item[0] for item in rules(page, server, twice)].count("c") == 1


def test_ignored_lessons_are_skipped_and_everything_completed_gives_nothing(
    page: Page, server: SiteServer
):
    state = lessons(a=DONE)
    state["ignored"] = ["b"]

    assert rules(page, server, state) == []
    everything = lessons(a=DONE, b=DONE, c=DONE, d=DONE)
    assert rules(page, server, everything) == []


def test_the_same_state_gives_the_same_recommendations(page: Page, server: SiteServer):
    state = lessons(c=DONE, a={"selfCheck": {"done": False, "attempts": 1}})

    assert rules(page, server, state) == rules(
        page, server, json.loads(json.dumps(state))
    )


# --- The pages -----------------------------------------------------------------


def own(errors: list[str]) -> list[str]:
    """The script errors that are not those of Quarto's navigation script on
    the drawing of the path page (an SVG link has no string ``href``), which
    this feature does not touch."""
    return [error for error in errors if "links[i].href" not in error]


def seed(page: Page, server: SiteServer, state: dict | None) -> None:
    page.goto(server.url + "about.html", wait_until="load")
    if state is not None:
        page.evaluate(
            "([key, text]) => localStorage.setItem(key, text)",
            [STORAGE_KEY, json.dumps(state)],
        )


def stored(page: Page) -> dict | None:
    text = page.evaluate("(key) => localStorage.getItem(key)", STORAGE_KEY)
    return json.loads(text) if text is not None else None


# kinematics is the first lesson of the mechanics course; newtons-laws needs it.
COMPLETED = lessons(kinematics=DONE)


def test_the_path_page_suggests_the_next_lesson_with_its_reason(
    page: Page, server: SiteServer
):
    seed(page, server, COMPLETED)
    page.goto(server.url + PATH_PAGE, wait_until="networkidle")

    items = page.locator("#recommendations .recommendations li")

    assert items.count() >= 1
    first = items.first
    assert first.locator("a").get_attribute("href").endswith("/index.html")
    assert first.locator(".recommendation-reason").inner_text().startswith("Why: ")
    assert (
        "Kinematics as a program"
        in first.locator(".recommendation-reason").inner_text()
    )


def test_a_lesson_page_suggests_what_to_do_next_with_working_links(
    page: Page, server: SiteServer
):
    seed(page, server, COMPLETED)
    page.goto(server.url + LESSON, wait_until="networkidle")

    link = page.locator("#recommendations .recommendations li a").first
    link.click()
    page.wait_for_load_state("load")

    assert page.title()
    assert page.url.startswith(server.url + "lessons/")


def test_ignoring_a_suggestion_with_the_keyboard_removes_it_and_it_can_be_shown_again(
    page: Page, server: SiteServer
):
    seed(page, server, COMPLETED)
    page.goto(server.url + PATH_PAGE, wait_until="networkidle")
    items = page.locator("#recommendations .recommendations li")
    before = items.count()
    title = items.first.locator("a").inner_text()

    button = items.first.get_by_role("button", name="Ignore")
    button.focus()
    page.keyboard.press("Enter")

    assert items.count() == before - 1
    assert stored(page)["ignored"]
    page.reload(wait_until="networkidle")
    titles = page.locator("#recommendations .recommendations li a").all_inner_texts()
    assert title not in titles
    page.get_by_role("button", name="Show ignored suggestions again").click()
    assert (
        title
        in page.locator("#recommendations .recommendations li a").all_inner_texts()
    )
    assert "ignored" not in stored(page)


def test_computing_and_ignoring_recommendations_makes_no_request(
    page: Page, server: SiteServer
):
    seed(page, server, COMPLETED)
    page.goto(server.url + PATH_PAGE, wait_until="networkidle")
    requests: list[str] = []
    page.on("request", lambda request: requests.append(request.url))

    page.locator("#recommendations").get_by_role("button", name="Ignore").first.click()
    page.get_by_role("button", name="Show ignored suggestions again").click()
    page.evaluate(
        "([key, text]) => { localStorage.setItem(key, text);"
        " window.dispatchEvent(new StorageEvent('storage', { key })); }",
        [STORAGE_KEY, json.dumps(lessons())],
    )
    page.wait_for_load_state("networkidle")

    assert requests == []
    assert page.locator("#recommendations .recommendations li").count() == 0


def test_loading_a_page_with_recommendations_requests_only_files_of_the_site(
    page: Page, server: SiteServer
):
    seed(page, server, COMPLETED)
    requests: list[tuple[str, str, str | None]] = []
    page.on("request", lambda r: requests.append((r.method, r.url, r.post_data)))

    page.goto(server.url + PATH_PAGE, wait_until="networkidle")

    assert requests
    for method, url, body in requests:
        assert url.startswith(server.origin + "/"), url
        assert method == "GET" and not body, url
        assert "path.json" not in url
    assert page.locator("#recommendations .recommendations li").count() >= 1


@pytest.mark.parametrize("name", [PATH_PAGE, LESSON])
def test_without_stored_state_the_plain_path_shows_and_nothing_is_suggested(
    browser: Browser, server: SiteServer, name: str
):
    context = browser.new_context(viewport=DESKTOP)
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))

    page.goto(server.url + name, wait_until="networkidle")

    assert not own(errors)
    assert page.locator("#recommendations li").count() == 0
    assert page.locator("#recommendations").is_hidden()
    assert stored(page) is None
    context.close()


def test_without_javascript_the_path_page_is_the_plain_learning_path(
    browser: Browser, server: SiteServer
):
    context = browser.new_context(viewport=DESKTOP, java_script_enabled=False)
    page = context.new_page()
    page.goto(server.url + PATH_PAGE, wait_until="load")

    assert page.locator(".path-card").count() > 0
    assert page.locator("#recommendations li, #recommendations button").count() == 0
    context.close()


def test_stored_data_with_a_wrong_ignored_list_is_discarded_and_the_page_works(
    page: Page, server: SiteServer
):
    bad = lessons(kinematics=DONE)
    bad["ignored"] = "kinematics"
    seed(page, server, bad)
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))

    page.goto(server.url + PATH_PAGE, wait_until="networkidle")

    assert not own(errors)
    assert stored(page) is None


def test_the_accessibility_scan_passes_with_suggestions_shown(
    page: Page, server: SiteServer
):
    seed(page, server, COMPLETED)
    page.goto(server.url + PATH_PAGE, wait_until="networkidle")
    options = {
        "runOnly": {"type": "tag", "values": WCAG_TAGS},
        "resultTypes": ["violations"],
    }
    results = Axe().run(page, options=options)
    found = [
        f"{finding['id']} at {node['target']}"
        for finding in results.response["violations"]
        for node in finding["nodes"]
    ]

    assert not found, "\n".join(found)
