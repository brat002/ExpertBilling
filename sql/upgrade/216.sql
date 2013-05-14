ALTER TABLE billservice_transaction ADD COLUMN prev_balance numeric;

CREATE OR REPLACE FUNCTION trs_ins_trg_fn()
  RETURNS trigger AS
$BODY$
DECLARE
    cur_chk boolean;
    table_name text;
BEGIN
    table_name:=to_char(NEW.created, 'trsYYYYMM01');
    select INTO cur_chk exists(select relname from pg_class where relname = table_name::text and relkind='r');
    
    IF cur_chk = True THEN
        EXECUTE 'INSERT INTO ' || table_name || ' SELECT (' || quote_literal(NEW) || '::' || TG_RELID::regclass || ').*';
    ELSE 
        BEGIN
            PERFORM trs_crt_pdb(NEW.created::date);
            EXECUTE 'INSERT INTO ' || table_name || ' SELECT (' || quote_literal(NEW) || '::' || TG_RELID::regclass || ').*';
        EXCEPTION 
          WHEN duplicate_table THEN
            EXECUTE 'INSERT INTO ' || table_name || ' SELECT (' || quote_literal(NEW) || '::' || TG_RELID::regclass || ').*';
        END;
     END IF;
        
        
    RETURN NULL;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
  
CREATE OR REPLACE FUNCTION account_transaction_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN

SELECT INTO NEW.prev_balance  COALESCE(ballance, 0) FROM billservice_account WHERE id=NEW.account_id;

IF (TG_OP = 'INSERT') THEN
UPDATE billservice_account SET ballance=COALESCE(ballance, 0)+NEW.summ WHERE id=NEW.account_id;
RETURN NEW;
ELSIF (TG_OP = 'DELETE') THEN
UPDATE billservice_account SET ballance=COALESCE(ballance, 0)-OLD.summ WHERE id=OLD.account_id;
RETURN OLD;
ELSIF (TG_OP = 'UPDATE') THEN
UPDATE billservice_account SET ballance=COALESCE(ballance, 0)-OLD.summ WHERE id=OLD.account_id;
UPDATE billservice_account SET ballance=COALESCE(ballance, 0)+NEW.summ WHERE id=NEW.account_id;
RETURN NEW;
END IF;
RETURN NULL;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION account_transaction_trg_fn()
  OWNER TO ebs;
  

DROP FUNCTION trs_crt_cur_ins(date);
DROP FUNCTION trs_crt_prev_ins(date);
DROP FUNCTION trs_cur_datechk(timestamp without time zone);
DROP FUNCTION trs_cur_dt();
DROP FUNCTION trs_cur_ins(billservice_transaction);
DROP FUNCTION trs_inserter(billservice_transaction);
DROP FUNCTION trs_prev_datechk(timestamp without time zone);
DROP FUNCTION trs_prev_ins(billservice_transaction);


CREATE OR REPLACE FUNCTION psh_crt_pdb(datetx date)
  RETURNS void AS
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
                     CREATE INDEX psh#rpdate#_account_id ON psh#rpdate# USING btree (account_id);
                     CREATE INDEX psh#rpdate#_created ON psh#rpdate# USING btree (created);
                     CREATE TRIGGER acc_psh_trg AFTER INSERT OR UPDATE OR DELETE ON psh#rpdate# FOR EACH ROW EXECUTE PROCEDURE account_transaction_trg_fn();
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

    

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION psh_crt_pdb(date)
  OWNER TO ebs;
  
CREATE OR REPLACE FUNCTION psh_ins_trg_fn()
  RETURNS trigger AS
$BODY$
DECLARE
    cur_chk boolean;
    table_name text;
BEGIN
    table_name:=to_char(NEW.created, 'pshYYYYMM01');
    select INTO cur_chk exists(select relname from pg_class where relname = table_name::text and relkind='r');
    
    IF cur_chk = True THEN
        EXECUTE 'INSERT INTO ' || table_name || ' SELECT (' || quote_literal(NEW) || '::' || TG_RELID::regclass || ').*';
    ELSE 
        BEGIN
            PERFORM psh_crt_pdb(NEW.created::date);
            EXECUTE 'INSERT INTO ' || table_name || ' SELECT (' || quote_literal(NEW) || '::' || TG_RELID::regclass || ').*';
        EXCEPTION 
          WHEN duplicate_table THEN
            EXECUTE 'INSERT INTO ' || table_name || ' SELECT (' || quote_literal(NEW) || '::' || TG_RELID::regclass || ').*';
        END;
     END IF;
        
        
    RETURN NULL;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
  
ALTER TABLE billservice_periodicalservicehistory
   ADD COLUMN prev_balance numeric;

