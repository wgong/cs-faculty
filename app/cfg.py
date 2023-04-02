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

EDITABLE_COLUMNS =  {
    "t_faculty": [
        'job_title',
        'phd_univ',
        'phd_year',
        'research_area',
        'research_concentration',
        'research_focus',
        'phone',
        'email',
        'cell_phone',
        'office_address',
        'department',
        'school'    
    ],
    't_note': [
        'title', 'url', 'note', 'tags'
    ],
    't_research_group': [
        'research_group', 'url'
    ],
}