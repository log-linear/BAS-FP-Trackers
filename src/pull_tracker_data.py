#!/usr/bin/env python3
"""
@author:        Victor Faner
@date:          2019-08-12
@description:   Pull data from Trackers into a single table to then be
                loaded into SQL Server.
"""
from pathlib import Path
import logging

import pandas as pd
import numpy as np
import pygsheets
from sqlalchemy import create_engine, types


def main():
    (Path.cwd() / '../logs').mkdir(exist_ok=True)
    logging.basicConfig(filename='../logs/tracker_data_pulls.log',
                        level=logging.INFO,
                        format='%(asctime)s: %(message)s')
    client = pygsheets.authorize(
        '../client_secret_507650277646-89evt7ufgfmlrfci4043cthvlgi3jf0s.apps.googleusercontent.com.json'
    )
    engine = create_engine(
        r'mssql+pyodbc://sql-cl-dw-pro\datawarehouse/ODS_CPS?driver=SQL+Server'
    )
    campuses = ['North Hills PS', 'Peak PS', 'Ascend PS', 'Elevate PS',
                'Gradus PS', 'Grand PS', 'Hampton PS', 'Heights PS',
                'Infinity PS', 'Luna PS', 'Meridian PS', 'Mighty PS',
                'Pinnacle PS', 'Summit PS', 'Triumph PS', 'White Rock Hills PS',
                'Williams PS', 'Wisdom PS', 'Uplift Lee PS']
    dtypes = {
		'Status'		  : types.VARCHAR(),
        'August Formal'   : types.VARCHAR(3),
        '9-Sep'           : types.VARCHAR(3),
        '23-Sep'          : types.VARCHAR(3),
        '7-Oct'           : types.VARCHAR(3),
        '21-Oct'          : types.VARCHAR(3),
        '4-Nov'           : types.VARCHAR(3),
        '18-Nov'          : types.VARCHAR(3),
        'December Formal' : types.VARCHAR(3),
        '3-Feb'           : types.VARCHAR(3),
        '17-Feb'          : types.VARCHAR(3),
        '2-Mar'           : types.VARCHAR(3),
        '16-Mar'          : types.VARCHAR(3),
        '30-Mar'          : types.VARCHAR(3),
        '13-Apr'          : types.VARCHAR(3),
        '27-Apr'          : types.VARCHAR(3),
        'May Formal'      : types.VARCHAR(3),
    }

    dfs = []
    for campus in campuses:
        tracker = client.open(f'{campus} 19-20 BAS/F&P Tracker')

        for grade_sheet in tracker.worksheets():
            if grade_sheet.title not in ['Instructions', 'Data Validation',
                                         'Roster Validation']:
                df = grade_sheet.get_as_df(start='A2', end='U2002',
                                           include_tailing_empty=True)
                df['Campus'] = campus
                df['Grade Level'] = grade_sheet.title
                dfs.append(df)

    master_df = (
        pd.concat(dfs, sort=False).astype(str)
            .replace('', np.nan)
            .replace('nan', np.nan)
    )
    
    master_df.to_sql('bas_fp_tracker_data_19_20', con=engine, schema='DAT',
                     if_exists='replace', index=False, dtype=dtypes)


if __name__ == '__main__':
    main()
