<params></params>

CREATE TABLE blogitemviews (
"id" SERIAL PRIMARY KEY,
"blogitemid" TEXT NOT NULL DEFAULT '',
"blogitemurl" TEXT NOT NULL DEFAULT '',
"http_referer" TEXT NOT NULL DEFAULT '',
"user_agent" TEXT NOT NULL DEFAULT '',
"visit_date" TIMESTAMP NOT NULL DEFAULT now(),

"time_stamp" TIMESTAMP NOT NULL DEFAULT now()
)
