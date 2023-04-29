"""
Streamlit app to manage CS Faculty data backed by DuckDB 


TODO:
- [2023-04-21] 
    - upgrade streamlit to 1.21
    - replace st.cache to st.cache_data

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
from pathlib import Path
import pandas as pd
from shutil import copy
import sys
from traceback import format_exc
from uuid import uuid4
import yaml

import warnings
warnings.filterwarnings("ignore")

import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode

from db import *
from config import *
from helper import (escape_single_quote, df_to_csv)

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
STR_REFRESH_HINT    = "Click 'Refresh' button to clear form"
STR_DOWNLOAD_CSV    = "Download CSV"

## menu
_STR_MENU_HOME              = STR_WELCOME
_STR_MENU_FACULTY           = STR_FACULTY
_STR_MENU_RESEARCH_GROUP    = STR_RESEARCH_GROUP
_STR_MENU_NOTE              = STR_NOTE
_STR_MENU_NOTE_2      = STR_NOTE + "-2"



# Aggrid options
_GRID_OPTIONS = {
    "grid_height": 350,
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
@st.cache
def _gen_label(col):
    "Convert table column into form label"
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
    return [k for k,v in COLUMN_PROPS[table_name].items() if v.get(prop_name, False) ]


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
                    ,title text not null
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

###################################################################
# handle Note
# ======================================
def _db_execute(sql_statement, DEBUG=True):
    with DBConn() as _conn:
        if DEBUG: print(sql_statement)
        _conn.execute(sql_statement)
        _conn.commit()           

def _db_select(table_name=TABLE_NOTE, orderby_cols=[]):
    """Select whole table"""
    with DBConn() as _conn:
        orderby_clause = f' order by {",".join(orderby_cols)}' if orderby_cols else ' '
        sql_stmt = f"""
            select {",".join(TABLE_COLUMNS[table_name])}
            from {table_name} 
            {orderby_clause};
        """
        return pd.read_sql(sql_stmt, _conn)

def _db_select_by_key(table_name=TABLE_NOTE, key_value=""):
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

def _db_delete(data):
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

    return _db_select(table_name=table_name)        

def _db_delete_by_id(data):
    if not data: 
        return None
    
    table_name = data.get("table_name", "")
    if not table_name:
        raise Exception(f"[ERROR] Missing key: table_name: {data}")

    id_val = data.get("id", "")
    if not id_val:
        return None
    
    delete_sql = f"""
        delete from {table_name}
        where id = '{id_val}';
    """
    _db_execute(delete_sql)

    return _db_select(table_name=table_name)        

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

    return _db_select(table_name=table_name) 

def _db_update_by_id(data):
    if not data: 
        return None
    
    table_name = data.get("table_name", "")
    if not table_name:
        raise Exception(f"[ERROR] Missing key: table_name: {data}")

    id_val = data.get("id", "")
    if not id_val:
        return None

    editable_columns = _get_columns(table_name, prop_name="is_editable")

    # build SQL
    set_clause = []
    for col,val in data.items():
        if col not in editable_columns: 
            continue
        set_clause.append(f"{col} = '{escape_single_quote(val)}'")

    if set_clause:
        update_sql = f"""
            update {table_name}
            set {', '.join(set_clause)}
            where id = '{id_val}';
        """
        _db_execute(update_sql)   

    return _db_select(table_name=table_name) 

def _db_insert(data):
    if not data: 
        return None
    
    table_name = data.get("table_name", "")
    if not table_name:
        raise Exception(f"[ERROR] Missing key: table_name: {data}")

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

    return _db_select(table_name=table_name) 

def _db_upsert_group(data, table_name=TABLE_RESEARCH_GROUP):
    _research_group = data.get("research_group", "")
    if not _research_group: return None

    with DBConn() as _conn:
        df = pd.read_sql(f"""
            select research_group from {table_name}
            where research_group='{_research_group}';
        """, _conn)

    _url = data.get("url", "")
    if df.shape[0] > 0:  # update
        sql_stmt = f"""
            update {table_name}
            set url = '{_url}'
            where research_group='{_research_group}';
        """
    else:
        sql_stmt = f"""
            insert into {table_name} (research_group, url)
            values ('{_research_group}', '{_url}');
        """
    _db_execute(sql_stmt)

    return _db_select(table_name=table_name) 

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

    return _db_select(table_name=table_name) 

def _move_url_2nd(df, url_col="url"):
    cols = df.columns
    if not url_col in cols:
        return df
    cols_new = [cols[0], url_col] + [c for c in cols[1:] if c != url_col]
    return df[cols_new]

def _display_grid(form_name=TABLE_RESEARCH_GROUP, 
                  orderby_cols=[], 
                  selection_mode="single"):
    st.session_state["form_name"] = form_name
    all_cols = TABLE_COLUMNS[form_name]
    df = _db_select(table_name=form_name, orderby_cols=orderby_cols)

    grid_resp = _display_grid_df(df, 
                            selection_mode=selection_mode, 
                            page_size=10, 
                            grid_height=370,
                            editable_columns=EDITABLE_COLUMNS[form_name],
                            clickable_columns=CLICKABLE_COLUMNS[form_name],
                    )
    selected_row = {}
    if grid_resp and grid_resp.get('selected_rows'):
        selected_row = grid_resp['selected_rows'][0]

    if not selected_row:
        return
    
    if st.button("Save", key=f"{form_name}_save"):
        data = selected_row
        data.update({"table_name": form_name})
        _ = _db_update(data=data)

def _display_grid_faculty(form_name=TABLE_FACULTY, 
                  orderby_cols=["name"], 
                  selection_mode="single"):
    st.session_state["form_name_parent"] = form_name
    all_cols = TABLE_COLUMNS[form_name]
    df = _db_select(table_name=form_name, orderby_cols=orderby_cols)
    df = _move_url_2nd(df)
    grid_resp = _display_grid_df(df, 
                            selection_mode=selection_mode, 
                            page_size=10, 
                            grid_height=370,
                            editable_columns=EDITABLE_COLUMNS[form_name],
                            clickable_columns=CLICKABLE_COLUMNS[form_name],
                    )
    
    selected_row = {}
    if grid_resp and grid_resp.get('selected_rows'):
        selected_row = grid_resp['selected_rows'][0]

    if not selected_row:
        return

    if st.button("Save", key=f"{form_name}_save"):
        data = selected_row
        data.update({"table_name": form_name})
        _ = _db_update(data=data)

    primary_key = selected_row.get("url")
    if not primary_key:
        print(f"[ERROR] Missing primary key: 'url' field")
        return
    
    # NOTE:
    # when using st.tab, grid not displayed correctly
    # use st.selectbox instead
    menu_options = ["Work", "Team", "Note"]
    default_ix = menu_options.index("Note")
    data_dict = {
        "Work": {
            "table": "t_person_work",
            "sql": f"""
                select w.* from t_person_work pw
                join t_work w
                    on pw.ref_type_2 = 't_work' and pw.ref_key_2 = w.id
                where pw.ref_type = 't_faculty'
                and pw.ref_key = '{primary_key}'
            """,
        },
        "Team": {
            "table": "t_person_team",
            "sql": f"""
                with team as (
                    select ref_key as team_url
                    from t_person_team
                    where ref_type = 't_team' and
                    ref_type_2 = 't_faculty' and ref_key_2 = '{primary_key}'
                )
                select p.* 
                from t_person p 
                join t_person_team pt
                    on pt.ref_type_2 = 't_person' and pt.ref_key_2 = p.url
                join team t
                    on pt.ref_type = 't_team' and pt.ref_key = t.team_url
            """,
        },
        "Note": {
            "table": "t_note",
            "sql": f"""
                select * from t_note
                where ref_type = 't_faculty' and ref_key = '{primary_key}'  
            """,
        },
    }

    faculty_name = selected_row.get("name")
    menu_item = st.selectbox(f"{faculty_name} : {primary_key}", 
                                menu_options, index=default_ix, key="faculty_menu_item")

    if menu_item == "Note":
        form_name = "t_note"
        _crud_display_grid_form(form_name, ref_type="t_faculty", ref_key=primary_key,
                                page_size=5, grid_height=200)
    else:
        with DBConn() as _conn:
            df = pd.read_sql(data_dict[menu_item]["sql"], _conn)
            child_grid_resp = _display_grid_df(df,
                        selection_mode="single", 
                        page_size=5, 
                        grid_height=200,
                        clickable_columns=["url"],                                             
                    )

def _crud_display_grid_form(form_name, ref_type="", ref_key="", orderby_cols=[], 
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
    if not table_name in COLUMN_PROPS:
        st.error(f"Invalid table name: {table_name}")
        return 
    COL_DEFS = COLUMN_PROPS[table_name]
    orderby_clause = f' order by {",".join(orderby_cols)}' if orderby_cols else ' '
    visible_columns = _get_columns(table_name, prop_name="is_visible")
    editable_columns = _get_columns(table_name, prop_name="is_editable")
    clickable_columns = _get_columns(table_name, prop_name="is_clickable")
    st.session_state["form_name"] = form_name
    st.session_state["visible_columns"] = visible_columns

    where_clause = ""
    with DBConn() as _conn:
        if ref_type and "ref_type" in COL_DEFS and \
            ref_key and "ref_key" in COL_DEFS:
            where_clause = f"""
                where ref_type = '{ref_type}'
                and ref_key = '{ref_key}'
            """
        sql_stmt = f"""
            select {",".join(visible_columns)}
            from {table_name} 
            {where_clause}
            {orderby_clause};
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

    old_row = {}
    dict_col_label = {}
    for col in visible_columns:
        old_row[col] = selected_row.get(col) if selected_row is not None else ""
        if 'label_text' in COL_DEFS[col]:
            dict_col_label[col] = COL_DEFS[col]['label_text']
        else:
            dict_col_label[col] = _gen_label(col)

    ## Form Layout

    # display buttons
    btn_save, btn_refresh, btn_delete = _crud_display_buttons()

    data = {"table_name": table_name, "ref_type":ref_type, "ref_key":ref_key}
    # display form and populate data dict
    col1_columns = []
    col2_columns = []
    for c in visible_columns:
        if COL_DEFS[c].get("form_column", "").startswith("col1-"):
            col1_columns.append(c)
        elif COL_DEFS[c].get("form_column", "").startswith("col2-"):
            col2_columns.append(c) 

    col1,col2 = st.columns([8,7])
    with col1:
        for col in col1_columns:
            widget_type = COL_DEFS[col].get("widget_type", "text_input")
            if widget_type == "text_area":
                kwargs = {"height":125}
                val = st.text_area(dict_col_label.get(col), value=old_row[col], key=f"col_{form_name}_{col}", kwargs=kwargs)
            else:
                kwargs = {}
                if COL_DEFS[col].get("is_system_col", False):
                    kwargs.update({"disabled":True})
                val = st.text_input(dict_col_label.get(col), value=old_row[col], key=f"col_{form_name}_{col}", kwargs=kwargs)

            if val != old_row[col]:
                data.update({col : val})

    with col2:
        for col in col2_columns:
            widget_type = COL_DEFS[col].get("widget_type", "text_input")
            if widget_type == "text_area":
                kwargs = {"height":125}
                val = st.text_area(dict_col_label.get(col), value=old_row[col], key=f"col_{form_name}_{col}", kwargs=kwargs)
            else:
                kwargs = {}
                if COL_DEFS[col].get("is_system_col", False):
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
        if selected_row is not None and data.get("id"):
            data.update({"ts": str(datetime.now()),})
            _ = _db_update_by_id(data)
        else:
            data.update({"id": str(uuid4()), "ts": str(datetime.now()),})
            _ = _db_insert(data)

    elif btn_delete and selected_row is not None and data.get("id"):
        _ = _db_delete_by_id(data)

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

