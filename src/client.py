#!/usr/bin/python3

"""FastDB client application
"""

import socket 
import getpass 
import datetime 
import re 

import utils
from config import *

class LoginError(Exception):
    pass

class FDB_Client:
    commands = {'exit', 'quit', 'help'}

    def __init__(self, username:str, address:str, port:int):
        self.username = username
        # Server information for connection
        self.address = address 
        self.port = port
        self.conn = None 
        self.checker = utils.SQL_Checker() 

    def send_data(self, data:bytes):
        """Send the data to the server."""
        if self.conn:
            self.conn.sendall(data)

    def print_results(self):
        """Wait and print incoming data."""
        results = self.conn.recv(1024)
        results = results.decode(encoding="utf-8")
        print(results)

    def connect_to_server(self):
        """Establish connection between client and server."""
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.address, self.port))

    def close_connection(self):
        """Close connection with server."""
        if self.conn:
            self.conn.close()
            self.conn = None  

    def login(self):
        """Manages user's login."""
        password = getpass.getpass(prompt="Enter password: ")
        data = bytes(self.username + DATA_SEPARATOR + password, 'utf-8')
        self.send_data(data)
        data = self.conn.recv(1024)
        if data.decode(encoding="utf-8") != 'ok':
            raise LoginError("Invalid username or password!")

    def find_custom_statement(self, entry:str) -> bytes:
        """Try to find a specific statement for user or database.

        If the entry is a custom statement, return the entry associated
        to the key found in the STATEMENTS dict.
        """
        data = b''
        for key, pattern in STATEMENTS.items():
            if re.fullmatch(pattern, entry, re.IGNORECASE | re.VERBOSE) is not None:
                data = bytes(key + DATA_SEPARATOR + entry, encoding="utf-8")
                break 
        return data 

    def run(self):
        """Application main loop."""
        try:
            self.connect_to_server()
            self.login()
        except (socket.error, LoginError) as e:
            print(e)
        else:
            cls = self.__class__
            cls.welcome()
            while True:
                entry = input(CLIENT_PROMPT)
                if entry in cls.commands:
                    if entry == 'exit' or entry == 'quit':
                        break 
                    elif entry == 'help':
                        cls.help()
                    else: pass
                else:
                    data = self.find_custom_statement(entry)
                    if not data:
                        self.checker.update(entry)
                        if self.checker.is_valid_statement():
                            data = self.checker.sql_to_bytes()
                        else:
                            print(f"\nERROR: {ERROR['invalid-statement']}\n")
                            continue
                    self.send_data(data)
                    self.print_results()
            print("\nBye\n")
        finally:
            self.close_connection()

    @classmethod
    def welcome(cls):
        """Show welcome message."""
        now = datetime.datetime.now()
        print("\n\t~ Welcome ~\t\n")
        print("%s client application, version %s" % (CLIENT_APP_NAME,
            CLIENT_APP_VERSION))
        print("Connect on %s at %s\n" % (now.strftime("%a %d %b %Y"), 
            now.strftime("%H:%M:%S")))
        print("For more information, type 'help'. 'exit' or 'quit' to quit.\n")

    @classmethod
    def help(cls):
        """Show client help"""
        print("\n********************* HELP **********************\n")
        print("This is the help you asked for. Read this carefully!")
        try:
            with open(HELP_FILE, 'r') as _file:
                print(_file.read())
        except FileNotFoundError:
            pass
        print("\n*************************************************\n")

    def __del__(self):
        self.close_connection()

# main
if __name__ == '__main__':
    args = utils.parse_client_args()
    if utils.is_valid_ip(args.host):
        client = FDB_Client(args.user, args.host, args.port)
        client.run()
    else:
        print("ERROR: Invalid IP address")
