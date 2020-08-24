:: Set conda env - Remove these lines before running if you have a system python 
:: installation  with the necessary libraries
call C:\Users\vfaner\AppData\Local\Continuum\miniconda3\Scripts\activate.bat 
call conda activate bas_fp_19_20

:: Update SQL master roster
cd /d "S:\Student Data\Analysts\Projects\2020-2021 F&P BAS Tracker"
sqlcmd -S sql-cl-dw-pro\datawarehouse -E -i queries\update_bas_fp_rosters.sql 

:: Update tracker rosters and pull SQL master tracker data
cd src
python update_rosters.py
python pull_tracker_data.py