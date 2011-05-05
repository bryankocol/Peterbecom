<params>since=None
direction="DESC"</params>

SELECT *

FROM
 blogitemviews
 
<dtml-unless "since==_.None or since =='None'">
WHERE
 visit_date >= <dtml-sqlvar since type="string">
</dtml-unless>

ORDER BY
 visit_date <dtml-var direction>
