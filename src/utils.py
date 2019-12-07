"""Utility module

This module contains:
    -> SQL_Checker (class) : used to check if a given SQL statement 
                             is valid.
    -> parse_client_args   : parse command line client arguments
    -> parse_server_args   : parse command line server arguments
"""

import sqlite3
import argparse

class SQL_Checker:
    """This is used to check if an SQL query is valid."""
    def __init__(self):
        """Constructor"""
        self._query = ""

    @property
    def query(self):
        return self._query
    
    def is_valid_statement(self) -> bool:
        """"""
        return sqlite3.complete_statement(self.query)

    def update(self, new_query):
        """Sets the underlying query statement."""
        self._query = str(new_query)

    def sql_to_bytes(self) -> bytes:
        """Returns the underlying query statement in bytes."""
        return bytes(self.query, encoding="utf-8")

# Useful functions

def parse_client_args(args):
    """Parse client command line arguments.
    
    Returns given address and port as a tuple.
    """
    pass 

def parse_server_args(args):
    """Parse server command line arguments.

    Returns given address and port as a tuple.
    """
    pass 
