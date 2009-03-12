CREATE TABLE billservice_transaction (
    id integer NOT NULL,
    bill character varying(255),
    account_id integer NOT NULL,
    type_id character varying,
    approved boolean,
    tarif_id integer,
    summ double precision,
    description text,
    created timestamp without time zone
);


CREATE TABLE billservice_groupstat (
    id integer NOT NULL,
    group_id integer NOT NULL,
    account_id integer NOT NULL,
    bytes integer NOT NULL,
    datetime timestamp without time zone NOT NULL,
    classes integer[],
    classbytes integer[],
    max_class integer
);

CREATE TRIGGER del_nfs_trg
    AFTER DELETE ON billservice_netflowstream
    FOR EACH ROW
    EXECUTE PROCEDURE del_nfs_trg_fn();


CREATE TRIGGER ins_nfs_trg
    BEFORE INSERT ON billservice_netflowstream
    FOR EACH ROW
    EXECUTE PROCEDURE nfs_ins_trg_fn();

CREATE FUNCTION del_nfs_trg_fn() RETURNS trigger
    AS $$
    BEGIN
        INSERT INTO billservice_netflowstream (nas_id, account_id, tarif_id, date_start, src_addr, traffic_class_id, 
            direction, traffic_transmit_node_id, dst_addr, octets, src_port, 
            dst_port, protocol, checkouted, for_checkout) VALUES( OLD.nas_id, OLD.account_id, OLD.tarif_id, OLD.date_start, OLD.src_addr, 
            OLD.traffic_class_id, OLD.direction, OLD.traffic_transmit_node_id, OLD.dst_addr, OLD.octets, OLD.src_port, 
            OLD.dst_port, OLD.protocol, OLD.checkouted, OLD.for_checkout);
        RETURN OLD;
    END;
$$
    LANGUAGE plpgsql;


CREATE FUNCTION nfs_crt_cur_ins(datetx date) RETURNS void
    AS $$
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



    dt_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION nfs_cur_dt() RETURNS date AS ';
    
    oneday_ text := '1 day';
    query_ text;
    
    prevdate_ date;
    
BEGIN    


    
        query_ :=  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;

        EXECUTE query_;


        query_ :=  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '+ interval ' || quote_literal(oneday_) ||  ch_fn_bd_tx3_) || fn_tx2_;

        EXECUTE query_;
        
        prevdate_ := nfs_cur_dt();
        
        PERFORM nfs_crt_prev_ins(prevdate_);
        
        query_ := dt_fn_tx1_ || quote_literal(' BEGIN RETURN  DATE ' || quote_literal(datetx_) || '; END; ') || fn_tx2_;
        
        EXECUTE query_;

        
    RETURN;

END;
$$
    LANGUAGE plpgsql;




CREATE FUNCTION nfs_crt_pdb(datetx date) RETURNS integer
    AS $$
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
                     CREATE INDEX nfs#rpdate#_date_start_id ON nfs#rpdate# USING btree (date_start);
                     ';
                     
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
$$
    LANGUAGE plpgsql;



CREATE FUNCTION nfs_crt_prev_ins(datetx date) RETURNS void
    AS $$
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

        EXECUTE  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;


        EXECUTE  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '; BEGIN ' || ch_fn_bd_tx3_) || ch_fn_tx2_;
        
    RETURN;

END;
$$
    LANGUAGE plpgsql;

