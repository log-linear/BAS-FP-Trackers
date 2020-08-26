/*
    author: vfaner
    date: 2019-08-05
    description: Create initial roster table for BAS/F&P Trackers
*/

-- Store vRoster as a temp table for optimization purposes
DROP TABLE IF EXISTS #vRoster
SELECT * INTO #vRoster FROM ODS_CPS.RPT.vRoster

-- Create Roster Table
DROP TABLE IF EXISTS ODS_CPS.DAT.bas_fp_roster_20_21
CREATE TABLE ODS_CPS.DAT.bas_fp_roster_20_21(
    StudentID               FLOAT
    ,StudentName            VARCHAR(MAX)
    ,GradeLevel             INT
    ,SchoolNameAbbreviated  VARCHAR(MAX)
    ,initial_roster         INT  -- indicator marking initial rosters, used in case
                                 -- a tracker needs to be rebuilt/debugged later on
    ,row_id                 INT
)

INSERT INTO ODS_CPS.DAT.bas_fp_roster_20_21
SELECT DISTINCT
    StudentID
    ,StudentName
    ,GradeLevel

    -- Normalize Lee/Delmas
    ,CASE
        WHEN SchoolNameAbbreviated LIKE '%Lee%' THEN 'Uplift Delmas Morton PS'
        WHEN SchoolNameAbbreviated LIKE '%Delmas%' THEN 'Uplift Delmas Morton PS'
        ELSE SchoolNameAbbreviated
    END AS SchoolNameAbbreviated
    ,1 AS initial_roster

    ,ROW_NUMBER() OVER(
        ORDER BY
            StudentID
            ,StudentName
            ,GradeLevel
            ,CASE
                WHEN SchoolNameAbbreviated LIKE '%Lee%' THEN 'Uplift Delmas Morton PS'
                WHEN SchoolNameAbbreviated LIKE '%Delmas%' THEN 'Uplift Delmas Morton PS'
                ELSE SchoolNameAbbreviated
            END
    ) AS row_id

FROM #vRoster

WHERE
    GETDATE() BETWEEN StudentEnrollDate AND StudentExitDate
    AND GETDATE() BETWEEN SchoolEntryDate AND SchoolExitDate
    AND GETDATE() BETWEEN SectionStartDate AND SectionEndDate
    AND GradeLevel BETWEEN 0 AND 5

