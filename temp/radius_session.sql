DROP INDEX radius_session_account_id;

CREATE OR REPLACE FUNCTION rsss_del_trg_fn() RETURNS trigger
    AS $$
    BEGIN
        INSERT INTO radius_session (account_id, sessionid, interrim_update, date_start, date_end, caller_id, called_id, nas_id, session_time, framed_protocol, bytes_in, bytes_out, checkouted_by_time, checkouted_by_trafic, disconnect_status, framed_ip_address) VALUES( OLD.account_id, OLD.sessionid, OLD.interrim_update, OLD.date_start, OLD.date_end, OLD.caller_id, OLD.called_id, OLD.nas_id, OLD.session_time, OLD.framed_protocol, OLD.bytes_in, OLD.bytes_out, OLD.checkouted_by_time, OLD.checkouted_by_trafic, OLD.disconnect_status, OLD.framed_ip_address);
        RETURN OLD;
    END;
$$
    LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION rsss_crt_cur_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION rsss_cur_ins (rsssr radius_session) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO rsss';
                         
    fn_bd_tx2_ text := '(account_id, sessionid, interrim_update, date_start, date_end, caller_id, called_id, nas_id, session_time, framed_protocol, bytes_in, bytes_out, checkouted_by_time, checkouted_by_trafic, disconnect_status, framed_ip_address)
                          VALUES 
                         (rsssr.account_id, rsssr.sessionid, rsssr.interrim_update, rsssr.date_start, rsssr.date_end, rsssr.caller_id, rsssr.called_id, rsssr.nas_id, rsssr.session_time, rsssr.framed_protocol, rsssr.bytes_in, rsssr.bytes_out, rsssr.checkouted_by_time, rsssr.checkouted_by_trafic, rsssr.disconnect_status, rsssr.framed_ip_address); RETURN; END;';
                          
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';


    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION rsss_cur_datechk(rsss_date timestamp without time zone) RETURNS integer AS ';

    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    rsss_date < d_s_ THEN RETURN -1; ELSIF rsss_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';



    dt_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION rsss_cur_dt() RETURNS date AS ';
    
    onemonth_ text := '1 month';
    query_ text;
    
    prevdate_ date;
    
BEGIN    


    
        query_ :=  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;

        EXECUTE query_;


        query_ :=  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '+ interval ' || quote_literal(onemonth_) ||  ch_fn_bd_tx3_) || fn_tx2_;

        EXECUTE query_;
        
        prevdate_ := rsss_cur_dt();
        
        PERFORM rsss_crt_prev_ins(prevdate_);
        
        query_ := dt_fn_tx1_ || quote_literal(' BEGIN RETURN  DATE ' || quote_literal(datetx_) || '; END; ') || fn_tx2_;
        
        EXECUTE query_;

        
    RETURN;

END;
$$
    LANGUAGE plpgsql;




CREATE OR REPLACE FUNCTION rsss_crt_pdb(datetx date) RETURNS integer
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');
    datetx_e_ text := to_char((datetx + interval '1 month')::date, 'YYYYMM01');

    qt_dtx_ text;
    qt_dtx_e_ text;
    seq_tx1_ text := 'CREATE SEQUENCE rsss#rpdate#_id_seq
                      INCREMENT 1
                      MINVALUE 1
                      MAXVALUE 9223372036854775807
                      START 1
                      CACHE 1;';
    seqname_tx1_ text := 'rsss#rpdate#_id_seq';

    chk_tx1_ text := 'CHECK ( interrim_update >= DATE #stdtx# AND interrim_update < DATE #eddtx# )';
    ct_tx1_ text := 'CREATE TABLE rsss#rpdate# (
                     #chk#,
                     CONSTRAINT rsss#rpdate#_id_pkey PRIMARY KEY (id) ) 
                     INHERITS (radius_session) 
                     WITH (OIDS=FALSE);                     
                     CREATE INDEX rsss#rpdate#_interrim_update_id ON rsss#rpdate# USING btree (interrim_update);
                     CREATE INDEX rsss#rpdate#_account_id ON rsss#rpdate# USING btree (account_id);
                     ';
                     
    at_tx1_ text := 'ALTER TABLE rsss#rpdate# ALTER COLUMN id SET DEFAULT nextval(#qseqname#::regclass);';

    chk_       text;
    seq_query_ text;
    ct_query_  text;
    seqn_      text;
    at_query_  text;


