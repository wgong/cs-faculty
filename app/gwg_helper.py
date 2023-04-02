from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import re
import hashlib
import pandas as pd


def gwg_in_us_session(now_str=None):
    if now_str is None:
        now_str = datetime.strftime(datetime.now(), '%H:%M:%S')
    return now_str >= '09:30:00' and now_str <= '16:00:00'


def gwg_get_now_str():
    """
    fmt_str = '%Y-%m-%d'
    fmt_str = '%Y-%m-%d_%H%M'
    """
    # return datetime.now().strftime(fmt_str)
    return str(datetime.now())

def gwg_get_weekday(dt="", fmt_str='%Y-%m-%d'):
    """reset to prior Friday when input dt is weekend
    """
    dt = datetime.strptime(dt, fmt_str) if dt else datetime.now
    wd = dt.weekday()
    return dt - timedelta(days=wd-4) if wd in [5, 6] else dt


def gwg_dates_of_this_week(wk_number_in=0, start_dt=""):
    """ Given a reference start date, calculate dates in the given relative week number
    wk_number_in
        = 0: current week
        = -1: prior week
        = 1: next week
    """
    start_date = datetime.strptime(
        start_dt, '%Y-%m-%d') if start_dt else datetime.now()
    wk_year, wk_number_cal = start_date.date().isocalendar()[:2]
    wk_step = 1 if wk_number_in >= 0 else -1
    wk_stop = (wk_number_cal + wk_number_in +
               1) if wk_number_in >= 0 else (wk_number_cal + wk_number_in - 1)
    wk_stop = min(max(0, wk_stop), 54)
    # print(wk_step, wk_stop)

    wk_dates = []
    for wk_number in range(wk_number_cal, wk_stop, wk_step):
        # print(wk_number)
        for i in range(0, 7):
            dt = date(wk_year, 1, 1) + relativedelta(weeks=+
                                                     wk_number) - timedelta(days=i)
            wk_dates.append(str(dt))
    return sorted(wk_dates), datetime.strftime(start_date.date(), '%Y-%m-%d')


def gwg_weekday(wk_number_in=0, start_dt=""):
    """ get week days and today strings like 'YYYY-MM-DD'
    """
    x = gwg_dates_of_this_week(wk_number_in, start_dt)
    return x[0], x[1]


#######################################################
#  Helper functions  - Charting
#######################################################

#######################################################
#  Helper functions  - Misc
#######################################################

# Function sourced from
# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunk_list(lst, n=20):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def gwg_merge_lists(*lists):
    s = set()
    [[s.add(i.upper()) for i in l] for l in lists]
    return sorted(list(s))


def gwg_hash_symbol(s):
    "map symbol to hex so that quote data are stored in one of 16 sqlite db files"
    return '{:x}'.format(int(hashlib.sha256(s.upper().encode("utf-8")).hexdigest(), 16) % 16)


def gwg_parse_tickers(s):
    tmp = {}
    for t in [i.strip().upper() for i in re.sub('[^0-9a-zA-Z]+', ' ', s).split() if i.strip()]:
        tmp[t] = 1
    return list(tmp.keys())


def gwg_parse_numeric_cols(create_table_str):
    cols = [i.replace("real", "").replace(",", "").strip()
            for i in create_table_str.split("\n") if i.strip() and "real" in i]
    return [c for c in cols if c not in ['open_', 'high_', 'low_', 'close_', 'low_1', 'high_1', 'close_1']]


def gwg_list2sql_str(l):
    """convert a list into SQL in string
    """
    return str(l).replace("[", "(").replace("]", ")")


def gwg_log_print(msg):
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


def _df_to_csv(df, index=False):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=index).encode('utf-8')


def _finviz_url(type, ticker, period):
    return f"https://finviz.com/{type}.ashx?t={ticker}&p={period}"


def _yahoo_url(ticker):
    return f"https://finance.yahoo.com/quote/{ticker}"


def _finviz_chart_url(ticker, period="d"):
    return _finviz_url("quote", ticker, period)
    # return f"https://finviz.com/quote.ashx?t={ticker}&p={period}"


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

def gwg_escape_single_quote(s):
    return s.replace("\'", "\'\'")

def gwg_unescape_single_quote(s):
    return s.replace("\'\'", "\'")