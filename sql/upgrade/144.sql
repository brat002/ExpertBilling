CREATE TABLE "ebsadmin_tablesettings" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "name" varchar(128) NOT NULL,
    "value" text NOT NULL
)
;
CREATE INDEX "ebsadmin_tablesettings_user_id" ON "ebsadmin_tablesettings" ("user_id");