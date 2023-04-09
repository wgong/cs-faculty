"""
Streamlit app to manage CS Faculty data backed by DuckDB 

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
from cfg import *
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

def _create_label(col):
    "Convert table column into form label"
    if "_" not in col:
        if col.upper() == "URL":
            return "URL"
        return col.capitalize()

    cols = []
    for c in col.split("_"):
        c  = c.strip()
        if not c: continue
        cols.append(c.capitalize())
    return " ".join(cols)

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

def _db_delete(data, table_name=TABLE_NOTE):
    if not data: 
        return None
    
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

def _db_update(data, table_name=TABLE_NOTE):
    if not data: 
        return None
    
    key_col = KEY_COLUMNS[table_name]
    key_val = data.get(key_col)
    if not key_val:
        print(f"[ERROR] missing primary key: '{key_col}'")
        return None
    
    df_old = _db_select_by_key(table_name=table_name, key_value=key_val).to_dict('records')
    if len(df_old) < 1:
        return None
    old_val = df_old[0]

    # build SQL
    all_cols = TABLE_COLUMNS[table_name]
    set_clause = []
    for col,val in data.items():
        if col == key_col or col == '_selectedRowNodeInfo': 
            continue
        if col not in all_cols:
            print(f"[WARN] column '{col}' not found in {str(all_cols)}")
            continue
        if val != old_val.get(col):
            set_clause.append(f"{col} = '{escape_single_quote(val)}'")

    if set_clause:
        update_sql = f"""
            update {table_name}
            set {', '.join(set_clause)}
            where {key_col} = '{key_val}';
        """
        _db_execute(update_sql)   

    return _db_select(table_name=table_name) 

def _db_insert(data, table_name=TABLE_NOTE):
    if not data: 
        return None
    
    key_col = KEY_COLUMNS[table_name]
    key_val = data.get(key_col)
    if not key_val:
        print(f"[ERROR] missing primary key: '{key_col}'")
        return None 

    all_cols = TABLE_COLUMNS[table_name]
    # build SQL
    col_clause = []
    val_clause = []
    for col,val in data.items():
        if col not in all_cols:
            print(f"[WARN] column '{col}' not found in {str(all_cols)}")
            continue
        col_clause.append(col) 
        if col == key_col:
            val_clause.append(f"'{val}'")
        else:
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

def _display_grid(form_name=TABLE_NOTE, 
                  orderby_cols=[], 
                  selection_mode="single"):
    st.session_state["form_name"] = form_name
    all_cols = TABLE_COLUMNS[form_name]
    df = _db_select(table_name=form_name, orderby_cols=orderby_cols)
    if form_name==TABLE_FACULTY:
        df = _move_url_2nd(df)
    grid_response = _display_grid_df(df, 
                            selection_mode=selection_mode, 
                            page_size=10, 
                            grid_height=370,
                            editable_columns=EDITABLE_COLUMNS[form_name],
                            clickable_columns=CLICKABLE_COLUMNS[form_name],
                    )
    selected_row = {}
    if grid_response and grid_response.get('selected_rows'):
        selected_row = grid_response['selected_rows'][0]

    df_new = None
    btn_save = st.button("Save", key=f"{form_name}_save")
    if btn_save and selected_row:
        df_new = _db_update(data=selected_row, table_name=form_name)

    if form_name.startswith("t_"):
        df_name = f"df_{form_name[2:]}"
        st.session_state[df_name] = df_new if df_new is not None else df

    if form_name == TABLE_FACULTY:
        faculty_name = selected_row.get("name")
        if not faculty_name:
            return
        
        st.subheader(f"{faculty_name}")
        
        tab1, tab2, tab3 = st.tabs(["Team", "Publications", "Notes"])

        with tab1:
            st.write(f"Team")

        with tab2:
            st.write(f"Publications")

        with tab3:
            st.write(f"Notes")


def _clear_form():
    form_name = st.session_state.get("form_name", TABLE_NOTE)  # same as table_name
    if not form_name: return
    for col in TABLE_COLUMNS[form_name]:
        ui_key = f"col_{form_name}_{col}"
        if not ui_key in st.session_state: continue
        st.session_state[ui_key] = ""

def _display_buttons(form_name=TABLE_NOTE):
    """button UI key: btn_<table_name>_action
        action: refresh, upsert, delete
    """
    st.session_state["form_name"] = form_name
    c0, c1, _, c2, c4 = st.columns([3,3,4,2,7])
    with c0:
        btn_save = st.button(STR_SAVE, key=f"btn_{form_name}_upsert")
    with c1:
        btn_refresh = st.button(STR_REFRESH, key=f"btn_{form_name}_refresh", on_click=_clear_form)
    with c2:
        btn_delete = st.button(STR_DELETE, key=f"btn_{form_name}_delete")
    with c4:
        st.info(STR_REFRESH_HINT)
    return btn_save, btn_refresh, btn_delete

def _display_grid_note(form_name=TABLE_NOTE):
    st.session_state["form_name"] = form_name
    all_cols = TABLE_COLUMNS[form_name]
    df_note = _db_select(table_name=form_name, orderby_cols = ["ts desc"])
    grid_response = _display_grid_df(df_note, 
                        selection_mode="single", 
                        page_size=10, 
                        grid_height=370,
                        editable_columns=EDITABLE_COLUMNS[form_name],
                        clickable_columns=CLICKABLE_COLUMNS[form_name],
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

    btn_save, btn_refresh, btn_delete = _display_buttons(form_name=form_name)

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
        for col in right_columns:
            if col == "id":     # read only
                val = st.text_input(dict_col_label.get(col), value=dict_old_val[col], key=f"col_{form_name}_{col}", disabled=True)
                data.update({col : val})

            elif col == "ts":
                val = st.text_input(dict_col_label.get(col), value=dict_old_val[col], key=f"col_{form_name}_{col}")
                data.update({col : val})

            elif col == "note":   # text_area
                val = st.text_area(dict_col_label.get(col), value=dict_old_val[col], height=125, key=f"col_{form_name}_{col}")
                if val != dict_old_val[col]: 
                    data.update({col : val})

    df_new = None
    if btn_save:
        if selected_row is not None and data.get("id"):
            data.update({"ts": str(datetime.now()),})
            df_new = _db_update(data)
        else:
            data.update({"id": str(uuid4()), "ts": str(datetime.now()),})
            df_new = _db_insert(data)

    elif btn_delete and selected_row is not None and data.get("id"):
        df_new = _db_delete(data)

    st.session_state["df_note"] = df_new if df_new is not None else df_note

### quick add note
def _sidebar_display_add_note(form_name="new_note"):
    with st.expander(f"{STR_QUICK_ADD}", expanded=True):
        with st.form(key=form_name):
            for col in NOTE_DATA_COLS:
                st.text_input(_create_label(col), value="", key=f"{form_name}_{col}")
            st.form_submit_button(STR_ADD, on_click=_sidebar_add_note)

    df_note = st.session_state.get("df_note", None)
    if df_note is not None:
        st.download_button(
            label=STR_DOWNLOAD_CSV,
            data=df_to_csv(df_note, index=False),
            file_name=f"df_note-{str(datetime.now())}.csv",
            mime='text/csv',
        )            

def _sidebar_add_note(form_name="new_note"):
    _title = st.session_state.get(f"{form_name}_title","")
    if not _title: return

    data = {
        "id": uuid4(), 
        "ts": str(datetime.now()),
    }
    
    for col in NOTE_DATA_COLS:
        data.update({col: st.session_state.get(f"{form_name}_{col}","")})
    df_new = _db_insert(data)
    if df_new is not None:
        st.session_state["df_note"] = df_new
    _sidebar_clear_note_form()

def _sidebar_clear_note_form(form_name="new_note"):
    for col in NOTE_DATA_COLS:
        st.session_state[f"{form_name}_{col}"] = ""


### quick add group
def _sidebar_display_add_group(form_name="new_group"):
    with st.expander(f"{STR_QUICK_ADD}", expanded=False):
        with st.form(key=form_name):
            for col in GROUP_DATA_COLS:
                st.text_input(_create_label(col), value="", key=f"{form_name}_{col}")
            st.form_submit_button(STR_ADD, on_click=_sidebar_add_group)

    df_research_group = st.session_state.get("df_research_group", None)
    if df_research_group is not None:
        st.download_button(
            label=STR_DOWNLOAD_CSV,
            data=df_to_csv(df_research_group, index=False),
            file_name=f"df_research_group-{str(datetime.now())}.csv",
            mime='text/csv',
        )


def _sidebar_add_group(form_name="new_group"):
    _research_group = st.session_state.get(f"{form_name}_research_group","")
    if not _research_group: return

    data = {}
    for col in GROUP_DATA_COLS:
        data.update({col: st.session_state.get(f"{form_name}_{col}","")})
    df_new = _db_upsert_group(data)
    if df_new is not None:
        st.session_state["df_research_group"] = df_new
    _sidebar_clear_group_form()

def _sidebar_clear_group_form(form_name="new_group"):
    for col in GROUP_DATA_COLS:
        st.session_state[f"{form_name}_{col}"] = ""

### quick add faculty
def _sidebar_display_faculty(form_name="new_faculty"):
    with st.expander(f"{STR_QUICK_ADD}", expanded=False):
        with st.form(key=form_name):
            for col in FACULTY_DATA_COLS:
                st.text_input(_create_label(col), value="", key=f"{form_name}_{col}")
            st.form_submit_button(STR_ADD, on_click=_sidebar_add_faculty)

    df_faculty = st.session_state.get("df_faculty", None)
    if df_faculty is not None:
        st.download_button(
            label=STR_DOWNLOAD_CSV,
            data=df_to_csv(df_faculty, index=False),
            file_name=f"df_faculty-{str(datetime.now())}.csv",
            mime='text/csv',
        )

def _sidebar_add_faculty(form_name="new_faculty"):
    _name = st.session_state.get(f"{form_name}_name","")
    if not _name: return

    data = {}
    for col in FACULTY_DATA_COLS:
        data.update({col: st.session_state.get(f"{form_name}_{col}","")})
    df_new = _db_upsert_faculty(data)
    if df_new is not None:
        st.session_state["df_faculty"] = df_new
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
