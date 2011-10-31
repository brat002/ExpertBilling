CREATE OR REPLACE FUNCTION account_payment_transaction_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN

IF (TG_OP = 'INSERT') THEN
    IF  NEW.accepted = TRUE THEN
        UPDATE billservice_account SET ballance=ballance+NEW.summ WHERE id=NEW.account_id;
    RETURN NEW;
    END IF;
END IF;    
    
IF (TG_OP = 'DELETE') THEN
    IF OLD.accepted = TRUE THEN
        UPDATE billservice_account SET ballance=ballance-OLD.summ WHERE id=OLD.account_id;
    RETURN OLD;
    END IF;
END IF;    

IF (TG_OP = 'UPDATE') THEN
    IF NEW.accepted = TRUE AND OLD.accepted = FALSE THEN
        UPDATE billservice_account SET ballance=ballance+NEW.summ WHERE id=NEW.account_id;
    ELSIF NEW.accepted = FALSE AND OLD.accepted = TRUE THEN
        UPDATE billservice_account SET ballance=ballance-OLD.summ WHERE id=NEW.account_id;
    ELSIF NEW.accepted = TRUE AND OLD.accepted = TRUE THEN
        UPDATE billservice_account SET ballance=ballance-OLD.summ WHERE id=NEW.account_id;
        UPDATE billservice_account SET ballance=ballance+NEW.summ WHERE id=NEW.account_id;    
    END IF;    
    RETURN NEW;
END IF;

RETURN NULL;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