def _crud_display_grid_form_all_notes(form_name=TABLE_NOTE):
    st.session_state["form_name"] = form_name
    all_cols = TABLE_COLUMNS[form_name]

    # display grid
    df_note = _db_select(table_name=form_name, orderby_cols = ["ts desc"])
    grid_resp = _display_grid_df(df_note, 
                        selection_mode="single", 
                        page_size=10, 
                        grid_height=370,
                        editable_columns=EDITABLE_COLUMNS[form_name],
                        clickable_columns=CLICKABLE_COLUMNS[form_name],
                    )
    selected_row = None
    if grid_resp:
        selected_rows = grid_resp['selected_rows']
        if selected_rows and len(selected_rows):
            selected_row = selected_rows[0]

    old_row = {}
    for col in all_cols:
        old_row[col] = selected_row.get(col) if selected_row is not None else ""

    dict_col_label = {col: _gen_label(col) for col in all_cols}

    ## Form Layout

    # display buttons
    btn_save, btn_refresh, btn_delete = _crud_display_buttons_all_notes(form_name=form_name)

    data = {"table_name": form_name}
    # display form and populate data dict
    col_left,col_right = st.columns([8,7])
    with col_left:
        left_columns = ["title", "url", "tags"]
        for col in left_columns:
            val = st.text_input(dict_col_label.get(col), value=old_row[col], key=f"col_{form_name}_{col}")
            if val != old_row[col]: 
                data.update({col : val})

    with col_right:
        right_columns = ["id", "note"]
        for col in right_columns:
            if col == "id":     # read only
                val = st.text_input(dict_col_label.get(col), value=old_row[col], key=f"col_{form_name}_{col}", disabled=True)
                data.update({col : val})

            elif col == "note":   # text_area
                val = st.text_area(dict_col_label.get(col), value=old_row[col], height=125, key=f"col_{form_name}_{col}")
                if val != old_row[col]: 
                    data.update({col : val})


    # handle buttons
    if btn_save:
        if selected_row is not None and data.get("id"):
            data.update({"ts": str(datetime.now()),})
            _ = _db_update(data)
        else:
            data.update({"id": str(uuid4()), "ts": str(datetime.now()),})
            _ = _db_insert(data)

    elif btn_delete and selected_row is not None and data.get("id"):
        _ = _db_delete(data)


