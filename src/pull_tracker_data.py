from pathlib import Path
import logging

import pandas as pd
import numpy as np
import pygsheets
from sqlalchemy import create_engine


def main():
    (Path.cwd() / '../logs').mkdir(exist_ok=True)
    logging.basicConfig(filename='../logs/tracker_data_pulls.log',
                        level=logging.INFO,
                        format='%(asctime)s: %(message)s')
    folder_id = '1wGf1rNKjFpdw9wFJbOlV-U0byotCP5AU'  # BAS/FP GDrive folder id
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
                'Williams PS', 'Wisdom PS']

    dfs = []
    for campus in campuses:
        tracker = client.open(f'{campus} 19-20 BAS/F&P Tracker')

        for grade_sheet in tracker.worksheets():
            if grade_sheet.title not in ['Instructions', 'Data Validation']:
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
                     if_exists='replace', index=False)


if __name__ == '__main__':
    main()
