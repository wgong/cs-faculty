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