ALTER TABLE billservice_addonservicetarif
   ADD COLUMN "type" integer;
   
UPDATE billservice_addonservicetarif SET type=0;

ALTER TABLE billservice_addonservicetarif
   ALTER COLUMN "type" SET NOT NULL;
