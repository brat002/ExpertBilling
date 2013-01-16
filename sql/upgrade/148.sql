CREATE OR REPLACE FUNCTION account_payment_transaction_trg_fn() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN

IF (TG_OP = 'INSERT') AND NEW.accepted = TRUE THEN
    UPDATE billservice_account SET ballance=ballance+NEW.summ WHERE id=NEW.account_id;
    RETURN NEW;
END IF;    
IF (TG_OP = 'INSERT') AND NEW.accepted = FALSE THEN
    RETURN NEW;
END IF;    
IF (TG_OP = 'DELETE') AND OLD.accepted = TRUE THEN
    UPDATE billservice_account SET ballance=ballance-OLD.summ WHERE id=OLD.account_id;
    RETURN OLD;
END IF;    
IF (TG_OP = 'UPDATE') AND NEW.accepted = TRUE AND OLD.accepted = FALSE THEN
    UPDATE billservice_account SET ballance=ballance+NEW.summ WHERE id=NEW.account_id;
    RETURN NEW;
END IF;
IF (TG_OP = 'UPDATE') AND NEW.accepted = FALSE AND OLD.accepted = TRUE THEN
    UPDATE billservice_account SET ballance=ballance-OLD.summ WHERE id=NEW.account_id;
    RETURN NEW;
END IF;    
IF (TG_OP = 'UPDATE') AND NEW.accepted = TRUE AND OLD.accepted = TRUE THEN
  UPDATE billservice_account SET ballance=ballance-OLD.summ WHERE id=NEW.account_id;
  UPDATE billservice_account SET ballance=ballance+NEW.summ WHERE id=NEW.account_id;
  RETURN NEW;
END IF;
IF (TG_OP = 'UPDATE') AND NEW.accepted = FALSE AND OLD.accepted=False THEN
  RETURN NEW;
END IF;
RETURN NULL;
END;
$$;

ALTER TABLE billservice_systemuser RENAME is_systemuser  TO is_superuser;
update billservice_systemuser set is_superuser=True WHERE username='admin';
DELETE FROM billservice_systemuser WHERE username='webadmin';
