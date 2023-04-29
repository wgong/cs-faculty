"""
Streamlit app to manage CS Faculty data backed by DuckDB 

TODO:
- [2023-04-23] 
    - complete _db_insert_person_team()
    - add menus: Team, Work, Person, 
    - add data from other schools

- [2023-04-21] 
    - upgrade streamlit to 1.21
    - replace st.cache to st.cache_data

DONE:
- [2023-04-25] 
    - revised table definitions: data in g_ prefix tables (see populate_g_tables.ipynb)


"""
__author__ = "wgong"
SRC_URL = "https://github.com/wgong/cs-faculty"

#####################################################
# Imports
#####################################################
# generic import
from datetime import datetime, date, timedelta
import glob
from io import StringIO
import yaml
import sys

from pathlib import Path
import pandas as pd
from shutil import copy
from traceback import format_exc
from uuid import uuid4


import warnings
warnings.filterwarnings("ignore")

import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode

from config_g import *
from helper import (escape_single_quote, df_to_csv)
from db import *

##====================================================
_STR_APP_NAME               = "CS Faculty"

st.set_page_config(
     page_title=f'{_STR_APP_NAME}',
     layout="wide",
     initial_sidebar_state="expanded",
)

# DBU_ = DBUtils()

# string constants (for i18n purpose)
## actions
STR_QUICK_ADD       = "Quick Add"
STR_ADD             = "Add"
STR_UPDATE          = "Update"
STR_SAVE            = "Save"
STR_DELETE          = "Delete"
STR_REFRESH         = "Refresh"
## entity
STR_WELCOME         = "Welcome"
STR_FACULTY         = "Faculty"
STR_RESEARCH_GROUP  = "Research Group"
STR_NOTE            = "Note"
STR_WORK            = "Work"
STR_PERSON          = "Person"
STR_NOTE_ALL        = "Note (All)"
STR_WORK_ALL        = "Work (All)"
STR_PERSON_ALL      = "Person (All)"
STR_REFRESH_HINT    = "Click 'Refresh' button to clear form"
STR_DOWNLOAD_CSV    = "Download CSV"

## menu
_STR_MENU_HOME              = STR_WELCOME
_STR_MENU_FACULTY           = STR_FACULTY
_STR_MENU_RESEARCH_GROUP    = STR_RESEARCH_GROUP
_STR_MENU_NOTE              = STR_NOTE_ALL
_STR_MENU_WORK              = STR_WORK_ALL
_STR_MENU_PERSON            = STR_PERSON_ALL

# Aggrid options
_GRID_OPTIONS = {
    "grid_height": 400,
    "return_mode_value": DataReturnMode.__members__["FILTERED"],
    "update_mode_value": GridUpdateMode.__members__["MODEL_CHANGED"],
    "update_mode": GridUpdateMode.SELECTION_CHANGED | GridUpdateMode.VALUE_CHANGED,
    "fit_columns_on_grid_load": False,   # False to display wide columns
    # "min_column_width": 50, 
    "selection_mode": "single",  #  "multiple",  # 
    "allow_unsafe_jscode": True,
    "groupSelectsChildren": True,
    "groupSelectsFiltered": True,
    "enable_pagination": True,
    "paginationPageSize": 10,
}


#####################################################
# Helpers (prefix with underscore)
#####################################################
def _download_df(df, filename_csv):
    """Download input df to CSV
    """
    if df is not None:
        st.download_button(
            label=STR_DOWNLOAD_CSV,
            data=df_to_csv(df, index=False),
            file_name=filename_csv,
            mime='text/csv',
        )            

@st.cache
def _gen_label(col):
    "Convert table column into form label"
    if col == 'ts_created': return "Created At"
    if "_" not in col:
        if col.upper() in ["URL","ID"]:
            return col.upper()
        elif col.upper() == "TS":
            return "Timestamp"
        return col.capitalize()

    cols = []
    for c in col.split("_"):
        c  = c.strip()
        if not c: continue
        cols.append(c.capitalize())
    return " ".join(cols)

@st.cache
def _get_columns(table_name, prop_name="is_visible"):
    cols_bool = []
    cols_text = {}
    for k,v in COLUMN_PROPS[table_name].items():
        if prop_name.startswith("is_") and v.get(prop_name, False):
            cols_bool.append(k)
            
        if not prop_name.startswith("is_"):
            val = v.get(prop_name, "")
            if val:
                cols_text.update({k: val})
    
    return cols_bool or cols_text
    # return [k for k,v in COLUMN_PROPS[table_name].items() if v.get(prop_name, False) ]

@st.cache
def _parse_column_props():
    """parse COLUMN_PROPS map
    """
    col_defs = {}
    for table_name in COLUMN_PROPS.keys():
        defs = {}
        cols_widget_type = {}
        cols_label_text = {}
        for p in PROPS:
            res = _get_columns(table_name, prop_name=p)
            # print(f"{p}: {res}")
            if p == 'widget_type':
                cols_widget_type = res
            elif p == 'label_text':
                cols_label_text = res
            defs[p] = res
            
        # reset label
        for col in cols_widget_type.keys():
            label = cols_label_text.get(col, "")
            if not label:
                label = _gen_label(col)
            cols_label_text.update({col : label})
        # print(cols_label_text)
        defs['label_text'] = cols_label_text
        defs['all_columns'] = list(cols_widget_type.keys())

        # sort form_column alpha-numerically
        # max number of form columns = 3
        # add them
        tmp = {}
        for i in range(1,4):
            m = {k:v for k,v in defs['form_column'].items() if v.startswith(f"col{i}-")}
            tmp[f"col{str(i)}_columns"] = sorted(m, key=m.__getitem__)        
        defs.update(tmp)
        col_defs[table_name] = defs

        
    return col_defs

#####################################################
# define constants
#####################################################
COLUMN_DEFS = _parse_column_props()
FACULTY_DATA_COLS = ['name', 'url', 'job_title',
        'research_area', 'email','department', 
        'phd_univ','phd_year','note',]
GROUP_DATA_COLS =  ['name', 'url', 'note',]
NOTE_DATA_COLS = ['name', 'url', 'note',"tags"]

def _load_db():

    if not Path(FILE_DB).exists():
        if not Path(FILE_XLSX).exists():
            raise Exception(f"source file: {FILE_XLSX} missing")
        
        xls = pd.ExcelFile(FILE_XLSX)
        sheet_name = STR_FACULTY
        df_faculty = pd.read_excel(xls, sheet_name, keep_default_na=False)
        sheet_name = STR_RESEARCH_GROUP
        df_research_group = pd.read_excel(xls, sheet_name, keep_default_na=False)

        with DBConn(FILE_DB, db_type="duckdb") as _conn:
            _conn.register("v_faculty", df_faculty)
            _conn.register("v_research_group", df_research_group)

            _conn.execute(f"Create table {TABLE_FACULTY} as select * from v_faculty;")
            _conn.execute(f"Create table {TABLE_RESEARCH_GROUP} as select * from v_research_group;")
            
            create_table_note_sql = f"""create table if not exists {TABLE_NOTE} (
                    id    text not null
                    ,name text not null
                    ,url   text
                    ,note  text 
                    ,tags  text
                    ,ts    text
                );
            """
            _conn.execute(create_table_note_sql)
            _conn.commit()

