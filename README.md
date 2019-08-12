# BAS/F&P Tracker - 2019-2020 edition

## High-level Summary
The BAS/F&P Tracker is a tool for K-5 teachers to enter their students' scores
on the BAS/F&P exam throughout the school year. The tool is deployed on Google
Drive, with aggregations available on Tableau.
 
## Automation steps
The tlxvdi-it-01 server has a task scheduled to run the run_scripts.bat file
every day at 5AM. In order, here are the jobs it runs:

1. Update the master roster list in SQL Server per the most recent rosters in
 vRoster (update_bas_fp_rosters.sql)
2. Update the rosters for each tracker (update_rosters.py)
3. Pull current data from the trackers into a single table in SQL Server
(pull_tracker_data.py)

The Tableau extract is set to refresh at 6AM every day.