DROP TRIGGER acc_trans_trg ON billservice_transaction;

CREATE TRIGGER acc_trs_trg BEFORE INSERT OR DELETE OR UPDATE ON billservice_transaction FOR EACH ROW EXECUTE PROCEDURE account_transaction_trg_fn(); 

ALTER TABLE billservice_transaction DROP CONSTRAINT billservice_transaction_account_id_fkey;
ALTER TABLE billservice_transaction DROP CONSTRAINT billservice_transaction_tarif_id_fkey;

CREATE OR REPLACE FUNCTION trs_crt_cur_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION trs_cur_ins (trsr billservice_transaction) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO trs';
                         
    fn_bd_tx2_ text := '(bill, account_id, type_id, approved, tarif_id, summ, description, 
            created, systemuser_id, promise, end_promise, promise_expired, 
            accounttarif_id)
                          VALUES 
                         (trsr.bill, trsr.account_id, trsr.type_id, trsr.approved, trsr.tarif_id, trsr.summ, trsr.description, trsr.created, trsr.systemuser_id, trsr.promise, trsr.end_promise, trsr.promise_expired, trsr.accounttarif_id); RETURN; END;';
                          
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';


    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION trs_cur_datechk(trs_date timestamp without time zone) RETURNS integer AS ';

    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    trs_date < d_s_ THEN RETURN -1; ELSIF trs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';



    dt_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION trs_cur_dt() RETURNS date AS ';
    
    onemonth_ text := '1 month';
    query_ text;
    
    prevdate_ date;
    
BEGIN    


    
        query_ :=  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;

        EXECUTE query_;


        query_ :=  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '+ interval ' || quote_literal(onemonth_) ||  ch_fn_bd_tx3_) || fn_tx2_;

        EXECUTE query_;
        
        prevdate_ := trs_cur_dt();
        
        PERFORM trs_crt_prev_ins(prevdate_);
        
        query_ := dt_fn_tx1_ || quote_literal(' BEGIN RETURN  DATE ' || quote_literal(datetx_) || '; END; ') || fn_tx2_;
        
        EXECUTE query_;

        
    RETURN;

END;
$$
    LANGUAGE plpgsql;
    
CREATE OR REPLACE FUNCTION trs_crt_pdb(datetx date) RETURNS integer
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');
    datetx_e_ text := to_char((datetx + interval '1 month')::date, 'YYYYMM01');

    qt_dtx_ text;
    qt_dtx_e_ text;
    seq_tx1_ text := 'CREATE SEQUENCE trs#rpdate#_id_seq
                      INCREMENT 1
                      MINVALUE 1
                      MAXVALUE 9223372036854775807
                      START 1
                      CACHE 1;';
    seqname_tx1_ text := 'trs#rpdate#_id_seq';

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
                     
    at_tx1_ text := 'ALTER TABLE trs#rpdate# ALTER COLUMN id SET DEFAULT nextval(#qseqname#::regclass);';

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
    
CREATE OR REPLACE FUNCTION trs_crt_prev_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION trs_prev_ins (trsr billservice_transaction) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO trs';
                         
    fn_bd_tx2_ text := '(bill, account_id, type_id, approved, tarif_id, summ, description, 
            created, systemuser_id, promise, end_promise, promise_expired, 
            accounttarif_id)
                          VALUES 
                         (trsr.bill, trsr.account_id, trsr.type_id, trsr.approved, trsr.tarif_id, trsr.summ, trsr.description, trsr.created, trsr.systemuser_id, trsr.promise, trsr.end_promise, trsr.promise_expired, trsr.accounttarif_id); RETURN; END;';
                          
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';


    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION trs_prev_datechk(trs_date timestamp without time zone) RETURNS integer AS ';

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
$$
    LANGUAGE plpgsql; 
 
CREATE OR REPLACE FUNCTION trs_cur_datechk(trs_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700201'; d_e_ date := (DATE '19700101'+ interval '1 month')::date; BEGIN IF    trs_date < d_s_ THEN RETURN -1; ELSIF trs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;
    
CREATE OR REPLACE FUNCTION trs_prev_datechk(trs_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700101'; d_e_ date := (DATE '19700101'+ interval '1 month')::date; BEGIN IF    trs_date < d_s_ THEN RETURN -1; ELSIF trs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;
    
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
    insq_ := 'INSERT INTO trs' || datetx_ || ' (bill, account_id, type_id, approved, tarif_id, summ, description, created, systemuser_id, promise, end_promise, promise_expired, accounttarif_id) VALUES (' || ttrn_bill || ',' || ttrn_account_id || ',' || ttrn_type_id || ',' || ttrn_approved || ',' || ttrn_tarif_id || ',' || ttrn_summ || ',' || ttrn_description || ',' || trsr.created || ',' || ttrn_systemuser_id || ',' || ttrn_promise || ',' || ttrn_end_promise || ',' || ttrn_promise_expired || ',' || ttrn_accounttarif_id || ');';
    EXECUTE insq_;
    RETURN;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
    
CREATE OR REPLACE FUNCTION trs_ins_trg_fn()
  RETURNS trigger AS
$BODY$
DECLARE
    cur_chk int;
    prev_chk int;
BEGIN
    cur_chk := trs_cur_datechk(NEW.created);

    IF cur_chk = 0 THEN
        PERFORM trs_cur_ins(NEW);
    ELSIF cur_chk = 1 THEN
        BEGIN
            PERFORM trs_crt_pdb(NEW.created::date);
            PERFORM trs_crt_cur_ins(NEW.created::date);
            EXECUTE trs_cur_ins(NEW);
        EXCEPTION 
          WHEN duplicate_table THEN
             PERFORM trs_crt_cur_ins(NEW.created::date);
             EXECUTE trs_cur_ins(NEW);
        END;
        
        
    ELSE 
        prev_chk := trs_prev_datechk(NEW.created);
        IF prev_chk = 0 THEN
            PERFORM trs_prev_ins(NEW);
        ELSE
            BEGIN 
                PERFORM trs_inserter(NEW);
            EXCEPTION 
              WHEN undefined_table THEN
                PERFORM trs_crt_pdb(NEW.created::date);
                PERFORM trs_inserter(NEW);
            END;
        END IF;      
    END IF;
    RETURN NULL;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
  
CREATE TRIGGER trs_ins_trg
  BEFORE INSERT
  ON billservice_transaction
  FOR EACH ROW
  EXECUTE PROCEDURE trs_ins_trg_fn();

CREATE OR REPLACE FUNCTION trs_del_trg_fn()
  RETURNS trigger AS
$BODY$
    BEGIN
        INSERT INTO billservice_transaction (bill, account_id, type_id, approved, tarif_id, summ, description, created, systemuser_id, promise, end_promise, promise_expired, accounttarif_id) 
        VALUES(OLD.bill, OLD.account_id, OLD.type_id, OLD.approved, OLD.tarif_id, OLD.summ, OLD.description, OLD.created, OLD.systemuser_id, OLD.promise, OLD.end_promise, OLD.promise_expired, OLD.accounttarif_id);
        RETURN OLD;
    END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
  

CREATE TRIGGER trs_del_trg
  AFTER DELETE
  ON billservice_transaction
  FOR EACH ROW
  EXECUTE PROCEDURE trs_del_trg_fn();


CREATE OR REPLACE FUNCTION trs_cur_dt()
  RETURNS date AS
$BODY$ BEGIN RETURN  DATE '19700102'; END; $BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;