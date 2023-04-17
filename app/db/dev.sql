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