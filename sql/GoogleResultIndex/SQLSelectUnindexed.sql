<params>limit</params>


SELECT searchterm, random() AS score

FROM (
  SELECT
    searchterm,
    TRIM(BOTH ' ' FROM UPPER(searchterm)) AS searchterm_u
  FROM
    searchreferers
    
  EXCEPT
  
    SELECT 
      searchterm,
      TRIM(BOTH ' ' FROM UPPER(searchterm)) AS searchterm_u
    FROM
      google_result_index
      
  ) AS uniques

ORDER BY score

LIMIT <dtml-sqlvar limit type="int">;