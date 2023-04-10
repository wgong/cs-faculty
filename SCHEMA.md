
# design

entity should have :

- user-keys (required): name | title, url
- system-key (optional): id, ts
- data columns: note, ... 
- editable columns: 
- clickable columns: url, url_img
- attachment columns: note

note is free-form long description field
id, ts are system-fields to track activities, e.g. t_note, t_work

table prefix: "t_"

# entity
3 broad categories:
- product - what
- people - who
- process - how/when/where

## product related (what) 

### research_discipline (table t_discipline)
- name (e.g. CS, Physics, ...)
- url (e.g. wikipedia link)
- description
- note

### research_field (table t_research_field)
- name (e.g. AI, security, ...)
- url (e.g. wikipedia link)
- description
- note

### research_group (table t_research_group)
- name (e.g. UCB System, ...)
- url (e.g. school link)
- description
- note

### research_work  (table t_work)
- type: publication, preprint, talk, poster, project, startup, company...
- title
- url
- summary
- authors
- tags
- note
- id
- ts

## people (who) related 

### organization (table t_org)
- name
- url
- note

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

## process related (how - operational data)

### team_member (table t_person_team)
intersection between t_person and t_team
- id
- ts
- ref_type: t_faculty
- ref_key: url ## name  (delimiter=" ## ")
- ref_type_2
- ref_key_2

### publications (table t_person_work)
intersection between t_person and t_work
- id
- ts
- ref_type: t_faculty | t_person
- ref_key: url ## name  (delimiter=" ## ")
- ref_type_2
- ref_key_2

### notes (table t_note)
intersection between t_person and any other entity
- id
- ts
- title
- url
- note
- tags
- ref_type
- ref_key
