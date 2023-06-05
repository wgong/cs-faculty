"""
Streamlit app to manage CS Faculty data stored in DuckDB 

TODO:
- [2023-05-14]
    - Task: todo list with email/text msg alert

- [2023-04-30]
    - Add menus: 
        - Event: seminar, conference, vacation, ...
        - Collaborator
        - Internship
        - Google Scholar, Best Paper Award on work quality, CSRanking ?

    - Import data from another user, ensure no duplicates

- [Long term]
    - config UI to manage g_column_props table
    - refactor data model to be general-purpose by using g_entity, g_extern, g_relation,
      so that special-purpose tables become unnecessary.

DONE:

- [2023-06-04]
    - added Award: Sloan, Best Paper, NSF career (e.g. https://www.cs.cornell.edu/information/awards-by-recipient)
    - select "Relation (All)" > "person-award" menu to view
    
- [2023-05-18]
    - Enhanced Ref Tab/Key/Val UI via selectbox
    - populate uid

- [2023-05-14]
    - Add/Revise schema
        - Add note_type to Note: journal, resource, idea, information, reminder, other
        - Org (School, Company, ...)
        - Project: work, task, person related to project

    - Resolve refresh button
        - https://discuss.streamlit.io/t/aggrid-unselect-all-rows/21367/2
        - Experiment: replace form with st.form(key, clear_on_submit=True)
            - still need button to refresh parent grid

- [2023-05-12]
    - Rename "Save" button to "Update" and persist to DB

- [2023-05-08]
    - review http://www.cs.cornell.edu/~cdesa/
    - continue cleanup and refactoring

- [2023-05-06]
    - replaced _db_insert() with _db_upsert() to avoid duplicates
    - populate uid column with OS login user 

- [2023-05-03]
    - Added award field to g_person, g_work to indicate its quality
    - merge db.py into helper.py
    - Add filter by Org in "Person (All)" and "Faculty" menu items
    - added patch_db_20230503.py to add new column to g_person, g_work

- [2023-04-30]
    - Added g_task table and related UI
    
- [2023-04-29] 
    - Release 1st working version 
    - CS faculty dataset includes schools of Cornell, MIT, CMU, Berkeley, Stanford, UIUC
    - Manages the following entities:
        - Person: Faculty, Student
        - Team: collection of persons
        - Work: artifact produced by person like publication, talk, course, project, company
        - Note: short writeup or attachment
        - Research Group: team of collaborative researchers
    - Import new scraped data
    - Export table to CSV

- [2023-04-02] 
    - Start prototyping in streamlit and duckdb

- [2023-03-21] 
    - Scrap CS faculty data (see notebooks at https://github.com/wgong/py4kids/tree/master/lesson-11-scrapy/scrap-cs-faculty)

"""
__author__ = "wgong"
SRC_URL = "https://github.com/wgong/cs-faculty"

#####################################################
# Imports
#####################################################
# generic import
from datetime import datetime, date, timedelta
from pathlib import Path
import pandas as pd
from uuid import uuid4
import os

# import glob
# from io import StringIO
# import yaml
# import sys
# from shutil import copy
# from traceback import format_exc

import warnings
warnings.filterwarnings("ignore")

import streamlit as st
from st_aggrid import (
        GridOptionsBuilder, 
        AgGrid, 
        GridUpdateMode, 
        DataReturnMode, 
        JsCode)

from app_config import *
from app_helper import (
        escape_single_quote, 
        df_to_csv, 
        list2sql_str, 
        DBConn, )

DEBUG_FLAG = True # False
##====================================================
_STR_APP_NAME        = "CS Faculty"

st.set_page_config(
    page_title=f'{_STR_APP_NAME}',
    layout="wide",
    initial_sidebar_state="expanded",
)

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
STR_TEAM            = "Team"
STR_NOTE            = "Note"
STR_WORK            = "Work"
STR_TASK            = "Task"
STR_PERSON          = "Person"
STR_AWARD           = "Award"
STR_RELATION        = "Relation"
STR_RELATION_ALL    = "Relation (All)"
STR_NOTE_ALL        = "Note (All)"
STR_WORK_ALL        = "Work (All)"
STR_PERSON_ALL      = "Person (All)"
STR_ORG_ALL         = "Org (All)"
STR_PROJECT_ALL     = "Project (All)"
STR_TASK_ALL        = "Task (All)"
STR_AWARD_ALL       = "Award (All)"
STR_REFRESH_HINT    = "Click 'Refresh' button to clear form"
STR_DOWNLOAD_CSV    = "Download CSV"
STR_IMPORT_EXPORT   = "Data Import/Export"
STR_IMPORT          = "Data Import"
STR_EXPORT          = "Data Export"
STR_ALL_ORGS        = "All Orgs"
STR_CORNELL_UNIV    = "Cornell Univ"

## menu
_STR_MENU_HOME              = STR_WELCOME
_STR_MENU_FACULTY           = STR_FACULTY
_STR_MENU_RESEARCH_GROUP    = STR_RESEARCH_GROUP
_STR_MENU_NOTE              = STR_NOTE_ALL
_STR_MENU_ORG               = STR_ORG_ALL
_STR_MENU_PROJECT           = STR_PROJECT_ALL
_STR_MENU_WORK              = STR_WORK_ALL
_STR_MENU_PERSON            = STR_PERSON_ALL
_STR_MENU_TASK              = STR_TASK_ALL
_STR_MENU_AWARD             = STR_AWARD_ALL
_STR_MENU_RELATION          = STR_RELATION_ALL
_STR_MENU_IMP_EXP           = STR_IMPORT_EXPORT

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

BLANK_LIST = [""]


# @st.cache
def get_uid():
    return os.getlogin()

def _query_ref_tab_key():
    ref_tab = st.session_state.get("ref_tab", "")
    ref_key = st.session_state.get("ref_key", "")
    # uid = get_uid()
    if all((ref_tab, ref_key)):
        with DBConn() as _conn:
            sql_stmt = f"""
                select distinct {ref_key}
                from {ref_tab} 
                where {ref_key} is not NULL
                order by {ref_key};
            """
            df = pd.read_sql(sql_stmt, _conn)
            # print(df)
            return BLANK_LIST + df[ref_key].to_list()
    else:
        return BLANK_LIST

