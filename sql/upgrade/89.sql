-- Function: psh_crt_pdb(date)

-- DROP FUNCTION psh_crt_pdb(date);

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
                     CREATE INDEX psh#rpdate#_accounttarif_id ON psh#rpdate# USING btree (accounttarif_id);
                     CREATE INDEX psh#rpdate#_account_id ON psh#rpdate# USING btree (account_id);
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

  