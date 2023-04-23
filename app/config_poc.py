FILE_ROOT = "./db"
FILE_DB = f"{FILE_ROOT}/faculty-Cornell-CS-20230422.duckdb"
FILE_XLSX = f"{FILE_ROOT}/faculty-Cornell-CS.xlsx"

TABLE_NOTE = "t_note"
TABLE_FACULTY = "t_faculty"
TABLE_PERSON = "t_person"
TABLE_RESEARCH_GROUP = "t_research_group"
TABLE_TEAM = "t_team"
TABLE_WORK = "t_work"
TABLE_PERSON_TEAM = "t_person_team"
TABLE_PERSON_WORK = "t_person_work"

PROPS = [
    'is_system_col',
    'is_user_key',
    'is_required',
    'is_visible',
    'is_editable',
    'is_clickable',
    'form_column',
    'widget_type',
    'label_text']

WORK_TYPES = ('publication', 
              'preprint', 
              'talk', 
              'poster', 
              'project', 
              'startup', 
              'company')


# run query for this meta-info
TABLE_COLUMNS = {
    't_faculty': [
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
    't_note': [
        'title', 
        'url', 
        'note', 
        'tags', 
        'ts', 
        'id'
    ],
    't_research_group': [
        'research_group', 
        'url',
        'note',

    ],
}

KEY_COLUMNS = {
    "t_faculty": 'name',
    't_note': 'id',
    't_research_group': 'name',    
}


EDITABLE_COLUMNS =  {
    table : [c for c in TABLE_COLUMNS[table] if c != KEY_COLUMNS[table]] for table in TABLE_COLUMNS.keys()
}

CLICKABLE_COLUMNS = {
    "t_faculty": [
        'url',
        'img_url',
    ],
    't_note': [
        'url',
    ],
    't_research_group': [
        'url',
    ],    
}

# derived - non system-cols
DATA_COLUMNS = {
    "t_faculty": ['name', 'url', 'job_title',
        'research_area', 'email','department', 
        'phd_univ','phd_year','note',],
    't_research_group': ['name', 'url', 'note',],
    't_note': [col for col in TABLE_COLUMNS["t_note"] if col not in ["id", "ts"]],
}

FACULTY_DATA_COLS = DATA_COLUMNS["t_faculty"]
GROUP_DATA_COLS = DATA_COLUMNS["t_research_group"]
NOTE_DATA_COLS = DATA_COLUMNS["t_note"]

## TODO this will be defined by UI
COLUMN_PROPS = {
    "t_note" : {
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
        "ts": {
            'is_system_col': True,
            'is_user_key': False,
            'is_required': False,
            'is_visible': False,
            'is_editable': False,
            'is_clickable': False,
        },
        "ref_type": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': False,
            'is_editable': False,
            'is_clickable': False,
        },
        "ref_key": {
            'is_system_col': False,
            'is_user_key': False,
            'is_required': False,
            'is_visible': False,
            'is_editable': False,
            'is_clickable': False,
        },
    },

    "t_team": {
        "name": {
            "is_system_col": False,
            "is_user_key": True,
            "is_required": True,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "col1-1",
            "widget_type": "text_input"},
        "url": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": True,
            "form_column": "col1-2",
            "widget_type": "text_input"},
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
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "col2-2",
            "widget_type": "text_area"}
    },

    "t_work": {
        "type": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "col1-1",
            "widget_type": "text_input",
            },
        "name": {
            "is_system_col": False,
            "is_user_key": True,
            "is_required": True,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "col1-2",
            "widget_type": "text_input",
            },
        "url": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": True,
            "form_column": "col1-3",
            "widget_type": "text_input",
            },
        "authors": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "col1-4",
            "widget_type": "text_input",
            },
        "tags": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "col1-5",
            "widget_type": "text_input",
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
        "summary": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "col2-2",
            "widget_type": "text_area",
            },
        "note": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": True,
            "is_editable": True,
            "is_clickable": False,
            "form_column": "col2-3",
            "widget_type": "text_area",
            },
        "ts_created": {
            "is_system_col": True,
            "is_user_key": False,
            "is_required": False,
            "is_visible": False,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "col3-1",
            "widget_type": "text_input",
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

    "t_person_team": {
        "id": {
            "is_system_col": True,
            "is_user_key": False,
            "is_required": True,
            "is_visible": False,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "col1-1",
            "widget_type": "text_input",
            },
        "ts": {
            "is_system_col": True,
            "is_user_key": False,
            "is_required": False,
            "is_visible": False,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "col1-1",
            "widget_type": "text_input",
            },
        "ref_type": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": False,
            "is_editable": False,
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
            "form_column": "col1-1",
            "widget_type": "text_input",
            },
        "ref_type_2": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": False,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "col1-1",
            "widget_type": "text_input",
            },
        "ref_key_2": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": False,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "col1-1",
            "widget_type": "text_input",
            }
    },

    "t_person_work": {
        "id": {
            "is_system_col": True,
            "is_user_key": False,
            "is_required": True,
            "is_visible": False,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "col1-1",
            "widget_type": "text_input",
            },
        "ts": {
            "is_system_col": True,
            "is_user_key": False,
            "is_required": False,
            "is_visible": False,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "col1-1",
            "widget_type": "text_input",
            },
        "ref_type": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": False,
            "is_editable": False,
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
            "form_column": "col1-1",
            "widget_type": "text_input",
            },
        "ref_type_2": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": False,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "col1-1",
            "widget_type": "text_input",
            },
        "ref_key_2": {
            "is_system_col": False,
            "is_user_key": False,
            "is_required": False,
            "is_visible": False,
            "is_editable": False,
            "is_clickable": False,
            "form_column": "col1-1",
            "widget_type": "text_input",
            }
    },


}


