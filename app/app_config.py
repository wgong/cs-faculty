# duckdb file
# FILE_DB = f"./db/cs-faculty-20230502.duckdb"
FILE_DB = "cs-faculty-20230604.duckdb"

# generic object
TABLE_ENTITY = "g_entity"
TABLE_EXTENT = "g_extent"   
# extension table for g_entity (1:1, with same ID)
TABLE_RELATION = "g_relation" 
# M:M relationship between 2 entities: (object-subject) object as parent, subject as child

# simple entity
# subject entity (related to object entity as parent)
TABLE_FACULTY = "g_person"  # (person_type=faculty)
TABLE_PERSON = "g_person"
TABLE_NOTE = "g_note"
TABLE_ORG = "g_org"
TABLE_PROJECT = "g_project"
TABLE_WORK = "g_work"
TABLE_TASK = "g_task"
## views
TABLE_AWARD = "g_entity" # (entity_type=award, view=g_award)
TABLE_RESEARCH_GROUP = "g_entity" # (entity_type=research_group, view=g_research_group)

# LOV
SYS_COLS = ["id","ts","uid"]

PROPS = [
    'is_system_col',
    'is_user_key',
    'is_required',
    'is_visible',
    'is_editable',
    'is_clickable',
    'form_column',
    'widget_type',
    'label_text',
    'kwargs'
]

ENTITY_TYPES = (
    '',
    'research_group',
    'award',
)

WORK_TYPES = (
    '',
    'profile', 
    'publication', 
    'paper', 
    'preprint', 
    'thesis', 
    'conference', 
    'talk', 
    'poster',
    'course',
    'book', 
    'documentation', 
    'tutorial', 
    'project', 
    'startup', 
    'company',
    'other',
)

PERSON_TYPES = (
    '',
    'faculty', 
    'team-lead', 
    'researcher', 
    'postdoc', 
    'staff', 
    'student', 
    'other',
)

NOTE_TYPES = (
    '',
    'journal', 
    'resource', 
    'idea', 
    'information', 
    'news', 
    'reminder', 
    'other',
)

ORG_TYPES = (
    '',
    'university', 
    'school', 
    'company', 
    'government', 
    'non-profit', 
    'other',
)

PROJECT_TYPES = (
    '',
    'work', 
    'personal', 
    'open-source', 
    'other',
)

TASK_STATUS = [
    '', 'In Progress', 'Pending', 'Completed', 'Canceled',
]

PRIORITY = [
    '', 'Urgent', 'Important-1', 'Important-2', 'Important-3',
]

# columns for Quick Add
COMMON_DATA_COLS = ['name', 'url', 'note', "tags"]

DATA_COLS = {
    TABLE_FACULTY: COMMON_DATA_COLS + ['job_title',
        'research_area', 'email', 'award', 'department', 'org',
        'phd_univ','phd_year',],
    TABLE_RESEARCH_GROUP: COMMON_DATA_COLS,
    TABLE_NOTE: COMMON_DATA_COLS + ['note_type'],
    TABLE_ORG: COMMON_DATA_COLS + ['org_type'],
    TABLE_PROJECT: COMMON_DATA_COLS + ['project_type'],
}

