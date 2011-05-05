<params></params>

CREATE TABLE mp3records (
"id" SERIAL PRIMARY KEY,
"title" TEXT NOT NULL DEFAULT '',
"artist" TEXT NOT NULL DEFAULT '',
"album" TEXT NOT NULL DEFAULT '',
"track" TEXT NOT NULL DEFAULT '',
"year" TEXT NOT NULL DEFAULT '',
"genre" TEXT NOT NULL DEFAULT '',
"comment" TEXT NOT NULL DEFAULT '',
"add_date" TIMESTAMP NOT NULL DEFAULT now(),
"external_links" TEXT NOT NULL DEFAULT '',

"am_url" TEXT NOT NULL DEFAULT '',
"am_imageurllarge" TEXT NOT NULL DEFAULT '',
"am_imageurlmedium" TEXT NOT NULL DEFAULT '',
"am_imageurlsmall" TEXT NOT NULL DEFAULT '',
"am_tracks" TEXT NOT NULL DEFAULT '',
"am_ourprice" TEXT NOT NULL DEFAULT '',
"am_productname" TEXT NOT NULL DEFAULT '',

"time_stamp" TIMESTAMP NOT NULL DEFAULT now()
);
