CREATE TABLE "billservice_permission" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(500) NOT NULL,
    "internal_name" varchar(500) NOT NULL,
    "ordering" integer NOT NULL
)
;
CREATE TABLE "billservice_permissiongroup_permissions" (
    "id" serial NOT NULL PRIMARY KEY,
    "permissiongroup_id" integer NOT NULL,
    "permission_id" integer NOT NULL REFERENCES "billservice_permission" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("permissiongroup_id", "permission_id")
)
;
CREATE TABLE "billservice_permissiongroup" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(128) NOT NULL,
    "deletable" boolean NOT NULL
)
;
ALTER TABLE billservice_systemuser
   ADD COLUMN permissiongroup_id integer;

ALTER TABLE billservice_systemuser
   ADD COLUMN is_systemuser boolean DEFAULT False;

ALTER TABLE billservice_permission
   ADD COLUMN app character varying(128);


ALTER TABLE "billservice_systemuser" ADD CONSTRAINT "permissiongroup_id_refs_id_e0fb6e4" FOREIGN KEY ("permissiongroup_id") REFERENCES "billservice_permissiongroup" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "billservice_permissiongroup_permissions" ADD CONSTRAINT "permissiongroup_id_refs_id_2b863de2" FOREIGN KEY ("permissiongroup_id") REFERENCES "billservice_permissiongroup" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "billservice_systemuser_permissiongroup_id" ON "billservice_systemuser" ("permissiongroup_id")