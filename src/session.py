"""Client - server session manager.
"""

import threading 
import sqlite3
import time
import re 
import os

import utils
from config import *


# select_regex = re.compile(
#     r"^select (\* | (?P<field>\w+,\s?)*?)?? (\w+) from \w+ .+?;$", 
#     re.IGNORECASE | re.VERBOSE | re.DOTALL)
select_regex = re.compile(r"^SELECT", re.IGNORECASE | re.VERBOSE)


def _is_select_statement(sql:str) -> bool:
    """Check if the SQL command is a SELECT statement."""
    return select_regex.search(sql) is not None

def _extract_fields(sql:str) -> list:
    """Extracts fields of a SELECT SQL statement."""
    matches = select_regex.findall(sql)
    fields = [match for match in matches]
    return fields


class ClientSession(threading.Thread):
    def __init__(self, server, conn):
        super().__init__()
        self.server = server 
        self.conn = conn 
        self.db_conn = None
        self._client_connected = False
        self._old_dbname = ''

    def _connect_db(self, dbname:str):
        """Connects to the database selected by the user."""
        self._close_db_connection()
        self.db_conn = sqlite3.connect(DATABASES_DIR + dbname  + DATABASE_EXT)

    def _close_db_connection(self):
        if self.db_conn:
            self.db_conn.close()
            self.db_conn = None

    def _handle_statement(self, key, stmt):
        """Handles user and database statements defined in config.py"""
        msg = ''
        if key in STATEMENTS.keys():
            match = re.fullmatch(STATEMENTS[key], stmt, re.IGNORECASE | re.VERBOSE)
            if match:
                if key in {'create-database', 'use-database', 'drop-database'}:
                    dbname = match.group('dbname')
                    if key == 'create-database':
                        try:
                            self.server.insert_new_database(dbname)
                            msg = SUCCESS['database-created'] % dbname 
                        except sqlite3.IntegrityError:
                            raise sqlite3.Error(ERROR['database-exists'] % dbname)
                    elif key == 'use-database':
                        if not self.server.is_database_exist(dbname):
                            raise sqlite3.Error(ERROR['unknown-database'] % dbname)
                        else:
                            if self._old_dbname != dbname:
                                self._old_dbname = dbname
                                self._connect_db(dbname)
                                msg = SUCCESS['database-changed']
                    elif key == 'drop-database':
                        if not self.server.is_database_exist(dbname):
                            raise sqlite3.Error(ERROR['no-database'] % dbname)
                        else:
                            self.server.delete_database_entry(dbname)
                            path = DATABASES_DIR + dbname + DATABASE_EXT
                            if os.path.exists(path):
                                os.remove(os.path.relpath(path))
                            msg = SUCCESS['database-deleted'] % dbname
                elif key in {'add-user', 'delete-user'}:
                    username = match.group('username')
                    if key == 'add-user':
                        password = match.group('pass')
                        try: 
                            self.server.insert_new_user(username, password)
                            msg = SUCCESS['user-added'] % username 
                        except: raise 
                    else: # delete-user
                        self.server.delete_user(username)
                        msg = SUCCESS['user-deleted'] % username
                elif key == 'show-databases':
                    table = utils.TextTable()
                    table.add_rows(self.server.select_databases())
                    msg = str(table)
        msg = "\n%s\n" % msg if len(msg) > 0 else " "
        return msg

    def run(self):
        """Handle client - server session."""
        with self.conn:
            # 1. client's connection (login)
            data = self.conn.recv(1024)
            data = data.decode(encoding="utf-8")
            if data:
                if self.server.is_user_exist(*data.split(DATA_SEPARATOR)):
                    self.conn.send(ACCESS_GRANTED)
                    self._client_connected = True
                else:
                    self.conn.send(ACCESS_DENIED)
            # 2. main activity
            if self._client_connected:
                table = utils.TextTable()
                message = ''
                while self.conn:
                    try:
                        sql = self.conn.recv(1024)
                        sql = sql.decode(encoding="utf-8")
                        if sql:
                            # Try to execute custom statements (on user, database)
                            parts = sql.split(DATA_SEPARATOR)
                            if len(parts) == 2:
                                message = self._handle_statement(*parts)
                            else:
                                if not self.db_conn:
                                    raise sqlite3.Error(ERROR['no-database-seleted'])
                                cursor = self.db_conn.cursor()
                                start = time.time()
                                cursor.execute(sql)
                                end = time.time()
                                elapsed_time = end - start
                                time_passed = "(%.3f sec)" % elapsed_time
                                if _is_select_statement(sql):
                                    table.clear()
                                    results = cursor.fetchall()
                                    # table.header(_extract_fields(sql))
                                    if results:
                                        table.add_rows(results)
                                        message = "%s\n %d rows in set %s\n" % (
                                            str(table), len(results), time_passed)
                                    else:
                                        message = f"\nEmpty set {time_passed}\n"
                                else:
                                    self.db_conn.commit()
                                    message = "\nQuery done %s\n" % time_passed
                    except sqlite3.Error as e:
                        message = f"\nERROR: {str(e)}\n"
                        if self.db_conn:
                            self.db_conn.rollback()
                    try:
                        self.conn.sendall(message.encode("utf-8"))
                    except BrokenPipeError:
                        break
            self._close_db_connection()
            self.conn.close()
