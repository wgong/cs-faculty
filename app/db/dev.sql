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