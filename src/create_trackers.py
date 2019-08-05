import pandas as pd
import pygsheets


def create_tracker(client, tracker_name, template, grade_levels):
    client.create(title=tracker_name,
                  folder=folder_id)
    tracker = client.open(tracker_name)

    # Copy sheets from template into each tracker
    for sheet in template.worksheets():
        if sheet.title in grade_levels:
            tracker.add_worksheet(title=sheet.title,
                                  rows=sheet.rows,
                                  cols=sheet.cols,
                                  src_tuple=(template.id, sheet.id))

    tracker.del_worksheet(tracker.worksheet_by_title('Sheet1'))

    return tracker


def populate_grade_sheet(tracker, current_roster, grade_level):
    grade_sheet = tracker.worksheet_by_title(grade_level)
    grade_sheet.set_dataframe(current_roster, start='A3', copy_head=False)

    # Prevent editing column headers/rosters
    grade_sheet.create_protected_range(start='A1', end='Z2')
    grade_sheet.create_protected_range(start='A1', end='E2002')


if __name__ == '__main__':
    client = pygsheets.authorize(
        'client_secret_507650277646-89evt7ufgfmlrfci4043cthvlgi3jf0s.apps.googleusercontent.com.json'
    )
    template = client.open('tracker_template')
    grade_dict = {
        '0': 'Kinder',
        '1': '1st',
        '2': '2nd',
        '3': '3rd',
        '4': '4th',
        '5': '5th',
    }
    folder_id = '1wGf1rNKjFpdw9wFJbOlV-U0byotCP5AU'  # BAS/FP GDrive folder id

    rosters = pd.read_csv('./data/initial_rosters_20190805.csv', dtype=str)
    rosters = rosters.replace(grade_dict)
    campuses = rosters['SchoolNameAbbreviated'].unique()

    for campus in campuses:
        grade_levels = rosters.query(
            f'SchoolNameAbbreviated == "{campus}"'
        )['GradeLevel'].unique()

        tracker_name = f'{campus} 19-20 BAS/F&P Tracker'
        tracker = create_tracker(client, tracker_name, template, grade_levels)

        # Fill in sheets for each grade level
        for grade_level in grade_levels:
            current_roster = rosters.query(
                    f'SchoolNameAbbreviated == "{campus}" '
                    f'& `GradeLevel` == "{grade_level}"'
                ).iloc[:, :4]
            teachers = current_roster[
                    ['TeacherNumber', 'TeacherName']
                ].drop_duplicates()
            teachers['GradeLevel'] = grade_level
            teacher_counts = teachers['TeacherNumber'].value_counts()

            populate_grade_sheet(tracker, current_roster,
                                 grade_level)