BEGIN    
    seq_query_ := replace(seq_tx1_, '#rpdate#', datetx_);
    EXECUTE seq_query_;
    qt_dtx_    := quote_literal(datetx_);
    qt_dtx_e_  := quote_literal(datetx_e_);
    chk_       := replace(chk_tx1_, '#stdtx#', qt_dtx_ );
    chk_       := replace(chk_, '#eddtx#', qt_dtx_e_ );
    ct_query_  := replace(ct_tx1_, '#rpdate#', datetx_);
    ct_query_  := replace(ct_query_, '#chk#', chk_);
    EXECUTE ct_query_;
    seqn_        := replace(seqname_tx1_, '#rpdate#', datetx_);
    at_query_    := replace(at_tx1_, '#rpdate#', datetx_);
    at_query_    := replace(at_query_, '#qseqname#', quote_literal(seqn_));
    EXECUTE at_query_;
    RETURN 0;

END;
$$
    LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION rsss_crt_prev_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION rsss_prev_ins (rsssr radius_session) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO rsss';
                         
    fn_bd_tx2_ text := '(account_id, sessionid, interrim_update, date_start, date_end, caller_id, called_id, nas_id, session_time, framed_protocol, bytes_in, bytes_out, checkouted_by_time, checkouted_by_trafic, disconnect_status, framed_ip_address)
                          VALUES 
                         (rsssr.account_id, rsssr.sessionid, rsssr.interrim_update, rsssr.date_start, rsssr.date_end, rsssr.caller_id, rsssr.called_id, rsssr.nas_id, rsssr.session_time, rsssr.framed_protocol, rsssr.bytes_in, rsssr.bytes_out, rsssr.checkouted_by_time, rsssr.checkouted_by_trafic, rsssr.disconnect_status, rsssr.framed_ip_address); RETURN; END;';
                          
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';


    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION rsss_prev_datechk(rsss_date timestamp without time zone) RETURNS integer AS ';

    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    rsss_date < d_s_ THEN RETURN -1; ELSIF rsss_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';

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
$$
    LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION rsss_cur_datechk(rsss_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700201'; d_e_ date := (DATE '19700201'+ interval '1 month')::date; BEGIN IF    rsss_date < d_s_ THEN RETURN -1; ELSIF rsss_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION rsss_cur_dt() RETURNS date
    AS $$ BEGIN RETURN  DATE '19700201'; END; $$
    LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION rsss_cur_ins(rsssr radius_session) RETURNS void
    AS $$BEGIN 
                         RETURN; END;$$
    LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION rsss_ins_trg_fn() RETURNS trigger
    AS $$
DECLARE
    cur_chk int;
    prev_chk int;
BEGIN
    cur_chk := rsss_cur_datechk(NEW.interrim_update);

    IF cur_chk = 0 THEN
        PERFORM rsss_cur_ins(NEW);
    ELSIF cur_chk = 1 THEN
        BEGIN
            PERFORM rsss_crt_pdb(NEW.interrim_update::date);
            PERFORM rsss_crt_cur_ins(NEW.interrim_update::date);
            EXECUTE rsss_cur_ins(NEW);
        EXCEPTION 
          WHEN duplicate_table THEN
             PERFORM rsss_crt_cur_ins(NEW.interrim_update::date);
             EXECUTE rsss_cur_ins(NEW);
        END;
        
        
    ELSE 
        prev_chk := rsss_prev_datechk(NEW.interrim_update);
        IF prev_chk = 0 THEN
            PERFORM rsss_prev_ins(NEW);
        ELSE
            BEGIN 
                PERFORM rsss_inserter(NEW);
            EXCEPTION 
              WHEN undefined_table THEN
                PERFORM rsss_crt_pdb(NEW.interrim_update::date);
                PERFORM rsss_inserter(NEW);
            END;
        END IF;      
    END IF;
    RETURN NULL;
END;
$$
    LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION rsss_inserter(rsssr radius_session) RETURNS void
    AS $$
DECLARE
    datetx_ text := to_char(rsssr.interrim_update::date, 'YYYYMM01');
    insq_   text;

  
    ttrn_sessionid_ text; 
    ttrn_interrim_update_ text; 
    ttrn_date_start_ text; 
    ttrn_date_end_ text; 
    ttrn_caller_id_ text; 
    ttrn_called_id_ text; 
    ttrn_session_time_ int;
    ttrn_bytes_in_ int; 
    ttrn_bytes_out_ int; 
    ttrn_checkouted_by_time_ boolean; 
    ttrn_checkouted_by_trafic_ boolean; 
    ttrn_disconnect_status_ text; 
    ttrn_framed_ip_address_ text;  
BEGIN
    
    IF rsssr.sessionid IS NULL THEN
       ttrn_sessionid_ := quote_literal('');
    ELSE
       ttrn_sessionid_ := quote_literal(rsssr.sessionid);
    END IF;
    IF rsssr.interrim_update IS NULL THEN
       ttrn_interrim_update_ := quote_literal(now()::timestamp without time zone);
    ELSE
       ttrn_interrim_update_ := quote_literal(rsssr.interrim_update);
    END IF;
    IF rsssr.date_start IS NULL THEN
       ttrn_date_start_ := 'NULL';
    ELSE
       ttrn_date_start_ := quote_literal(rsssr.date_start);
    END IF;
    IF rsssr.date_end IS NULL THEN
       ttrn_date_end_ := 'NULL';
    ELSE
       ttrn_date_end_ := quote_literal(rsssr.date_end);
    END IF;
    IF rsssr.caller_id IS NULL THEN
       ttrn_caller_id_ := quote_literal('');
    ELSE
       ttrn_caller_id_ := quote_literal(rsssr.caller_id);
    END IF;
    IF rsssr.called_id IS NULL THEN
       ttrn_called_id_ := quote_literal('');
    ELSE
       ttrn_called_id_ := quote_literal(rsssr.called_id);
    END IF;
    IF rsssr.session_time IS NULL THEN
       ttrn_session_time_ := 0;
    ELSE
       ttrn_session_time_ := rsssr.session_time;
    END IF;
    IF rsssr.bytes_in IS NULL THEN
       ttrn_bytes_in_ := 0;
    ELSE
       ttrn_bytes_in_ := rsssr.bytes_in;
    END IF;
    IF rsssr.bytes_out IS NULL THEN
       ttrn_bytes_out_ := 0;
    ELSE
       ttrn_bytes_out_ := rsssr.bytes_out;
    END IF;
    IF rsssr.checkouted_by_time IS NULL THEN
       ttrn_checkouted_by_time_ := FALSE;
    ELSE
       ttrn_checkouted_by_time_ := rsssr.checkouted_by_time;
    END IF;
    IF rsssr.checkouted_by_trafic IS NULL THEN
       ttrn_checkouted_by_trafic_ := FALSE;
    ELSE
       ttrn_checkouted_by_trafic_ := rsssr.checkouted_by_trafic;
    END IF;    
    IF rsssr.disconnect_status IS NULL THEN
       ttrn_disconnect_status_ := 'NULL';
    ELSE
       ttrn_disconnect_status_ := quote_literal(rsssr.disconnect_status);
    END IF;
    IF rsssr.framed_ip_address IS NULL THEN
       ttrn_framed_ip_address_ := 'NULL';
    ELSE
       ttrn_framed_ip_address_ := quote_literal(rsssr.framed_ip_address);
    END IF;
    --check quote literal

    insq_ := 'INSERT INTO rsss' || datetx_ || ' (account_id, sessionid, interrim_update, date_start, date_end, caller_id, called_id, nas_id, session_time, framed_protocol, bytes_in, bytes_out, checkouted_by_time, checkouted_by_trafic, disconnect_status, framed_ip_address) VALUES ('  || rsssr.account_id || ','  || ttrn_sessionid_ || ',' || ttrn_interrim_update_ || ',' || ttrn_date_start_ || ',' || ttrn_date_end_  || ',' ||  ttrn_caller_id_ || ','  || ttrn_called_id_ || ',' || quote_literal(rsssr.nas_id) || ',' || ttrn_session_time_ || ',' || quote_literal(rsssr.framed_protocol) || ',' || ttrn_bytes_in_ || ',' || ttrn_bytes_out_ || ',' || ttrn_checkouted_by_time_ || ',' || ttrn_checkouted_by_trafic_ || ',' || ttrn_disconnect_status_ || ',' || ttrn_framed_ip_address_ || ');';
    EXECUTE insq_;
    RETURN;
END;
$$
    LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION rsss_prev_datechk(rsss_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700101'; d_e_ date := (DATE '19700101'+ interval '1 month')::date; BEGIN IF    rsss_date < d_s_ THEN RETURN -1; ELSIF rsss_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION rsss_prev_ins(rsssr radius_session) RETURNS void
    AS $$BEGIN 
                          RETURN; END;$$
    LANGUAGE plpgsql;
    
    
CREATE TRIGGER rsss_del_trg
    AFTER DELETE ON radius_session
    FOR EACH ROW
    EXECUTE PROCEDURE rsss_del_trg_fn();


CREATE TRIGGER rsss_ins_trg
    BEFORE INSERT ON radius_session
    FOR EACH ROW
    EXECUTE PROCEDURE rsss_ins_trg_fn();