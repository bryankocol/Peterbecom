<params>title
artist</params>

SELECT * 

FROM
 mp3records
 
WHERE
 UPPER(title) LIKE UPPER(<dtml-sqlvar title type="string">)
 AND
 UPPER(artist) LIKE UPPER(<dtml-sqlvar artist type="string">)