## Important Note:
# for a LOV typed filed to be displayed as selectbox properly
# on UI-form when no row is selected,
# ensure the LOV type has empty string value as a default type
SELECTBOX_OPTIONS = {
    "entity_type": ENTITY_TYPES,
    "work_type": WORK_TYPES,
    "person_type": PERSON_TYPES,
    "org_type": ORG_TYPES,
    "project_type": PROJECT_TYPES,
    "note_type": NOTE_TYPES,
    "priority": PRIORITY,
    "task_status": TASK_STATUS,
    "ref_tab": BLANK_LIST + sorted([t for t in TABLE_LIST if t not in ["g_relation"]]),
    "ref_key": BLANK_LIST + ["id", "name", "url"],
    "ref_val": _query_ref_tab_key,
    "ref_tab_sub": BLANK_LIST + sorted([t for t in TABLE_LIST if t not in ["g_relation"]]),
    "ref_key_sub": BLANK_LIST + ["id", "name", "url"],
}

#####################################################
# Helpers (prefix with underscore)
#####################################################
def _debug_print(msg, debug=DEBUG_FLAG):
    if debug and msg:
        # st.write(f"[DEBUG] {str(msg)}")
        print(f"[DEBUG] {str(msg)}")

def _download_df(df, filename_csv):
    """Download input df to CSV
    """
    if df is not None:
        st.dataframe(df)
        st.download_button(
            label=STR_DOWNLOAD_CSV,
            data=df_to_csv(df, index=False),
            file_name=filename_csv,
            mime='text/csv',
        )



# @st.cache
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

# @st.cache
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

# @st.cache
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


# def _load_db():

#     if not Path(FILE_DB).exists():
#         if not Path(FILE_XLSX).exists():
#             raise Exception(f"source file: {FILE_XLSX} missing")
        
#         xls = pd.ExcelFile(FILE_XLSX)
#         sheet_name = STR_FACULTY
#         df_faculty = pd.read_excel(xls, sheet_name, keep_default_na=False)
#         sheet_name = STR_RESEARCH_GROUP
#         df_research_group = pd.read_excel(xls, sheet_name, keep_default_na=False)

#         with DBConn(FILE_DB, db_type="duckdb") as _conn:
#             _conn.register("v_faculty", df_faculty)
#             _conn.register("v_research_group", df_research_group)

#             _conn.execute(f"Create table {TABLE_FACULTY} as select * from v_faculty;")
#             _conn.execute(f"Create table {TABLE_RESEARCH_GROUP} as select * from v_research_group;")
            
#             create_table_note_sql = f"""create table if not exists {TABLE_NOTE} (
#                     id    text not null
#                     ,name text not null
#                     ,url   text
#                     ,note  text 
#                     ,tags  text
#                     ,ts    text
#                 );
#             """
#             _conn.execute(create_table_note_sql)
#             _conn.commit()

