#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
data_proc.py

Calculate student grades from cvs containing grades 
then recommend letter based on standard deviation, which is printed for each student based on a class roster cvs 

"""

import sys
from argparse import ArgumentParser
import numpy as np
import os

SUCCESS = 0
INVALID_DATA = 1
IO_Error = 2

DEFAULT_STUDENTS_FILE_NAME = 'ClassRoster.csv'
DEFAULT_GRADES_FILE_NAME = 'ClassGradebook.csv'

NUM_QUIZZES = 4
NUM_TESTS = 2
WEIGHT_QUIZZES = .4
WEIGHT_TESTS = .6


def warning(*objs):
    """Writes a message to stderr."""
    print("WARNING: ", *objs, file=sys.stderr)


def cal_grades(data_array):
    """
    Find the letter grade of students based off of assignment weight and standard deviation of the group

    Parameters
    ----------
    data_array : numpy array of student grades (one column per student)

    Returns
    -------
    final_lettter_grade : list of strings
        is a single row with a column for each student storing their letter grade as a string

    Important Constants
    ---------------
    NUM_QUIZZES : integer number of quizzes this term
    NUM_TESTS : integer number of tests this term
    WEIGHT_QUIZZES : decimal form of weight of quizzes (e.g. 50% weight is .5)
    WEIGHT_TESTS : decimal form of weight of tests (e.g. 50% weight is .5)
    """

    num_assignments, num_students = data_array.shape
    final_num_grade = np.zeros((1, num_students))
    final_letter_grade = []

    for x in range(0, num_students):
        # compute weighted score
        quiz_avg = np.sum(data_array[:NUM_QUIZZES, x])
        quiz_grade = quiz_avg * WEIGHT_QUIZZES
        test_avg = np.sum(data_array[(num_assignments - NUM_TESTS - 1):, x])
        test_grade = test_avg * WEIGHT_TESTS
        tot_grade = quiz_grade + test_grade

        # store weighted score
        final_num_grade[0, x] = tot_grade

    # find standard deviation of class
    dev = np.std(final_num_grade)
    mean = np.mean(final_num_grade)

    # assign letter grades based on stand deviation
    for x in range(0, num_students):
        if final_num_grade[0, x] > (mean + dev):
            final_letter_grade.append("A")
        elif final_num_grade[0, x] > mean:
            final_letter_grade.append("B")
        elif final_num_grade[0, x] > (mean - dev):
            final_letter_grade.append("C")
        else:
            final_letter_grade.append("F")

    return final_letter_grade


def parse_cmdline(argv):
    """
    Returns the parsed argument list and return code.
    `argv` is a list of arguments, or `None` for ``sys.argv[1:]``.
    """
    if argv is None:
        argv = sys.argv[1:]

    # initialize the parser object:
    parser = ArgumentParser(description="Reads in a two csv files (one name roster and one and grade file) and "
                                        "calculates the recommended grade based on standard deviation. Rows must of the"
                                        "same number of values and columns must have the same number of values ")

    parser.add_argument("-r", "--roster_csv_data_file", help="The location (directory and file name) of the csv file "
                                                             "with student names as strings",
                        default=DEFAULT_STUDENTS_FILE_NAME)

    parser.add_argument("-g", "--grade_csv_data_file", help="The location (directory and file name) of the csv file "
                                                            "with student grades as integers",
                        default=DEFAULT_GRADES_FILE_NAME)

    args = None
    try:
        args = parser.parse_args(argv)
        args.roster_csv_data = np.loadtxt(fname=args.roster_csv_data_file, dtype=np.str, delimiter=',')
        args.grades_csv_data = np.loadtxt(fname=args.grade_csv_data_file, dtype=np.float, delimiter=',')
    except IOError as e:
        warning("Problems reading file:", e)
        parser.print_help()
        return args, IO_Error
    except ValueError as e:
        warning("Read invalid data:", e)
        parser.print_help()
        return args, INVALID_DATA

    return args, SUCCESS


def main(argv=None):
    args, ret = parse_cmdline(argv)
    if ret != SUCCESS:
        return ret

    final_grades = cal_grades(args.grades_csv_data)

    # get the name of the input file without the directory it is in, if one was specified
    base_out_fname = os.path.basename(args.grade_csv_data_file)
    # get the first part of the file name (omit extension) and add the suffix
    base_out_fname = os.path.splitext(base_out_fname)[0] + '_letter'
    # add suffix and extension
    out_fname = base_out_fname + '.csv'
    # make array to save roster with letter grades
    sys.stdout = open(out_fname, "w+")
    num_students = len(args.roster_csv_data)
    for x in range(0, num_students):
        print("{}: {}".format(args.roster_csv_data[x], final_grades[x]))

    sys.stdout = sys.__stdout__
    print("Wrote file: {}".format(out_fname))

    return SUCCESS


if __name__ == "__main__":
    status = main()
    sys.exit(status)
