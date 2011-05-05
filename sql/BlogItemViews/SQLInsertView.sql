<params>blogitemid
blogitemurl
http_referer
user_agent</params>

INSERT INTO blogitemviews (
blogitemid,
blogitemurl,
http_referer,
user_agent,
visit_date
)

VALUES (
<dtml-sqlvar blogitemid type="string">,
<dtml-sqlvar blogitemurl type="string">,
<dtml-sqlvar http_referer type="string">,
<dtml-sqlvar user_agent type="string">,
NOW()
)


