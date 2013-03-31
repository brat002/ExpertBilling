CREATE OR REPLACE FUNCTION periodicaltr_fn(ps_id_ integer, acctf_id_ integer, account_id_ integer, credit_ numeric, type_id_ character varying, summ_ numeric, created_ timestamp without time zone, ps_condition_type_ integer, ps_condition_summ_ numeric)
  RETURNS numeric AS
$BODY$
DECLARE
    new_summ_ decimal;
    pslog_id integer;
BEGIN
    SELECT INTO new_summ_ summ_*(NOT EXISTS (SELECT id FROM billservice_suspendedperiod WHERE account_id=account_id_ AND (created_ BETWEEN start_date AND end_date)))::int;

    IF (ps_condition_type_ = 1) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(get_ballance_for_date(account_id_, created_)+credit_ < ps_condition_summ_)::int INTO new_summ_;
    ELSIF (ps_condition_type_ = 2) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(get_ballance_for_date(account_id_, created_)+credit_ <= ps_condition_summ_)::int INTO new_summ_;
    ELSIF (ps_condition_type_ = 3) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(get_ballance_for_date(account_id_, created_)+credit_ <> ps_condition_summ_)::int INTO new_summ_;
    ELSIF (ps_condition_type_ = 4) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(get_ballance_for_date(account_id_, created_)+credit_ >= ps_condition_summ_)::int INTO new_summ_;
    ELSIF (ps_condition_type_ = 5) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(get_ballance_for_date(account_id_, created_)+credit_ > ps_condition_summ_)::int INTO new_summ_;
    END IF; 

    IF (new_summ_<>0) THEN 
      INSERT INTO billservice_periodicalservicehistory (service_id, accounttarif_id,account_id, type_id, summ, created) VALUES (ps_id_, acctf_id_, account_id_, type_id_, (-1)*new_summ_, created_);
    END IF;
    SELECT  id FROM billservice_periodicalservicelog WHERE service_id=ps_id_ and accounttarif_id=acctf_id_ LIMIT 1 INTO pslog_id;
    IF pslog_id>0 THEN
        UPDATE billservice_periodicalservicelog SET datetime=created_ WHERE id=pslog_id;  
    ELSE
        INSERT INTO billservice_periodicalservicelog(service_id, accounttarif_id, datetime) VALUES(ps_id_, acctf_id_, created_);
      
    END IF;
    RETURN  new_summ_;
    
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
  