"""Client - server session manager.
"""

import threading 
import sqlite3
import time
import re 

import utils


DATA_SEPARATOR = '$'
ACCESS_GRANTED = b'ok'
ACCESS_DENIED  = b'access denied'

# select_regex = re.compile(
#     r"^select (\* | (?P<field>\w+,\s?)*?)?? (\w+) from \w+ .+?;$", 
#     re.IGNORECASE | re.VERBOSE | re.DOTALL)
select_regex = re.compile(r"^select", re.IGNORECASE | re.VERBOSE)


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
        self._client_connected = False

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
                            cursor = self.server.db_conn.cursor()
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
                                self.server.db_conn.commit()
                                message = "\nQuery done %s\n" % time_passed
                    except sqlite3.Error as e:
                        message = f"\nERROR: {str(e)}\n"
                        self.server.db_conn.rollback()
                    try:
                        self.conn.sendall(message.encode("utf-8"))
                    except BrokenPipeError:
                        break 
            self.conn.close()
