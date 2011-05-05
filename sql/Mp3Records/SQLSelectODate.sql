<params>direction="DESC"
start
size</params>

SELECT *

FROM mp3records

ORDER BY
 add_date <dtml-var direction>
 
<dtml-if "size!=_.None">
 LIMIT <dtml-var size>
</dtml-if>

<dtml-if "start!=_.None">
 OFFSET <dtml-var start>
</dtml-if>

