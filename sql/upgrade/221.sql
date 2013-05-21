CREATE OR REPLACE FUNCTION radiusstat_active_insert(nas_id_ integer,  active_ integer, datetime_ timestamp without time zone)
  RETURNS void AS
$BODY$ 
DECLARE
        datetime_agg_ timestamp without time zone;
        ins_tr_id_ int;
BEGIN   

    datetime_agg_ := date_trunc('minute', datetime_); 
    UPDATE radius_radiusstat SET active=COALESCE(active_, 0) WHERE nas_id=nas_id_  and datetime=datetime_agg_;
    IF NOT FOUND THEN
        INSERT INTO radius_radiusstat(nas_id, start, alive, "end", active, datetime) VALUES (nas_id_, 0, 0, 0, active_, datetime_agg_) RETURNING id INTO ins_tr_id_;
    END IF;

    RETURN;  
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
  