CREATE TABLE "billservice_accountsuppagreement" (
    "id" serial NOT NULL PRIMARY KEY,
    "suppagreement_id" integer NOT NULL,
    "account_id" integer NOT NULL REFERENCES "billservice_account" ("id") DEFERRABLE INITIALLY DEFERRED,
    "contract" varchar(128) NOT NULL,
    "accounthardware_id" integer REFERENCES "billservice_accounthardware" ("id") DEFERRABLE INITIALLY DEFERRED,
    "created" timestamp with time zone NOT NULL,
    "closed" timestamp with time zone
)
;
CREATE TABLE "billservice_suppagreement" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(128) NOT NULL,
    "description" text NOT NULL,
    "body" text NOT NULL,
    "length" integer,
    "disable_tarff_change" boolean NOT NULL
)
;

CREATE INDEX "billservice_accountsuppagreement_suppagreement_id" ON "billservice_accountsuppagreement" ("suppagreement_id");
CREATE INDEX "billservice_accountsuppagreement_account_id" ON "billservice_accountsuppagreement" ("account_id");
CREATE INDEX "billservice_accountsuppagreement_accounthardware_id" ON "billservice_accountsuppagreement" ("accounthardware_id");

INSERT INTO billservice_permission(
            name, internal_name, ordering, app)
    VALUES ('Просматривать виды доп. соглашений', 'view_suppagreement', '250', 'billservice');

INSERT INTO billservice_permission(
            name, internal_name, ordering, app)
    VALUES ('Редактировать виды доп. соглашений', 'edit_suppagreement', '251', 'billservice');

INSERT INTO billservice_permission(
            name, internal_name, ordering, app)
    VALUES ('Удалять виды доп. соглашений', 'delete_suppagreement', '252', 'billservice');
    