###################################################################
# handle UI
# ======================================
def _layout_grid(df, 
            selection_mode="multiple", 
            page_size=_GRID_OPTIONS["paginationPageSize"],
            grid_height=_GRID_OPTIONS["grid_height"],
            editable_columns=[],
            clickable_columns=[]):
    """show df in a grid and return selected row

    Note: renamed from _display_grid_df() to be similar to layout_form()
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

    render_clickable =  JsCode("""
    function(params) {return `<a href=${params.value} target="_blank">${params.value}</a>`}
    """)
    for col_name in clickable_columns:
        gb.configure_column(col_name, cellRenderer=render_clickable)

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

def _layout_form_relation(table_name, 
                 selected_row):
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
    btn_save, btn_refresh, btn_delete = _crud_display_buttons(form_name)

    data = {"table_name": table_name}
        
    # display form and populate data dict
    col1_columns = []
    col2_columns = []
    col3_columns = []
    for c in visible_columns:
        if form_columns.get(c, "").startswith("COL_1-"):
            col1_columns.append(c)
        elif form_columns.get(c, "").startswith("COL_2-"):
            col2_columns.append(c)
        elif form_columns.get(c, "").startswith("COL_3-"):
            col3_columns.append(c) 

    displayed_cols = []
    col1,col2,col3 = st.columns([6,5,4])
    with col1:
        for col in col1_columns:
            data = _layout_form_fields(data,form_name,old_row,col,
                        widget_types,col_labels,system_columns)
            displayed_cols.append(col)
    with col2:
        for col in col2_columns:
            data = _layout_form_fields(data,form_name,old_row,col,
                        widget_types,col_labels,system_columns)
            displayed_cols.append(col)
    with col3:
        for col in col3_columns:
            data = _layout_form_fields(data,form_name,old_row,col,
                        widget_types,col_labels,system_columns)
            displayed_cols.append(col)

    st.session_state[f"displayed_columns_{form_name}"] = displayed_cols

    # copy id if present
    id_val = old_row.get("id", "")
    if id_val:
        data.update({"id" : id_val})

    try:
        # handle buttons
        if btn_save:
            if data.get("id"):
                data.update({"ts": str(datetime.now()),
                            "uid": get_uid(), })
                _db_update_by_id(data)
            else:
                data.update({"id": str(uuid4()), 
                            "ts": str(datetime.now()),
                            "uid": get_uid(), })
                _db_upsert(data)

        elif btn_delete and data.get("id"):
            _db_delete_by_id(data)

        elif btn_refresh:
            _crud_clear_form()
    except Exception as ex:
        st.error(f"{str(ex)}")


def _layout_form(table_name, 
                 selected_row, 
                 entity_type="",
                 ref_tab="", 
                 ref_key="", 
                 ref_val=""
        ):
    """ layout form for a table and handles button actions 
    """

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
    btn_save, btn_refresh, btn_delete = _crud_display_buttons(form_name)

    data = {"table_name": table_name}
    # if all((ref_tab, ref_key, ref_val)):
    data.update({"ref_tab":ref_tab, "ref_key":ref_key, "ref_val":ref_val})
    if entity_type:
        data.update({"entity_type":entity_type})
        
    # display form and populate data dict
    col1_columns = []
    col2_columns = []
    col3_columns = []
    for c in visible_columns:
        if form_name_suffix and c in ["ref_tab", "ref_key", "ref_val"]:
            # skip displaying ref_key, ref_val for parent/child view
            continue
        if form_columns.get(c, "").startswith("COL_1-"):
            col1_columns.append(c)
        elif form_columns.get(c, "").startswith("COL_2-"):
            col2_columns.append(c)
        elif form_columns.get(c, "").startswith("COL_3-"):
            col3_columns.append(c) 

    displayed_cols = []
    col1,col2,col3 = st.columns([6,5,4])
    with col1:
        for col in col1_columns:
            data = _layout_form_fields(data,form_name,old_row,col,
                        widget_types,col_labels,system_columns)
            displayed_cols.append(col)
    with col2:
        for col in col2_columns:
            data = _layout_form_fields(data,form_name,old_row,col,
                        widget_types,col_labels,system_columns)
            displayed_cols.append(col)
    with col3:
        for col in col3_columns:
            data = _layout_form_fields(data,form_name,old_row,col,
                        widget_types,col_labels,system_columns)
            displayed_cols.append(col)

    st.session_state[f"displayed_columns_{form_name}"] = displayed_cols

    # copy id if present
    id_val = old_row.get("id", "")
    if id_val:
        data.update({"id" : id_val})

    try:
        # handle buttons
        if btn_save:
            if data.get("id"):
                data.update({"ts": str(datetime.now()),
                            "uid": get_uid(), })
                _db_update_by_id(data)
            else:
                data.update({"id": str(uuid4()), 
                            "ts": str(datetime.now()),
                            "uid": get_uid(), })
                _db_upsert(data)

        elif btn_delete and data.get("id"):
            _db_delete_by_id(data)

        elif btn_refresh:
            _crud_clear_form()
    except Exception as ex:
        st.error(f"{str(ex)}")

def _layout_form_st(table_name, 
                 selected_row, 
                 ref_tab="", 
                 ref_key="", 
                 ref_val="", 
                 entity_type=""):
    """ use st.form to layout form for a table and handles button actions 
    
        Don't work as expected:
    """

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

    data = {"table_name": table_name}
    if all((ref_tab, ref_key, ref_val)):
        data.update({"ref_tab":ref_tab, "ref_key":ref_key, "ref_val":ref_val})
    if entity_type:
        data.update({"entity_type":entity_type})

    # copy id if present
    id_val = old_row.get("id", "")
    if id_val:
        data.update({"id" : id_val})

    # display form and populate data dict
    col1_columns = []
    col2_columns = []
    col3_columns = []
    for c in visible_columns:
        if form_name_suffix and c in ["ref_tab", "ref_key", "ref_val"]:
            # skip displaying ref_key, ref_val for parent/child view
            continue
        if form_columns.get(c, "").startswith("COL_1-"):
            col1_columns.append(c)
        elif form_columns.get(c, "").startswith("COL_2-"):
            col2_columns.append(c)
        elif form_columns.get(c, "").startswith("COL_3-"):
            col3_columns.append(c) 

    with st.form(form_name, clear_on_submit=True):
        col1,col2,col3 = st.columns([6,5,4])
        with col1:
            for col in col1_columns:
                data = _layout_form_fields(data,form_name,old_row,col,
                            widget_types,col_labels,system_columns)
        with col2:
            for col in col2_columns:
                data = _layout_form_fields(data,form_name,old_row,col,
                            widget_types,col_labels,system_columns)
        with col3:
            for col in col3_columns:
                data = _layout_form_fields(data,form_name,old_row,col,
                            widget_types,col_labels,system_columns)

            # add checkbox for deleting this record
            col = "delelte_record"
            delete_flag = st.checkbox("Delelte Record?", value=False)
            data.update({col: delete_flag})

        save_btn = st.form_submit_button("Save")
        if save_btn:
            try:
                delete_flag = data.get("delelte_record", False)
                if delete_flag:
                    if data.get("id"):
                        _db_delete_by_id(data)
                else:
                    if data.get("id"):
                        data.update({"ts": str(datetime.now()),
                                    "uid": get_uid(), })
                        _db_update_by_id(data)
                    else:
                        data.update({"id": str(uuid4()), 
                                    "ts": str(datetime.now()),
                                    "uid": get_uid(), })
                        _db_upsert(data)

            except Exception as ex:
                st.error(f"{str(ex)}")

def _layout_form_inter(table_name, 
            selected_row, 
            ref_tab,
            ref_key,  
            ref_val,
            inter_table_name,
            rel_type):
    """ layout form for a table with intersection table dependency
    and handles button actions: Save (I/U), Delete (D)
    """

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
    btn_save, btn_refresh, btn_delete = _crud_display_buttons(form_name)

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
    col3_columns = []
    for c in visible_columns:
        if form_columns.get(c, "").startswith("COL_1-"):
            col1_columns.append(c)
        elif form_columns.get(c, "").startswith("COL_2-"):
            col2_columns.append(c) 
        elif form_columns.get(c, "").startswith("COL_3-"):
            col3_columns.append(c) 

    displayed_cols = []
    col1,col2,col3 = st.columns([6,5,4])
    with col1:
        for col in col1_columns:
            data = _layout_form_fields(data,form_name,old_row,col,
                        widget_types,col_labels,system_columns)
            displayed_cols.append(col)
    with col2:
        for col in col2_columns:
            data = _layout_form_fields(data,form_name,old_row,col,
                        widget_types,col_labels,system_columns)
            displayed_cols.append(col)
    with col3:
        for col in col3_columns:
            data = _layout_form_fields(data,form_name,old_row,col,
                        widget_types,col_labels,system_columns)
            displayed_cols.append(col)

    st.session_state[f"displayed_columns_{form_name}"] = displayed_cols

    # copy id if present
    id_val = old_row.get("id", "")
    if id_val:
        data.update({"id" : id_val})

    try:
        # handle buttons
        if btn_save:
            if data.get("id"):
                data.update({"ts": str(datetime.now()),
                            "uid": get_uid(), })
                _db_update_by_id(data)
            else:
                data.update({"id": str(uuid4()), 
                            "ts": str(datetime.now()),
                            "uid": get_uid(), })
                _db_insert_inter(data)

        elif btn_delete and data.get("id"):
            _db_delete_by_id_inter(data)

        elif btn_refresh:
            _crud_clear_form()

    except Exception as ex:
        st.error(f"{str(ex)}")


###################################################################
# handle DB Backend
# ======================================
def _db_execute(sql_statement, debug=DEBUG_FLAG):
    with DBConn() as _conn:
        _debug_print(sql_statement, debug=debug)
        _conn.execute(sql_statement)
        _conn.commit()           

def _db_select_by_id(table_name, id_value=""):
    """Select row by primary key: id
    """
    if not id_value: return []

    with DBConn() as _conn:
        sql_stmt = f"""
            select *
            from {table_name} 
            where id = '{id_value}' ;
        """
        return pd.read_sql(sql_stmt, _conn).fillna("").to_dict('records')

def _db_select_by_name_url(table_name, name="", url=""):
    """Select row by user key: (name, url)
    """
    if not any((name,url)):
        return []
    
    with DBConn() as _conn:
        sql_stmt = f"""
            select *
            from {table_name} 
            where name='{name}' 
                and url='{url}';
        """
        return pd.read_sql(sql_stmt, _conn).fillna("").to_dict('records')

def _validate_name_url(data):
    """ since all entities have (name,url) as required User-key
    validate them here
    """
    name_ = data.get("name", "")
    if not name_:
        raise Exception(f"Missing required field 'name'")
    # url_ = data.get("url", "")
    # if not url_:
    #     data.update({"url": "TBD"})
    return data

def _db_upsert(data, user_key_cols=["name","url"]):
    if not data: 
        return None
    
    table_name = data.get("table_name", "")
    if not table_name:
        raise Exception(f"[ERROR] Missing table_name: {data}")

    if not "uid" in data or not data.get("uid", ""):
        data.update({"uid":get_uid()})

    # build SQL
    visible_columns = _get_columns(table_name, prop_name="is_visible")

    # query by user-key to avoid duplicates
    uk_where_clause = []
    for col,val in data.items():
        if col in user_key_cols:
            if val != "":
                uk_where_clause.append(f" {col} = '{escape_single_quote(val)}' ")

    if not uk_where_clause:
        return None # skip if user key cols not populated

    with DBConn() as _conn:
        where_clause = " and ".join(uk_where_clause)
        sql_stmt = f"""
            select id
            from {table_name} 
            where {where_clause};
        """
        rows = pd.read_sql(sql_stmt, _conn).to_dict('records')

    if not len(rows):
        sql_type = "INSERT" 
    else: 
        sql_type = "UPDATE"  
        old_row = rows[0]

    
    if sql_type == "INSERT":
        col_clause = []
        val_clause = []
        for col,val in data.items():
            if col not in visible_columns:
                continue
            col_clause.append(col)
            if col in ["due_date", "done_date", "alert_date", "alert_time"]:
                col_val = val
            else:
                col_val = escape_single_quote(val)
            val_clause.append(f"'{col_val}'")

        upsert_sql = f"""
            insert into {table_name} (
                {", ".join(col_clause)}
            )
            values (
                {", ".join(val_clause)}
            );
        """

    else:
        set_clause = []
        for col,val in data.items():
            if col not in visible_columns or col in user_key_cols:
                continue

            # skip if no change
            old_val = old_row.get(col, "")
            if old_val is None:
                old_val = ""
            if val == old_val:
                continue

            if col in ["due_date", "done_date", "alert_date", "alert_time"]:
                col_val = val
            else:
                col_val = escape_single_quote(val)

            set_clause.append(f" {col} = '{col_val}'")

        if set_clause:
            id_ = old_row.get("id")
            upsert_sql = f"""
                update {table_name} 
                set 
                    {", ".join(set_clause)}
                where id = '{id_}';
            """

    _db_execute(upsert_sql)

def _db_update_by_id(data, update_changed=True):
    if not data: 
        return
    
    table_name = data.get("table_name", "")
    if not table_name:
        raise Exception(f"[ERROR] Missing table_name: {data}")

    id_val = data.get("id", "")
    if not id_val:
        return

    if not "uid" in data or not data.get("uid", ""):
        data.update({"uid":get_uid()})

    if update_changed:
        rows = _db_select_by_id(table_name=table_name, id_value=id_val)
        if len(rows) < 1:
            return
        old_row = rows[0]

    editable_columns = _get_columns(table_name, prop_name="is_editable")

    # build SQL
    set_clause = []
    for col,val in data.items():
        if col not in editable_columns: 
            continue
        if col in ["due_date", "done_date", "alert_date", "alert_time"]:
            set_clause.append(f"{col} = '{val}'")
            continue

        if update_changed:
            # skip if no change
            old_val = old_row.get(col, "")
            if val != old_val:
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

def _db_delete_by_id_inter(data):
    if not data: 
        return None
    
    table_name = data.get("table_name", "")
    if not table_name:
        raise Exception(f"[ERROR] Missing key: table_name: {data}")

    inter_table_name = data.get("inter_table_name", "")
    if not inter_table_name:
        raise Exception(f"[ERROR] Missing key: inter_table_name: {data}")
    
    rel_type = data.get("rel_type", "")
    ref_tab = data.get("ref_tab", "")
    ref_key = data.get("ref_key", "")
    ref_val = data.get("ref_val", "")
    ref_tab_sub = table_name
    ref_key_sub = "id"
    ref_val_sub = data.get(ref_key_sub, "")

    inter_col_clause = ['rel_type', 'ref_tab', 'ref_key', 'ref_val', 'ref_tab_sub', 'ref_key_sub', 'ref_val_sub']
    inter_vals = [rel_type, ref_tab, ref_key, ref_val, ref_tab_sub, ref_key_sub, ref_val_sub]
    inter_where_clause = ["1=1"]
    for n,col in enumerate(inter_col_clause):
        val = inter_vals[n]
        inter_where_clause.append(f" {col} = '{escape_single_quote(val)}' ")

    # remove row from intersection table only
    where_clause_str = " and ".join(inter_where_clause)
    delete_sql = f"""
        delete from {inter_table_name}
        where {where_clause_str}
        ;
    """
    _db_execute(delete_sql)

def _db_insert_inter(data):
    """populate both child and intersection tables

    TODO:
        enhance with upsert logic like _db_upsert()
    """
    if not data: 
        return None
    
    table_name = data.get("table_name", "")
    if not table_name:
        raise Exception(f"[ERROR] Missing key: table_name: {data}")
    
    inter_table_name = data.get("inter_table_name", "")
    if not inter_table_name:
        raise Exception(f"[ERROR] Missing key: inter_table_name: {data}")
    
    if not "uid" in data or not data.get("uid", ""):
        data.update({"uid":get_uid()})

    data = _validate_name_url(data)

    rel_type = data.get("rel_type", "")
    ref_tab = data.get("ref_tab", "")
    ref_key = data.get("ref_key", "")
    ref_val = data.get("ref_val", "")
    ref_tab_sub = table_name
    ref_key_sub = "id"
    ref_val_sub = data.get(ref_key_sub, "")

    _id = str(uuid4())
    _ts = data.get("ts", str(datetime.now()))
    _uid = get_uid()

    inter_col_clause = ['id', 'ts', 'uid', 'rel_type', 'ref_tab', 'ref_key', 'ref_val', 'ref_tab_sub', 'ref_key_sub', 'ref_val_sub']
    inter_vals = [_id, _ts, _uid, rel_type, ref_tab, ref_key, ref_val, ref_tab_sub, ref_key_sub, ref_val_sub]
    inter_val_clause = []
    for val in inter_vals:
        inter_val_clause.append(f"'{escape_single_quote(val)}'")

    # build SQL
    visible_columns = _get_columns(table_name, prop_name="is_visible")
    col_clause = []
    val_clause = []
    for col,val in data.items():
        if col not in set(visible_columns + SYS_COLS):
            continue
        col_clause.append(col) 
        val_clause.append(f"'{escape_single_quote(val)}'")

    insert_sql = f"""
        -- populate child table
        insert into {table_name} (
            {", ".join(col_clause)}
        )
        values (
            {", ".join(val_clause)}
        );

        -- populate intersection table
        insert into {inter_table_name} (
            {", ".join(inter_col_clause)}
        )
        values (
            {", ".join(inter_val_clause)}
        );
    """
    _db_execute(insert_sql)


def _db_quick_add(data):

    table_name = data.get("table_name")
    # data_cols = DATA_COLS[table_name]

    COL_DEFS = COLUMN_DEFS[table_name]
    editable_columns = COL_DEFS["is_editable"]
    data_cols = list(set(editable_columns).union(set(SYS_COLS)))
    name = data.get("name")
    url = data.get("url")
    rows = _db_select_by_name_url(table_name, name, url)
    
    if len(rows) < 1:  # insert
        data.update({"id": str(uuid4()),
                     "ts": str(datetime.now()),
                     "uid": get_uid(), })        
        col_names = []
        col_vals = []
        for c in data_cols:
            v = data.get(c, "")
            if not v: continue
            col_names.append(c)
            col_vals.append(f"'{v}'")        

        sql_stmt = f"""
            insert into {table_name} 
            ( {", ".join(col_names)} )
            values 
            (  {", ".join(col_vals)} );
        """
        _db_execute(sql_stmt)


def _push_selected_cols_to_end(cols, selected_cols=["entity_type", "ref_tab", "ref_key", "ref_val"] + SYS_COLS):
    """move selected column to the end,
        e.g. id, ts, uid system cols
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


