<params>
photoid
photopath
photourl
http_referer
user_agent
</params>

INSERT INTO photoviews (
photoid,
photopath,
photourl,
http_referer,
user_agent
)

VALUES (
<dtml-sqlvar photoid type="string">,
<dtml-sqlvar photopath type="string">,
<dtml-sqlvar photourl type="string">,
<dtml-sqlvar http_referer type="string">,
<dtml-sqlvar user_agent type="string">
)