CREATE FUNCTION nfs_cur_datechk(nfs_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '20090223'; d_e_ date := (DATE '20090223'+ interval '1 day')::date; BEGIN IF    nfs_date < d_s_ THEN RETURN -1; ELSIF nfs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;


CREATE FUNCTION nfs_cur_dt() RETURNS date
    AS $$ BEGIN RETURN  DATE '20090223'; END; $$
    LANGUAGE plpgsql;


CREATE FUNCTION nfs_cur_ins(nfsr billservice_netflowstream) RETURNS void
    AS $$BEGIN 
                         INSERT INTO nfs20090223(nas_id, account_id, tarif_id, date_start, src_addr, traffic_class_id, direction, traffic_transmit_node_id, dst_addr, octets, src_port, dst_port, protocol, checkouted, for_checkout)
                          VALUES 
                         (nfsr.nas_id, nfsr.account_id, nfsr.tarif_id, nfsr.date_start, nfsr.src_addr, 
                          nfsr.traffic_class_id, nfsr.direction, nfsr.traffic_transmit_node_id, nfsr.dst_addr, nfsr.octets, nfsr.src_port, 
                          nfsr.dst_port, nfsr.protocol, nfsr.checkouted, nfsr.for_checkout); RETURN; END;$$
    LANGUAGE plpgsql;


CREATE FUNCTION nfs_ins_trg_fn() RETURNS trigger
    AS $$
DECLARE
    cur_chk int;
    prev_chk int;
BEGIN
    cur_chk := nfs_cur_datechk(NEW.date_start);

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
        END IF;      
    END IF;
    RETURN NULL;
END;
$$
    LANGUAGE plpgsql;


CREATE FUNCTION nfs_inserter(nfsr billservice_netflowstream) RETURNS void
    AS $$
DECLARE
    datetx_ text := to_char(nfsr.date_start::date, 'YYYYMMDD');
    insq_   text;

    ttrn_id_ text;    
BEGIN
    
    IF nfsr.traffic_transmit_node_id IS NULL THEN
       ttrn_id_ := 'NULL';
    ELSE
       ttrn_id_ := nfsr.traffic_transmit_node_id::text;
    END IF;
    insq_ := 'INSERT INTO nfs' || datetx_ || ' (nas_id, account_id, tarif_id, date_start, src_addr, traffic_class_id, direction, traffic_transmit_node_id, dst_addr, octets, src_port, dst_port, protocol, checkouted, for_checkout) VALUES (' 
    || nfsr.nas_id || ',' || nfsr.account_id || ','  || nfsr.tarif_id || ','  || quote_literal(nfsr.date_start) || ','  || quote_literal(nfsr.src_addr) || ','  || quote_literal(nfsr.traffic_class_id) || ','  || quote_literal(nfsr.direction) || ','  || ttrn_id_ || ','  || quote_literal(nfsr.dst_addr) || ','  || nfsr.octets || ','  || nfsr.src_port || ','  || nfsr.dst_port || ','  || nfsr.protocol || ','  || nfsr.checkouted || ','  || nfsr.for_checkout || ');';
    EXECUTE insq_;
    RETURN;
END;
$$
    LANGUAGE plpgsql;

CREATE FUNCTION nfs_prev_datechk(nfs_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '20090221'; d_e_ date := DATE '20090221'; BEGIN IF    nfs_date < d_s_ THEN RETURN -1; ELSIF nfs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;

CREATE FUNCTION nfs_prev_ins(nfsr billservice_netflowstream) RETURNS void
    AS $$BEGIN 
                         INSERT INTO nfs20090221(nas_id, account_id, tarif_id, date_start, src_addr, traffic_class_id, direction, traffic_transmit_node_id, dst_addr, octets, src_port, dst_port, protocol, checkouted, for_checkout)
                          VALUES 
                         (nfsr.nas_id, nfsr.account_id, nfsr.tarif_id, nfsr.date_start, nfsr.src_addr, 
                          nfsr.traffic_class_id, nfsr.direction, nfsr.traffic_transmit_node_id, nfsr.dst_addr, nfsr.octets, nfsr.src_port, 
                          nfsr.dst_port, nfsr.protocol, nfsr.checkouted, nfsr.for_checkout); RETURN; END;$$
    LANGUAGE plpgsql;
    
    
    
CREATE FUNCTION transaction_fn(bill_ character varying, account_id_ integer, type_id_ character varying, approved_ boolean, tarif_id_ integer, summ_ double precision, description_ text, created_ timestamp without time zone, ps_id_ integer, acctf_id_ integer, ps_condition_type_ integer) RETURNS void
    AS $$
DECLARE
    new_summ_ double precision;
    tr_id_ int;
BEGIN
    SELECT INTO new_summ_ summ_*(NOT EXISTS (SELECT id FROM billservice_suspendedperiod WHERE account_id=account_id AND (created_ BETWEEN start_date AND end_date)))::int;
    IF (ps_condition_type_ = 1) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance => 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    ELSIF (ps_condition_type_ = 2) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance < 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    END IF; 
    IF (new_summ_ > 0) THEN
        INSERT INTO billservice_transaction (bill, account_id,  type_id, approved,  tarif_id, summ, description, created) VALUES (bill_ , account_id_ ,  type_id_, approved_,  tarif_id_, new_summ_, description_, created_) RETURNING id INTO tr_id_;
    END IF;
    INSERT INTO billservice_periodicalservicehistory (service_id, transaction_id, accounttarif_id,  datetime) VALUES (ps_id_, tr_id_, acctf_id_, created_);
END;
$$
    LANGUAGE plpgsql;
    
    CREATE FUNCTION nfs_crt_prev_ins(datetx date) RETURNS void
    AS $$
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
    --ch_fn_bd_tx2_ text := '; d_e_ date := DATE ';
    --ch_fn_bd_tx3_ text := 'IF    nfs_date < d_s_ THEN RETURN -1; ELSIF nfs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';
    
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    nfs_date < d_s_ THEN RETURN -1; ELSIF nfs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';

    ch_fn_tx2_ text := ' LANGUAGE plpgsql VOLATILE COST 100;';

    qts_ text := 'CHK % % %';
    
    
   oneday_ = interval '1 day';
BEGIN    


        EXECUTE  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;


        --EXECUTE  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '; BEGIN ' || ch_fn_bd_tx3_) || ch_fn_tx2_;
        
        
        query_ :=  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '+ interval ' || quote_literal(oneday_) ||  ch_fn_bd_tx3_) || fn_tx2_;
        
        EXECUTE query_;
        
    RETURN;

END;
$$
    LANGUAGE plpgsql;