"""This module tests the 'utils' module (utils.py)
"""

import unittest 
import os

import utils

def get_tests() -> tuple:
    """Returns all test classes."""
    return TestSQL_Checker, TestLogger

class TestSQL_Checker(unittest.TestCase):
    def _create_checker(self):
        return utils.SQL_Checker()

    def test_checker(self):
        checker = self._create_checker()
        sql = "SELECT * FROM users;"
        checker.update(sql)
        # test : is_valid_statement
        self.assertTrue(checker.is_valid_statement(), 
            'Valid SQL Statement')
        # test : sql_to_bytes
        self.assertEqual(checker.sql_to_bytes(), f"{sql}".encode("utf-8"), 
            'Two bytes values are not equal')


class TestLogger(unittest.TestCase):
    def test_logger(self):
        message = "hello everyone"
        test_file = 'test-file.test'
        # Creating instance
        logger = utils.Logger(test_file)
        # Testing opening operation
        logger.open_file('w')
        self.assertTrue(logger.opened)
        # Testing writing operation
        logger.write_line(message)
        # Testing closing operation
        logger.close_file()
        self.assertFalse(logger.opened)

        # More...Reading written line
        logger.open_file('r')
        f = logger._file 
        self.assertEqual(f.read(), message)
        logger.close_file()
        self.assertFalse(logger.opened)

        # Remove created file
        os.remove(os.path.realpath(test_file))
