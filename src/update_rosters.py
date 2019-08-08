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
        r'mssql+pyodbc://sql-cl-dw-pro\datawarehouse/ODS_CPS_STAGING?driver=SQL+Server'
    )

    with open('../queries/pull_staging_roster.sql', 'r') as fp:
        sql = fp.read()

    rosters = pd.read_sql(sql, engine).astype(str)
    rosters = rosters.replace(grade_dict)
    campuses = rosters['SchoolNameAbbreviated'].unique()

    # Create campus trackers
    for campus in campuses:
        grade_levels = rosters.query(
            f'SchoolNameAbbreviated == "{campus}"'
        )['GradeLevel'].unique()

        tracker_name = f'{campus} 19-20 BAS/F&P Tracker'
        tracker = client.open(tracker_name)

        # Fill in sheets for each grade level
        for grade_level in grade_levels:
            grade_sheet = tracker.worksheet_by_title(grade_level)
            old_roster = grade_sheet.get_as_df(start='A2', end='U2002',
                                               include_tailing_empty=True)
            new_records = (
                rosters.query(
                    f'SchoolNameAbbreviated == "{campus}" '
                    f'& `GradeLevel` == "{grade_level}"'
                )
                .iloc[:, :4]
                .rename(columns={'TeacherNumber': 'Employee ID',
                                 'TeacherName': 'Teacher Name',
                                 'StudentName': 'Scholar Name'})
            )

            updated_roster = (
                pd.concat([old_roster, new_records], sort=False)
                    .replace('', np.nan)
                    .replace('nan', np.nan)
            )
            grade_sheet.set_dataframe(updated_roster, start='A3',
                                      copy_head=False, nan='')

            logging.info(f'{len(new_records)} new records loaded to '
                         f'{tracker_name}, grade {grade_level}')


if __name__ == '__main__':
    main()
