<params>urls
limit</params>

SELECT 
 x.combined, 
 COUNT(x.combined) AS count
 
FROM 
 (SELECT
    REPLACE(
     REPLACE(domain||'?'||querystring,'&ie=UTF-8&oe=UTF-8',''),
     '&btnG=Google+Search','') AS combined
  FROM referers WHERE querystring <> ''
  AND (1=0
       <dtml-in urls>
         OR url ILIKE <dtml-sqlvar sequence-item type="string">
       </dtml-in>)
 UNION
  SELECT 
    domain AS combined
  FROM referers WHERE querystring = ''
  AND (1=0
       <dtml-in urls>
         OR url ILIKE <dtml-sqlvar sequence-item type="string">
       </dtml-in>)
 ) AS x
 
 GROUP BY x.combined 
 ORDER BY count DESC
 
 LIMIT <dtml-sqlvar limit type="int">
 