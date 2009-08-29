--06.04.2009
ALTER TABLE billservice_shedulelog
DROP CONSTRAINT billservice_shedulelog_accounttarif_id_fkey;

ALTER TABLE billservice_shedulelog
ADD CONSTRAINT billservice_shedulelog_accounttarif_id_fkey FOREIGN KEY (accounttarif_id)
REFERENCES billservice_accounttarif (id) MATCH SIMPLE
ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;


ALTER TABLE billservice_shedulelog
DROP CONSTRAINT billservice_shedulelog_account_id_fkey;

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

ALTER TABLE psh20090401
   ALTER COLUMN transaction_id SET DEFAULT False;
-- !!! 
ALTER TABLE billservice_transaction
  DROP CONSTRAINT billservice_transaction_tarif_id_fkey;
ALTER TABLE billservice_transaction
  ADD CONSTRAINT billservice_transaction_tarif_id_fkey FOREIGN KEY (tarif_id)
      REFERENCES billservice_tariff (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL DEFERRABLE INITIALLY IMMEDIATE;
      

INSERT INTO billservice_transactiontype(id, "name", internal_name) VALUES (10, 'Операция проведена кассиром', 'CASSA_TRANSACTION');
INSERT INTO billservice_transactiontype("name", internal_name) VALUES ('Платёжная система ОСМП', 'OSMP_BILL');    


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
    SELECT INTO result_ sum(ssum) FROM (SELECT sum(summ) AS ssum FROM billservice_transaction WHERE account_id=account_id_ AND (accounttarif_id=acctf_id_) AND (summ > 0)  AND (created > start_date_ AND created < end_date_) UNION ALL SELECT sum(summ) AS ssum FROM billservice_traffictransaction WHERE account_id=account_id_ AND (accounttarif_id=acctf_id_) AND (summ > 0)  AND (datetime > start_date_ AND datetime < end_date_) UNION ALL SELECT sum(summ) AS ssum FROM billservice_timetransaction WHERE account_id=account_id_ AND (accounttarif_id=acctf_id_) AND (summ > 0)  AND (datetime > start_date_ AND datetime < end_date_)  UNION ALL SELECT sum(summ) AS ssum FROM billservice_periodicalservicehistory WHERE account_id=account_id_ AND (accounttarif_id=acctf_id_) AND (summ > 0)  AND (datetime > start_date_ AND datetime < end_date_)  UNION ALL SELECT sum(summ) AS ssum FROM billservice_onetimeservicehistory WHERE account_id=account_id_ AND (accounttarif_id=acctf_id_) AND (summ > 0)  AND (datetime > start_date_ AND datetime < end_date_)) AS ts_union ;
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

--ALTER TABLE billservice_periodicalservicehistory DROP COLUMN transaction_id;
ALTER TABLE billservice_periodicalservicehistory ADD COLUMN summ double precision;
ALTER TABLE billservice_periodicalservicehistory ADD COLUMN account_id int;
ALTER TABLE billservice_periodicalservicehistory ADD COLUMN type_id character varying;
ALTER TABLE billservice_periodicalservicehistory ADD CONSTRAINT billservice_periodicalservicehistory_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;
CREATE TRIGGER acc_psh_trg BEFORE INSERT OR DELETE OR UPDATE ON billservice_periodicalservicehistory FOR EACH ROW EXECUTE PROCEDURE account_transaction_trg_fn(); 

CREATE OR REPLACE FUNCTION periodicaltr_fn(ps_id_ integer, acctf_id_ integer, account_id_ integer, type_id_ character varying, summ_ double precision, created_ timestamp without time zone, ps_condition_type_ integer) RETURNS void
    AS $$
DECLARE
    new_summ_ double precision;
BEGIN
    SELECT INTO new_summ_ summ_*(NOT EXISTS (SELECT id FROM billservice_suspendedperiod WHERE account_id=account_id_ AND (created_ BETWEEN start_date AND end_date)))::int;
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
                         
    fn_bd_tx2_ text := '(service_id, account_id, accounttarif_id, type_id, summ, datetime)
                          VALUES 
                         (pshr.service_id, pshr.account_id, pshr.accounttarif_id, pshr.type_id, pshr.summ, pshr.datetime); RETURN; END;';
                          
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
                         
    fn_bd_tx2_ text := '(service_id, account_id, accounttarif_id,type_id, summ, datetime)
                          VALUES 
                         (pshr.service_id, pshr.account_id, pshr.accounttarif_id, pshr.type_id, pshr.summ, pshr.datetime); RETURN; END;';
                          
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
    insq_ := 'INSERT INTO psh' || datetx_ || ' (service_id, account_id, accounttarif_id, type_id, summ, datetime) VALUES (' 
    || pshr.service_id || ',' || pshr.account_id || ',' || pshr.accounttarif_id || ','  || quote_literal(pshr.type_id) || ',' || pshr.summ || ','  || quote_literal(pshr.datetime) || ');';
    EXECUTE insq_;
    RETURN;
END;
$$
    LANGUAGE plpgsql;
    
ALTER TABLE billservice_onetimeservicehistory ADD COLUMN summ double precision;
ALTER TABLE billservice_onetimeservicehistory ADD COLUMN account_id int;
ALTER TABLE billservice_onetimeservicehistory ADD CONSTRAINT billservice_onetimeservicehistory_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE billservice_onetimeservicehistory ADD CONSTRAINT billservice_onetimeservicehistory_onetimeservice_id_fkey FOREIGN KEY (onetimeservice_id) REFERENCES billservice_onetimeservice(id) ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;
--ALTER TABLE billservice_onetimeservicehistory DROP COLUMN transaction_id;
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
ALTER TABLE billservice_traffictransaction OWNER TO ebs;

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
ALTER TABLE billservice_timetransaction OWNER TO ebs;

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


--13.04.2009
ALTER TABLE billservice_bankdata ALTER bank TYPE character varying(255);
ALTER TABLE billservice_bankdata
   ALTER COLUMN bank SET DEFAULT '';
ALTER TABLE billservice_bankdata
   ALTER COLUMN bank DROP NOT NULL;

ALTER TABLE billservice_bankdata ALTER bankcode TYPE character varying(40);
ALTER TABLE billservice_bankdata
   ALTER COLUMN bankcode SET DEFAULT '';
ALTER TABLE billservice_bankdata
   ALTER COLUMN bankcode DROP NOT NULL;

ALTER TABLE billservice_bankdata ALTER rs TYPE character varying(60);
ALTER TABLE billservice_bankdata
   ALTER COLUMN rs SET DEFAULT '';
ALTER TABLE billservice_bankdata
   ALTER COLUMN rs DROP NOT NULL;

ALTER TABLE billservice_bankdata ALTER currency TYPE character varying(40);
ALTER TABLE billservice_bankdata
   ALTER COLUMN currency SET DEFAULT '';
ALTER TABLE billservice_bankdata
   ALTER COLUMN currency DROP NOT NULL;


ALTER TABLE billservice_operator
   ALTER COLUMN bank_id DROP NOT NULL;

-- 15.04.2009 
INSERT INTO billservice_template (id, name, type_id, body) VALUES (4, 'Акт выполненных работ', 4, 'Акт выполненных работ');
INSERT INTO billservice_template (id, name, type_id, body) VALUES (5, 'Счет фактура', 3, 'Счет фактура');
INSERT INTO billservice_template (id, name, type_id, body) VALUES (6, 'Договор на подключение юр. лиц', 2, '<html>
            <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            </head>
            <body>
            Имя: ${account.username}  <br>
${organization.name} 
${bank.bankcode} 
            </body>
            </html>');
INSERT INTO billservice_template (id, name, type_id, body) VALUES (7, 'Кассовый чек', 5, '<html>
 <head>
 <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
 <style>
   td{
        FONT: 9px Times New Roman;
    }
    h1{
        FONT: 9px Arial;
    }
  </style>
 </head>
 <body>
  <table align=center width="85%">
    <tr>
     <td>
       <h1 align=center> <b> Квитанция об оплате услуг № ${transaction_id} </b> </h1>
       <strong>Абонент:</strong> ${account.fullname} <br>
       <strong>Тарифный план:</strong> ${tarif.name} <br>
       <strong>Логин:</strong> ${account.username}<br>
       <strong>Сумма:</strong> ${sum}<br>
       <strong>Дата приема платежа:</strong> ${created}<br>
    </td>
   </tr>
  </table>
 </body>
</html>
');
INSERT INTO billservice_template (id, name, type_id, body) VALUES (2, 'Договор', 1, '<html>
            <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            </head>
            <body>
${account.id}<br />
${account.username}<br />
${account.password}<br />
${account.fullname}<br />
${account.email}<br />
${account.address}<br />
${account.nas_id}<br />
${account.vpn_ip_address}<br />
${account.assign_ipn_ip_from_dhcp}<br />
${account.ipn_ip_address}<br />
${account.ipn_mac_address}<br />
${account.ipn_status}<br />
${account.status}<br />
${account.suspended}<br />
${account.created}<br />
${account.ballance}<br />
${account.credit}<br />
${account.disabled_by_limit}<br />
${account.balance_blocked}<br />
${account.ipn_speed}<br />
${account.vpn_speed}<br />
${account.netmask}<br />
${account.ipn_added}<br />
${account.city}<br />
${account.postcode}<br />
${account.region}<br />
${account.street}<br />
${account.house}<br />
${account.house_bulk}<br />
${account.entrance}<br />
${account.room}<br />
${account.vlan}<br />
${account.allow_webcab}<br />
${account.allow_expresscards}<br />
${account.assign_dhcp_null}<br />
${account.assign_dhcp_block}<br />
${account.allow_vpn_null}<br />
${account.allow_vpn_block}<br />
${account.passport}<br />
${account.passport_date}<br />
${account.passport_given}<br />

${tarif.name}<br />


${created}<br />
            
            
            
            </body>
            </html>
');
INSERT INTO billservice_template (id, name, type_id, body) VALUES (8, 'Накладная на карты экспресс-оплаты', 6, '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
"http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head>

<body>
<div style="width:100%; "> 
<div style="float:right ">
<span style="font-weight:bold; ">Дилер</span><br>		
Организация: ${dealer.organization}<br>	
Директор: ${dealer.director}<br>	
Юр адрес: ${dealer.uraddress}<br>	
р/с: ${dealer.rs}<br>	
УНН: ${dealer.unp}<br>	
ОКПО: ${dealer.okpo}<br>	
Банк: ${dealer.bank}, код ${dealer.bankcode}<br>	
</div>

<div style="float:left ">
	<span style="font-weight:bold; ">Оператор</span><br>	
	Организация: ${operator.organization}<br>	
	Директор: ${operator.director}<br>	
	Юр адрес: ${operator.uraddress}<br>
  р/с: ${operator.rs}	<br>	
	УНН: ${operator.unp}<br>	
	ОКПО: ${operator.okpo}<br>	
	Банк: ${operator.bank}, Код ${operator.bankcode}<br>	
</div>
</div>

<div style="font-weight:bold; float:left; width:100%; text-align:center; margin-bottom:20px; margin-top:20px; ">Накладная от ${created}</div>

<div style="clear:both "></div>
<table border="1" align="center" style="width:100%">
	<tr>
		<td>ID карты</td>
		<td>Серия</td>
		<td>Номинал</td>
		<td>Активировать С</td>
		<td>Активировать По</td>
	</tr>
	
	% for card in cards:
	<tr>
	   <td>${card.id}</td>
	   <td>${card.series}</td>
	   <td>${card.nominal}</td>
	   <td>${card.start_date}</td>
	   <td>${card.end_date}</td>
	</tr>
	% endfor
</table>

Итого ${cardcount} карт на сумму: ${sum_for_pay}<br>	
Скидка: ${discount} на сумму ${discount_sum}<br>	
Оплачено: ${pay}<br>	
Оплатить до:${paydeffer}

</body>
</html>');
INSERT INTO billservice_template (id, name, type_id, body) VALUES (9, 'Шаблон карты экспресс-оплаты', 7, '<div style="position:relative; display:block; width:255px; height:143px; font-face:Arial;">
<img src="img/card_blue.gif" style="border:none;">
	<div style="position:absolute; display:block; top:60px; left:16px; font-size:32px;">${card.nominal}</div>
	<div style="position:absolute; display:block; top:96px; left:3px; font-size:10px;">PIN: ${card.pin}</div>
	<div style="position:absolute; display:block; top:96px; left:175px; font-size:10px;">Серия: ${card.series}</div>
	<div style="position:absolute; display:block; top:118px; left:3px; font-size:6px;">Активировать c ${card.start_date} по ${card.end_date} </div>
	<div style="position:absolute; display:block; top:128px; left:3px; font-size:6px;">${operator.organization}. Тел. ${operator.phone}</div>
</div>
');


--23-04-2009----------------------------------------------
CREATE OR REPLACE FUNCTION speedlimit_ins_fn(splimit_id_ int, account_id_ int) RETURNS void
    AS $$ 
BEGIN
    UPDATE billservice_accountspeedlimit SET speedlimit_id=splimit_id_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_accountspeedlimit(account_id, speedlimit_id) VALUES(account_id_,splimit_id_);
    END IF;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;
    
    
CREATE OR REPLACE FUNCTION shedulelog_co_fn(account_id_ int, accounttarif_id_ int, checkout_ timestamp without time zone) RETURNS void
    AS $$ 
BEGIN
    UPDATE billservice_shedulelog SET ballance_checkout=checkout_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_shedulelog(account_id, accounttarif_id, ballance_checkout) VALUES(account_id_,accounttarif_id_, checkout_);
    END IF;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;
    
    
CREATE OR REPLACE FUNCTION shedulelog_blocked_fn(account_id_ int, accounttarif_id_ int, blocked_ timestamp without time zone, cost_ double precision) RETURNS void
    AS $$ 
BEGIN
	UPDATE billservice_account SET balance_blocked=True WHERE id=account_id_ and ballance+credit<cost_;
    UPDATE billservice_shedulelog SET balance_blocked=blocked_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_shedulelog(account_id, accounttarif_id, balance_blocked) VALUES(account_id_,accounttarif_id_, blocked_);
    END IF;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;
    
    
CREATE OR REPLACE FUNCTION shedulelog_tr_reset_fn(account_id_ int, accounttarif_id_ int, reset_ timestamp without time zone) RETURNS void
    AS $$ 
BEGIN
	DELETE FROM billservice_accountprepaystrafic WHERE account_tarif_id=accounttarif_id_;
    UPDATE billservice_shedulelog SET prepaid_traffic_reset=reset_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_traffic_reset) VALUES(account_id_,accounttarif_id_, reset_);
    END IF;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION shedulelog_time_reset_fn(account_id_ int, accounttarif_id_ int, reset_ timestamp without time zone) RETURNS void
    AS $$ 
BEGIN
	DELETE FROM billservice_accountprepaystime WHERE account_tarif_id=accounttarif_id_;
    UPDATE billservice_shedulelog SET prepaid_time_reset=reset_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_time_reset) VALUES(account_id_,accounttarif_id_, reset_);
    END IF;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;


--23-04-2009----------------------------------------------
CREATE OR REPLACE FUNCTION speedlimit_ins_fn(splimit_id_ int, account_id_ int) RETURNS void
    AS $$ 
BEGIN
    UPDATE billservice_accountspeedlimit SET speedlimit_id=splimit_id_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_accountspeedlimit(account_id, speedlimit_id) VALUES(account_id_,splimit_id_);
    END IF;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;
    
    
CREATE OR REPLACE FUNCTION shedulelog_co_fn(account_id_ int, accounttarif_id_ int, checkout_ timestamp without time zone) RETURNS void
    AS $$ 
BEGIN
    UPDATE billservice_shedulelog SET ballance_checkout=checkout_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_shedulelog(account_id, accounttarif_id, ballance_checkout) VALUES(account_id_,accounttarif_id_, checkout_);
    END IF;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;
    
    
CREATE OR REPLACE FUNCTION shedulelog_blocked_fn(account_id_ int, accounttarif_id_ int, blocked_ timestamp without time zone, cost_ double precision) RETURNS void
    AS $$ 
BEGIN
	UPDATE billservice_account SET balance_blocked=True WHERE id=account_id_ and ballance+credit<cost_;
    UPDATE billservice_shedulelog SET balance_blocked=blocked_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_shedulelog(account_id, accounttarif_id, balance_blocked) VALUES(account_id_,accounttarif_id_, blocked_);
    END IF;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;
    
    
CREATE OR REPLACE FUNCTION shedulelog_tr_reset_fn(account_id_ int, accounttarif_id_ int, reset_ timestamp without time zone) RETURNS void
    AS $$ 
BEGIN
	DELETE FROM billservice_accountprepaystrafic WHERE account_tarif_id=accounttarif_id_;
    UPDATE billservice_shedulelog SET prepaid_traffic_reset=reset_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_traffic_reset) VALUES(account_id_,accounttarif_id_, reset_);
    END IF;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION shedulelog_time_reset_fn(account_id_ int, accounttarif_id_ int, reset_ timestamp without time zone) RETURNS void
    AS $$ 
BEGIN
	DELETE FROM billservice_accountprepaystime WHERE account_tarif_id=accounttarif_id_;
    UPDATE billservice_shedulelog SET prepaid_time_reset=reset_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_time_reset) VALUES(account_id_,accounttarif_id_, reset_);
    END IF;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;


    
    
CREATE OR REPLACE FUNCTION shedulelog_tr_credit_fn(account_id_ int, accounttarif_id_ int, trts_id_ int, datetime_ timestamp without time zone) RETURNS void
    AS $$ 
DECLARE
	prepaid_tr_id_ int;
	size_ double precision;
	count_ int := 0;
BEGIN
	
	FOR prepaid_tr_id_, size_ IN SELECT id, size FROM billservice_prepaidtraffic WHERE traffic_transmit_service_id=trts_id_ LOOP
    UPDATE billservice_accountprepaystrafic SET size=size+size_*1048576, datetime=datetime_ WHERE account_tarif_id=accounttarif_id_ AND prepaid_traffic_id=prepaid_tr_id_;
		IF NOT FOUND THEN
			INSERT INTO billservice_accountprepaystrafic (account_tarif_id, prepaid_traffic_id, size, datetime) VALUES(accounttarif_id_, prepaid_tr_id_, size_*1048576, datetime_);
        END IF;
        count_ := count_ + 1;
    END LOOP;
    IF count_ > 0 THEN
    	UPDATE billservice_shedulelog SET prepaid_traffic_accrued=datetime_ WHERE account_id=account_id_;
    	IF NOT FOUND THEN
        	INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_traffic_accrued) VALUES(account_id_,accounttarif_id_, datetime_);
    	END IF;
   	END IF;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;
    
    
    
    
CREATE OR REPLACE FUNCTION shedulelog_time_credit_fn(account_id_ int, accounttarif_id_ int, taccs_id_ int, size_ int, datetime_ timestamp without time zone) RETURNS void
    AS $$ 
BEGIN	
	UPDATE billservice_accountprepaystime SET size=size+size_, datetime=datetime_ WHERE account_tarif_id=accounttarif_id_; -- AND??
	IF NOT FOUND THEN
		INSERT INTO billservice_accountprepaystime (account_tarif_id, size, datetime, prepaid_time_service_id) VALUES(accounttarif_id_, size_, datetime_, taccs_id_);
    END IF;
	UPDATE billservice_shedulelog SET prepaid_time_accrued=datetime_ WHERE account_id=account_id_;
	IF NOT FOUND THEN
    	INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_time_accrued) VALUES(account_id_,accounttarif_id_, datetime_);
	END IF;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION accountipnspeed_ins_fn(account_id_ int, speed_ character varying, state_ boolean, datetime_ timestamp without time zone) RETURNS void
    AS $$ 
