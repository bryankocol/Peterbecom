<params>start
end</params>

SELECT 
 COUNT(*) AS count

FROM
 searchreferers
 
WHERE 
 add_date >= <dtml-sqlvar start type="string">
 AND
 add_date < <dtml-sqlvar end type="string">