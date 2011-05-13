CREATE OR REPLACE FUNCTION trs_inserter(trsr billservice_transaction) RETURNS void
    AS 
$BODY$
DECLARE
    datetx_ text := to_char(trsr.created::date, 'YYYYMM01');
    insq_   text;

    ttrn_actfid_ text;  
    ttrn_bill    text;
    ttrn_account_id    text;
    ttrn_type_id    text;
    ttrn_approved    text;
    ttrn_tarif_id    text;
    ttrn_summ    text;
    ttrn_description    text;
    ttrn_created    text;
    ttrn_systemuser_id    text;
    ttrn_accounttarif_id    text;
    ttrn_promise   text;
    ttrn_end_promise   text;
    ttrn_promise_expired   text;  
BEGIN
    
    IF trsr.bill IS NULL THEN
       ttrn_bill := 'NULL';
    ELSE
       ttrn_bill := quote_literal(trsr.bill);
    END IF;
    IF trsr.accounttarif_id IS NULL AND trsr.account_id NOTNULL THEN
    	SELECT INTO ttrn_accounttarif_id ba.id FROM billservice_accounttarif AS ba WHERE ba.account_id = trsr.account_id AND ba.datetime < trsr.created ORDER BY ba.datetime DESC LIMIT 1;
    END IF;
    IF trsr.account_id IS NULL THEN
	   ttrn_account_id := 'NULL';
	ELSE
	   ttrn_account_id := trsr.account_id::text;
	END IF;
	IF trsr.type_id IS NULL THEN
	   ttrn_type_id := 'NULL';
	ELSE
	   ttrn_type_id := quote_literal(trsr.type_id);
	END IF;
	IF trsr.approved IS NULL THEN
	   ttrn_approved := 'NULL';
	ELSE
	   ttrn_approved := trsr.approved::text;
	END IF;
	IF trsr.tarif_id IS NULL THEN
	   ttrn_tarif_id := 'NULL';
	ELSE
	   ttrn_tarif_id := trsr.tarif_id::text;
	END IF;
	IF trsr.summ IS NULL THEN
	   ttrn_summ := 'NULL';
	ELSE
	   ttrn_summ := trsr.summ::text;
	END IF;
	IF trsr.description IS NULL THEN
	   ttrn_description := 'NULL';
	ELSE
	   ttrn_description := quote_literal(trsr.description);
	END IF;
	IF trsr.created IS NULL THEN
	   ttrn_created := 'NULL';
	ELSE
		ttrn_created := quote_literal(trsr.created);
	END IF;
	IF trsr.systemuser_id IS NULL THEN
	   ttrn_systemuser_id := 'NULL';
	ELSE
	   ttrn_systemuser_id := trsr.systemuser_id::text;
	END IF;
	IF trsr.promise IS NULL THEN
	   ttrn_promise := 'NULL';
	ELSE
	   ttrn_promise := trsr.promise::text;
	END IF;
	IF trsr.end_promise IS NULL THEN
	   ttrn_end_promise := 'NULL';
	ELSE
	   ttrn_end_promise := quote_literal(trsr.end_promise);
	END IF;
	IF trsr.promise_expired IS NULL THEN
	   ttrn_promise_expired := 'NULL';
	ELSE
	   ttrn_promise_expired := trsr.promise_expired::text;
	END IF;
	IF trsr.accounttarif_id IS NULL THEN
	   ttrn_accounttarif_id := 'NULL';
	ELSE
	   ttrn_accounttarif_id := trsr.accounttarif_id::text;
	END IF;
    insq_ := 'INSERT INTO trs' || datetx_ || ' (bill, account_id, type_id, approved, tarif_id, summ, description, created, systemuser_id, promise, end_promise, promise_expired, accounttarif_id) VALUES (' || ttrn_bill || ',' || ttrn_account_id || ',' || ttrn_type_id || ',' || ttrn_approved || ',' || ttrn_tarif_id || ',' || ttrn_summ || ',' || ttrn_description || ',' || ttrn_created || ',' || ttrn_systemuser_id || ',' || ttrn_promise || ',' || ttrn_end_promise || ',' || ttrn_promise_expired || ',' || ttrn_accounttarif_id || ');';
    EXECUTE insq_;
    RETURN;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;