## TODO
# move data into g_column_props table
# in order to become UI-configurable
COLUMN_PROPS = {

    "g_entity": {
        "name": {
            "is_system_col": False,
            "is_user_key": True,
            "is_required": True,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_1-1",
            "widget_type": "text_input",
            "label_text": "Name"
        },
        "url": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": True,
            "form_column": "COL_1-2",
            "widget_type": "text_input",
            "label_text": "URL"
        },

        "tags": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_1-3",
            "widget_type": "text_input",
        },

        "entity_type": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_2-2",
            "widget_type": "selectbox",
        },
        "note": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_2-3",
            "widget_type": "text_area",
            "label_text": "Note"
        },

        "ref_tab": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_3-1",
            "widget_type": "selectbox",
            "label_text": "Ref Table",              
            },
        "ref_key": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_3-2",
            "widget_type": "selectbox",
            "label_text": "Ref Column",              
            },
        "ref_val": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_3-3",
            "widget_type": "selectbox",  
            "label_text": "Ref Value",              
            },

        "id": {
            "is_system_col": True,
            "is_user_key": False,
            "is_required": True,
            "is_visible": True,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "COL_3-97",
            "widget_type": "text_input",
            "label_text": "ID"
        },
        "ts": {
            'is_system_col': True,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': False,
            'is_clickable': False,
            "form_column": "COL_3-98",
            "widget_type": "text_input",
            "label_text": "Timestamp",              
        },
        "uid": {
            'is_system_col': True,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': False,
            'is_clickable': False,
            "form_column": "COL_3-99",
            "widget_type": "text_input",
            "label_text": "UID",              
        },

    },

    "g_relation": {


        "ref_tab": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_1-2",
            "widget_type": "selectbox",
            "label_text": "Object Table"
        },
        "ref_key": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_1-3",
            "widget_type": "selectbox",
            "label_text": "Object Column",              
        },
        "ref_val": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_1-4",
            "widget_type": "text_input",  
            "label_text": "Object Value",              
        },


        "ref_tab_sub": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_2-1",
            "widget_type": "selectbox",
            "label_text": "Subject Table"
        },
        "ref_key_sub": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_2-2",
            "widget_type": "selectbox",
            "label_text": "Subject Column",              
        },
        "ref_val_sub": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_2-3",
            "widget_type": "text_input",  
            "label_text": "Subject Value",              
        },


        "props": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_3-2",
            "widget_type": "text_area",
            "label_text": "Props"
        },

        "rel_type": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_3-3",
            "widget_type": "text_input",
            "label_text": "Relation Type"
        },

        "id": {
            "is_system_col": True,
            "is_user_key": False,
            "is_required": True,
            "is_visible": True,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "COL_3-97",
            "widget_type": "text_input",
            "label_text": "ID"
        },
        "ts": {
            'is_system_col': True,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': False,
            'is_clickable': False,
            "form_column": "COL_3-98",
            "widget_type": "text_input",
            "label_text": "Timestamp",              
        },
        "uid": {
            'is_system_col': True,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': False,
            'is_clickable': False,
            "form_column": "COL_3-99",
            "widget_type": "text_input",
            "label_text": "UID",              
        },

    },

    "g_person": {
        "name": {
            "is_system_col": False,
            "is_user_key": True,
            "is_required": True,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_1-1",
            "widget_type": "text_input",
            "label_text": "Name"
        },
        "url": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": True,
            "form_column": "COL_1-2",
            "widget_type": "text_input",
            "label_text": "URL"
        },
        "research_area": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_1-3",
            "widget_type": "text_input",
            "label_text": "Research Area"
        },
        "job_title": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_1-4",
            "widget_type": "text_input",
        },
        "tags": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_1-5",
            "widget_type": "text_input",
        },
        "department": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_1-6",
            "widget_type": "text_input",
        },

        "email": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_2-1",
            "widget_type": "text_input",
            "label_text": "Email"
        },
        "cell_phone": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_2-2",
            "widget_type": "text_input",
            "label_text": "Cell"
        },
        "office_address": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_2-3",
            "widget_type": "text_input",

        },
        "note": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_2-4",
            "widget_type": "text_area",
            "label_text": "Note",
        },


        "person_type": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_3-2",
            "widget_type": "selectbox",
            "label_text": "Person Type"
        },
        "award": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_3-3",
            "widget_type": "text_input",
            },

        "org": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_3-4",
            "widget_type": "text_input",
        },


        "phd_univ": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_3-5",
            "widget_type": "text_input",
        },
        "phd_year": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_3-6",
            "widget_type": "text_input",
        },


        "id": {
            "is_system_col": True,
            "is_user_key": False,
            "is_required": True,
            "is_visible": True,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "COL_3-97",
            "widget_type": "text_input",
            "label_text": "ID"
        },
        "ts": {
            'is_system_col': True,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': False,
            'is_clickable': False,
            "form_column": "COL_3-98",
            "widget_type": "text_input",
            "label_text": "Timestamp",              
        },
        "uid": {
            'is_system_col': True,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': False,
            'is_clickable': False,
            "form_column": "COL_3-99",
            "widget_type": "text_input",
            "label_text": "UID",              
        },

    },

    "g_note" : {
        "name": {
            'is_system_col': False,
            'is_user_key': True,
            'is_required': True,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': False,
            'form_column': 'COL_1-1',
            'widget_type': 'text_input',
        },
        "url": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': True,
            'form_column': 'COL_1-2',
            'widget_type': 'text_input',
            'label_text': 'URL'  
        },
        "tags": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': False,
            'form_column': 'COL_1-3',
            'widget_type': 'text_input',
        },

        "note_type": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': False,
            'form_column': 'COL_2-2',
            'widget_type': 'selectbox',
        },
        "note": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': False,
            'form_column': 'COL_2-3',
            'widget_type': 'text_area',
        },
        "ref_tab": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': False,
            'form_column': 'COL_3-1',
            'widget_type': 'selectbox',
            "label_text": "Ref Table",              
        },
        "ref_key": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': False,
            'form_column': 'COL_3-2',
            'widget_type': 'selectbox',
            "label_text": "Ref Column",              
        },
        "ref_val": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': False,
            'form_column': 'COL_3-3',
            'widget_type': "selectbox",  # 'text_input',
            "label_text": "Ref Value",              
        },

        "id": {
            "is_system_col": True,
            "is_user_key": False,
            "is_required": True,
            "is_visible": True,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "COL_3-97",
            "widget_type": "text_input",
            "label_text": "ID"
        },
        "ts": {
            'is_system_col': True,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': False,
            'is_clickable': False,
            "form_column": "COL_3-98",
            "widget_type": "text_input",
            "label_text": "Timestamp",              
        },
        "uid": {
            'is_system_col': True,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': False,
            'is_clickable': False,
            "form_column": "COL_3-99",
            "widget_type": "text_input",
            "label_text": "UID",              
        },

    },

    "g_org" : {
        "name": {
            'is_system_col': False,
            'is_user_key': True,
            'is_required': True,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': False,
            'form_column': 'COL_1-1',
            'widget_type': 'text_input',
        },
        "url": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': True,
            'form_column': 'COL_1-2',
            'widget_type': 'text_input',
            'label_text': 'URL'  
        },
        "tags": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': False,
            'form_column': 'COL_1-3',
            'widget_type': 'text_input',
        },

        "org_type": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': False,
            'form_column': 'COL_2-2',
            'widget_type': 'selectbox',
        },
        "note": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': False,
            'form_column': 'COL_2-3',
            'widget_type': 'text_area',
        },
        "ref_tab": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': False,
            'form_column': 'COL_3-1',
            'widget_type': 'selectbox',
            "label_text": "Ref Table",              
        },
        "ref_key": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': False,
            'form_column': 'COL_3-2',
            'widget_type': 'selectbox',
            "label_text": "Ref Column",              
        },
        "ref_val": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': False,
            'form_column': 'COL_3-3',
            'widget_type': "selectbox",  # 'text_input',
            "label_text": "Ref Value",              
        },

        "id": {
            "is_system_col": True,
            "is_user_key": False,
            "is_required": True,
            "is_visible": True,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "COL_3-97",
            "widget_type": "text_input",
            "label_text": "ID"
        },
        "ts": {
            'is_system_col': True,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': False,
            'is_clickable': False,
            "form_column": "COL_3-98",
            "widget_type": "text_input",
            "label_text": "Timestamp",              
        },
        "uid": {
            'is_system_col': True,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': False,
            'is_clickable': False,
            "form_column": "COL_3-99",
            "widget_type": "text_input",
            "label_text": "UID",              
        },


    },

    "g_project" : {
        "name": {
            'is_system_col': False,
            'is_user_key': True,
            'is_required': True,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': False,
            'form_column': 'COL_1-1',
            'widget_type': 'text_input',
        },
        "url": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': True,
            'form_column': 'COL_1-2',
            'widget_type': 'text_input',
            'label_text': 'URL'  
        },
        "tags": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': False,
            'form_column': 'COL_1-3',
            'widget_type': 'text_input',
        },

        "project_type": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': False,
            'form_column': 'COL_2-2',
            'widget_type': 'selectbox',
        },
        "note": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': False,
            'form_column': 'COL_2-3',
            'widget_type': 'text_area',
        },
        "ref_tab": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': False,
            'form_column': 'COL_3-1',
            'widget_type': 'selectbox',
            "label_text": "Ref Table",              
        },
        "ref_key": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': False,
            'form_column': 'COL_3-2',
            'widget_type': 'selectbox',
            "label_text": "Ref Column",              
        },
        "ref_val": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': False,
            'form_column': 'COL_3-3',
            'widget_type': "selectbox",  # 'text_input',
            "label_text": "Ref Value",              
        },

        "id": {
            "is_system_col": True,
            "is_user_key": False,
            "is_required": True,
            "is_visible": True,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "COL_3-97",
            "widget_type": "text_input",
            "label_text": "ID"
        },
        "ts": {
            'is_system_col': True,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': False,
            'is_clickable': False,
            "form_column": "COL_3-98",
            "widget_type": "text_input",
            "label_text": "Timestamp",              
        },
        "uid": {
            'is_system_col': True,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': False,
            'is_clickable': False,
            "form_column": "COL_3-99",
            "widget_type": "text_input",
            "label_text": "UID",              
        },

    },


    "g_work": {
        "name": {
            "is_system_col": False,
            "is_user_key": True,
            "is_required": True,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_1-1",
            "widget_type": "text_input",
            },
        "url": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": True,
            "form_column": "COL_1-2",
            "widget_type": "text_input",
            },
        "summary": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_1-3",
            "widget_type": "text_area",
            },
        "authors": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_2-1",
            "widget_type": "text_input",
            },
        "tags": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_2-2",
            "widget_type": "text_input",
            },
        "note": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_2-3",
            "widget_type": "text_area",
            },


        "work_type": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_3-2",
            "widget_type": "selectbox",
            },

        "award": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_3-3",
            "widget_type": "text_input",
            },

        "id": {
            "is_system_col": True,
            "is_user_key": False,
            "is_required": True,
            "is_visible": True,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "COL_3-97",
            "widget_type": "text_input",
            "label_text": "ID"
        },
        "ts": {
            'is_system_col': True,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': False,
            'is_clickable': False,
            "form_column": "COL_3-98",
            "widget_type": "text_input",
            "label_text": "Timestamp",              
        },
        "uid": {
            'is_system_col': True,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': False,
            'is_clickable': False,
            "form_column": "COL_3-99",
            "widget_type": "text_input",
            "label_text": "UID",              
        },


    },

    "g_task": {
        "name": {
            "is_system_col": False,
            "is_user_key": True,
            "is_required": True,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_1-1",
            "widget_type": "text_input",
            },
        "url": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": True,
            "form_column": "COL_1-2",
            "widget_type": "text_input",
            },
        "priority": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_1-3",
            "widget_type": "selectbox",
            },
        "note": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_1-4",
            "widget_type": "text_area",
            },
        "tags": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_1-5",
            "widget_type": "text_input",
            },

        "task_status": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_2-1",
            "widget_type": "selectbox",
            },

        "due_date": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_2-2",
            "widget_type": "date_input",
            },
        "alert_date": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_2-3",
            "widget_type": "date_input",
            },
        "alert_time": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_2-4",
            "widget_type": "time_input",
            },
        "alert_to": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_2-5",
            "widget_type": "text_input",
            "label_text": "Alert To (cell or email)",
            },

        "alert_msg": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_2-6",
            "widget_type": "text_input",
            },


        "ref_tab": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_3-2",
            "widget_type": "selectbox",
            "label_text": "Ref Table",              
            },
        "ref_key": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_3-3",
            "widget_type": "selectbox",
            "label_text": "Ref Column",              
            },
        "ref_val": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_3-4",
            "widget_type": "selectbox",  
            "label_text": "Ref Value",              
            },
        "done_date": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_3-5",
            "widget_type": "date_input",
            "label_text": "Completion Date",            
            },



        "id": {
            "is_system_col": True,
            "is_user_key": False,
            "is_required": True,
            "is_visible": True,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "COL_3-97",
            "widget_type": "text_input",
            "label_text": "ID"
        },
        "ts": {
            'is_system_col': True,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': False,
            'is_clickable': False,
            "form_column": "COL_3-98",
            "widget_type": "text_input",
            "label_text": "Timestamp",              
        },
        "uid": {
            'is_system_col': True,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': False,
            'is_clickable': False,
            "form_column": "COL_3-99",
            "widget_type": "text_input",
            "label_text": "UID",              
        },


    },


}

TABLE_LIST = list(COLUMN_PROPS.keys()) + ["g_award","g_research_group"]

