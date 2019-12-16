"""This module defines constants used by all services.
"""

DATABASES_DIR = 'databases/'

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 5100
SERVER_DATABASE = DATABASES_DIR + 'fastdb_info.db'
LOG_FILE = 'log.txt'

DATA_SEPARATOR = '$'
ACCESS_GRANTED = b'ok'
ACCESS_DENIED  = b'access denied'

CLIENT_PROMPT = "fastdb> "
CLIENT_APP_NAME = "FastDB"
CLIENT_APP_VERSION = "1.0.1"

HELP_FILE = 'help'
DATABASE_EXT = '.db'

ERROR = {
    'invalid-statement': "Invalid SQL syntax at line 1",
    'database-exists': "Database '%s' already exists",
    'unknown-database': "Unknown database '%s'",
    'no-database': "No such database '%s'",
    'no-user': "No user named '%s'",
    'no-database-seleted': "No database in use"
}

SUCCESS = {
    'database-deleted': "Database '%s' deleted",
    'database-created': "Database '%s' created",
    'database-changed': "Database changed",
    'user-added': "User '%s' added successfully",
    'user-deleted': "User '%s' deleted successfully"
}

STATEMENTS = {
    'create-database': r"^CREATE\s+?DATABASE\s+?(IF\s+?NOT\s+?EXISTS)?(?P<dbname>\w+)\s*?;$",
    'show-databases': r"^SHOW\s+?DATABASES\s*?;$",
    'drop-database': r"^DROP\s+?DATABASE\s+?(?P<dbname>\w+)\s*?;$",
    'use-database': r"USE\s+?(?P<dbname>\w+)(\s*?;)?$",
    # The two below are not really SQL statements
    'add-user': r"ADD\s+?USER\s+?(?P<username>\w+)\s+?PASSWORD\s+?(?P<pass>\w+)\s*?;$",
    'delete-user': r"DELETE\s+?USER\s+?(?P<username>\w+)\s*?;$"
}
