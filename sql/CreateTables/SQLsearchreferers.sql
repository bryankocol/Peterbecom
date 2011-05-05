<params></params>

CREATE TABLE searchreferers (
"id" SERIAL PRIMARY KEY,
"site" TEXT NOT NULL DEFAULT '',
"searchterm" TEXT NOT NULL DEFAULT '',
"add_date" TIMESTAMP NOT NULL DEFAULT now()
)