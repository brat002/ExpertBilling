CREATE OR REPLACE FUNCTION gpst_crt_pdb(datetx date)
  RETURNS integer AS
$BODY$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');
    datetx_e_ text := to_char((datetx + interval '1 month')::date, 'YYYYMM01');

    qt_dtx_ text;
    qt_dtx_e_ text;


    chk_tx1_ text := 'CHECK ( datetime >= DATE #stdtx# AND datetime < DATE #eddtx# )';
    ct_tx1_ text := 'CREATE TABLE gpst#rpdate# (
                     #chk#,
                     CONSTRAINT gpst#rpdate#_id_pkey PRIMARY KEY (id) ) 
                     INHERITS (billservice_groupstat) 
                     WITH (OIDS=FALSE);                     
                     CREATE INDEX gpst#rpdate#_datetime_id ON gpst#rpdate# USING btree (datetime);
                     CREATE INDEX gpst#rpdate#_gr_acc_dt_id ON gpst#rpdate# USING btree (group_id, account_id, datetime);
                     CREATE INDEX gpst#rpdate#_group_id ON gpst#rpdate# USING btree (group_id);
                     ';
                    

    chk_       text;
    ct_query_  text;
    at_query_  text;


BEGIN    


    qt_dtx_    := quote_literal(datetx_);
    qt_dtx_e_  := quote_literal(datetx_e_);
    chk_       := replace(chk_tx1_, '#stdtx#', qt_dtx_ );
    chk_       := replace(chk_, '#eddtx#', qt_dtx_e_ );
    ct_query_  := replace(ct_tx1_, '#rpdate#', datetx_);
    ct_query_  := replace(ct_query_, '#chk#', chk_);
    EXECUTE ct_query_;


    RETURN 0;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION gpst_crt_pdb(date) OWNER TO ebs;

DROP TRIGGER IF EXISTS gpst_del_trg ON billservice_groupstat;
DROP FUNCTION IF EXISTS  nfs_crt_cur_ins(date);
DROP FUNCTION IF EXISTS  nfs_crt_pdb(date);
DROP FUNCTION IF EXISTS  nfs_crt_prev_ins(date);
DROP FUNCTION IF EXISTS  nfs_cur_datechk(timestamp without time zone);
DROP FUNCTION IF EXISTS  nfs_cur_dt();
DROP FUNCTION IF EXISTS  nfs_cur_ins(billservice_netflowstream);
DROP FUNCTION IF EXISTS  nfs_inserter(billservice_netflowstream);
DROP FUNCTION IF EXISTS  nfs_prev_datechk(timestamp without time zone);
DROP FUNCTION IF EXISTS  nfs_prev_ins(billservice_netflowstream);

DROP TRIGGER IF EXISTS  billservice_tariff_trg ON billservice_tariff;

CREATE TRIGGER billservice_tariff_trg
  BEFORE DELETE
  ON billservice_tariff
  FOR EACH ROW
  EXECUTE PROCEDURE billservice_tariff_trg_fn();
  
DROP FUNCTION IF EXISTS  periodicaltr_fn(integer, integer, integer, character varying, numeric, timestamp without time zone, integer);

CREATE OR REPLACE FUNCTION periodicaltr_fn(ps_id_ integer, acctf_id_ integer, account_id_ integer, type_id_ character varying, summ_ numeric, created_ timestamp without time zone, ps_condition_type_ integer)
  RETURNS numeric AS
$BODY$
DECLARE
    new_summ_ decimal;
    pslog_id integer;
BEGIN
    SELECT INTO new_summ_ summ_*(NOT EXISTS (SELECT id FROM billservice_suspendedperiod WHERE account_id=account_id_ AND (created_ BETWEEN start_date AND end_date)))::int;
    IF (ps_condition_type_ = 1) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance+credit >= 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    ELSIF (ps_condition_type_ = 2) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance+credit < 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    ELSIF (ps_condition_type_ = 3) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance+credit > 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    END IF; 
    IF (new_summ_<>0) THEN 
      INSERT INTO billservice_periodicalservicehistory (service_id, accounttarif_id,account_id, type_id, summ, created) VALUES (ps_id_, acctf_id_, account_id_, type_id_, new_summ_, created_);
    END IF;
    SELECT INTO pslog_id id FROM billservice_periodicalservicelog WHERE service_id=ps_id_ and accounttarif_id=acctf_id_;
    IF (pslog_id is Null) THEN
      INSERT INTO billservice_periodicalservicelog(service_id, accounttarif_id, datetime) VALUES(ps_id_, acctf_id_, created_);
    ELSE
      UPDATE billservice_periodicalservicelog SET datetime=created_ WHERE id=pslog_id;  
    END IF;
    RETURN  new_summ_;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION periodicaltr_fn(integer, integer, integer, character varying, numeric, timestamp without time zone, integer) OWNER TO postgres;


