CREATE OR REPLACE FUNCTION nfs_cur_dt()
  RETURNS date AS
$BODY$ BEGIN RETURN date '19700101'; END;$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
ALTER FUNCTION nfs_cur_dt() OWNER TO ebs;

------------------------------------------------------------------------------


CREATE OR REPLACE FUNCTION nfs_cur_datechk(nfs_date timestamp without time zone)
  RETURNS integer AS
$BODY$ DECLARE d_s_ date := DATE '19700101'; d_e_ date := (DATE '19700101'+ interval '1 day')::date; BEGIN IF    nfs_date < d_s_ THEN RETURN -1; ELSIF nfs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
ALTER FUNCTION nfs_cur_datechk(timestamp without time zone) OWNER TO ebs;

------------------------------------------------------------------------------


CREATE OR REPLACE FUNCTION nfs_cur_ins(nfsr billservice_netflowstream)
  RETURNS void AS
$BODY$
DECLARE

BEGIN	
      return;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
ALTER FUNCTION nfs_prev_ins(billservice_netflowstream) OWNER TO ebs;

------------------------------------------------------------------------------


CREATE OR REPLACE FUNCTION nfs_prev_datechk(nfs_date timestamp without time zone)
  RETURNS integer AS
$BODY$ DECLARE d_s_ date := DATE '19700101'; d_e_ date := (DATE '19700101'+ interval '1 day')::date; BEGIN IF    nfs_date < d_s_ THEN RETURN -1; ELSIF nfs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
ALTER FUNCTION nfs_cur_datechk(timestamp without time zone) OWNER TO ebs;

------------------------------------------------------------------------------


CREATE OR REPLACE FUNCTION nfs_prev_ins(nfsr billservice_netflowstream)
  RETURNS void AS
$BODY$
DECLARE

BEGIN	
      return;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
ALTER FUNCTION nfs_prev_ins(billservice_netflowstream) OWNER TO ebs;

------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION nfs_crt_cur_ins(datetx date)
  RETURNS void AS
$BODY$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMMDD');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION nfs_cur_ins (nfsr billservice_netflowstream) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO nfs';
                         
    fn_bd_tx2_ text := '(nas_id, account_id, tarif_id, date_start, src_addr, traffic_class_id, direction, traffic_transmit_node_id, dst_addr, octets, src_port, dst_port, protocol, checkouted, for_checkout)
                          VALUES 
                         (nfsr.nas_id, nfsr.account_id, nfsr.tarif_id, nfsr.date_start, nfsr.src_addr, 
                          nfsr.traffic_class_id, nfsr.direction, nfsr.traffic_transmit_node_id, nfsr.dst_addr, nfsr.octets, nfsr.src_port, 
                          nfsr.dst_port, nfsr.protocol, nfsr.checkouted, nfsr.for_checkout); RETURN; END;';
                          
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';


    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION nfs_cur_datechk(nfs_date timestamp without time zone) RETURNS integer AS ';

    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    nfs_date < d_s_ THEN RETURN -1; ELSIF nfs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';

    --ch_fn_tx2_ text := ' LANGUAGE plpgsql VOLATILE COST 100;';


	dt_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION nfs_cur_dt() RETURNS date AS ';
	
    oneday_ text := '1 day';
    query_ text;
    
    prevdate_ date;
    
BEGIN	

        --DROP FUNCTION IF EXISTS nfs_prev_ins(billservice_netflowstream);
        --ALTER FUNCTION nfs_cur_ins(billservice_netflowstream) RENAME TO nfs_prev_ins;

	--DROP FUNCTION IF EXISTS nfs_cur_ins(billservice_netflowstream);
	
        query_ :=  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;

        EXECUTE query_;

        --raise warning 'q1 %', query_;
	--DROP FUNCTION IF EXISTS nfs_prev_datechk(timestamp without time zone);
	--DROP FUNCTION IF EXISTS nfs_cur_datechk(billservice_netflowstream);
        --ALTER FUNCTION nfs_cur_datechk(timestamp without time zone) RENAME TO nfs_prev_datechk;

        query_ :=  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '+ interval ' || quote_literal(oneday_) ||  ch_fn_bd_tx3_) || fn_tx2_;

        EXECUTE query_;
        
        prevdate_ := nfs_cur_dt();
        
        PERFORM nfs_crt_prev_ins(prevdate_);
        
        query_ := dt_fn_tx1_ || quote_literal(' BEGIN RETURN  DATE ' || quote_literal(datetx_) || '; END; ') || fn_tx2_;
        
        EXECUTE query_;

        --raise warning 'q1 %', query_;
        
	RETURN;

