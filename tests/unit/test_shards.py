"""The division of a test file of tests/e2e over several runs."""

import pytest
from support.shards import ShardError, parse, part_of

FILE = "tests/e2e/test_x.py"
TABLE = {FILE: [[], ["test_slow"]]}
# Every test of the file, whether a run selects it or not.
KNOWN = ["test_one", "test_two", "test_slow"]


def test_a_test_runs_in_the_part_that_lists_it():
    tests = ["test_one", "test_slow", "test_slow", "test_two"]
    assert part_of(FILE, tests, TABLE, 2, KNOWN) == [1, 2, 2, 1]


def test_a_test_that_no_part_lists_runs_in_the_first_part():
    known = [*KNOWN, "test_new"]
    assert part_of(FILE, ["test_new", "test_slow"], TABLE, 2, known) == [1, 2]


def test_a_listed_test_that_does_not_exist_is_refused():
    with pytest.raises(ShardError, match="does not exist: test_slow"):
        part_of(FILE, ["test_one"], TABLE, 2, ["test_one", "test_two"])


def test_a_selection_of_the_file_is_divided_like_the_whole_file():
    # One test selected by its node ID: the tests that the selection leaves
    # out still exist, and are not reported as missing.
    assert part_of(FILE, ["test_one"], TABLE, 2, KNOWN) == [1]
    assert part_of(FILE, ["test_slow"], TABLE, 2, KNOWN) == [2]
    assert part_of(FILE, [], TABLE, 2, KNOWN) == []


def test_a_test_listed_twice_is_refused():
    table = {FILE: [["test_one"], ["test_one"]]}
    with pytest.raises(ShardError, match="more than once"):
        part_of(FILE, ["test_one"], table, 2, KNOWN)


def test_another_number_of_parts_than_the_division_is_refused():
    with pytest.raises(ShardError, match="divided in 2 parts, not in 3"):
        part_of(FILE, ["test_one"], TABLE, 3, KNOWN)


def test_a_file_without_a_division_is_refused():
    with pytest.raises(ShardError, match="has no division"):
        part_of("tests/e2e/test_y.py", ["test_one"], TABLE, 2, KNOWN)


def test_the_option_names_a_part_of_a_number_of_parts():
    assert parse("1/2") == (1, 2)
    assert parse("3/3") == (3, 3)


@pytest.mark.parametrize("option", ["0/2", "3/2", "1", "1/0", "a/b", "1/2/3", "-1/2"])
def test_a_malformed_option_is_refused(option):
    with pytest.raises(ShardError, match="expected <part>/<parts>"):
        parse(option)
