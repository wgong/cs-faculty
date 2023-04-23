
# design

entity should have :

table prefix: "t_"

- system-columns (required): 
        - id, 
        - ts (last update timestamp), 
        - uid (last updated by user, foreign key to t_user table)
        - ts_creation (creation timestamp)
        - uid_creation (creation user)

- user-keys (required): name | title, url
- note: long description

- data columns: note, ... 
- editable columns: 
- clickable columns: url, url_img
- attachment column: note (free-form long description field)


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

### research_work  (table t_work)
- type: publication, preprint, talk, poster, project, startup, company...
- title
- url
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
- note
- is_active

### person (table t_person)
- name
- url
- email
- first_name
- mid_name
- last_name
- note

### faculty  (table t_faculty)
        'name',
        'url',
        'job_title',
        'phd_univ',
        'phd_year',
        'research_area',
        ...

### team (table t_team)
- name
- url
- note

## process related (how - operational data)

### team_member (table t_person_team)
intersection between t_person and t_team
- ref_type: t_faculty
- ref_key: url ## name  (delimiter=" ## ")
- ref_type_2
- ref_key_2

### publications (table t_person_work)
intersection between t_person and t_work
- ref_type: t_faculty | t_person
- ref_key: url ## name  (delimiter=" ## ")
- ref_type_2 t_work # publication (delimiter=" # ")
- ref_key_2  url ## title

### notes (table t_note)
intersection between t_person and any other entity
- title
- url
- note
- tags
- ref_type (optional)
- ref_key (optional)


