"""The planned list of the home page is derived from the curriculum file, and
the examples the page links exist as lessons."""

from support.paths import SITE_SOURCE

from pbc.authoring import COURSES, HomeContent, LearningPath
from pbc.authoring.home import CONSTRUCT_EXAMPLE, INVESTIGATE_EXAMPLE, VERIFY_EXAMPLE


def test_the_planned_list_names_every_course_and_path_of_the_file_with_real_counts():
    path = LearningPath.read(SITE_SOURCE)
    lines = HomeContent(path).planned().splitlines()
    assert len(path.paths) == 4
    for course in COURSES:
        expected = (
            f"- {course.title}, course: {len(path.in_course(course))} "
            f"lesson{'' if len(path.in_course(course)) == 1 else 's'} published, "
            f"{len(path.planned_in_course(course))} planned."
        )
        assert expected in lines
    for method_path in path.paths:
        published = len(path.in_path(method_path))
        expected = (
            f"- {method_path.title}, method path: {published} "
            f"lesson{'' if published == 1 else 's'} published, "
            f"{len(path.planned_in_path(method_path))} planned."
        )
        assert expected in lines


def test_a_planned_lesson_is_never_part_of_a_published_count():
    path = LearningPath.read(SITE_SOURCE)
    published = {lesson.slot for lesson in path.lessons if lesson.slot}
    planned = {slot.label for slot in path.curriculum.slots} - published
    assert len(path.curriculum.slots) == len(published) + len(planned)
    for course in COURSES:
        unfilled = {slot.label for slot in path.planned_in_course(course)}
        assert unfilled <= planned
        assert not unfilled & {lesson.slot for lesson in path.in_course(course)}


def test_the_planned_list_names_no_delivered_feature_and_links_nothing():
    text = HomeContent(LearningPath.read(SITE_SOURCE)).planned()
    assert "](" not in text and "http" not in text
    assert "roadmap" not in text.lower() and "F15" not in text and "F5" not in text


def test_the_examples_are_published_lessons_of_the_three_activities():
    path = LearningPath.read(SITE_SOURCE)
    content = HomeContent(path)
    for lesson_id in (CONSTRUCT_EXAMPLE, INVESTIGATE_EXAMPLE, VERIFY_EXAMPLE):
        assert path.lesson(lesson_id).title in content.example(lesson_id)
    assert "simulation" in path.lesson(CONSTRUCT_EXAMPLE).methods
    assert "llm-agents" in path.lesson(INVESTIGATE_EXAMPLE).methods
    assert "lean" in path.lesson(VERIFY_EXAMPLE).methods
