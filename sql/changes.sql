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

CREATE TRIGGER clear_tariff_services_trg
  BEFORE DELETE
  ON billservice_tariff
  FOR EACH ROW
  EXECUTE PROCEDURE clear_tariff_services_trg_fn();
  
  
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
      
      
---11.08.2009
ALTER TABLE billservice_accounttarif ADD COLUMN periodical_billed boolean DEFAULT FALSE;

UPDATE billservice_accounttarif SET periodical_billed=FALSE;

UPDATE billservice_accounttarif as acctf1 SET periodical_billed=TRUE WHERE acctf1.id in (SELECT acctf2.id FROM billservice_accounttarif AS acctf2 WHERE acctf2.account_id=acctf1.account_id and acctf2.datetime < (SELECT datetime FROM billservice_accounttarif AS att WHERE att.account_id=acctf1.account_id and att.datetime<now()ORDER BY datetime DESC LIMIT 1));

---16.08.2009 16:22
 CREATE OR REPLACE FUNCTION check_allowed_users_trg_fn() RETURNS trigger AS 
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
 