BEGIN
    UPDATE billservice_accountipnspeed SET speed=speed_, state=state_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_accountipnspeed(account_id, speed, state, datetime) VALUES(account_id_, speed_, state_, datetime_);
    END IF;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;

-- 13.05.2009 

ALTER TABLE billservice_tariff
   ADD COLUMN require_tarif_cost boolean;
   
ALTER TABLE billservice_tariff
   ALTER COLUMN require_tarif_cost SET DEFAULT False;
   
-- 15.05.2009
CREATE OR REPLACE FUNCTION return_allowed() RETURNS bigint     AS 
$$
BEGIN    
RETURN 0;
END;$$    
LANGUAGE plpgsql;
CREATE OR REPLACE FUNCTION check_allowed_users_trg_fn() RETURNS trigger    AS 
$$ 
DECLARE 
counted_num_ bigint;              
allowed_num_ bigint := 0;              
BEGIN              	
allowed_num_ := return_allowed();                
SELECT count(*) INTO counted_num_ FROM billservice_account;                
IF counted_num_ + 1 > allowed_num_ THEN  
RAISE EXCEPTION 'Amount of users[% + 1] will exceed allowed[%] for the license file!', counted_num_, allowed_num_;                
ELSE                     
RETURN NEW;                
END IF;                 
END; 
$$    
LANGUAGE plpgsql;
CREATE OR REPLACE FUNCTION crt_allowed_checker(allowed bigint) RETURNS void    AS 
$$
DECLARE    
allowed_ text := allowed::text;    
prev_ bigint  := 0;    
fn_tx1_    text := 'CREATE OR REPLACE FUNCTION return_allowed() RETURNS bigint AS ';    
fn_bd_tx1_ text := ' BEGIN RETURN ';    
fn_bd_tx2_ text := '; END;';    
fn_tx2_ text := ' LANGUAGE plpgsql VOLATILE COST 100;';
BEGIN        
prev_ := return_allowed();    
IF prev_ != allowed THEN    	
EXECUTE  fn_tx1_  || quote_literal(fn_bd_tx1_ || allowed_ || fn_bd_tx2_ ) || fn_tx2_;    
END IF;    
RETURN;
END;
$$    
LANGUAGE plpgsql;

