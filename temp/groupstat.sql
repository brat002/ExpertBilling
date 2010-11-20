DROP INDEX billservice_groupstat_account_id;
DROP INDEX billservice_groupstat_datetime;
DROP INDEX billservice_groupstat_gr_acc_dt_id;
DROP INDEX billservice_groupstat_group_id;

CREATE OR REPLACE FUNCTION gpst_del_trg_fn() RETURNS trigger
    AS $$
    BEGIN
        INSERT INTO billservice_groupstat (group_id, account_id, bytes, datetime, classes, classbytes, max_class) VALUES( OLD.group_id, OLD.account_id, OLD.bytes, OLD.datetime, OLD.classes, OLD.classbytes, OLD.max_class);
        RETURN OLD;
    END;
$$
    LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION gpst_crt_cur_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION gpst_cur_ins (gpstr billservice_groupstat) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO gpst';
                         
    fn_bd_tx2_ text := '(group_id, account_id, bytes, datetime, classes, classbytes, max_class)
                          VALUES 
                         (gpstr.group_id, gpstr.account_id, gpstr.bytes, gpstr.datetime, gpstr.classes, gpstr.classbytes, gpstr.max_class); RETURN; END;';
                          
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';


    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION gpst_cur_datechk(gpst_date timestamp without time zone) RETURNS integer AS ';

    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    gpst_date < d_s_ THEN RETURN -1; ELSIF gpst_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';



    dt_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION gpst_cur_dt() RETURNS date AS ';
    
    onemonth_ text := '1 month';
    query_ text;
    
    prevdate_ date;
    
BEGIN    


    
        query_ :=  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;

        EXECUTE query_;


        query_ :=  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '+ interval ' || quote_literal(onemonth_) ||  ch_fn_bd_tx3_) || fn_tx2_;

        EXECUTE query_;
        
        prevdate_ := gpst_cur_dt();
        
        PERFORM gpst_crt_prev_ins(prevdate_);
        
        query_ := dt_fn_tx1_ || quote_literal(' BEGIN RETURN  DATE ' || quote_literal(datetx_) || '; END; ') || fn_tx2_;
        
        EXECUTE query_;

        
    RETURN;

END;
$$
    LANGUAGE plpgsql;




CREATE OR REPLACE FUNCTION gpst_crt_pdb(datetx date) RETURNS integer
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');
    datetx_e_ text := to_char((datetx + interval '1 month')::date, 'YYYYMM01');

    qt_dtx_ text;
    qt_dtx_e_ text;
    seq_tx1_ text := 'CREATE SEQUENCE gpst#rpdate#_id_seq
                      INCREMENT 1
                      MINVALUE 1
                      MAXVALUE 9223372036854775807
                      START 1
                      CACHE 1;';
    seqname_tx1_ text := 'gpst#rpdate#_id_seq';

    chk_tx1_ text := 'CHECK ( datetime >= DATE #stdtx# AND datetime < DATE #eddtx# )';
    ct_tx1_ text := 'CREATE TABLE gpst#rpdate# (
                     #chk#,
                     CONSTRAINT gpst#rpdate#_id_pkey PRIMARY KEY (id) ) 
                     INHERITS (billservice_groupstat) 
                     WITH (OIDS=FALSE);                     
                     CREATE INDEX gpst#rpdate#_datetime_id ON gpst#rpdate# USING btree (datetime);
                     CREATE INDEX gpst#rpdate#_gr_acc_dt_id ON gpst#rpdate# USING btree (group_id, account_id, datetime);
                     CREATE INDEX gpst#rpdate#_account_id ON gpst#rpdate# USING btree (account_id);
                     CREATE INDEX gpst#rpdate#_group_id ON gpst#rpdate# USING btree (group_id);
                     ';
                     
    at_tx1_ text := 'ALTER TABLE gpst#rpdate# ALTER COLUMN id SET DEFAULT nextval(#qseqname#::regclass);';

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



CREATE OR REPLACE FUNCTION gpst_crt_prev_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION gpst_prev_ins (gpstr billservice_groupstat) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO gpst';
                         
    fn_bd_tx2_ text := '(group_id, account_id, bytes, datetime, classes, classbytes, max_class)
                          VALUES 
                         (gpstr.group_id, gpstr.account_id, gpstr.bytes, gpstr.datetime, gpstr.classes, gpstr.classbytes, gpstr.max_class); RETURN; END;';
                          
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';


    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION gpst_prev_datechk(gpst_date timestamp without time zone) RETURNS integer AS ';

    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    gpst_date < d_s_ THEN RETURN -1; ELSIF gpst_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';

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