def _display_grid_df(df, 
                    selection_mode="multiple", 
                    page_size=_GRID_OPTIONS["paginationPageSize"],
                    grid_height=_GRID_OPTIONS["grid_height"],
                    editable_columns=[],
                    clickable_columns=[]):
    """show df in a grid and return selected row
    """

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection(selection_mode,
            use_checkbox=True,
            groupSelectsChildren=_GRID_OPTIONS["groupSelectsChildren"], 
            groupSelectsFiltered=_GRID_OPTIONS["groupSelectsFiltered"]
        )
    gb.configure_pagination(paginationAutoPageSize=False, 
        paginationPageSize=page_size)
    gb.configure_columns(editable_columns, editable=True)

    cell_renderer =  JsCode("""
    function(params) {return `<a href=${params.value} target="_blank">${params.value}</a>`}
    """)
    for col_name in clickable_columns:
        gb.configure_column(col_name, cellRenderer=cell_renderer)

    gb.configure_grid_options(domLayout='normal')
    grid_response = AgGrid(
        df, 
        gridOptions=gb.build(),
        height=grid_height, 
        # width='100%',
        data_return_mode=_GRID_OPTIONS["return_mode_value"],
        # update_mode=_GRID_OPTIONS["update_mode_value"],
        update_mode=_GRID_OPTIONS["update_mode"],
        fit_columns_on_grid_load=_GRID_OPTIONS["fit_columns_on_grid_load"],
        allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
    )
    return grid_response

def _layout_form_inter(table_name, 
                selected_row, 
                ref_tab,
                ref_key,  
                ref_val,
                inter_table_name,
                rel_type):
    """ layout form for a table and handles button actions 
    which have intersection table dependency
    """
    # st.write(f"selected_row:\n{selected_row}")

    form_name = st.session_state.get("form_name","")

    COL_DEFS = COLUMN_DEFS[table_name]
    visible_columns = COL_DEFS["is_visible"]
    system_columns = COL_DEFS["is_system_col"]
    form_columns = COL_DEFS["form_column"]
    col_labels = COL_DEFS["label_text"]
    widget_types = COL_DEFS["widget_type"]

    old_row = {}
    for col in visible_columns:
        old_row[col] = selected_row.get(col) if selected_row is not None else ""

    # display buttons
    btn_save, btn_refresh, btn_delete = _crud_display_buttons()

    # collect info for DB action
    data = {"table_name": table_name,   # ref_tab_sub
            "ref_tab": ref_tab,
            "ref_key": ref_key,  
            "ref_val": ref_val,
            "inter_table_name": inter_table_name,
            "rel_type":rel_type }

    # display form and populate data dict
    col1_columns = []
    col2_columns = []
    for c in visible_columns:
        if form_columns.get(c, "").startswith("col1-"):
            col1_columns.append(c)
        elif form_columns.get(c, "").startswith("col2-"):
            col2_columns.append(c) 

    col1,col2 = st.columns([8,7])
    with col1:
        for col in col1_columns:
            data = _layout_form_fields(data,form_name,old_row,col,
                        widget_types,col_labels,system_columns)

    with col2:
        for col in col2_columns:
            data = _layout_form_fields(data,form_name,old_row,col,
                        widget_types,col_labels,system_columns)

    # copy id if present
    id_val = old_row.get("id", "")
    if id_val:
        data.update({"id" : id_val})

    # st.write(f"data={data}")

    # handle buttons
    if btn_save:
        if data.get("id"):
            data.update({"ts": str(datetime.now()),})
            _db_update_by_id(data)
        else:
            data.update({"id": str(uuid4()), "ts": str(datetime.now()),})
            _db_insert_inter(data)

    elif btn_delete and data.get("id"):
        _db_delete_by_id_inter(data)

def _layout_form(table_name, selected_row, ref_key="", ref_val="", entity_type=""):
    """ layout form for a table and handles button actions 
    """
    # st.write(f"selected_row:\n{selected_row}")

    form_name = st.session_state.get("form_name","")
    form_name_suffix = form_name.split("#")[-1]

    COL_DEFS = COLUMN_DEFS[table_name]
    visible_columns = COL_DEFS["is_visible"]
    system_columns = COL_DEFS["is_system_col"]
    form_columns = COL_DEFS["form_column"]
    col_labels = COL_DEFS["label_text"]
    widget_types = COL_DEFS["widget_type"]

    old_row = {}
    for col in visible_columns:
        old_row[col] = selected_row.get(col) if selected_row is not None else ""

    # display buttons
    btn_save, btn_refresh, btn_delete = _crud_display_buttons()

    data = {"table_name": table_name}
    if ref_key and ref_val:
        data.update({"ref_key":ref_key, "ref_val":ref_val})
    if entity_type:
        data.update({"entity_type":entity_type})
        
    # display form and populate data dict
    col1_columns = []
    col2_columns = []
    for c in visible_columns:
        if form_name_suffix and c in ["ref_key", "ref_val"]:
            # no need to display ref_key, ref_val for parent/child view
            continue
        if form_columns.get(c, "").startswith("col1-"):
            col1_columns.append(c)
        elif form_columns.get(c, "").startswith("col2-"):
            col2_columns.append(c) 

    col1,col2 = st.columns([8,7])
    with col1:
        for col in col1_columns:
            data = _layout_form_fields(data,form_name,old_row,col,
                        widget_types,col_labels,system_columns)

    with col2:
        for col in col2_columns:
            data = _layout_form_fields(data,form_name,old_row,col,
                        widget_types,col_labels,system_columns)

    # copy id if present
    id_val = old_row.get("id", "")
    if id_val:
        data.update({"id" : id_val})

    # st.write(f"data={data}")

    # handle buttons
    if btn_save:
        if data.get("id"):
            data.update({"ts": str(datetime.now()),})
            _db_update_by_id(data)
        else:
            data.update({"id": str(uuid4()), "ts": str(datetime.now()),})
            _db_insert(data)

    elif btn_delete and data.get("id"):
        _db_delete_by_id(data)


###################################################################
# handle Note
# ======================================
def _db_execute(sql_statement, DEBUG=True):
    with DBConn() as _conn:
        if DEBUG: print(sql_statement)
        _conn.execute(sql_statement)
        _conn.commit()           

def _db_select(table_name, orderby_cols=[]):
    """Select whole table"""
    with DBConn() as _conn:
        orderby_clause = f' order by {",".join(orderby_cols)}' if orderby_cols else ' '
        sql_stmt = f"""
            select *
            from {table_name} 
            {orderby_clause};
        """
        return pd.read_sql(sql_stmt, _conn)

def _db_select_by_id(table_name, id_value=""):
    """Select row by key"""
    if not id_value: return []

    with DBConn() as _conn:
        sql_stmt = f"""
            select *
            from {table_name} 
            where id = '{id_value}' ;
        """
        return pd.read_sql(sql_stmt, _conn)

def _db_select_by_key(table_name, key_value=""):
    """Select row by key"""

    with DBConn() as _conn:
        key_col = KEY_COLUMNS[table_name]
        where_clause = f" {key_col} = '{key_value}' "
        sql_stmt = f"""
            select *
            from {table_name} 
            where 
            {where_clause};
        """
        return pd.read_sql(sql_stmt, _conn)

def _db_delete_by_key(data):
    if not data: 
        return None
    
    table_name = data.get("table_name", "")
    if not table_name:
        raise Exception(f"[ERROR] Missing key: table_name: {data}")

    key_col = KEY_COLUMNS[table_name]
    key_val = data.get(key_col)
    if not key_val:
        print(f"[ERROR] missing primary key: '{key_col}'")
        return None
    
    delete_sql = f"""
        delete from {table_name}
        where {key_col} = '{key_val}';
    """
    _db_execute(delete_sql)

    # return _db_select(table_name=table_name)        


