
# design

entity should have :

table prefix: "t_"

- system columns:
        - id (required),  
        - ts (last update timestamp), 
        - uid (last updated by user, foreign key to t_user table)
        
        - ts_creation (creation timestamp)
        - uid_creation (creation user)

- user-keys columns: 
        - name (required)
        - url 
- note: long description

- editable columns: appear in CRUD form
- clickable columns: 
        - url
        - url_img

# entity
3 broad categories:
- product - what
- people - who, org
- process - how/when/where

## product related (what) 

### research_discipline (table t_discipline)
- name (e.g. CS, Physics, ...)
- url (e.g. wikipedia link)
- note

### research_field (table t_research_field)
- name (e.g. AI, security, ...)
- url (e.g. wikipedia link)
- note

### research_group (table t_research_group)
- name (e.g. UCB System, ...)
- url (e.g. school link)
- note

### notes (table t_note)
- name
- url
- tags
- note
- ref_type (optional) if this note belongs to an entity
- ref_key (optional)

### research_work  (table t_work)
- name
- url
- type: publication, preprint, talk, poster, project, startup, company...
- summary
- authors
- tags
- note

## people (who) related 

### organization (table t_org)
- name
- url
- note

### user (table t_user)
- userid  (unique string like email)
- password
- is_active
- note

system user: id = 0, userid = admin

### person (table t_person)
- name
- url
- email
- job_title
- person_type (e.g. faculty, student, staff, other)
- phd_univ
- phd_year
- research_area
- research_concentration
- research_focus
- first_name
- mid_name
- last_name
- img_url
- phone
- cell_phone
- office_address
- department
- school
- org
- note

### team (table t_team)
- name
- url
- team_lead (FK to person's name)
- note

### entity with 3 common attributes (table s_entity)
- entity_type  [t_org, t_discipline, t_research_field, t_research_group]
- name
- url
- note

## process related (how - operational data)

### team_member (table t_relation)
intersection between two entities, e.g., t_person and t_team, t_person and t_work
- ref_type: t_person
- ref_key: id or name ## url (delimiter=" ## ") 
- ref_type_2: t_work
- ref_key_2: id or name ## url

