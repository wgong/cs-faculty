select * from t_faculty where url='http://people.ece.cornell.edu/atang/' ;
select * from t_work;

insert into t_work(id, type,title,url,summary,authors)
values (
'atang/pub/22/ICML2022.pdf',
'publication',
'Task-aware Privacy Preservation for Multi-dimensional Data',
'http://people.ece.cornell.edu/atang/pub/22/ICML2022.pdf',
'Extensive experiments demonstrate that our task-aware approach significantly
improves ultimate task accuracy compared to standard benchmark LDP approaches with the same
level of privacy guarantee', 
'J. Cheng, A. Tang and S. Chinchali'
);

insert into t_work(id, type,title,url,summary,authors)
values (
'atang/pub/21/NeurIPS-2021.pdf',
'publication',
'Data Sharing and Compression for Cooperative Networked Control',
'http://people.ece.cornell.edu/atang/pub/21/NeurIPS-2021.pdf',
'we present theoretical compression results for a networked variant of the classical
linear quadratic regulator (LQR) control problem', 
'J. Cheng, M. Pavone, S. Katti, S. Chinchali, and A. Tang'
);

describe t_work;
alter table t_work add id text;
alter table t_work add ts text;

alter table t_team add id text;
select * from t_team;

insert into t_person_work(id, ts, ref_type, ref_key, ref_type_2, ref_key_2)
values (
'atang/pub/21/NeurIPS-2021.pdf',
'2023-04-16 10:01:02',
't_faculty',
'http://people.ece.cornell.edu/atang/',
't_work',
'atang/pub/21/NeurIPS-2021.pdf'
);

insert into t_person_work(id, ts, ref_type, ref_key, ref_type_2, ref_key_2)
values (
'atang/pub/22/ICML2022.pdf',
'2023-04-16 10:01:01',
't_faculty',
'http://people.ece.cornell.edu/atang/',
't_work',
'atang/pub/22/ICML2022.pdf'
);

select * from t_person_work;
select * from t_work;

select * from t_faculty;
select * from t_research_group;
select * from t_note;

describe t_team;
insert into t_team(name,url,note) values (
'Networks Group at Cornell',
'http://networks.ece.cornell.edu/',
'We are broadly interested in control, optimization, and their applications in networking and networked systems.'
);

describe t_person;
select * from t_person;
insert into t_person
(
	name
	,url
	,email
	,first_name
	,last_name) 
values 
(
	'Yuchong Geng'
	,'https://yuchong-geng.github.io/'
	,'yg534@cornell.edu'
	,'Yuchong'
	,'Geng'),
(
	'Faraz Farahvash'
	,'http://networks.ece.cornell.edu/faraz'
	,'ff227@cornell.edu'
	,'Faraz'
	,'Farahvash')
;


describe t_person_team;
select * from t_person_team;

insert into t_person_team(id, ts, ref_type, ref_key, ref_type_2, ref_key_2)
values (
't_faculty # http://people.ece.cornell.edu/atang/'
,'2023-04-16 10:01:01'
,'t_team'
,'http://networks.ece.cornell.edu/'
,'t_faculty'
,'http://people.ece.cornell.edu/atang/'
),
(
't_person # https://yuchong-geng.github.io/'
,'2023-04-16 10:01:01'
,'t_team'
,'http://networks.ece.cornell.edu/'
,'t_person'
,'https://yuchong-geng.github.io/'
), 
(
't_person # http://networks.ece.cornell.edu/faraz'
,'2023-04-16 10:01:01'
,'t_team'
,'http://networks.ece.cornell.edu/'
,'t_person'
,'http://networks.ece.cornell.edu/faraz'
)
;

with team as (
    select ref_key as team_url
    from t_person_team
    where ref_type = 't_team' and
    ref_type_2 = 't_faculty' and ref_key_2 = 'http://people.ece.cornell.edu/atang/'
)
select p.* from t_person p 
join t_person_team pt
    on pt.ref_type_2 = 't_person' and pt.ref_key_2 = p.url
join team t
    on pt.ref_type = 't_team' and pt.ref_key = t.team_url
    ;

select * from t_note
where ref_type = 't_faculty' and ref_key = 'http://people.ece.cornell.edu/atang/';
    
describe t_note;
select * from t_note;
insert into t_note(
title
,note
,url
,id
,ref_type
,ref_key
) values (
'Kevin Tang Home page'
,'I teach in the School of ECE (Electrical and Computer Engineering) at Cornell'
,'http://people.ece.cornell.edu/atang/'
,'t_faculty # http://people.ece.cornell.edu/atang/'
,'t_faculty'
,'http://people.ece.cornell.edu/atang/'
);


create table if not exists t_note (
                title text not null
                ,url   text
                ,note  text 
                ,tags  text
                ,ts    text
                ,id    text);
                
describe t_person_work;

-- https://duckdb.org/docs/sql/information_schema
select  current_schema();

-- select  current_schemas(TRUE);

call duckdb_functions();
SELECT * FROM duckdb_settings();

call duckdb_settings();
-- SELECT SERVERPROPERTY('EngineEdition');

select * from information_schema.schemata;

select  t.table_name
from information_schema.tables t where t.table_name like 'g_%';

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


-- Meta table
select  c.table_name, c.column_name, c.data_type --, c.*
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
order by c.table_name, c.ordinal_position
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


