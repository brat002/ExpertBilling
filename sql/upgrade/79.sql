
CREATE OR REPLACE FUNCTION gpst_ins_trg_fn()
  RETURNS trigger AS
$BODY$
DECLARE
    cur_chk int;
    prev_chk int;
BEGIN

BEGIN
    
    EXECUTE gpst_inserter(NEW);
-- Complet
-- Completed on 2012-05-28 20:30:34 FET

--
-- PostgreSQL database dump complete
--
ed on 2012-05-28 20:30:34 FET

--
-- PostgreSQL database dump complete
--
    
EXCEPTION 
  WHEN undefined_table THEN
    EXECUTE gpst_crt_pdb(NEW.datetime::date);
    EXECUTE gpst_inserter(NEW);
  END;

  
    RETURN NULL;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
-- Completed on 2012-05-28 20:30:34 FET

--
-- PostgreSQL database dump complete
--
  
  COST 100;

DROP FUNCTION gpst_crt_pdb(date);
CREATE OR REPLACE FUNCTION gpst_crt_pdb(datetx date)
  RETURNS void AS
$BODY$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');
    datetx_e_ text := to_char((datetx + interval '1 month')::date, 'YYYYMM01');

    qt_dtx_ text;
    qt_dtx_e_ text;


    chk_tx1_ text := 'CHECK ( datetime >= DATE #stdtx# AND datetime < DATE #eddtx# )';
    ct_tx1_ text := 'CREATE TABLE gpst#rpdate# (
                     #chk#,
                     CONSTRAINT gpst#rpdate#_id_pkey PRIMARY KEY (id) ) 
                     INHERITS (billservice_groupstat) 
                     WITH (OIDS=FALSE);                     
                     CREATE INDEX gpst#rpdate#_datetime_id ON gpst#rpdate# USING btree (datetime);
                     CREATE INDEX gpst#rpdate#_gr_acc_dt_id ON gpst#rpdate# USING btree (group_id, account_id, datetime);
                     CREATE INDEX gpst#rpdate#_group_id ON gpst#rpdate# USING btree (group_id);
                     ';
                    

    chk_       text;
    ct_query_  text;
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

DROP FUNCTION gpst_inserter(billservice_groupstat);

CREATE OR REPLACE FUNCTION gpst_inserter(gpstr billservice_groupstat)
  RETURNS void AS
$BODY$
DECLARE
    datetx_ text := to_char(gps
-- Completed on 2012-05-28 20:30:34 FET

--
-- PostgreSQL database dump complete
--
    tr.datetime::date, 'YYYYMM01');
    insq_   text;
    ttrn_classes_ text; 
    ttrn_classbytes_ text; 
    ttrn_max_class_ int; 
    accounttarif_id_ int;
    transaction_id_ int;
 
BEGIN
    
    IF gpstr.classes IS NULL THEN
       ttrn_classes_ := quote_literal('{}'::int[]);
    ELSE
       ttrn_classes_ := quote_literal(gpstr.classes);
    END IF;
    IF gpstr.classbytes IS NULL THEN
       ttrn_classbytes_ := quote_literal('{}'::bigint[]);
    ELSE
       ttrn_classbytes_ := quote_literal(gpstr.classbytes);
    END IF;    
    IF gpstr.max_class IS NULL THEN
       ttrn_max_class_ := 'NULL';
    ELSE
       ttrn_max_class_ := gpstr.max_class;
    END IF;

    IF gpstr.accounttarif_id IS NULL THEN
       accounttarif_id_ := 'NULL';
    ELSE
       accounttarif_id_ := gpstr.accounttarif_id;
    END IF;

    IF gpstr.transaction_id IS NULL THEN
       transaction_id_ := 'NULL';
    ELSE
       transaction_id_ := gpstr.transaction_id;
    END IF;
    
    
    insq_ := 'INSERT INTO gpst' || datetx_ || ' (group_id, account_id, bytes, datetime, classes, classbytes, max_class, accounttarif_id, transaction_id) VALUES (' 
    || gpstr.group_id || ',' || gpstr.account_id || ','  || gpstr.bytes || ',' || quote_literal(gpstr.datetime) || ',' ||ttrn_classes_ || ',' || ttrn_classbytes_ || ',' ||  ttrn_max_class_ || ',' || accounttarif_id_ ||  ',' || transaction_id_ ||');';
    EXECUTE insq_;
    RETURN;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
  
  -- Function: traftrans_crt_pdb(date)

-- DROP FUNCTION traftrans_crt_pdb(date);

CREATE OR REPLACE FUNCTION traftrans_crt_pdb(datetx date)
  RETURNS integer AS
$BODY$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');
    datetx_e_ text := to_char((datetx + interval '1 month')::date, 'YYYYMM01');

    qt_dtx_ text;
    qt_dtx_e_ text;

    chk_tx1_ text := 'CHECK ( created >= DATE #stdtx# AND created < DATE #eddtx# )';
    ct_tx1_ text := 'CREATE TABLE traftrans#rpdate# (
                     #chk#,
                     CONSTRAINT traftrans#rpdate#_id_pkey PRIMARY KEY (id) ) 
                     INHERITS (billservice_traffictransaction) 
                     WITH (OIDS=FALSE);                     
                     CREATE INDEX traftrans#rpdate#_account_id ON traftrans#rpdate# USING btree (account_id);
                     CREATE TRIGGER acc_tftrans_trg AFTER INSERT OR UPDATE OR DELETE ON traftrans#rpdate# FOR EACH ROW EXECUTE PROCEDURE account_transaction_trg_fn();
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

    RETURN 0;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

  
  