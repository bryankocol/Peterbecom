<params>date</params>

SELECT
 *
 
FROM
 mp3records
 
WHERE
 add_date >= <dtml-sqlvar date type="string">
 
ORDER BY
 add_date DESC
