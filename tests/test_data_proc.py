#!/usr/bin/env python3
"""
Unit and regression test for the cericeproject_gradecalculator package.
"""

# Import package, test suite, and other packages as needed
import errno
import os
import sys
import unittest
from contextlib import contextmanager
from io import StringIO
import numpy as np
import logging
from cericeproject_gradecalculator.data_proc import main, cal_grades

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
DISABLE_REMOVE = logger.isEnabledFor(logging.DEBUG)

CURRENT_DIR = os.path.dirname(__file__)
MAIN_DIR = os.path.join(CURRENT_DIR, '..')
TEST_DATA_DIR = os.path.join(CURRENT_DIR, 'data_proc')
PROJ_DIR = os.path.join(MAIN_DIR, 'cericeproject_gradecalculator')
DATA_DIR = os.path.join(PROJ_DIR, 'data')
SAMPLE_ROSTER_DATA_FILE_LOC = os.path.join(DATA_DIR, 'ClassRoster.csv')
SAMPLE_GRADE_DATA_FILE_LOC = os.path.join(DATA_DIR, 'ClassGradebook.csv')

# Assumes running tests from the main directory
DEF_CSV_OUT = os.path.join(MAIN_DIR, 'ClassGradebook_letter.csv')


def silent_remove(filename, disable=False):
    """
    Removes the target file name, catching and ignoring errors that indicate that the
    file does not exist.

    @param filename: The file to remove.
    @param disable: boolean to flag if want to disable removal
    """
    if not disable:
        try:
            os.remove(filename)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

class TestMain(unittest.TestCase):
    # These tests make sure that the program can run properly from main
    def testSampleData(self):
        # Checks that runs with defaults and that files are created
        test_input = ["-r", SAMPLE_ROSTER_DATA_FILE_LOC, "-g", SAMPLE_GRADE_DATA_FILE_LOC]
        try:
            if logger.isEnabledFor(logging.DEBUG):
                main(test_input)
            # checks that the expected message is sent to standard out
            with capture_stdout(main, test_input) as output:
                self.assertTrue(".csv" in output)

            self.assertTrue(os.path.isfile("ClassGradebook_letter.csv"))
        finally:
            silent_remove(DEF_CSV_OUT, disable=DISABLE_REMOVE)

class TestMainFailWell(unittest.TestCase):
    def testMissingFile_r(self):
        test_input = ["-r", "ghost.txt", "-g", SAMPLE_GRADE_DATA_FILE_LOC]
        if logger.isEnabledFor(logging.DEBUG):
            main(test_input)
        with capture_stderr(main, test_input) as output:
            self.assertTrue("ghost.txt" in output)

    def testMissingFile_g(self):
        test_input = ["-r", SAMPLE_ROSTER_DATA_FILE_LOC, "-g", "ghost.txt"]
        if logger.isEnabledFor(logging.DEBUG):
            main(test_input)
        with capture_stderr(main, test_input) as output:
            self.assertTrue("ghost.txt" in output)

    def testDataDiffNumCols(self):
        input_file = os.path.join(TEST_DATA_DIR, "sample_Gradebook_MissingColumns.csv")
        test_input = ["-r", SAMPLE_ROSTER_DATA_FILE_LOC, "-g", input_file]
        if logger.isEnabledFor(logging.DEBUG):
            main(test_input)
        with capture_stderr(main, test_input) as output:
            self.assertTrue("Wrong number of columns" in output)

class TestDataAnalysis(unittest.TestCase):
    def testSampleData(self):
        # Tests that the np array generated by the data_analysis function matches saved expected results
        grade_data = np.loadtxt(fname=SAMPLE_GRADE_DATA_FILE_LOC, delimiter=',')
        analysis_results_num, analysis_results_letter = cal_grades(grade_data)
        expected_results_num = np.loadtxt(fname=os.path.join(TEST_DATA_DIR, "sample1_num_results.csv"), delimiter=',')
        expected_results_letter = np.loadtxt(fname=os.path.join(TEST_DATA_DIR, "sample1_letter_results.csv"), dtype=np.str, delimiter=',')
        self.assertTrue(np.allclose(expected_results_num, analysis_results_num))
        self.assertTrue(analysis_results_letter in expected_results_letter)

    def testSampleData2(self):
        # A second check, with slightly different values, of the data_analysis function
        grade_data = np.loadtxt(fname=os.path.join(TEST_DATA_DIR, "ClassGradebook2.csv"), delimiter=',')
        analysis_results_num, analysis_results_letter = cal_grades(grade_data)
        expected_results_num = np.loadtxt(fname=os.path.join(TEST_DATA_DIR, "sample2_num_results.csv"), delimiter=',')
        expected_results_letter = np.loadtxt(fname=os.path.join(TEST_DATA_DIR, "sample2_letter_results.csv"), dtype=np.str, delimiter=',')
        self.assertTrue(np.allclose(expected_results_num, analysis_results_num))
        self.assertTrue(analysis_results_letter in expected_results_letter)


# Utility functions

# From http://schinckel.net/2013/04/15/capture-and-test-sys.stdout-sys.stderr-in-unittest.testcase/
@contextmanager
def capture_stdout(command, *args, **kwargs):
    # pycharm doesn't know six very well, so ignore the false warning
    # noinspection PyCallingNonCallable
    out, sys.stdout = sys.stdout, StringIO()
    command(*args, **kwargs)
    sys.stdout.seek(0)
    yield sys.stdout.read()
    sys.stdout = out

@contextmanager
def capture_stderr(command, *args, **kwargs):
    # pycharm doesn't know six very well, so ignore the false warning
    # noinspection PyCallingNonCallable
    err, sys.stderr = sys.stderr, StringIO()
    command(*args, **kwargs)
    sys.stderr.seek(0)
    yield sys.stderr.read()
    sys.stderr = err

