CREATE TABLE "billservice_switchport" (
    "id" serial NOT NULL PRIMARY KEY,
    "switch_id" integer NOT NULL REFERENCES "billservice_switch" ("id") DEFERRABLE INITIALLY DEFERRED,
    "port" integer NOT NULL,
    "comment" varchar(1024) NOT NULL,
    "oper_status" integer NOT NULL,
    "admin_status" integer NOT NULL,
    "uplink" boolean NOT NULL,
    "broken" boolean NOT NULL,
    "protection_id" integer REFERENCES "billservice_hardware" ("id") DEFERRABLE INITIALLY DEFERRED
)
;
CREATE TABLE "billservice_switchportstat" (
    "id" serial NOT NULL PRIMARY KEY,
    "switchport_id" integer NOT NULL REFERENCES "billservice_switchport" ("id") DEFERRABLE INITIALLY DEFERRED,
    "oper_status" integer NOT NULL,
    "admin_status" integer NOT NULL,
    "out_bytes" integer NOT NULL,
    "in_errors" integer NOT NULL,
    "out_errors" integer NOT NULL,
    "datetime" timestamp with time zone NOT NULL
);



CREATE INDEX "billservice_switch_manufacturer_id" ON "billservice_switch" ("manufacturer_id");
CREATE INDEX "billservice_switch_model_id" ON "billservice_switch" ("model_id");
CREATE INDEX "billservice_switch_city_id" ON "billservice_switch" ("city_id");
CREATE INDEX "billservice_switchport_switch_id" ON "billservice_switchport" ("switch_id");
CREATE INDEX "billservice_switchport_port" ON "billservice_switchport" ("port");
CREATE INDEX "billservice_switchport_protection_id" ON "billservice_switchport" ("protection_id");
CREATE INDEX "billservice_switchportstat_switchport_id" ON "billservice_switchportstat" ("switchport_id");