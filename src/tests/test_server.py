"""Module used to test server program.
"""

import unittest
import os

import server

def get_tests() -> tuple:
    return TestServer,

class TestServer(unittest.TestCase):
    def test_server(self):
        """Tests all server functionalities except run() method.

        This also tests Logger class at the same time because server
        uses it.
        """
        _server = server.FDB_Server(server.DEFAULT_HOST, server.DEFAULT_PORT)
        # 1. Database operations
        # Connection to database
        if os.path.exists(server.SERVER_DATABASE):
            # Remove file if already exists to avoid issues
            os.remove(os.path.realpath(server.SERVER_DATABASE))
            
        _server.connect_to_database()
        self.assertIsNotNone(_server.db_conn)

        # Testing creation of the specific tables
        _server.create_tables()

        # Check if 'ludo' user exists
        self.assertFalse(_server.is_user_exist('ludo', 'ludo'))
        # Check if 'tweet' table exists
        self.assertFalse(_server.is_database_exist('tweet'))

        # Close database connection
        _server.close_db_connection()
        self.assertIsNone(_server.db_conn)

        # 2. File output operations
        # Opening file
        _server.logger.open_file('w')
        self.assertTrue(_server.logger.opened)

        # Testing writing
        _server.log("hello", False)
        # Close file
        _server.logger.close_file()
        self.assertFalse(_server.logger.opened)

        # Read written line
        with open(server.LOG_FILE, 'r') as f:
            self.assertEqual(f.read(), "hello")

        # 3. Socket creation and destruction
        _server.create_socket()
        self.assertIsNotNone(_server.socket)
        _server.close_socket()
        self.assertIsNone(_server.socket)
