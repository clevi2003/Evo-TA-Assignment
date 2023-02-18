"""
TA_allocation.py: assigns TA to sections based on fitness criteria.
"""

import random as rnd
import evo
import pandas as pd
from collections import Counter
from solution import Solution
import numpy as np
import csv


def overallocation(solution):
    """
    calculates overallocation penalty score for given solution
    :param solution: Solution object
    :return: int, overallocation penalty score, 1 point for each section overassigned for each TA
    """
    solution.calculate_current_tas()
    current_assignments = solution.current_ta_assignments
    max_assignments = solution.max_requested
    # sums overallocations for each TA
    penalty = sum([current_assignments[i] - max_assignments[i] for i in range(len(max_assignments)) if
                   current_assignments[i] - max_assignments[i] > 0])
    return penalty


def time_conflicts(solution):
    """
    calculates time conflict penalty score
    :param solution: Solution object
    :return: conflicts: int, time conflict penalty score, 1 point for each TA who has a conflict
    """
    # make list of lists for each ta with indices of their assigned sections
    assigned_indices = [[i for i in range(len(solution.assignments[j])) if solution.assignments[j][i] == 1] for j in
                        range(len(solution.assignments))]
    # make list of lists for each ta with times of their assigned sections
    assigned_times = [[solution.times[i] for i in assigned_indices[j]] for j in range(len(assigned_indices))]
    # sum list of 1s for each time conflict
    conflicts = sum([1 for elem in assigned_times if len(set(elem)) < len(elem)])
    return conflicts


def undersupport(solution):
    """
    calculates undersupport penalty score for given solution
    :param solution: Solution object
    :return: penalty: int, undersupport penalty score, 1 point for each TA below minimum requirement for each section
    """
    current_assignments = solution.current_tas_by_section
    min_assignments = solution.min_tas
    penalty = sum([min_assignments[i] - current_assignments[i] for i in range(len(min_assignments)) if
                   (min_assignments[i] - current_assignments[i]) > 0])
    return penalty


def unwilling(solution):
    """
    calculates unwilling penalty score for given solution
    :param solution: Solution object
    :return: penalty: int, unwilling penalty score, 1 point for each section assigned to an unwilling TA
    """
    preferences = solution.preferences
    assignments = solution.assignments
    # sums number of sections assigned to an unwilling TA
    penalty = sum(
        [sum([1 for i in range(len(assignments[j])) if assignments[j][i] == 1 and preferences[j][i] == "U"]) for
         j in range(len(assignments))])
    return penalty


def unpreferred(solution):
    """
    calculates unpreferred penalty score for given solution
    :param solution: Solution object
    :return: penalty: int, unpreferred penalty score, 1 point for each section assigned to an unpreferred (willing) TA
    """
    preferences = solution.preferences
    assignments = solution.assignments
    # sums number of sections assigned to an unpreferred (willing) TA
    penalty = sum(
        [sum([1 for i in range(len(assignments[j])) if assignments[j][i] == 1 and preferences[j][i] == "W"]) for
         j in range(len(assignments))])
    return penalty


def time_conflict_remover(solutions):
    """
    removes time conflicts from randomly chosen TA by unassigning from more supported section
    :param solutions: list, contains Solution objects
    :return: solution: updated solution
    """
    solution = solutions[0]

    # chooses random TA
    fix_num = rnd.randint(0, len(solution.assignments) - 1)
    fix_row = solution.assignments[fix_num]
    # gets assigned section and section times indices for TA
    assigned_indices = [i if fix_row[i] == 1 else None for i in range(len(fix_row))]
    assigned_times = [solution.times[idx] if idx is not None else None for idx in assigned_indices]

    # frequency dictionary for each time slot that TA is assigned to
    time_counts = Counter(assigned_times)
    del time_counts[None]

    # checks if there is a time conflict
    if any(count > 1 for count in time_counts.values()):
        for key, value in time_counts.items():
            # finds time slot of conflict
            if value > 1:
                time = key
                break
        # gets section indices of conflicting sections
        time_indices = [index for index, value in enumerate(assigned_times) if value == time]
        # finds how supported each conflicting section is
        assign_diff_1 = solution.min_tas[time_indices[0]] - solution.current_tas_by_section[time_indices[0]]
        assign_diff_2 = solution.min_tas[time_indices[1]] - solution.current_tas_by_section[time_indices[1]]
        diffs = {assign_diff_1: time_indices[0], assign_diff_2: time_indices[1]}

        # finds index of more supported section
        time_idx = diffs[max(diffs.keys())]
        # unassigns TA from more supported section
        solution.assignments[fix_num][time_idx] = 0
        solution.current_tas_by_section[time_idx] -= 1
    return solution


