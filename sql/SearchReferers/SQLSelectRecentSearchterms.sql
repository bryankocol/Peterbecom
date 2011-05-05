<params>limit
since=None</params>

SELECT
 *
 
FROM 
 searchreferers
 
<dtml-unless "since==_.None or since =='None'">
WHERE
 add_date >= <dtml-sqlvar since type="string">
</dtml-unless>

ORDER BY 
 add_date DESC
 
LIMIT <dtml-sqlvar limit type="int">