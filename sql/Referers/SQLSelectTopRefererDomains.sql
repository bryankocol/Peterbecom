<params>limit</params>

SELECT 
 domain, 
 count(domain) AS count
 
FROM
 referers
 
GROUP BY
 domain 
 
ORDER BY
 count DESC
 
LIMIT <dtml-sqlvar limit type="int">;