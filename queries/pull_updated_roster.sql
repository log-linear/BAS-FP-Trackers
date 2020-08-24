/*
    author: vfaner
    description: Pull bas_fp_roster_19_20_STAGING table for Tracker updates
*/

SELECT DISTINCT 
    TeacherNumber
    ,TeacherName
    ,StudentID
    ,StudentName
    ,GradeLevel
    ,CASE
        WHEN SchoolNameAbbreviated LIKE '%Lee%' THEN 'Uplift Delmas Morton PS'
        WHEN SchoolNameAbbreviated LIKE '%Delmas%' THEN 'Uplift Delmas Morton PS'
        ELSE SchoolNameAbbreviated
    END AS SchoolNameAbbreviated
    ,TeacherEmail

FROM ODS_CPS.DAT.bas_fp_roster_20_21

ORDER BY 
    TeacherNumber
    ,StudentID
