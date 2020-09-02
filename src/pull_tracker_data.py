#!/usr/bin/env python3
"""
author:        Victor Faner
date:          2019-08-12
description:   Pull data from Trackers into a single table to then be
               loaded into SQL Server.
"""
import pandas as pd
import numpy as np
import pygsheets
from sqlalchemy import create_engine, types


def main():
    client = pygsheets.authorize(
        '../client_secret_306687575540-dgtvvmcmk3flnvig5mt1j7gk21s5087c.apps.googleusercontent.com.json'
    )
    engine = create_engine(
        r'mssql+pyodbc://TLXSQLPROD-01/ODS_CPS?driver=ODBC+Driver+13+for+SQL+Server',
        fast_executemany=True  # Faster loads - for SQLAlchemy 1.3+ ONLY
    )
    campuses = [
        'North Hills PS',
        'Peak PS',
        'Ascend PS',
        'Elevate PS',
        'Gradus PS',
        'Grand PS',
        'Hampton PS',
        'Heights PS',
        'Infinity PS',
        'Luna PS',
        'Meridian PS',
        'Mighty PS',
        'Pinnacle PS',
        'Triumph PS',
        'White Rock Hills PS',
        'Williams PS',
        'Wisdom PS',
        'Uplift Delmas Morton PS',
        'Summit PS'
    ]
    dtypes = {
		'Status'		 : types.VARCHAR(),
        'August Formal'  : types.VARCHAR(3),
        '9-Sep'          : types.VARCHAR(3),
        '23-Sep'         : types.VARCHAR(3),
        '7-Oct'          : types.VARCHAR(3),
        '21-Oct'         : types.VARCHAR(3),
        '4-Nov'          : types.VARCHAR(3),
        '18-Nov'         : types.VARCHAR(3),
        'December Formal': types.VARCHAR(3),
        '3-Feb'          : types.VARCHAR(3),
        '17-Feb'         : types.VARCHAR(3),
        '2-Mar'          : types.VARCHAR(3),
        '16-Mar'         : types.VARCHAR(3),
        '30-Mar'         : types.VARCHAR(3),
        '13-Apr'         : types.VARCHAR(3),
        '27-Apr'         : types.VARCHAR(3),
        'May Formal'     : types.VARCHAR(3),
    }

    # Get data from each campus tracker as a list of dataframes
    dfs = []
    for campus in campuses:
        tracker = client.open(f'{campus} 20-21 BAS/F&P Tracker')

        # Loop through each Grade level sheet
        for grade_sheet in tracker.worksheets():
            if grade_sheet.title in ['Kinder', '1st', '2nd', '3rd', '4th', '5th']:
                df = grade_sheet.get_as_df(start='A2', end='U2002',
                                           include_tailing_empty=True)
                df['Campus'] = campus
                df['Grade Level'] = grade_sheet.title

                df = df[
                    'Teacher',
                    'Scholar',
                    'Status',
                    'August Formal',
                    '9-Sep',
                    '23-Sep',
                    '7-Oct',
                    '21-Oct',
                    '4-Nov',
                    '18-Nov',
                    'December Formal',
                    '3-Feb',
                    '17-Feb',
                    '2-Mar',
                    '16-Mar',
                    '30-Mar',
                    '13-Apr',
                    '27-Apr',
                    'May Formal'
                ]

                dfs.append(df)

    master_df = (
        pd.concat(dfs, sort=False).astype(str)

            .replace(r'|'  # Handle NaN/None/NULL values
                     r'nan|'
                     r'None|'
                     r'#N/A|'
                     r'#REF!\W|'
                     r'#REF!\W +|'
                     r', +', np.nan)
            .dropna(  # Remove rows with no data
                how='all',
                subset=[
                    'Teacher',
                    'Scholar',
                    'Status',
                    'August Formal',
                    '9-Sep',
                    '23-Sep',
                    '7-Oct',
                    '21-Oct',
                    '4-Nov',
                    '18-Nov',
                    'December Formal',
                    '3-Feb',
                    '17-Feb',
                    '2-Mar',
                    '16-Mar',
                    '30-Mar',
                    '13-Apr',
                    '27-Apr',
                    'May Formal'
                ]
        )
    )
    
    master_df.to_sql('bas_fp_tracker_data_20_21', con=engine, schema='DAT',

                     if_exists='replace', index=False, dtype=dtypes)


if __name__ == '__main__':
    main()
