"""The division of a test file of tests/e2e over several runs."""

import pytest
from support.shards import ShardError, parse, part_of, unlisted

FILE = "tests/e2e/test_x.py"
BY_LESSON = {FILE: {"by": "lesson", "shards": [["a"], ["b", "c"]]}}
BY_TEST = {FILE: {"by": "test", "shards": [[], ["test_slow"]]}}
# Everything that exists, whether a run selects it or not.
KNOWN = {"lesson": ["a", "b", "c"], "test": ["test_one", "test_two", "test_slow"]}


def test_a_lesson_runs_in_the_part_that_lists_it():
    tests = [("test_one", "a"), ("test_one", "b"), ("test_two", "c"), ("test_two", "a")]
    assert part_of(FILE, tests, BY_LESSON, 2, KNOWN) == [1, 2, 2, 1]


def test_a_test_without_a_lesson_runs_in_the_first_part():
    tests = [("test_guard", None), ("test_one", "a"), ("test_one", "b"), ("t", "c")]
    assert part_of(FILE, tests, BY_LESSON, 2, KNOWN) == [1, 1, 2, 2]


def test_a_lesson_that_no_part_lists_runs_in_exactly_one_part():
    # A new lesson needs no entry: its path selects the part, the same one in
    # every run, and over many lessons every part is used.
    lessons = [f"lessons/x/{n:02d}-new/index.html" for n in range(40)]
    tests = [("test_one", lesson) for lesson in lessons]
    table = {FILE: {"by": "lesson", "shards": [[], [], []]}}
    numbers = part_of(FILE, tests, table, 3, KNOWN)
    assert numbers == [unlisted(lesson, 3) for lesson in lessons]
    assert set(numbers) == {1, 2, 3}
    # Fixed values: a change of the rule would move lessons between parts.
    assert unlisted("lessons/mechanics/01-kinematics-as-a-program/index.html", 2) == 2


def test_a_listed_lesson_that_does_not_exist_is_refused():
    tests = [("test_one", "a"), ("test_one", "b")]
    with pytest.raises(ShardError, match="does not exist: c"):
        part_of(FILE, tests, BY_LESSON, 2, {**KNOWN, "lesson": ["a", "b"]})


def test_a_test_that_no_part_lists_runs_in_the_first_part():
    tests = [("test_new", None), ("test_slow", None), ("test_slow", "a")]
    assert part_of(FILE, tests, BY_TEST, 2, KNOWN) == [1, 2, 2]


def test_a_listed_test_that_does_not_exist_is_refused():
    with pytest.raises(ShardError, match="does not exist: test_slow"):
        part_of(FILE, [("test_new", None)], BY_TEST, 2, {**KNOWN, "test": ["test_new"]})


def test_a_selection_of_the_file_is_divided_like_the_whole_file():
    # One test selected by its node ID: the lessons and tests that the
    # selection leaves out still exist, and are not reported as missing.
    assert part_of(FILE, [("test_one", "b")], BY_LESSON, 2, KNOWN) == [2]
    assert part_of(FILE, [("test_one", None)], BY_TEST, 2, KNOWN) == [1]
    assert part_of(FILE, [], BY_TEST, 2, KNOWN) == []


def test_a_key_listed_twice_is_refused():
    table = {FILE: {"by": "lesson", "shards": [["a"], ["a"]]}}
    with pytest.raises(ShardError, match="more than once"):
        part_of(FILE, [("test_one", "a")], table, 2, KNOWN)


def test_another_number_of_parts_than_the_division_is_refused():
    with pytest.raises(ShardError, match="divided in 2 parts, not in 3"):
        part_of(FILE, [("test_one", "a")], BY_LESSON, 3, KNOWN)


def test_a_file_without_a_division_is_refused():
    with pytest.raises(ShardError, match="has no division"):
        part_of("tests/e2e/test_y.py", [("test_one", None)], BY_LESSON, 2, KNOWN)


def test_an_unknown_way_to_divide_is_refused():
    table = {FILE: {"by": "order", "shards": [[], []]}}
    with pytest.raises(ShardError, match="unknown"):
        part_of(FILE, [("test_one", None)], table, 2, KNOWN)


def test_the_option_names_a_part_of_a_number_of_parts():
    assert parse("1/2") == (1, 2)
    assert parse("3/3") == (3, 3)


@pytest.mark.parametrize("option", ["0/2", "3/2", "1", "1/0", "a/b", "1/2/3", "-1/2"])
def test_a_malformed_option_is_refused(option):
    with pytest.raises(ShardError, match="expected <part>/<parts>"):
        parse(option)