CREATE OR REPLACE FUNCTION gpst_cur_datechk(gpst_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700201'; d_e_ date := (DATE '19700201'+ interval '1 month')::date; BEGIN IF    gpst_date < d_s_ THEN RETURN -1; ELSIF gpst_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION gpst_cur_dt() RETURNS date
    AS $$ BEGIN RETURN  DATE '19700201'; END; $$
    LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION gpst_cur_ins(gpstr billservice_groupstat) RETURNS void
    AS $$BEGIN 
                         RETURN; END;$$
    LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION gpst_ins_trg_fn() RETURNS trigger
    AS $$
DECLARE
    cur_chk int;
    prev_chk int;
BEGIN
    cur_chk := gpst_cur_datechk(NEW.datetime);

    IF cur_chk = 0 THEN
        PERFORM gpst_cur_ins(NEW);
    ELSIF cur_chk = 1 THEN
        BEGIN
            PERFORM gpst_crt_pdb(NEW.datetime::date);
            PERFORM gpst_crt_cur_ins(NEW.datetime::date);
            EXECUTE gpst_cur_ins(NEW);
        EXCEPTION 
          WHEN duplicate_table THEN
             PERFORM gpst_crt_cur_ins(NEW.datetime::date);
             EXECUTE gpst_cur_ins(NEW);
        END;
        
        
    ELSE 
        prev_chk := gpst_prev_datechk(NEW.datetime);
        IF prev_chk = 0 THEN
            PERFORM gpst_prev_ins(NEW);
        ELSE
            BEGIN 
                PERFORM gpst_inserter(NEW);
            EXCEPTION 
              WHEN undefined_table THEN
                PERFORM gpst_crt_pdb(NEW.datetime::date);
                PERFORM gpst_inserter(NEW);
            END;
        END IF;      
    END IF;
    RETURN NULL;
END;
$$
    LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION gpst_inserter(gpstr billservice_groupstat) RETURNS void
    AS $$
DECLARE
    datetx_ text := to_char(gpstr.datetime::date, 'YYYYMM01');
    insq_   text;
    ttrn_classes_ text; 
    ttrn_classbytes_ text; 
    ttrn_max_class_ int; 
 
BEGIN
    
    IF gpstr.classes IS NULL THEN
       ttrn_classes_ := '{}';
    ELSE
       ttrn_classes_ := quote_literal(gpstr.classes);
    END IF;
    IF gpstr.classbytes IS NULL THEN
       ttrn_classbytes_ := '{}';
    ELSE
       ttrn_classbytes_ := quote_literal(gpstr.classbytes);
    END IF;    
    IF gpstr.max_class IS NULL THEN
       ttrn_max_class_ := 'NULL';
    ELSE
       ttrn_max_class_ := gpstr.max_class;
    END IF;

    --check quote literal
    
    insq_ := 'INSERT INTO gpst' || datetx_ || ' (group_id, account_id, bytes, datetime, classes, classbytes, max_class) VALUES (' 
    || gpstr.group_id || ',' || gpstr.account_id || ','  || gpstr.bytes || ',' || quote_literal(gpstr.datetime) || ',' ||ttrn_classes_ || ',' || ttrn_classbytes_ || ',' ||  ttrn_max_class_ || ');';
    EXECUTE insq_;
    RETURN;
END;
$$
    LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION gpst_prev_datechk(gpst_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700101'; d_e_ date := (DATE '19700101'+ interval '1 month')::date; BEGIN IF    gpst_date < d_s_ THEN RETURN -1; ELSIF gpst_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION gpst_prev_ins(gpstr billservice_groupstat) RETURNS void
    AS $$BEGIN 
                          RETURN; END;$$
    LANGUAGE plpgsql;
    
    
CREATE TRIGGER gpst_del_trg
    AFTER DELETE ON billservice_groupstat
    FOR EACH ROW
    EXECUTE PROCEDURE gpst_del_trg_fn();


CREATE TRIGGER gpst_ins_trg
    BEFORE INSERT ON billservice_groupstat
    FOR EACH ROW
    EXECUTE PROCEDURE gpst_ins_trg_fn();