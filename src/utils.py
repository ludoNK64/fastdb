"""Utility module

This module contains:
    -> SQL_Checker (class) : used to check if a given SQL statement 
                             is valid.
    -> parse_client_args   : parse command line client arguments
    -> parse_server_args   : parse command line server arguments
"""

import sqlite3
import argparse
import re 

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


class Logger:
    """Used to output state/status in the file."""
    def __init__(self, filename:str):
        self._file = None 
        self._filename = filename

    @property
    def filename(self):
        return self._filename

    @property
    def opened(self):
        return self._file and not self._file.closed 

    def open_file(self, mode, encoding_="utf-8"):
        modes = ('r', 'a', 'w')
        if not mode in modes:
            raise ValueError("Invalid mode. Expected %s, got %s" %
                (str(modes), str(mode)))
        if not self._file:
            self._file = open(self.filename, mode, encoding=encoding_)
        else:
            raise RuntimeError("Logger file already opened")

    def close_file(self):
        if self._file:
            self._file.close()
            self._file = None

    def write_line(self, line:str):
        if self._file:
            self._file.write(line)

    def __del__(self):
        self.close_file()


# Useful functions

def is_valid_ip(ip:str) -> bool:
    """Check if the given IP address is in valid format."""
    return re.fullmatch(r'\d{1,3}?(\.\d{1,3}?){3}', ip) is not None

def hash_password(algo:str, data:str):
    """Hash a password with the given algorithm name."""
    if algo in {'sha1', 'sha224', 'sha256', 'sha384', 'sha512'}:
        return hashlib.new(algo, bytes(data, encoding="utf-8")).hexdigest()
    else:
        return None

def parse_client_args(args):
    """Parse client command line arguments.
    
    Returns given address, port and user.
    """
    parser = argparse.ArgumentParser()
    parser.usage = 'server.py --addr=ADDRESS --port=PORT --user=USERNAME'
    parser.add_argument('-a', '--addr', dest="host", required=True, type=str)
    parser.add_argument('-p', '--port', dest="port", required=True, type=int)
    parser.add_argument('-u', '--user', dest="user", required=True, type=str)
    return parser.parse_args()

def parse_server_args(args):
    """Parse server command line arguments.

    Returns given address and port.
    """
    parser = argparse.ArgumentParser()
    parser.usage = 'server.py --addr=ADDRESS --port=PORT'
    parser.add_argument('-a', '--addr', dest="host", required=True, type=str)
    parser.add_argument('-p', '--port', dest="port", required=True, type=int)
    return parser.parse_args() 
