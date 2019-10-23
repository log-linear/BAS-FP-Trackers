:: Update SQL master roster
call venv\Scripts\activate.bat
sqlcmd -S TLXSQLPROD-01 -E -i queries\update_bas_fp_rosters.sql 

:: Update tracker rosters and pull SQL master tracker data
cd src
python update_rosters.py
python pull_tracker_data.py