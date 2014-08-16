ALTER TABLE billservice_tariff
   DROP COLUMN deleted;
ALTER TABLE billservice_tariff
   ADD COLUMN deleted timestamp without time zone;