def _db_delete_person_team(data):
    if not data: 
        return None
    
    inter_table_name = data.get("inter_table_name", "")
    if not inter_table_name:
        raise Exception(f"[ERROR] Missing key: inter_table_name: {data}")
    
    ref_type = data.get("ref_type", "")
    team_lead = data.get("team_lead", "")
    ref_type_2 = data.get("ref_type_2", "")
    ref_key_2 = data.get("ref_key_2", "")

    delete_sql = f"""
        delete from {inter_table_name}
        where 1=1 
        and ref_type = '{ref_type}' 
        and ref_key in (
            select url from TABLE_TEAM 
            where team_lead = '{team_lead}' 
        )
        and ref_type_2 = '{ref_type_2}' 
        and ref_key_2 = '{ref_key_2}'
        ;
    """
    _db_execute(delete_sql)

# TODO
def _db_insert_person_team(data):
    """insert into both child and intersection tables
    """
    if not data: 
        return None
    
    table_name = data.get("table_name", "")
    if not table_name:
        raise Exception(f"[ERROR] Missing key: table_name: {data}")
    
    inter_table_name = data.get("inter_table_name", "")
    if not inter_table_name:
        raise Exception(f"[ERROR] Missing key: inter_table_name: {data}")
    
    ref_type = data.get("ref_type", "")
    ref_key = data.get("ref_key", "")
    ref_type_2 = data.get("ref_type_2", "")
    ref_key_2 = data.get("ref_key_2", "")

    # build SQL
    visible_columns = _get_columns(table_name, prop_name="is_visible")
    col_clause = []
    val_clause = []
    for col,val in data.items():
        if col not in visible_columns:
            continue
        col_clause.append(col) 
        val_clause.append(f"'{escape_single_quote(val)}'")

    _id = str(uuid4())
    _ts = data.get("ts", str(datetime.now()))
    insert_sql = f"""
        -- insert child table
        insert into {table_name} (
            {", ".join(col_clause)}
        )
        values (
            {", ".join(val_clause)}
        );

        -- insert intersection table
        insert into {inter_table_name} (
            id, ts, ref_type, ref_key, ref_type_2, ref_key_2
        )
        values (
            '{_id}', '{_ts}', '{ref_type}','{ref_key}','{ref_type_2}','{ref_key_2}'
        );
    """
    # TODO
    # _db_execute(insert_sql)

def _db_delete_by_id_inter(data):
    if not data: 
        return None
    
    inter_table_name = data.get("inter_table_name", "")
    if not inter_table_name:
        raise Exception(f"[ERROR] Missing key: inter_table_name: {data}")
    
    ref_type = data.get("ref_type", "")
    ref_key = data.get("ref_key", "")
    ref_type_2 = data.get("ref_type_2", "")
    ref_key_2 = data.get("ref_key_2", "")

    delete_sql = f"""
        delete from {inter_table_name}
        where 1=1 
        and ref_type = '{ref_type}' and ref_key = '{ref_key}'
        and ref_type_2 = '{ref_type_2}' and ref_key_2 = '{ref_key_2}'
        ;
    """
    _db_execute(delete_sql)

def _db_insert_inter(data):
    """insert into both child and intersection tables
    """
    if not data: 
        return None
    
    table_name = data.get("table_name", "")
    if not table_name:
        raise Exception(f"[ERROR] Missing key: table_name: {data}")
    
    inter_table_name = data.get("inter_table_name", "")
    if not inter_table_name:
        raise Exception(f"[ERROR] Missing key: inter_table_name: {data}")
    
    ref_type = data.get("ref_type", "")
    ref_key = data.get("ref_key", "")
    ref_type_2 = data.get("ref_type_2", "")
    ref_key_2 = data.get("ref_key_2", "")

    # build SQL
    visible_columns = _get_columns(table_name, prop_name="is_visible")
    col_clause = []
    val_clause = []
    for col,val in data.items():
        if col not in visible_columns:
            continue
        col_clause.append(col) 
        val_clause.append(f"'{escape_single_quote(val)}'")

    _id = str(uuid4())
    _ts = data.get("ts", str(datetime.now()))
    insert_sql = f"""
        -- insert child table
        insert into {table_name} (
            {", ".join(col_clause)}
        )
        values (
            {", ".join(val_clause)}
        );

        -- insert intersection table
        insert into {inter_table_name} (
            id, ts, ref_type, ref_key, ref_type_2, ref_key_2
        )
        values (
            '{_id}', '{_ts}', '{ref_type}','{ref_key}','{ref_type_2}','{ref_key_2}'
        );
    """
    _db_execute(insert_sql)

def _db_delete_by_id_child(data):
    if not data: 
        return None
    
    inter_table_name = data.get("inter_table_name", "")
    if not inter_table_name:
        raise Exception(f"[ERROR] Missing key: inter_table_name: {data}")
    
    ref_type = data.get("ref_type", "")
    ref_key = data.get("ref_key", "")
    ref_type_2 = data.get("ref_type_2", "")
    ref_key_2 = data.get("ref_key_2", "")

    delete_sql = f"""
        delete from {inter_table_name}
        where 1=1 
        and ref_type = '{ref_type}' and ref_key = '{ref_key}'
        and ref_type_2 = '{ref_type_2}' and ref_key_2 = '{ref_key_2}'
        ;
    """
    _db_execute(delete_sql)



def _db_insert_child(data):
    """insert into both child and intersection tables
    """
    if not data: 
        return None
    
    table_name = data.get("table_name", "")
    if not table_name:
        raise Exception(f"[ERROR] Missing key: table_name: {data}")
    
    inter_table_name = data.get("inter_table_name", "")
    if not inter_table_name:
        raise Exception(f"[ERROR] Missing key: inter_table_name: {data}")
    
    ref_type = data.get("ref_type", "")
    ref_key = data.get("ref_key", "")
    ref_type_2 = data.get("ref_type_2", "")
    ref_key_2 = data.get("ref_key_2", "")

    # build SQL
    visible_columns = _get_columns(table_name, prop_name="is_visible")
    col_clause = []
    val_clause = []
    for col,val in data.items():
        if col not in visible_columns:
            continue
        col_clause.append(col) 
        val_clause.append(f"'{escape_single_quote(val)}'")

    _id = str(uuid4())
    _ts = data.get("ts", str(datetime.now()))
    insert_sql = f"""
        -- insert child table
        insert into {table_name} (
            {", ".join(col_clause)}
        )
        values (
            {", ".join(val_clause)}
        );

        -- insert intersection table
        insert into {inter_table_name} (
            id, ts, ref_type, ref_key, ref_type_2, ref_key_2
        )
        values (
            '{_id}', '{_ts}', '{ref_type}','{ref_key}','{ref_type_2}','{ref_key_2}'
        );
    """
    _db_execute(insert_sql)