def _push_selected_cols_to_front(cols, selected_cols=["name","url","note"]):
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

def _reorder_selected_cols(cols):
    return _push_selected_cols_to_front(_push_selected_cols_to_end(cols))

# _STR_MENU_FACULTY
def _crud_display_grid_parent_child(table_name,
                person_type="faculty",
                form_name_suffix="",
                orderby_cols=["name"], 
                selection_mode="single"):
    
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

    with DBConn() as _conn:
        orderby_clause = f' order by {",".join(orderby_cols)}' if orderby_cols else ""
        where_clause = f" where person_type = '{person_type}' "
        # add org_filter
        selected_org = st.session_state.get("selected_org", STR_ALL_ORGS)
        if selected_org is None or selected_org == "" :
            where_clause += f"""
                and ( org = '' or org is NULL )
            """
        elif selected_org != STR_ALL_ORGS:
            where_clause += f"""
                and org = '{selected_org}'
            """
            
        selected_cols = _reorder_selected_cols(visible_columns)
        sql_stmt = f"""
            select 
                {",".join(selected_cols)}
            from {table_name} 
                {where_clause}
                {orderby_clause};
        """
        df = pd.read_sql(sql_stmt, _conn).fillna("")

    grid_resp = _layout_grid(df, 
            selection_mode=selection_mode, 
            page_size=10, 
            grid_height=370,
            editable_columns=editable_columns,
            clickable_columns=clickable_columns)
    
    selected_row = {}
    if grid_resp and grid_resp.get('selected_rows'):
        selected_row = grid_resp['selected_rows'][0]

    if not selected_row:
        return

    if st.button("Update", key=f"{form_name}_save"):
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
    menu_options = [STR_WORK, STR_TEAM, STR_NOTE, STR_TASK]
    idx_default = menu_options.index(STR_WORK)

    faculty_name = selected_row.get("name")
    menu_item = st.selectbox(f"Menu for '{faculty_name}' ({primary_key}): ", 
                                menu_options, index=idx_default, key="faculty_menu_item")

    if menu_item == STR_NOTE:
        table_name = TABLE_NOTE
        _crud_display_grid_form_subject(table_name,
                        ref_tab=TABLE_PERSON, 
                        ref_key="url", 
                        ref_val=primary_key,
                        form_name_suffix="faculty", 
                        page_size=5, grid_height=220)

    elif menu_item == STR_WORK:
        try:
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

    elif menu_item == STR_TEAM:
        try:
            table_name = TABLE_PERSON 
            _crud_display_grid_form_inter(table_name, 
                        ref_tab=TABLE_PERSON, 
                        ref_key="url", 
                        ref_val=primary_key,
                        form_name_suffix="faculty",
                        inter_table_name=TABLE_RELATION,
                        rel_type='person-team',
                        page_size=5, grid_height=220)
        except:
            pass  # workaround to fix an streamlit issue

    elif menu_item == STR_TASK:
        table_name = TABLE_TASK
        _crud_display_grid_form_subject(table_name,
                        ref_tab=TABLE_PERSON, 
                        ref_key="url", 
                        ref_val=primary_key,
                        form_name_suffix="faculty", 
                        page_size=5, grid_height=220)

