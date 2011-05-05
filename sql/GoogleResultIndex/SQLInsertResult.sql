<params>index
searchterm</params>

INSERT INTO
 google_result_index
(
index,
searchterm,
check_date
)

VALUES (
<dtml-sqlvar index type="int">,
<dtml-sqlvar searchterm type="string">,
now()
)