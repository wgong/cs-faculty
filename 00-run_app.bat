rem Step 0: Install Anaconda python 
rem ============================================================
rem follow tutorial at https://www.datacamp.com/tutorial/installing-anaconda-windows

rem Step 1: Download cs-faculty 
rem ============================================================
rem visit https://github.com/wgong/cs-faculty

rem Step 1: create virtual python env called cs and activate it
rem ============================================================
rem python -m venv cs 
rem cs\Scripts\activate 

rem Step 2: install dependent packages 
rem ============================================================
rem pip install -r requirements.txt 

rem Step 3: launch app
rem ============================================================
cd app
streamlit run app.py