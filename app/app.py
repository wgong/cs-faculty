"""
Streamlit app to manage CS Faculty data backed by DuckDB 

"""
__author__ = "wgong"
SRC_URL = "https://github.com/wgong/cs_faculty"

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

from db import *
from cfg import *

import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode

##====================================================
_STR_APP_NAME               = "CS Faculty"

st.set_page_config(
     page_title=f'{_STR_APP_NAME}',
     layout="wide",
     initial_sidebar_state="expanded",
)

# DBU_ = DBUtils()

_STR_MENU_HOME              = "Welcome"
_STR_MENU_FACULTY           = "Faculty"
_STR_MENU_RESEARCH_GROUP    = "Research Group"
_STR_MENU_NOTE             = "Note"

STR_DOUBLE_CLICK = "Double-click to commit changes"
STR_FETCH_LOG = "Get the latest log"


# Aggrid options
_GRID_OPTIONS = {
    "grid_height": 350,
    "return_mode_value": DataReturnMode.__members__["FILTERED"],
    "update_mode_value": GridUpdateMode.__members__["MODEL_CHANGED"],
    "fit_columns_on_grid_load": False,   # False to display wide columns
    # "min_column_width": 50, 
    "selection_mode": "single",  #  "multiple",  # 
    "allow_unsafe_jscode": True,
    "groupSelectsChildren": True,
    "groupSelectsFiltered": True,
    "enable_pagination": True,
    "paginationPageSize": 10,
}

NOTE_DATA_COLS = [col for col in TABLE_COLUMNS["t_note"] if col not in ["id", "ts"]]
#####################################################
# Helpers (prefix with underscore)
#####################################################

def _escape_single_quote(s):
    return s.replace("\'", "\'\'")

def _unescape_single_quote(s):
    return s.replace("\'\'", "\'")


