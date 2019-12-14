"""Utility module

This module contains:
    -> SQL_Checker (class) : used to check if a given SQL statement 
                             is valid.
    -> Logger (class)      : output status 
    -> TextTable (class)   : output data into a table
    -> is_valid_ip         : check if a given IP address is valid
    -> hash_password       : hash a password 
    -> parse_client_args   : parse command line client arguments
    -> parse_server_args   : parse command line server arguments
"""

import sqlite3
import argparse
import hashlib 
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


class TextTable:
    """Represent data as a table."""
    def __init__(self):
        self._array = []

    def clear(self):
        """Clear the underlying array."""
        self._array.clear()

    def header(self, head:list):
        """Sets the table header."""
        if self._array:
            self._array.insert(0, head)
        else:
            self._array.append(head)

    def add_row(self, row):
        """Add row to the underlying array."""
        if not isinstance(row, (list, tuple)):
            return 
        if self._array and len(row) != len(self._array[0]):
            return 
        self._array.append(list(row))

    def add_rows(self, rows:list):
        """Add multiple rows at the same time."""
        for row in rows: 
            self.add_row(row)

    def print(self):
        """Print the result."""
        print(self._format())

    def __str__(self):
        return self._format()

    def _format(self) -> str:
        """Format the array to display it properly."""
        def get_fields_size() -> list:
            """Compute maximum string length for each column."""
            if not self._array:
                return []
            sub_arr_length = len(self._array[0])
            sizes = [0] * sub_arr_length
            for i in range(len(self._array)):
                for j in range(sub_arr_length):
                    sizes[j] = max(sizes[j], len(str(self._array[i][j])))
            return sizes

        result = ""
        sizes = get_fields_size()
        sizes_len = len(sizes)
        if sizes:
            line = "\n+"
            for i in range(sizes_len):
                line += ('-' * (sizes[i] + 2)) + "+"
            result += line 
            for i in range(len(self._array)):
                    result += "\n| "
                    for j in range(sizes_len):
                        elt = str(self._array[i][j])
                        elt += " " * (sizes[j] - len(elt))
                        self._array[i][j] = elt 
                    result += " | ".join([elt for elt in self._array[i]])
                    result += " |" + line 
        return result


# Useful functions

def is_valid_ip(ip:str) -> bool:
    """Check if the given IP address is valid."""
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
