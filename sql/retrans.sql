CREATE OR REPLACE FUNCTION account_transaction_trg_fn() RETURNS trigger
    AS $$
    
BEGIN

IF (TG_OP = 'INSERT') THEN
--UPDATE billservice_account SET ballance=ballance-NEW.summ WHERE id=NEW.account_id;
RETURN NEW;
ELSIF (TG_OP = 'DELETE') THEN
--UPDATE billservice_account SET ballance=ballance+OLD.summ WHERE id=OLD.account_id;
RETURN OLD;
ELSIF (TG_OP = 'UPDATE') THEN
--UPDATE billservice_account SET ballance=ballance+OLD.summ WHERE id=OLD.account_id;
--UPDATE billservice_account SET ballance=ballance-NEW.summ WHERE id=NEW.account_id;
RETURN NEW;
END IF;
RETURN NULL;
END;
$$
    LANGUAGE plpgsql;


UPDATE billservice_onetimeservicehistory SET account_id = (SELECT bacc.account_id FROM billservice_accounttarif AS bacc WHERE bacc.id = accounttarif_id);
UPDATE billservice_periodicalservicehistory SET account_id = (SELECT bacc.account_id FROM billservice_accounttarif AS bacc WHERE bacc.id = accounttarif_id);
UPDATE billservice_onetimeservicehistory SET summ = (SELECT btr.summ from billservice_transaction as btr WHERE btr.id = transaction_id);
UPDATE billservice_periodicalservicehistory SET summ = (SELECT btr.summ from billservice_transaction as btr WHERE btr.id = transaction_id), type_id = (SELECT btr.type_id from billservice_transaction as btr WHERE btr.id = transaction_id);

UPDATE billservice_onetimeservicehistory SET summ = 0 WHERE summ IS NULL;
UPDATE billservice_periodicalservicehistory SET summ = 0 WHERE summ IS NULL;
DELETE from billservice_transaction WHERE type_id IN ('ONETIME_SERVICE', 'PS_GRADUAL', 'PS_AT_START', 'PS_AT_END');
    
CREATE OR REPLACE FUNCTION account_transaction_trg_fn() RETURNS trigger
    AS $$
BEGIN

IF (TG_OP = 'INSERT') THEN
UPDATE billservice_account SET ballance=ballance-NEW.summ WHERE id=NEW.account_id;
RETURN NEW;
ELSIF (TG_OP = 'DELETE') THEN
UPDATE billservice_account SET ballance=ballance+OLD.summ WHERE id=OLD.account_id;
RETURN OLD;
ELSIF (TG_OP = 'UPDATE') THEN
UPDATE billservice_account SET ballance=ballance+OLD.summ WHERE id=OLD.account_id;
UPDATE billservice_account SET ballance=ballance-NEW.summ WHERE id=NEW.account_id;
RETURN NEW;
END IF;
RETURN NULL;
END;
$$
    LANGUAGE plpgsql; 
