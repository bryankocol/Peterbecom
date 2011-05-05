<params></params>

CREATE TABLE photoviews (
"id"           SERIAL PRIMARY KEY,
"photoid"      VARCHAR (100) NOT NULL DEFAULT '',
"photopath"    VARCHAR (200) NOT NULL DEFAULT '',
"photourl"     TEXT NOT NULL DEFAULT '',
"http_referer" TEXT NOT NULL DEFAULT '',
"user_agent"   TEXT NOT NULL DEFAULT '',
"time_stamp"   TIMESTAMP NOT NULL DEFAULT now()
)
