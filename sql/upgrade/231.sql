ALTER TABLE billservice_periodicalservicehistory ADD COLUMN real_created timestamp without time zone;
ALTER TABLE billservice_periodicalservicehistory ALTER COLUMN real_created SET DEFAULT now();