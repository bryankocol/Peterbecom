<params>limit
offset</params>


SELECT *
FROM google_result_index
WHERE index = 1
ORDER BY check_date DESC

LIMIT <dtml-sqlvar limit type="int">
OFFSET <dtml-sqlvar offset type="int">