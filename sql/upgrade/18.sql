CREATE TABLE "billservice_contracttemplate" (
    "id" serial NOT NULL PRIMARY KEY,
    "template" text NOT NULL
);
ALTER TABLE billservice_tariff
   ADD COLUMN contracttemplate_id integer;

ALTER TABLE billservice_tariff ADD CONSTRAINT billservice_tariff_contracttemplate_id_fkey FOREIGN KEY (contracttemplate_id) REFERENCES billservice_contracttemplate (id)
   ON UPDATE NO ACTION ON DELETE SET NULL;
CREATE INDEX fki_billservice_tariff_contracttemplate_id_fkey ON billservice_tariff(contracttemplate_id);

ALTER TABLE billservice_contracttemplate
   ADD COLUMN counter integer;

