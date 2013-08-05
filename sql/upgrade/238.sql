
CREATE OR REPLACE FUNCTION billservice_balancehistory_crt_pdb(datetx date)
  RETURNS void AS
$BODY$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');
    datetx_e_ text := to_char((datetx + interval '1 month')::date, 'YYYYMM01');

    qt_dtx_ text;
    qt_dtx_e_ text;


    chk_tx1_ text := 'CHECK ( datetime >= DATE #stdtx# AND datetime < DATE #eddtx# )';
    ct_tx1_ text := 'CREATE TABLE billservice_balancehistory#rpdate# (
                     #chk#,
                     CONSTRAINT billservice_balancehistory#rpdate#_id_pkey PRIMARY KEY (id) ) 
                     INHERITS (billservice_balancehistory) 
                     WITH (OIDS=FALSE);                     
                     CREATE INDEX billservice_balancehistory#rpdate#_account_id ON billservice_balancehistory#rpdate# USING btree (account_id);
                     CREATE INDEX billservice_balancehistory#rpdate#_datetime ON billservice_balancehistory#rpdate# USING btree (datetime);
                     CREATE INDEX billservice_balancehistory#rpdate#_id ON billservice_balancehistory#rpdate# USING btree (id);
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



CREATE OR REPLACE FUNCTION billservice_balancehistory_ins_trg_fn()
  RETURNS trigger AS
$BODY$
DECLARE
    cur_chk boolean;
    table_name text;
BEGIN
    table_name:='billservice_balancehistory' || to_char(NEW.datetime, 'YYYYMM01');
    select INTO cur_chk exists(select relname from pg_class where relname = table_name::text and relkind='r');
    
    IF cur_chk = True THEN
        EXECUTE 'INSERT INTO ' || table_name || ' SELECT (' || quote_literal(NEW) || '::' || TG_RELID::regclass || ').*';
    ELSE 
        BEGIN
            PERFORM billservice_balancehistory_crt_pdb(NEW.datetime::date);
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

CREATE  TRIGGER billservice_balancehistory_ins_trg
  BEFORE INSERT
  ON billservice_balancehistory
  FOR EACH ROW
  EXECUTE PROCEDURE billservice_balancehistory_ins_trg_fn();


CREATE OR REPLACE FUNCTION billservice_balancehistory_del_trg_fn()
  RETURNS trigger AS
$BODY$
    BEGIN
        INSERT INTO billservice_balancehistory VALUES( OLD.*);
        RETURN OLD;
    END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;


CREATE TRIGGER billservice_balancehistory_del_trg
  AFTER DELETE
  ON billservice_balancehistory
  FOR EACH ROW
  EXECUTE PROCEDURE billservice_balancehistory_del_trg_fn();
  
delete from billservice_balancehistory;
DROP TRIGGER billservice_balancehistory_del_trg ON billservice_balancehistory;
