"""Client - server session manager.
"""

import threading 
import re 

DATA_SEPARATOR = '$'
ACCESS_GRANTED = b'ok'
ACCESS_DENIED  = b'access denied'

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
            if self.server.is_user_exist(*data.split(DATA_SEPARATOR)):
                self.conn.send(ACCESS_GRANTED)
                self._client_connected = True
            else:
                self.conn.send(ACCESS_DENIED)
            # 2. main activity
            if self._client_connected:
                pass 