DROP FUNCTION psh_crt_cur_ins(date);
DROP FUNCTION psh_crt_prev_ins(date);
DROP FUNCTION psh_cur_datechk(timestamp without time zone);
DROP FUNCTION psh_cur_dt();
DROP FUNCTION psh_cur_ins(billservice_periodicalservicehistory);
DROP FUNCTION psh_inserter(billservice_periodicalservicehistory);
DROP FUNCTION psh_prev_datechk(timestamp without time zone);
DROP FUNCTION psh_prev_ins(billservice_periodicalservicehistory);


CREATE OR REPLACE FUNCTION traftrans_ins_trg_fn()
  RETURNS trigger AS
$BODY$
DECLARE
    cur_chk boolean;
    table_name text;
BEGIN
    table_name:=to_char(NEW.created, 'traftransYYYYMM01');
    select INTO cur_chk exists(select relname from pg_class where relname = table_name::text and relkind='r');
    
    IF cur_chk = True THEN
        EXECUTE 'INSERT INTO ' || table_name || ' SELECT (' || quote_literal(NEW) || '::' || TG_RELID::regclass || ').*';
    ELSE 
        BEGIN
            PERFORM traftrans_crt_pdb(NEW.created::date);
            EXECUTE 'INSERT INTO ' || table_name || ' SELECT (' || quote_literal(NEW) || '::' || TG_RELID::regclass || ').*';
        EXCEPTION 
          WHEN duplicate_table THEN
            EXECUTE 'INSERT INTO ' || table_name || ' SELECT (' || quote_literal(NEW) || '::' || TG_RELID::regclass || ').*';
        END;
     END IF;
        
        
    RETURN NULL;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
  
ALTER TABLE billservice_traffictransaction
   ADD COLUMN prev_balance numeric;

DROP FUNCTION traftrans_crt_cur_ins(date);
DROP FUNCTION traftrans_crt_prev_ins(date);
DROP FUNCTION traftrans_cur_datechk(timestamp without time zone);
DROP FUNCTION traftrans_cur_dt();
DROP FUNCTION traftrans_cur_ins(billservice_traffictransaction);
DROP FUNCTION traftrans_inserter(billservice_traffictransaction);
DROP FUNCTION traftrans_prev_datechk(timestamp without time zone);


CREATE OR REPLACE FUNCTION radius_activesession_ins_trg_fn()
  RETURNS trigger AS
$BODY$
DECLARE
    cur_chk boolean;
    table_name text;
BEGIN
    table_name:=to_char(NEW.created, 'radacctsYYYYMM01');
    select INTO cur_chk exists(select relname from pg_class where relname = table_name::text and relkind='r');
    
    IF cur_chk = True THEN
        EXECUTE 'INSERT INTO ' || table_name || ' SELECT (' || quote_literal(NEW) || '::' || TG_RELID::regclass || ').*';
    ELSE 
        BEGIN
            PERFORM radius_activesession_trs_crt_pdb(NEW.created::date);
            EXECUTE 'INSERT INTO ' || table_name || ' SELECT (' || quote_literal(NEW) || '::' || TG_RELID::regclass || ').*';
        EXCEPTION 
          WHEN duplicate_table THEN
            EXECUTE 'INSERT INTO ' || table_name || ' SELECT (' || quote_literal(NEW) || '::' || TG_RELID::regclass || ').*';
        END;
     END IF;
        
        
    RETURN NULL;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
  
  
ALTER TABLE qiwi_invoice
   ADD COLUMN prev_balance numeric;

ALTER TABLE billservice_addonservicetransaction
   ADD COLUMN prev_balance numeric;
   
ALTER TABLE billservice_onetimeservicehistory
   ADD COLUMN prev_balance numeric;
   
ALTER TABLE billservice_timetransaction
   ADD COLUMN prev_balance numeric;
   
   
DROP VIEW billservice_totaltransactionreport;

