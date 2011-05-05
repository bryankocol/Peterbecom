<params>start_date
end_date</params>

SELECT
  COUNT(id) AS count, 
  SUM(index) AS sum,  
  SUM(index)::REAL/COUNT(id) AS average
 
FROM
  google_result_index 
  
WHERE 
  index <= 20
  AND
  check_date >= <dtml-sqlvar start_date type="string">
  AND
  check_date < <dtml-sqlvar end_date type="string">
  
  