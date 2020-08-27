/*
    author: vfaner
    date: 2019-08-05
    description:

    Creates a single table where each row corresponds to either a
    scholar or a teacher, with columns for the grade level and school
    they attend or teach. Decided to make a singular table to avoid
    having separate teacher/scholar rosters.
*/

-- Store vRoster as a temp table for optimization purposes
DROP TABLE IF EXISTS #vRoster
SELECT
    StudentID
    ,StudentName
    ,SchoolNameAbbreviated
    ,TeacherName
    ,GradeLevel
    ,TeacherNumber
    ,SchoolEntryDate
    ,SchoolExitDate
    ,StudentEnrollDate
    ,StudentExitDate
    ,SectionStartDate
    ,SectionEndDate
INTO #vRoster
FROM ODS_CPS.RPT.vRoster
WHERE YearID = 30

SELECT * FROM #vRoster WHERE TeacherName LIKE '%farah, zainab%'
-- Create Roster Table
DROP TABLE IF EXISTS ODS_CPS.DAT.bas_fp_roster_20_21
CREATE TABLE ODS_CPS.DAT.bas_fp_roster_20_21 (
    person_id               VARCHAR(MAX)
    ,SchoolNameAbbreviated  VARCHAR(MAX)
    ,is_scholar             INT
    ,initial_roster         INT  -- indicator marking initial rosters, used in case
                                 -- a tracker needs to be rebuilt/debugged later on
)

INSERT INTO ODS_CPS.DAT.bas_fp_roster_20_21
-- Scholars
SELECT DISTINCT
    CAST(CAST(StudentID AS INT) AS VARCHAR) + ' | ' + StudentName AS person_id

    -- Normalize Lee/Delmas
    ,CASE
        WHEN SchoolNameAbbreviated LIKE '%Lee%' THEN 'Uplift Delmas Morton PS'
        WHEN SchoolNameAbbreviated LIKE '%Delmas%' THEN 'Uplift Delmas Morton PS'
        ELSE SchoolNameAbbreviated
    END AS SchoolNameAbbreviated

    ,1 AS is_scholar
    ,1 AS initial_roster

FROM #vRoster

WHERE
    GETDATE() BETWEEN StudentEnrollDate AND StudentExitDate
    AND GETDATE() BETWEEN SchoolEntryDate AND SchoolExitDate
    AND GETDATE() BETWEEN SectionStartDate AND SectionEndDate
    AND GradeLevel BETWEEN 0 AND 5

UNION

-- Teachers
SELECT DISTINCT
    CAST(CAST(TeacherNumber AS INT) AS VARCHAR) + ' | ' + TeacherName AS person_id

    -- Normalize Lee/Delmas
    ,CASE
        WHEN SchoolNameAbbreviated LIKE '%Lee%' THEN 'Uplift Delmas Morton PS'
        WHEN SchoolNameAbbreviated LIKE '%Delmas%' THEN 'Uplift Delmas Morton PS'
        ELSE SchoolNameAbbreviated
    END AS SchoolNameAbbreviated

    ,0 AS is_scholar
    ,1 AS initial_roster

FROM #vRoster

WHERE
    GETDATE() BETWEEN StudentEnrollDate AND StudentExitDate
    AND GETDATE() BETWEEN SchoolEntryDate AND SchoolExitDate
    AND GETDATE() BETWEEN SectionStartDate AND SectionEndDate
    AND GradeLevel BETWEEN 0 AND 5
