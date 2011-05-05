<params></params>

CREATE TABLE google_result_index (
"id" SERIAL PRIMARY KEY,
"index" INTEGER NOT NULL DEFAULT 0,
"searchterm" TEXT NOT NULL DEFAULT '',
"check_date" TIMESTAMP NOT NULL DEFAULT now()
)