def _db_update(data):
    if not data: 
        return None
    
    table_name = data.get("table_name", "")
    if not table_name:
        raise Exception(f"[ERROR] Missing key: table_name: {data}")

    key_col = KEY_COLUMNS[table_name]
    key_val = data.get(key_col)
    if not key_val:
        print(f"[ERROR] Missing primary key: '{key_col}'")
        return None
    
    df_old = _db_select_by_key(table_name=table_name, key_value=key_val).to_dict('records')
    if len(df_old) < 1:
        return None
    
    old_row = df_old[0]

    # build SQL
    all_cols = TABLE_COLUMNS[table_name]
    set_clause = []
    for col,val in data.items():
        if col == key_col or col in ['_selectedRowNodeInfo', 'table_name']: 
            continue
        if col not in all_cols:
            print(f"[WARN] column '{col}' not found in {str(all_cols)}")
            continue
        if val != old_row.get(col):
            set_clause.append(f"{col} = '{escape_single_quote(val)}'")

    if set_clause:
        update_sql = f"""
            update {table_name}
            set {', '.join(set_clause)}
            where {key_col} = '{key_val}';
        """
        _db_execute(update_sql)   

    # return _db_select(table_name=table_name) 

def _db_insert(data):
    if not data: 
        return None
    
    table_name = data.get("table_name", "")
    if not table_name:
        raise Exception(f"[ERROR] Missing table_name: {data}")

    # build SQL
    visible_columns = _get_columns(table_name, prop_name="is_visible")
    col_clause = []
    val_clause = []
    for col,val in data.items():
        if col not in visible_columns:
            continue
        col_clause.append(col) 
        val_clause.append(f"'{escape_single_quote(val)}'")

    insert_sql = f"""
        insert into {table_name} (
            {", ".join(col_clause)}
        )
        values (
            {", ".join(val_clause)}
        );
    """
    _db_execute(insert_sql)

def _db_update_by_id(data, update_changed=True):
    if not data: 
        return
    
    table_name = data.get("table_name", "")
    if not table_name:
        raise Exception(f"[ERROR] Missing table_name: {data}")

    id_val = data.get("id", "")
    if not id_val:
        return

    if update_changed:
        df_old = _db_select_by_id(table_name=table_name, id_value=id_val).to_dict('records')
        if len(df_old) < 1:
            return
        old_row = df_old[0]

    editable_columns = _get_columns(table_name, prop_name="is_editable")

    # build SQL
    set_clause = []
    for col,val in data.items():
        if col not in editable_columns: 
            continue
        if update_changed:
            if val != old_row.get(col):
                set_clause.append(f"{col} = '{escape_single_quote(val)}'")
        else:
            set_clause.append(f"{col} = '{escape_single_quote(val)}'")

    if set_clause:
        update_sql = f"""
            update {table_name}
            set {', '.join(set_clause)}
            where id = '{id_val}';
        """
        _db_execute(update_sql)   

def _db_delete_by_id(data):
    if not data: 
        return None
    
    table_name = data.get("table_name", "")
    if not table_name:
        raise Exception(f"[ERROR] Missing table_name: {data}")

    id_val = data.get("id", "")
    if not id_val:
        return None
    
    delete_sql = f"""
        delete from {table_name}
        where id = '{id_val}';
    """
    _db_execute(delete_sql)

def _db_upsert_group(data, table_name=TABLE_RESEARCH_GROUP):
    _research_group = data.get("name", "")
    if not _research_group: return None

    with DBConn() as _conn:
        df = pd.read_sql(f"""
            select name from {table_name}
            where name='{_research_group}';
        """, _conn)

    _url = data.get("url", "")
    if df.shape[0] > 0:  # update
        sql_stmt = f"""
            update {table_name}
            set url = '{_url}'
            where name='{_research_group}';
        """
    else:
        sql_stmt = f"""
            insert into {table_name} (name, url)
            values ('{_research_group}', '{_url}');
        """
    _db_execute(sql_stmt)

    # return _db_select(table_name=table_name) 

def _db_upsert_faculty(data, 
                       table_name=TABLE_FACULTY, 
                       use_key_col="name",
                       data_cols = FACULTY_DATA_COLS,
                       ):
    _user_key_val = data.get(use_key_col, "")
    if not _user_key_val: return None

    with DBConn() as _conn:
        df = pd.read_sql(f"""
            select * from {table_name}
            where {use_key_col} = '{_user_key_val}';
        """, _conn)


    if df.shape[0] > 0:  # update
        set_clause = []
        for c in data_cols:
            if c == use_key_col: continue
            v = data.get(c, "")
            set_clause.append(f"{c} = '{v}'")

        if set_clause:
            sql_stmt = f"""
                update {table_name}
                set {", ".join(set_clause)}
                where {use_key_col} = '{_user_key_val}';
            """
        else:
            sql_stmt = ""
    else:               # insert
        col_names = []
        col_vals = []
        for c in data_cols:
            col_names.append(c)
            v = data.get(c, "")
            col_vals.append(f"'{v}'")        

        sql_stmt = f"""
            insert into {table_name} 
            ( {", ".join(col_names)} )
            values 
            (  {", ".join(col_vals)} );
        """
    if sql_stmt:
        _db_execute(sql_stmt)

    # return _db_select(table_name=table_name) 

def _push_selected_cols_to_end(cols, selected_cols=SYS_COLS):
    """move selected column to the end,
    e.g. id, ts system cols
    """
    new_select_cols = []
    new_cols = []
    for c in cols:
        if c in selected_cols:
            new_select_cols.append(c)
        else:
            new_cols.append(c)
    if not new_select_cols:
        return new_cols
    else:
        return new_cols + new_select_cols


def _push_selected_cols_to_front(cols, selected_cols=["name","url"]):
    """move selected column to the front,
    e.g. name, url
    """
    new_select_cols = []
    new_cols = []
    for c in cols:
        if c in selected_cols:
            new_select_cols.append(c)
        else:
            new_cols.append(c)
    if not new_select_cols:
        return new_cols
    else:
        return new_select_cols + new_cols


# _STR_MENU_FACULTY
def _display_grid_faculty(table_name=TABLE_FACULTY,
                form_name_suffix="",
                orderby_cols=["name"], 
                selection_mode="single"):
    
    if not table_name in COLUMN_PROPS or not table_name in COLUMN_DEFS:
        st.error(f"Invalid table name: {table_name}")
        return
     
    form_name = f"{table_name}#{form_name_suffix}"

    COL_DEFS = COLUMN_DEFS[table_name]
    visible_columns = COL_DEFS["is_visible"]
    editable_columns = COL_DEFS["is_editable"]
    clickable_columns = COL_DEFS["is_clickable"]

    st.session_state["form_name"] = form_name

    with DBConn() as _conn:
        orderby_clause = f' order by {",".join(orderby_cols)}' if orderby_cols else ""
        where_clause = " where person_type = 'faculty' "
        selected_cols = _push_selected_cols_to_front(visible_columns, selected_cols=["name","url"])
        selected_cols = _push_selected_cols_to_end(selected_cols, selected_cols=SYS_COLS)
        sql_stmt = f"""
            select {",".join(selected_cols)}
            from {table_name} 
            {where_clause}
            {orderby_clause};
        """
        df = pd.read_sql(sql_stmt, _conn)

    grid_resp = _display_grid_df(df, 
                        selection_mode=selection_mode, 
                        page_size=10, 
                        grid_height=370,
                        editable_columns=editable_columns,
                        clickable_columns=clickable_columns
                    )
    
    selected_row = {}
    if grid_resp and grid_resp.get('selected_rows'):
        selected_row = grid_resp['selected_rows'][0]

    if not selected_row:
        return

    if st.button("Save", key=f"{form_name}_save"):
        data = selected_row
        data.update({"table_name": table_name})
        _db_update_by_id(data=data)

    primary_key = selected_row.get("url")
    if not primary_key:
        print(f"[ERROR] Missing primary key 'url' field")
        return
    
    # NOTE:
    # when using st.tab, grid not displayed correctly
    # use st.selectbox instead
    menu_options = ["Work", "Team", "Note"]
    idx_default = menu_options.index("Work")

    faculty_name = selected_row.get("name")
    menu_item = st.selectbox(f"{faculty_name} : {primary_key}", 
                                menu_options, index=idx_default, key="faculty_menu_item")

    if menu_item == "Work":
        try:
            # _crud_display_grid_form_work(TABLE_WORK, 
            table_name = TABLE_WORK
            _crud_display_grid_form_inter(table_name, 
                        ref_tab=TABLE_PERSON, 
                        ref_key="url", 
                        ref_val=primary_key,
                        form_name_suffix="faculty",
                        inter_table_name=TABLE_RELATION,
                        rel_type='person-work',
                        page_size=5, grid_height=220)
        except:
            pass  # workaround to fix an streamlit issue

    elif menu_item == "Team":
        try:
            table_name = TABLE_PERSON 
            _crud_display_grid_form_inter(table_name, 
                        ref_tab=TABLE_PERSON, 
                        ref_key="url", 
                        ref_val=primary_key,
                        form_name_suffix="faculty",
                        inter_table_name=TABLE_RELATION,
                        rel_type='team-person',
                        page_size=5, grid_height=220)
        except:
            pass  # workaround to fix an streamlit issue

    elif menu_item == "Note":
        table_name = TABLE_NOTE
        _crud_display_grid_form_subject(table_name,
                        ref_key=f"{TABLE_PERSON}#url", 
                        ref_val=primary_key,
                        form_name_suffix="faculty", 
                        page_size=5, grid_height=220)