def _crud_display_buttons_all_notes(form_name=TABLE_NOTE):
    """button UI key: btn_<table_name>_action
        action: refresh, upsert, delete
    """
    st.session_state["form_name"] = form_name
    c_save, c_refresh, _, c_delete, c_info = st.columns([3,3,4,2,7])
    with c_save:
        btn_save = st.button(STR_SAVE, key=f"btn_{form_name}_upsert")
    with c_refresh:
        btn_refresh = st.button(STR_REFRESH, key=f"btn_{form_name}_refresh", on_click=_crud_clear_form_all_notes)
    with c_delete:
        btn_delete = st.button(STR_DELETE, key=f"btn_{form_name}_delete")
    with c_info:
        st.info(STR_REFRESH_HINT)
    return btn_save, btn_refresh, btn_delete


def _crud_clear_form_all_notes():
    form_name = st.session_state.get("form_name", "")  # same as table_name
    if not form_name: return
    for col in TABLE_COLUMNS[form_name]:
        col_key = f"col_{form_name}_{col}"
        if not col_key in st.session_state: continue
        st.session_state[col_key] = ""


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


### quick add note
def _sidebar_display_add_note(form_name="new_note"):
    with st.expander(f"{STR_QUICK_ADD}", expanded=False):
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
    df_new = _db_insert(data)

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
    df_new = _db_upsert_group(data)

    _sidebar_clear_group_form()

