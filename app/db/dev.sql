select * from t_faculty;
select * from t_research_group;
select * from t_note;

create table if not exists t_note (
                title text not null
                ,url   text
                ,note  text 
                ,tags  text
                ,ts    text
                ,id    text);
                
describe t_note;

-- https://duckdb.org/docs/sql/information_schema
select  current_schema();

-- select  current_schemas(TRUE);

call duckdb_functions();
SELECT * FROM duckdb_settings();

call duckdb_settings();
-- SELECT SERVERPROPERTY('EngineEdition');

select * from information_schema.schemata;

select  t.*
from information_schema.tables t
where 1=1
and t.table_catalog = 'faculty-Cornell-CS'
and t.table_schema = 'main'
;
/*
t_faculty
t_research_group
t_note
t_work
t_org
t_person
t_team
t_person_team
t_person_work
 */

select  c.table_name, c.column_name, c.data_type, c.*
from information_schema.columns c
where 1=1
and c.table_catalog = 'faculty-Cornell-CS'
and c.table_schema = 'main'
and c.table_name in (
	--'t_note'
	select table_name from information_schema.tables t
	where t.table_catalog = 'faculty-Cornell-CS'
	and t.table_schema = 'main'
)
order by c.table_catalog,c.table_schema,c.table_name, c.ordinal_position
;

-- revise schema
alter table t_note add ref_type text;
alter table t_note add ref_key text;
describe t_note;


alter table t_faculty add note text;
alter table t_research_group add note text;
describe t_faculty;

create table if not exists 
t_work (
        type   text not null
        ,title text not null
        ,url   text
        ,summary  text 
        ,authors  text 
        ,tags  text
        ,note  text 
        ,ts_created text
    );
describe t_work;
        
create table if not exists 
t_org (
        name text not null
        ,url   text
        ,note  text 
    );
describe t_org;

create table if not exists 
t_person (
        name text not null
        ,url   text
        ,email  text
        ,first_name  text 
        ,mid_name  text 
        ,last_name  text 
        ,note  text 
    );   
describe t_person;

create table if not exists 
t_team (
        name text not null
        ,url   text
        ,note  text 
    );
    
create table if not exists 
t_person_team (
        id    text not null
        ,ts   text
        ,ref_type text not null
        ,ref_key  text not null
        ,ref_type_2 text not null
        ,ref_key_2  text not null
    );
describe t_person_team;

create table if not exists 
t_person_work (
        id    text not null
        ,ts   text not null
        ,ref_type text not null
        ,ref_key  text not null
        ,ref_type_2 text not null
        ,ref_key_2  text not null
    );
describe t_person_work;    