DROP FUNCTION IF EXISTS psh_crt_pdb(date);

CREATE OR REPLACE FUNCTION psh_crt_pdb(datetx date)
  RETURNS integer AS
$BODY$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');
    datetx_e_ text := to_char((datetx + interval '1 month')::date, 'YYYYMM01');

    qt_dtx_ text;
    qt_dtx_e_ text;


    chk_tx1_ text := 'CHECK ( created >= DATE #stdtx# AND created < DATE #eddtx# )';
    ct_tx1_ text := 'CREATE TABLE psh#rpdate# (
                     #chk#,
                     CONSTRAINT psh#rpdate#_id_pkey PRIMARY KEY (id) ) 
                     INHERITS (billservice_periodicalservicehistory) 
                     WITH (OIDS=FALSE);                     
                     CREATE INDEX psh#rpdate#_created_id ON psh#rpdate# USING btree (created);
                     CREATE INDEX psh#rpdate#_service_id ON psh#rpdate# USING btree (service_id);
                     CREATE INDEX psh#rpdate#_accounttarif_id ON psh#rpdate# USING btree (accounttarif_id);
                     ';
                     

    chk_       text;
    seq_query_ text;
    ct_query_  text;
    seqn_      text;
    at_query_  text;


BEGIN    

    qt_dtx_    := quote_literal(datetx_);
    qt_dtx_e_  := quote_literal(datetx_e_);
    chk_       := replace(chk_tx1_, '#stdtx#', qt_dtx_ );
    chk_       := replace(chk_, '#eddtx#', qt_dtx_e_ );
    ct_query_  := replace(ct_tx1_, '#rpdate#', datetx_);
    ct_query_  := replace(ct_query_, '#chk#', chk_);
    EXECUTE ct_query_;

    RETURN 0;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION psh_crt_pdb(date) OWNER TO ebs;


CREATE OR REPLACE FUNCTION radius_activesession_trs_crt_pdb(datetx date)
  RETURNS integer AS
$BODY$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');
    datetx_e_ text := to_char((datetx + interval '1 month')::date, 'YYYYMM01');

    qt_dtx_ text;
    qt_dtx_e_ text;


    chk_tx1_ text := 'CHECK ( date_start >= DATE #stdtx# AND date_start < DATE #eddtx# )';
    ct_tx1_ text := 'CREATE TABLE radaccts#rpdate# (
                     #chk#,
                     CONSTRAINT radaccts#rpdate#_id_pkey PRIMARY KEY (id) ) 
                     INHERITS (radius_activesession) 
                     WITH (OIDS=FALSE);                     
                     CREATE INDEX radaccts#rpdate#_account_id ON radaccts#rpdate# USING btree (account_id);
                     CREATE INDEX radaccts#rpdate#_subaccount_id ON radaccts#rpdate# USING btree (subaccount_id);
                     CREATE INDEX radaccts#rpdate#_session_status ON radaccts#rpdate# USING btree (session_status);
                     ';

    chk_       text;
    seq_query_ text;
    ct_query_  text;
    seqn_      text;
    at_query_  text;


BEGIN    

    qt_dtx_    := quote_literal(datetx_);
    qt_dtx_e_  := quote_literal(datetx_e_);
    chk_       := replace(chk_tx1_, '#stdtx#', qt_dtx_ );
    chk_       := replace(chk_, '#eddtx#', qt_dtx_e_ );
    ct_query_  := replace(ct_tx1_, '#rpdate#', datetx_);
    ct_query_  := replace(ct_query_, '#chk#', chk_);
    EXECUTE ct_query_;

    RETURN 0;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION radius_activesession_trs_crt_pdb(date) OWNER TO postgres;

DROP FUNCTION IF EXISTS rsss_crt_cur_ins(date);
DROP FUNCTION IF EXISTS rsss_crt_pdb(date);
DROP FUNCTION IF EXISTS rsss_crt_prev_ins(date);
DROP FUNCTION IF EXISTS rsss_cur_datechk(timestamp without time zone);
DROP FUNCTION IF EXISTS rsss_cur_dt();
DROP FUNCTION IF EXISTS rsss_cur_ins(radius_session);
DROP FUNCTION IF EXISTS rsss_inserter(radius_session);
DROP FUNCTION IF EXISTS rsss_prev_datechk(timestamp without time zone);
DROP FUNCTION IF EXISTS rsss_prev_ins(radius_session);
DROP FUNCTION IF EXISTS timetransaction_insert(integer, integer, integer, numeric, timestamp without time zone, character varying, timestamp without time zone);

-- Function: psh_crt_cur_ins(date)

-- DROP FUNCTION psh_crt_cur_ins(date);

CREATE OR REPLACE FUNCTION psh_crt_cur_ins(datetx date)
  RETURNS void AS
