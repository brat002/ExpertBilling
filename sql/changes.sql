--14.04.2009

ALTER TABLE billservice_transaction ADD COLUMN accounttarif_id int;
UPDATE billservice_transaction AS bt SET accounttarif_id = (SELECT ba.id FROM billservice_accounttarif AS ba WHERE ba.account_id = bt.account_id AND ba.datetime < bt.created ORDER BY ba.datetime DESC LIMIT 1);

CREATE OR REPLACE FUNCTION trans_acctf_ins_trg_fn() RETURNS trigger
    AS $$ 
BEGIN
    IF NEW.accounttarif_id IS NULL THEN
        SELECT INTO NEW.accounttarif_id ba.id FROM billservice_accounttarif AS ba WHERE ba.account_id = NEW.account_id AND ba.datetime < NEW.created ORDER BY ba.datetime DESC LIMIT 1;
    END IF;
    RETURN NEW;    
END;
$$
    LANGUAGE plpgsql;
    
    
CREATE OR REPLACE FUNCTION transaction_sum(account_id_ int, acctf_id_ int, start_date_ timestamp without time zone, end_date_ timestamp without time zone) RETURNS double precision
    AS $$ 
DECLARE
    start_date_5m_ timestamp without time zone;
    result_ double precision;
BEGIN
    start_date_5m_ := date_trunc('minute', start_date_) - interval '1 min' * (date_part('min', start_date_)::int % 5); 
    SELECT INTO result_ sum(ssum) FROM (SELECT sum(summ) AS ssum FROM billservice_transaction WHERE account_id=account_id_ AND (accounttarif_id=acctf_id_) AND (summ > 0)  AND (created > start_date_ AND created < end_date_) UNION ALL SELECT sum(summ) AS ssum FROM billservice_traffictransaction WHERE account_id=account_id_ AND (accounttarif_id=acctf_id_) AND (summ > 0)  AND (datetime > start_date_ AND datetime < end_date_)UNION ALL SELECT sum(summ) AS ssum FROM billservice_timetransaction WHERE account_id=account_id_ AND (accounttarif_id=acctf_id_) AND (summ > 0)  AND (datetime > start_date_ AND datetime < end_date_)  UNION ALL SELECT sum(summ) AS ssum FROM billservice_periodicalservicehistory WHERE account_id=account_id_ AND (accounttarif_id=acctf_id_) AND (summ > 0)  AND (datetime > start_date_ AND datetime < end_date_)  UNION ALL SELECT sum(summ) AS ssum FROM billservice_onetimeservicehistory WHERE account_id=account_id_ AND (accounttarif_id=acctf_id_) AND (summ > 0)  AND (datetime > start_date_ AND datetime < end_date_)) AS ts_union ;
    RETURN result_;
END;
$$
    LANGUAGE plpgsql;
    
CREATE OR REPLACE FUNCTION transaction_block_sum(account_id_ int, start_date_ timestamp without time zone, end_date_ timestamp without time zone) RETURNS double precision
    AS $$ 
DECLARE
    start_date_5m_ timestamp without time zone;
    result_ double precision;
BEGIN
    start_date_5m_ := date_trunc('minute', start_date_) - interval '1 min' * (date_part('min', start_date_)::int % 5); 
    SELECT INTO result_ sum(ssum) FROM (SELECT sum(summ) AS ssum FROM billservice_transaction WHERE account_id=account_id_ AND (summ > 0) AND (created BETWEEN start_date_ AND end_date_) UNION ALL SELECT sum(summ) AS ssum FROM billservice_traffictransaction WHERE account_id=account_id_ AND (summ > 0) AND (datetime BETWEEN start_date_ AND end_date_) UNION ALL SELECT sum(summ) AS ssum FROM billservice_timetransaction WHERE account_id=account_id_ AND (summ > 0) AND (datetime BETWEEN start_date_ AND end_date_) UNION ALL SELECT sum(summ) AS ssum FROM billservice_periodicalservicehistory WHERE account_id=account_id_ AND (summ > 0) AND (datetime BETWEEN start_date_ AND end_date_)  UNION ALL SELECT sum(summ) AS ssum FROM billservice_onetimeservicehistory WHERE account_id=account_id_ AND (summ > 0) AND (datetime BETWEEN start_date_ AND end_date_)) AS ts_union ;
    RETURN result_;
