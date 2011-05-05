<params>since=None
direction="DESC"</params>

SELECT *

FROM
 photoviews
 
<dtml-unless "since==_.None or since =='None'">
WHERE
 time_stamp >= <dtml-sqlvar since type="string">
</dtml-unless>

ORDER BY
 time_stamp <dtml-var direction>
