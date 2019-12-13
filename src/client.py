#!/usr/bin/python3

"""FastDB client application
"""

import socket 
import getpass 

import utils

CLIENT_PROMPT = "fastdb> "
ERRORS = {
    'invalid-statement': "Invalid SQL syntax at line 1"
}
DATA_SEPARATOR = '$'

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

    def send_request(self, msg:bytes):
        """Send the SQL statement to the server."""
        if self.conn:
            self.conn.sendall(msg)

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
        self.send_request(data)
        data = self.conn.recv(1024)
        if data.decode(encoding="utf-8") != 'ok':
            raise LoginError("Invalid username or password!")

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
                    self.checker.update(entry)
                    if self.checker.is_valid_statement():
                        self.send_request(self.checker.sql_to_bytes())
                        self.print_results()
                    else:
                        print(ERRORS['invalid-statement'])
        finally:
            self.close_connection()

    @classmethod
    def welcome(cls):
        """Show welcome message."""
        print("\nWelcome ...\n") # login date and time, app version and commands

    @classmethod
    def help(cls):
        """Show client help"""
        print("\n********************* HELP *********************\n")
        print("This is the help you ask for. Read this carefully!")
        print("\n************************************************\n")

    def __del__(self):
        self.close_connection()

# main
if __name__ == '__main__':
    import sys
    args = utils.parse_client_args(sys.argv[1:])
    if utils.is_valid_ip(args.host):
        client = FDB_Client(args.user, args.host, args.port)
        client.run()
    else:
        print("ERROR: Invalid IP address")
