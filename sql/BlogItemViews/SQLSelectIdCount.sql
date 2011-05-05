<params>since=None</params>

SELECT
 blogitemid,
 COUNT(blogitemid) AS count
 
FROM
 blogitemviews
 
<dtml-unless "since==_.None or since =='None'">
WHERE
 visit_date >= <dtml-sqlvar since type="string">
</dtml-unless> 
 
GROUP BY
 blogitemid
 
ORDER BY
 count DESC
