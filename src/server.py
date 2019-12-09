"""SGBD Server
"""

import sqlite3
import socket 
import datetime 
import time 
import utils
# from session import ClientSession 

SERVER_DATABASE = 'fastdb_info.db'
LOG_FILE = 'log.txt'

class FDB_Server:
    def __init__(self, host:str, port:int):
        self._host = host 
        self._port = port 
        self._db_conn = None
        self._socket = None 
        self._logger = utils.Logger(LOG_FILE) 
        self._nb_clients = 0
        self.tables = {'users': 'users', 'databases': 'databases'}

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port 

    def is_user_exist(self, username:str) -> bool:
        """Checks if the given username is allowed to connect server."""
        if self._db_conn:
            with self._db_conn:
                cursor = self._db_conn.cursor()
                cursor.execute('SELECT username FROM %s WHERE username=?' % 
                    self.tables['users'], (username,))
                return cursor.fetchone() is not None 
        return False

    def is_database_exist(self, dbname:str) -> bool:
        """Checks if the selected database exists."""
        if self._db_conn:
            with self._db_conn:
                cursor = self._db_conn.cursor()
                cursor.execute('SELECT dbname FROM %s WHERE dbname=?' % 
                    self.tables['databases'], (dbname,))
                return cursor.fetchone() is not None 
        return False 

    def insert_new_user(self, username:str):
        pass

    def delete_user(self, username:str):
        pass

    def insert_new_database(self, dbname:str):
        pass

    def delete_database_entry(self, dbname:str):
        pass 

    def create_database(self):
        """Create server database info if not already exists."""
        if not self._db_conn:
            self.connect_to_database()

        with self._db_conn:
            sql = """
                CREATE TABLE %(users)s (
                    id INT NOT NULL AUTOINCREMENT PRIMARY KEY, 
                    username VARCHAR(50) NOT NULL UNIQUE
                );
                CREATE TABLE %(databases)s (
                    id INT NOT NULL AUTOICREMENT PRIMARY KEY,
                    dbname VARCHAR(50) NOT NULL UNIQUE
                );""" % self.tables 
            self._db_conn.execute(sql)
            self._db_conn.commit()

    def connect_to_database(self):
        """Connect to the server database information."""
        self._db_conn = sqlite3.connect(SERVER_DATABASE) 

    def close_database_conn(self):
        """Close connection to the server database."""
        if self._db_conn:
            self._db_conn.close()
            self._db_conn = None 

    def create_socket(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((self.host, self.port)) 

    def close_socket(self):
        if self._socket:
            self._socket.close()
            self._socket = None  

    def log(self, msg:str, output=True):
        """Write status in the log file and stdout if output=True."""
        self._logger.write_line(msg)
        if output:
            print(msg) 

    def __del__(self):
        self.close_database_conn()
        self.close_socket()

    def run(self):
        """Main server activity."""
        try:
            self.create_socket()
            self.connect_to_database()
            self._logger.open_file("a")

            now = datetime.datetime.now()
            self.log("\n     ======== %s ========\n" % now.strftime('%d-%m-%Y'))
            self.log("[%s] Server started successfully\n" % now.strftime('%H:%M:%S'))

            while True:
                self._socket.listen()
                conn, address = self._socket.accept()
                self._nb_clients += 1
                self.log("[%s] New Client connected at %s\n" % 
                    (time.strftime('%H:%M:%S'), str(address)))
                # session = ClientSession(conn, self)
                # session.start_session()
        except KeyboardInterrupt:
            self.log("Total today clients: %d\n" % self._nb_clients)
            self.log("Shutting down server...\n")
        except (sqlite3.Error, socket.error) as e:
            print(e)
        finally:
            self._logger.close_file()
            self.close_database_conn()
            self.close_socket()

if __name__ == '__main__':
    import sys
    args = utils.parse_server_args(sys.argv[1:])
    if utils.is_valid_ip(args.host):
        server = FDB_Server(args.host, args.port)
        server.run()
    else:
        print("Error: Invalid IP address")
