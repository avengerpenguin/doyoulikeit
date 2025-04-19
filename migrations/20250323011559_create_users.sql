-- Create "things" table
CREATE TABLE "things"
(
    "thing_id"    text NOT NULL,
    "label"       text NOT NULL,
    "description" text NOT NULL,
    "image_url"   text NOT NULL,
    PRIMARY KEY ("thing_id")
);