$BODY$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION psh_cur_ins (pshr billservice_periodicalservicehistory) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO psh';
                         
    fn_bd_tx2_ text := '(service_id, account_id, accounttarif_id, type_id, summ, created)
                          VALUES 
                         (pshr.service_id, pshr.account_id, pshr.accounttarif_id, pshr.type_id, pshr.summ, pshr.created); RETURN; END;';
                          
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';


    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION psh_cur_datechk(psh_date timestamp without time zone) RETURNS integer AS ';

    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    psh_date < d_s_ THEN RETURN -1; ELSIF psh_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';



    dt_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION psh_cur_dt() RETURNS date AS ';
    
    onemonth_ text := '1 month';
    query_ text;
    
    prevdate_ date;
    
BEGIN    


    
        query_ :=  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;

        EXECUTE query_;


        query_ :=  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '+ interval ' || quote_literal(onemonth_) ||  ch_fn_bd_tx3_) || fn_tx2_;

        EXECUTE query_;
        
        prevdate_ := psh_cur_dt();
        
        PERFORM psh_crt_prev_ins(prevdate_);
        
        query_ := dt_fn_tx1_ || quote_literal(' BEGIN RETURN  DATE ' || quote_literal(datetx_) || '; END; ') || fn_tx2_;
        
        EXECUTE query_;

        
    RETURN;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION psh_crt_cur_ins(date) OWNER TO ebs;

-- Function: psh_crt_prev_ins(date)

-- DROP FUNCTION psh_crt_prev_ins(date);

CREATE OR REPLACE FUNCTION psh_crt_prev_ins(datetx date)
  RETURNS void AS
$BODY$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION psh_prev_ins (pshr billservice_periodicalservicehistory) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO psh';
                         
    fn_bd_tx2_ text := '(service_id, account_id, accounttarif_id,type_id, summ, created)
                          VALUES 
                         (pshr.service_id, pshr.account_id, pshr.accounttarif_id, pshr.type_id, pshr.summ, pshr.created); RETURN; END;';
                          
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';


    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION psh_prev_datechk(psh_date timestamp without time zone) RETURNS integer AS ';

    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    psh_date < d_s_ THEN RETURN -1; ELSIF psh_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';

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
ALTER FUNCTION psh_crt_prev_ins(date) OWNER TO ebs;

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

CREATE OR REPLACE FUNCTION traftrans_crt_pdb(datetx date)
  RETURNS integer AS
$BODY$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');
    datetx_e_ text := to_char((datetx + interval '1 month')::date, 'YYYYMM01');

    qt_dtx_ text;
    qt_dtx_e_ text;

    chk_tx1_ text := 'CHECK ( created >= DATE #stdtx# AND created < DATE #eddtx# )';
    ct_tx1_ text := 'CREATE TABLE traftrans#rpdate# (
                     #chk#,
                     CONSTRAINT traftrans#rpdate#_id_pkey PRIMARY KEY (id) ) 
                     INHERITS (billservice_traffictransaction) 
                     WITH (OIDS=FALSE);                     
                     CREATE INDEX traftrans#rpdate#_account_id ON traftrans#rpdate# USING btree (account_id);
                     CREATE TRIGGER acc_tftrans_trg AFTER UPDATE OR DELETE ON traftrans#rpdate# FOR EACH ROW EXECUTE PROCEDURE account_transaction_trg_fn();
                     ';
                     

    chk_       text;
    seq_query_ text;
    ct_query_  text;
    seqn_      text;
    at_query_  text;


BEGIN    

    qt_dtx_    := quote_literal(datetx_);
    qt_dtx_e_  := quote_literal(datetx_e_);
    chk_       := replace(chk_tx1_, '#stdtx#', qt_dtx_ );
    chk_       := replace(chk_, '#eddtx#', qt_dtx_e_ );
    ct_query_  := replace(ct_tx1_, '#rpdate#', datetx_);
    ct_query_  := replace(ct_query_, '#chk#', chk_);
    EXECUTE ct_query_;

    RETURN 0;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION traftrans_crt_pdb(date) OWNER TO postgres;

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

-- Function: traftrans_inserter(billservice_traffictransaction)

-- DROP FUNCTION traftrans_inserter(billservice_traffictransaction);

CREATE OR REPLACE FUNCTION traftrans_inserter(traftrns billservice_traffictransaction)
  RETURNS void AS
$BODY$
DECLARE
    datetx_ text := to_char(traftrns.created::date, 'YYYYMM01');
    insq_   text;

    traftrns_traffictransmitservice_id text;  
    traftrns_radiustraffictransmitservice_id text;
    traftrns_account_id    text;
    traftrns_accounttarif_id    text;
    traftrns_summ    text;
    traftrns_created    text;
BEGIN
    
IF traftrns.traffictransmitservice_id IS NULL THEN
   traftrns_traffictransmitservice_id := 'NULL';
