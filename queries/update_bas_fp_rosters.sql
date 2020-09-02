/*
    author: vfaner
    date: 2019-08-05
    description: Stored proc for updating BAS/F&P production roster table. Used
                 e.g. when a scholar changes schools or joins the network
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

--------------------------------------------------------------------------------
--  Pull current rosters
--------------------------------------------------------------------------------

DROP TABLE IF EXISTS #roster_current
SELECT DISTINCT
    CAST(CAST(StudentID AS INT) AS VARCHAR) + ' | ' + StudentName AS person_id

    -- Normalize Lee/Delmas
    ,CASE
        WHEN SchoolNameAbbreviated LIKE '%Lee%' THEN 'Uplift Delmas Morton PS'
        WHEN SchoolNameAbbreviated LIKE '%Delmas%' THEN 'Uplift Delmas Morton PS'
        ELSE SchoolNameAbbreviated
    END AS SchoolNameAbbreviated

    ,1 AS is_scholar
    ,0 AS initial_roster

INTO #roster_current

FROM #vRoster

WHERE
    GETDATE() BETWEEN StudentEnrollDate AND StudentExitDate
    AND GETDATE() BETWEEN SchoolEntryDate AND SchoolExitDate
    AND GETDATE() BETWEEN SectionStartDate AND SectionEndDate
    AND GradeLevel BETWEEN 0 AND 5

UNION

-- Teachers
SELECT DISTINCT
    CAST(TeacherNumber AS VARCHAR) + ' | ' + TeacherName AS person_id

    -- Normalize Lee/Delmas
    ,CASE
        WHEN SchoolNameAbbreviated LIKE '%Lee%' THEN 'Uplift Delmas Morton PS'
        WHEN SchoolNameAbbreviated LIKE '%Delmas%' THEN 'Uplift Delmas Morton PS'
        ELSE SchoolNameAbbreviated
    END AS SchoolNameAbbreviated

    ,0 AS is_scholar
    ,0 AS initial_roster

FROM #vRoster

WHERE
    GETDATE() BETWEEN StudentEnrollDate AND StudentExitDate
    AND GETDATE() BETWEEN SchoolEntryDate AND SchoolExitDate
    AND GETDATE() BETWEEN SectionStartDate AND SectionEndDate
    AND GradeLevel BETWEEN 0 AND 5

--------------------------------------------------------------------------------
--  Find unmatched rows and add to staging roster temp table
--------------------------------------------------------------------------------
DROP TABLE IF EXISTS #new_rosters
SELECT
    #roster_current.*

INTO #new_rosters

FROM #roster_current
    
    LEFT JOIN ODS_CPS.DAT.bas_fp_roster_20_21 AS basfp
        ON ISNULL(#roster_current.person_id, 0)               = ISNULL(basfp.person_id, 0)
        AND ISNULL(#roster_current.SchoolNameAbbreviated, '') = ISNULL(basfp.SchoolNameAbbreviated, '')

WHERE
    basfp.person_id                 IS NULL
    AND basfp.SchoolNameAbbreviated IS NULL

--------------------------------------------------------------------------------
--  Add unmatched rows to production table
--------------------------------------------------------------------------------
INSERT INTO ODS_CPS.DAT.bas_fp_roster_20_21

SELECT *

FROM #new_rosters
