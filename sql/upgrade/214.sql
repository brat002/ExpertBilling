CREATE OR REPLACE FUNCTION suspended_period_check_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN
  IF (TG_OP = 'UPDATE') THEN
    IF NEW.status IN (1,2) THEN
        UPDATE billservice_suspendedperiod SET end_date = now() WHERE account_id=OLD.id AND end_date ISNULL;
    ELSIF NEW.status=3 and OLD.status<>3 THEN
        INSERT INTO billservice_suspendedperiod (account_id, start_date) VALUES (NEW.id, now());
    ELSIF NEW.status=4 and OLD.status<>4 THEN
        INSERT INTO billservice_suspendedperiod (account_id, start_date, activated_by_account) VALUES (NEW.id, now(), True);
    END IF;
    RETURN NEW;

  ELSIF (TG_OP = 'INSERT') THEN
    IF NEW.status = 3 THEN
        INSERT INTO billservice_suspendedperiod (account_id, start_date) VALUES (NEW.id, now());
    ELSIF NEW.status = 4 THEN
        INSERT INTO billservice_suspendedperiod (account_id, start_date, activated_by_account) VALUES (NEW.id, now(), True);
    END IF;
    RETURN NEW;
  END IF;
  RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
  
  
update billservice_account set status=3 where status=2;