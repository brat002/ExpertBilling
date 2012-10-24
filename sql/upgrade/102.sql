update billservice_account as acc set house=(SELECT "name" FROM billservice_house WHERE id=acc.house_id);
ALTER TABLE billservice_account DROP COLUMN house_id;

update billservice_account as acc set street=(SELECT "name" FROM billservice_street WHERE id=acc.street_id);
ALTER TABLE billservice_account DROP COLUMN street_id;