def _layout_form_fields(data,form_name,old_row,col,
                        widget_types,col_labels,system_columns):
    if old_row:
        widget_type = widget_types.get(col, "text_input")
        if widget_type == "text_area":
            kwargs = {"height":125}
            val = st.text_area(col_labels.get(col), value=old_row[col], key=f"col_{form_name}_{col}", kwargs=kwargs)
        elif widget_type == "selectbox":
            # check if options is avail, otherwise display as text_input
            if col in SELECTBOX_OPTIONS:
                try:
                    val = st.selectbox(col_labels.get(col), SELECTBOX_OPTIONS.get(col,[]), index=0, key=f"col_{form_name}_{col}")
                except ValueError:
                    opts = SELECTBOX_OPTIONS.get(col,[])
                    val = opts[0] if opts else "" # workaround for refresh error
            else:
                val = st.text_input(col_labels.get(col), value=old_row[col], key=f"col_{form_name}_{col}")
        else:
            kwargs = {}
            if col in system_columns:
                kwargs.update({"disabled":True})
            val = st.text_input(col_labels.get(col), value=old_row[col], key=f"col_{form_name}_{col}", kwargs=kwargs)

        if val != old_row[col]:
            data.update({col : val})

    return data

def _crud_display_grid_form_inter(table_name, 
                    ref_tab,  
                    ref_key,  
                    ref_val,
                    form_name_suffix="",
                    inter_table_name=TABLE_RELATION,
                    rel_type='person-work',
                    page_size=10, grid_height=370):
    """Render grid according to column properties, 
    used to display a database table, or child table when ref_type/_key are given

    Inputs:
        form_name (required): 
            table name if ref_type is not given

        ref_type: must be parent table name if given, form_name can be different from underlying table name
        ref_key: foreign key

    Outputs:
    Buttons on top for Upsert, Delete action
    Fields below in columns: 1, 2, or 3 specified by 'form_column'
    """
    if not table_name in COLUMN_PROPS or not table_name in COLUMN_DEFS:
        st.error(f"Invalid table name: {table_name}")
        return
    
    form_name = f"{table_name}#{form_name_suffix}"
    st.session_state["form_name"] = form_name

    COL_DEFS = COLUMN_DEFS[table_name]
    visible_columns = COL_DEFS["is_visible"]
    editable_columns = COL_DEFS["is_editable"]
    clickable_columns = COL_DEFS["is_clickable"]

    # prepare dataframe
    with DBConn() as _conn:
        # fetch child table keys first
        sql_stmt = f"""
            select 
                it.ref_key_sub as "key_col", 
                it.ref_val_sub as "key_val"
            from {inter_table_name} it 
            where it.rel_type = '{rel_type}'
                and it.ref_tab = '{ref_tab}'
                and it.ref_key = '{ref_key}'
                and it.ref_val = '{ref_val}'
                and it.ref_tab_sub = '{table_name}'
        """
        df_1 = pd.read_sql(sql_stmt, _conn)    
        rows = df_1.groupby("key_col")["key_val"].apply(list).to_dict()
        where_clause = []
        for k,v in rows.items():
            where_clause.append(f" {k} in {str(v).replace('[','(').replace(']',')')}")

        # fetch child table rows
        selected_cols = _push_selected_cols_to_front(visible_columns, selected_cols=["name","url"])
        selected_cols = _push_selected_cols_to_end(selected_cols, selected_cols=SYS_COLS)
        sql_stmt = f"""
            select {", ".join(selected_cols)}
            from {table_name}
            where {" or ".join(where_clause)}
        """
        df = pd.read_sql(sql_stmt, _conn)    

    grid_resp = _display_grid_df(df, 
                    selection_mode="single", 
                    page_size=page_size, 
                    grid_height=grid_height,
                    editable_columns=editable_columns,
                    clickable_columns=clickable_columns)
    selected_row = None
    if grid_resp:
        selected_rows = grid_resp['selected_rows']
        if selected_rows and len(selected_rows):
            selected_row = selected_rows[0]

    # st.write(f"selected_row:\n{selected_row}")

    _layout_form_inter(table_name, 
                selected_row, 
                ref_tab,
                ref_key,  
                ref_val,
                inter_table_name,
                rel_type)

