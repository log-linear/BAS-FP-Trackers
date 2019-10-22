#!/usr/bin/env python3
"""
@author:        Victor Faner
@date:          2019-08-12
@description:   Automatically update Trackers with most recent rosters
                from vRoster.
"""
from pathlib import Path
import logging

import numpy as np
import pandas as pd
import pygsheets
from sqlalchemy import create_engine


def main():
    (Path.cwd() / '../logs').mkdir(exist_ok=True)
    logging.basicConfig(filename='../logs/roster_updates.log',
                        level=logging.INFO,
                        format='%(asctime)s: %(message)s')
    grade_dict = {'0': 'Kinder',
                  '1': '1st',
                  '2': '2nd',
                  '3': '3rd',
                  '4': '4th',
                  '5': '5th'}
    client = pygsheets.authorize(
        '../client_secret_507650277646-89evt7ufgfmlrfci4043cthvlgi3jf0s.apps.googleusercontent.com.json'
    )
    engine = create_engine(
        r'mssql+pyodbc://TLXSQLPROD-01/ODS_CPS_STAGING?driver=SQL+Server'
    )

    with open('../queries/pull_updated_roster.sql', 'r') as fp:
        sql = fp.read()

    rosters = pd.read_sql(sql, engine).astype(str)
    rosters = rosters.replace(grade_dict)
    campuses = rosters['SchoolNameAbbreviated'].unique()
    
    # Create campus trackers
    for campus in campuses:
        tracker_name = f'{campus} 19-20 BAS/F&P Tracker'
        tracker = client.open(tracker_name)

        roster_validation = tracker.worksheet_by_title('Roster Validation')

        updated_roster = (
            rosters.query(
                f'SchoolNameAbbreviated == "{campus}" '
            )
            .iloc[:, :4]
            .rename(columns={'TeacherNumber': 'Employee ID',
                             'TeacherName': 'Teacher Name',
                             'StudentName': 'Scholar Name'})
            .sort_values(by=['Employee ID', 'StudentID'])
        )
         
        teachers = updated_roster[['Employee ID', 'Teacher Name']].drop_duplicates()
        scholars = updated_roster[['StudentID', 'Scholar Name']].drop_duplicates()
        
        roster_validation.set_dataframe(teachers, start='A2',
                                        copy_head=True, nan='')
        roster_validation.set_dataframe(scholars, start='C2',
                                        copy_head=True, nan='')
                                        
        logging.info(f'{len(updated_roster)} new records loaded to {tracker_name}')


if __name__ == '__main__':
    main()
