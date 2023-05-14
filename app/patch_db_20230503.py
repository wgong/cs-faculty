"""
- Add new column "award" to 2 tables: "g_person", "g_work"
"""

from app_helper import *

# add column "award" to g_work, g_person
ADD_AWARD_COLUMN = True # False # 

# populate uid columns
UPDATE_UID = True # False # 

# add column "note_type" to g_note
ADD_NOTE_TYPE = True # False # 

# add table "g_org"
ADD_TABLE_ORG = True # False # 

# add table "g_project"
ADD_TABLE_PROJECT = True # False # 

if ADD_TABLE_ORG:
    # point to old DB file
    FILE_DB = "db/cs-faculty-20230429.duckdb"

    with DBConn(file_db=FILE_DB) as _conn:
        create_sql = f"""
            create table if not exists 
            g_org (
                    name text not null
                    ,url   text
                    ,tags  text 
                    ,note  text 
                    ,org_type text
                    ,ref_tab text
                    ,ref_key text
                    ,ref_val text
                    ,uid   text
                    ,ts    text
                    ,id    text);
        """
        _conn.execute(create_sql)
        _conn.commit()

if ADD_TABLE_PROJECT:
    # point to old DB file
    FILE_DB = "db/cs-faculty-20230429.duckdb"

    with DBConn(file_db=FILE_DB) as _conn:
        create_sql = f"""
            create table if not exists 
            g_project (
                    name text not null
                    ,url   text
                    ,tags  text 
                    ,note  text 
                    ,project_type text
                    ,ref_tab text
                    ,ref_key text
                    ,ref_val text
                    ,uid   text
                    ,ts    text
                    ,id    text);
        """
        _conn.execute(create_sql)
        _conn.commit()

if ADD_NOTE_TYPE:
    # point to old DB file
    FILE_DB = "db/cs-faculty-20230429.duckdb"

    col_name = "note_type"
    for table_name in ["g_note"]:
        df_1, df_2, err_msg = alter_table_add_column(table_name, col_name)

if ADD_AWARD_COLUMN:
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

if UPDATE_UID:
    uid = get_uid()
    FILE_DB = "db/cs-faculty-20230502.duckdb"
    with DBConn(file_db=FILE_DB) as _conn:
        # populate uid column if NULL for all tables
        for table_name in TABLE_LIST:
            update_sql = f"""
                update {table_name} 
                set uid = '{uid}'
                where uid is null;
            """
            _conn.execute(update_sql)
            _conn.commit()  
