"""
- Add new column "award" to 2 tables: "g_person", "g_work"
"""

from helper import *

# point to old DB file
FILE_DB = "db/cs-faculty-20230429.duckdb"

col_name = "award"
for table_name in ["g_person", "g_work"]:
    df_1, df_2, err_msg = alter_table_add_column(table_name, col_name)
    assert df_1 is None 
    assert df_2 is not None 
    assert err_msg != ""

# verify
col_name = "award"
with DBConn(file_db=FILE_DB) as _conn:
    for table_name in ["g_person", "g_work"]:
        select_sql = f"""
            select {col_name} from {table_name};
        """
        df = _conn.execute(select_sql).df()
        assert df.shape[0] > 0 