-- 18.05.2009
ALTER TABLE billservice_groupstat ALTER bytes TYPE bigint;
ALTER TABLE billservice_groupstat ALTER classbytes TYPE bigint[];
DROP FUNCTION group_type1_fn(integer, integer, integer, timestamp without time zone, integer[], integer[], integer);
CREATE OR REPLACE FUNCTION group_type1_fn(group_id_ integer, account_id_ integer, octets_ bigint, datetime_ timestamp without time zone, classes_ integer[], classbytes_ bigint[], max_class_ integer)  RETURNS void AS
$BODY$
BEGIN    
INSERT INTO billservice_groupstat (group_id, account_id, bytes, datetime, classes, classbytes, max_class) VALUES (group_id_, account_id_, octets_, datetime_, classes_, classbytes_ , max_class_);
EXCEPTION WHEN unique_violation THEN    
UPDATE billservice_groupstat SET bytes=bytes+octets_ WHERE group_id=group_id_ AND account_id=account_id_ AND datetime=datetime_;
END;
$BODY$  
LANGUAGE 'plpgsql' VOLATILE  COST 100;  

DROP FUNCTION group_type2_fn(integer, integer, integer, timestamp without time zone, integer[], integer[], integer);

CREATE OR REPLACE FUNCTION group_type2_fn(group_id_ integer, account_id_ integer, octets_ bigint, datetime_ timestamp without time zone, classes_ integer[], classbytes_ bigint[], max_class_ integer)
  RETURNS void AS
$BODY$
DECLARE
    old_classes_ int[];
    old_classbytes_  bigint[];


    i int;
    ilen int;
    j int;
    max_ bigint;
    maxclass_ int;
    nbytes bigint;
    nclass int;
    --jlen int;
BEGIN
    INSERT INTO billservice_groupstat (group_id, account_id, bytes, datetime, classes, classbytes, max_class) VALUES (group_id_, account_id_, octets_, datetime_, classes_, classbytes_ , max_class_);
EXCEPTION WHEN unique_violation THEN
    SELECT classes, classbytes INTO old_classes_ ,old_classbytes_ FROM billservice_groupstat WHERE group_id=group_id_ AND account_id=account_id_ AND datetime=datetime_ FOR UPDATE;
    ilen := icount(classes_);
    max_ := 0;
    maxclass_ := NULL;
    --jlen := icount(old_classes_);
    FOR i IN 1..ilen LOOP
        nclass := classes_[i];
        nbytes := classbytes_[i];
        j := idx(old_classes_, nclass);
        IF j = 0 THEN
	    old_classes_ := array_append(old_classes_, nclass);
	    old_classbytes_ := array_append(old_classbytes_, nbytes);
	    IF nbytes > max_ THEN
	        max_ := nbytes;
	        maxclass_ := nclass;
	    END IF;
	ELSE
	    old_classbytes_[j] := old_classbytes_[j] + nbytes;
	    IF old_classbytes_[j] > max_ THEN
	        max_ := old_classbytes_[j];
	        maxclass_ := nclass;
	    END IF;
	END IF;      
    END LOOP;    
    UPDATE billservice_groupstat SET bytes=max_, max_class=maxclass_, classes=old_classes_, classbytes=old_classbytes_ WHERE group_id=group_id_ AND account_id=account_id_ AND datetime=datetime_;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
  
  
-- 19.05.2009


