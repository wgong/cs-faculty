table_name, 
col list: [c1, c2, ...]

column properties: 
- stored in user table: t_col_prop
- with UI to configure

c1: {
	is_system_col: T/F,   # read-only, maybe hidden such as id,ts,uid
	is_user_key: T/F,
	is_required: T/F,
	is_visible: T/F,  # appear in form or not
	is_editable: T/F,
	is_clickable: T/F,  # URL link

	form_column: left-n (default, required) | mid-n | right-n  # n sequence, mid/right
	widget_type: text_input (default) | selectbox | checkbox | text_area | ... (see st API docs)
	label_text: "C1", # optional, use _gen_label(col) when unavailable

}


generalize form generation API

_display_grid_form(
	form_name="faculty_note", 
	ref_type="t_faculty", 
	ref_key="")
"""
form_name: view name (All notes or Faculty notes)
ref_type: parent table
ref_key: f-key

ref_type, ref_key are NULL for All notes
"""