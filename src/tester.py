"""Tests battery

This module runs all tests inside a given folder name.
Default folder is 'tests'.
"""

import unittest
import doctest
import os 
import sys
import warnings
from argparse import ArgumentParser


DEFAULT_TESTS_FOLDER = 'tests'

def main(directory=DEFAULT_TESTS_FOLDER):
    if not os.path.exists(directory):
        print("No directory named '%s'" % directory)
        sys.exit(1)
    modules = []
    module_paths = []
    # find all files
    for dirpath, dirs, filenames in os.walk(directory):
        del dirs
        for filename in filenames:
            if filename.startswith("test") and filename.endswith(".py"):
                module_paths.append(os.path.join(dirpath, filename))
                modules.append(filename[:-3]) # remove .py extension

    sys.path.append(directory)
    # import each module
    suite = unittest.TestSuite()
    for module in modules:
        m = __import__(module)
        if hasattr(m, 'get_tests'):
            test_cases = m.get_tests()
            for test_case in test_cases:
                suite.addTest(unittest.makeSuite(test_case))
        else:
            warnings.warn("'%s' module has no function 'get_tests'" % module)

    nb_test_cases = suite.countTestCases()
    if nb_test_cases == 0:
        print("No test.")
        sys.exit(1)
    print("Total modules found : %d" % nb_test_cases)
    
    campaign = unittest.TextTestRunner(verbosity=2)
    campaign.run(suite)
    sys.path.remove(directory)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.usage = 'python3 tester.py --dir=FOLDER'
    parser.add_argument('-d', '--dir', dest='directory', required=True)
    args = parser.parse_args(sys.argv[1:])
    main(args.directory)
