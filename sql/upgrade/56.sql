ALTER TABLE billservice_periodicalservicehistory RENAME COLUMN datetime TO created;
ALTER TABLE billservice_traffictransaction RENAME COLUMN datetime TO created;
ALTER TABLE billservice_onetimeservicehistory RENAME COLUMN datetime TO created;
ALTER TABLE billservice_timetransaction RENAME datetime  TO created;
