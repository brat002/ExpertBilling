CREATE OR REPLACE FUNCTION timetransaction_insert(taccs_id_ int, accounttarif_id_ int, account_id_ int, summ_ decimal, datetime_ timestamp without time zone, sessionid_ character varying(32), interrim_update_ timestamp without time zone) RETURNS void
    AS $$ 
DECLARE
        datetime_agg_ timestamp without time zone;
        ins_tr_id_ int;
BEGIN   

    datetime_agg_ := date_trunc('minute', datetime_) - interval '1 min' * (date_part('min', datetime_)::int % 5); 
    UPDATE billservice_timetransaction SET summ=summ+summ_ WHERE timeaccessservice_id=taccs_id_ AND account_id=account_id_ AND created=datetime_agg_ RETURNING id INTO ins_tr_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_timetransaction(timeaccessservice_id, accounttarif_id, account_id, summ, created) VALUES (taccs_id_, accounttarif_id_, account_id_, summ_, datetime_agg_) RETURNING id INTO ins_tr_id_;
    END IF;

    RETURN;  
END;
$$
    LANGUAGE plpgsql;
DROP FUNCTION tmtrans_ins_trg_fn() CASCADE;