#!/usr/bin/env python3
"""
@author:        Victor Faner
@date:          2019-08-12
@description:   Rebuild initial rosters in SQL Server. Useful when the
                tracker needs to be modified.
"""
import pandas as pd
from sqlalchemy import create_engine, types


def main():
    engine = create_engine(
        r'mssql+pyodbc://sql-cl-dw-pro\datawarehouse/ODS_CPS?driver=SQL+Server'
    )
    dtypes = {
        'TeacherNumber': types.VARCHAR(30),
        'TeacherName': types.VARCHAR(102),
        'StudentID': types.FLOAT,
        'StudentName': types.VARCHAR(135),
        'GradeLevel': types.BIGINT,
        'SchoolNameAbbreviated': types.VARCHAR(100),
        'TeacherEmail': types.VARCHAR(360),
    }
    rosters = pd.read_csv('../data/initial_rosters_20190806.csv', dtype=str)
    rosters.to_sql('bas_fp_roster_19_20', con=engine, schema='DAT',
                   if_exists='replace', index=False, dtype=dtypes, )


if __name__ == '__main__':
    rebuild = input('Rebuild Rosters? Y/N ')
    if rebuild == 'Y':
        main()
    else:
        exit(0)
