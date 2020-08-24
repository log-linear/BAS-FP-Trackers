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


def main():
    grade_dict = {'0': 'Kinder',
                  '1': '1st',
                  '2': '2nd',
                  '3': '3rd',
                  '4': '4th',
                  '5': '5th',}

    # GDrive IDs
    folder_id = '1wGf1rNKjFpdw9wFJbOlV-U0byotCP5AU'  # Where trackers will be housed
    template_id = '1PDw7GFP1jc_P-_crqD8efcZXQSr6c-VgPXx3dGEcXJU'  # template file
    client = pygsheets.authorize(
        '../client_secret_507650277646-89evt7ufgfmlrfci4043cthvlgi3jf0s.apps.googleusercontent.com.json'
    )

    rosters = pd.read_csv('../data/initial_rosters_20190806.csv', dtype=str)
    rosters = rosters.replace(grade_dict)
    campuses = rosters['SchoolNameAbbreviated'].unique()

    # Create campus trackers
    for campus in campuses:
        current_roster = rosters.query(
            f'SchoolNameAbbreviated == "{campus}" '
        ).iloc[:, :4]

        tracker_name = f'{campus} 20-21 BAS/F&P Tracker'
        client.drive.copy_file(template_id, tracker_name, folder_id)
        tracker = client.open(tracker_name)
        roster_validation = tracker.worksheet_by_title('Roster Validation')
        roster_validation.set_dataframe(current_roster, start='A2',
                                        copy_head=False, nan='')


if __name__ == '__main__':
    main()
