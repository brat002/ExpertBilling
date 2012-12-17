CREATE OR REPLACE FUNCTION transaction_block_sum(account_id_ integer, start_date_ timestamp without time zone, end_date_ timestamp without time zone)
  RETURNS numeric AS
$BODY$ 
DECLARE
    start_date_5m_ timestamp without time zone;
    result_ decimal;
BEGIN
    start_date_5m_ := date_trunc('minute', start_date_) - interval '1 min' * (date_part('min', start_date_)::int % 5); 
    SELECT INTO result_ sum(ssum) FROM (
        SELECT sum(summ) AS ssum FROM billservice_transaction WHERE account_id=account_id_ AND (((summ > 0) AND (created BETWEEN start_date_ AND end_date_)) OR ((summ < 0) AND created <= end_date_))
        UNION ALL 
        SELECT sum(summ) AS ssum FROM billservice_traffictransaction WHERE account_id=account_id_ AND (summ > 0) AND (created BETWEEN start_date_ AND end_date_) 
        UNION ALL 
        SELECT sum(summ) AS ssum FROM billservice_timetransaction WHERE account_id=account_id_ AND (summ > 0) AND (created BETWEEN start_date_ AND end_date_) 
        UNION ALL 
        SELECT sum(summ) AS ssum FROM billservice_periodicalservicehistory WHERE account_id=account_id_ AND (summ > 0) AND (created BETWEEN start_date_ AND end_date_)  
        UNION ALL 
        SELECT sum(summ) AS ssum FROM billservice_onetimeservicehistory WHERE account_id=account_id_ AND (summ > 0) AND (created BETWEEN start_date_ AND end_date_)) 
    AS ts_union ;
    RETURN result_;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION transaction_block_sum(integer, timestamp without time zone, timestamp without time zone)
  OWNER TO ebs;
  