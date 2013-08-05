CREATE TABLE "ebsadmin_comment" (
    "id" serial NOT NULL PRIMARY KEY,
    "content_type_id" integer REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED,
    "object_id" integer CHECK ("object_id" >= 0),
    "comment" text NOT NULL,
    "notify_date" timestamp with time zone NOT NULL,
    "due_date" timestamp with time zone NOT NULL,
    "deleted" timestamp with time zone NOT NULL
)
;