def _layout_form_fields(data,form_name,old_row,col,
                        widget_types,col_labels,system_columns):
    DISABLED = col in system_columns
    if old_row:
        old_val = old_row.get(col, "")
        widget_type = widget_types.get(col, "text_input")
        if widget_type == "text_area":
            kwargs = {"height":125}
            val = st.text_area(col_labels.get(col), value=old_val, disabled=DISABLED, key=f"col_{form_name}_{col}", kwargs=kwargs)
        elif widget_type == "date_input":
            old_date_input = old_val.split("T")[0]
            if old_date_input:
                val_date = datetime.strptime(old_date_input, "%Y-%m-%d")
            else:
                val_date = datetime.now().date()
            val = st.date_input(col_labels.get(col), value=val_date, disabled=DISABLED, key=f"col_{form_name}_{col}")
            val = datetime.strftime(val, "%Y-%m-%d")
        elif widget_type == "time_input":
            old_time_input = old_val
            if old_time_input:
                val_time = datetime.strptime(old_time_input.split(".")[0], "%H:%M:%S").time()
            else:
                val_time = datetime.now().time()
            val = st.time_input(col_labels.get(col), value=val_time, disabled=DISABLED, key=f"col_{form_name}_{col}")
        elif widget_type == "selectbox":
            # check if options is avail, otherwise display as text_input
            if col in SELECTBOX_OPTIONS:
                try:
                    if col == "ref_val":
                        _options = SELECTBOX_OPTIONS[col]()
                    else:
                        _options = SELECTBOX_OPTIONS.get(col,[])

                    old_val = old_row.get(col, "")
                    _idx = _options.index(old_val)
                    val = st.selectbox(col_labels.get(col), _options, index=_idx, key=f"col_{form_name}_{col}")
                except ValueError:
                    # if col != "ref_val":
                    #     opts = SELECTBOX_OPTIONS.get(col,[])
                    #     val = opts[0] if opts else "" # workaround for refresh error
                    # else:
                    #     val = old_row.get(col, "")
                    val = old_row.get(col, "")
            else:
                val = st.text_input(col_labels.get(col), value=old_val, disabled=DISABLED, key=f"col_{form_name}_{col}")

        else:
            val = st.text_input(col_labels.get(col), value=old_val, disabled=DISABLED, key=f"col_{form_name}_{col}")

        if val != old_val or col in ["ref_tab", "ref_key"]:
            data.update({col : val})

        if col in ["ref_tab", "ref_key"]:
            # store ref_tab/ref_key selection in session_state
            # used by _query_ref_tab_key()
            st.session_state[col] = val


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
        # print(f"sql_stmt1 = {sql_stmt}")
        df_1 = pd.read_sql(sql_stmt, _conn).fillna("")  
        rows = df_1.groupby("key_col")["key_val"].apply(list).to_dict()
        where_clause = []
        for k,v in rows.items():
            where_clause.append(f" {k} in {list2sql_str(v)}")

        # fetch child table rows
        selected_cols = _reorder_selected_cols(visible_columns)
        where_clause_str = " or ".join(where_clause) if where_clause else " 1=2 "
        sql_stmt = f"""
            select {", ".join(selected_cols)}
            from {table_name}
            where {where_clause_str}
        """
        # print(f"sql_stmt = {sql_stmt}")
        df = pd.read_sql(sql_stmt, _conn)   

    grid_resp = _layout_grid(df, 
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

    _layout_form_inter(table_name, 
                selected_row, 
                ref_tab,
                ref_key,  
                ref_val,
                inter_table_name,
                rel_type)

# _STR_MENU_RELATION
def _crud_display_grid_form_relation(
                table_name="g_relation",
                form_name_suffix="", 
                orderby_clause="ref_tab,ref_tab_sub,ref_key,ref_key_sub",
                page_size=10, grid_height=400):

    if not table_name in COLUMN_PROPS or not table_name in COLUMN_DEFS:
        st.error(f"Invalid table name: {table_name}")
        return
     
    form_name = f"{table_name}#{form_name_suffix}"
    st.session_state["form_name"] = form_name

    COL_DEFS = COLUMN_DEFS[table_name]
    visible_columns = COL_DEFS["is_visible"]
    editable_columns = COL_DEFS["is_editable"]
    clickable_columns = COL_DEFS["is_clickable"]
    selected_rel_type = st.session_state.get("selected_rel_type")

    # prepare dataframe
    with DBConn() as _conn:
        selected_cols = _push_selected_cols_to_front(visible_columns, selected_cols=["ref_val","ref_val_sub","props"])
        where_clause = f" where rel_type = '{selected_rel_type}' "
        sql_stmt = f"""
            select 
                {",".join(selected_cols)}
            from {table_name} 
                {where_clause}
                order by {orderby_clause};
        """
        df = pd.read_sql(sql_stmt, _conn).fillna("")        

    ## show data grid
    grid_resp = _layout_grid(df, 
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
    _layout_form_relation(table_name, selected_row)

# _STR_MENU_NOTE
def _crud_display_grid_form_subject(table_name, 
                ref_tab="", 
                ref_key="", 
                ref_val="", 
                form_name_suffix="", 
                # orderby_cols=["name"], 
                orderby_clause="name",
                page_size=10, grid_height=400):
    """Render data grid defined by column properties, 
    for table, or child table when (ref_key,ref_val) are given

    Inputs:
        table_name (required): 
        form_name_suffix (optional) : used for different view on the same underlying table

        (ref_tab,ref_key,ref_val) : reference parent entity

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

    # # make sure orderby_cols exists
    # orderby_cols = list(set(orderby_cols).intersection(set(visible_columns)))

    # prepare dataframe
    with DBConn() as _conn:
        # orderby_clause = f' order by {",".join(orderby_cols)}' if orderby_cols else ""

        where_clause = " where 1=1 "
        if all((ref_tab,ref_key,ref_val)):
            where_clause += f"""
                and ref_tab = '{ref_tab}'
                and ref_key = '{ref_key}'
                and ref_val = '{ref_val}'
            """
        if table_name == TABLE_PERSON:
            # add org_filter
            selected_org = st.session_state.get("selected_org", STR_ALL_ORGS)
            if selected_org is None or selected_org == "" :
                where_clause += f"""
                    and ( org = '' or org is NULL )
                """
            elif selected_org != STR_ALL_ORGS:
                where_clause += f"""
                    and org = '{selected_org}'
                """

        selected_cols = _reorder_selected_cols(visible_columns)
        sql_stmt = f"""
            select 
                {",".join(selected_cols)}
            from {table_name} 
                {where_clause}
                order by {orderby_clause};
        """
        df = pd.read_sql(sql_stmt, _conn).fillna("")

    ## show data grid
    grid_resp = _layout_grid(df, 
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
    _layout_form(table_name, selected_row, entity_type="", 
                 ref_tab=ref_tab, ref_key=ref_key, ref_val=ref_val)
    # _layout_form_st(table_name, selected_row, ref_tab=ref_tab, ref_key=ref_key, ref_val=ref_val)

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
    # _debug_print(COLUMN_PROPS.keys())
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
        selected_cols = _reorder_selected_cols(visible_columns)
        sql_stmt = f"""
            select {", ".join(selected_cols)}
            from {table_name} 
            {where_clause}
            {orderby_clause};
        """
        # print(sql_stmt)
        df = pd.read_sql(sql_stmt, _conn).fillna("")

    ## show data grid
    grid_resp = _layout_grid(df, 
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
    _layout_form(table_name, selected_row, entity_type=entity_type, 
                 ref_tab="", ref_key="", ref_val="")

def _crud_display_buttons(form_name):
    """button UI key: btn_<table_name>_action
        action: refresh, upsert, delete
    """
    # if form_name_child == "no_child":
    #     form_name = st.session_state.get("form_name", "")
    # else:
    #     form_name = form_name_child
    #     st.session_state["form_name"] = form_name

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

    exist_displayed_cols = st.session_state[f"displayed_columns_{form_name}"]
    # print(f"exist_displayed_cols = {exist_displayed_cols}")
    # for col in st.session_state.get("visible_columns", []):
    for col in exist_displayed_cols:
        try:
            col_key = f"col_{form_name}_{col}"
            st.session_state.update({col_key: ""}) 
        except Exception:
            pass

    st.session_state[f"displayed_columns_{form_name}"] = []

### Quick Add
def _sidebar_quick_add_form(form_name):
    table_name = form_name.split("-")[-1]
    st.session_state["quick_add_form_name"] = form_name
    with st.expander(f"{STR_QUICK_ADD}", expanded=False):
        with st.form(key=form_name):
            for col in DATA_COLS[table_name]:
                st.text_input(_gen_label(col), value="", key=f"{form_name}_{col}")
            st.form_submit_button(STR_ADD, on_click=_sidebar_quick_add)

def _sidebar_quick_add():
    form_name = st.session_state.get("quick_add_form_name", "")
    table_name = form_name.split("-")[-1]
    data = {"table_name": table_name}

    if table_name == TABLE_FACULTY:
        data.update({"person_type": "faculty"})
    elif table_name == TABLE_RESEARCH_GROUP:
        data.update({"entity_type": "research_group"})

    for col in DATA_COLS[table_name]:
        data.update({col: st.session_state.get(f"{form_name}_{col}","")})
    _db_quick_add(data)
    _sidebar_quick_clear_form()

def _sidebar_quick_clear_form():
    form_name = st.session_state.get("quick_add_form_name", "")
    table_name = form_name.split("-")[-1]
    for col in DATA_COLS[table_name]:
        st.session_state[f"{form_name}_{col}"] = ""

# add org filter
def _sidebar_display_org_filter(menu_iterm=_STR_MENU_PERSON):
    with DBConn() as _conn:
        sql_stmt = """select distinct org
            from g_person
            order by org;
        """
        df = pd.read_sql(sql_stmt, _conn)
        org_list = [STR_ALL_ORGS] + df["org"].to_list()
        idx_default = org_list.index(STR_ALL_ORGS) if menu_iterm==_STR_MENU_PERSON else org_list.index(STR_CORNELL_UNIV)
        st.selectbox("Select Org:", org_list, index=idx_default, key="selected_org")

def _sidebar_display_rel_type():
    with DBConn() as _conn:
        sql_stmt = """select distinct rel_type
            from g_relation
            order by rel_type;
        """
        df = pd.read_sql(sql_stmt, _conn)
        rel_type_list = df["rel_type"].to_list()
        st.selectbox("Select Rel Type:", rel_type_list, index=0, key="selected_rel_type")

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
    - [Cornell-CS](https://www.cs.cornell.edu/people/faculty)
    - [MIT-AID](https://www.eecs.mit.edu/role/faculty-aid/)
    - [MIT-CS](https://www.eecs.mit.edu/role/faculty-cs/)
    - [CMU-CS](https://csd.cmu.edu/people/faculty)
    - [Berkeley-CS](https://www2.eecs.berkeley.edu/Faculty/Lists/CS/faculty.html)
    - [Stanford-CS](https://cs.stanford.edu/directory/faculty)
    - [UIUC-CS](https://cs.illinois.edu/about/people/department-faculty)
    - [Yale-CS](https://cpsc.yale.edu/people/faculty)
    
    #### Additional Resources
    - [CS Faculty Composition and Hiring Trends (Blog)](https://jeffhuang.com/computer-science-open-data/#cs-faculty-composition-and-hiring-trends)
    - [2200 Computer Science Professors in 50 top US Graduate Programs](https://cs.brown.edu/people/apapouts/faculty_dataset.html)
    - [CS Professors (Data Explorer)](https://drafty.cs.brown.edu/csprofessors?src=csopendata)
    - [Drafty Project](https://drafty.cs.brown.edu/)
    - [CSRankings.org](https://csrankings.org/#/fromyear/2011/toyear/2023/index?ai&vision&mlmining&nlp&inforet&act&crypt&log&us)

    """, unsafe_allow_html=True)


def do_faculty():
    st.subheader(f"{_STR_MENU_FACULTY}")
    _crud_display_grid_parent_child(TABLE_FACULTY)

def do_research_group():
    st.subheader(f"{_STR_MENU_RESEARCH_GROUP}")
    _crud_display_grid_form_entity(TABLE_ENTITY, entity_type="research_group")

def do_award():
    st.subheader(f"{_STR_MENU_AWARD}")
    _crud_display_grid_form_entity(TABLE_ENTITY, entity_type="award")

def do_person():
    st.subheader(f"{_STR_MENU_PERSON}")
    _crud_display_grid_form_subject(TABLE_PERSON)

def do_org():
    st.subheader(f"{_STR_MENU_ORG}")
    _crud_display_grid_form_subject(TABLE_ORG)

def do_work():
    st.subheader(f"{_STR_MENU_WORK}")
    _crud_display_grid_form_subject(TABLE_WORK)

def do_note():
    st.subheader(f"{_STR_MENU_NOTE}")
    _crud_display_grid_form_subject(TABLE_NOTE, orderby_clause="ts desc")

def do_project():
    st.subheader(f"{_STR_MENU_PROJECT}")
    _crud_display_grid_form_subject(TABLE_PROJECT)

def do_task():
    st.subheader(f"{_STR_MENU_TASK}")
    _crud_display_grid_form_subject(TABLE_TASK)

def do_relation():
    st.subheader(f"{_STR_MENU_RELATION}")
    _crud_display_grid_form_relation()

def do_import_export():
    # Export
    st.subheader(f"{STR_EXPORT}")
    st.write(f"FILE_DB: {FILE_DB}, exists: {Path(FILE_DB).exists()}")

    with DBConn() as _conn:
        sql_stmt = """select t.table_name
            from information_schema.tables t where t.table_name like 'g_%';
        """
        df1 = pd.read_sql(sql_stmt, _conn)
        tables = df1["table_name"].to_list()
        idx_default = tables.index("g_work")
        selected_table = st.selectbox("Select table:", tables, index=idx_default, key="export_table")

        export_btn = st.button("Export Data ...")
        if export_btn:
            sql_stmt = f"""select * from {selected_table};"""
            df = pd.read_sql(sql_stmt, _conn).fillna("")
            ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename_csv = f"{selected_table}_{ts}.csv"
            _download_df(df, filename_csv)

    # Import
    st.subheader(f"{STR_IMPORT}")
    st.markdown(f"""
    The CS Faculty dataset is scraped using [this notebook](https://github.com/wgong/py4kids/blob/master/lesson-11-scrapy/scrap-cs-faculty/bs_cornell.ipynb) <br>
    The spreadsheet column header must be the same as that of [this sample](https://github.com/wgong/py4kids/blob/master/lesson-11-scrapy/scrap-cs-faculty/faculty-Cornell-CS.xlsx)
    """, unsafe_allow_html=True)

    c_left,c_right = st.columns([5,1])
    df_dict = {}
    filename = ""
    with c_right:
        uploaded_file = st.file_uploader("Upload file", type=["csv","xlsx"])
        if uploaded_file is not None:
            filename = uploaded_file.name
            file_ext = filename.split(".")[-1].lower()
            if file_ext == "csv":
                df_dict[filename] = pd.read_csv(uploaded_file)
            elif file_ext == "xlsx":
                xlsx_obj = pd.ExcelFile(uploaded_file, engine="openpyxl")
                for sheet in xlsx_obj.sheet_names:
                    key = sheet.lower().replace(" ", "_")
                    df_dict[key] = pd.read_excel(xlsx_obj, sheet, keep_default_na=False)

    with c_left:
        if filename: st.write(f"filename: {filename}")
        for key in df_dict.keys():
            st.write(f"{key} df:")
            st.dataframe(df_dict[key])

    import_btn = st.empty()
    if filename:
        import_btn = st.button("Import Data ...")
    if import_btn:
        with DBConn() as _conn:
            for key in df_dict.keys():
                view_name = f"v_{key}"
                st.write(f"view_name = {view_name}")
                df = df_dict[key]
                st.write(f"columns = {df.columns}")
                _conn.register(f"{view_name}", df)

                _id = uuid()
                _uid = get_uid()
                _ts = str(datetime.now())
                if key == "faculty":
                    sql_stmt = f"""insert into g_person (
                            id, uid, ts, 
                            person_type, name, job_title, phd_univ, phd_year, 
                            research_area, research_concentration, 
                            research_focus, url, img_url, phone, email, cell_phone, 
                            office_address, department, org
                        )
                        select 
                            '{_id}', '{_uid}', '{_ts}', 
                            'faculty', name, job_title, phd_univ, phd_year, 
                            research_area, research_concentration, 
                            research_focus, url, img_url, phone, email, cell_phone, 
                            office_address, department, org
                        from {view_name}
                    """
                    st.write(f"sql_stmt =\n {sql_stmt}")
                    res = _conn.execute(sql_stmt).df()
                    st.dataframe(res)
                elif key == "research_groups":
                    sql_stmt = f"""insert into g_entity (
                            id, uid, ts, 
                            entity_type, name, url
                        )
                        select 
                            '{_id}', '{_uid}', '{_ts}', 
                            'research_group', research_group, url
                        from {view_name}
                    """
                    st.write(f"sql_stmt =\n {sql_stmt}")
                    res = _conn.execute(sql_stmt).df()
                    st.dataframe(res)

#####################################################
# setup menu_items 
#####################################################
menu_dict = {
    _STR_MENU_HOME :                {"fn": do_welcome},
    _STR_MENU_FACULTY:              {"fn": do_faculty},
    _STR_MENU_RESEARCH_GROUP:       {"fn": do_research_group},
    _STR_MENU_PERSON:               {"fn": do_person},
    _STR_MENU_ORG:                  {"fn": do_org},
    _STR_MENU_NOTE:                 {"fn": do_note},
    _STR_MENU_WORK:                 {"fn": do_work},
    _STR_MENU_PROJECT:              {"fn": do_project},
    _STR_MENU_TASK:                 {"fn": do_task},
    _STR_MENU_AWARD:                {"fn": do_award},
    _STR_MENU_RELATION:             {"fn": do_relation},
    _STR_MENU_IMP_EXP:              {"fn": do_import_export},

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
            _sidebar_display_org_filter(menu_item)
            _sidebar_quick_add_form(form_name=f"quick_add-{TABLE_FACULTY}")

        elif menu_item == _STR_MENU_RESEARCH_GROUP:
            _sidebar_quick_add_form(form_name=f"quick_add-{TABLE_RESEARCH_GROUP}")

        elif menu_item == _STR_MENU_NOTE:
            _sidebar_quick_add_form(form_name=f"quick_add-{TABLE_NOTE}")

        elif menu_item == _STR_MENU_ORG:
            _sidebar_quick_add_form(form_name=f"quick_add-{TABLE_ORG}")

        elif menu_item == _STR_MENU_PROJECT:
            _sidebar_quick_add_form(form_name=f"quick_add-{TABLE_PROJECT}")

        elif menu_item == _STR_MENU_PERSON:
            _sidebar_display_org_filter()

        elif menu_item == _STR_MENU_AWARD:
            _sidebar_quick_add_form(form_name=f"quick_add-{TABLE_AWARD}")

        elif menu_item == _STR_MENU_RELATION:
            _sidebar_display_rel_type()

        else:
            pass

# body
def do_body():
    menu_item = st.session_state.get("menu_item", _STR_MENU_HOME)
    menu_dict[menu_item]["fn"]()

def main():
    # _load_db()
    do_sidebar()
    do_body()

if __name__ == '__main__':
    main()
