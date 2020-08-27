#!/usr/bin/env python3
"""
author:        Victor Faner
date:          2019-08-12
description:   Script to create/populate the initial Trackers from a
               pre-uploaded template. Should only need to run once at
               the beginning of the school year, or if you are testing
               the scripts out.
"""
import pandas as pd
import pygsheets

from sqlalchemy import create_engine


def main():
    # GDrive IDs
    folder_id = '1349q9kxsZAd_LGZ-GuItnAMDYJYTety_'  # Where trackers will be housed
    template_id = '17UIEnwv8-qfQ_37r84o0uDGoOw_Ccpim7fxN4Qbpw00'  # template file
    client = pygsheets.authorize(
        '../client_secret_306687575540-dgtvvmcmk3flnvig5mt1j7gk21s5087c.apps.googleusercontent.com.json'
    )

    # Read rosters from SQL
    engine = create_engine(
        r'mssql+pyodbc://TLXSQLPROD-01/ODS_CPS?driver=ODBC+Driver+13+for+SQL+Server',
        fast_executemany=True  # Faster loads - for SQLAlchemy 1.3+ ONLY
    )
    rosters = pd.read_sql(
        'SELECT * FROM ODS_CPS.DAT.bas_fp_roster_20_21 WHERE initial_roster = 1',
        con=engine
    )

    # Loop through and create trackers for each campus
    campuses = rosters['SchoolNameAbbreviated'].unique()

    for campus in campuses:
        current_roster = rosters[rosters['SchoolNameAbbreviated'] == campus]

        # Separate scholars and teachers into separate dataframes
        scholars = current_roster[current_roster['is_scholar'] == 1].iloc[:, [0]]
        teachers = current_roster[current_roster['is_scholar'] == 0].iloc[:, [0]]

        # Create workbook from template
        tracker_name = f'{campus} 20-21 BAS/F&P Tracker'
        client.drive.copy_file(template_id, tracker_name, folder_id)
        tracker = client.open(tracker_name)

        # Fill in Data Validation fields
        data_validation = tracker.worksheet_by_title('Data Validation')
        data_validation.set_dataframe(teachers, start='C2', copy_head=False,
                                      extend=True, nan='')
        data_validation.set_dataframe(scholars, start='D2', copy_head=False,
                                      extend=True, nan='',)


if __name__ == '__main__':
    main()


