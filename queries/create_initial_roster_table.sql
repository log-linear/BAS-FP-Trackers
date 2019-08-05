/*
    @author: vfaner
    @date: 2019-08-05
    @description: Create initial roster table for BAS/F&P Trackers
*/

IF OBJECT_ID('ODS_CPS.DAT.bas_fp_roster_19_20') IS NOT NULL DROP TABLE ODS_CPS.DAT.bas_fp_roster_19_20

SELECT DISTINCT
    TeacherNumber
    ,TeacherName
    ,StudentID
    ,StudentName
    ,GradeLevel
    ,SchoolNameAbbreviated
    ,TeacherEmail

INTO ODS_CPS.DAT.bas_fp_roster_19_20

FROM ODS_CPS.RPT.vRosterCurrent

WHERE GradeLevel BETWEEN 0 AND 5

ORDER BY 
    SchoolNameAbbreviated
    ,GradeLevel
    ,TeacherName
    ,StudentName