def _load_db():

    if not Path(FILE_DB).exists():
        if not Path(FILE_XLSX).exists():
            raise Exception(f"source file: {FILE_XLSX} missing")
        
        xls = pd.ExcelFile(FILE_XLSX)
        sheet_name = "Faculty"
        df_faculty = pd.read_excel(xls, sheet_name, keep_default_na=False)
        sheet_name = "Research Groups"
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
                    editable_columns=[]):
    """show df in a grid and return selected row
    """
    # st.dataframe(df) 
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection(selection_mode,
            use_checkbox=True,
            groupSelectsChildren=_GRID_OPTIONS["groupSelectsChildren"], 
            groupSelectsFiltered=_GRID_OPTIONS["groupSelectsFiltered"]
        )
    gb.configure_pagination(paginationAutoPageSize=False, 
        paginationPageSize=page_size)
    gb.configure_columns(editable_columns, editable=True)
    gb.configure_grid_options(domLayout='normal')
    grid_response = AgGrid(
        df, 
        gridOptions=gb.build(),
        height=grid_height, 
        # width='100%',
        data_return_mode=_GRID_OPTIONS["return_mode_value"],
        update_mode=_GRID_OPTIONS["update_mode_value"],
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

def _db_select_note(table_name=TABLE_NOTE, orderby_cols = ["ts desc"]):
    with DBConn() as _conn:
        sql_stmt = f"""
            select {",".join(TABLE_COLUMNS[table_name])}
            from {table_name} 
            order by {",".join(orderby_cols)};
        """
        return pd.read_sql(sql_stmt, _conn)

def _db_delete_note(data, table_name=TABLE_NOTE):
    if not data: 
        return
    
    primary_key = data.get("id")
    if not primary_key:
        print(f"[ERROR] missing primary key: 'id'")
        return    
    
    delete_sql = f"""
        delete from {table_name}
        where id = '{primary_key}';
    """
    _db_execute(delete_sql)         

def _db_update_note(data, table_name=TABLE_NOTE):
    if not data or len(data) < 3: 
        return
    
    primary_key = data.get("id")
    if not primary_key:
        print(f"[ERROR] missing primary key: 'id'")
        return    

    # build SQL
    all_cols = TABLE_COLUMNS[table_name]
    set_clause = []
    for col,val in data.items():
        if col == "id": 
            continue
        if col not in all_cols:
            print(f"[WARN] column '{col}' not found in {str(all_cols)}")
            continue
        set_clause.append(f"{col} = '{_escape_single_quote(val)}'")
    update_sql = f"""
        update {table_name}
        set {', '.join(set_clause)}
        where id = '{primary_key}';
    """
    _db_execute(update_sql)   

def _db_insert_note(data, table_name=TABLE_NOTE):
    if not data: 
        return
    
    primary_key = data.get("id")
    if not primary_key:
        print(f"[ERROR] missing primary key: 'id'")
        return    

    all_cols = TABLE_COLUMNS[table_name]
    # build SQL
    col_clause = []
    val_clause = []
    for col,val in data.items():
        if col not in all_cols:
            print(f"[WARN] column '{col}' not found in {str(all_cols)}")
            continue
        col_clause.append(col) 
        if col in ["id","ts"]:
            val_clause.append(f"'{val}'")
        else:
            val_clause.append(f"'{_escape_single_quote(val)}'")

    insert_sql = f"""
        insert into {table_name} (
            {",".join(col_clause)}
        )
        values (
            {",".join(val_clause)}
        );
    """
    _db_execute(insert_sql)


def _db_select(table_name=TABLE_FACULTY, orderby_cols=[]):
    with DBConn() as _conn:
        orderby_clause = f' order by {",".join(orderby_cols)}' if orderby_cols else ' '
        sql_stmt = f"""
            select {",".join(TABLE_COLUMNS[table_name])}
            from {table_name} 
            {orderby_clause};
        """
        return pd.read_sql(sql_stmt, _conn)

def _display_grid(form_name=TABLE_FACULTY, orderby_cols=[]):
    st.session_state["form_name"] = form_name
    all_cols = TABLE_COLUMNS[form_name]
    df = _db_select(table_name=form_name, orderby_cols=orderby_cols)
    grid_response = _display_grid_df(df, 
                            selection_mode="single", 
                            page_size=10, 
                            grid_height=370,
                            editable_columns=EDITABLE_COLUMNS[form_name]
                    )
    selected_row = None
    if grid_response:
        selected_rows = grid_response['selected_rows']
        if selected_rows and len(selected_rows):
            selected_row = selected_rows[0]


def _clear_form():
    form_name = st.session_state.get("form_name", TABLE_NOTE)  # same as table_name
    if not form_name: return
    for col in TABLE_COLUMNS[form_name]:
        ui_key = f"col_{form_name}_{col}"
        if not ui_key in st.session_state: continue
        st.session_state[ui_key] = ""

def _display_buttons(form_name=TABLE_NOTE):
    """button UI key: btn_<table_name>_action
        action: refresh, insert, update, delete
    """
    st.session_state["form_name"] = form_name
    c0, c1, c2, c3, _, c4 = st.columns([2,2,2,2,4,6])
    with c0:
        btn_refresh = st.button('Refresh', key=f"btn_{form_name}_refresh", on_click=_clear_form)
    with c1:
        btn_add = st.button("  Add ", key=f"btn_{form_name}_insert")
    with c2:
        btn_update = st.button("Update", key=f"btn_{form_name}_update")
    with c3:
        btn_delete = st.button("Delete", key=f"btn_{form_name}_delete")
    with c4:
        st.info("Click 'Refresh' button to clear form")
    return btn_refresh,btn_add,btn_update,btn_delete

def _display_grid_note(form_name=TABLE_NOTE):
    st.session_state["form_name"] = form_name
    all_cols = TABLE_COLUMNS[form_name]
    df_note = _db_select_note()
    grid_response = _display_grid_df(df_note, 
                        selection_mode="single", 
                        page_size=10, 
                        grid_height=370,
                        editable_columns=EDITABLE_COLUMNS[form_name],
                    )
    selected_row = None
    if grid_response:
        selected_rows = grid_response['selected_rows']
        if selected_rows and len(selected_rows):
            selected_row = selected_rows[0]

    dict_old_val = {}
    for col in all_cols:
        dict_old_val[col] = selected_row.get(col) if selected_row is not None else ""

    dict_col_label = {col: col.capitalize() for col in all_cols}
    dict_col_label.update({"id": "ID","ts": "Timestamp","url": "URL"})

    btn_refresh,btn_add,btn_update,btn_delete = _display_buttons(form_name=form_name)

    # setup form and populate data dict
    col_left,col_right = st.columns([9,5])
    data = {}
    with col_left:
        left_columns = ["title", "url", "tags"]
        for col in left_columns:
            val = st.text_input(dict_col_label.get(col), value=dict_old_val[col], key=f"col_{form_name}_{col}")
            if val != dict_old_val[col]: 
                data.update({col : val})

    with col_right:
        right_columns = ["id", "ts", "note"]
        col = "id"     # read only
        val = st.text_input(dict_col_label.get(col), value=dict_old_val[col], key=f"col_{form_name}_{col}", disabled=True)
        data.update({col : val})

        col = "ts"
        val = st.text_input(dict_col_label.get(col), value=dict_old_val[col], key=f"col_{form_name}_{col}")
        data.update({col : val})

        col = "note"   # text_area
        val = st.text_area(dict_col_label.get(col), value=dict_old_val[col], height=125, key=f"col_{form_name}_{col}")
        if val != dict_old_val[col]: 
            data.update({col : val})

    if btn_add and any([data.get(col) for col in all_cols if col not in ["id","ts"]]):
        if data.get("id"):
            data.update({"ts": str(datetime.now()),})
            _db_update_note(data)
        else:
            data.update({"id": str(uuid4()), "ts": str(datetime.now()),})
            _db_insert_note(data)

    elif btn_update and selected_row is not None:
        data.update({"ts": str(datetime.now()),})
        _db_update_note(data)

    elif btn_delete and selected_row is not None:
        _db_delete_note(data)

    # not working
    # if any([btn_add, btn_update, btn_delete]):
    #     _clear_form()

# quick add note (not required, will remove)
def _sidebar_display_add_note(form_name="new_note"):
    with st.expander("Add Note", expanded=True):
        with st.form(key=form_name):
            for col in NOTE_DATA_COLS:
                st.text_input(col.capitalize(), value="", key=f"{form_name}_{col}")
            st.form_submit_button('Add', on_click=_sidebar_add_note)

def _sidebar_add_note(form_name="new_note"):
    _title = st.session_state.get(f"{form_name}_title","")
    if not _title: return

    data = {
        "id": uuid4(), 
        "ts": str(datetime.now()),
    }
    
    for col in NOTE_DATA_COLS:
        data.update({col: st.session_state.get(f"{form_name}_{col}","")})
    _db_insert_note(data)
    _sidebar_clear_note_form()

def _sidebar_clear_note_form(form_name="new_note"):
    for col in NOTE_DATA_COLS:
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
    """, unsafe_allow_html=True)



def do_faculty():
    st.subheader(f"{_STR_MENU_FACULTY}")
    _display_grid(form_name=TABLE_FACULTY, orderby_cols=["name"])

def do_research_group():
    st.subheader(f"{_STR_MENU_RESEARCH_GROUP}")
    _display_grid(form_name=TABLE_RESEARCH_GROUP, orderby_cols=["research_group"])

def do_note():
    st.subheader(f"{_STR_MENU_NOTE}")
    _display_grid_note()



#####################################################
# setup menu_items 
#####################################################
menu_dict = {
    _STR_MENU_HOME :                {"fn": do_welcome},
    _STR_MENU_FACULTY:              {"fn": do_faculty},
    _STR_MENU_RESEARCH_GROUP:       {"fn": do_research_group},
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

        if menu_item == _STR_MENU_NOTE:
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
