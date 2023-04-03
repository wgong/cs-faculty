from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import re
import hashlib
import pandas as pd

#######################################################
#  Helper functions  - Misc
#######################################################

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
    return s.replace("\'", "\'\'")

def unescape_single_quote(s):
    return s.replace("\'\'", "\'")