DELETE FROM ebsadmin_comment;
CREATE TABLE "ebsadmin_comment" (
    "id" serial NOT NULL PRIMARY KEY,
    "content_type_id" integer REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED,
    "object_id" integer CHECK ("object_id" >= 0),
    "comment" text NOT NULL,
    "created" timestamp with time zone,
    "done_date" timestamp with time zone,
    "done_systemuser_id" integer REFERENCES "billservice_systemuser" ("id") DEFERRABLE INITIALLY DEFERRED,
    "due_date" timestamp with time zone,
    "deleted" timestamp with time zone
)
;
