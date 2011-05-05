<params>domain
querystring
url
http_user_agent
add_date</params>

INSERT INTO
 referers (
domain,
querystring,
url,
http_user_agent,
add_date
)

VALUES (
<dtml-sqlvar domain type="string">,
<dtml-sqlvar querystring type="string">,
<dtml-sqlvar url type="string">,
<dtml-sqlvar http_user_agent type="string">,
<dtml-sqlvar add_date type="string">
)