def _sidebar_clear_group_form(form_name="new_group"):
    for col in GROUP_DATA_COLS:
        st.session_state[f"{form_name}_{col}"] = ""

### quick add faculty
def _sidebar_display_faculty(form_name="new_faculty"):
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
    df_new = _db_upsert_faculty(data)

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
    - [CS Faculty Composition and Hiring Trends (Blog)](https://jeffhuang.com/computer-science-open-data/#cs-faculty-composition-and-hiring-trends)
    - [2200 Computer Science Professors in 50 top US Graduate Programs](https://cs.brown.edu/people/apapouts/faculty_dataset.html)
    - [CS Professors (Data Explorer)](https://drafty.cs.brown.edu/csprofessors?src=csopendata)
    - [Drafty Project](https://drafty.cs.brown.edu/)
    - [CSRankings.org](https://csrankings.org/#/fromyear/2011/toyear/2023/index?ai&vision&mlmining&nlp&inforet&act&crypt&log&us)
    - [CS Faculty Info](https://github.com/wgong/py4kids/tree/master/lesson-11-scrapy/scrap-cs-faculty) : scraped a few top US CS schools (work in progress)
    - Schools:
        - [MIT-AID](https://www.eecs.mit.edu/role/faculty-aid/)
        - [MIT-CS](https://www.eecs.mit.edu/role/faculty-cs/)
        - [Stanford-CS](https://cs.stanford.edu/directory/faculty)
        - [CMU-CS](https://csd.cmu.edu/people/faculty)
        - [UCB-CS](https://www2.eecs.berkeley.edu/Faculty/Lists/CS/faculty.html)
        - [UIUC-CS](https://cs.illinois.edu/about/people/department-faculty)
        - [Cornell-CS](https://www.cs.cornell.edu/people/faculty)
    """, unsafe_allow_html=True)


def do_faculty():
    st.subheader(f"{_STR_MENU_FACULTY}")
    _display_grid_faculty()

def do_research_group():
    st.subheader(f"{_STR_MENU_RESEARCH_GROUP}")
    _display_grid(form_name=TABLE_RESEARCH_GROUP, orderby_cols=["research_group"])

def do_note():
    st.subheader(f"{_STR_MENU_NOTE}")
    _crud_display_grid_form("t_note")

def do_note_2():
    st.subheader(f"{_STR_MENU_NOTE_2}")
    _crud_display_grid_form_all_notes()

#####################################################
# setup menu_items 
#####################################################
menu_dict = {
    _STR_MENU_HOME :                {"fn": do_welcome},
    _STR_MENU_FACULTY:              {"fn": do_faculty},
    _STR_MENU_RESEARCH_GROUP:       {"fn": do_research_group},
    _STR_MENU_NOTE:                 {"fn": do_note},
    # _STR_MENU_NOTE_2:                 {"fn": do_note_2},
}

## sidebar Menu
def do_sidebar():
    menu_options = list(menu_dict.keys())
    default_ix = menu_options.index(_STR_MENU_HOME)

    with st.sidebar:
        st.markdown(f"<h1><font color=red>{_STR_APP_NAME}</font></h1>",unsafe_allow_html=True) 

        menu_item = st.selectbox("Menu:", menu_options, index=default_ix, key="menu_item")
        # keep menu item in the same order as i18n strings

        if menu_item == _STR_MENU_NOTE:
            _sidebar_display_add_note()

        elif menu_item == _STR_MENU_RESEARCH_GROUP:
            _sidebar_display_add_group()

        elif menu_item == _STR_MENU_FACULTY:
            _sidebar_display_faculty()

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
