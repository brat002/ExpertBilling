DROP TRIGGER acc_psh_trg ON billservice_periodicalservicehistory;
DROP FUNCTION periodicaltr_fn(integer, integer, integer, character varying, numeric, timestamp without time zone, integer);
CREATE OR REPLACE FUNCTION periodicaltr_fn(ps_id_ integer, acctf_id_ integer, account_id_ integer, type_id_ character varying, summ_ numeric, created_ timestamp without time zone, ps_condition_type_ integer)
  RETURNS decimal AS
$BODY$
DECLARE
    new_summ_ decimal;
BEGIN
    SELECT INTO new_summ_ summ_*(NOT EXISTS (SELECT id FROM billservice_suspendedperiod WHERE account_id=account_id_ AND (created_ BETWEEN start_date AND end_date)))::int;
    IF (ps_condition_type_ = 1) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance+credit >= 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    ELSIF (ps_condition_type_ = 2) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance+credit < 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    ELSIF (ps_condition_type_ = 3) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance+credit > 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    END IF; 
    UPDATE billservice_account SET ballance=ballance-new_summ_ WHERE id=account_id_;
    INSERT INTO billservice_periodicalservicehistory (service_id, accounttarif_id,account_id, type_id, summ, datetime) VALUES (ps_id_, acctf_id_, account_id_, type_id_, new_summ_, created_);
    RETURN  new_summ_;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION periodicaltr_fn(integer, integer, integer, character varying, numeric, timestamp without time zone, integer) OWNER TO postgres;

