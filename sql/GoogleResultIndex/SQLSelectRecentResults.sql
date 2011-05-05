<params>limit</params>

SELECT
 *
FROM
 google_result_index
 
ORDER BY
 check_date DESC
 
LIMIT <dtml-sqlvar limit type="int">