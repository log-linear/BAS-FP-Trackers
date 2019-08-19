/*
    @author: vfaner
    @description: Pull bas_fp_roster_19_20_STAGING table for Tracker updates
*/

SELECT DISTINCT *

FROM ODS_CPS.DAT.bas_fp_roster_19_20

ORDER BY 
    TeacherNumber
    ,StudentID
