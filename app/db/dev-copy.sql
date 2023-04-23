select  c.table_name, c.column_name, c.data_type, c.*
from information_schema.columns c
where 1=1
and c.table_catalog like 'faculty-Cornell-CS%'
and c.table_schema = 'main'
and c.table_name in (
	--'t_note'
	select table_name from information_schema.tables t
	where t.table_catalog like 'faculty-Cornell-CS%'
	and t.table_schema = 'main'
)
order by c.table_catalog,c.table_schema,c.table_name, c.ordinal_position
;

CREATE TYPE field_ui_type AS ENUM ('text_input', 'text_area', 'select_box', 'check_box');
create table t_column_props (
table_name VARCHAR,
col_name VARCHAR,
is_system_col BOOLEAN,
is_user_key BOOLEAN,
is_required BOOLEAN,
is_visible BOOLEAN,
is_editable BOOLEAN,
is_clickable BOOLEAN,
form_column VARCHAR,
widget_type field_ui_type,
label_text VARCHAR 
);

select * from t_column_props;