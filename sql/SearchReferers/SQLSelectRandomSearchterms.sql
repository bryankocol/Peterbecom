<params>limit</params>

SELECT
 id, 
 site,
 searchterm,
 add_date,
 random() AS score
 
FROM 
 searchreferers
 
ORDER BY 
 score DESC
 
LIMIT <dtml-sqlvar limit type="int">