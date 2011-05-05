<params>since=None</params>

SELECT
 COUNT(*) AS count
 

 
FROM
 photoviews
 
<dtml-unless "since==_.None or since =='None'">
WHERE
 time_stamp >= <dtml-sqlvar since type="string">
</dtml-unless> 
