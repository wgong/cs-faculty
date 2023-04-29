CREATE TYPE field_ui_type AS ENUM (
	'text_input', 'text_area', 'selectbox', 'checkbox');

create table g_column_props (
	table_name VARCHAR
	,col_name VARCHAR
	,is_system_col BOOLEAN
	,is_user_key BOOLEAN
	,is_required BOOLEAN
	,is_visible BOOLEAN
	,is_editable BOOLEAN
	,is_clickable BOOLEAN
	,form_column VARCHAR
	,widget_type field_ui_type
	,label_text VARCHAR
	,kwargs VARCHAR
);
-- select * from g_column_props;


create table g_entity (
	id VARCHAR NOT NULL
	,uid VARCHAR
	,ts VARCHAR
	,entity_type VARCHAR NOT NULL
	,name VARCHAR NOT NULL
	,url VARCHAR
	,note VARCHAR
);

create table g_note (
	id VARCHAR NOT NULL
	,uid VARCHAR
	,ts VARCHAR
	,name VARCHAR NOT NULL
	,url VARCHAR
	,note VARCHAR
    ,tags VARCHAR
	,ref_key VARCHAR -- e.g. g_person#url  table#column
	,ref_val VARCHAR -- e.g. url value
);


-- g_org is g_entity where entity_type = 'org'
-- g_research_group is g_entity where entity_type = 'research_group'

create table g_person (
	id VARCHAR NOT NULL
	,uid VARCHAR
	,ts VARCHAR
	,person_type VARCHAR  -- e.g. faculty, student, staff
	,name VARCHAR NOT NULL
	,url VARCHAR
	,note VARCHAR
	,email VARCHAR
	,first_name VARCHAR
	,mid_name VARCHAR
	,last_name VARCHAR
	,job_title VARCHAR
	,phd_univ VARCHAR
	,phd_year VARCHAR
	,research_area VARCHAR
	,research_concentration VARCHAR
	,research_focus VARCHAR
	,img_url VARCHAR
	,phone VARCHAR
	,cell_phone VARCHAR
	,office_address VARCHAR
	,department VARCHAR
	,org VARCHAR
);


create table g_work (
	id VARCHAR NOT NULL
	,uid VARCHAR
	,ts VARCHAR
	,work_type VARCHAR -- e.g. publication, talk, poster, project, startup
	,name VARCHAR NOT NULL
	,url VARCHAR
	,note VARCHAR
	,summary VARCHAR
	,authors VARCHAR
	,tags VARCHAR
);
  
-- generic table to store relationship between two entities
-- rel_type = 
--		person-work (represent one's work like publication, talk)
--		team-person (represent one's team members, a faculty has a team by default)
create table g_relation (
	id VARCHAR NOT NULL
	,uid VARCHAR
	,ts VARCHAR
	,rel_type VARCHAR
	,ref_tab text  -- table (parent)
	,ref_key VARCHAR  -- object (parent) e.g. person
	,ref_val VARCHAR
	,ref_tab_sub VARCHAR
	,ref_key_sub VARCHAR  -- subject (child) e.g. person's work
	,ref_val_sub VARCHAR
);


select  c.table_name, c.column_name, c.data_type
--, c.*
from information_schema.columns c
where 1=1
--and c.table_catalog = 'faculty-Cornell-CS'
and c.table_schema = 'main'
and c.table_name like 'g_%'
order by c.table_catalog,c.table_schema,c.table_name, c.ordinal_position
;



    