from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import re
from pathlib import Path
import pandas as pd
import os

import sqlite3
import duckdb

from app_config import *

#######################################################
#  Helper functions  - database
#######################################################
class DBConn(object):
    def __init__(self, file_db=FILE_DB):
        """Support only DuckDB and SQLite
        """
        if not Path(file_db).exists():
            raise Exception(f"Database file not found: {file_db}")
        if file_db.endswith("duckdb"):
            self.conn = duckdb.connect(file_db)
        else:
            self.conn = sqlite3.connect(file_db)

    def __enter__(self):
        return self.conn

    def __exit__(self, type, value, traceback):
        self.conn.close()

def alter_table_add_column(table_name, col_name, col_type = "VARCHAR", file_db=FILE_DB):
    df_1, df_2, err_msg = None, None, ""
    with DBConn(file_db) as _conn:
        try:
            select_sql = f"""
                select {col_name} from {table_name};
            """
            df_1 = _conn.execute(select_sql).df()
        except Exception as ex:
            err_msg = str(ex)

            if re.search(r"column(.*)not found", err_msg):
                alter_sql = f"""
                    ALTER TABLE {table_name} add column {col_name} {col_type};
                """
                df_2 = _conn.execute(alter_sql).df()
    return df_1, df_2, err_msg

def alter_table_drop_column(table_name, col_name, file_db=FILE_DB):
    df, err_msg = None, ""
    with DBConn(file_db) as _conn:
        try:
            alter_sql = f"""
                ALTER TABLE {table_name} drop {col_name};
            """
            df = _conn.execute(alter_sql).df()
        except Exception as ex:
            err_msg = str(ex)
    return df, err_msg

#######################################################
#  Helper functions  - Misc
#######################################################

def get_uid():
    return os.getlogin()

# Function sourced from
# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunk_list(lst, n=20):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def merge_lists(*lists):
    s = set()
    [[s.add(i.upper()) for i in l] for l in lists]
    return sorted(list(s))


def list2sql_str(l):
    """convert a list into SQL in string
    """
    return str(l).replace("[", "(").replace("]", ")")


def log_print(msg):
    """print msg to console
    log msg to __file__.log
    """
    print(msg)
    file_log= ".".join(__file__.split(".")[: -1]) + ".log"
    open(file_log, 'a').write(f"{msg}\n")

# user function - regexp
# https://benjr.tw/104785


def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None


def _file_mtime_in_hour(filename):
    # return -1 when file not found
    try:
        age = (time.time() - getmtime(filename))/3600
    except:
        # FileNotFoundError: [WinError 2] The system cannot find the file specified:
        age = -1
    return age


def df_to_csv(df, index=False):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=index).encode('utf-8')



def _reverse_dedup_list(tickers):
    _map = {}
    for t in tickers:
        if not t in _map:
            _map[t] = True
    return list(_map.keys())[: : -1]

def _dedup_list(tickers):
    _lst = []
    for t in tickers:
        if not t in _lst:
            _lst.append(t)
    return _lst

def escape_single_quote(s):
    if s is None or s == 'None':
        return ''
    if not "'" in s:
        return s
    return s.replace("\'", "\'\'")

def unescape_single_quote(s):
    return s.replace("\'\'", "\'")