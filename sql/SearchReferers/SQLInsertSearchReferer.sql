<params>site
searchterm
add_date</params>

INSERT INTO
 searchreferers 
(
site,
searchterm,
add_date
)

VALUES (
<dtml-sqlvar site type="string">,
<dtml-sqlvar searchterm type="string">,
<dtml-sqlvar add_date type="string">
)