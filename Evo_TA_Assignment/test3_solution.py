import numpy as np
import pandas as pd
from collections import Counter
import copy
import functools

TEST3 = np.array(pd.read_csv('test3.csv', header=None))

class Solution3:

    def __init__(self, ta_df, practicum_df):
        # grid of w p u for ta preference for each section
        self.preferences = ta_df[[str(elem) for elem in (range(17))]].to_numpy()
        # grid of 0 and 1 for if a ta is assigned or not
        self.assignments = np.array([])
        # 1d array of min tas for each section
        self.min_tas = np.array(practicum_df.iloc[:, -2])
        # current ta count for each section
        self.current_tas_by_section = np.array([])
        # 1d array of section times
        self.times = np.array(practicum_df.iloc[:, 2])
        # 1d array of how many sections each ta is maxed out at
        self.max_requested = np.array(ta_df["max_assigned"])
        # current section count for each ta
        self.current_ta_assignments = np.array([])
        # array of dicts for how many p, w, u sections each ta is assigned
        self.preference_assignments = np.array([])
        # array of dicts of p w u keys and list of assigned times values
        self.preference_times_assigned = np.array([])

    def elem_to_time(self, elem):
        """
                gets section time of input element
                :param elem: list with format [<preference>, <index>]
                :return: string, corresponding section time
        """
        return self.times[elem[1]]

    def filter_preference(self, elem, preference):
        """
                checks if preference of elem is equal to input preference
                :param elem: list, with format [<preference>, <index>]
                :param preference: string, either P, W, U
                :return: boolean, True if equal, False if not
        """
        return elem[0] == preference

    def filter_iterable_preference(self, iterable, preference):
        """
                filters an iterable for given preference
                :param iterable: 2d array, list of elems
                :param preference: string, either P, W, U
                :return: 2d array, filtered iterable
        """
        return filter(lambda elem: self.filter_preference(elem, preference), iterable)

    def map_elems_to_time(self, elems):
        """
                maps section elems to section times
                :param elems: 2d array, list of elems
                :return: 1d array, contains section times
        """
        return np.array(list(map(self.elem_to_time, elems)))

    def convert_ta_data_to_time(self, ta_data, preference):
        """
        filters section times for a ta for one single preference
                :param ta_data: 2d array, list of elems
                :param preference: string, either P, W, U
                :return: 1d array, contains section times of a single (the filter) preference
        """
        filtered_ta_data = self.filter_iterable_preference(ta_data, preference)
        return np.array(list(self.map_elems_to_time(filtered_ta_data)))

    def add_to_dict(self, dict, pair):
        """
                adds elem pair to dictionary
                :param dict: dictionary
                :param pair: tuple, (<preference>, <index>)
                :return: updated dictionary that contains pair
        """
        dict.update({pair[0]: pair[1]})
        return dict

    def convert_ta_data(self, ta_data, prefers):
        """
                converts TA preferences into dictionary with section times
                :param ta_data: 2d array, list of elems
                :param prefers: list, contains preferences
                :return: dictionary, keys are preferences, values are arrays of section times
                """
        # gets list of 1d arrays containing preference section times
        preference_time_slots = np.array(list(map(lambda preference: self.convert_ta_data_to_time(ta_data, preference),
                                                  prefers)), dtype=object)
        # {w: [time_slots], u: [time_slots], p: [time_slots]}
        return functools.reduce(self.add_to_dict, zip(prefers, preference_time_slots), {})

    def calculate_preference_time_assignments(self):
        """
        updates preference_times_assigned state to an array of dictionaries containing preference section time info
        """
        # [[[w/u/p, 0], [w/u/p, 1]]]
        assigned_time_preferences = [[[self.preferences[j][i], i] for i in range(len(self.assignments[j]))] for j in
                                     range(len(self.preferences))]
        prefers = ["W", "U", "P"]
        # [{w:[11:45, 3:25] , p: , u: }]
        self.preference_times_assigned = np.array(list(map(lambda ta_data: self.convert_ta_data(ta_data, prefers),
                                                           assigned_time_preferences)))

    def calculate_preference_assignments(self):
        """
        updates preference_assignments state to a list of dictionaries
        with keys as preferences and values as number of sections assigned
        """
        assignment_preferences = [[self.preferences[j][i] for i in range(len(self.preferences[j]))
                                   if self.assignments[j][i] == 1] for j in range(len(self.preferences))]
        self.preference_assignments = [Counter(assignment_preferences[j]) for j in
                                       range(len(assignment_preferences))]

    def populate_assignments(self):
        self.assignments = TEST3

    def calculate_current_tas_section(self):
        """
        updates current_tas_by_section state to list of number of TAs assigned to each section
        """
        self.current_tas_by_section = [sum(x) for x in zip(*self.assignments)]

    def calculate_current_tas(self):
        """
        updates current_ta_assignment state to list of number of assigned sections for each TA
        """
        self.current_ta_assignments = [sum(row) for row in self.assignments]

    def __str__(self):
        """
        prints assignment array
        """
        rslt = ''
        for i in range(len(self.assignments)):
            rslt += '\n'
            rslt += ' '.join(str(elem) for elem in self.assignments[i])
        return rslt
