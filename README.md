# CS Faculty Info

**Important Note**: <br>
In order to perserve your data, you should backup your local duckdb file before upgrading to the latest code.

## Get started
### Setup for Windows 

#### Install Anaconda python 
follow tutorial at https://www.datacamp.com/tutorial/installing-anaconda-windows

#### Download cs-faculty 
visit https://github.com/wgong/cs-faculty

#### (Optional) create virtual python env called cs and activate it
```
python -m venv cs 
cs\Scripts\activate 
```

#### Install dependent python packages 
```
pip install -r requirements.txt 
```

#### Launch streamlit app
```
cd app
streamlit run app.py
```
open browser at http://localhost:8501/

**Note**: <br>
Commands may differ for other OS, but the logical sequence remains the same.


### Setup from GitHub source
```
$ git clone git@github.com:wgong/cs-faculty.git
$ cd cs-faculty
$ pip install -r requirements.txt
$ cd app
$ streamlit run app.py
open browser at http://localhost:8501/
```

## Screenshots

- List of Faculties
![Faculties](https://github.com/wgong/cs-faculty/blob/main/docs/Screenshots/1-faculty-1_work.jpg "Faculties")
- Edit Work
![Faculties](https://github.com/wgong/cs-faculty/blob/main/docs/Screenshots/1-faculty-1_work-edit.jpg "Work")
- [... More screenshots are here](https://github.com/wgong/cs-faculty/tree/main/docs/Screenshots)

## Configuration

- If you rename DuckDB file, ensure to change `FILE_DB` variable in `config.py` accordingly

## Release Notes

- [2023-05-06]
    - added setup instruction

- [2023-05-03]
    - added `award` column to 2 tables: g_person, g_work
    - if you have added data to `db/cs-faculty-20230429.duckdb`, please run `patch_db_20230503.py` which will alter those 2 tables by adding the `award` column

- [2023-04-29] 
    - first working version released

## Credits

- This app is powered by the awesome `streamlit` framework. Thank you, the [Streamlit](https://streamlit.io/) creators and [community](https://streamlit.io/community) !
- This app uses the awesome `streamlit-aggrid` to display tabular data. Thank you, [Pablo Fonseca](https://github.com/PablocFonseca/streamlit-aggrid) !
