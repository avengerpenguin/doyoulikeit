-- Create "votes" table
CREATE TABLE "votes"
(
    "user_id"  text    NOT NULL,
    "thing_id" text    NOT NULL,
    "liked"    boolean NULL,
    PRIMARY KEY ("user_id", "thing_id")
);
