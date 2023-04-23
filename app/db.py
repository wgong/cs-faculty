import sqlite3
import duckdb

from config_poc import *

class DBConn(object):
    def __init__(self):
        if FILE_DB.endswith("duckdb"):
            self.conn = duckdb.connect(FILE_DB)
        else:
            self.conn = sqlite3.connect(FILE_DB)

    def __enter__(self):
        return self.conn

    def __exit__(self, type, value, traceback):
        self.conn.close()


class DBUtils():
    """SQLite database query utility """
    def dummy(self):
        pass