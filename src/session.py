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

select_regex = re.compile(
    r"^select (\* | (?P<field>\w+,\s?)*?)?? (\w+) from \w+ .+?;$", 
    re.IGNORECASE | re.VERBOSE | re.DOTALL)


def _is_select_statement(sql:str) -> bool:
    """Check if the SQL command is a SELECT statement."""
    select_regex.fullmatch(sql) is not None

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
                            start = time.time()
                            result = self.server.db_conn.execute(sql)
                            end = time.time()
                            elapsed_time = end - start
                            message = "\nQuery done in %.2fs\n" % elapsed_time
                            if _is_select_statement(sql):
                                table.clear()
                                table.header(_extract_fields(sql))
                                table.add_rows(result)
                                message = f"\n{str(table)} {message}"
                    except sqlite3.error as e:
                        message = e
                    self.conn.sendall(message.encode("utf-8"))
            self.conn.close()
