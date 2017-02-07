CREATE OR REPLACE FUNCTION billservice_account_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN

IF (TG_OP = 'DELETE') THEN
    DELETE FROM billservice_accountaddonservice WHERE account_id=OLD.id;
    DELETE FROM billservice_accountipnspeed WHERE account_id=OLD.id;
    DELETE FROM billservice_accountspeedlimit WHERE account_id=OLD.id;
    DELETE FROM billservice_accounttarif WHERE account_id=OLD.id;
    DELETE FROM billservice_accountviewednews WHERE account_id=OLD.id;
    DELETE FROM billservice_addonservicetransaction WHERE account_id=OLD.id;
    DELETE FROM billservice_balancehistory WHERE account_id=OLD.id;
    DELETE FROM billservice_document WHERE account_id=OLD.id;
    DELETE FROM billservice_groupstat WHERE account_id=OLD.id;
    DELETE FROM billservice_onetimeservicehistory WHERE account_id=OLD.id;
    DELETE FROM billservice_organization WHERE account_id=OLD.id;
    DELETE FROM billservice_periodicalservicehistory WHERE account_id=OLD.id;
    DELETE FROM billservice_shedulelog WHERE account_id=OLD.id;
    DELETE FROM billservice_subaccount WHERE account_id=OLD.id;
    DELETE FROM billservice_suspendedperiod WHERE account_id=OLD.id;
    DELETE FROM billservice_timetransaction WHERE account_id=OLD.id;
    DELETE FROM billservice_transaction WHERE account_id=OLD.id;
    DELETE FROM billservice_traffictransaction WHERE account_id=OLD.id;
    DELETE FROM billservice_x8021 WHERE account_id=OLD.id;
    DELETE FROM radius_activesession WHERE account_id=OLD.id;
    DELETE FROM webmoney_payment WHERE account_id=OLD.id;
    
    RETURN OLD;
END IF;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION billservice_account_trg_fn()
  OWNER TO ebs;