END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
ALTER FUNCTION nfs_crt_cur_ins(date) OWNER TO ebs;

------------------------------------------------------------------------------


CREATE OR REPLACE FUNCTION nfs_crt_pdb(datetx date)
  RETURNS integer AS
$BODY$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMMDD');
    datetx_e_ text := to_char((datetx + interval '1 day')::date, 'YYYYMMDD');

    qt_dtx_ text;
    qt_dtx_e_ text;
    seq_tx1_ text := 'CREATE SEQUENCE nfs#rpdate#_id_seq
                      INCREMENT 1
                      MINVALUE 1
                      MAXVALUE 9223372036854775807
                      START 1
                      CACHE 1;';
    seqname_tx1_ text := 'nfs#rpdate#_id_seq';

    chk_tx1_ text := 'CHECK ( date_start >= DATE #stdtx# AND date_start < DATE #eddtx# )';
    ct_tx1_ text := 'CREATE TABLE nfs#rpdate# (
                     #chk#,
                     CONSTRAINT nfs#rpdate#_id_pkey PRIMARY KEY (id) ) 
                     INHERITS (billservice_netflowstream) 
                     WITH (OIDS=FALSE);
                     CREATE INDEX nfs#rpdate#_account_id ON nfs#rpdate# USING btree (account_id);
                     CREATE INDEX nfs#rpdate#_date_start_id ON nfs#rpdate# USING btree (date_start);
                     CREATE INDEX nfs#rpdate#_nas_id ON nfs#rpdate# USING btree (nas_id);
                     CREATE INDEX nfs#rpdate#_tarif_id ON nfs#rpdate# USING btree (tarif_id);
                     CREATE INDEX nfs#rpdate#_traffic_class_id ON nfs#rpdate# USING btree (traffic_class_id);
                     CREATE INDEX nfs#rpdate#_traffic_transmit_node_id ON nfs#rpdate# USING btree (traffic_transmit_node_id);';
                     
    at_tx1_ text := 'ALTER TABLE nfs#rpdate# ALTER COLUMN id SET DEFAULT nextval(#qseqname#::regclass);';

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
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
ALTER FUNCTION nfs_crt_pdb(date) OWNER TO ebs;

------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION nfs_crt_prev_ins(datetx date)
  RETURNS void AS
$BODY$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMMDD');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION nfs_prev_ins (nfsr billservice_netflowstream) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO nfs';
                         
    fn_bd_tx2_ text := '(nas_id, account_id, tarif_id, date_start, src_addr, traffic_class_id, direction, traffic_transmit_node_id, dst_addr, octets, src_port, dst_port, protocol, checkouted, for_checkout)
                          VALUES 
                         (nfsr.nas_id, nfsr.account_id, nfsr.tarif_id, nfsr.date_start, nfsr.src_addr, 
                          nfsr.traffic_class_id, nfsr.direction, nfsr.traffic_transmit_node_id, nfsr.dst_addr, nfsr.octets, nfsr.src_port, 
                          nfsr.dst_port, nfsr.protocol, nfsr.checkouted, nfsr.for_checkout); RETURN; END;';
                          
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';


    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION nfs_prev_datechk(nfs_date timestamp without time zone) RETURNS integer AS ';

    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    ch_fn_bd_tx2_ text := '; d_e_ date := DATE ';
    ch_fn_bd_tx3_ text := 'IF    nfs_date < d_s_ THEN RETURN -1; ELSIF nfs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';

    ch_fn_tx2_ text := ' LANGUAGE plpgsql VOLATILE COST 100;';

    qts_ text := 'CHK % % %';
BEGIN	

        --DROP FUNCTION IF EXISTS nfs_prev_ins(billservice_netflowstream);
        --ALTER FUNCTION nfs_cur_ins(billservice_netflowstream) RENAME TO nfs_prev_ins;

        EXECUTE  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;

	--DROP FUNCTION IF EXISTS nfs_prev_datechk(timestamp without time zone);
        --ALTER FUNCTION nfs_cur_datechk(timestamp without time zone) RENAME TO nfs_prev_datechk;

        EXECUTE  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '; BEGIN ' || ch_fn_bd_tx3_) || ch_fn_tx2_;
        --|| 'raise warning ' || quote_literal(qts) || ', d_s_, d_e_, nfs_date; '
        
	RETURN;

END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
ALTER FUNCTION nfs_crt_prev_ins(date) OWNER TO ebs;


------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION nfs_inserter(nfsr billservice_netflowstream)
  RETURNS void AS
