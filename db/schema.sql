CREATE TABLE things (
  thing_id text PRIMARY KEY,
  label text NOT NULL,
  description text NOT NULL,
  image_url text NOT NULL
);

CREATE TABLE votes (
    user_id text,
    thing_id text,
    liked boolean,
    PRIMARY KEY(user_id, thing_id)
);
