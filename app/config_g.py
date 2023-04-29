FILE_ROOT = "./db"
FILE_DB = f"{FILE_ROOT}/faculty-Cornell-CS-20230422.duckdb"
FILE_XLSX = f"{FILE_ROOT}/faculty-Cornell-CS.xlsx"

SYS_COLS = ["id","ts","uid"]
TABLE_NOTE = "g_note" # done
TABLE_ENTITY = "g_entity" # replaced with g_entity (entity_type=research_group)
TABLE_RESEARCH_GROUP = "g_entity" # replaced with g_entity (entity_type=research_group)

TABLE_FACULTY = "g_person"  # replaced with g_person (person_type=faculty)
TABLE_PERSON = "g_person"
TABLE_TEAM = "t_team"   # deprecated
TABLE_WORK = "g_work"
TABLE_PERSON_TEAM = "t_person_team"  # replaced with g_relation (rel_type=team-person)
TABLE_PERSON_WORK = "t_person_work"  # replaced with g_relation (rel_type=person-work)
TABLE_ENTITY = "g_entity"
TABLE_RELATION = "g_relation"


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
    'kwargs']

ENTITY_TYPES = ('research_group',
                )

WORK_TYPES = ('publication', 
              'preprint', 
              'talk', 
              'poster', 
              'documentation', 
              'project', 
              'startup', 
              'company',
              'other',
              )

PERSON_TYPES = ('faculty', 
                'student', 
                'staff', 
                'other',
                )

SELECTBOX_OPTIONS = {
    "entity_type": ENTITY_TYPES,
    "work_type": WORK_TYPES,
    "person_type": PERSON_TYPES,
}

# run query for this meta-info
TABLE_COLUMNS = {
    'g_person': [
        'name',
        'url',
        'job_title',
        'phd_univ',
        'phd_year',
        'research_area',
        'research_concentration',
        'research_focus',
        'img_url',
        'phone',
        'email',
        'cell_phone',
        'office_address',
        'department',
        'school',
        'note'
    ],
    'g_note': [
        'title', 
        'url', 
        'note', 
        'tags', 
        'ts', 
        'id'
    ],
    'g_entity': [
        'research_group', 
        'url',
        'note',
    ],
}

KEY_COLUMNS = {
    "g_person": 'name',
    'g_note': 'id',
    'g_entity': 'name',    
}


EDITABLE_COLUMNS =  {
    table : [c for c in TABLE_COLUMNS[table] if c != KEY_COLUMNS[table]] for table in TABLE_COLUMNS.keys()
}

CLICKABLE_COLUMNS = {
    "g_person": [
        'url',
        'img_url',
    ],
    'g_note': [
        'url',
    ],
    'g_entity': [
        'url',
    ],    
}


## TODO
# move data into g_column_props table
# this will be defined by UI
COLUMN_PROPS = {

    "g_entity": {
        "name": {
            "is_system_col": False,
            "is_user_key": True,
            "is_required": True,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "col1-1",
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
            "form_column": "col1-2",
            "widget_type": "text_input",
            "label_text": "URL"
        },
        "entity_type": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "col1-3",
            "widget_type": "selectbox",
        },
        
        "id": {
            "is_system_col": True,
            "is_user_key": False,
            "is_required": True,
            "is_visible": True,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "col2-1",
            "widget_type": "text_input",
            "label_text": "ID"
        },

        "note": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "col2-2",
            "widget_type": "text_area",
            "label_text": "Note"
        }
    },

    "g_person": {
        "name": {
            "is_system_col": False,
            "is_user_key": True,
            "is_required": True,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "col1-1",
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
            "form_column": "col1-2",
            "widget_type": "text_input",
            "label_text": "URL"
        },
        "email": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "col1-3",
            "widget_type": "text_input",
            "label_text": "Email"
        },
        "job_title": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "col1-4",
            "widget_type": "text_input",
            "label_text": "Job Title"
        },

        "research_area": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "col1-5",
            "widget_type": "text_input",
            "label_text": "Research Area"
        },

        "id": {
            "is_system_col": True,
            "is_user_key": False,
            "is_required": True,
            "is_visible": True,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "col2-1",
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
            "form_column": "col2-2",
            "widget_type": "selectbox",
            "label_text": "Person Type"
        },
        "cell_phone": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "col2-3",
            "widget_type": "text_input",
            "label_text": "Cell Phone"
        },
        "note": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "col2-4",
            "widget_type": "text_area",
            "label_text": "Note"
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
            'form_column': 'col1-1',
            'widget_type': 'text_input',
        },
        "url": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': True,
            'form_column': 'col1-2',
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
            'form_column': 'col1-3',
            'widget_type': 'text_input',
        },
        "ref_key": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': False,
            'form_column': 'col1-4',
            'widget_type': 'text_input',
        },
        "id": {
            'is_system_col': True,
            'is_user_key': False,
            'is_required': True,
            'is_visible': True,
            'is_editable': False,
            'is_clickable': False,
            'form_column': 'col2-1',
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
            'form_column': 'col2-2',
            'widget_type': 'text_area',
        },
        "ref_val": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': True,
            'is_editable': True,
            'is_clickable': False,
            'form_column': 'col2-3',
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
            "form_column": "col1-1",
            "widget_type": "text_input",
            },
        "url": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": True,
            "form_column": "col1-2",
            "widget_type": "text_input",
            },
        "authors": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "col1-3",
            "widget_type": "text_input",
            },
        "summary": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "col1-4",
            "widget_type": "text_area",
            },
        "id": {
            "is_system_col": True,
            "is_user_key": False,
            "is_required": True,
            "is_visible": True,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "col2-1",
            "widget_type": "text_input",
            },
        "work_type": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "col2-2",
            "widget_type": "selectbox",
            },

        "tags": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "col2-3",
            "widget_type": "text_input",
            },
        "note": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "col2-4",
            "widget_type": "text_area",
            },

        "ts": {
            "is_system_col": True,
            "is_user_key": False,
            "is_required": False,
            "is_visible": False,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "col3-2",
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
            "form_column": "col1-1",
            "widget_type": "text_input",
            },
        "ref_key": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": False,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "col1-2",
            "widget_type": "text_input",
            },
        "ref_val": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": False,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "col1-3",
            "widget_type": "text_input",
            },

        "id": {
            "is_system_col": True,
            "is_user_key": False,
            "is_required": True,
            "is_visible": False,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "col2-1",
            "widget_type": "text_input",
            },

        "ref_key_sub": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": False,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "col2-2",
            "widget_type": "text_input",
            },
        "ref_val_sub": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": False,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "col2-3",
            "widget_type": "text_input",
            },
    },


}


