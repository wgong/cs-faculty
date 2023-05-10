# duckdb file
FILE_DB = f"./db/cs-faculty-20230502.duckdb"

# ORG_ALIAS = {
#     "Cornell": "Cornell Univ",
#     "MIT": "Massachusetts Institute Technology",
#     "CMU": "Carnegie Mellon Univ",
#     "Berkely": "Univ California Berkeley",
#     "Stanford": "Stanford Univ",
#     "UIUC": "Univ Illinois Urbana-Champaign",
# }

# generic object
TABLE_ENTITY = "g_entity"
TABLE_EXTENT = "g_extent"   
# extension table for g_entity (1:1, with same ID)
TABLE_RELATION = "g_relation" 
# M:M relationship between 2 entities: (object-subject) object as parent, subject as child

# simple entity
TABLE_RESEARCH_GROUP = "g_entity" # (entity_type=research_group)
# subject entity (related to object entity as parent)
TABLE_FACULTY = "g_person"  # (person_type=faculty)
TABLE_PERSON = "g_person"
TABLE_WORK = "g_work"
TABLE_NOTE = "g_note"
TABLE_TASK = "g_task"

TABLE_LIST = [
    TABLE_ENTITY, 
    TABLE_RELATION, 
    TABLE_PERSON,
    TABLE_WORK,
    TABLE_NOTE,
    TABLE_TASK,
]

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
)

WORK_TYPES = (
    '',
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
    'researcher', 
    'postdoc', 
    'staff', 
    'student', 
    'other',
)

TASK_STATUS = [
    '', 'In Progress', 'Pending', 'Completed', 'Canceled',
]

PRIORITY = [
    '', 'Urgent', 'Important-1', 'Important-2', 'Important-3',
]

## Important Note:
# for a LOV typed filed to be displayed as selectbox properly
# on UI-form when no row is selected,
# ensure the LOV type has empty string value as a default type
SELECTBOX_OPTIONS = {
    "entity_type": ENTITY_TYPES,
    "work_type": WORK_TYPES,
    "person_type": PERSON_TYPES,
    "priority": PRIORITY,
    "task_status": TASK_STATUS,
}

# columns for Quick Add
DATA_COLS = {
    TABLE_FACULTY : ['name', 'url', 'job_title',
        'research_area', 'award', 'email','department', 'org',
        'phd_univ','phd_year','note',],
    TABLE_RESEARCH_GROUP: ['name', 'url', 'note',],
    TABLE_NOTE: ['name', 'url',"tags", 'note',],
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

        "note": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_2-1",
            "widget_type": "text_area",
            "label_text": "Note"
        },

        "id": {
            "is_system_col": True,
            "is_user_key": False,
            "is_required": True,
            "is_visible": True,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "COL_3-1",
            "widget_type": "text_input",
            "label_text": "ID"
        },
        "entity_type": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_3-2",
            "widget_type": "selectbox",
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
        "department": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_1-5",
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



        "id": {
            "is_system_col": True,
            "is_user_key": False,
            "is_required": True,
            "is_visible": True,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "COL_3-1",
            "widget_type": "text_input",
            "label_text": "ID"
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
        "id": {
            'is_system_col': True,
            'is_user_key': False,
            'is_required': True,
            'is_visible': True,
            'is_editable': False,
            'is_clickable': False,
            'form_column': 'COL_2-1',
            'widget_type': 'text_input',
            'label_text': 'ID'                  
        },
        "note": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': False,
            'form_column': 'COL_2-2',
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
            'widget_type': 'text_input',
        },
        "ref_key": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': False,
            'form_column': 'COL_3-2',
            'widget_type': 'text_input',
        },
        "ref_val": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': False,
            'form_column': 'COL_3-3',
            'widget_type': 'text_input',
        },
        "ts": {
            'is_system_col': True,
            'is_user_key': False,
            'is_required': False,
            'is_visible': False,
            'is_editable': False,
            'is_clickable': False,
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

        "id": {
            "is_system_col": True,
            "is_user_key": False,
            "is_required": True,
            "is_visible": True,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "COL_3-1",
            "widget_type": "text_input",
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
        "ts": {
            "is_system_col": True,
            "is_user_key": False,
            "is_required": False,
            "is_visible": False,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "COL_3-4",
            "widget_type": "text_input",
            }
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

        "id": {
            "is_system_col": True,
            "is_user_key": False,
            "is_required": True,
            "is_visible": True,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "COL_3-1",
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
            "widget_type": "text_input",
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
            "widget_type": "text_input",
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
            "widget_type": "text_input",
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


        "ts": {
            "is_system_col": True,
            "is_user_key": False,
            "is_required": False,
            "is_visible": False,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "COL_3-3",
            "widget_type": "text_input",
            }
    },


    "g_relation": {
        "rel_type": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "COL_1-1",
            "widget_type": "text_input",
            },
        "ref_key": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": False,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "COL_1-2",
            "widget_type": "text_input",
            },
        "ref_val": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": False,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "COL_1-3",
            "widget_type": "text_input",
            },

        "id": {
            "is_system_col": True,
            "is_user_key": False,
            "is_required": True,
            "is_visible": False,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "COL_2-1",
            "widget_type": "text_input",
            },

        "ref_key_sub": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": False,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "COL_2-2",
            "widget_type": "text_input",
            },
        "ref_val_sub": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": False,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "COL_2-3",
            "widget_type": "text_input",
            },
    },


}


