<params></params>

CREATE TABLE referers (
"id" SERIAL PRIMARY KEY,
"domain" TEXT NOT NULL DEFAULT '',
"querystring" TEXT NOT NULL DEFAULT '',
"url" TEXT NOT NULL DEFAULT '',
"http_user_agent" TEXT NOT NULL DEFAULT '',
"add_date" TIMESTAMP NOT NULL DEFAULT now()
)