def _crud_display_grid_form_work(table_name, 
                    ref_tab,  
                    ref_key,  
                    ref_val,
                    form_name_suffix="",
                    inter_table_name=TABLE_RELATION,
                    rel_type='person-work',
                    page_size=10, grid_height=370):
    """Render grid according to column properties, 
    used to display a database table, or child table when ref_type/_key are given

    Inputs:
        form_name (required): 
            table name if ref_type is not given

        ref_type: must be parent table name if given, form_name can be different from underlying table name
        ref_key: foreign key

    Outputs:
    Buttons on top for Upsert, Delete action
    Fields below in columns: 1, 2, or 3 specified by 'form_column'
    """
    if not table_name in COLUMN_PROPS or not table_name in COLUMN_DEFS:
        st.error(f"Invalid table name: {table_name}")
        return
    
    form_name = f"{table_name}#{form_name_suffix}"
    
    COL_DEFS = COLUMN_DEFS[table_name]
    visible_columns = COL_DEFS["is_visible"]
    editable_columns = COL_DEFS["is_editable"]
    clickable_columns = COL_DEFS["is_clickable"]

    st.session_state["form_name"] = form_name
    st.session_state["visible_columns"] = visible_columns

    # prepare dataframe
    with DBConn() as _conn:
        # fetch child table keys first
        sql_stmt = f"""
            select 
                it.ref_key_sub as "key_col", 
                it.ref_val_sub as "key_val"
            from {inter_table_name} it 
            where it.rel_type = '{rel_type}'
                and it.ref_tab = '{ref_tab}'
                and it.ref_key = '{ref_key}'
                and it.ref_val = '{ref_val}'
                and it.ref_tab_sub = '{table_name}'
        """
        df_1 = pd.read_sql(sql_stmt, _conn)    
        rows = df_1.groupby("key_col")["key_val"].apply(list).to_dict()
        where_clause = []
        for k,v in rows.items():
            where_clause.append(f" {k} in {str(v).replace('[','(').replace(']',')')}")

        # fetch child table rows
        selected_cols = _push_selected_cols_to_front(visible_columns, selected_cols=["name","url"])
        selected_cols = _push_selected_cols_to_end(selected_cols, selected_cols=SYS_COLS)
        sql_stmt = f"""
            select {", ".join(selected_cols)}
            from {table_name}
            where {" or ".join(where_clause)}
        """
        df = pd.read_sql(sql_stmt, _conn)    

    grid_resp = _display_grid_df(df, 
                    selection_mode="single", 
                    page_size=page_size, 
                    grid_height=grid_height,
                    editable_columns=editable_columns,
                    clickable_columns=clickable_columns)
    selected_row = None
    if grid_resp:
        selected_rows = grid_resp['selected_rows']
        if selected_rows and len(selected_rows):
            selected_row = selected_rows[0]

    # st.write(f"selected_row:\n{selected_row}")

    # old_row = {}
    # dict_col_label = COL_DEFS['label_text']
    # for col in visible_columns:
    #     old_row[col] = selected_row.get(col) if selected_row is not None else ""

    # ## Form Layout

    # # display buttons
    # btn_save, btn_refresh, btn_delete = _crud_display_buttons()

    # data = {"table_name": table_name, "inter_table_name": data_dict["Work"]["table"], 
    #         "ref_type":ref_type, "ref_key":ref_key,
    #         "ref_type_2":TABLE_WORK, "ref_key_2":old_row.get("id"),
    #         }
    # # display form and populate data dict
    # col1_columns = COL_DEFS['col1_columns']
    # col2_columns = COL_DEFS['col2_columns']

    # idx_default = WORK_TYPES.index("publication")
    # col1,col2 = st.columns([8,7])
    # with col1:
    #     for col in col1_columns:
    #         if col == "type":
    #             # hard-code col=type via st.selectbox
    #             val = st.selectbox(dict_col_label.get(col), WORK_TYPES, index=idx_default, key=f"col_{form_name}_{col}")
    #         else:
    #             widget_type = COL_DEFS['widget_type'][col]
    #             if widget_type == "text_area":
    #                 kwargs = {"height":200}
    #                 val = st.text_area(dict_col_label.get(col), value=old_row[col], key=f"col_{form_name}_{col}", kwargs=kwargs)
    #             else:
    #                 kwargs = {}
    #                 if col in COL_DEFS["is_system_col"]:
    #                     kwargs.update({"disabled":True})
    #                 val = st.text_input(dict_col_label.get(col), value=old_row[col], key=f"col_{form_name}_{col}", kwargs=kwargs)

    #         if val != old_row[col]:
    #             data.update({col : val})

    # with col2:
    #     for col in col2_columns:
    #         widget_type = COL_DEFS['widget_type'][col]
    #         if widget_type == "text_area":
    #             kwargs = {"height":200}
    #             val = st.text_area(dict_col_label.get(col), value=old_row[col], key=f"col_{form_name}_{col}", kwargs=kwargs)
    #         else:
    #             kwargs = {}
    #             if col in COL_DEFS["is_system_col"]:
    #                 kwargs.update({"disabled":True})
    #             val = st.text_input(dict_col_label.get(col), value=old_row[col], key=f"col_{form_name}_{col}", kwargs=kwargs)

    #         if val != old_row[col]: 
    #             data.update({col : val})

    # # copy id if present
    # id_val = old_row.get("id", "")
    # if id_val:
    #     data.update({"id" : id_val})

    # # st.write(f"data={data}")
    # # handle buttons
    # if btn_save:
    #     _ts = str(datetime.now())
    #     if selected_row is not None and data.get("id"):
    #         data.update({"ts": _ts,})
    #         _db_update_by_id(data)
    #     else:
    #         _id = str(uuid4())
    #         data.update({"id": _id, 
    #                      "ts": _ts,
    #                      "ref_key_2": _id })
    #         _db_insert_child(data)

    # elif btn_delete and selected_row is not None and data.get("id"):
    #     _db_delete_by_id_child(data)

def _crud_display_grid_form_team(form_name, ref_type=TABLE_PERSON, ref_key="",  
                            page_size=10, grid_height=370):
    """Render grid according to column properties, 
    used to display a database table, or child table when ref_type/_key are given

    Inputs:
        form_name (required): 
            table name if ref_type is not given

        ref_type: must be parent table name if given, form_name can be different from underlying table name
        ref_key: foreign key

    Outputs:
    Buttons on top for Upsert, Delete action
    Fields below in columns: 1, 2, or 3 specified by 'form_column'
    """

    table_name = form_name
    # validate table_name exists
    if not table_name in COLUMN_DEFS:
        st.error(f"Invalid table name: {table_name}")
        return 
    
    COL_DEFS = COLUMN_DEFS[TABLE_PERSON]
    visible_columns = COL_DEFS["is_visible"]
    editable_columns = COL_DEFS["is_editable"]
    clickable_columns = COL_DEFS["is_clickable"]
    st.session_state["form_name"] = form_name
    st.session_state["visible_columns"] = visible_columns

    selected_cols = ",".join([f"p.{c}" for c in visible_columns])
    select_sql = f"""
        with per as (
            select 
                pt.ref_key_2 person_url
            from {TABLE_TEAM} t 
            join {TABLE_PERSON_TEAM} pt
                on pt.ref_key = t.url 
                    and pt.ref_type = '{TABLE_TEAM}' 
                    and pt.ref_type_2 = '{TABLE_PERSON}' 
            where t.team_lead = '{ref_key}'
        )
        select {selected_cols} 
        from {TABLE_PERSON} p
        join per 
            on per.person_url = p.url
        where p.url != '{ref_key}';
    """
    

    with DBConn() as _conn:
        df = pd.read_sql(select_sql, _conn)
    grid_resp = _display_grid_df(df, 
                    selection_mode="single", 
                    page_size=page_size, 
                    grid_height=grid_height,
                    editable_columns=editable_columns,
                    clickable_columns=clickable_columns)
    selected_row = None
    if grid_resp:
        selected_rows = grid_resp['selected_rows']
        if selected_rows and len(selected_rows):
            selected_row = selected_rows[0]

    # st.write(f"selected_row:\n{selected_row}")

    old_row = {}
    dict_col_label = COL_DEFS['label_text']
    for col in visible_columns:
        old_row[col] = selected_row.get(col) if selected_row is not None else ""

    ## Form Layout

    # display buttons
    btn_save, btn_refresh, btn_delete = _crud_display_buttons()

    data = {"table_name": TABLE_PERSON, 
            "inter_table_name": TABLE_PERSON_TEAM, 
            "ref_type":TABLE_TEAM, 
            "team_lead":ref_key,
            "ref_type_2":TABLE_PERSON, 
            "ref_key_2":old_row.get("url"),
            }
    # display form and populate data dict
    col1_columns = COL_DEFS['col1_columns']
    col2_columns = COL_DEFS['col2_columns']

    idx_default = PERSON_TYPES.index("student")
    col1,col2 = st.columns([8,7])
    with col1:
        for col in col1_columns:
            widget_type = COL_DEFS['widget_type'][col]
            if widget_type == "text_area":
                kwargs = {"height":200}
                val = st.text_area(dict_col_label.get(col), value=old_row[col], key=f"col_{form_name}_{col}", kwargs=kwargs)
            else:
                kwargs = {}
                if col in COL_DEFS["is_system_col"]:
                    kwargs.update({"disabled":True})
                val = st.text_input(dict_col_label.get(col), value=old_row[col], key=f"col_{form_name}_{col}", kwargs=kwargs)

            if val != old_row[col]:
                data.update({col : val})

    with col2:
        for col in col2_columns:
            if col == "person_type":
                val = st.selectbox(dict_col_label.get(col), options=PERSON_TYPES, index=idx_default, key=f"col_{form_name}_{col}")
            else:
                widget_type = COL_DEFS['widget_type'][col]
                if widget_type == "text_area":
                    kwargs = {"height":200}
                    val = st.text_area(dict_col_label.get(col), value=old_row[col], key=f"col_{form_name}_{col}", kwargs=kwargs)
                else:
                    kwargs = {}
                    if col in COL_DEFS["is_system_col"]:
                        kwargs.update({"disabled":True})
                    val = st.text_input(dict_col_label.get(col), value=old_row[col], key=f"col_{form_name}_{col}", kwargs=kwargs)

            if val != old_row[col]: 
                data.update({col : val})

    # copy id if present
    id_val = old_row.get("id", "")
    if id_val:
        data.update({"id" : id_val})

    # st.write(f"data={data}")

    # handle buttons
    if btn_save:
        _ts = str(datetime.now())
        if selected_row is not None and data.get("id"):
            data.update({"ts": _ts,})
            _db_update_by_id(data)
        else:
            _id = str(uuid4())
            data.update({"id": _id, 
                         "ts": _ts })
            _db_insert_person_team(data)

    elif btn_delete and selected_row is not None and data.get("id"):
        _db_delete_person_team(data)

