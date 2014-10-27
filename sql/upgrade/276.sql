CREATE OR REPLACE FUNCTION balance_history_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN
  IF (TG_OP = 'UPDATE') THEN
    IF NEW.ballance<>OLD.ballance THEN
        INSERT INTO billservice_balancehistory(account_id, balance, summ, datetime) VALUES(NEW.id, NEW.ballance, COALESCE(NEW.ballance, 0)-COALESCE(OLD.ballance, 0),clock_timestamp());
    END IF;
  END IF;
  RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION balance_history_trg_fn()
  OWNER TO ebs;
  
update billservice_balancehistory set datetime =datetime+interval '1 second' WHERE id in (SELECT max(id) FROM billservice_balancehistory GROUP BY account_id);
  