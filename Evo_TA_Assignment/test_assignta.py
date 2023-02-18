import pytest
import TA_allocation as ta
from test1_solution import Solution1
from test2_solution import Solution2
from test3_solution import Solution3
import pandas as pd

@pytest.fixture
def cases():
    ta = pd.read_csv("tas.csv").drop(["name"], axis=1)
    practicums = pd.read_csv("sections.csv")[["section", "min_ta", "daytime"]]

    # set assignment solution based on test1.csv array
    default_solution1 = Solution1(ta, practicums)
    default_solution1.populate_assignments()
    default_solution1.calculate_preference_assignments()
    default_solution1.calculate_current_tas()
    default_solution1.calculate_current_tas_section()
    default_solution1.calculate_preference_time_assignments()

    # set assignment solution based on test2.csv array
    default_solution2 = Solution2(ta, practicums)
    default_solution2.populate_assignments()
    default_solution2.calculate_preference_assignments()
    default_solution2.calculate_current_tas()
    default_solution2.calculate_current_tas_section()
    default_solution2.calculate_preference_time_assignments()

    # set assignment solution based on test3.csv array
    default_solution3 = Solution3(ta, practicums)
    default_solution3.populate_assignments()
    default_solution3.calculate_preference_assignments()
    default_solution3.calculate_current_tas()
    default_solution3.calculate_current_tas_section()
    default_solution3.calculate_preference_time_assignments()
    return default_solution1, default_solution2, default_solution3


def test_overallocation(cases):
    """
    Unit tests for overallocation function
    """
    test1, test2, test3 = cases
    assert ta.overallocation(test1) == 37, "Incorrect overallocation score for test 1"
    assert ta.overallocation(test2) == 41, "Incorrect overallocation score for test 2"
    assert ta.overallocation(test3) == 23, "Incorrect overallocation score for test 3"


def test_time_conflicts(cases):
    """
        Unit tests for time conflict function
    """
    test1, test2, test3 = cases
    assert ta.time_conflicts(test1) == 8, "Incorrect time conflicts score for test 1"
    assert ta.time_conflicts(test2) == 5, "Incorrect time conflicts score for test 2"
    assert ta.time_conflicts(test3) == 2, "Incorrect time conflicts score for test 3"


def test_undersupport(cases):
    """
        Unit tests for undersupport function
    """
    test1, test2, test3 = cases
    assert ta.undersupport(test1) == 1, "Incorrect undersupport score for test 1"
    assert ta.undersupport(test2) == 0, "Incorrect undersupport score for test 2"
    assert ta.undersupport(test3) == 7, "Incorrect undersupport score for test 3"


def test_unwilling(cases):
    """
        Unit tests for unwilling function
    """
    test1, test2, test3 = cases
    assert ta.unwilling(test1) == 53, "Incorrect unwilling score for test 1"
    assert ta.unwilling(test2) == 58, "Incorrect unwilling score for test 2"
    assert ta.unwilling(test3) == 43, "Incorrect unwilling score for test 3"


def test_unpreferred(cases):
    """
        Unit tests for unpreferred function
    """
    test1, test2, test3 = cases
    assert ta.unpreferred(test1) == 15, "Incorrect unpreferred score for test 1"
    assert ta.unpreferred(test2) == 19, "Incorrect unpreferred score for test 2"
    assert ta.unpreferred(test3) == 10, "Incorrect unpreferred score for test 3"
