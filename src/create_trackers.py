import pandas as pd
import pygsheets


def main():
    grade_dict = {'0': 'Kinder',
                  '1': '1st',
                  '2': '2nd',
                  '3': '3rd',
                  '4': '4th',
                  '5': '5th',}
    folder_id = '1wGf1rNKjFpdw9wFJbOlV-U0byotCP5AU'  # BAS/FP GDrive folder id
    template_id = '18XIK6-_xs0LEGaFZ1kGU-bsNXQwJ9WPNwKAyTHO19yY'
    client = pygsheets.authorize(
        '../client_secret_507650277646-89evt7ufgfmlrfci4043cthvlgi3jf0s.apps.googleusercontent.com.json'
    )

    rosters = pd.read_csv('../data/initial_rosters_20190806.csv', dtype=str)
    rosters = rosters.replace(grade_dict)
    campuses = rosters['SchoolNameAbbreviated'].unique()

    # Create campus trackers
    for campus in campuses:
        grade_levels = rosters.query(
            f'SchoolNameAbbreviated == "{campus}"'
        )['GradeLevel'].unique()

        tracker_name = f'{campus} 19-20 BAS/F&P Tracker'
        client.drive.copy_file(template_id, tracker_name, folder_id)
        tracker = client.open(tracker_name)

        # Fill in sheets for each grade level
        for grade_level in grade_levels:
            current_roster = rosters.query(
                    f'SchoolNameAbbreviated == "{campus}" '
                    f'& `GradeLevel` == "{grade_level}"'
                ).iloc[:, :4]

            grade_sheet = tracker.worksheet_by_title(grade_level)
            grade_sheet.set_dataframe(current_roster, start='A3',
                                      copy_head=False)


if __name__ == '__main__':
    main()
