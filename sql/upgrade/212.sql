update billservice_card set salecard_id=(SELECT max(id) FROM billservice_salecard);
UPDATE billservice_account set allow_webcab =True;