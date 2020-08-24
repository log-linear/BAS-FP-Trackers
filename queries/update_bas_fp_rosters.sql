/*
    author: vfaner
    date: 2019-08-05
    description: Stored proc for updating BAS/F&P production roster table
*/

--------------------------------------------------------------------------------
--  Pull current rosters
--------------------------------------------------------------------------------
IF OBJECT_ID('tempdb..#roster') IS NOT NULL DROP TABLE #roster

SELECT DISTINCT
    TeacherNumber
    ,TeacherName
    ,StudentID
    ,StudentName
    ,GradeLevel
    ,SchoolNameAbbreviated
    ,TeacherEmail

INTO #roster

FROM ODS_CPS.RPT.vRosterCurrent

WHERE GradeLevel BETWEEN 0 AND 5

ORDER BY 
    SchoolNameAbbreviated
    ,GradeLevel
    ,TeacherName
    ,StudentName

--------------------------------------------------------------------------------
--  Find unmatched rows and add to staging roster table
--------------------------------------------------------------------------------
DROP TABLE IF EXISTS ODS_CPS_STAGING.DAT.bas_fp_roster_20_21_STAGING
SELECT #roster.*

INTO ODS_CPS_STAGING.DAT.bas_fp_roster_20_21_STAGING

FROM #roster
    
    LEFT JOIN ODS_CPS.DAT.bas_fp_roster_20_21 AS basfp
        ON ISNULL(#roster.TeacherNumber, 0)           = ISNULL(basfp.TeacherNumber, 0)
        AND ISNULL(#roster.TeacherName, '')           = ISNULL(basfp.TeacherName, '')
        AND ISNULL(#roster.StudentID, 0)              = ISNULL(basfp.StudentID, 0)
        AND ISNULL(#roster.StudentName, '')           = ISNULL(basfp.StudentName, '')
        AND ISNULL(#roster.GradeLevel, 0)             = ISNULL(basfp.GradeLevel, 0)
        AND ISNULL(#roster.SchoolNameAbbreviated, '') = ISNULL(basfp.SchoolNameAbbreviated, '')
        AND ISNULL(#roster.TeacherEmail, '')          = ISNULL(basfp.TeacherEmail, '')

WHERE
    basfp.TeacherNumber             IS NULL
    AND basfp.TeacherName           IS NULL
    AND basfp.StudentID             IS NULL
    AND basfp.StudentName           IS NULL
    AND basfp.GradeLevel            IS NULL
    AND basfp.SchoolNameAbbreviated IS NULL
    AND basfp.TeacherEmail          IS NULL

--------------------------------------------------------------------------------
--  Add unmatched rows to production table
--------------------------------------------------------------------------------
INSERT INTO ODS_CPS.DAT.bas_fp_roster_20_21

SELECT *

FROM ODS_CPS_STAGING.DAT.bas_fp_roster_20_21_STAGING