$BODY$
DECLARE
    datetx_ text := to_char(nfsr.date_start::date, 'YYYYMMDD');
    insq_   text;

    ttrn_id_ text;

    
BEGIN
    --ttrn_id_    := nfsr.traffic_transmit_node_id;
    
    IF nfsr.traffic_transmit_node_id IS NULL THEN
       ttrn_id_ := 'NULL';
    ELSE
       ttrn_id_ := nfsr.traffic_transmit_node_id::text;
    END IF;
    insq_ := 'INSERT INTO nfs' || datetx_ || ' (nas_id, account_id, tarif_id, date_start, src_addr, traffic_class_id, direction, traffic_transmit_node_id, dst_addr, octets, src_port, dst_port, protocol, checkouted, for_checkout) VALUES (' 
    || nfsr.nas_id || ',' || nfsr.account_id || ','  || nfsr.tarif_id || ','  || quote_literal(nfsr.date_start) || ','  || quote_literal(nfsr.src_addr) || ','  || quote_literal(nfsr.traffic_class_id) || ','  || quote_literal(nfsr.direction) || ','  || ttrn_id_ || ','  || quote_literal(nfsr.dst_addr) || ','  || nfsr.octets || ','  || nfsr.src_port || ','  || nfsr.dst_port || ','  || nfsr.protocol || ','  || nfsr.checkouted || ','  || nfsr.for_checkout || ');';
    --raise warning '%', insq_;
    EXECUTE insq_;
    RETURN;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
ALTER FUNCTION nfs_inserter(billservice_netflowstream) OWNER TO ebs;

------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION nfs_ins_trg_fn()
  RETURNS trigger AS
$BODY$
DECLARE
    cur_chk int;
    prev_chk int;
BEGIN
    cur_chk := nfs_cur_datechk(NEW.date_start);

    --raise warning 'new check %d %s', cur_chk, NEW.date_start::date;
    IF cur_chk = 0 THEN
        PERFORM nfs_cur_ins(NEW);
    ELSIF cur_chk = 1 THEN
        BEGIN
            PERFORM nfs_crt_pdb(NEW.date_start::date);
            PERFORM nfs_crt_cur_ins(NEW.date_start::date);
            EXECUTE nfs_cur_ins(NEW);
        EXCEPTION 
          WHEN duplicate_table THEN
             PERFORM nfs_crt_cur_ins(NEW.date_start::date);
             EXECUTE nfs_cur_ins(NEW);
        END;
        --raise warning 'create pdb %s', NEW.date_start::date;
        
        --execute pg_sleep(5);
        
    ELSE 
        prev_chk := nfs_prev_datechk(NEW.date_start);
        IF prev_chk = 0 THEN
            PERFORM nfs_prev_ins(NEW);
        ELSE
            BEGIN 
                PERFORM nfs_inserter(NEW);
            EXCEPTION 
              WHEN undefined_table THEN
                PERFORM nfs_crt_pdb(NEW.date_start::date);
                PERFORM nfs_inserter(NEW);
            END;
            --raise warning 'create pdb %s', NEW.date_start::date;
            --PERFORM nfs_inserter(NEW);
        END IF;      
    END IF;
    RETURN NULL;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
ALTER FUNCTION nfs_ins_trg_fn() OWNER TO ebs;


------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION del_nfs_trg_fn()
  RETURNS trigger AS
$BODY$
    BEGIN
        INSERT INTO billservice_netflowstream (nas_id, account_id, tarif_id, date_start, src_addr, traffic_class_id, 
            direction, traffic_transmit_node_id, dst_addr, octets, src_port, 
            dst_port, protocol, checkouted, for_checkout) VALUES( OLD.nas_id, OLD.account_id, OLD.tarif_id, OLD.date_start, OLD.src_addr, 
            OLD.traffic_class_id, OLD.direction, OLD.traffic_transmit_node_id, OLD.dst_addr, OLD.octets, OLD.src_port, 
            OLD.dst_port, OLD.protocol, OLD.checkouted, OLD.for_checkout);
        RETURN OLD;
    END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
ALTER FUNCTION del_nfs_trg_fn() OWNER TO ebs;

------------------------------------------------------------------------------

CREATE TRIGGER del_nfs_trg
  AFTER DELETE
  ON billservice_netflowstream
  FOR EACH ROW
  EXECUTE PROCEDURE del_nfs_trg_fn();


------------------------------------------------------------------------------

CREATE TRIGGER ins_nfs_trg
  BEFORE INSERT
  ON billservice_netflowstream
  FOR EACH ROW
  EXECUTE PROCEDURE nfs_ins_trg_fn();
  
------------------------------------------------------------------------------