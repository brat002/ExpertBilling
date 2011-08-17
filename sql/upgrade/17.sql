ALTER TABLE radius_activesession
   ADD COLUMN nas_port_id integer;

ALTER TABLE radius_activesession
   ADD COLUMN ipinuse_id integer;


CREATE OR REPLACE FUNCTION rad_activesession_crt_cur_ins(datetx date)
  RETURNS void AS
$BODY$
DECLARE
    datetx_ text := to_char(datetx, 'YYYYMM01');
    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION rad_activesession_cur_ins (radaccts radius_activesession) RETURNS void AS ';
    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO radaccts';
    fn_bd_tx2_ text := '(account_id, sessionid, interrim_update, date_start, date_end, 
            caller_id, called_id, nas_id, session_time, framed_protocol, 
            bytes_in, bytes_out, session_status, speed_string, framed_ip_address, 
            nas_int_id, subaccount_id, acct_terminate_cause,lt_time, lt_bytes_in,lt_bytes_out,nas_port_id, ipinuse_id)
                          VALUES 
                         (radaccts.account_id, radaccts.sessionid, radaccts.interrim_update, radaccts.date_start, radaccts.date_end, 
			    radaccts.caller_id, radaccts.called_id, radaccts.nas_id, radaccts.session_time, radaccts.framed_protocol, 
			    radaccts.bytes_in, radaccts.bytes_out, radaccts.session_status, radaccts.speed_string, radaccts.framed_ip_address, 
			    radaccts.nas_int_id, radaccts.subaccount_id, radaccts.acct_terminate_cause, radaccts.lt_time, radaccts.lt_bytes_in, radaccts.lt_bytes_out, radaccts.nas_port_id,radaccts.ipinuse_id); RETURN; END;';
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';
    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION rad_activesession_cur_datechk(rad_activesession_date timestamp without time zone) RETURNS integer AS ';
    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    rad_activesession_date < d_s_ THEN RETURN -1; ELSIF rad_activesession_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';
    dt_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION activesession_cur_dt() RETURNS date AS ';
    onemonth_ text := '1 month';
    query_ text;
    prevdate_ date;
    
BEGIN    
        query_ :=  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;
        EXECUTE query_;
        query_ :=  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '+ interval ' || quote_literal(onemonth_) ||  ch_fn_bd_tx3_) || fn_tx2_;
        EXECUTE query_;
        prevdate_ := activesession_cur_dt();
        PERFORM radius_activesession_crt_prev_ins(prevdate_);
        query_ := dt_fn_tx1_ || quote_literal(' BEGIN RETURN  DATE ' || quote_literal(datetx_) || '; END; ') || fn_tx2_;
        EXECUTE query_;
    RETURN;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION rad_activesession_crt_cur_ins(date) OWNER TO ebs;


CREATE OR REPLACE FUNCTION radius_activesession_crt_prev_ins(datetx date)
  RETURNS void AS
$BODY$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');
    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION radius_activesession_prev_ins (radaccts radius_activesession) RETURNS void AS ';
    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO radaccts';
    fn_bd_tx2_ text := '(account_id, sessionid, interrim_update, date_start, date_end, 
            caller_id, called_id, nas_id, session_time, framed_protocol, 
            bytes_in, bytes_out, session_status, speed_string, framed_ip_address, 
            nas_int_id, subaccount_id, acct_terminate_cause,lt_time, lt_bytes_in, lt_bytes_out, nas_port_id, ipiunse_id)
                          VALUES 
                         (radaccts.account_id, radaccts.sessionid, radaccts.interrim_update, radaccts.date_start, radaccts.date_end, 
			    radaccts.caller_id, radaccts.called_id, radaccts.nas_id, radaccts.session_time, radaccts.framed_protocol, 
			    radaccts.bytes_in, radaccts.bytes_out, radaccts.session_status, radaccts.speed_string, radaccts.framed_ip_address, 
			    radaccts.nas_int_id, radaccts.subaccount_id, radaccts.acct_terminate_cause, radaccts.lt_time, radaccts.lt_bytes_in, radaccts.lt_bytes_out, radaccts.nas_port_id, radaccts.ipinuse_id); RETURN; END;';
                          
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';


    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION radius_activesession_prev_datechk(trs_date timestamp without time zone) RETURNS integer AS ';

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
ALTER FUNCTION radius_activesession_crt_prev_ins(date) OWNER TO ebs;

