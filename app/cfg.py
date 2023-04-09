FILE_ROOT = "./db"
FILE_DB = f"{FILE_ROOT}/faculty-Cornell-CS.duckdb"
FILE_XLSX = f"{FILE_ROOT}/faculty-Cornell-CS.xlsx"

TABLE_NOTE = "t_note"
TABLE_FACULTY = "t_faculty"
TABLE_RESEARCH_GROUP = "t_research_group"

TABLE_COLUMNS = {
    't_faculty': [
        'name',
        'job_title',
        'phd_univ',
        'phd_year',
        'research_area',
        'research_concentration',
        'research_focus',
        'url',
        'img_url',
        'phone',
        'email',
        'cell_phone',
        'office_address',
        'department',
        'school'
    ],
    't_note': [
        'title', 'url', 'note', 'tags', 'ts', 'id'
    ],
    't_research_group': [
        'research_group', 'url'
    ],
}

KEY_COLUMNS = {
    "t_faculty": 'name',
    't_note': 'id',
    't_research_group': 'research_group',    
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

DATA_COLUMNS = {
    "t_faculty": ['name', 'url', 'job_title',
        'research_area', 'email','department', 
        'phd_univ','phd_year'],
    't_research_group': ['research_group', 'url'],
    't_note': [col for col in TABLE_COLUMNS["t_note"] if col not in ["id", "ts"]],
}

FACULTY_DATA_COLS = DATA_COLUMNS["t_faculty"]
GROUP_DATA_COLS = DATA_COLUMNS["t_research_group"]
NOTE_DATA_COLS = DATA_COLUMNS["t_note"]