def remove_overages(solution, fix_num, preference):
    """
    unassigns given TA from sections of given preference, if TA is overallocated
    :param solution: Solution object
    :param fix_num: int, index of a TA
    :param preference: string, P, W, or U
    :return: solution: updated Solution object
    """
    diff = solution.current_ta_assignments[fix_num] - solution.max_requested[fix_num]

    if diff <= 0:
        return solution
    # gets assigned times of certain preference for TA
    current_ta_preference_times = solution.preference_times_assigned[fix_num][preference]
    # gets assigned times that will be removed
    current_ta_preference_removals = current_ta_preference_times[: min(diff, len(current_ta_preference_times))]
    # gets section indices of times that will be removed
    remove_indices = map(lambda time_slot: np.where(time_slot == solution.times), current_ta_preference_removals)
    # unassigns TA from sections
    for idx in remove_indices:
        solution.assignments[fix_num][idx] = 0
    return solution


def reduce_overallocation(solutions):
    """
    removes overallocations for all TAs
    :param solutions: list, contains Solution objects
    :return: solution: Solution object
    """
    solution = solutions[0]
    for i in range(len(solution.max_requested)):
        solution = remove_overages(solution, i, "U")
        solution = remove_overages(solution, i, "W")
        solution = remove_overages(solution, i, "P")
    solution.calculate_preference_time_assignments()
    solution.calculate_preference_assignments()
    solution.calculate_current_tas_section()
    solution.calculate_current_tas()
    return solution

def add_support(solutions):
    """

    :param solutions:
    :return:
    """
    solution = solutions[0]
    # gets section indices of undersupported sections
    indices = [i for i in range(len(solution.min_tas)) if solution.min_tas[i] > solution.current_tas_by_section[i]]
    for idx in indices:
        # gets assignments and preferences of a certain section
        fix_assignments = np.array([solution.assignments[i][idx] for i in range(len(solution.assignments))])
        fix_preferences = np.array([solution.preferences[i][idx] for i in range(len(solution.assignments))])
        for i in range(len(fix_assignments)):
            # if a TA is not assigned to the section and not unwilling, and is not overallocated
            # then the TA gets assigned
            if fix_assignments[i] == 0 and fix_preferences[i] != "U":
                if solution.max_requested[i] > solution.current_ta_assignments[i]:
                    solution.assignments[i][idx] = 1

    # updates states
    solution.calculate_preference_time_assignments()
    solution.calculate_preference_assignments()
    solution.calculate_current_tas_section()
    solution.calculate_current_tas()
    return solution



def main():
    allocation = evo.Environment()
    # reads csv data
    ta = pd.read_csv("tas.csv").drop(["name"], axis=1)
    practicums = pd.read_csv("sections.csv")[["section", "min_ta", "daytime"]]

    # sets default assignment solution
    default_solution = Solution(ta, practicums)
    default_solution.populate_assignments()
    default_solution.calculate_preference_assignments()
    default_solution.calculate_current_tas()
    default_solution.calculate_current_tas_section()
    default_solution.calculate_preference_time_assignments()

    # adds fitness criteria and agents
    allocation.add_fitness_criteria("overallocation", overallocation)
    allocation.add_fitness_criteria("time conflicts", time_conflicts)
    allocation.add_fitness_criteria("undersupport", undersupport)
    allocation.add_fitness_criteria("unwilling", unwilling)
    allocation.add_fitness_criteria("unpreferred", unpreferred)

    allocation.add_agent("overallocation reducer", reduce_overallocation)
    allocation.add_agent("time conflict remover", time_conflict_remover)
    allocation.add_agent("support adder", add_support)

    # adds default solution to Environment object
    allocation.add_solution(default_solution)

    # evolves solutions
    allocation.evolve(n=1000000, dom=20)

    # writes csv file to contain all solutions and their fitness scores
    with open("results.csv","w") as infile:
        header = ["group name", "overallocation", "time conflicts", "undersupport", "unwilling", "unpreferred"]
        writer = csv.writer(infile)
        writer.writerow(header)
        for key in allocation.pop:
            row = ["CCG"]
            for score in key:
                row.append(score[1])
            writer.writerow(row)
    print(allocation.best_solution().assignments)


if __name__ == "__main__":
    main()
