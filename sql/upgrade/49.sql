CREATE OR REPLACE FUNCTION account_payment_transaction_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN

IF (TG_OP = 'INSERT') AND NEW.accepted = TRUE THEN
UPDATE billservice_account SET ballance=ballance+NEW.summ WHERE id=NEW.account_id;
RETURN NEW;
ELSIF (TG_OP = 'DELETE') AND OLD.accepted = TRUE THEN
UPDATE billservice_account SET ballance=ballance-OLD.summ WHERE id=OLD.account_id;
RETURN OLD;
ELSIF (TG_OP = 'UPDATE') AND NEW.accepted = TRUE AND OLD.accepted = FALSE THEN
UPDATE billservice_account SET ballance=ballance+NEW.summ WHERE id=NEW.account_id;
RETURN NEW;
ELSIF (TG_OP = 'UPDATE') AND NEW.accepted = FALSE AND OLD.accepted = TRUE THEN
UPDATE billservice_account SET ballance=ballance-OLD.summ WHERE id=NEW.account_id;
RETURN NEW;
ELSIF (TG_OP = 'UPDATE') AND NEW.accepted = TRUE AND OLD.accepted = TRUE THEN
  UPDATE billservice_account SET ballance=ballance-OLD.summ WHERE id=NEW.account_id;
  UPDATE billservice_account SET ballance=ballance+NEW.summ WHERE id=NEW.account_id;
  RETURN NEW;
ELSIF (TG_OP = 'UPDATE') THEN
  RETURN NEW;
END IF;
RETURN NULL;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