CREATE TABLE billservice_tpchangerule
(
  id serial NOT NULL,
  from_tariff_id integer NOT NULL,
  to_tariff_id integer NOT NULL,
  disabled boolean NOT NULL,
  "cost" numeric NOT NULL,
  ballance_min double precision NOT NULL,
  settlement_period_id integer DEFAULT 0,
  CONSTRAINT billservice_tpchangerule_pkey PRIMARY KEY (id),
  CONSTRAINT billservice_tpchangerule_from_tariff_id_fkey FOREIGN KEY (from_tariff_id)
      REFERENCES billservice_tariff (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT billservice_tpchangerule_settlement_period_id_fkey FOREIGN KEY (settlement_period_id)
      REFERENCES billservice_settlementperiod (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL,
  CONSTRAINT billservice_tpchangerule_to_tariff_id_fkey FOREIGN KEY (to_tariff_id)
      REFERENCES billservice_tariff (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED
)
WITH (OIDS=FALSE);
ALTER TABLE billservice_tpchangerule OWNER TO mikrobill;

-- Index: billservice_tpchangerule_from_tariff_id

-- DROP INDEX billservice_tpchangerule_from_tariff_id;

CREATE INDEX billservice_tpchangerule_from_tariff_id
  ON billservice_tpchangerule
  USING btree
  (from_tariff_id);

-- Index: billservice_tpchangerule_settlement_period_id_index

-- DROP INDEX billservice_tpchangerule_settlement_period_id_index;

CREATE INDEX billservice_tpchangerule_settlement_period_id_index
  ON billservice_tpchangerule
  USING btree
  (settlement_period_id);

-- Index: billservice_tpchangerule_tariff_tariff

-- DROP INDEX billservice_tpchangerule_tariff_tariff;

CREATE UNIQUE INDEX billservice_tpchangerule_tariff_tariff
  ON billservice_tpchangerule
  USING btree
  (from_tariff_id, to_tariff_id);

-- Index: billservice_tpchangerule_to_tariff_id

-- DROP INDEX billservice_tpchangerule_to_tariff_id;

CREATE INDEX billservice_tpchangerule_to_tariff_id
  ON billservice_tpchangerule
  USING btree
  (to_tariff_id);
  

ALTER TABLE billservice_account ALTER ballance TYPE decimal;
ALTER TABLE billservice_account ALTER credit TYPE decimal;
ALTER TABLE billservice_card ALTER nominal TYPE decimal;
ALTER TABLE billservice_dealer ALTER prepayment TYPE decimal;
ALTER TABLE billservice_dealer ALTER discount TYPE decimal;
ALTER TABLE billservice_dealerpay ALTER pay TYPE decimal;
ALTER TABLE billservice_onetimeservice ALTER cost TYPE decimal;
ALTER TABLE billservice_onetimeservicehistory ALTER summ TYPE decimal;
ALTER TABLE billservice_periodicalservice ALTER cost TYPE decimal;
ALTER TABLE billservice_periodicalservicehistory ALTER summ TYPE decimal;
ALTER TABLE billservice_salecard ALTER sum_for_pay TYPE decimal;
ALTER TABLE billservice_salecard ALTER discount TYPE decimal;
ALTER TABLE billservice_salecard ALTER discount_sum TYPE decimal;
ALTER TABLE billservice_salecard ALTER prepayment TYPE decimal;
ALTER TABLE billservice_tariff ALTER cost TYPE decimal;
ALTER TABLE billservice_timeaccessnode ALTER cost TYPE decimal;
ALTER TABLE billservice_timetransaction ALTER summ TYPE decimal;
ALTER TABLE billservice_traffictransmitnodes ALTER cost TYPE decimal;
ALTER TABLE billservice_traffictransaction ALTER summ TYPE decimal;
ALTER TABLE billservice_transaction ALTER summ TYPE decimal;
ALTER TABLE billservice_tpchangerule ALTER cost TYPE decimal;

ALTER TABLE billservice_prepaidtraffic ALTER size TYPE bigint;
ALTER TABLE billservice_accountprepaystrafic ALTER size TYPE bigint;
ALTER TABLE billservice_trafficlimit ALTER size TYPE bigint;


DROP FUNCTION credit_account(integer, double precision);

CREATE OR REPLACE FUNCTION credit_account(account_id integer, sum decimal)
  RETURNS void AS
$BODY$
BEGIN
	UPDATE billservice_account SET ballance=ballance-sum WHERE id=account_id;
RETURN;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
  
DROP FUNCTION debit_account(integer, double precision);

CREATE OR REPLACE FUNCTION debit_account(account_id integer, sum decimal)
  RETURNS void AS
$BODY$
BEGIN
	UPDATE billservice_account SET ballance=ballance+sum WHERE id=account_id;
RETURN;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
  
  
DROP FUNCTION periodicaltr_fn(integer, integer, integer, character varying, double precision, timestamp without time zone, integer);

CREATE OR REPLACE FUNCTION periodicaltr_fn(ps_id_ integer, acctf_id_ integer, account_id_ integer, type_id_ character varying, summ_ decimal, created_ timestamp without time zone, ps_condition_type_ integer)
  RETURNS void AS
$BODY$
DECLARE
    new_summ_ decimal;
BEGIN
    SELECT INTO new_summ_ summ_*(NOT EXISTS (SELECT id FROM billservice_suspendedperiod WHERE account_id=account_id AND (created_ BETWEEN start_date AND end_date)))::int;
    IF (ps_condition_type_ = 1) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance >= 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    ELSIF (ps_condition_type_ = 2) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance < 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    END IF; 
    INSERT INTO billservice_periodicalservicehistory (service_id, accounttarif_id,account_id, type_id, summ, datetime) VALUES (ps_id_, acctf_id_, account_id_, type_id_, new_summ_, created_);
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
  
DROP FUNCTION shedulelog_blocked_fn(integer, integer, timestamp without time zone, double precision);

CREATE OR REPLACE FUNCTION shedulelog_blocked_fn(account_id_ integer, accounttarif_id_ integer, blocked_ timestamp without time zone, cost_ decimal)
  RETURNS void AS
$BODY$ 
BEGIN
	UPDATE billservice_account SET balance_blocked=True WHERE id=account_id_ and ballance+credit<cost_;
    UPDATE billservice_shedulelog SET balance_blocked=blocked_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_shedulelog(account_id, accounttarif_id, balance_blocked) VALUES(account_id_,accounttarif_id_, blocked_);
    END IF;
    RETURN;  
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
  
  
  
DROP FUNCTION shedulelog_tr_credit_fn(integer, integer, integer, timestamp without time zone);

CREATE OR REPLACE FUNCTION shedulelog_tr_credit_fn(account_id_ integer, accounttarif_id_ integer, trts_id_ integer, datetime_ timestamp without time zone)
  RETURNS void AS
$BODY$ 
DECLARE
	prepaid_tr_id_ int;
	size_ bigint;
	count_ int := 0;
BEGIN
	
	FOR prepaid_tr_id_, size_ IN SELECT id, size FROM billservice_prepaidtraffic WHERE traffic_transmit_service_id=trts_id_ LOOP
		UPDATE billservice_accountprepaystrafic SET size=size+size_, datetime=datetime_ WHERE account_tarif_id=accounttarif_id_ AND prepaid_traffic_id=prepaid_tr_id_;
		IF NOT FOUND THEN
			INSERT INTO billservice_accountprepaystrafic (account_tarif_id, prepaid_traffic_id, size, datetime) VALUES(accounttarif_id_, prepaid_tr_id_, size_, datetime_);
        END IF;
        count_ := count_ + 1;
    END LOOP;
    IF count_ > 0 THEN
    	UPDATE billservice_shedulelog SET prepaid_traffic_accrued=datetime_ WHERE account_id=account_id_;
    	IF NOT FOUND THEN
        	INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_traffic_accrued) VALUES(account_id_,accounttarif_id_, datetime_);
    	END IF;
   	END IF;
    RETURN;  
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
  
  
DROP FUNCTION transaction_block_sum(integer, timestamp without time zone, timestamp without time zone);
  
CREATE OR REPLACE FUNCTION transaction_block_sum(account_id_ integer, start_date_ timestamp without time zone, end_date_ timestamp without time zone)
  RETURNS decimal AS
$BODY$ 
DECLARE
    start_date_5m_ timestamp without time zone;
    result_ decimal;
BEGIN
    start_date_5m_ := date_trunc('minute', start_date_) - interval '1 min' * (date_part('min', start_date_)::int % 5); 
    SELECT INTO result_ sum(ssum) FROM (SELECT sum(summ) AS ssum FROM billservice_transaction WHERE account_id=account_id_ AND (summ > 0) AND (created BETWEEN start_date_ AND end_date_) UNION ALL SELECT sum(summ) AS ssum FROM billservice_traffictransaction WHERE account_id=account_id_ AND (summ > 0) AND (datetime BETWEEN start_date_ AND end_date_) UNION ALL SELECT sum(summ) AS ssum FROM billservice_timetransaction WHERE account_id=account_id_ AND (summ > 0) AND (datetime BETWEEN start_date_ AND end_date_) UNION ALL SELECT sum(summ) AS ssum FROM billservice_periodicalservicehistory WHERE account_id=account_id_ AND (summ > 0) AND (datetime BETWEEN start_date_ AND end_date_)  UNION ALL SELECT sum(summ) AS ssum FROM billservice_onetimeservicehistory WHERE account_id=account_id_ AND (summ > 0) AND (datetime BETWEEN start_date_ AND end_date_)) AS ts_union ;
    RETURN result_;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
  
  
DROP FUNCTION transaction_sum(integer, integer, timestamp without time zone, timestamp without time zone);

CREATE OR REPLACE FUNCTION transaction_sum(account_id_ integer, acctf_id_ integer, start_date_ timestamp without time zone, end_date_ timestamp without time zone)
  RETURNS decimal AS
$BODY$ 
DECLARE
    start_date_5m_ timestamp without time zone;
    result_ decimal;
BEGIN
    start_date_5m_ := date_trunc('minute', start_date_) - interval '1 min' * (date_part('min', start_date_)::int % 5); 
    SELECT INTO result_ sum(ssum) FROM (SELECT sum(summ) AS ssum FROM billservice_transaction WHERE account_id=account_id_ AND (accounttarif_id=acctf_id_) AND (summ > 0)  AND (created > start_date_ AND created < end_date_) UNION ALL SELECT sum(summ) AS ssum FROM billservice_traffictransaction WHERE account_id=account_id_ AND (accounttarif_id=acctf_id_) AND (summ > 0)  AND (datetime > start_date_ AND datetime < end_date_)UNION ALL SELECT sum(summ) AS ssum FROM billservice_timetransaction WHERE account_id=account_id_ AND (accounttarif_id=acctf_id_) AND (summ > 0)  AND (datetime > start_date_ AND datetime < end_date_)  UNION ALL SELECT sum(summ) AS ssum FROM billservice_periodicalservicehistory WHERE account_id=account_id_ AND (accounttarif_id=acctf_id_) AND (summ > 0)  AND (datetime > start_date_ AND datetime < end_date_)  UNION ALL SELECT sum(summ) AS ssum FROM billservice_onetimeservicehistory WHERE account_id=account_id_ AND (accounttarif_id=acctf_id_) AND (summ > 0)  AND (datetime > start_date_ AND datetime < end_date_)) AS ts_union ;
    RETURN result_;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
  
-- 23.05.2009

ALTER TABLE billservice_onetimeservicehistory ALTER account_id DROP NOT NULL;
ALTER TABLE billservice_onetimeservicehistory ALTER onetimeservice_id DROP NOT NULL;

ALTER TABLE billservice_periodicalservicehistory ALTER account_id DROP NOT NULL;
ALTER TABLE billservice_periodicalservicehistory ALTER service_id DROP NOT NULL;

ALTER TABLE billservice_timetransaction ALTER account_id DROP NOT NULL;
ALTER TABLE billservice_timetransaction ALTER session_id DROP NOT NULL;

ALTER TABLE billservice_traffictransaction ALTER account_id DROP NOT NULL;
ALTER TABLE billservice_traffictransaction ALTER traffictransmitservice_id DROP NOT NULL;

ALTER TABLE billservice_transaction ALTER account_id DROP NOT NULL;
ALTER TABLE billservice_transaction ALTER systemuser_id DROP NOT NULL;
  
-- 01.06.2009

CREATE OR REPLACE FUNCTION shedulelog_blocked_fn(account_id_ integer, accounttarif_id_ integer, blocked_ timestamp without time zone, cost_ decimal)
  RETURNS void AS
$BODY$ 
BEGIN
	UPDATE billservice_account SET balance_blocked=True WHERE id=account_id_ and ballance+credit<cost_;
    UPDATE billservice_shedulelog SET balance_blocked=blocked_, accounttarif_id=accounttarif_id_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_shedulelog(account_id, accounttarif_id, balance_blocked) VALUES(account_id_,accounttarif_id_, blocked_);
    END IF;
    RETURN;  
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
  
  
  
DROP FUNCTION shedulelog_tr_credit_fn(integer, integer, integer, timestamp without time zone);

CREATE OR REPLACE FUNCTION shedulelog_tr_credit_fn(account_id_ integer, accounttarif_id_ integer, trts_id_ integer, datetime_ timestamp without time zone)
  RETURNS void AS
$BODY$ 
DECLARE
	prepaid_tr_id_ int;
	size_ bigint;
	count_ int := 0;
BEGIN
	
	FOR prepaid_tr_id_, size_ IN SELECT id, size FROM billservice_prepaidtraffic WHERE traffic_transmit_service_id=trts_id_ LOOP
		UPDATE billservice_accountprepaystrafic SET size=size+size_, datetime=datetime_ WHERE account_tarif_id=accounttarif_id_ AND prepaid_traffic_id=prepaid_tr_id_;
		IF NOT FOUND THEN
			INSERT INTO billservice_accountprepaystrafic (account_tarif_id, prepaid_traffic_id, size, datetime) VALUES(accounttarif_id_, prepaid_tr_id_, size_, datetime_);
        END IF;
        count_ := count_ + 1;
    END LOOP;
    IF count_ > 0 THEN
    	UPDATE billservice_shedulelog SET prepaid_traffic_accrued=datetime_, accounttarif_id=accounttarif_id_ WHERE account_id=account_id_;
    	IF NOT FOUND THEN
        	INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_traffic_accrued) VALUES(account_id_,accounttarif_id_, datetime_);
    	END IF;
   	END IF;
    RETURN;  
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
  
CREATE OR REPLACE FUNCTION shedulelog_co_fn(account_id_ int, accounttarif_id_ int, checkout_ timestamp without time zone) RETURNS void
    AS $$ 
BEGIN
    UPDATE billservice_shedulelog SET ballance_checkout=checkout_, accounttarif_id=accounttarif_id_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_shedulelog(account_id, accounttarif_id, ballance_checkout) VALUES(account_id_,accounttarif_id_, checkout_);
    END IF;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;

    
    
CREATE OR REPLACE FUNCTION shedulelog_tr_reset_fn(account_id_ int, accounttarif_id_ int, reset_ timestamp without time zone) RETURNS void
    AS $$ 
BEGIN
	DELETE FROM billservice_accountprepaystrafic WHERE account_tarif_id=accounttarif_id_;
    UPDATE billservice_shedulelog SET prepaid_traffic_reset=reset_, accounttarif_id=accounttarif_id_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_traffic_reset) VALUES(account_id_,accounttarif_id_, reset_);
    END IF;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION shedulelog_time_reset_fn(account_id_ int, accounttarif_id_ int, reset_ timestamp without time zone) RETURNS void
    AS $$ 