select  c.table_name, c.column_name, c.data_type --, c.*
from information_schema.columns c
where 1=1
--and c.table_catalog like 'faculty-Cornell-CS%'
and c.table_schema = 'main'
and c.table_name in (
	--'t_note'
	select table_name from information_schema.tables t
	where 1=1
	--and t.table_catalog like 'faculty-Cornell-CS%'
	and t.table_schema = 'main'
)
and c.table_name not like 't1_%'
order by c.table_catalog,c.table_schema,c.table_name, c.ordinal_position
;

select * from information_schema.tables t;

select * from t_column_props;

create table t1_faculty as select * from t_faculty;
create table t1_note as select * from t_note;
create table t1_person as 
select * from t_person;
create table t1_person_team as select * from t_person_team;
create table t1_person_work as 
select * from t_person_work;
create table t1_research_group as select * from t_research_group;
create table t1_team as select * from t_team;
create table t1_work as 
select * from t_work;

delete from t_work where authors='Y. Bi and A. Tang';

select * from t1_faculty;
select name,url,job_title,phd_univ,phd_year,research_area,research_concentration,research_focus,img_url,phone,email,cell_phone,office_address,department,school,note from t1_faculty order by name


select * from t1_person;

select * from t1_research_group;

select * from t1_work;

alter table t_note rename column title to name;
alter table t_research_group rename column research_group to name;
alter table t_work rename column title to name;


-- merge t_faculty into t_person 
update t_person set id = email;
select * from t_person;
select * from t_faculty order by name;

select current_schema();
select gen_random_uuid() as id from t_person;
SELECT strftime(TIMESTAMP '1992-03-02 20:32:45', '%A, %-d %B %Y - %I:%M:%S %p');

alter table t_person add column id text;
alter table t_person add column ts text;
alter table t_person add column job_title text;
alter table t_person add column person_type text;
alter table t_person add column phd_univ text;
alter table t_person add column phd_year text;
alter table t_person add column research_area text;
alter table t_person add column research_concentration text;
alter table t_person add column research_focus text;
alter table t_person add column img_url text;
alter table t_person add column phone text;
alter table t_person add column cell_phone text;
alter table t_person add column office_address text;
alter table t_person add column department text;
alter table t_person add column school text;
alter table t_person add column org text;

select * from t_person_work;
update t_person_work set ref_type='t_person' where ref_type='t_faculty';

select * from t_note;
update t_note set ref_type='t_person' where ref_type='t_faculty';

select * from t_team;
select * from t_person_team;
update t_person_team 
set ref_type_2='t_person', id = 't_person # http://people.ece.cornell.edu/atang/'
where id = 't_faculty # http://people.ece.cornell.edu/atang/';

select * from t_research_group order by name;
select * from t_research_group where url = '' order by name;
--delete from t_research_group where url = '';
alter table t_research_group add column id text;
alter table t_research_group add column ts text;

alter table t_team add column team_lead text;
update t_team set team_lead= 'http://people.ece.cornell.edu/atang/', id=url
where name='Networks Group at Cornell';

select * from t_person where person_type='faculty' order by name;

with per as (
    select 
        pt.ref_key_2 person_url
    from t_team t 
    join t_person_team pt
        on pt.ref_key = t.url 
            and pt.ref_type = 't_team' 
            and pt.ref_type_2 = 't_person' 
    where t.team_lead = 'http://people.ece.cornell.edu/atang/'
)
select p.* 
from t_person p 
join per 
    on per.person_url = p.url
where p.url != 'http://people.ece.cornell.edu/atang/';

select * from t_person where name like '%%be%%';
select * from t_person where name like '%be%';

select * from g_entity;

select * from g_relation;
alter table g_relation add column ref_tab text;
alter table g_relation add column ref_tab_sub text;

select split_part(ref_key, '#', 1) from g_relation;

update g_relation 
set ref_tab='g_person', ref_tab_sub='g_work',
ref_key='url', ref_key_sub='id'
where rel_type = 'person-work';

update g_relation 
set ref_tab='g_person', ref_tab_sub='g_person',
ref_key='url', ref_key_sub='url'
where rel_type = 'team-person';

select org,person_type,count(*) from g_person group by org,person_type;
-- https://www.sqlshack.com/different-ways-to-sql-delete-duplicate-rows-from-a-sql-table/





--delete from g_entity where entity_type='research_group' and url like 'https://www2.eecs.berkeley.edu/%' ;
--delete from g_person where org = 'Univ California Berkeley';

select * from g_entity where entity_type='research_group' and note is null;

update g_entity set note='Cornell' where entity_type='research_group' and url like '%cornell%';
update g_entity set note='Berkeley' where entity_type='research_group' and url like '%berkeley%';
update g_entity set note='MIT' where entity_type='research_group' and url like '%mit.edu%';


select name,url, count(*) from g_work group by name,url having count(*) > 1;  -- 36 dup 
select name,url, count(*) from g_entity group by name,url having count(*) > 1;  -- 36 dup 

select name,url, count(*) from g_person group by name,url having count(*) > 1;  -- 36 dup 
-- REMOVE DUPLICATES
WITH dup AS (
	SELECT name,url, id, ROW_NUMBER() OVER(PARTITION BY name,url ORDER BY id) AS dup_id
   	FROM g_person
)
--SELECT * FROM dup where dup_id > 1
--select * 
delete from g_person where id in (
	select id from dup where dup_id > 1
)
;

select * from g_person where org is null;
select org,count(*) from g_person group by org;
select count(*) from g_person;

