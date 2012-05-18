CREATE OR REPLACE FUNCTION shedulelog_tr_credit_fn(account_id_ integer, accounttarif_id_ integer, trts_id_ integer, need_traffic_reset boolean, coeff_ numeric, datetime_ timestamp without time zone)
  RETURNS void AS
$BODY$
DECLARE
        prepaid_tr_id_ int;
        size_ bigint;
        count_ int := 0;
        old_size bigint;
BEGIN
    FOR prepaid_tr_id_, size_ IN SELECT id, size FROM billservice_prepaidtraffic WHERE traffic_transmit_service_id=trts_id_ LOOP
        old_size:=0;
        IF need_traffic_reset!=True THEN
            SELECT INTO old_size (SELECT sum(size) FROM billservice_accountprepaystrafic WHERE account_tarif_id=accounttarif_id_ AND prepaid_traffic_id=prepaid_tr_id_ and current=True and reseted=False)::bigint;
        END IF;
      
        INSERT INTO billservice_accountprepaystrafic (account_tarif_id, prepaid_traffic_id, size, datetime, current) VALUES(accounttarif_id_, prepaid_tr_id_, COALESCE(old_size,0)+(size_*coeff_)::bigint, datetime_, True);
        count_ := count_ + 1;
    END LOOP;
    UPDATE billservice_accountprepaystrafic as preptr SET current=False WHERE datetime<datetime_ and current=True and preptr.account_tarif_id in (SELECT id FROM billservice_accounttarif WHERE account_id=(SELECT account_id FROM billservice_accounttarif WHERE id=accounttarif_id_));    
    IF count_ > 0 THEN
        UPDATE billservice_shedulelog SET prepaid_traffic_accrued=datetime_, accounttarif_id=accounttarif_id_ WHERE account_id=account_id_;
        IF NOT FOUND THEN
                INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_traffic_accrued) VALUES(account_id_,accounttarif_id_, datetime_);
        END IF;
    END IF;
    RETURN;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION shedulelog_tr_credit_fn(integer, integer, integer, boolean, numeric, timestamp without time zone)
  OWNER TO ebs;