BEGIN
	DELETE FROM billservice_accountprepaystime WHERE account_tarif_id=accounttarif_id_;
    UPDATE billservice_shedulelog SET prepaid_time_reset=reset_, accounttarif_id=accounttarif_id_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_time_reset) VALUES(account_id_,accounttarif_id_, reset_);
    END IF;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;

    
    
CREATE OR REPLACE FUNCTION shedulelog_time_credit_fn(account_id_ int, accounttarif_id_ int, taccs_id_ int, size_ int, datetime_ timestamp without time zone) RETURNS void
    AS $$ 
BEGIN	
	UPDATE billservice_accountprepaystime SET size=size+size_, datetime=datetime_ WHERE account_tarif_id=accounttarif_id_; -- AND??
	IF NOT FOUND THEN
		INSERT INTO billservice_accountprepaystime (account_tarif_id, size, datetime, prepaid_time_service_id) VALUES(accounttarif_id_, size_, datetime_, taccs_id_);
    END IF;
	UPDATE billservice_shedulelog SET prepaid_time_accrued=datetime_, accounttarif_id=accounttarif_id_ WHERE account_id=account_id_;
	IF NOT FOUND THEN
    	INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_time_accrued) VALUES(account_id_,accounttarif_id_, datetime_);
	END IF;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;
    