ELSE
   traftrns_traffictransmitservice_id := traftrns.traffictransmitservice_id::text;
END IF;

  IF traftrns.radiustraffictransmitservice_id IS NULL THEN
   traftrns_radiustraffictransmitservice_id := 'NULL';
ELSE
   traftrns_radiustraffictransmitservice_id := traftrns.radiustraffictransmitservice_id::text;
END IF;


  IF traftrns.account_id IS NULL THEN
   traftrns_account_id := 'NULL';
ELSE
   traftrns_account_id := traftrns.account_id::text;
END IF;

    IF traftrns.accounttarif_id IS NULL THEN
   traftrns_accounttarif_id := 'NULL';
ELSE
   traftrns_accounttarif_id := traftrns.accounttarif_id::text;
END IF;

IF traftrns.summ IS NULL THEN
   traftrns_summ := 'NULL';
ELSE
   traftrns_summ := traftrns.summ::text;
END IF;


IF traftrns.created IS NULL THEN
   traftrns_created := 'NULL';
ELSE
   traftrns_created := quote_literal(traftrns.created);
END IF;

    insq_ := 'INSERT INTO traftrans' || datetx_ || ' (traffictransmitservice_id, radiustraffictransmitservice_id, account_id, accounttarif_id, summ, created) VALUES (' || traftrns_traffictransmitservice_id || ',' || traftrns_radiustraffictransmitservice_id || ',' || traftrns_account_id || ',' || traftrns_accounttarif_id || ',' || traftrns_summ || ',' || traftrns_created || ');';
    EXECUTE insq_;
    RETURN;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION traftrans_inserter(billservice_traffictransaction) OWNER TO postgres;

DROP FUNCTION IF EXISTS transaction_fn(character varying, integer, character varying, boolean, integer, double precision, text, timestamp without time zone, integer, integer, integer);
DROP FUNCTION IF EXISTS transaction_tarif(character varying, character varying, boolean, integer, double precision, text, timestamp without time zone, timestamp without time zone);

CREATE OR REPLACE FUNCTION trs_crt_pdb(datetx date)
  RETURNS integer AS
$BODY$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');
    datetx_e_ text := to_char((datetx + interval '1 month')::date, 'YYYYMM01');

    qt_dtx_ text;
    qt_dtx_e_ text;

    chk_tx1_ text := 'CHECK ( created >= DATE #stdtx# AND created < DATE #eddtx# )';
    ct_tx1_ text := 'CREATE TABLE trs#rpdate# (
                     #chk#,
                     CONSTRAINT trs#rpdate#_id_pkey PRIMARY KEY (id) ) 
                     INHERITS (billservice_transaction) 
                     WITH (OIDS=FALSE);                     
                     CREATE INDEX trs#rpdate#_created_id ON trs#rpdate# USING btree (created);
                     CREATE INDEX trs#rpdate#_systemuser_id ON trs#rpdate# USING btree (systemuser_id);
                     CREATE INDEX trs#rpdate#_tarif_id ON trs#rpdate# USING btree (tarif_id);
                     CREATE INDEX trs#rpdate#_account_id ON trs#rpdate# USING btree (account_id);
                     CREATE TRIGGER acc_trs_trg AFTER UPDATE OR DELETE ON trs#rpdate# FOR EACH ROW EXECUTE PROCEDURE account_transaction_trg_fn();
                     ';
                     

    chk_       text;
    seq_query_ text;
    ct_query_  text;
    seqn_      text;
    at_query_  text;


BEGIN    

    qt_dtx_    := quote_literal(datetx_);
    qt_dtx_e_  := quote_literal(datetx_e_);
    chk_       := replace(chk_tx1_, '#stdtx#', qt_dtx_ );
    chk_       := replace(chk_, '#eddtx#', qt_dtx_e_ );
    ct_query_  := replace(ct_tx1_, '#rpdate#', datetx_);
    ct_query_  := replace(ct_query_, '#chk#', chk_);
    EXECUTE ct_query_;
    RETURN 0;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION trs_crt_pdb(date) OWNER TO ebs;

ALTER TABLE billservice_timespeed DROP CONSTRAINT billservice_timespeed_time_id_fkey;

ALTER TABLE billservice_timespeed
  ADD CONSTRAINT billservice_timespeed_time_id_fkey FOREIGN KEY (time_id)
      REFERENCES billservice_timeperiod (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL DEFERRABLE INITIALLY IMMEDIATE;
      
DROP TRIGGER IF EXISTS return_ipinuse_to_pool_trg ON radius_activesession;      
DROP FUNCTION IF EXISTS return_ipinuse_to_pool_trg_fn();

ALTER TABLE radius_activesession DROP CONSTRAINT account_id_refs_id_16c70393;

DROP TABLE IF EXISTS radius_session;