CREATE OR REPLACE VIEW billservice_totaltransactionreport AS 
        (        (        (        (        (         SELECT psh.id, psh.service_id, ( SELECT billservice_periodicalservice.name
                                                           FROM billservice_periodicalservice
                                                          WHERE billservice_periodicalservice.id = psh.service_id) AS service_name, 'billservice_periodicalservicehistory'::text AS "table", psh.created, ( SELECT billservice_accounttarif.tarif_id
                                                           FROM billservice_accounttarif
                                                          WHERE billservice_accounttarif.id = psh.accounttarif_id) AS tariff_id, psh.summ, psh.account_id, psh.type_id, NULL::integer AS systemuser_id, ''::character varying AS bill, ''::text AS description, NULL::timestamp without time zone AS end_promise, NULL::boolean AS promise_expired, prev_balance::numeric as prev_balance
                                                   FROM billservice_periodicalservicehistory psh
                                        UNION ALL 
                                                 SELECT transaction.id, NULL::integer AS service_id, ''::character varying AS service_name, 'billservice_transaction'::text AS "table", transaction.created, ( SELECT billservice_accounttarif.tarif_id
                                                           FROM billservice_accounttarif
                                                          WHERE billservice_accounttarif.id = transaction.accounttarif_id) AS tariff_id, transaction.summ::numeric AS summ, transaction.account_id, transaction.type_id, transaction.systemuser_id, transaction.bill, transaction.description, transaction.end_promise, transaction.promise_expired, prev_balance::numeric as prev_balance
                                                   FROM billservice_transaction transaction)
                                UNION ALL 
                                         SELECT tr.id, NULL::integer AS service_id, ''::character varying AS service_name, 'billservice_traffictransaction'::text AS "table", tr.created, ( SELECT billservice_accounttarif.tarif_id
                                                   FROM billservice_accounttarif
                                                  WHERE billservice_accounttarif.id = tr.accounttarif_id) AS tariff_id, tr.summ, tr.account_id, 'NETFLOW_BILL'::character varying AS type_id, NULL::integer AS systemuser_id, ''::character varying AS bill, ''::text AS description, NULL::timestamp without time zone AS end_promise, NULL::boolean AS promise_expired, prev_balance::numeric as prev_balance
                                           FROM billservice_traffictransaction tr)
                        UNION ALL 
                                 SELECT addst.id, addst.service_id, ( SELECT billservice_addonservice.name
                                           FROM billservice_addonservice
                                          WHERE billservice_addonservice.id = addst.service_id) AS service_name, 'billservice_addonservicetransaction'::text AS "table", addst.created, ( SELECT billservice_accounttarif.tarif_id
                                           FROM billservice_accounttarif
                                          WHERE billservice_accounttarif.id = addst.accounttarif_id) AS tariff_id, addst.summ, addst.account_id, addst.type_id, NULL::integer AS systemuser_id, ''::character varying AS bill, ''::text AS description, NULL::timestamp without time zone AS end_promise, NULL::boolean AS promise_expired, prev_balance::numeric as prev_balance
                                   FROM billservice_addonservicetransaction addst)
                UNION ALL 
                         SELECT osh.id, osh.onetimeservice_id AS service_id, ''::character varying AS service_name, 'billservice_onetimeservicehistory'::text AS "table", osh.created, ( SELECT billservice_accounttarif.tarif_id
                                   FROM billservice_accounttarif
                                  WHERE billservice_accounttarif.id = osh.accounttarif_id) AS tariff_id, osh.summ, osh.account_id, 'ONETIME_SERVICE'::character varying AS type_id, NULL::integer AS systemuser_id, ''::character varying AS bill, ''::text AS description, NULL::timestamp without time zone AS end_promise, NULL::boolean AS promise_expired, prev_balance::numeric as prev_balance
                           FROM billservice_onetimeservicehistory osh)
        UNION ALL 
                 SELECT tr.id, NULL::integer AS service_id, ''::character varying AS service_name, 'billservice_timetransaction'::text AS "table", tr.created, ( SELECT billservice_accounttarif.tarif_id
                           FROM billservice_accounttarif
                          WHERE billservice_accounttarif.id = tr.accounttarif_id) AS tariff_id, tr.summ, tr.account_id, 'TIME_ACCESS'::character varying AS type_id, NULL::integer AS systemuser_id, ''::character varying AS bill, ''::text AS description, NULL::timestamp without time zone AS end_promise, NULL::boolean AS promise_expired, prev_balance::numeric as prev_balance
                   FROM billservice_timetransaction tr)
UNION ALL 
         SELECT qi.id, NULL::integer AS service_id, ''::character varying AS service_name, 'qiwi_payment'::text AS "table", qi.created, get_tarif(qi.account_id, qi.created) AS tariff_id, qi.summ, qi.account_id, 'qiwi_payment'::character varying AS type_id, NULL::integer AS systemuser_id, qi.autoaccept::text AS bill, qi.date_accepted::text AS description, NULL::timestamp without time zone AS end_promise, NULL::boolean AS promise_expired, prev_balance::numeric as prev_balance
           FROM qiwi_invoice qi;

ALTER TABLE billservice_totaltransactionreport
  OWNER TO ebs;


CREATE OR REPLACE RULE billservice_totaltransactionreport_delete AS ON DELETE TO billservice_totaltransactionreport
    DO INSTEAD(SELECT 1);
    
