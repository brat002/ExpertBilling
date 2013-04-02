CREATE INDEX  psh20090501_created
  ON psh20090501
  USING btree
  (created);

CREATE INDEX  psh20090601_created
  ON psh20090601
  USING btree
  (created);

CREATE INDEX  psh20090701_created
  ON psh20090701
  USING btree
  (created);

CREATE INDEX  psh20090801_created
  ON psh20090801
  USING btree
  (created);

CREATE INDEX  psh20090901_created
  ON psh20090901
  USING btree
  (created);

CREATE INDEX  psh20091001_created
  ON psh20091001
  USING btree
  (created);
  
CREATE INDEX  psh20091101_created
  ON psh20091101
  USING btree
  (created);

CREATE INDEX  psh20091201_created
  ON psh20091201
  USING btree
  (created);

---
CREATE INDEX  psh20100101_created
  ON psh20100101
  USING btree
  (created);

CREATE INDEX  psh20100201_created
  ON psh20100201
  USING btree
  (created);

CREATE INDEX  psh20100301_created
  ON psh20100301
  USING btree
  (created);

CREATE INDEX  psh20100401_created
  ON psh20100401
  USING btree
  (created);

CREATE INDEX  psh20100501_created
  ON psh20100501
  USING btree
  (created);

CREATE INDEX  psh20100601_created
  ON psh20100601
  USING btree
  (created);

CREATE INDEX  psh20100701_created
  ON psh20100701
  USING btree
  (created);

CREATE INDEX  psh20100801_created
  ON psh20100801
  USING btree
  (created);

CREATE INDEX  psh20100901_created
  ON psh20100901
  USING btree
  (created);

CREATE INDEX  psh20101001_created
  ON psh20101001
  USING btree
  (created);
  
CREATE INDEX  psh20101101_created
  ON psh20101101
  USING btree
  (created);

CREATE INDEX  psh20101201_created
  ON psh20101201
  USING btree
  (created);

---
CREATE INDEX  psh20110101_created
  ON psh20110101
  USING btree
  (created);

CREATE INDEX  psh20110201_created
  ON psh20110201
  USING btree
  (created);

CREATE INDEX  psh20110301_created
  ON psh20110301
  USING btree
  (created);

CREATE INDEX  psh20110401_created
  ON psh20110401
  USING btree
  (created);

CREATE INDEX  psh20110501_created
  ON psh20110501
  USING btree
  (created);

CREATE INDEX  psh20110601_created
  ON psh20110601
  USING btree
  (created);

CREATE INDEX  psh20110701_created
  ON psh20110701
  USING btree
  (created);

CREATE INDEX  psh20110801_created
  ON psh20110801
  USING btree
  (created);

CREATE INDEX  psh20110901_created
  ON psh20110901
  USING btree
  (created);

CREATE INDEX  psh20111001_created
  ON psh20111001
  USING btree
  (created);
  
CREATE INDEX  psh20111101_created
  ON psh20111101
  USING btree
  (created);

CREATE INDEX  psh20111201_created
  ON psh20111201
  USING btree
  (created);
---

CREATE INDEX  psh20120101_created
  ON psh20120101
  USING btree
  (created);

CREATE INDEX  psh20120201_created
  ON psh20120201
  USING btree
  (created);

CREATE INDEX  psh20120301_created
  ON psh20120301
  USING btree
  (created);

CREATE INDEX  psh20120401_created
  ON psh20120401
  USING btree
  (created);

CREATE INDEX  psh20120501_created
  ON psh20120501
  USING btree
  (created);

CREATE INDEX  psh20120601_created
  ON psh20120601
  USING btree
  (created);

CREATE INDEX  psh20120701_created
  ON psh20120701
  USING btree
  (created);

CREATE INDEX  psh20120801_created
  ON psh20120801
  USING btree
  (created);

CREATE INDEX  psh20120901_created
  ON psh20120901
  USING btree
  (created);

CREATE INDEX  psh20121001_created
  ON psh20121001
  USING btree
  (created);
  
CREATE INDEX  psh20121101_created
  ON psh20121101
  USING btree
  (created);

CREATE INDEX  psh20121201_created
  ON psh20121201
  USING btree
  (created);
  


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
  