# _STR_MENU_NOTE
def _crud_display_grid_form_subject(table_name, 
                    ref_key="", 
                    ref_val="", 
                    form_name_suffix="", 
                    orderby_cols=["name"], 
                    page_size=10, grid_height=400):
    """Render data grid defined by column properties, 
    for table, or child table when (ref_key,ref_val) are given

    Inputs:
        table_name (required): 
        form_name_suffix (optional) : used for different view on the same underlying table

        (ref_key,ref_val) : reference parent entity

    Outputs:
    Buttons: Upsert, Refresh, Delete 
    Fields in 2 columns: configured by 'form_column' prop
    """
    if not table_name in COLUMN_PROPS or not table_name in COLUMN_DEFS:
        st.error(f"Invalid table name: {table_name}")
        return
     
    form_name = f"{table_name}#{form_name_suffix}"
    st.session_state["form_name"] = form_name

    COL_DEFS = COLUMN_DEFS[table_name]
    visible_columns = COL_DEFS["is_visible"]
    editable_columns = COL_DEFS["is_editable"]
    clickable_columns = COL_DEFS["is_clickable"]

    # make sure orderby_cols exists
    orderby_cols = list(set(orderby_cols).intersection(set(visible_columns)))

    # prepare dataframe
    with DBConn() as _conn:
        orderby_clause = f' order by {",".join(orderby_cols)}' if orderby_cols else ""
        where_clause = f"""
            where ref_key = '{ref_key}'
            and ref_val = '{ref_val}'
        """ if ref_key and ref_val else ""
        selected_cols = _push_selected_cols_to_end(visible_columns, selected_cols=["ref_key","ref_val"])
        selected_cols = _push_selected_cols_to_end(selected_cols, selected_cols=SYS_COLS)
        sql_stmt = f"""
            select {",".join(selected_cols)}
            from {table_name} 
            {where_clause}
            {orderby_clause};
        """
        df = pd.read_sql(sql_stmt, _conn)

    ## show data grid
    grid_resp = _display_grid_df(df, 
                    selection_mode="single", 
                    page_size=page_size, 
                    grid_height=grid_height,
                    editable_columns=editable_columns,
                    clickable_columns=clickable_columns)
    selected_row = None
    if grid_resp:
        selected_rows = grid_resp['selected_rows']
        if selected_rows and len(selected_rows):
            selected_row = selected_rows[0]

    ## layout form
    _layout_form(table_name, selected_row, ref_key=ref_key, ref_val=ref_val)

# _STR_MENU_RESEARCH_GROUP
def _crud_display_grid_form_entity(table_name, 
                            entity_type="research_group",
                            orderby_cols=["name"],
                            page_size=10, grid_height=370):
    """Render grid according to column properties, 
    used to display a database table, or child table when ref_type/_key are given

    Inputs:
        table_name (required): 

    Outputs:
    Buttons on top for Upsert, Delete action
    Fields below in columns: 1, 2, or 3 specified by 'form_column'
    """
    # validate table_name exists
    # st.write(COLUMN_PROPS.keys())
    if not table_name in COLUMN_PROPS or not table_name in COLUMN_DEFS:
        st.error(f"Invalid table name: {table_name}")
        return
    
    form_name = f"{table_name}#{entity_type}"
    st.session_state["form_name"] = form_name

    COL_DEFS = COLUMN_DEFS[table_name]
    visible_columns = COL_DEFS["is_visible"]
    editable_columns = COL_DEFS["is_editable"]
    clickable_columns = COL_DEFS["is_clickable"]

    with DBConn() as _conn:
        orderby_clause = f' order by {",".join(orderby_cols)}' if orderby_cols else ' '
        where_clause = f" where entity_type = '{entity_type}' " if entity_type else ""
        selected_cols = _push_selected_cols_to_end(visible_columns, selected_cols=["entity_type"])
        selected_cols = _push_selected_cols_to_end(selected_cols, selected_cols=SYS_COLS)
        sql_stmt = f"""
            select {", ".join(selected_cols)}
            from {table_name} 
            {where_clause}
            {orderby_clause};
        """
        # print(sql_stmt)
        df = pd.read_sql(sql_stmt, _conn)

    ## show data grid
    grid_resp = _display_grid_df(df, 
                    selection_mode="single", 
                    page_size=page_size, 
                    grid_height=grid_height,
                    editable_columns=editable_columns,
                    clickable_columns=clickable_columns)
    selected_row = None
    if grid_resp:
        selected_rows = grid_resp['selected_rows']
        if selected_rows and len(selected_rows):
            selected_row = selected_rows[0]

    ## layout form
    _layout_form(table_name, selected_row, entity_type=entity_type)

def _crud_display_buttons():
    """button UI key: btn_<table_name>_action
        action: refresh, upsert, delete
    """
    form_name = st.session_state.get("form_name", "")
    if not form_name: 
        return
    c_save, c_refresh, _, c_delete, c_info = st.columns([3,3,3,3,7])
    with c_save:
        btn_save = st.button(STR_SAVE, key=f"btn_{form_name}_upsert")
    with c_refresh:
        btn_refresh = st.button(STR_REFRESH, key=f"btn_{form_name}_refresh", on_click=_crud_clear_form)
    with c_delete:
        btn_delete = st.button(STR_DELETE, key=f"btn_{form_name}_delete")
    with c_info:
        st.info(STR_REFRESH_HINT)
    return btn_save, btn_refresh, btn_delete

