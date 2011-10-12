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
   

CREATE INDEX fki_billservice_systemuser_fkey ON billservice_transaction(systemuser_id);


ALTER TABLE billservice_transaction
   ADD COLUMN promise_expired boolean;
ALTER TABLE billservice_transaction
   ALTER COLUMN promise_expired SET DEFAULT False;

ALTER TABLE billservice_transaction
  DROP CONSTRAINT billservice_transaction_tarif_id_fkey;
ALTER TABLE billservice_transaction
  ADD CONSTRAINT billservice_transaction_tarif_id_fkey FOREIGN KEY (tarif_id)
      REFERENCES billservice_tariff (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL DEFERRABLE INITIALLY IMMEDIATE;
      
SELECT pg_catalog.setval('billservice_transactiontype_id_seq', 21, true);
INSERT INTO billservice_transactiontype("name", internal_name) VALUES ('Операция проведена кассиром', 'CASSA_TRANSACTION');
  


--14.04.2009

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
    
DROP FUNCTION transaction_sum(account_id_ int, acctf_id_ int, start_date_ timestamp without time zone, end_date_ timestamp without time zone);
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
DROP FUNCTION transaction_block_sum(account_id_ int, start_date_ timestamp without time zone, end_date_ timestamp without time zone);    
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


ALTER TABLE billservice_periodicalservicehistory ADD COLUMN summ double precision;
ALTER TABLE billservice_periodicalservicehistory ADD COLUMN account_id int;
ALTER TABLE billservice_periodicalservicehistory ADD COLUMN type_id character varying;
ALTER TABLE billservice_periodicalservicehistory ADD CONSTRAINT billservice_periodicalservicehistory_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;
CREATE TRIGGER acc_psh_trg BEFORE INSERT OR DELETE OR UPDATE ON billservice_periodicalservicehistory FOR EACH ROW EXECUTE PROCEDURE account_transaction_trg_fn(); 

CREATE OR REPLACE FUNCTION periodicaltr_fn(ps_id_ integer, acctf_id_ integer, account_id_ integer, type_id_ character varying, summ_ numeric, created_ timestamp without time zone, ps_condition_type_ integer)
  RETURNS void AS
$BODY$
DECLARE
    new_summ_ decimal;
BEGIN
    SELECT INTO new_summ_ summ_*(NOT EXISTS (SELECT id FROM billservice_suspendedperiod WHERE account_id=account_id AND (created_ BETWEEN start_date AND end_date)))::int;
    IF (ps_condition_type_ = 1) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance+credit >= 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    ELSIF (ps_condition_type_ = 2) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance+credit < 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    END IF; 
    INSERT INTO billservice_periodicalservicehistory (service_id, accounttarif_id,account_id, type_id, summ, datetime) VALUES (ps_id_, acctf_id_, account_id_, type_id_, new_summ_, created_);
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
ALTER FUNCTION periodicaltr_fn(integer, integer, integer, character varying, numeric, timestamp without time zone, integer) OWNER TO postgres;

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

CREATE TRIGGER acc_otsh_trg AFTER INSERT OR DELETE OR UPDATE ON billservice_onetimeservicehistory FOR EACH ROW EXECUTE PROCEDURE account_transaction_trg_fn();  
  
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
    
CREATE TRIGGER acc_tmtrans_trg 
  AFTER INSERT OR DELETE OR UPDATE ON billservice_timetransaction 
  FOR EACH ROW 
  EXECUTE PROCEDURE account_transaction_trg_fn();


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

--15.04.2009 
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


--23.04.2009
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


--23.04.2009
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
	UPDATE billservice_accountprepaystime SET size=size+size_, datetime=datetime_ WHERE account_tarif_id=accounttarif_id_; 
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

--13.05.2009 

ALTER TABLE billservice_tariff
   ADD COLUMN require_tarif_cost boolean;
   
ALTER TABLE billservice_tariff
   ALTER COLUMN require_tarif_cost SET DEFAULT False;
   
--15.05.2009
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

--18.05.2009
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
BEGIN
    INSERT INTO billservice_groupstat (group_id, account_id, bytes, datetime, classes, classbytes, max_class) VALUES (group_id_, account_id_, octets_, datetime_, classes_, classbytes_ , max_class_);
EXCEPTION WHEN unique_violation THEN
    SELECT classes, classbytes INTO old_classes_ ,old_classbytes_ FROM billservice_groupstat WHERE group_id=group_id_ AND account_id=account_id_ AND datetime=datetime_ FOR UPDATE;
    ilen := icount(classes_);
    max_ := 0;
    maxclass_ := NULL;
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
  
  
--19.05.2009


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
ALTER TABLE billservice_tpchangerule OWNER TO ebs;


CREATE INDEX billservice_tpchangerule_from_tariff_id
  ON billservice_tpchangerule
  USING btree
  (from_tariff_id);


CREATE INDEX billservice_tpchangerule_settlement_period_id_index
  ON billservice_tpchangerule
  USING btree
  (settlement_period_id);

CREATE UNIQUE INDEX billservice_tpchangerule_tariff_tariff
  ON billservice_tpchangerule
  USING btree
  (from_tariff_id, to_tariff_id);

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

CREATE OR REPLACE FUNCTION periodicaltr_fn(ps_id_ integer, acctf_id_ integer, account_id_ integer, type_id_ character varying, summ_ numeric, created_ timestamp without time zone, ps_condition_type_ integer)
  RETURNS void AS
$BODY$
DECLARE
    new_summ_ decimal;
BEGIN
    SELECT INTO new_summ_ summ_*(NOT EXISTS (SELECT id FROM billservice_suspendedperiod WHERE account_id=account_id AND (created_ BETWEEN start_date AND end_date)))::int;
    IF (ps_condition_type_ = 1) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance+credit >= 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    ELSIF (ps_condition_type_ = 2) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance+credit < 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    END IF; 
    INSERT INTO billservice_periodicalservicehistory (service_id, accounttarif_id,account_id, type_id, summ, datetime) VALUES (ps_id_, acctf_id_, account_id_, type_id_, new_summ_, created_);
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
ALTER FUNCTION periodicaltr_fn(integer, integer, integer, character varying, numeric, timestamp without time zone, integer) OWNER TO postgres;
  
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
    SELECT INTO result_ sum(ssum) FROM (
        SELECT sum(summ) AS ssum FROM billservice_transaction WHERE account_id=account_id_ AND (summ > 0) AND (created BETWEEN start_date_ AND end_date_) 
        UNION ALL 
        SELECT sum(summ) AS ssum FROM billservice_traffictransaction WHERE account_id=account_id_ AND (summ > 0) AND (datetime BETWEEN start_date_ AND end_date_) 
        UNION ALL 
        SELECT sum(summ) AS ssum FROM billservice_timetransaction WHERE account_id=account_id_ AND (summ > 0) AND (datetime BETWEEN start_date_ AND end_date_) 
        UNION ALL 
        SELECT sum(summ) AS ssum FROM billservice_periodicalservicehistory WHERE account_id=account_id_ AND (summ > 0) AND (datetime BETWEEN start_date_ AND end_date_)  
        UNION ALL 
        SELECT sum(summ) AS ssum FROM billservice_onetimeservicehistory WHERE account_id=account_id_ AND (summ > 0) AND (datetime BETWEEN start_date_ AND end_date_)) 
    AS ts_union ;
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
  
--23.05.2009

ALTER TABLE billservice_onetimeservicehistory ALTER account_id DROP NOT NULL;
ALTER TABLE billservice_onetimeservicehistory ALTER onetimeservice_id DROP NOT NULL;

ALTER TABLE billservice_periodicalservicehistory ALTER account_id DROP NOT NULL;
ALTER TABLE billservice_periodicalservicehistory ALTER service_id DROP NOT NULL;

ALTER TABLE billservice_timetransaction ALTER account_id DROP NOT NULL;

ALTER TABLE billservice_traffictransaction ALTER account_id DROP NOT NULL;
ALTER TABLE billservice_traffictransaction ALTER traffictransmitservice_id DROP NOT NULL;

ALTER TABLE billservice_transaction ALTER account_id DROP NOT NULL;
ALTER TABLE billservice_transaction ALTER systemuser_id DROP NOT NULL;
  
--01.06.2009

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
	UPDATE billservice_accountprepaystime SET size=size+size_, datetime=datetime_ WHERE account_tarif_id=accounttarif_id_; 
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
    
--02.06.2009
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
ALTER TABLE billservice_radiusattrs OWNER TO ebs;


CREATE INDEX billservice_radiusattrs_tarif_id
  ON billservice_radiusattrs
  USING btree
  (tarif_id);

ALTER TABLE billservice_radiusattrs
   ALTER COLUMN vendor SET DEFAULT 0;
ALTER TABLE billservice_radiusattrs
   ALTER COLUMN vendor DROP NOT NULL;

--16.06.2009

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

--03.07.2009

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

--15.07.2009

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
      
--28.07.2009
ALTER TABLE billservice_account
   ADD COLUMN associate_pptp_ipn_ip boolean;
ALTER TABLE billservice_account
   ALTER COLUMN associate_pptp_ipn_ip SET NOT NULL;
   
ALTER TABLE billservice_account
   ALTER COLUMN associate_pptp_ipn_ip SET DEFAULT False;

ALTER TABLE billservice_account
   ADD COLUMN associate_pppoe_mac boolean;

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


--31.07.2009
ALTER TABLE billservice_suspendedperiod ALTER start_date TYPE timestamp without time zone;

ALTER TABLE billservice_suspendedperiod ALTER end_date TYPE timestamp without time zone;


--07.08.2009
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
    

CREATE INDEX billservice_x8021_account_id  ON billservice_x8021  USING btree  (account_id);

DROP INDEX billservice_x8021_nas_id;

CREATE INDEX billservice_x8021_nas_id  ON billservice_x8021  USING btree  (nas_id);  

ALTER TABLE billservice_account   ADD COLUMN "comment" character varying;

ALTER TABLE billservice_speedlimit ADD COLUMN speed_units character varying(10);


ALTER TABLE billservice_speedlimit ALTER COLUMN speed_units SET STORAGE EXTENDED;ALTER TABLE billservice_speedlimit ALTER COLUMN speed_units SET NOT NULL;

ALTER TABLE billservice_speedlimit ALTER COLUMN speed_units SET DEFAULT 'Kbps'::character varying;ALTER TABLE billservice_speedlimit ADD COLUMN change_speed_type character varying(20);

ALTER TABLE billservice_speedlimit ALTER COLUMN change_speed_type SET STORAGE EXTENDED;ALTER TABLE billservice_speedlimit ALTER COLUMN change_speed_type SET DEFAULT 'add'::character varying;


--11.08.2009

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

CREATE INDEX billservice_addonservice_nas_id
  ON billservice_addonservice
  USING btree
  (nas_id);


CREATE INDEX billservice_addonservice_sp_period_id
  ON billservice_addonservice
  USING btree
  (sp_period_id);


CREATE INDEX billservice_addonservice_timeperiod_id
  ON billservice_addonservice
  USING btree
  (timeperiod_id);


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


CREATE INDEX billservice_addonservicetarif_activation_count_period_id
  ON billservice_addonservicetarif
  USING btree
  (activation_count_period_id);


CREATE INDEX billservice_addonservicetarif_service_id
  ON billservice_addonservicetarif
  USING btree
  (service_id);


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

CREATE INDEX billservice_accountaddonservice_account_id
  ON billservice_accountaddonservice
  USING btree
  (account_id);

CREATE INDEX billservice_accountaddonservice_service_id
  ON billservice_accountaddonservice
  USING btree
  (service_id);



--16.08.2009
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
ALTER TABLE billservice_addonservicetransaction OWNER TO ebs;

CREATE INDEX billservice_addonservicetransaction_account_id
  ON billservice_addonservicetransaction
  USING btree
  (account_id);


CREATE INDEX billservice_addonservicetransaction_accountaddonservice_id
  ON billservice_addonservicetransaction
  USING btree
  (accountaddonservice_id);


CREATE INDEX billservice_addonservicetransaction_accounttarif_id
  ON billservice_addonservicetransaction
  USING btree
  (accounttarif_id);


CREATE INDEX billservice_addonservicetransaction_service_id
  ON billservice_addonservicetransaction
  USING btree
  (service_id);


CREATE INDEX fki_billservice_addonservicetransaction_type_id_fkey
  ON billservice_addonservicetransaction
  USING btree
  (type_id);


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

--27.08.2009


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
ALTER TABLE billservice_account DROP COLUMN passport_date;
ALTER TABLE billservice_account ADD COLUMN passport_date character varying;
ALTER TABLE billservice_account ALTER COLUMN passport_date SET STORAGE EXTENDED;
ALTER TABLE billservice_account ALTER COLUMN passport_date SET DEFAULT ''::character varying;


ALTER TABLE billservice_tpchangerule ADD COLUMN settlement_period_id integer;
ALTER TABLE billservice_tpchangerule ALTER COLUMN settlement_period_id SET STORAGE PLAIN;
ALTER TABLE billservice_tpchangerule ALTER COLUMN settlement_period_id SET DEFAULT 0;


CREATE OR REPLACE FUNCTION suspended_period_check_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN
  IF (TG_OP = 'UPDATE') THEN
    IF NEW.status IN (1,3) THEN
        UPDATE billservice_suspendedperiod SET end_date = now() WHERE account_id=OLD.id AND end_date ISNULL;
    ELSIF NEW.status=2 and OLD.status<>2 THEN
        INSERT INTO billservice_suspendedperiod (account_id, start_date) VALUES (NEW.id, now());
    END IF;
    RETURN NEW;

  ELSIF (TG_OP = 'INSERT') THEN
    IF NEW.status = 2 THEN
    INSERT INTO billservice_suspendedperiod (account_id, start_date) VALUES (NEW.id, now());
    END IF; 
    RETURN NEW;    
  END IF;
  RETURN NEW;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;


CREATE TRIGGER suspended_period_check_trg
  AFTER INSERT OR UPDATE ON billservice_account
  FOR EACH ROW
  EXECUTE PROCEDURE suspended_period_check_trg_fn();
  
  
--09.09.2009

SELECT pg_catalog.setval('billservice_transactiontype_id_seq', 19, true);

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


ALTER FUNCTION public.gpst_crt_prev_ins(datetx date) OWNER TO ebs;
 
--09.09.2009

 SELECT pg_catalog.setval('billservice_transactiontype_id_seq', 21, true);
 

ALTER TABLE nas_nas
   ADD COLUMN speed_vendor_1 integer;

ALTER TABLE nas_nas
   ADD COLUMN speed_vendor_2 integer;

ALTER TABLE nas_nas
   ADD COLUMN speed_attr_id1 integer;

ALTER TABLE nas_nas
   ADD COLUMN speed_attr_id2 integer;

ALTER TABLE nas_nas
   ADD COLUMN speed_value1 character varying(4096);
ALTER TABLE nas_nas
   ALTER COLUMN speed_value1 SET DEFAULT '';
ALTER TABLE nas_nas
   ADD COLUMN speed_value2 character varying(4096);
ALTER TABLE nas_nas
   ALTER COLUMN speed_value2 SET DEFAULT '';

--23.09.2009

ALTER TABLE billservice_systemuser ADD COLUMN text_password character varying(255);
ALTER TABLE billservice_systemuser ALTER COLUMN text_password SET STORAGE EXTENDED;
ALTER TABLE billservice_systemuser ALTER COLUMN text_password SET DEFAULT ''::character varying;

UPDATE billservice_systemuser SET text_password = 'RPCwebadmin' WHERE username='webadmin';
UPDATE billservice_systemuser SET text_password = 'admin' WHERE username='admin';


CREATE TABLE billservice_news
(
  id serial NOT NULL,
  title character varying(255) NOT NULL,
  body text NOT NULL,
  date_from date,
  date_to date,
  CONSTRAINT billservice_news_pkey PRIMARY KEY (id)
)
WITH (OIDS=FALSE);

--14.10.2009
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
	UPDATE billservice_account SET ipn_ip_address = account_ip_ WHERE id=account_data_.id;
	RETURN account_data_;
    END IF; 

    RETURN tmp;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
ALTER FUNCTION card_activate_fn(character varying, character varying, integer, inet) OWNER TO ebs;


--03.11.2009

CREATE OR REPLACE FUNCTION periodicaltr_fn(ps_id_ integer, acctf_id_ integer, account_id_ integer, type_id_ character varying, summ_ numeric, created_ timestamp without time zone, ps_condition_type_ integer)
  RETURNS void AS
$BODY$
DECLARE
    new_summ_ decimal;
BEGIN
    SELECT INTO new_summ_ summ_*(NOT EXISTS (SELECT id FROM billservice_suspendedperiod WHERE account_id=account_id AND (created_ BETWEEN start_date AND end_date)))::int;
    IF (ps_condition_type_ = 1) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance+credit >= 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    ELSIF (ps_condition_type_ = 2) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance+credit < 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    END IF; 
    INSERT INTO billservice_periodicalservicehistory (service_id, accounttarif_id,account_id, type_id, summ, datetime) VALUES (ps_id_, acctf_id_, account_id_, type_id_, new_summ_, created_);
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
ALTER FUNCTION periodicaltr_fn(integer, integer, integer, character varying, numeric, timestamp without time zone, integer) OWNER TO postgres;
  
  
--09.11.2009
DROP TABLE IF EXISTS billservice_news;

CREATE TABLE billservice_news
(
  id serial NOT NULL,
  body text NOT NULL,
  public boolean DEFAULT false,
  private boolean DEFAULT false,
  agent boolean DEFAULT false,
  created timestamp without time zone DEFAULT now(),
  age timestamp without time zone,
  CONSTRAINT billservice_news_pkey PRIMARY KEY (id)
)
WITH (OIDS=FALSE);
ALTER TABLE billservice_news OWNER TO ebs;


CREATE TABLE billservice_accountviewednews
(
  id serial NOT NULL,
  news_id integer NOT NULL,
  account_id integer NOT NULL,
  viewed boolean NOT NULL,
  CONSTRAINT billservice_accountviewednews_pkey PRIMARY KEY (id),
  CONSTRAINT billservice_accountviewednews_account_id_fkey FOREIGN KEY (account_id)
      REFERENCES billservice_account (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT billservice_accountviewednews_news_id_fkey FOREIGN KEY (news_id)
      REFERENCES billservice_news (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED
)
WITH (OIDS=FALSE);
ALTER TABLE billservice_accountviewednews OWNER TO ebs;



CREATE INDEX billservice_accountviewednews_account_id
  ON billservice_accountviewednews
  USING btree
  (account_id);

CREATE INDEX billservice_accountviewednews_news_id
  ON billservice_accountviewednews
  USING btree
  (news_id);
  

--13.11.2009

CREATE OR REPLACE FUNCTION periodicaltr_fn(ps_id_ integer, acctf_id_ integer, account_id_ integer, type_id_ character varying, summ_ numeric, created_ timestamp without time zone, ps_condition_type_ integer)
  RETURNS void AS
$BODY$
DECLARE
    new_summ_ decimal;
BEGIN
    SELECT INTO new_summ_ summ_*(NOT EXISTS (SELECT id FROM billservice_suspendedperiod WHERE account_id=account_id_ AND (created_ BETWEEN start_date AND end_date)))::int;
    IF (ps_condition_type_ = 1) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance+credit >= 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    ELSIF (ps_condition_type_ = 2) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance+credit < 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    END IF; 
    INSERT INTO billservice_periodicalservicehistory (service_id, accounttarif_id,account_id, type_id, summ, datetime) VALUES (ps_id_, acctf_id_, account_id_, type_id_, new_summ_, created_);
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
ALTER FUNCTION periodicaltr_fn(integer, integer, integer, character varying, numeric, timestamp without time zone, integer) OWNER TO postgres;

ALTER TABLE billservice_traffictransmitnodes ADD COLUMN edge_value integer DEFAULT 0;

CREATE TABLE billservice_log
(
  id serial NOT NULL,
  systemuser_id integer NOT NULL,
  "text" text NOT NULL,
  created timestamp with time zone NOT NULL,
  CONSTRAINT billservice_log_pkey PRIMARY KEY (id),
  CONSTRAINT billservice_log_systemuser_id_fkey FOREIGN KEY (systemuser_id)
      REFERENCES billservice_systemuser (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
)
WITH (OIDS=FALSE);
ALTER TABLE billservice_log OWNER TO ebs;

--20.11.2009

ALTER TABLE billservice_addonservicetransaction
   ALTER COLUMN account_id DROP NOT NULL;

ALTER TABLE billservice_addonservicetransaction
   ALTER COLUMN accountaddonservice_id DROP NOT NULL;

ALTER TABLE billservice_addonservicetransaction
   ALTER COLUMN accounttarif_id DROP NOT NULL;

ALTER TABLE billservice_addonservicetransaction
   ALTER COLUMN service_id DROP NOT NULL;

ALTER TABLE billservice_addonservicetransaction
  DROP CONSTRAINT billservice_addonservicetransaction_account_id_fkey;

ALTER TABLE billservice_addonservicetransaction
  ADD CONSTRAINT billservice_addonservicetransaction_account_id_fkey FOREIGN KEY (account_id)
      REFERENCES billservice_account (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;
      

--24.11.2009

ALTER TABLE billservice_tpchangerule
   ADD COLUMN on_next_sp boolean;
UPDATE billservice_tpchangerule SET on_next_sp=False;

ALTER TABLE billservice_tpchangerule
   ALTER COLUMN on_next_sp SET NOT NULL;
ALTER TABLE billservice_tpchangerule
   ALTER COLUMN on_next_sp SET DEFAULT False;


INSERT INTO billservice_transactiontype(
             "name", internal_name)
    VALUES ('Списание за смену тарифного плана', 'TP_CHANGE');


INSERT INTO billservice_documenttype (id, name) VALUES (8, 'Информационное письмо');

INSERT INTO billservice_template (name, type_id, body) VALUES ('Информационное письмо', 8, '---------------------------------------------------
 Это сообщение сгенерировано биллинговой системой!
 ---------------------------------------------------

Здравствуйте, ${account.username}.
Уведомляем, что актуальный баланс Вашего лицевого счета составляет ${"%.2f" % account.ballance} руб. Размер кредита ${account.credit}.
Пожалуйста, пополните баланс во избежание блокировки.
 ---
${operator.organization}');

--08.12.2009

ALTER TABLE billservice_traffictransmitnodes ALTER edge_value TYPE int; 

CREATE TYPE group_bytes AS (
    group_id_t int,
    bytes_t    numeric
); 

CREATE TYPE group_nodes AS (
    group_id_t int,
    node_egde_t   int[]
);  


--11.12.2009


CREATE TABLE billservice_systemgroup
(
  id serial NOT NULL,
  "name" character varying(255) NOT NULL,
  CONSTRAINT billservice_systemgroup_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);

CREATE TABLE billservice_systemuser_group
(
  id serial NOT NULL,
  systemuser_id integer NOT NULL,
  systemgroup_id integer NOT NULL
 
)
WITH (
  OIDS=FALSE
);
ALTER TABLE billservice_systemuser_group OWNER TO ebs;


ALTER TABLE billservice_systemgroup OWNER TO ebs;


ALTER TABLE billservice_tariff ADD COLUMN systemgroup_id integer;
ALTER TABLE billservice_tariff ALTER COLUMN systemgroup_id SET STORAGE PLAIN;

ALTER TABLE billservice_tariff
  ADD CONSTRAINT billservice_tariff_systemgroup_id_fkey FOREIGN KEY (systemgroup_id)
      REFERENCES billservice_systemgroup (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL DEFERRABLE INITIALLY IMMEDIATE;

--16.12.2009
CREATE OR REPLACE FUNCTION transaction_block_sum(account_id_ integer, start_date_ timestamp without time zone, end_date_ timestamp without time zone)
  RETURNS decimal AS
$BODY$ 
DECLARE
    start_date_5m_ timestamp without time zone;
    result_ decimal;
BEGIN
    start_date_5m_ := date_trunc('minute', start_date_) - interval '1 min' * (date_part('min', start_date_)::int % 5); 
    SELECT INTO result_ sum(ssum) FROM (
        SELECT sum(summ) AS ssum FROM billservice_transaction WHERE account_id=account_id_ AND (((summ > 0) AND (created BETWEEN start_date_ AND end_date_)) OR ((summ < 0) AND created <= end_date_))
        UNION ALL 
        SELECT sum(summ) AS ssum FROM billservice_traffictransaction WHERE account_id=account_id_ AND (summ > 0) AND (datetime BETWEEN start_date_ AND end_date_) 
        UNION ALL 
        SELECT sum(summ) AS ssum FROM billservice_timetransaction WHERE account_id=account_id_ AND (summ > 0) AND (datetime BETWEEN start_date_ AND end_date_) 
        UNION ALL 
        SELECT sum(summ) AS ssum FROM billservice_periodicalservicehistory WHERE account_id=account_id_ AND (summ > 0) AND (datetime BETWEEN start_date_ AND end_date_)  
        UNION ALL 
        SELECT sum(summ) AS ssum FROM billservice_onetimeservicehistory WHERE account_id=account_id_ AND (summ > 0) AND (datetime BETWEEN start_date_ AND end_date_)) 
    AS ts_union ;
    RETURN result_*(-1::decimal);
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
  
  
--06.01.2010
ALTER TABLE billservice_account
   ADD COLUMN contract text DEFAULT '';
   
--29.01.2010

ALTER TABLE billservice_ipinuse ALTER ip TYPE inet USING ip::inet;

CREATE OR REPLACE FUNCTION get_free_ip_from_pool(ag_pool_id_ int) 
  RETURNS inet AS
$BODY$
BEGIN
    RETURN (SELECT free_ip.ipaddress FROM (SELECT (SELECT start_ip FROM billservice_ippool WHERE id=ag_pool_id_) + ip_series.ip_inc FROM generate_series(0, (SELECT end_ip - start_ip FROM billservice_ippool WHERE id=ag_pool_id_)) AS ip_series(ip_inc)) AS free_ip(ipaddress) WHERE free_ip.ipaddress NOT IN (SELECT ip FROM billservice_ipinuse WHERE pool_id=ag_pool_id_) LIMIT 1);

END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
  
CREATE OR REPLACE FUNCTION return_ipinuse_to_pool_trg_fn() 
  RETURNS trigger AS
$BODY$
DECLARE
    vpn_pool_id int;
BEGIN
    IF (OLD.session_status ISNULL) AND (NEW.session_status NOTNULL) THEN
        SELECT bacc.vpn_ipinuse_id FROM billservice_account AS bacc WHERE bacc.id = NEW.account_id AND bacc.vpn_ip_address = '0.0.0.0'::inet INTO vpn_pool_id;
        IF vpn_pool_id NOTNULL THEN
             DELETE FROM billservice_ipinuse AS ipnuse WHERE ipnuse.pool_id=vpn_pool_id AND ipnuse.ip=NEW.framed_ip_address::inet;    
        END IF;
    END IF;
    RETURN NEW;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
  
  
  
CREATE TRIGGER return_ipinuse_to_pool_trg
 AFTER UPDATE
   ON radius_activesession
   FOR EACH ROW
   EXECUTE PROCEDURE return_ipinuse_to_pool_trg_fn();
   

ALTER TABLE billservice_systemuser ADD COLUMN email text;
ALTER TABLE billservice_systemuser ALTER COLUMN email SET STORAGE EXTENDED;
ALTER TABLE billservice_systemuser ALTER COLUMN email SET DEFAULT ''::text;

ALTER TABLE billservice_systemgroup ADD COLUMN "system" boolean;
ALTER TABLE billservice_systemgroup ALTER COLUMN "system" SET STORAGE PLAIN;
ALTER TABLE billservice_systemgroup ALTER COLUMN "system" SET DEFAULT false;

ALTER TABLE billservice_systemgroup ADD COLUMN system_name text;
ALTER TABLE billservice_systemgroup ALTER COLUMN system_name SET STORAGE EXTENDED;

--10.02.2010

ALTER TABLE billservice_onetimeservice
   ADD COLUMN created timestamp without time zone DEFAULT now();
   
--16.02.2010


UPDATE billservice_accounttarif SET datetime=date_trunc('second', datetime);

UPDATE billservice_accountaddonservice SET activated=date_trunc('second', activated);
UPDATE billservice_accountaddonservice SET deactivated=date_trunc('second', deactivated);

--12.03.2010
INSERT INTO billservice_transactiontype("name", internal_name) VALUES ('Оплата через платежные системы', 'PAYMENTGATEWAY_BILL');
--23.10.2010
ALTER TABLE billservice_organization
   ADD COLUMN kpp text;
ALTER TABLE billservice_organization
   ALTER COLUMN kpp SET DEFAULT '';


ALTER TABLE billservice_organization
   ADD COLUMN kor_s text;
ALTER TABLE billservice_organization
   ALTER COLUMN kor_s SET DEFAULT '';
--23.11.2010
alter table billservice_accountipnspeed alter column speed type text;

--05.12.2010
UPDATE billservice_template SET body='
<html>
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
       <h1 align=center> <b> Квитанция об оплате услуг № ${transaction.id} </b> </h1>
       <strong>Абонент:</strong> ${account.fullname} <br>
       <strong>Тарифный план:</strong> ${tarif.name} <br>
       <strong>Логин:</strong> ${account.username}<br>
       <strong>Сумма:</strong> ${transaction.summ}<br>
       <strong>Дата приема платежа:</strong> ${transaction.created}<br>
    </td>
   </tr>
  </table>
 </body>
</html>
'
WHERE type_id=5;

--04.01.2011

ALTER TABLE nas_nas ADD COLUMN subacc_add_action text;
ALTER TABLE nas_nas ALTER COLUMN subacc_add_action SET DEFAULT ''::text;


ALTER TABLE nas_nas ADD COLUMN subacc_delete_action text;
ALTER TABLE nas_nas ALTER COLUMN subacc_delete_action SET DEFAULT ''::text;
ALTER TABLE nas_nas ADD COLUMN subacc_ipn_speed_action text;
ALTER TABLE nas_nas ALTER COLUMN subacc_ipn_speed_action SET DEFAULT ''::text;
ALTER TABLE nas_nas ADD COLUMN subacc_enable_action text;
ALTER TABLE nas_nas ALTER COLUMN subacc_enable_action SET DEFAULT ''::text;
ALTER TABLE nas_nas ADD COLUMN subacc_disable_action text;
ALTER TABLE nas_nas ALTER COLUMN subacc_disable_action SET DEFAULT ''::text;
ALTER TABLE nas_nas ADD COLUMN acct_interim_interval integer;
ALTER TABLE nas_nas ALTER COLUMN acct_interim_interval SET DEFAULT 60;

ALTER TABLE radius_activesession ADD COLUMN subaccount_id integer;

CREATE TABLE billservice_subaccount
(
  id serial NOT NULL,
  account_id integer NOT NULL,
  username character varying(64) DEFAULT ''::character varying,
  "password" character varying(64) DEFAULT ''::character varying,
  vpn_ip_address inet DEFAULT '0.0.0.0'::inet,
  ipn_ip_address inet DEFAULT '0.0.0.0'::inet,
  ipn_mac_address character varying(18),
  nas_id integer,
  ipn_added boolean DEFAULT false,
  ipn_enabled boolean NOT NULL DEFAULT false,
  need_resync boolean DEFAULT false,
  speed text DEFAULT ''::text,
  switch_id integer,
  switch_port integer,
  allow_dhcp boolean DEFAULT false,
  allow_dhcp_with_null boolean DEFAULT false,
  allow_dhcp_with_minus boolean DEFAULT false,
  allow_dhcp_with_block boolean DEFAULT false,
  allow_vpn_with_null boolean DEFAULT false,
  allow_vpn_with_minus boolean DEFAULT false,
  allow_vpn_with_block boolean DEFAULT false,
  associate_pptp_ipn_ip boolean DEFAULT false,
  associate_pppoe_ipn_mac boolean DEFAULT false,
  ipn_speed text DEFAULT ''::text,
  vpn_speed text DEFAULT ''::text,
  allow_addonservice boolean DEFAULT false,
  ipn_sleep boolean DEFAULT false,
  CONSTRAINT billservice_subaccount_pkey PRIMARY KEY (id),
  CONSTRAINT billservice_subaccount_account_id_fkey FOREIGN KEY (account_id)
      REFERENCES billservice_account (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED
)
WITH (
  OIDS=FALSE
);


ALTER TABLE billservice_accountaddonservice ADD COLUMN subaccount_id integer;

ALTER TABLE billservice_account
   ALTER COLUMN nas_id DROP NOT NULL;

ALTER TABLE billservice_account
  DROP CONSTRAINT billservice_account_nas_id_fkey;
  
ALTER TABLE billservice_accountaddonservice
   ALTER COLUMN account_id DROP NOT NULL;
  
CREATE OR REPLACE FUNCTION periodicaltr_fn(ps_id_ integer, acctf_id_ integer, account_id_ integer, type_id_ character varying, summ_ numeric, created_ timestamp without time zone, ps_condition_type_ integer)
  RETURNS void AS
$BODY$
DECLARE
    new_summ_ decimal;
BEGIN
    SELECT INTO new_summ_ summ_*(NOT EXISTS (SELECT id FROM billservice_suspendedperiod WHERE account_id=account_id_ AND (created_ BETWEEN start_date AND end_date)))::int;
    IF (ps_condition_type_ = 1) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance+credit >= 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    ELSIF (ps_condition_type_ = 2) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance+credit < 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    ELSIF (ps_condition_type_ = 3) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance+credit > 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    END IF; 
    INSERT INTO billservice_periodicalservicehistory (service_id, accounttarif_id,account_id, type_id, summ, datetime) VALUES (ps_id_, acctf_id_, account_id_, type_id_, new_summ_, created_);
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
  
ALTER TABLE billservice_account
   ADD COLUMN systemuser_id integer;


CREATE INDEX fki_billservice_account_systemuser_fkey ON billservice_account(systemuser_id);

ALTER TABLE billservice_account
  DROP CONSTRAINT billservice_account_vpnipinuse_fkey;
  
  ALTER TABLE billservice_account
    ADD CONSTRAINT billservice_account_vpnipinuse_fkey FOREIGN KEY (vpn_ipinuse_id)
    REFERENCES billservice_ipinuse (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE SET NULL;
ALTER TABLE billservice_subaccount ADD COLUMN vpn_ipinuse_id integer;
ALTER TABLE billservice_subaccount ADD COLUMN ipn_ipinuse_id integer;

ALTER TABLE billservice_subaccount
  ADD CONSTRAINT billservice_subaccount_vpnipinuse_fkey FOREIGN KEY (vpn_ipinuse_id)
  REFERENCES billservice_ipinuse (id) MATCH SIMPLE
  ON UPDATE NO ACTION ON DELETE SET NULL;
              
ALTER TABLE billservice_subaccount
    ADD CONSTRAINT billservice_subaccount_ipnipinuse_fkey FOREIGN KEY (ipn_ipinuse_id)
    REFERENCES billservice_ipinuse (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE SET NULL;
                            
CREATE OR REPLACE FUNCTION shedulelog_tr_credit_fn(account_id_ integer, accounttarif_id_ integer, trts_id_ integer, coeff_ numeric, datetime_ timestamp without time zone)
  RETURNS void AS
$BODY$
DECLARE
        prepaid_tr_id_ int;
        size_ bigint;
        count_ int := 0;
BEGIN

        FOR prepaid_tr_id_, size_ IN SELECT id, size FROM billservice_prepaidtraffic WHERE traffic_transmit_service_id=trts_id_ LOOP
                UPDATE billservice_accountprepaystrafic SET size=size+size_*coeff_, datetime=datetime_ WHERE account_tarif_id=accounttarif_id_ AND prepaid_traffic_id=prepaid_tr_id_;
                IF NOT FOUND THEN
                        INSERT INTO billservice_accountprepaystrafic (account_tarif_id, prepaid_traffic_id, size, datetime) VALUES(accounttarif_id_, prepaid_tr_id_, size_*coeff_, datetime_);
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
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION shedulelog_tr_credit_fn(integer, integer, integer, numeric, timestamp without time zone) OWNER TO postgres;

ALTER TABLE billservice_account ADD COLUMN last_balance_null timestamp without time zone;
CREATE OR REPLACE FUNCTION last_balance_null_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN
  IF (TG_OP = 'UPDATE') OR (TG_OP = 'INSERT') THEN
    IF NEW.ballance<=0 THEN
        NEW.last_balance_null=now();
    END IF;
  END IF;
  RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;


CREATE TRIGGER last_balance_null_trg
  BEFORE INSERT OR UPDATE
  ON billservice_account
  FOR EACH ROW
  EXECUTE PROCEDURE last_balance_null_trg_fn();

CREATE TABLE billservice_balancehistory
(
  id serial NOT NULL,
  account_id integer NOT NULL,
  balance numeric NOT NULL,
  datetime timestamp with time zone DEFAULT now(),
  CONSTRAINT billservice_balancehistory_pkey PRIMARY KEY (id),
  CONSTRAINT billservice_balancehistory_account_id_fkey FOREIGN KEY (account_id)
      REFERENCES billservice_account (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
)
WITH (
  OIDS=FALSE
);
ALTER TABLE billservice_balancehistory OWNER TO ebs;

CREATE OR REPLACE FUNCTION balance_history_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN
  IF (TG_OP = 'UPDATE') THEN
    IF NEW.ballance<>OLD.ballance THEN
        INSERT INTO billservice_balancehistory(account_id, balance, datetime) VALUES(NEW.id, NEW.ballance, now());
    END IF;
  END IF;
  RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

  
CREATE TRIGGER balance_history_trg
  BEFORE INSERT OR UPDATE
  ON billservice_account
  FOR EACH ROW
  EXECUTE PROCEDURE balance_history_trg_fn();


ALTER TABLE radius_activesession
   ADD COLUMN acct_terminate_cause text DEFAULT '';

CREATE OR REPLACE FUNCTION rad_activesession_crt_cur_ins(datetx date) RETURNS void
    AS $$
DECLARE
    datetx_ text := to_char(datetx, 'YYYYMM01');
    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION rad_activesession_cur_ins (radaccts radius_activesession) RETURNS void AS ';
    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO radaccts';  
    fn_bd_tx2_ text := '(account_id, sessionid, interrim_update, date_start, date_end, 
            caller_id, called_id, nas_id, session_time, framed_protocol, 
            bytes_in, bytes_out, session_status, speed_string, framed_ip_address, 
            nas_int_id, subaccount_id, acct_terminate_cause)
                          VALUES 
                         (radaccts.account_id, radaccts.sessionid, radaccts.interrim_update, radaccts.date_start, radaccts.date_end, 
			    radaccts.caller_id, radaccts.called_id, radaccts.nas_id, radaccts.session_time, radaccts.framed_protocol, 
			    radaccts.bytes_in, radaccts.bytes_out, radaccts.session_status, radaccts.speed_string, radaccts.framed_ip_address, 
			    radaccts.nas_int_id, radaccts.subaccount_id, radaccts.acct_terminate_cause); RETURN; END;';      
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
$$
    LANGUAGE plpgsql;
    
CREATE OR REPLACE FUNCTION radius_activesession_trs_crt_pdb(datetx date) RETURNS integer
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');
    datetx_e_ text := to_char((datetx + interval '1 month')::date, 'YYYYMM01');

    qt_dtx_ text;
    qt_dtx_e_ text;
    seq_tx1_ text := 'CREATE SEQUENCE radaccts#rpdate#_id_seq
                      INCREMENT 1
                      MINVALUE 1
                      MAXVALUE 9223372036854775807
                      START 1
                      CACHE 1;';
    seqname_tx1_ text := 'radaccts#rpdate#_id_seq';

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
                     
    at_tx1_ text := 'ALTER TABLE radaccts#rpdate# ALTER COLUMN id SET DEFAULT nextval(#qseqname#::regclass);';

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
    
CREATE OR REPLACE FUNCTION radius_activesession_crt_prev_ins(datetx date) RETURNS void
    AS $$
DECLARE
    datetx_ text := to_char(datetx, 'YYYYMM01');
    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION radius_activesession_prev_ins (radaccts radius_activesession) RETURNS void AS ';
    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO radaccts';
    fn_bd_tx2_ text := '(account_id, sessionid, interrim_update, date_start, date_end, 
            caller_id, called_id, nas_id, session_time, framed_protocol, 
            bytes_in, bytes_out, session_status, speed_string, framed_ip_address, 
            nas_int_id, subaccount_id, acct_terminate_cause)
                          VALUES 
                         (radaccts.account_id, radaccts.sessionid, radaccts.interrim_update, radaccts.date_start, radaccts.date_end, 
			    radaccts.caller_id, radaccts.called_id, radaccts.nas_id, radaccts.session_time, radaccts.framed_protocol, 
			    radaccts.bytes_in, radaccts.bytes_out, radaccts.session_status, radaccts.speed_string, radaccts.framed_ip_address, 
			    radaccts.nas_int_id, radaccts.subaccount_id, radaccts.acct_terminate_cause); RETURN; END;';
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
$$
    LANGUAGE plpgsql; 
 
CREATE OR REPLACE FUNCTION radius_activesession_cur_datechk(trs_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700201'; d_e_ date := (DATE '19700101'+ interval '1 month')::date; BEGIN IF    trs_date < d_s_ THEN RETURN -1; ELSIF trs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;
    
CREATE OR REPLACE FUNCTION radius_activesession_prev_datechk(trs_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700101'; d_e_ date := (DATE '19700101'+ interval '1 month')::date; BEGIN IF    trs_date < d_s_ THEN RETURN -1; ELSIF trs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;
    
CREATE OR REPLACE FUNCTION radius_activesession_inserter(radaccts radius_activesession) RETURNS void
    AS 
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

    insq_ := 'INSERT INTO radaccts' || datetx_ || ' (account_id, sessionid, interrim_update, date_start, date_end, caller_id, called_id, nas_id, session_time, framed_protocol, bytes_in, bytes_out, session_status, speed_string, framed_ip_address, nas_int_id, subaccount_id, acct_terminate_cause) VALUES (' || radaccts_account_id || ',' || radaccts_sessionid || ',' || radaccts_interrim_update || ',' || radaccts_date_start || ',' || radaccts_date_end || ',' || radaccts_caller_id || ',' || adaccts_called_id || ',' || radaccts_nas_id || ',' || radaccts_session_time || ',' || radaccts_framed_protocol || ',' || radaccts_bytes_in || ',' || radaccts_bytes_out || ',' || radaccts_session_status || ',' || radaccts_speed_string || ',' || radaccts_framed_ip_address || ',' || radaccts_nas_int_id || ',' || radaccts_subaccount_id || ',' || radaccts_acct_terminate_cause || ');';
    EXECUTE insq_;
    RETURN;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
    
CREATE OR REPLACE FUNCTION radius_activesession_ins_trg_fn()
  RETURNS trigger AS
$BODY$
DECLARE
    cur_chk int;
    prev_chk int;
BEGIN
    cur_chk := radius_activesession_cur_datechk(NEW.date_start);

    IF cur_chk = 0 THEN
        PERFORM rad_activesession_cur_ins(NEW);
    ELSIF cur_chk = 1 THEN
        BEGIN
            PERFORM radius_activesession_trs_crt_pdb(NEW.date_start::date);
            PERFORM rad_activesession_crt_cur_ins(NEW.date_start::date);
            EXECUTE rad_activesession_cur_ins(NEW);
        EXCEPTION 
          WHEN duplicate_table THEN
             PERFORM rad_activesession_crt_cur_ins(NEW.date_start::date);
             EXECUTE rad_activesession_cur_ins(NEW);
        END;
    ELSE 
        prev_chk := radius_activesession_prev_datechk(NEW.date_start);
        IF prev_chk = 0 THEN
            PERFORM radius_activesession_prev_ins(NEW);
        ELSE
            BEGIN 
                PERFORM radius_activesession_inserter(NEW);
            EXCEPTION 
              WHEN undefined_table THEN
                PERFORM radius_activesession_trs_crt_pdb(NEW.date_start::date);
                PERFORM radius_activesession_inserter(NEW);
            END;
        END IF;      
    END IF;
    RETURN NULL;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
  
CREATE TRIGGER radius_activesession_ins_trg
  BEFORE INSERT
  ON radius_activesession
  FOR EACH ROW
  EXECUTE PROCEDURE radius_activesession_ins_trg_fn();

CREATE OR REPLACE FUNCTION activesession_cur_dt()
  RETURNS date AS
$BODY$ BEGIN RETURN  DATE '19700102'; END; $BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;


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
    insq_ := 'INSERT INTO trs' || datetx_ || ' (bill, account_id, type_id, approved, tarif_id, summ, description, created, systemuser_id, promise, end_promise, promise_expired, accounttarif_id) VALUES (' || ttrn_bill || ',' || ttrn_account_id || ',' || ttrn_type_id || ',' || ttrn_approved || ',' || ttrn_tarif_id || ',' || ttrn_summ || ',' || ttrn_description || ',' || ttrn_created || ',' || ttrn_systemuser_id || ',' || ttrn_promise || ',' || ttrn_end_promise || ',' || ttrn_promise_expired || ',' || ttrn_accounttarif_id || ');';
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

DELETE FROM billservice_transaction;
DROP TRIGGER IF EXISTS trs_del_trg ON billservice_transaction;

DROP TRIGGER acc_tftrans_trg ON billservice_traffictransaction;

CREATE TRIGGER acc_tftrans_trg BEFORE INSERT OR DELETE OR UPDATE ON billservice_traffictransaction FOR EACH ROW EXECUTE PROCEDURE account_transaction_trg_fn();

ALTER TABLE billservice_traffictransaction
  DROP CONSTRAINT billservice_traffictransaction_traffictransmitservice_id_fkey;

CREATE OR REPLACE FUNCTION traftrans_crt_cur_ins(datetx date) RETURNS void
    AS $$
DECLARE
    datetx_ text := to_char(datetx, 'YYYYMM01');
    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION traftrans_cur_ins (traftrns billservice_traffictransaction) RETURNS void AS ';
    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO traftrans';        
    fn_bd_tx2_ text := '(traffictransmitservice_id, account_id, accounttarif_id, summ, datetime)
                          VALUES 
                         (traftrns.traffictransmitservice_id, traftrns.account_id, traftrns.accounttarif_id, traftrns.summ, traftrns.datetime); RETURN; END;';
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
$$
    LANGUAGE plpgsql;
    
CREATE OR REPLACE FUNCTION traftrans_crt_pdb(datetx date) RETURNS integer
    AS $$
DECLARE
    datetx_ text := to_char(datetx, 'YYYYMM01');
    datetx_e_ text := to_char((datetx + interval '1 month')::date, 'YYYYMM01');
    qt_dtx_ text;
    qt_dtx_e_ text;
    seq_tx1_ text := 'CREATE SEQUENCE traftrans#rpdate#_id_seq
                      INCREMENT 1
                      MINVALUE 1
                      MAXVALUE 9223372036854775807
                      START 1
                      CACHE 1;';
    seqname_tx1_ text := 'traftrans#rpdate#_id_seq';

    chk_tx1_ text := 'CHECK ( datetime >= DATE #stdtx# AND datetime < DATE #eddtx# )';
    ct_tx1_ text := 'CREATE TABLE traftrans#rpdate# (
                     #chk#,
                     CONSTRAINT traftrans#rpdate#_id_pkey PRIMARY KEY (id) ) 
                     INHERITS (billservice_traffictransaction) 
                     WITH (OIDS=FALSE);                     
                     CREATE INDEX traftrans#rpdate#_account_id ON traftrans#rpdate# USING btree (account_id);
                     CREATE TRIGGER acc_tftrans_trg AFTER UPDATE OR DELETE ON traftrans#rpdate# FOR EACH ROW EXECUTE PROCEDURE account_transaction_trg_fn();
                     ';
    at_tx1_ text := 'ALTER TABLE traftrans#rpdate# ALTER COLUMN id SET DEFAULT nextval(#qseqname#::regclass);';
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
    
CREATE OR REPLACE FUNCTION traftrans_crt_prev_ins(datetx date) RETURNS void
    AS $$
DECLARE
    datetx_ text := to_char(datetx, 'YYYYMM01');
    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION traftrans_prev_ins (traftrns billservice_traffictransaction) RETURNS void AS ';
    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO traftrans';
    fn_bd_tx2_ text := '(traffictransmitservice_id, account_id, accounttarif_id, summ, datetime)
                          VALUES 
                         (traftrns.traffictransmitservice_id, traftrns.account_id, traftrns.accounttarif_id, traftrns.summ, traftrns.datetime); RETURN; END;';
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
$$
    LANGUAGE plpgsql; 
 
CREATE OR REPLACE FUNCTION traftrans_cur_datechk(trs_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700201'; d_e_ date := (DATE '19700101'+ interval '1 month')::date; BEGIN IF    trs_date < d_s_ THEN RETURN -1; ELSIF trs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;
    
CREATE OR REPLACE FUNCTION traftrans_prev_datechk(trs_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700101'; d_e_ date := (DATE '19700101'+ interval '1 month')::date; BEGIN IF    trs_date < d_s_ THEN RETURN -1; ELSIF trs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;
    
CREATE OR REPLACE FUNCTION traftrans_inserter(traftrns billservice_traffictransaction) RETURNS void
    AS 
$BODY$
DECLARE
    datetx_ text := to_char(traftrns.datetime::date, 'YYYYMM01');
    insq_   text;

    traftrns_traffictransmitservice_id text;  
    traftrns_account_id    text;
    traftrns_accounttarif_id    text;
    traftrns_summ    text;
    traftrns_datetime    text;
BEGIN
    
    	IF traftrns.traffictransmitservice_id IS NULL THEN
	   traftrns_traffictransmitservice_id := 'NULL';
	ELSE
	   traftrns_traffictransmitservice_id := traftrns.traffictransmitservice_id::text;
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


	IF traftrns.datetime IS NULL THEN
	   traftrns_datetime := 'NULL';
	ELSE
	   traftrns_datetime := quote_literal(traftrns.datetime);
	END IF;

    insq_ := 'INSERT INTO traftrans' || datetx_ || ' (traffictransmitservice_id, account_id, accounttarif_id, summ, datetime) VALUES (' || traftrns_traffictransmitservice_id || ',' || traftrns_account_id || ',' || traftrns_accounttarif_id || ',' || traftrns_summ || ',' || traftrns_datetime || ');';
    EXECUTE insq_;
    RETURN;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
    
CREATE OR REPLACE FUNCTION traftrans_ins_trg_fn()
  RETURNS trigger AS
$BODY$
DECLARE
    cur_chk int;
    prev_chk int;
BEGIN
    cur_chk := traftrans_cur_datechk(NEW.datetime);

    IF cur_chk = 0 THEN
        PERFORM traftrans_cur_ins(NEW);
    ELSIF cur_chk = 1 THEN
        BEGIN
            PERFORM traftrans_crt_pdb(NEW.datetime::date);
            PERFORM traftrans_crt_cur_ins(NEW.datetime::date);
            EXECUTE traftrans_cur_ins(NEW);
        EXCEPTION 
          WHEN duplicate_table THEN
             PERFORM traftrans_crt_cur_ins(NEW.datetime::date);
             EXECUTE traftrans_cur_ins(NEW);
        END;
        
        
    ELSE 
        prev_chk := traftrans_prev_datechk(NEW.datetime);
        IF prev_chk = 0 THEN
            PERFORM traftrans_prev_ins(NEW);
        ELSE
            BEGIN 
                PERFORM traftrans_inserter(NEW);
            EXCEPTION 
              WHEN undefined_table THEN
                PERFORM traftrans_crt_pdb(NEW.datetime::date);
                PERFORM traftrans_inserter(NEW);
            END;
        END IF;      
    END IF;
    RETURN NULL;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
  
CREATE TRIGGER traftrans_ins_trg
  BEFORE INSERT
  ON billservice_traffictransaction
  FOR EACH ROW
  EXECUTE PROCEDURE traftrans_ins_trg_fn();


CREATE OR REPLACE FUNCTION traftrans_cur_dt()
  RETURNS date AS
$BODY$ BEGIN RETURN  DATE '19700102'; END; $BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;


ALTER TABLE billservice_systemuser
   ADD COLUMN job text DEFAULT '';
ALTER TABLE billservice_systemuser
   ADD COLUMN fullname text DEFAULT '';

ALTER TABLE billservice_systemuser
   ADD COLUMN address text DEFAULT '';

ALTER TABLE billservice_systemuser
   ADD COLUMN home_phone text DEFAULT '';


ALTER TABLE billservice_systemuser
   ADD COLUMN mobile_phone text DEFAULT '';
ALTER TABLE billservice_systemuser
   ADD COLUMN passport text DEFAULT '';

ALTER TABLE billservice_systemuser
   ADD COLUMN passport_details text DEFAULT '';


ALTER TABLE billservice_systemuser
   ADD COLUMN passport_number text DEFAULT '';

ALTER TABLE billservice_systemuser
   ADD COLUMN unp text DEFAULT '';


ALTER TABLE billservice_systemuser
   ADD COLUMN im text DEFAULT '';

ALTER TABLE nas_nas
   ADD COLUMN snmp_version text DEFAULT '';


ALTER TABLE billservice_account
   ADD COLUMN entrance_code character varying(256) DEFAULT '';

ALTER TABLE billservice_account
   ADD COLUMN private_passport_number character varying(128) DEFAULT '';


ALTER TABLE billservice_account
   ADD COLUMN city_id integer;

ALTER TABLE billservice_account
   ADD COLUMN street_id integer;

ALTER TABLE billservice_account
   ADD COLUMN house_id integer;

CREATE OR REPLACE FUNCTION get_tarif_name(acc_id integer, dattime timestamp without time zone)
  RETURNS text AS
$BODY$
declare
xxx text;
begin
SELECT "name" INTO xxx
  FROM billservice_tariff WHERE id=(SELECT tarif_id FROM billservice_accounttarif WHERE account_id=acc_id and datetime<dattime ORDER BY datetime DESC LIMIT 1);
RETURN xxx;
end;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;


ALTER TABLE billservice_subaccount
   ADD COLUMN allow_ipn_with_null boolean DEFAULT False;

ALTER TABLE billservice_subaccount
   ADD COLUMN allow_ipn_with_minus boolean DEFAULT False;

ALTER TABLE billservice_subaccount
   ADD COLUMN allow_ipn_with_block boolean DEFAULT False;

CREATE TABLE billservice_city
(
  id serial NOT NULL,
  "name" character varying(320) NOT NULL,
  CONSTRAINT billservice_city_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);

CREATE TABLE billservice_street
(
  id serial NOT NULL,
  "name" character varying(320) NOT NULL,
  city_id integer NOT NULL,
  CONSTRAINT billservice_street_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE billservice_street OWNER TO ebs;


CREATE INDEX billservice_street_city_id
  ON billservice_street
  USING btree
  (city_id);

CREATE TABLE billservice_house
(
  id serial NOT NULL,
  "name" character varying(320) NOT NULL,
  street_id integer NOT NULL,
  CONSTRAINT billservice_house_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE billservice_house OWNER TO ebs;


CREATE INDEX billservice_house_street_id
  ON billservice_house
  USING btree
  (street_id);


CREATE TABLE radius_authlog
(
  id serial NOT NULL,
  account_id integer,
  "type" character varying(100) NOT NULL,
  service character varying(40) NOT NULL,
  subaccount_id integer,
  nas_id integer,
  cause text NOT NULL,
  datetime timestamp with time zone DEFAULT now(),
  CONSTRAINT radius_authlog_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE radius_authlog OWNER TO ebs;

ALTER TABLE billservice_account
   ADD COLUMN city_id integer;

ALTER TABLE billservice_account
   ADD COLUMN street_id integer;

ALTER TABLE billservice_account
   ADD COLUMN house_id integer;

ALTER TABLE billservice_periodicalservice ADD COLUMN deactivated timestamp without time zone;
ALTER TABLE billservice_periodicalservice ADD COLUMN deleted boolean;
ALTER TABLE billservice_periodicalservice ALTER COLUMN deleted SET DEFAULT false;

--13.02.2011
CREATE TABLE billservice_templatetype
(
  id serial NOT NULL,
  "name" text NOT NULL,
  CONSTRAINT billservice_templatetype_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE billservice_templatetype OWNER TO ebs;

INSERT INTO billservice_templatetype(name, id) VALUES('Информационное письмо',8);
INSERT INTO billservice_templatetype(name, id) VALUES('Договор',1);
INSERT INTO billservice_templatetype(name, id) VALUES('Акт выполненных работ',4);
INSERT INTO billservice_templatetype(name, id) VALUES('Счет фактура',3);
INSERT INTO billservice_templatetype(name, id) VALUES('Договор на подключение юр. лиц',2);
INSERT INTO billservice_templatetype(name, id) VALUES('Кассовый чек',5);
INSERT INTO billservice_templatetype(name, id) VALUES('Накладная на карты экспресс-оплаты',6);
INSERT INTO billservice_templatetype(name, id) VALUES('Шаблон карты экспресс-оплаты',7);


ALTER TABLE billservice_template ADD CONSTRAINT billservice_template_type_id_billservice_templatetype_fkey FOREIGN KEY (type_id) REFERENCES billservice_templatetype (id)
   ON UPDATE SET NULL ON DELETE SET NULL;


ALTER TABLE billservice_account ADD COLUMN allow_ipn_with_null boolean;
ALTER TABLE billservice_account ALTER COLUMN allow_ipn_with_null SET DEFAULT false;

ALTER TABLE billservice_account ADD COLUMN allow_ipn_with_minus boolean;
ALTER TABLE billservice_account ALTER COLUMN allow_ipn_with_minus SET DEFAULT false;

ALTER TABLE billservice_account ADD COLUMN allow_ipn_with_block boolean;
ALTER TABLE billservice_account ALTER COLUMN allow_ipn_with_block SET DEFAULT false;

--17.02.2011
ALTER TABLE billservice_tariff ADD COLUMN radius_traffic_transmit_service_id integer;
ALTER TABLE billservice_timeaccessservice
   ADD COLUMN rounding integer DEFAULT 0;

ALTER TABLE billservice_timeaccessservice
   ADD COLUMN tarification_step integer DEFAULT 0;


ALTER TABLE radius_activesession
   ADD COLUMN lt_time numeric DEFAULT 0;

ALTER TABLE radius_activesession
   ADD COLUMN lt_bytes_in numeric DEFAULT 0;

ALTER TABLE radius_activesession
   ADD COLUMN lt_bytes_out numeric DEFAULT 0;
   
--17.02.2011
CREATE OR REPLACE FUNCTION rad_activesession_crt_cur_ins(datetx date) RETURNS void
    AS $$
DECLARE
    datetx_ text := to_char(datetx, 'YYYYMM01');
    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION rad_activesession_cur_ins (radaccts radius_activesession) RETURNS void AS ';
    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO radaccts';
    fn_bd_tx2_ text := '(account_id, sessionid, interrim_update, date_start, date_end, 
            caller_id, called_id, nas_id, session_time, framed_protocol, 
            bytes_in, bytes_out, session_status, speed_string, framed_ip_address, 
            nas_int_id, subaccount_id, acct_terminate_cause,lt_time, lt_bytes_in,lt_bytes_out)
                          VALUES 
                         (radaccts.account_id, radaccts.sessionid, radaccts.interrim_update, radaccts.date_start, radaccts.date_end, 
			    radaccts.caller_id, radaccts.called_id, radaccts.nas_id, radaccts.session_time, radaccts.framed_protocol, 
			    radaccts.bytes_in, radaccts.bytes_out, radaccts.session_status, radaccts.speed_string, radaccts.framed_ip_address, 
			    radaccts.nas_int_id, radaccts.subaccount_id, radaccts.acct_terminate_cause, radaccts.lt_time, radaccts.lt_bytes_in, radaccts.lt_bytes_out); RETURN; END;';
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
$$
    LANGUAGE plpgsql;

    
CREATE OR REPLACE FUNCTION radius_activesession_crt_prev_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');
    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION radius_activesession_prev_ins (radaccts radius_activesession) RETURNS void AS ';
    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO radaccts';
    fn_bd_tx2_ text := '(account_id, sessionid, interrim_update, date_start, date_end, 
            caller_id, called_id, nas_id, session_time, framed_protocol, 
            bytes_in, bytes_out, session_status, speed_string, framed_ip_address, 
            nas_int_id, subaccount_id, acct_terminate_cause,lt_time, lt_bytes_in, lt_bytes_out)
                          VALUES 
                         (radaccts.account_id, radaccts.sessionid, radaccts.interrim_update, radaccts.date_start, radaccts.date_end, 
			    radaccts.caller_id, radaccts.called_id, radaccts.nas_id, radaccts.session_time, radaccts.framed_protocol, 
			    radaccts.bytes_in, radaccts.bytes_out, radaccts.session_status, radaccts.speed_string, radaccts.framed_ip_address, 
			    radaccts.nas_int_id, radaccts.subaccount_id, radaccts.acct_terminate_cause, radaccts.lt_time, radaccts.lt_bytes_in, radaccts.lt_bytes_out); RETURN; END;';
                          
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
$$
    LANGUAGE plpgsql; 
 
CREATE OR REPLACE FUNCTION radius_activesession_inserter(radaccts radius_activesession) RETURNS void
    AS  $BODY$
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

  
    insq_ := 'INSERT INTO radaccts' || datetx_ || ' (account_id, sessionid, interrim_update, date_start, date_end, caller_id, called_id, nas_id, session_time, framed_protocol, bytes_in, bytes_out, session_status, speed_string, framed_ip_address, nas_int_id, subaccount_id, acct_terminate_cause,lt_time,lt_bytes_in,lt_bytes_out) VALUES (' || radaccts_account_id || ',' || radaccts_sessionid || ',' || radaccts_interrim_update || ',' || radaccts_date_start || ',' || radaccts_date_end || ',' || radaccts_caller_id || ',' || adaccts_called_id || ',' || radaccts_nas_id || ',' || radaccts_session_time || ',' || radaccts_framed_protocol || ',' || radaccts_bytes_in || ',' || radaccts_bytes_out || ',' || radaccts_session_status || ',' || radaccts_speed_string || ',' || radaccts_framed_ip_address || ',' || radaccts_nas_int_id || ',' || radaccts_subaccount_id || ',' || radaccts_acct_terminate_cause || ',' || radaccts_lt_time || ',' || radaccts_lt_bytes_in || ',' || radaccts_lt_bytes_out ||');';
    EXECUTE insq_;
    RETURN;
END;$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
    

--19.02.2011
ALTER TABLE billservice_shedulelog ADD COLUMN prepaid_radius_traffic_reset timestamp without time zone;
ALTER TABLE billservice_shedulelog ADD COLUMN prepaid_radius_traffic_accrued timestamp without time zone;
CREATE TABLE billservice_accountprepaysradiustrafic (
    id serial NOT NULL PRIMARY KEY,
    account_tarif_id integer NOT NULL,
    prepaid_traffic_id integer NOT NULL,
    size double precision NOT NULL,
    direction integer NOT NULL,
    datetime timestamp with time zone NOT NULL
)
;

CREATE OR REPLACE FUNCTION shedulelog_radius_tr_reset_fn(account_id_ integer, accounttarif_id_ integer, reset_ timestamp without time zone)
  RETURNS void AS
$BODY$
BEGIN
        DELETE FROM billservice_accountprepaysradiustrafic WHERE account_tarif_id=accounttarif_id_;
    UPDATE billservice_shedulelog SET prepaid_radius_traffic_reset=reset_, accounttarif_id=accounttarif_id_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_radius_traffic_reset) VALUES(account_id_,accounttarif_id_, reset_);
    END IF;
    RETURN;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION shedulelog_radius_tr_reset_fn(integer, integer, timestamp without time zone) OWNER TO postgres;

CREATE OR REPLACE FUNCTION shedulelog_radius_tr_credit_fn(account_id_ integer, accounttarif_id_ integer, trts_id_ integer, size_ numeric, direction_ integer, coeff_ numeric, datetime_ timestamp without time zone)
  RETURNS void AS
$BODY$
DECLARE
     
BEGIN

	UPDATE billservice_accountprepaysradiustrafic SET size=size+size_*coeff_, direction=direction_, datetime=datetime_ WHERE account_tarif_id=accounttarif_id_;
	IF NOT FOUND THEN
	    INSERT INTO billservice_accountprepaysradiustrafic (account_tarif_id, prepaid_traffic_id, size, direction, datetime) VALUES(accounttarif_id_, trts_id_, size_*coeff_, direction_, datetime_);
	END IF;

	UPDATE billservice_shedulelog SET prepaid_radius_traffic_accrued=datetime_, accounttarif_id=accounttarif_id_ WHERE account_id=account_id_;
	IF NOT FOUND THEN
		INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_radius_traffic_accrued) VALUES(account_id_,accounttarif_id_, datetime_);
	END IF;
	RETURN;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

CREATE TABLE billservice_radiustraffic
(
  id serial NOT NULL,
  direction integer NOT NULL,
  tarification_step integer NOT NULL,
  rounding integer NOT NULL,
  prepaid_direction integer NOT NULL,
  prepaid_value integer NOT NULL,
  created timestamp with time zone DEFAULT now(),
  deleted timestamp with time zone,
  reset_prepaid_traffic boolean DEFAULT false,
  CONSTRAINT billservice_radiustraffic_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
CREATE TABLE billservice_radiustrafficnode
(
  id serial NOT NULL,
  radiustraffic_id integer NOT NULL,
  "value" numeric DEFAULT 0,
  timeperiod_id integer NOT NULL,
  "cost" numeric DEFAULT 0,
  CONSTRAINT billservice_radiustrafficnode_pkey PRIMARY KEY (id),
  CONSTRAINT billservice_radiustrafficnode_radiustraffic_id_fkey FOREIGN KEY (radiustraffic_id)
      REFERENCES billservice_radiustraffic (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT billservice_radiustrafficnode_timeperiod_id_fkey FOREIGN KEY (timeperiod_id)
      REFERENCES billservice_timeperiod (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
)
WITH (
  OIDS=FALSE
);
ALTER TABLE billservice_radiustrafficnode OWNER TO ebs;




ALTER TABLE billservice_radiustraffic
   ALTER COLUMN created SET DEFAULT now();
ALTER TABLE billservice_radiustraffic
   ALTER COLUMN created DROP NOT NULL;

ALTER TABLE billservice_radiustraffic
   ALTER COLUMN deleted DROP NOT NULL;
ALTER TABLE billservice_tariff
   ADD COLUMN radius_traffic_transmit_service_id integer;

ALTER TABLE billservice_timeaccessservice
   ADD COLUMN rounding integer DEFAULT 0;

ALTER TABLE billservice_timeaccessservice
   ADD COLUMN tarification_step integer DEFAULT 1;

--20.02.2011
ALTER TABLE billservice_traffictransaction ADD COLUMN radiustraffictransmitservice_id integer;
CREATE OR REPLACE FUNCTION traftrans_crt_cur_ins(datetx date) RETURNS void
    AS $$
DECLARE
    datetx_ text := to_char(datetx, 'YYYYMM01');
    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION traftrans_cur_ins (traftrns billservice_traffictransaction) RETURNS void AS ';
    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO traftrans';
    fn_bd_tx2_ text := '(traffictransmitservice_id, radiustraffictransmitservice_id, account_id, accounttarif_id, summ, datetime)
                          VALUES 
                         (traftrns.traffictransmitservice_id, traftrns.radiustraffictransmitservice_id,traftrns.account_id, traftrns.accounttarif_id, traftrns.summ, traftrns.datetime); RETURN; END;';        
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
$$
    LANGUAGE plpgsql;
    

    
CREATE OR REPLACE FUNCTION traftrans_crt_prev_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION traftrans_prev_ins (traftrns billservice_traffictransaction) RETURNS void AS ';
    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO traftrans';
    fn_bd_tx2_ text := '(traffictransmitservice_id, radiustraffictransmitservice_id,account_id, accounttarif_id, summ, datetime)
                          VALUES 
                         (traftrns.traffictransmitservice_id, traftrns.radiustraffictransmitservice_id, traftrns.account_id, traftrns.accounttarif_id, traftrns.summ, traftrns.datetime); RETURN; END;';
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
$$
    LANGUAGE plpgsql; 
 

CREATE OR REPLACE FUNCTION traftrans_inserter(traftrns billservice_traffictransaction) RETURNS void
    AS 
$BODY$
DECLARE
    datetx_ text := to_char(traftrns.datetime::date, 'YYYYMM01');
    insq_   text;

    traftrns_traffictransmitservice_id text;  
    traftrns_radiustraffictransmitservice_id text;
    traftrns_account_id    text;
    traftrns_accounttarif_id    text;
    traftrns_summ    text;
    traftrns_datetime    text;
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


	IF traftrns.datetime IS NULL THEN
	   traftrns_datetime := 'NULL';
	ELSE
	   traftrns_datetime := quote_literal(traftrns.datetime);
	END IF;

    insq_ := 'INSERT INTO traftrans' || datetx_ || ' (traffictransmitservice_id, radiustraffictransmitservice_id, account_id, accounttarif_id, summ, datetime) VALUES (' || traftrns_traffictransmitservice_id || ',' || traftrns_radiustraffictransmitservice_id || ',' || traftrns_account_id || ',' || traftrns_accounttarif_id || ',' || traftrns_summ || ',' || traftrns_datetime || ');';
    EXECUTE insq_;
    RETURN;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
    
ALTER TABLE billservice_traffictransmitnodes ALTER edge_value TYPE double precision;

--24.02.2011
CREATE TABLE qiwi_invoice
(
  id serial NOT NULL,
  txn_id character varying(64),
  account_id integer NOT NULL,
  phone character varying(15) NOT NULL,
  summ numeric NOT NULL,
  created timestamp without time zone,
  lifetime integer,
  check_after integer,
  accepted boolean DEFAULT false,
  deleted boolean DEFAULT false,
  date_accepted timestamp without time zone,
  autoaccept boolean DEFAULT false,
  "password" text DEFAULT ''::text,
  CONSTRAINT qiwi_invoice_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE qiwi_invoice OWNER TO ebs;


CREATE INDEX qiwi_invoice_account_id
  ON qiwi_invoice
  USING btree
  (account_id);


CREATE OR REPLACE FUNCTION account_payment_transaction_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN

IF (TG_OP = 'INSERT') AND NEW.accepted = TRUE THEN
UPDATE billservice_account SET ballance=ballance+NEW.summ WHERE id=NEW.account_id;
RETURN NEW;
ELSIF (TG_OP = 'DELETE') AND OLD.accepted = TRUE THEN
UPDATE billservice_account SET ballance=ballance-OLD.summ WHERE id=OLD.account_id;
RETURN OLD;
ELSIF (TG_OP = 'UPDATE') AND NEW.accepted = TRUE AND OLD.accepted = FALSE THEN
UPDATE billservice_account SET ballance=ballance+NEW.summ WHERE id=NEW.account_id;
RETURN NEW;
ELSIF (TG_OP = 'UPDATE') AND NEW.accepted = FALSE AND OLD.accepted = TRUE THEN
UPDATE billservice_account SET ballance=ballance-OLD.summ WHERE id=NEW.account_id;
RETURN NEW;
ELSIF (TG_OP = 'UPDATE') AND NEW.accepted = TRUE AND OLD.accepted = TRUE THEN
UPDATE billservice_account SET ballance=ballance-OLD.summ WHERE id=NEW.account_id;
UPDATE billservice_account SET ballance=ballance+NEW.summ WHERE id=NEW.account_id;
RETURN NEW;
END IF;
RETURN NULL;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

CREATE TRIGGER qiwi_trs_trg
  BEFORE INSERT OR UPDATE OR DELETE
  ON qiwi_invoice
  FOR EACH ROW
  EXECUTE PROCEDURE account_payment_transaction_trg_fn();
  

CREATE OR REPLACE FUNCTION card_activate_fn(login_ character varying, pin_ character varying, nas_id_ integer, account_ip_ inet)
  RETURNS record AS
$BODY$
DECLARE
    tarif_id_ int;
    account_id_ int;
    subaccount_id_ int;
    card_id_ int;
    sold_ timestamp without time zone;
    activated_ timestamp without time zone;
    card_data_ record;
    account_data_ record;
    tmp record;
    tmp_pass text;
BEGIN
    -- Получаем информацию о карточке, которая продана и у которой не истёк срок годности
    SELECT id, sold, activated, activated_by_id, nominal, tarif_id, pin INTO card_data_ FROM billservice_card WHERE "login"=login_ and sold is not Null and now() between start_date and end_date;
    -- Если карты нету - return
    IF (card_data_ is NULL) THEN
    RETURN tmp;

    -- Если карта уже продана, но ещё не активирвоана
    ELSIF card_data_.activated_by_id IS NULL and card_data_.sold is not NULL and card_data_.pin=pin_ THEN
    -- Создаём пользователя
        INSERT INTO billservice_account(username, "password", ipn_ip_address, ipn_status, status, created, ipn_added, allow_webcab, allow_expresscards, assign_dhcp_null, assign_dhcp_block, allow_vpn_null, allow_vpn_block)
        VALUES(login_, pin_, account_ip_, False, 1, now(), False, True, True, False, False, False, False) RETURNING id INTO account_id_;
    INSERT INTO billservice_subaccount(
             account_id, username, "password", ipn_ip_address, 
            nas_id, ipn_added, ipn_enabled, need_resync, 
            speed, allow_addonservice)
    VALUES (account_id_, login_, pin_, account_ip_, nas_id_, 
            False, False, False, '', True) RETURNING id INTO subaccount_id_;

    -- Добавлеяем пользователю тариф
        INSERT INTO billservice_accounttarif(account_id, tarif_id, datetime) VALUES(account_id_, card_data_.tarif_id, now());
        -- Пополняем счёт
        INSERT INTO billservice_transaction(bill, account_id, type_id, approved, tarif_id, summ, description, created)
        VALUES('Карта доступа', account_id_, 'ACCESS_CARD', True, card_data_.tarif_id, card_data_.nominal*(-1),'', now());
    -- Обновляем информацию о карточке
    UPDATE billservice_card SET activated = now(), activated_by_id = account_id_ WHERE id = card_data_.id;

    -- Выбираем нужную информацию
    SELECT account.id, subaccount.id, subaccount.password, subaccount.nas_id, bsat.tarif_id,  account.status, 
    account.balance_blocked, (account.ballance+account.credit) as ballance, account.disabled_by_limit, 
    tariff.active INTO account_data_ 
    FROM billservice_subaccount as subaccount
    JOIN billservice_account as account ON account.id=subaccount.account_id
    JOIN billservice_accounttarif as bsat ON bsat.id=(SELECT id FROM billservice_accounttarif as acct WHERE acct.account_id=account.id and acct.datetime<=now() ORDER BY acct.datetime DESC LIMIT 1)
    JOIN billservice_tariff as tariff on tariff.id=bsat.tarif_id
    WHERE  subaccount.id=subaccount_id_;
    RETURN account_data_;
    -- Если карта продана и уже активирована
    ELSIF (card_data_.sold is not Null) AND (card_data_.activated_by_id is not Null) THEN
    SELECT account.id, subaccount.id as subaccount_id, subaccount.password, subaccount.nas_id, bsat.tarif_id,  account.status, 
    account.balance_blocked, (account.ballance+account.credit) as ballance, account.disabled_by_limit, 
    tariff.active INTO account_data_
    FROM billservice_subaccount as subaccount
    JOIN billservice_account as account ON account.id=subaccount.account_id and account.id=card_data_.activated_by_id
    JOIN billservice_accounttarif as bsat ON bsat.id=(SELECT id FROM billservice_accounttarif as acct WHERE acct.account_id=account.id and acct.datetime<=now() ORDER BY acct.datetime DESC LIMIT 1)
    JOIN billservice_tariff as tariff on tariff.id=bsat.tarif_id
    WHERE subaccount.username=login_;
    UPDATE billservice_subaccount SET ipn_ip_address = account_ip_ WHERE id=account_data_.subaccount_id;
        RETURN account_data_;
    END IF; 

    RETURN tmp;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION card_activate_fn(character varying, character varying, integer, inet) OWNER TO postgres;

CREATE OR REPLACE FUNCTION rad_activesession_crt_cur_ins(datetx date) RETURNS void
    AS $$
DECLARE
    datetx_ text := to_char(datetx, 'YYYYMM01');
    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION rad_activesession_cur_ins (radaccts radius_activesession) RETURNS void AS ';
    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO radaccts';
    fn_bd_tx2_ text := '(account_id, sessionid, interrim_update, date_start, date_end, 
            caller_id, called_id, nas_id, session_time, framed_protocol, 
            bytes_in, bytes_out, session_status, speed_string, framed_ip_address, 
            nas_int_id, subaccount_id, acct_terminate_cause,lt_time, lt_bytes_in,lt_bytes_out)
                          VALUES 
                         (radaccts.account_id, radaccts.sessionid, radaccts.interrim_update, radaccts.date_start, radaccts.date_end, 
			    radaccts.caller_id, radaccts.called_id, radaccts.nas_id, radaccts.session_time, radaccts.framed_protocol, 
			    radaccts.bytes_in, radaccts.bytes_out, radaccts.session_status, radaccts.speed_string, radaccts.framed_ip_address, 
			    radaccts.nas_int_id, radaccts.subaccount_id, radaccts.acct_terminate_cause, radaccts.lt_time, radaccts.lt_bytes_in, radaccts.lt_bytes_out); RETURN; END;';
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
$$
    LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION radius_activesession_crt_prev_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');
    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION radius_activesession_prev_ins (radaccts radius_activesession) RETURNS void AS ';
    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO radaccts';
    fn_bd_tx2_ text := '(account_id, sessionid, interrim_update, date_start, date_end, 
            caller_id, called_id, nas_id, session_time, framed_protocol, 
            bytes_in, bytes_out, session_status, speed_string, framed_ip_address, 
            nas_int_id, subaccount_id, acct_terminate_cause,lt_time, lt_bytes_in, lt_bytes_out)
                          VALUES 
                         (radaccts.account_id, radaccts.sessionid, radaccts.interrim_update, radaccts.date_start, radaccts.date_end, 
			    radaccts.caller_id, radaccts.called_id, radaccts.nas_id, radaccts.session_time, radaccts.framed_protocol, 
			    radaccts.bytes_in, radaccts.bytes_out, radaccts.session_status, radaccts.speed_string, radaccts.framed_ip_address, 
			    radaccts.nas_int_id, radaccts.subaccount_id, radaccts.acct_terminate_cause, radaccts.lt_time, radaccts.lt_bytes_in, radaccts.lt_bytes_out); RETURN; END;';
                          
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
$$
    LANGUAGE plpgsql; 

--09.03.2011
ALTER TABLE billservice_subaccount
   ADD COLUMN vpn_ipv6_ip_address inet DEFAULT '::';

ALTER TABLE billservice_subaccount
   ADD COLUMN ipn_ipv6_ip_address inet DEFAULT '::';
ALTER TABLE billservice_subaccount
   ADD COLUMN vlan integer DEFAULT 0;

ALTER TABLE billservice_subaccount ADD COLUMN vpn_ipv6_ipinuse_id integer;

ALTER TABLE billservice_subaccount
  ADD CONSTRAINT billservice_subaccount_ipv6_vpnipinuse_fkey FOREIGN KEY (vpn_ipv6_ipinuse_id)
      REFERENCES billservice_ipinuse (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL;
      
--10.03.2010
ALTER TABLE auth_permission ALTER "name" TYPE character varying(256);
INSERT INTO billservice_templatetype(id,
            "name")
    VALUES (9, 'Отчёты');
      
ALTER TABLE billservice_template DROP CONSTRAINT billservice_template_type_id_fkey;
SELECT setval('public.billservice_template_id_seq', 9, true);
update billservice_account set   allow_ipn_with_null = false;
update billservice_account set     allow_ipn_with_minus  = false;
update billservice_account set     allow_ipn_with_block  = false;
ALTER TABLE billservice_subaccount
   ADD COLUMN allow_mac_update boolean DEFAULT False;
update billservice_subaccount set     allow_mac_update  = false;

--16.03.2011
ALTER TABLE billservice_accountprepaysradiustrafic
   ADD COLUMN "current" boolean DEFAULT False;

ALTER TABLE billservice_accountprepaystime
   ADD COLUMN "current" boolean DEFAULT False;

ALTER TABLE billservice_accountprepaystrafic
   ADD COLUMN "current" boolean DEFAULT False;


ALTER TABLE billservice_accountprepaysradiustrafic
   ADD COLUMN reseted boolean DEFAULT False;

ALTER TABLE billservice_accountprepaystime
   ADD COLUMN reseted boolean DEFAULT False;

ALTER TABLE billservice_accountprepaystrafic
   ADD COLUMN reseted boolean DEFAULT False;


CREATE OR REPLACE FUNCTION shedulelog_radius_tr_reset_fn(account_id_ integer, accounttarif_id_ integer, reset_ timestamp without time zone)
  RETURNS void AS
$BODY$
BEGIN
    UPDATE billservice_accountprepaysradiustrafic set reseted=True WHERE account_tarif_id in (SELECT id FROM billservice_accounttarif WHERE account_id=account_id_) and reseted=False and current=True;
    UPDATE billservice_shedulelog SET prepaid_radius_traffic_reset=reset_, accounttarif_id=accounttarif_id_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_radius_traffic_reset) VALUES(account_id_,accounttarif_id_, reset_);
    END IF;
    RETURN;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION shedulelog_radius_tr_reset_fn(integer, integer, timestamp without time zone) OWNER TO postgres;



CREATE OR REPLACE FUNCTION shedulelog_radius_tr_credit_fn(account_id_ integer, accounttarif_id_ integer, trts_id_ integer, need_radius_traffic_reset boolean, size_ numeric, direction_ integer, coeff_ numeric, datetime_ timestamp without time zone)
  RETURNS void AS
$BODY$
DECLARE
    old_size bigint;
BEGIN
    old_size:=0;
    IF need_radius_traffic_reset!=True THEN
        SELECT INTO old_size (SELECT size FROM billservice_accountprepaysradiustrafic WHERE account_tarif_id=accounttarif_id_ and current=True and reseted=False)::bigint;
    END IF;
    
    UPDATE billservice_accountprepaysradiustrafic as preptr SET current=False WHERE preptr.account_tarif_id in (SELECT id FROM billservice_accounttarif WHERE account_id=account_id_) and current=True;

    INSERT INTO billservice_accountprepaysradiustrafic (account_tarif_id, prepaid_traffic_id, size, direction, datetime, current) VALUES(accounttarif_id_, trts_id_, old_size+(size_*coeff_)::bigint, direction_, datetime_,True);


    UPDATE billservice_shedulelog SET prepaid_radius_traffic_accrued=datetime_, accounttarif_id=accounttarif_id_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_radius_traffic_accrued) VALUES(account_id_,accounttarif_id_, datetime_);
    END IF;
    RETURN;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION shedulelog_radius_tr_credit_fn(integer, integer, integer, boolean, numeric, integer, numeric, timestamp without time zone) OWNER TO postgres;

CREATE OR REPLACE FUNCTION shedulelog_time_reset_fn(account_id_ integer, accounttarif_id_ integer, reset_ timestamp without time zone)
  RETURNS void AS
$BODY$
BEGIN
    UPDATE billservice_accountprepaystime set reseted=False WHERE account_tarif_id in (SELECT id FROM billservice_accounttarif WHERE account_id=account_id_) and reseted=False and current=True;
    UPDATE billservice_shedulelog SET prepaid_time_reset=reset_, accounttarif_id=accounttarif_id_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_time_reset) VALUES(account_id_,accounttarif_id_, reset_);
    END IF;
    RETURN;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION shedulelog_time_reset_fn(integer, integer, timestamp without time zone) OWNER TO postgres;

CREATE OR REPLACE FUNCTION shedulelog_time_credit_fn(account_id_ integer, accounttarif_id_ integer, taccs_id_ integer, need_time_reset boolean, size_ integer, coeff_ double precision, datetime_ timestamp without time zone)
  RETURNS void AS
$BODY$
DECLARE
    old_size double precision;
BEGIN
    old_size:=0;
    IF need_time_reset!=True THEN
        SELECT INTO old_size (SELECT size FROM billservice_accountprepaystime WHERE account_tarif_id=accounttarif_id_ and current=True and reseted=False)::double precision;
    END IF;
    UPDATE billservice_accountprepaystime as preptr SET current=False WHERE current=True and preptr.account_tarif_id in (SELECT id FROM billservice_accounttarif WHERE account_id=account_id_);

    INSERT INTO billservice_accountprepaystime (account_tarif_id, size, datetime, prepaid_time_service_id, current) VALUES(accounttarif_id_, old_size+size_*coeff_, datetime_, taccs_id_, True);

    UPDATE billservice_shedulelog SET prepaid_time_accrued=datetime_, accounttarif_id=accounttarif_id_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_time_accrued) VALUES(account_id_,accounttarif_id_, datetime_);
    END IF;
    RETURN;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
  
  
CREATE OR REPLACE FUNCTION shedulelog_tr_reset_fn(account_id_ integer, accounttarif_id_ integer, reset_ timestamp without time zone)
  RETURNS void AS
$BODY$
BEGIN
    UPDATE billservice_accountprepaystrafic SET reseted=False WHERE account_tarif_id=accounttarif_id_ and current=True and reseted=False;
    UPDATE billservice_shedulelog SET prepaid_traffic_reset=reset_, accounttarif_id=accounttarif_id_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_traffic_reset) VALUES(account_id_,accounttarif_id_, reset_);
    END IF;
    RETURN;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION shedulelog_tr_reset_fn(integer, integer, timestamp without time zone) OWNER TO postgres;


CREATE OR REPLACE FUNCTION shedulelog_tr_reset_fn(account_id_ integer, accounttarif_id_ integer, reset_ timestamp without time zone)
  RETURNS void AS
$BODY$
BEGIN
    UPDATE billservice_accountprepaystrafic SET reseted=False WHERE account_tarif_id=accounttarif_id_ and current=True and reseted=False;
    UPDATE billservice_shedulelog SET prepaid_traffic_reset=reset_, accounttarif_id=accounttarif_id_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_traffic_reset) VALUES(account_id_,accounttarif_id_, reset_);
    END IF;
    RETURN;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION shedulelog_tr_reset_fn(integer, integer, timestamp without time zone) OWNER TO postgres;


CREATE OR REPLACE FUNCTION shedulelog_tr_credit_fn(account_id_ integer, accounttarif_id_ integer, trts_id_ integer, need_traffic_reset boolean,  coeff_ numeric, datetime_ timestamp without time zone)
  RETURNS void AS
$BODY$
DECLARE
        prepaid_tr_id_ int;
        size_ bigint;
        count_ int := 0;
        old_size bigint;
BEGIN
    FOR prepaid_tr_id_, size_ IN SELECT id, size FROM billservice_prepaidtraffic WHERE traffic_transmit_service_id=trts_id_ LOOP
        old_size:=0;
        IF need_traffic_reset!=True THEN
            SELECT INTO old_size (SELECT sum(size) FROM billservice_accountprepaystrafic WHERE account_tarif_id=accounttarif_id_ AND prepaid_traffic_id=prepaid_tr_id_ and current=True and reseted=False)::bigint;
        END IF;
      
        INSERT INTO billservice_accountprepaystrafic (account_tarif_id, prepaid_traffic_id, size, datetime, current) VALUES(accounttarif_id_, prepaid_tr_id_, old_size+(size_*coeff_)::bigint, datetime_, True);
        count_ := count_ + 1;
    END LOOP;
	UPDATE billservice_accountprepaystrafic as preptr SET current=False WHERE datetime<datetime_ and current=True and preptr.account_tarif_id in (SELECT id FROM billservice_accounttarif WHERE account_id=(SELECT account_id FROM billservice_accounttarif WHERE id=accounttarif_id_));    
    IF count_ > 0 THEN
        UPDATE billservice_shedulelog SET prepaid_traffic_accrued=datetime_, accounttarif_id=accounttarif_id_ WHERE account_id=account_id_;
        IF NOT FOUND THEN
                INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_traffic_accrued) VALUES(account_id_,accounttarif_id_, datetime_);
        END IF;
    END IF;
    RETURN;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;


ALTER FUNCTION shedulelog_tr_credit_fn(integer, integer, integer, boolean, numeric, timestamp without time zone) OWNER TO postgres;

ALTER TABLE billservice_traffictransmitnodes ALTER edge_value TYPE double precision;

ALTER TABLE billservice_accountprepaysradiustrafic
   ALTER COLUMN size SET DEFAULT 0;
ALTER TABLE billservice_accountprepaysradiustrafic
   ALTER COLUMN size DROP NOT NULL;

ALTER TABLE billservice_balancehistory
  DROP CONSTRAINT billservice_balancehistory_account_id_fkey;
  
DROP TABLE IF EXISTS auth_group_permissions;
DROP TABLE IF EXISTS auth_message;
DROP TABLE IF EXISTS auth_user_user_permissions;
DROP TABLE IF EXISTS auth_user_groups;
DROP TABLE IF EXISTS auth_permission;
DROP TABLE IF EXISTS auth_group;

--19.03.2011
ALTER TABLE billservice_card ADD CONSTRAINT billservice_card_login_pin_series_unique UNIQUE ("login", pin, series);

ALTER TABLE billservice_card
  DROP CONSTRAINT billservice_card_tarif_fkey;
  
ALTER TABLE billservice_card
  ADD CONSTRAINT billservice_card_tarif_fkey FOREIGN KEY (tarif_id)
      REFERENCES billservice_tariff (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL DEFERRABLE INITIALLY IMMEDIATE;

      ALTER TABLE billservice_card
DROP CONSTRAINT billservice_card_nas_fkey;
  
ALTER TABLE billservice_card
  ADD CONSTRAINT billservice_card_nas_fkey FOREIGN KEY (nas_id)
      REFERENCES nas_nas (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE billservice_card
  DROP CONSTRAINT billservice_card_template_fkey;
  
ALTER TABLE billservice_card
  ADD CONSTRAINT billservice_card_template_fkey FOREIGN KEY (template_id)
      REFERENCES billservice_template (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL DEFERRABLE INITIALLY IMMEDIATE;

      ALTER TABLE billservice_card
DROP CONSTRAINT billservice_card_account_fkey;

ALTER TABLE billservice_card
  ADD CONSTRAINT billservice_card_account_fkey FOREIGN KEY (account_id)
      REFERENCES billservice_account (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL DEFERRABLE INITIALLY IMMEDIATE;
      
ALTER TABLE billservice_card
  DROP CONSTRAINT billservice_card_ipinuse_fkey;
ALTER TABLE billservice_card
  ADD CONSTRAINT billservice_card_ipinuse_fkey FOREIGN KEY (ipinuse_id)
      REFERENCES billservice_ipinuse (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL DEFERRABLE INITIALLY IMMEDIATE;
      
ALTER TABLE billservice_card
   ADD COLUMN "type" integer;

update billservice_card set type=0 WHERE login is null and nas_id is null;
update billservice_card set type=1 WHERE login is not null and nas_id is null;
update billservice_card set type=2 WHERE login is not null and nas_id is not null;
ALTER TABLE billservice_card
   ALTER COLUMN "type" SET NOT NULL;


CREATE OR REPLACE FUNCTION card_activate_fn(login_ character varying, pin_ character varying, nas_id_ integer, account_ip_ inet)
  RETURNS record AS
$BODY$
DECLARE
    tarif_id_ int;
    account_id_ int;
    subaccount_id_ int;
    card_id_ int;
    sold_ timestamp without time zone;
    activated_ timestamp without time zone;
    card_data_ record;
    account_data_ record;
    tmp record;
    tmp_pass text;
BEGIN
    -- Получаем информацию о карточке, которая продана и у которой не истёк срок годности
    SELECT id, sold, activated, activated_by_id, nominal, tarif_id, pin INTO card_data_ FROM billservice_card WHERE type=1 and "login"=login_ and sold is not Null and now() between start_date and end_date;
    -- Если карты нету - return
    IF (card_data_ is NULL) THEN
    RETURN tmp;

    -- Если карта уже продана, но ещё не активирвоана
    ELSIF card_data_.activated_by_id IS NULL and card_data_.sold is not NULL and card_data_.pin=pin_ THEN
    -- Создаём пользователя
        INSERT INTO billservice_account(username, "password", ipn_ip_address, ipn_status, status, created, ipn_added, allow_webcab, allow_expresscards, assign_dhcp_null, assign_dhcp_block, allow_vpn_null, allow_vpn_block)
        VALUES(login_, pin_, account_ip_, False, 1, now(), False, True, True, False, False, False, False) RETURNING id INTO account_id_;
    INSERT INTO billservice_subaccount(
             account_id, username, "password", ipn_ip_address, 
            nas_id, ipn_added, ipn_enabled, need_resync, 
            speed, allow_addonservice)
    VALUES (account_id_, login_, pin_, account_ip_, nas_id_, 
            False, False, False, '', True) RETURNING id INTO subaccount_id_;

    -- Добавлеяем пользователю тариф
        INSERT INTO billservice_accounttarif(account_id, tarif_id, datetime) VALUES(account_id_, card_data_.tarif_id, now());
        -- Пополняем счёт
        INSERT INTO billservice_transaction(bill, account_id, type_id, approved, tarif_id, summ, description, created)
        VALUES('Карта доступа', account_id_, 'ACCESS_CARD', True, card_data_.tarif_id, card_data_.nominal*(-1),'', now());
    -- Обновляем информацию о карточке
    UPDATE billservice_card SET activated = now(), activated_by_id = account_id_ WHERE id = card_data_.id;

    -- Выбираем нужную информацию
    SELECT account.id, subaccount.id, subaccount.password, subaccount.nas_id, bsat.tarif_id,  account.status, 
    account.balance_blocked, (account.ballance+account.credit) as ballance, account.disabled_by_limit, 
    tariff.active INTO account_data_ 
    FROM billservice_subaccount as subaccount
    JOIN billservice_account as account ON account.id=subaccount.account_id
    JOIN billservice_accounttarif as bsat ON bsat.id=(SELECT id FROM billservice_accounttarif as acct WHERE acct.account_id=account.id and acct.datetime<=now() ORDER BY acct.datetime DESC LIMIT 1)
    JOIN billservice_tariff as tariff on tariff.id=bsat.tarif_id
    WHERE  subaccount.id=subaccount_id_;
    RETURN account_data_;
    -- Если карта продана и уже активирована
    ELSIF (card_data_.sold is not Null) AND (card_data_.activated_by_id is not Null) THEN
    SELECT account.id, subaccount.id as subaccount_id, subaccount.password, subaccount.nas_id, bsat.tarif_id,  account.status, 
    account.balance_blocked, (account.ballance+account.credit) as ballance, account.disabled_by_limit, 
    tariff.active INTO account_data_
    FROM billservice_subaccount as subaccount
    JOIN billservice_account as account ON account.id=subaccount.account_id and account.id=card_data_.activated_by_id
    JOIN billservice_accounttarif as bsat ON bsat.id=(SELECT id FROM billservice_accounttarif as acct WHERE acct.account_id=account.id and acct.datetime<=now() ORDER BY acct.datetime DESC LIMIT 1)
    JOIN billservice_tariff as tariff on tariff.id=bsat.tarif_id
    WHERE subaccount.username=login_;
    UPDATE billservice_subaccount SET ipn_ip_address = account_ip_ WHERE id=account_data_.subaccount_id;
        RETURN account_data_;
    END IF; 

    RETURN tmp;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION card_activate_fn(character varying, character varying, integer, inet) OWNER TO postgres;

ALTER TABLE billservice_account ALTER last_balance_null TYPE timestamp without time zone;

