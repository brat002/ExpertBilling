
CREATE TABLE "tagging_tag" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(50) NOT NULL UNIQUE
)
;
CREATE TABLE "tagging_taggeditem" (
    "id" serial NOT NULL PRIMARY KEY,
    "tag_id" integer NOT NULL REFERENCES "tagging_tag" ("id") DEFERRABLE INITIALLY DEFERRED,
    "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED,
    "object_id" integer CHECK ("object_id" >= 0) NOT NULL,
    UNIQUE ("tag_id", "content_type_id", "object_id")
)
;
