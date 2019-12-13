#!/usr/bin/python3

"""SGBD Server
"""

import sqlite3
import socket 
import datetime 
import time 

import utils
from session import ClientSession 

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 5100
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

    @property
    def logger(self):
        return self._logger

    @property
    def socket(self):
        return self._socket

    @property
    def db_conn(self):
        return self._db_conn 

    def is_user_exist(self, username:str, password:str) -> bool:
        """Checks if the given username is allowed to connect server."""
        if self._db_conn:
            with self._db_conn:
                cursor = self._db_conn.cursor()
                cursor.execute("""SELECT * FROM %s WHERE username=? AND
                    password=?""" % self.tables['users'], 
                    (username, utils.hash_password('sha512', password)))
                return cursor.fetchone() is not None 
        return False

    def is_database_exist(self, dbname:str) -> bool:
        """Checks if the given database name exists."""
        if self._db_conn:
            with self._db_conn:
                cursor = self._db_conn.cursor()
                cursor.execute('SELECT dbname FROM %s WHERE dbname=?' % 
                    self.tables['databases'], (dbname,))
                return cursor.fetchone() is not None 
        return False 

    def insert_new_user(self, username:str, password:str):
        pass

    def delete_user(self, username:str):
        pass

    def insert_new_database(self, dbname:str):
        pass

    def delete_database_entry(self, dbname:str):
        pass 

    def create_tables(self):
        """Create server tables if not already exist."""
        if not self._db_conn:
            self.connect_to_database()

        with self._db_conn:
            sql = ("""
                CREATE TABLE %s (
                    `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
                    `username` VARCHAR(50) NOT NULL UNIQUE,
                    `password` VARCHAR(255) NOT NULL
                );""" % self.tables['users'], 
                """
                CREATE TABLE %s (
                    `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    `dbname` VARCHAR(50) NOT NULL UNIQUE
                );""" % self.tables['databases'])
            self._db_conn.execute(sql[0])
            self._db_conn.execute(sql[1])
            self._db_conn.commit()

    def connect_to_database(self):
        """Connect to the server database information."""
        self._db_conn = sqlite3.connect(SERVER_DATABASE, check_same_thread=False) 

    def close_db_connection(self):
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
        self.logger.write_line(msg)
        if output:
            print(msg) 

    def __del__(self):
        self.logger.close_file()
        self.close_db_connection()
        self.close_socket()

    def run(self):
        """Main server activity."""
        try:
            self.create_socket()
            self.connect_to_database()
            self.logger.open_file("a")

            now = datetime.datetime.now()
            self.log("     ======== %s ========\n" % now.strftime('%d-%m-%Y'))
            self.log("[%s] Server started successfully\n" % now.strftime('%H:%M:%S'))

            while True:
                self._socket.listen()
                conn, address = self._socket.accept()
                self._nb_clients += 1
                self.log("[%s] New Client connected at %s\n" % 
                    (time.strftime('%H:%M:%S'), str(address)))
                session = ClientSession(self, conn)
                session.start()
        except KeyboardInterrupt:
            self.log("Total today clients: %d\n" % self._nb_clients)
            self.log("Shutting down server...\n")
        except (sqlite3.Error, socket.error) as e:
            print(e)
        finally:
            self.logger.close_file()
            self.close_db_connection()
            self.close_socket()

if __name__ == '__main__':
    import sys
    args = utils.parse_server_args(sys.argv[1:])
    if utils.is_valid_ip(args.host):
        server = FDB_Server(args.host, args.port)
        server.run()
    else:
        print("Error: Invalid IP address")
