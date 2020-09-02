:: Update SQL master roster
cd /d "S:\Student Data\Analysts\Projects\2020-2021 F&P BAS Tracker"
sqlcmd -S sql-cl-dw-pro\datawarehouse -E -i queries\update_bas_fp_rosters.sql 

:: Update tracker rosters and pull SQL master tracker data
cd src
python update_rosters.py
python pull_tracker_data.py