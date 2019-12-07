"""This module tests the 'utils' module (utils.py)
"""

import unittest 
import utils

def get_tests():
    """Returns all test classes."""
    return TestSQL_Checker,

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
            'Two bytes values are equal')
