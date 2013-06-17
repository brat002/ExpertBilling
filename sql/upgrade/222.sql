CREATE OR REPLACE FUNCTION account_transaction_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN



IF (TG_OP = 'INSERT') THEN
SELECT INTO NEW.prev_balance  COALESCE(ballance, 0) FROM billservice_account WHERE id=NEW.account_id;
UPDATE billservice_account SET ballance=COALESCE(ballance, 0)+NEW.summ WHERE id=NEW.account_id;
RETURN NEW;
ELSIF (TG_OP = 'DELETE') THEN
UPDATE billservice_account SET ballance=COALESCE(ballance, 0)-OLD.summ WHERE id=OLD.account_id;
RETURN OLD;
ELSIF (TG_OP = 'UPDATE') THEN
SELECT INTO NEW.prev_balance  COALESCE(ballance, 0) FROM billservice_account WHERE id=NEW.account_id;
UPDATE billservice_account SET ballance=COALESCE(ballance, 0)-OLD.summ WHERE id=OLD.account_id;
UPDATE billservice_account SET ballance=COALESCE(ballance, 0)+NEW.summ WHERE id=NEW.account_id;
RETURN NEW;
END IF;
RETURN NULL;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION account_transaction_trg_fn()
  OWNER TO ebs;
  