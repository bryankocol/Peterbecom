<params>limit</params>

SELECT
 searchterm,
 count(searchterm) AS count
 
FROM
 searchreferers
 
GROUP BY
 searchterm
 
ORDER BY
 count DESC
 
LIMIT <dtml-sqlvar limit type="int">;