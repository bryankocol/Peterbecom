<params>searchterm</params>


SELECT 
 index, check_date
 

FROM
 google_result_index

WHERE 
 searchterm ILIKE <dtml-sqlvar searchterm type="string"> 

ORDER BY check_date DESC

