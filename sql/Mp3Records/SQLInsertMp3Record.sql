<params>id
title
artist
album
track
year
genre
comment
external_links
add_date</params>

INSERT INTO mp3records (
id,
title,
artist,
album,
track,
year,
genre,
comment,
external_links,
add_date
)

VALUES (
<dtml-sqlvar id type="int">,
<dtml-sqlvar title type="string">,
<dtml-sqlvar artist type="string">,
<dtml-sqlvar album type="string">,
<dtml-sqlvar track type="string">,
<dtml-sqlvar year type="string">,
<dtml-sqlvar genre type="string">,
<dtml-sqlvar comment type="string">,
<dtml-sqlvar external_links type="string">,
<dtml-sqlvar add_date type="string">
)