CREATE OR REPLACE FUNCTION radius_activesession_inserter(radaccts radius_activesession)
  RETURNS void AS
$BODY$
DECLARE
    datetx_ text := to_char(trsr.date_start::date, 'YYYYMM01');
    insq_   text;
  radaccts_account_id text;
  radaccts_sessionid text;
  radaccts_interrim_update text;
  radaccts_date_start text;
  radaccts_date_end text;
  radaccts_caller_id text;
  radaccts_called_id text;
  radaccts_nas_id text;
  radaccts_session_time text;
  radaccts_framed_protocol text;
  radaccts_bytes_in text;
  radaccts_bytes_out text;
  radaccts_session_status text;
  radaccts_speed_string text;
  radaccts_framed_ip_address text;
  radaccts_nas_int_id text;
  radaccts_subaccount_id text;
  radaccts_acct_terminate_cause text;
  radaccts_lt_time text;
  radaccts_lt_bytes_in text;
  radaccts_lt_bytes_out text;
  radaccts_nas_port_id text;
  radaccts_ipinuse_id text;
BEGIN
    
  
    	IF radaccts.account_id IS NULL THEN
	   radaccts_account_id := 'NULL';
	ELSE
	   radaccts_account_id := radaccts.account_id::text;
	END IF;

	IF radaccts.sessionid IS NULL THEN
	   radaccts_sessionid := 'NULL';
	ELSE
	   radaccts_sessionid := quote_literal(radaccts.sessionid);
	END IF;

	IF radaccts.interrim_update IS NULL THEN
	   radaccts_interrim_update := 'NULL';
	ELSE
	   radaccts_interrim_update := quote_literal(radaccts.interrim_update);
	END IF;

	IF radaccts.date_start IS NULL THEN
	   radaccts_date_start := 'NULL';
	ELSE
	   radaccts_date_start := quote_literal(radaccts.date_start);
	END IF;

	IF radaccts.date_end IS NULL THEN
	   radaccts_date_end := 'NULL';
	ELSE
	   radaccts_date_end := quote_literal(radaccts.date_end);
	END IF;

	IF radaccts.caller_id IS NULL THEN
	   radaccts_caller_id := 'NULL';
	ELSE
	   radaccts_caller_id := quote_literal(radaccts.caller_id);
	END IF;

	IF radaccts.called_id IS NULL THEN
	   radaccts_called_id := 'NULL';
	ELSE
	   radaccts_called_id := quote_literal(radaccts.called_id);
	END IF;

    	IF radaccts.nas_id IS NULL THEN
	   radaccts_nas_id := 'NULL';
	ELSE
	   radaccts_nas_id := quote_literal(radaccts.nas_id);
	END IF;

	IF radaccts.session_time IS NULL THEN
	   radaccts_session_time := 'NULL';
	ELSE
	   radaccts_session_time := radaccts.session_time::text;
	END IF;

	IF radaccts.framed_protocol IS NULL THEN
	   radaccts_framed_protocol := 'NULL';
	ELSE
	   radaccts_framed_protocol := quote_literal(radaccts.framed_protocol);
	END IF;

	IF radaccts.bytes_in IS NULL THEN
	   radaccts_bytes_in := 'NULL';
	ELSE
	   radaccts_bytes_in := radaccts.bytes_in::text;
	END IF;

	IF radaccts.bytes_out IS NULL THEN
	   radaccts_bytes_out := 'NULL';
	ELSE
	   radaccts_bytes_out := radaccts.bytes_out::text;
	END IF;


	IF radaccts.session_status IS NULL THEN
	   radaccts_session_status := 'NULL';
	ELSE
	   radaccts_session_status := quote_literal(radaccts.session_status);
	END IF;

	IF radaccts.speed_string IS NULL THEN
	   radaccts_speed_string := 'NULL';
	ELSE
	   radaccts_speed_string := quote_literal(radaccts.speed_string);
	END IF;

	IF radaccts.framed_ip_address IS NULL THEN
	   radaccts_framed_ip_address := 'NULL';
	ELSE
	   radaccts_framed_ip_address := radaccts.framed_ip_address::text;
	END IF;

    	IF radaccts.nas_int_id IS NULL THEN
	   radaccts_nas_int_id := 'NULL';
	ELSE
	   radaccts_nas_int_id := radaccts.nas_int_id::text;
	END IF;

    	IF radaccts.subaccount_id IS NULL THEN
	   radaccts_subaccount_id := 'NULL';
	ELSE
	   radaccts_subaccount_id := radaccts.subaccount_id::text;
	END IF;


	IF radaccts.acct_terminate_cause IS NULL THEN
	   radaccts_acct_terminate_cause := 'NULL';
	ELSE
	   radaccts_acct_terminate_cause := quote_literal(radaccts.acct_terminate_cause);
	END IF;
	
	IF radaccts.lt_time IS NULL THEN
	   radaccts_lt_time := 'NULL';
	ELSE
	   radaccts_lt_time := quote_literal(radaccts.lt_time);
	END IF;


	
	IF radaccts.lt_bytes_in IS NULL THEN
	   radaccts_lt_bytes_in := 'NULL';
	ELSE
	   radaccts_lt_bytes_in := quote_literal(radaccts.lt_bytes_in);
	END IF;

	IF radaccts.lt_bytes_out IS NULL THEN
	   radaccts_lt_bytes_out := 'NULL';
	ELSE
	   radaccts_lt_bytes_out := quote_literal(radaccts.lt_bytes_out);
	END IF;

    	IF radaccts.nas_port_id IS NULL THEN
	   radaccts_nas_port_id := 'NULL';
	ELSE
	   radaccts_nas_port_id := radaccts.nas_port_id::text;
	END IF;

    	IF radaccts.ipinuse_id IS NULL THEN
	   radaccts_ipinuse_id := 'NULL';
	ELSE
	   radaccts_ipinuse_id := radaccts.ipinuse_id::text;
	END IF;
	
    insq_ := 'INSERT INTO radaccts' || datetx_ || ' (account_id, sessionid, interrim_update, date_start, date_end, caller_id, called_id, nas_id, session_time, framed_protocol, bytes_in, bytes_out, session_status, speed_string, framed_ip_address, nas_int_id, subaccount_id, acct_terminate_cause,lt_time,lt_bytes_in,lt_bytes_out, nas_port_id, ipinuse_id) VALUES (' || radaccts_account_id || ',' || radaccts_sessionid || ',' || radaccts_interrim_update || ',' || radaccts_date_start || ',' || radaccts_date_end || ',' || radaccts_caller_id || ',' || adaccts_called_id || ',' || radaccts_nas_id || ',' || radaccts_session_time || ',' || radaccts_framed_protocol || ',' || radaccts_bytes_in || ',' || radaccts_bytes_out || ',' || radaccts_session_status || ',' || radaccts_speed_string || ',' || radaccts_framed_ip_address || ',' || radaccts_nas_int_id || ',' || radaccts_subaccount_id || ',' || radaccts_acct_terminate_cause || ',' || radaccts_lt_time || ',' || radaccts_lt_bytes_in || ',' || radaccts_lt_bytes_out || ',' || radaccts_nas_port_id || ',' || radaccts_ipinuse_id ||');';
    EXECUTE insq_;
    RETURN;
END;$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION radius_activesession_inserter(radius_activesession) OWNER TO ebs;