--02.06.2009 14:26
CREATE TABLE billservice_radiusattrs
(
  id serial NOT NULL,
  tarif_id integer NOT NULL,
  vendor integer NOT NULL,
  attrid integer NOT NULL,
  "value" character varying(255) NOT NULL,
  CONSTRAINT billservice_radiusattrs_pkey PRIMARY KEY (id),
  CONSTRAINT billservice_radiusattrs_tarif_id_fkey FOREIGN KEY (tarif_id)
      REFERENCES billservice_tariff (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED
)
WITH (OIDS=FALSE);
ALTER TABLE billservice_radiusattrs OWNER TO mikrobill;

-- Index: billservice_radiusattrs_tarif_id

-- DROP INDEX billservice_radiusattrs_tarif_id;

CREATE INDEX billservice_radiusattrs_tarif_id
  ON billservice_radiusattrs
  USING btree
  (tarif_id);

ALTER TABLE billservice_radiusattrs
   ALTER COLUMN vendor SET DEFAULT 0;
ALTER TABLE billservice_radiusattrs
   ALTER COLUMN vendor DROP NOT NULL;

-- 16.06.2009 17:06

CREATE OR REPLACE FUNCTION card_activate_fn(login_ character varying, pin_ character varying, nas_id_ integer, account_ip_ inet)
  RETURNS record AS
$BODY$
DECLARE
    tarif_id_ int;
    account_id_ int;
    card_id_ int;
    sold_ timestamp without time zone;
    activated_ timestamp without time zone;
    card_data_ record;
    account_data_ record;
    tmp record;
BEGIN
    -- Получаем финормацию о карточке, которая прдана и у которой не истёк срок годности
    SELECT id, sold, activated, activated_by_id, nominal, tarif_id INTO card_data_ FROM billservice_card WHERE "login"=login_ and pin=pin_ and sold is not Null and now() between start_date and end_date;
    -- Если карты нету - return
    IF card_data_ is NULL THEN
	RETURN tmp;
    -- Если карта уже продана, но ещё не активирвоана
    ELSIF card_data_.activated_by_id IS NULL and card_data_.sold is not NULL THEN
	-- Создаём пользователя
        INSERT INTO billservice_account(username, "password", nas_id, ipn_ip_address, ipn_status, status, created, ipn_added, allow_webcab, allow_expresscards, assign_dhcp_null, assign_dhcp_block, allow_vpn_null, allow_vpn_block)
        VALUES(login_, pin_, nas_id_, account_ip_, False, True, now(), False, True, True, False, False, False, False) RETURNING id INTO account_id_;
      
	-- Добавлеяем пользователю тариф
        INSERT INTO billservice_accounttarif(account_id, tarif_id, datetime) VALUES(account_id_, card_data_.tarif_id, now());
        -- Пополняем счёт
        INSERT INTO billservice_transaction(bill, account_id, type_id, approved, tarif_id, summ, description, created)
        VALUES('Карта доступа', account_id_, 'ACCESS_CARD', True, card_data_.tarif_id, card_data_.nominal*(-1),'', now());
	-- Обновляем информацию о карточке
	UPDATE billservice_card SET activated = now(), activated_by_id = account_id_ WHERE id = card_data_.id;
	
	-- Обновляем информацию о IP-адресе пользователя
	UPDATE billservice_account SET ipn_ip_address = account_ip_ WHERE id = account_id_;
	-- Выбираем нужную информацию
	SELECT account.id, account.password, account.nas_id, bsat.tarif_id,  account.status, 
	account.balance_blocked, (account.ballance+account.credit) as ballance, account.disabled_by_limit, 
	tariff.active INTO account_data_ 
	FROM billservice_account as account
	JOIN billservice_accounttarif as bsat ON bsat.account_id=account.id
	JOIN billservice_tariff as tariff on tariff.id=bsat.tarif_id
	WHERE  account.id=account_id_ AND 
	account.ballance+account.credit>0
	ORDER BY bsat.datetime DESC LIMIT 1;
	RETURN account_data_;
    -- Если карта продана и уже активирована
    ELSIF (card_data_.sold is not Null) AND (card_data_.activated_by_id is not Null) THEN
	SELECT account.id, account.password, account.nas_id, bsat.tarif_id,  account.status, 
	account.balance_blocked, (account.ballance+account.credit) as ballance, account.disabled_by_limit, 
	tariff.active INTO account_data_
	FROM billservice_account as account
	JOIN billservice_accounttarif as bsat ON bsat.account_id=account.id
	JOIN billservice_tariff as tariff on tariff.id=bsat.tarif_id
	WHERE  bsat.datetime<now() and account.id=card_data_.activated_by_id AND 
	account.ballance+account.credit>0
	AND
	((account.balance_blocked=False and account.disabled_by_limit=False and account.status=True))=True 
	ORDER BY bsat.datetime DESC LIMIT 1;
	RETURN account_data_;
    END IF; 

    RETURN tmp;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
ALTER FUNCTION card_activate_fn(character varying, character varying, integer, inet) OWNER TO ebs;

-- 16.06.2009 18.51
ALTER TABLE radius_session ADD COLUMN transaction_id bigint;


ALTER TABLE radius_session
  ADD CONSTRAINT radius_session_transaction_id_fkey FOREIGN KEY (transaction_id)
      REFERENCES billservice_timetransaction (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE billservice_timetransaction DROP COLUMN session_id;

CREATE INDEX radius_session_account_session_interrim_idx
  ON radius_session
  USING btree
  (account_id, sessionid, interrim_update);
  
  
CREATE OR REPLACE FUNCTION timetransaction_insert(taccs_id_ int, accounttarif_id_ int, account_id_ int, summ_ decimal, datetime_ timestamp without time zone, sessionid_ character varying(32), interrim_update_ timestamp without time zone) RETURNS void
    AS $$ 
DECLARE
	datetime_agg_ timestamp without time zone;
	ins_tr_id_ int;
BEGIN	

    datetime_agg_ := date_trunc('minute', datetime_) - interval '1 min' * (date_part('min', datetime_)::int % 5); 
    UPDATE billservice_timetransaction SET summ=summ+summ_ WHERE timeaccessservice_id=taccs_id_ AND account_id=account_id_ AND datetime=datetime_agg_ RETURNING id INTO ins_tr_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_timetransaction(timeaccessservice_id, accounttarif_id, account_id, summ, datetime) VALUES (taccs_id_, accounttarif_id_, account_id_, summ_, datetime_agg_) RETURNING id INTO ins_tr_id_;
    END IF;
	UPDATE radius_session SET transaction_id=ins_tr_id_ WHERE account_id=account_id_ AND sessionid=sessionid_ AND interrim_update=interrim_update_;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;

-- 03.07.2009 21:43

CREATE OR REPLACE FUNCTION psh_crt_pdb(datetx date)
  RETURNS integer AS
$BODY$
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
                     CREATE TRIGGER acc_psh_trg AFTER UPDATE OR DELETE ON psh#rpdate# FOR EACH ROW EXECUTE PROCEDURE account_transaction_trg_fn();
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
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
ALTER FUNCTION psh_crt_pdb(date) OWNER TO ebs;

-- 15.07.2009

DROP RULE on_tariff_delete_rule ON billservice_tariff;


  
  
CREATE OR REPLACE FUNCTION clear_tariff_services_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN
	
	IF OLD.traffic_transmit_service_id NOTNULL THEN
	    DELETE FROM billservice_traffictransmitservice WHERE id=OLD.traffic_transmit_service_id;
	END IF;
	
	IF OLD.time_access_service_id NOTNULL THEN
	    DELETE FROM billservice_timeaccessservice WHERE id=OLD.time_access_service_id;   
	RETURN OLD;
	END IF;
	
	 IF OLD.access_parameters_id NOTNULL THEN
            DELETE FROM billservice_accessparameters WHERE id=OLD.access_parameters_id;
        END IF;
RETURN OLD;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
  
--CREATE TRIGGER clear_tariff_services_trg
-- BEFORE DELETE
--  ON billservice_tariff
--  FOR EACH ROW
--  EXECUTE PROCEDURE clear_tariff_services_trg_fn();
  
    
CREATE OR REPLACE FUNCTION set_deleted_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN
	IF OLD.deleted IS TRUE THEN
	    RETURN OLD;
	ELSE
        UPDATE billservice_tariff SET deleted=TRUE WHERE id=OLD.id;
	    RETURN NULL;
	END IF;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;

CREATE TRIGGER a_set_deleted_trg
  BEFORE DELETE
  ON billservice_tariff
  FOR EACH ROW
  EXECUTE PROCEDURE set_deleted_trg_fn();

ALTER TABLE billservice_shedulelog DROP CONSTRAINT billservice_shedulelog_accounttarif_id_fkey;

ALTER TABLE billservice_shedulelog
  ADD CONSTRAINT billservice_shedulelog_accounttarif_id_fkey FOREIGN KEY (accounttarif_id)
      REFERENCES billservice_accounttarif (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;
      
----28.07.2009 14:14
ALTER TABLE billservice_account
   ADD COLUMN associate_pptp_ipn_ip boolean;

--UPDATE billservice_account SET associate_pptp_ipn_ip=FALSE;
ALTER TABLE billservice_account
   ALTER COLUMN associate_pptp_ipn_ip SET NOT NULL;
   
ALTER TABLE billservice_account
   ALTER COLUMN associate_pptp_ipn_ip SET DEFAULT False;

ALTER TABLE billservice_account
   ADD COLUMN associate_pppoe_mac boolean;

--UPDATE billservice_account SET associate_pppoe_mac=FALSE;
ALTER TABLE billservice_account
   ALTER COLUMN associate_pppoe_mac SET NOT NULL;
   
ALTER TABLE billservice_account
   ALTER COLUMN associate_pppoe_mac SET DEFAULT False;

ALTER TABLE billservice_account ALTER COLUMN status DROP DEFAULT;

ALTER TABLE billservice_account ALTER COLUMN status TYPE int  USING case when status then 1 else 2 end;

ALTER TABLE billservice_account
   ALTER COLUMN status SET DEFAULT 1;
   
UPDATE billservice_account SET status = 1;

ALTER TABLE billservice_suspendedperiod
   ALTER COLUMN end_date DROP NOT NULL;


-- 31.07.2009 18:00
ALTER TABLE billservice_suspendedperiod ALTER start_date TYPE timestamp without time zone;

ALTER TABLE billservice_suspendedperiod ALTER end_date TYPE timestamp without time zone;


-- 07.08.2009 14:20
ALTER TABLE radius_activesession ADD COLUMN nas_int_id integer;

ALTER TABLE billservice_account   ADD COLUMN contactperson_phone character varying;

ALTER TABLE billservice_account   ALTER COLUMN contactperson_phone SET DEFAULT '';

CREATE TABLE billservice_x8021(  
id serial NOT NULL,  
account_id integer,  
nas_id integer NOT NULL,  
port smallint,  
typeauth character varying(32) NOT NULL,  
vlan_accept integer,  
vlan_reject integer,  
simpleauth boolean NOT NULL,  
CONSTRAINT billservice_x8021_pkey PRIMARY KEY (id),  
CONSTRAINT billservice_x8021_account_id_fkey FOREIGN KEY (account_id)      
    REFERENCES billservice_account (id) MATCH SIMPLE      
    ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,  
CONSTRAINT billservice_x8021_nas_id_fkey FOREIGN KEY (nas_id)      
    REFERENCES nas_nas (id) MATCH SIMPLE      
    ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED)WITH (OIDS=FALSE);ALTER TABLE billservice_x8021 OWNER TO ebs;
    
-- Index: billservice_x8021_account_id-- 
--DROP INDEX billservice_x8021_account_id;
CREATE INDEX billservice_x8021_account_id  ON billservice_x8021  USING btree  (account_id);
-- Index: billservice_x8021_nas_id-- 
--
DROP INDEX billservice_x8021_nas_id;

CREATE INDEX billservice_x8021_nas_id  ON billservice_x8021  USING btree  (nas_id);  

ALTER TABLE billservice_account   ADD COLUMN "comment" character varying;

ALTER TABLE billservice_speedlimit ADD COLUMN speed_units character varying(10);


ALTER TABLE billservice_speedlimit ALTER COLUMN speed_units SET STORAGE EXTENDED;ALTER TABLE billservice_speedlimit ALTER COLUMN speed_units SET NOT NULL;

ALTER TABLE billservice_speedlimit ALTER COLUMN speed_units SET DEFAULT 'Kbps'::character varying;ALTER TABLE billservice_speedlimit ADD COLUMN change_speed_type character varying(20);

ALTER TABLE billservice_speedlimit ALTER COLUMN change_speed_type SET STORAGE EXTENDED;ALTER TABLE billservice_speedlimit ALTER COLUMN change_speed_type SET DEFAULT 'add'::character varying;


-- 11.08.2009 15:47

ALTER TABLE billservice_accounttarif ADD COLUMN periodical_billed boolean DEFAULT FALSE;

UPDATE billservice_accounttarif SET periodical_billed=FALSE;

UPDATE billservice_accounttarif as acctf1 SET periodical_billed=TRUE WHERE acctf1.id in (SELECT acctf2.id FROM billservice_accounttarif AS acctf2 WHERE acctf2.account_id=acctf1.account_id and acctf2.datetime < (SELECT datetime FROM billservice_accounttarif AS att WHERE att.account_id=acctf1.account_id and att.datetime<now()ORDER BY datetime DESC LIMIT 1));





CREATE TABLE billservice_addonservice
(
  id serial NOT NULL,
  "name" character varying(255) NOT NULL,
  allow_activation boolean NOT NULL,
  service_type character varying(32) NOT NULL,
  sp_type character varying(32) DEFAULT '',
  sp_period_id integer NOT NULL,
  timeperiod_id integer NOT NULL,
  "cost" numeric(60,10) NOT NULL,
  cancel_subscription boolean NOT NULL,
  wyte_period_id integer NOT NULL,
  wyte_cost numeric(60,10) NOT NULL,
  "action" boolean NOT NULL,
  nas_id integer DEFAULT NULL,
  service_activation_action character varying(8000) NOT NULL,
  service_deactivation_action character varying(8000) NOT NULL,
  deactivate_service_for_blocked_account boolean NOT NULL,
  change_speed boolean NOT NULL,
  change_speed_type character varying(32) NOT NULL,
  speed_units character varying(32) NOT NULL,
  max_tx integer DEFAULT 0,
  max_rx integer DEFAULT 0,
  burst_tx integer DEFAULT 0,
  burst_rx integer DEFAULT 0,
  burst_treshold_tx integer DEFAULT 0,
  burst_treshold_rx integer DEFAULT 0,
  burst_time_tx integer DEFAULT 0,
  burst_time_rx integer DEFAULT 0,
  min_tx integer DEFAULT 0,
  min_rx integer DEFAULT 0,
  priority integer DEFAULT 8,
  CONSTRAINT billservice_addonservice_pkey PRIMARY KEY (id),
  CONSTRAINT billservice_addonservice_nas_id_fkey FOREIGN KEY (nas_id)
      REFERENCES nas_nas (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT billservice_addonservice_sp_period_id_fkey FOREIGN KEY (sp_period_id)
      REFERENCES billservice_settlementperiod (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT billservice_addonservice_timeperiod_id_fkey FOREIGN KEY (timeperiod_id)
      REFERENCES billservice_timeperiod (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT billservice_addonservice_wyte_period_id_fkey FOREIGN KEY (wyte_period_id)
      REFERENCES billservice_settlementperiod (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED
)
WITH (OIDS=FALSE);
ALTER TABLE billservice_addonservice OWNER TO ebs;

-- Index: billservice_addonservice_nas_id

-- DROP INDEX billservice_addonservice_nas_id;

CREATE INDEX billservice_addonservice_nas_id
  ON billservice_addonservice
  USING btree
  (nas_id);

-- Index: billservice_addonservice_sp_period_id

-- DROP INDEX billservice_addonservice_sp_period_id;

CREATE INDEX billservice_addonservice_sp_period_id
  ON billservice_addonservice
  USING btree
  (sp_period_id);

-- Index: billservice_addonservice_timeperiod_id

-- DROP INDEX billservice_addonservice_timeperiod_id;

CREATE INDEX billservice_addonservice_timeperiod_id
  ON billservice_addonservice
  USING btree
  (timeperiod_id);

-- Index: billservice_addonservice_wyte_period_id

-- DROP INDEX billservice_addonservice_wyte_period_id;

CREATE INDEX billservice_addonservice_wyte_period_id
  ON billservice_addonservice
  USING btree
  (wyte_period_id);



CREATE TABLE billservice_addonservicetarif
(
  id serial NOT NULL,
  tarif_id integer NOT NULL,
  service_id integer NOT NULL,
  activation_count integer DEFAULT 0,
  activation_count_period_id integer DEFAULT NULL,
  CONSTRAINT billservice_addonservicetarif_pkey PRIMARY KEY (id),
  CONSTRAINT billservice_addonservicetarif_activation_count_period_id_fkey FOREIGN KEY (activation_count_period_id)
      REFERENCES billservice_settlementperiod (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT billservice_addonservicetarif_service_id_fkey FOREIGN KEY (service_id)
      REFERENCES billservice_addonservice (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT billservice_addonservicetarif_tarif_id_fkey FOREIGN KEY (tarif_id)
      REFERENCES billservice_tariff (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED
)
WITH (OIDS=FALSE);
ALTER TABLE billservice_addonservicetarif OWNER TO ebs;

-- Index: billservice_addonservicetarif_activation_count_period_id

-- DROP INDEX billservice_addonservicetarif_activation_count_period_id;

CREATE INDEX billservice_addonservicetarif_activation_count_period_id
  ON billservice_addonservicetarif
  USING btree
  (activation_count_period_id);

-- Index: billservice_addonservicetarif_service_id

-- DROP INDEX billservice_addonservicetarif_service_id;

CREATE INDEX billservice_addonservicetarif_service_id
  ON billservice_addonservicetarif
  USING btree
  (service_id);

-- Index: billservice_addonservicetarif_tarif_id

-- DROP INDEX billservice_addonservicetarif_tarif_id;

CREATE INDEX billservice_addonservicetarif_tarif_id
  ON billservice_addonservicetarif
  USING btree
  (tarif_id);
  


CREATE TABLE billservice_accountaddonservice
(
  id serial NOT NULL,
  service_id integer NOT NULL,
  account_id integer NOT NULL,
  activated timestamp without time zone NOT NULL,
  deactivated timestamp without time zone,
  action_status boolean DEFAULT false,
  speed_status boolean DEFAULT false,
  temporary_blocked timestamp without time zone,
  last_checkout timestamp without time zone,
  CONSTRAINT billservice_accountaddonservice_pkey PRIMARY KEY (id),
  CONSTRAINT billservice_accountaddonservice_account_id_fkey FOREIGN KEY (account_id)
      REFERENCES billservice_account (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT billservice_accountaddonservice_service_id_fkey FOREIGN KEY (service_id)
      REFERENCES billservice_addonservice (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED
)
WITH (OIDS=FALSE);
ALTER TABLE billservice_accountaddonservice OWNER TO ebs;

-- Index: billservice_accountaddonservice_account_id

-- DROP INDEX billservice_accountaddonservice_account_id;

CREATE INDEX billservice_accountaddonservice_account_id
  ON billservice_accountaddonservice
  USING btree
  (account_id);

-- Index: billservice_accountaddonservice_service_id

-- DROP INDEX billservice_accountaddonservice_service_id;

CREATE INDEX billservice_accountaddonservice_service_id
  ON billservice_accountaddonservice
  USING btree
  (service_id);



---16.08.2009 16:22
CREATE OR REPLACE FUNCTION check_allowed_users_trg_fn() RETURNS trigger    AS
$$
DECLARE counted_num_ bigint;
  allowed_num_ bigint := 0;
BEGIN
  allowed_num_ := return_allowed();
  SELECT count(*) INTO counted_num_ FROM billservice_account;
  IF counted_num_ + 1 > allowed_num_ THEN
  RAISE EXCEPTION 'Amount of users[% + 1] will exceed allowed[%] for the license file!', counted_num_, allowed_num_;
  ELSE
  RETURN NEW;
  END IF;
  END;
$$
LANGUAGE plpgsql;

CREATE UNIQUE INDEX billservice_transactiontype_ind
   ON billservice_transactiontype (id);


INSERT INTO billservice_transactiontype(id,
             "name", internal_name)
    VALUES (11,'Списание средств за преждевременное отключение услуги абонентом', 'ADDONSERVICE_WYTE_PAY');

CREATE TABLE billservice_addonservicetransaction
(
  id serial NOT NULL,
  service_id integer NOT NULL,
  service_type character varying(32) NOT NULL,
  account_id integer NOT NULL,
  accountaddonservice_id integer NOT NULL,
  accounttarif_id integer NOT NULL,
  summ numeric NOT NULL,
  created timestamp without time zone NOT NULL,
  type_id character varying(255) NOT NULL,
  CONSTRAINT billservice_addonservicetransaction_pkey PRIMARY KEY (id),
  CONSTRAINT billservice_addonservicetransaction_account_id_fkey FOREIGN KEY (account_id)
      REFERENCES billservice_account (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT billservice_addonservicetransaction_accountaddonservice_id_fkey FOREIGN KEY (accountaddonservice_id)
      REFERENCES billservice_accountaddonservice (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT billservice_addonservicetransaction_accounttarif_id_fkey FOREIGN KEY (accounttarif_id)
      REFERENCES billservice_accounttarif (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT billservice_addonservicetransaction_service_id_fkey FOREIGN KEY (service_id)
      REFERENCES billservice_addonservice (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT billservice_addonservicetransaction_type_id_fkey FOREIGN KEY (type_id)
      REFERENCES billservice_transactiontype (internal_name) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL
)
WITH (OIDS=FALSE);
ALTER TABLE billservice_addonservicetransaction OWNER TO mikrobill;

-- Index: billservice_addonservicetransaction_account_id

-- DROP INDEX billservice_addonservicetransaction_account_id;

CREATE INDEX billservice_addonservicetransaction_account_id
  ON billservice_addonservicetransaction
  USING btree
  (account_id);

-- Index: billservice_addonservicetransaction_accountaddonservice_id

-- DROP INDEX billservice_addonservicetransaction_accountaddonservice_id;

CREATE INDEX billservice_addonservicetransaction_accountaddonservice_id
  ON billservice_addonservicetransaction
  USING btree
  (accountaddonservice_id);

-- Index: billservice_addonservicetransaction_accounttarif_id

-- DROP INDEX billservice_addonservicetransaction_accounttarif_id;

CREATE INDEX billservice_addonservicetransaction_accounttarif_id
  ON billservice_addonservicetransaction
  USING btree
  (accounttarif_id);

-- Index: billservice_addonservicetransaction_service_id

-- DROP INDEX billservice_addonservicetransaction_service_id;

CREATE INDEX billservice_addonservicetransaction_service_id
  ON billservice_addonservicetransaction
  USING btree
  (service_id);

-- Index: fki_billservice_addonservicetransaction_type_id_fkey

-- DROP INDEX fki_billservice_addonservicetransaction_type_id_fkey;

CREATE INDEX fki_billservice_addonservicetransaction_type_id_fkey
  ON billservice_addonservicetransaction
  USING btree
  (type_id);


-- Trigger: adds_trans_trg on billservice_addonservicetransaction

-- DROP TRIGGER adds_trans_trg ON billservice_addonservicetransaction;

CREATE TRIGGER adds_trans_trg
  AFTER INSERT OR UPDATE OR DELETE
  ON billservice_addonservicetransaction
  FOR EACH ROW
  EXECUTE PROCEDURE account_transaction_trg_fn();
  
  
  
ALTER TABLE billservice_tpchangerule
   ADD COLUMN settlement_period_id integer;
ALTER TABLE billservice_tpchangerule
   DROP COLUMN oldtptime;
   
   
CREATE INDEX billservice_tpchangerule_settlement_period_id_index
   ON billservice_tpchangerule (settlement_period_id);

ALTER TABLE billservice_tpchangerule ADD CONSTRAINT billservice_tpchangerule_settlement_period_id_fkey FOREIGN KEY (settlement_period_id) REFERENCES billservice_settlementperiod (id)
   ON UPDATE NO ACTION ON DELETE SET NULL;

ALTER TABLE billservice_tpchangerule
   ALTER COLUMN settlement_period_id SET DEFAULT 0;

ALTER TABLE billservice_addonservice
   ALTER COLUMN wyte_period_id DROP NOT NULL;
ALTER TABLE billservice_addonservice ALTER wyte_cost TYPE numeric(60, 10);
ALTER TABLE billservice_addonservice
   ALTER COLUMN wyte_cost DROP NOT NULL;

ALTER TABLE billservice_addonservice ALTER service_activation_action TYPE character varying(8000);
ALTER TABLE billservice_addonservice
   ALTER COLUMN service_activation_action SET DEFAULT '';
ALTER TABLE billservice_addonservice
   ALTER COLUMN service_activation_action DROP NOT NULL;


ALTER TABLE billservice_addonservice ALTER service_deactivation_action TYPE character varying(8000);

ALTER TABLE billservice_addonservice
   ALTER COLUMN service_deactivation_action SET DEFAULT '';
   
ALTER TABLE billservice_addonservice
   ALTER COLUMN service_deactivation_action DROP NOT NULL;
   
ALTER TABLE billservice_addonservice
   ALTER COLUMN deactivate_service_for_blocked_account SET DEFAULT False;
   
ALTER TABLE billservice_addonservice
   ALTER COLUMN deactivate_service_for_blocked_account DROP NOT NULL;

ALTER TABLE billservice_addonservice
   ALTER COLUMN change_speed SET DEFAULT False;
ALTER TABLE billservice_addonservice
   ALTER COLUMN change_speed DROP NOT NULL;

ALTER TABLE billservice_addonservice ALTER change_speed_type TYPE character varying(32);
ALTER TABLE billservice_addonservice
   ALTER COLUMN change_speed_type SET DEFAULT 'abs';
ALTER TABLE billservice_addonservice
   ALTER COLUMN change_speed_type DROP NOT NULL;

ALTER TABLE billservice_addonservice ALTER speed_units TYPE character varying(32);
ALTER TABLE billservice_addonservice
   ALTER COLUMN speed_units SET DEFAULT 'Kbps';
ALTER TABLE billservice_addonservice
   ALTER COLUMN speed_units DROP NOT NULL;

ALTER TABLE billservice_addonservice
   ALTER COLUMN "action" SET DEFAULT False;
ALTER TABLE billservice_addonservice
   ALTER COLUMN "action" DROP NOT NULL;

ALTER TABLE billservice_addonservice
   ALTER COLUMN cancel_subscription SET DEFAULT False;
ALTER TABLE billservice_addonservice
   ALTER COLUMN cancel_subscription DROP NOT NULL;

ALTER TABLE billservice_addonservice ALTER "cost" TYPE numeric(60, 10);
ALTER TABLE billservice_addonservice
   ALTER COLUMN "cost" SET DEFAULT 0;
ALTER TABLE billservice_addonservice
   ALTER COLUMN "cost" DROP NOT NULL;

ALTER TABLE billservice_addonservice
   ALTER COLUMN allow_activation SET DEFAULT False;
ALTER TABLE billservice_addonservice
   ALTER COLUMN allow_activation DROP NOT NULL;


ALTER TABLE billservice_addonservicetransaction
   DROP COLUMN type_id;
   
ALTER TABLE billservice_addonservicetransaction
   ADD COLUMN type_id character varying(255);
ALTER TABLE billservice_addonservicetransaction
   ALTER COLUMN type_id SET NOT NULL;

ALTER TABLE billservice_addonservicetransaction ADD CONSTRAINT billservice_addonservicetransaction_type_id_fkey FOREIGN KEY (type_id) REFERENCES billservice_transactiontype (internal_name)
   ON UPDATE NO ACTION ON DELETE SET NULL;
CREATE INDEX fki_billservice_addonservicetransaction_type_id_fkey ON billservice_addonservicetransaction(type_id);


ALTER TABLE billservice_addonservice ALTER "cost" TYPE numeric;
ALTER TABLE billservice_addonservice ALTER wyte_cost TYPE numeric;

ALTER TABLE billservice_addonservice
   ADD COLUMN "comment" character varying;
ALTER TABLE billservice_addonservice
   ALTER COLUMN "comment" SET DEFAULT '';

-- 27.08.2009 23:02


ALTER TABLE billservice_account
   ADD COLUMN "row" character varying;
ALTER TABLE billservice_account
   ALTER COLUMN "row" SET DEFAULT '';
   
ALTER TABLE billservice_account
   ADD COLUMN elevator_direction character varying;
ALTER TABLE billservice_account
   ALTER COLUMN elevator_direction SET DEFAULT '';


INSERT INTO billservice_transactiontype(
            "name", internal_name)
    VALUES ('Списание по подключаемой периодической услуге со снятием денег в течении периода', 'ADDONSERVICE_PERIODICAL_GRADUAL');
INSERT INTO billservice_transactiontype(
            "name", internal_name)
    VALUES ('Списание по подключаемой периодической услуге со снятием денег в начале периода', 'ADDONSERVICE_PERIODICAL_AT_START');
INSERT INTO billservice_transactiontype(
            "name", internal_name)
    VALUES ('Списание по подключаемой периодической услуге со снятием денег в конце периода', 'ADDONSERVICE_PERIODICAL_AT_END');
    
    
INSERT INTO billservice_transactiontype(
            "name", internal_name)
    VALUES ('Списание средств за преждевременное отключение услуги абонентом', 'ADDONSERVICE_WYTE_PAY');
    
INSERT INTO billservice_transactiontype(
            "name", internal_name)
    VALUES ('Списание по разовой услуге за подключаемую услугу', 'ADDONSERVICE_ONETIME');
    
INSERT INTO billservice_transactiontype(
            "name", internal_name)
    VALUES ('Оплата по карте экспресс-оплаты', 'PAY_CARD');
    

ALTER TABLE billservice_account DROP COLUMN status;
ALTER TABLE billservice_account ADD COLUMN status integer;
ALTER TABLE billservice_account ALTER COLUMN status SET STORAGE PLAIN;
ALTER TABLE billservice_account ALTER COLUMN status SET DEFAULT 1;
ALTER TABLE billservice_account ADD COLUMN contactperson character varying;
ALTER TABLE billservice_account ALTER COLUMN contactperson SET STORAGE EXTENDED;
ALTER TABLE billservice_account ALTER COLUMN contactperson SET DEFAULT ''::character varying;
ALTER TABLE billservice_account ADD COLUMN contactperson_phone character varying;
ALTER TABLE billservice_account ALTER COLUMN contactperson_phone SET STORAGE EXTENDED;
ALTER TABLE billservice_account ALTER COLUMN contactperson_phone SET DEFAULT ''::character varying;
ALTER TABLE billservice_account ADD COLUMN "comment" character varying;
ALTER TABLE billservice_account ALTER COLUMN "comment" SET STORAGE EXTENDED;
ALTER TABLE billservice_account ALTER COLUMN "comment" SET DEFAULT ''::character varying;

ALTER TABLE billservice_account ADD COLUMN "row" character varying;
ALTER TABLE billservice_account ALTER COLUMN "row" SET STORAGE EXTENDED;
ALTER TABLE billservice_account ALTER COLUMN "row" SET DEFAULT ''::character varying;

ALTER TABLE billservice_account ADD COLUMN elevator_direction character varying;
ALTER TABLE billservice_account ALTER COLUMN elevator_direction SET STORAGE EXTENDED;
ALTER TABLE billservice_account ALTER COLUMN elevator_direction SET DEFAULT ''::character varying;

