#!/usr/bin/env python3
"""
author:        Victor Faner
date:          2019-08-12
description:   Automatically update Trackers with most recent rosters
               from vRoster.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import pygsheets
from sqlalchemy import create_engine


def main():
    client = pygsheets.authorize(
        '../client_secret_306687575540-dgtvvmcmk3flnvig5mt1j7gk21s5087c.apps.googleusercontent.com.json'
    )

    # Read rosters from SQL
    engine = create_engine(
        r'mssql+pyodbc://TLXSQLPROD-01/ODS_CPS?driver=ODBC+Driver+13+for+SQL+Server',
        fast_executemany=True  # Faster loads - for SQLAlchemy 1.3+ ONLY
    )
    rosters = pd.read_sql(
        'SELECT * FROM ODS_CPS.DAT.bas_fp_roster_20_21',
        con=engine
    )

    # Loop through and update each tracker
    campuses = rosters['SchoolNameAbbreviated'].unique()

    for campus in campuses:
        current_roster = rosters[rosters['SchoolNameAbbreviated'] == campus]

        # Separate scholars and teachers into separate dataframes
        scholars = current_roster[current_roster['is_scholar'] == 1].iloc[:, [0]]
        teachers = current_roster[current_roster['is_scholar'] == 0].iloc[:, [0]]

        # Open tracker
        tracker_name = f'{campus} 20-21 BAS/F&P Tracker'
        tracker = client.open(tracker_name)

        # Fill in Data Validation fields
        data_validation = tracker.worksheet_by_title('Data Validation')
        data_validation.set_dataframe(teachers, start='C2', copy_head=False,
                                      extend=True, nan='')
        data_validation.set_dataframe(scholars, start='D2', copy_head=False,
                                      extend=True, nan='',)


if __name__ == '__main__':
    main()