END;
$$
    LANGUAGE plpgsql;
    
CREATE TRIGGER trans_acctf_ins_trg
    BEFORE INSERT ON billservice_transaction
    FOR EACH ROW
    EXECUTE PROCEDURE trans_acctf_ins_trg_fn();

ALTER TABLE billservice_periodicalservicehistory DROP COLUMN transaction_id;
ALTER TABLE billservice_periodicalservicehistory ADD COLUMN summ double precision;
ALTER TABLE billservice_periodicalservicehistory ADD COLUMN account_id int;
ALTER TABLE billservice_periodicalservicehistory ADD COLUMN type_id character varying;
ALTER TABLE billservice_periodicalservicehistory ADD CONSTRAINT billservice_periodicalservicehistory_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;
CREATE TRIGGER acc_psh_trg AFTER INSERT OR DELETE OR UPDATE ON billservice_periodicalservicehistory FOR EACH ROW EXECUTE PROCEDURE account_transaction_trg_fn(); 

CREATE OR REPLACE FUNCTION periodicaltr_fn(ps_id_ integer, acctf_id_ integer, account_id_ integer, type_id_ character varying, summ_ double precision, created_ timestamp without time zone, ps_condition_type_ integer) RETURNS void
    AS $$
DECLARE
    new_summ_ double precision;
BEGIN
    SELECT INTO new_summ_ summ_*(NOT EXISTS (SELECT id FROM billservice_suspendedperiod WHERE account_id=account_id AND (created_ BETWEEN start_date AND end_date)))::int;
    IF (ps_condition_type_ = 1) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance >= 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    ELSIF (ps_condition_type_ = 2) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance < 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    END IF; 
    INSERT INTO billservice_periodicalservicehistory (service_id, accounttarif_id,account_id, type_id, summ, datetime) VALUES (ps_id_, acctf_id_, account_id_, type_id_, new_summ_, created_);
END;
$$
    LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION psh_crt_cur_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION psh_cur_ins (pshr billservice_periodicalservicehistory) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO psh';
                         
    fn_bd_tx2_ text := '(service_id, account_id, accounttarif_id, summ, datetime)
                          VALUES 
                         (pshr.service_id, pshr.account_id, pshr.accounttarif_id, pshr.summ, pshr.datetime); RETURN; END;';
                          
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
$$
    LANGUAGE plpgsql;
    
CREATE OR REPLACE FUNCTION psh_crt_pdb(datetx date) RETURNS integer
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');
    datetx_e_ text := to_char((datetx + interval '1 month')::date, 'YYYYMM01');

    qt_dtx_ text;
    qt_dtx_e_ text;
    seq_tx1_ text := 'CREATE SEQUENCE psh#rpdate#_id_seq
                      INCREMENT 1
                      MINVALUE 1
                      MAXVALUE 9223372036854775807
                      START 1
                      CACHE 1;';
    seqname_tx1_ text := 'psh#rpdate#_id_seq';

    chk_tx1_ text := 'CHECK ( datetime >= DATE #stdtx# AND datetime < DATE #eddtx# )';
    ct_tx1_ text := 'CREATE TABLE psh#rpdate# (
                     #chk#,
                     CONSTRAINT psh#rpdate#_id_pkey PRIMARY KEY (id) ) 
                     INHERITS (billservice_periodicalservicehistory) 
                     WITH (OIDS=FALSE);                     
                     CREATE INDEX psh#rpdate#_datetime_id ON psh#rpdate# USING btree (datetime);
                     CREATE INDEX psh#rpdate#_service_id ON psh#rpdate# USING btree (service_id);
                     CREATE INDEX psh#rpdate#_accounttarif_id ON psh#rpdate# USING btree (accounttarif_id);
                     ';
                     
    at_tx1_ text := 'ALTER TABLE psh#rpdate# ALTER COLUMN id SET DEFAULT nextval(#qseqname#::regclass);';

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
    
