rem Step 0: 
rem     Install Anaconda python 
rem ============================================================
rem follow tutorial at https://www.datacamp.com/tutorial/installing-anaconda-windows

rem Step 1: 
rem     Download cs-faculty 
rem ============================================================
rem visit https://github.com/wgong/cs-faculty

rem Step 2: (Optional)
rem     create virtual python env called cs and activate it
rem ============================================================

rem python -m venv cs 
rem cs\Scripts\activate 

rem Step 3: 
rem     Install dependent python packages 
rem ============================================================

rem pip install -r requirements.txt 

rem Step 3: 
rem     Launch streamlit app
rem ============================================================

cd app
streamlit run app.py