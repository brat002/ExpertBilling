CREATE OR REPLACE FUNCTION psh_inserter(pshr billservice_periodicalservicehistory)
  RETURNS void AS
$BODY$
DECLARE
    datetx_ text := to_char(pshr.created::date, 'YYYYMM01');
    insq_   text;

    ttrn_actfid_ text;    
BEGIN
    
    IF pshr.accounttarif_id IS NULL THEN
       ttrn_actfid_ := 'NULL';
    ELSE
       ttrn_actfid_ := pshr.accounttarif_id::text;
    END IF;
    insq_ := 'INSERT INTO psh' || datetx_ || ' (service_id, account_id, accounttarif_id, type_id, summ, created) VALUES (' 
    || pshr.service_id || ',' || pshr.account_id || ',' || pshr.accounttarif_id || ','  || quote_literal(pshr.type_id) || ',' || pshr.summ || ','  || quote_literal(pshr.created) || ');';
    EXECUTE insq_;
    RETURN;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION psh_inserter(billservice_periodicalservicehistory)
  OWNER TO ebs;

  