CREATE OR REPLACE FUNCTION psh_crt_prev_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION psh_prev_ins (pshr billservice_periodicalservicehistory) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO psh';
                         
    fn_bd_tx2_ text := '(service_id, account_id, accounttarif_id, summ, datetime)
                          VALUES 
                         (pshr.service_id, pshr.account_id, pshr.accounttarif_id, pshr.summ, pshr.datetime); RETURN; END;';
                          
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
$$
    LANGUAGE plpgsql; 
 
CREATE OR REPLACE FUNCTION psh_cur_datechk(psh_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700201'; d_e_ date := (DATE '19700101'+ interval '1 month')::date; BEGIN IF    psh_date < d_s_ THEN RETURN -1; ELSIF psh_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;
    
CREATE OR REPLACE FUNCTION psh_prev_datechk(psh_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700101'; d_e_ date := (DATE '19700101'+ interval '1 month')::date; BEGIN IF    psh_date < d_s_ THEN RETURN -1; ELSIF psh_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;
    
CREATE OR REPLACE FUNCTION psh_inserter(pshr billservice_periodicalservicehistory) RETURNS void
    AS $$
DECLARE
    datetx_ text := to_char(pshr.datetime::date, 'YYYYMM01');
    insq_   text;

    ttrn_actfid_ text;    
BEGIN
    
    IF pshr.accounttarif_id IS NULL THEN
       ttrn_actfid_ := 'NULL';
    ELSE
       ttrn_actfid_ := pshr.accounttarif_id::text;
    END IF;
    insq_ := 'INSERT INTO psh' || datetx_ || ' (service_id, account_id, accounttarif_id, summ, datetime) VALUES (' 
    || pshr.service_id || ',' || pshr.account_id || ',' || pshr.accounttarif_id || ',' || pshr.summ || ','  || quote_literal(pshr.datetime) || ','  || ttrn_actfid_ || ');';
    EXECUTE insq_;
    RETURN;
END;
$$
    LANGUAGE plpgsql;
    
ALTER TABLE billservice_onetimeservicehistory ADD COLUMN summ double precision;
ALTER TABLE billservice_onetimeservicehistory ADD COLUMN account_id int;
ALTER TABLE billservice_onetimeservicehistory ADD CONSTRAINT billservice_onetimeservicehistory_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE billservice_onetimeservicehistory ADD CONSTRAINT billservice_onetimeservicehistory_onetimeservice_id_fkey FOREIGN KEY (onetimeservice_id) REFERENCES billservice_onetimeservice(id) ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE billservice_onetimeservicehistory DROP COLUMN transaction_id;
CREATE TRIGGER acc_otsh_trg AFTER INSERT OR DELETE OR UPDATE ON billservice_onetimeservicehistory FOR EACH ROW EXECUTE PROCEDURE account_transaction_trg_fn();  


--ALTER TABLE billservice_traffictransaction RENAME COLUMN sum TO summ;
  
  
-----------------------------------------------  
  
CREATE TABLE billservice_traffictransaction
(
  id serial NOT NULL,
  traffictransmitservice_id integer NOT NULL,
  account_id integer NOT NULL,
  accounttarif_id integer NOT NULL,
  summ double precision NOT NULL,
  datetime timestamp without time zone NOT NULL,
  CONSTRAINT billservice_traffictransaction_pkey PRIMARY KEY (id),
  CONSTRAINT billservice_traffictransaction_account_id_fkey FOREIGN KEY (account_id)
      REFERENCES billservice_account (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT billservice_traffictransaction_traffictransmitservice_id_fkey FOREIGN KEY (traffictransmitservice_id)
      REFERENCES billservice_traffictransmitservice (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED
)
WITH (OIDS=FALSE);
ALTER TABLE billservice_traffictransaction OWNER TO mikrobill;

CREATE INDEX billservice_traffictransaction_account_id
  ON billservice_traffictransaction
  USING btree
  (account_id);

CREATE INDEX billservice_traffictransaction_traffictransmitservice_id_accounttarif_id_datetime
  ON billservice_traffictransaction
  USING btree
  (traffictransmitservice_id, accounttarif_id, datetime);
  

CREATE OR REPLACE FUNCTION tftrans_ins_trg_fn() RETURNS trigger
    AS $$ 
BEGIN
    NEW.datetime := date_trunc('minute', NEW.datetime) - interval '1 min' * (date_part('min', NEW.datetime)::int % 5); 
    UPDATE billservice_traffictransaction SET summ=summ+NEW.summ WHERE traffictransmitservice_id=NEW.traffictransmitservice_id AND account_id=NEW.account_id AND datetime=NEW.datetime;
    IF FOUND THEN
        RETURN NULL;
    ELSE
        RETURN NEW;
    END IF;
    
END;
$$
    LANGUAGE plpgsql;
    
CREATE TRIGGER tftrans_ins_trg
    BEFORE INSERT ON billservice_traffictransaction
    FOR EACH ROW
    EXECUTE PROCEDURE tftrans_ins_trg_fn();
    
CREATE TRIGGER acc_tftrans_trg AFTER INSERT OR DELETE OR UPDATE ON billservice_traffictransaction FOR EACH ROW EXECUTE PROCEDURE account_transaction_trg_fn();

CREATE TABLE billservice_timetransaction
(
  id serial NOT NULL,
  timeaccessservice_id integer NOT NULL,
  account_id integer NOT NULL,
  accounttarif_id integer NOT NULL,
  session_id integer NOT NULL,
  summ double precision NOT NULL,
  datetime timestamp without time zone NOT NULL,
  CONSTRAINT billservice_timetransaction_pkey PRIMARY KEY (id),
  CONSTRAINT billservice_timetransaction_account_id_fkey FOREIGN KEY (account_id)
      REFERENCES billservice_account (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT billservice_timetransaction_timeaccessservice_id_fkey FOREIGN KEY (timeaccessservice_id)
      REFERENCES billservice_timeaccessservice (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT billservice_timetransaction_sessionid_fkey FOREIGN KEY (session_id)
      REFERENCES radius_session (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED
)
WITH (OIDS=FALSE);
ALTER TABLE billservice_timetransaction OWNER TO mikrobill;

CREATE INDEX billservice_timetransaction_account_id
  ON billservice_timetransaction
  USING btree
  (account_id);

CREATE INDEX billservice_timetransaction_traffictransmitservice_id_account_id_datetime
  ON billservice_timetransaction
  USING btree
  (timeaccessservice_id, accounttarif_id, datetime);
  

CREATE OR REPLACE FUNCTION tmtrans_ins_trg_fn() RETURNS trigger
    AS $$ 
BEGIN
    NEW.datetime := date_trunc('minute', NEW.datetime) - interval '1 min' * (date_part('min', NEW.datetime)::int % 5); 
    UPDATE billservice_timetransaction SET summ=summ+NEW.summ WHERE timeaccessservice_id=NEW.timeaccessservice_id AND account_id=NEW.account_id AND datetime=NEW.datetime;
    IF FOUND THEN
        RETURN NULL;
    ELSE
        RETURN NEW;
    END IF;
    
END;
$$
    LANGUAGE plpgsql;
    
CREATE TRIGGER tmtrans_ins_trg
    BEFORE INSERT ON billservice_timetransaction
    FOR EACH ROW
    EXECUTE PROCEDURE tmtrans_ins_trg_fn();
    
CREATE TRIGGER acc_tmtrans_trg AFTER INSERT OR DELETE OR UPDATE ON billservice_timetransaction FOR EACH ROW EXECUTE PROCEDURE account_transaction_trg_fn();

--06.04.2009
ALTER TABLE billservice_shedulelog
DROP CONSTRAINT billservice_shedulelog_accounttarif_id_fkey;

ALTER TABLE billservice_shedulelog
ADD CONSTRAINT billservice_shedulelog_accounttarif_id_fkey FOREIGN KEY (accounttarif_id)
REFERENCES billservice_accounttarif (id) MATCH SIMPLE
ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;


ALTER TABLE billservice_shedulelog
DROP CONSTRAINT billservice_shedulelog_account_id_fkey

ALTER TABLE billservice_shedulelog
ADD CONSTRAINT billservice_shedulelog_account_id_fkey FOREIGN KEY (account_id)
REFERENCES billservice_account (id) MATCH SIMPLE
ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE billservice_traffictransmitnodes
  DROP CONSTRAINT billservice_traffictransmitnodes_group_id_fkey ;

ALTER TABLE billservice_traffictransmitnodes
  ADD CONSTRAINT billservice_traffictransmitnodes_group_id_fkey FOREIGN KEY (group_id)
      REFERENCES billservice_group (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE;
      
CREATE OR REPLACE FUNCTION clear_tariff_services_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN


IF (TG_OP = 'DELETE') THEN
    IF (OLD.traffic_transmit_service_id is not Null) THEN
        DELETE FROM billservice_traffictransmitservice WHERE id=OLD.traffic_transmit_service_id;
    END IF;

    IF (OLD.time_access_service_id is not Null) THEN
        DELETE FROM billservice_timeaccessservice WHERE id=OLD.time_access_service_id;   
    RETURN OLD;
    END IF;
    
END IF;
RETURN OLD;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;


CREATE TRIGGER clear_tariff_services_trg
  BEFORE DELETE
  ON billservice_tariff
  FOR EACH ROW
  EXECUTE PROCEDURE clear_tariff_services_trg_fn();

--7.04.2009
ALTER TABLE billservice_systemuser
   ADD COLUMN "role" integer;
ALTER TABLE billservice_systemuser
   ALTER COLUMN "role" SET NOT NULL;
   
UPDATE billservice_systemuser SET role = 0 WHERE id>0;

--08.04.2009
ALTER TABLE radius_activesession
   ALTER COLUMN interrim_update DROP DEFAULT;
ALTER TABLE billservice_transaction
   ADD COLUMN systemuser_id integer;
   
ALTER TABLE billservice_transaction ADD CONSTRAINT billservice_systemuser_fkey FOREIGN KEY (systemuser_id) REFERENCES billservice_systemuser (id)
   ON UPDATE NO ACTION ON DELETE SET NULL
   DEFERRABLE;
CREATE INDEX fki_billservice_systemuser_fkey ON billservice_transaction(systemuser_id);

ALTER TABLE billservice_transaction
   ADD COLUMN promise boolean;
ALTER TABLE billservice_transaction
   ALTER COLUMN promise SET DEFAULT False;
   
ALTER TABLE billservice_transaction
   ADD COLUMN end_promise timestamp without time zone;


ALTER TABLE billservice_transaction
   ADD COLUMN promise_expired boolean;
ALTER TABLE billservice_transaction
   ALTER COLUMN promise_expired SET DEFAULT False;

-- !!! 
ALTER TABLE billservice_transaction
  ADD CONSTRAINT billservice_transaction_tarif_id_fkey FOREIGN KEY (tarif_id)
      REFERENCES billservice_tariff (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL DEFERRABLE INITIALLY IMMEDIATE;
      

INSERT INTO billservice_transactiontype(
             "name", internal_name)
    VALUES ('Платёж совершён кассиром', 'CASSA_TRANSACTION');
    
