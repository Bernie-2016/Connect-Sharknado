DROP TABLE IF EXISTS video;
DROP TABLE IF EXISTS event;
DROP TABLE IF EXISTS issue;
DROP TABLE IF EXISTS article;

CREATE TABLE video (
    uuid uuid NOT NULL,
    video_id text,
    site text,
    title text,
    description text,
    thumbnail_url text,
    timestamp_creation timestamp with time zone,
    timestamp_publish timestamp with time zone,
    description_snippet text
);

CREATE UNIQUE INDEX index_video_uuid ON video (uuid);

CREATE UNIQUE INDEX index_video_id ON video (video_id);


CREATE TABLE event (
    uuid uuid NOT NULL,
    event_id text,
    event_id_obfuscated text,
    url text,
    name text,
    date text,
    start_time timestamp without time zone,
    timezone text,
    description text,
    latitude double precision,
    longitude double precision,
    attendee_count integer,
    capacity integer,
    site text,
    lang text,
    event_type_name text,
    venue_address1 text,
    venue_address2 text,
    venue_address3 text,
    venue_name text,
    venue_city text,
    venue_state text,
    venue_zip integer,
    timestamp_creation timestamp with time zone,
    is_official boolean
);

CREATE UNIQUE INDEX index_event_uuid ON event (uuid);

CREATE UNIQUE INDEX index_event_id ON event (event_id);


CREATE TABLE issue (
    uuid uuid NOT NULL,
    url text,
    site text,
    lang text,
    title text,
    article_type text,
    body text,
    body_html text,
    description text,
    description_html text,
    timestamp_creation timestamp with time zone,
    timestamp_publish timestamp with time zone
);

CREATE UNIQUE INDEX index_issue_uuid ON video (uuid);

CREATE UNIQUE INDEX index_issue_url ON video (url);

CREATE TABLE article (
  uuid uuid NOT NULL,
  article_id text,
  timestamp_creation timestamp with time zone,
  timestamp_publish timestamp with time zone,
  title text,
  article_type text,
  site text,
  lang text,
  excerpt_html text,
  excerpt text,
  article_category text,
  url text,
  image_url text,
  body text,
  body_html text,
  body_html_nostyle text,
  CONSTRAINT title_article_type UNIQUE (title, article_type) -- No duplicates with the same title and article type
)
CREATE UNIQUE INDEX index_article_uuid ON article (uuid);

CREATE UNIQUE INDEX index_article_id ON article (article_id);