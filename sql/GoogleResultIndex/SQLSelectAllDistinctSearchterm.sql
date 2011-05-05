<params>limit
offset</params>



SELECT 
 searchterm, index, check_date
 

FROM
 google_result_index

WHERE 
 searchterm IN 
 (SELECT DISTINCT searchterm 
  FROM google_result_index)
 

ORDER BY searchterm, check_date DESC

LIMIT <dtml-sqlvar limit type="int">
OFFSET <dtml-sqlvar offset type="int">

