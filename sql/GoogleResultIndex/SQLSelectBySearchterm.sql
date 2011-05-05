<params>searchterm</params>

SELECT
 *
 
FROM 
 google_result_index
 
WHERE
 searchterm ILIKE <dtml-sqlvar searchterm type="string">