def _crud_clear_form():
    form_name = st.session_state.get("form_name", "")
    if not form_name: 
        return

    for col in st.session_state.get("visible_columns", []):
        col_key = f"col_{form_name}_{col}"
        if not col_key in st.session_state: 
            continue
        st.session_state[col_key] = ""




### quick add note
def _sidebar_display_add_note(form_name="new_note"):
    with st.expander(f"{STR_QUICK_ADD}", expanded=False):
        st.write(NOTE_DATA_COLS)
        with st.form(key=form_name):
            for col in NOTE_DATA_COLS:
                st.text_input(_gen_label(col), value="", key=f"{form_name}_{col}")
            st.form_submit_button(STR_ADD, on_click=_sidebar_add_note)

def _sidebar_add_note(form_name="new_note"):
    _title = st.session_state.get(f"{form_name}_title","")
    if not _title: return

    data = {
        "table_name": TABLE_NOTE,
        "id": uuid4(), 
        "ts": str(datetime.now()),
    }
    
    for col in NOTE_DATA_COLS:
        data.update({col: st.session_state.get(f"{form_name}_{col}","")})
    _db_insert(data)

    _sidebar_clear_note_form()

def _sidebar_clear_note_form(form_name="new_note"):
    for col in NOTE_DATA_COLS:
        st.session_state[f"{form_name}_{col}"] = ""


### quick add group
def _sidebar_display_add_group(form_name="new_group"):
    with st.expander(f"{STR_QUICK_ADD}", expanded=False):
        with st.form(key=form_name):
            for col in GROUP_DATA_COLS:
                st.text_input(_gen_label(col), value="", key=f"{form_name}_{col}")
            st.form_submit_button(STR_ADD, on_click=_sidebar_add_group)


def _sidebar_add_group(form_name="new_group"):
    _research_group = st.session_state.get(f"{form_name}_research_group","")
    if not _research_group: return

    data = {
        "table_name": TABLE_RESEARCH_GROUP
    }
    for col in GROUP_DATA_COLS:
        data.update({col: st.session_state.get(f"{form_name}_{col}","")})
    _db_upsert_group(data)

    _sidebar_clear_group_form()

def _sidebar_clear_group_form(form_name="new_group"):
    for col in GROUP_DATA_COLS:
        st.session_state[f"{form_name}_{col}"] = ""

### quick add faculty
def _sidebar_display_add_faculty(form_name="new_faculty"):
    with st.expander(f"{STR_QUICK_ADD}", expanded=False):
        with st.form(key=form_name):
            for col in FACULTY_DATA_COLS:
                st.text_input(_gen_label(col), value="", key=f"{form_name}_{col}")
            st.form_submit_button(STR_ADD, on_click=_sidebar_add_faculty)

def _sidebar_add_faculty(form_name="new_faculty"):
    _name = st.session_state.get(f"{form_name}_name","")
    if not _name: return

    data = {
        "table_name": TABLE_FACULTY
    }

    for col in FACULTY_DATA_COLS:
        data.update({col: st.session_state.get(f"{form_name}_{col}","")})
    _db_upsert_faculty(data)

    _sidebar_clear_faculty_form()

def _sidebar_clear_faculty_form(form_name="new_faculty"):
    for col in FACULTY_DATA_COLS:
        st.session_state[f"{form_name}_{col}"] = ""


#####################################################
# Menu Handlers
#####################################################
def do_welcome():
    st.header("CS Faculty")

    st.markdown(f"""
    #### Intro 
    This app helps one manage and track CS faculty and research information.

    It is built on [Streamlit](https://streamlit.io/) (frontend) and [DuckDb](https://duckdb.org/) (backend). All the logic is written in python, no HTML/CSS/JS is involved.
    
    The GitHub source code is at: https://github.com/wgong/cs-faculty
    
    The CS Faculty dataset is [scraped](https://github.com/wgong/py4kids/tree/master/lesson-11-scrapy/scrap-cs-faculty) from the following CS Faculty homepages:
    - [MIT-AID](https://www.eecs.mit.edu/role/faculty-aid/)
    - [MIT-CS](https://www.eecs.mit.edu/role/faculty-cs/)
    - [Stanford-CS](https://cs.stanford.edu/directory/faculty)
    - [CMU-CS](https://csd.cmu.edu/people/faculty)
    - [UCB-CS](https://www2.eecs.berkeley.edu/Faculty/Lists/CS/faculty.html)
    - [UIUC-CS](https://cs.illinois.edu/about/people/department-faculty)
    - [Cornell-CS](https://www.cs.cornell.edu/people/faculty)
    
    #### Additional Resources
    - [CS Faculty Composition and Hiring Trends (Blog)](https://jeffhuang.com/computer-science-open-data/#cs-faculty-composition-and-hiring-trends)
    - [2200 Computer Science Professors in 50 top US Graduate Programs](https://cs.brown.edu/people/apapouts/faculty_dataset.html)
    - [CS Professors (Data Explorer)](https://drafty.cs.brown.edu/csprofessors?src=csopendata)
    - [Drafty Project](https://drafty.cs.brown.edu/)
    - [CSRankings.org](https://csrankings.org/#/fromyear/2011/toyear/2023/index?ai&vision&mlmining&nlp&inforet&act&crypt&log&us)

    """, unsafe_allow_html=True)


def do_faculty():
    st.subheader(f"{_STR_MENU_FACULTY}")
    _display_grid_faculty()

def do_research_group():
    st.subheader(f"{_STR_MENU_RESEARCH_GROUP}")
    _crud_display_grid_form_entity(TABLE_ENTITY, entity_type="research_group")

def do_person():
    st.subheader(f"{_STR_MENU_PERSON}")
    _crud_display_grid_form_subject(TABLE_PERSON)

def do_work():
    st.subheader(f"{_STR_MENU_WORK}")
    _crud_display_grid_form_subject(TABLE_WORK)

def do_note():
    st.subheader(f"{_STR_MENU_NOTE}")
    _crud_display_grid_form_subject(TABLE_NOTE)




#####################################################
# setup menu_items 
#####################################################
menu_dict = {
    _STR_MENU_HOME :                {"fn": do_welcome},
    _STR_MENU_FACULTY:              {"fn": do_faculty},
    _STR_MENU_RESEARCH_GROUP:       {"fn": do_research_group},
    _STR_MENU_PERSON:               {"fn": do_person},
    _STR_MENU_WORK:                 {"fn": do_work},
    _STR_MENU_NOTE:                 {"fn": do_note},

}

## sidebar Menu
def do_sidebar():
    menu_options = list(menu_dict.keys())
    default_ix = menu_options.index(_STR_MENU_HOME)

    with st.sidebar:
        st.markdown(f"<h1><font color=red>{_STR_APP_NAME}</font></h1>",unsafe_allow_html=True) 

        menu_item = st.selectbox("Menu:", menu_options, index=default_ix, key="menu_item")
        # keep menu item in the same order as i18n strings

        if menu_item == _STR_MENU_FACULTY:
            _sidebar_display_add_faculty()

        elif menu_item == _STR_MENU_RESEARCH_GROUP:
            _sidebar_display_add_group()

        elif menu_item == _STR_MENU_NOTE:
            _sidebar_display_add_note()

        else:
            pass

# body
def do_body():
    menu_item = st.session_state.get("menu_item", _STR_MENU_HOME)
    menu_dict[menu_item]["fn"]()

def main():
    _load_db()
    do_sidebar()
    do_body()

if __name__ == '__main__':
    main()
