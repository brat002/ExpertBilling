-- Function: traftrans_crt_cur_ins(date)

-- DROP FUNCTION traftrans_crt_cur_ins(date);

CREATE OR REPLACE FUNCTION traftrans_crt_cur_ins(datetx date)
  RETURNS void AS
$BODY$
DECLARE
    datetx_ text := to_char(datetx, 'YYYYMM01');
    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION traftrans_cur_ins (traftrns billservice_traffictransaction) RETURNS void AS ';
    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO traftrans';
    fn_bd_tx2_ text := '(traffictransmitservice_id, radiustraffictransmitservice_id, account_id, accounttarif_id, summ, created)
                          VALUES 
                         (traftrns.traffictransmitservice_id, traftrns.radiustraffictransmitservice_id,traftrns.account_id, traftrns.accounttarif_id, traftrns.summ, traftrns.created); RETURN; END;';        
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';
    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION traftrans_cur_datechk(trs_date timestamp without time zone) RETURNS integer AS ';
    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    trs_date < d_s_ THEN RETURN -1; ELSIF trs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';
    dt_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION traftrans_cur_dt() RETURNS date AS ';
    onemonth_ text := '1 month';
    query_ text;
    
    prevdate_ date;
    
BEGIN    
        query_ :=  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;
        EXECUTE query_;
        query_ :=  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '+ interval ' || quote_literal(onemonth_) ||  ch_fn_bd_tx3_) || fn_tx2_;
        EXECUTE query_;
        prevdate_ := traftrans_cur_dt();
        PERFORM traftrans_crt_prev_ins(prevdate_);
        query_ := dt_fn_tx1_ || quote_literal(' BEGIN RETURN  DATE ' || quote_literal(datetx_) || '; END; ') || fn_tx2_;
        EXECUTE query_;
    RETURN;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION traftrans_crt_cur_ins(date) OWNER TO postgres;



-- Function: traftrans_crt_prev_ins(date)

-- DROP FUNCTION traftrans_crt_prev_ins(date);

CREATE OR REPLACE FUNCTION traftrans_crt_prev_ins(datetx date)
  RETURNS void AS
$BODY$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION traftrans_prev_ins (traftrns billservice_traffictransaction) RETURNS void AS ';
    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO traftrans';
    fn_bd_tx2_ text := '(traffictransmitservice_id, radiustraffictransmitservice_id,account_id, accounttarif_id, summ, created)
                          VALUES 
                         (traftrns.traffictransmitservice_id, traftrns.radiustraffictransmitservice_id, traftrns.account_id, traftrns.accounttarif_id, traftrns.summ, traftrns.created); RETURN; END;';
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';
    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION traftrans_prev_datechk(trs_date timestamp without time zone) RETURNS integer AS ';
    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    trs_date < d_s_ THEN RETURN -1; ELSIF trs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';
    ch_fn_tx2_ text := ' LANGUAGE plpgsql VOLATILE COST 100;';
    qts_ text := 'CHK % % %';
    onemonth_ text := '1 month';
    query_ text;
BEGIN    
        EXECUTE  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;
        query_ :=  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '+ interval ' || quote_literal(onemonth_) ||  ch_fn_bd_tx3_) || fn_tx2_;
        EXECUTE query_;
    RETURN;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION traftrans_crt_prev_ins(date) OWNER TO postgres;

-- Function: traftrans_cur_ins(billservice_traffictransaction)

-- DROP FUNCTION traftrans_cur_ins(billservice_traffictransaction);

CREATE OR REPLACE FUNCTION traftrans_cur_ins(traftrns billservice_traffictransaction)
  RETURNS void AS
$BODY$BEGIN 
                         INSERT INTO traftrans20120301(traffictransmitservice_id, radiustraffictransmitservice_id, account_id, accounttarif_id, summ, created)
                          VALUES 
                         (traftrns.traffictransmitservice_id, traftrns.radiustraffictransmitservice_id,traftrns.account_id, traftrns.accounttarif_id, traftrns.summ, traftrns.created); RETURN; END;$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION traftrans_cur_ins(billservice_traffictransaction) OWNER TO ebs;

