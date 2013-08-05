-- Function: radius_activesession_trs_crt_pdb(date)

-- DROP FUNCTION radius_activesession_trs_crt_pdb(date);

CREATE OR REPLACE FUNCTION radius_activesession_trs_crt_pdb(datetx date)
  RETURNS integer AS
$BODY$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');
    datetx_e_ text := to_char((datetx + interval '1 month')::date, 'YYYYMM01');

    qt_dtx_ text;
    qt_dtx_e_ text;


    chk_tx1_ text := 'CHECK ( date_start >= DATE #stdtx# AND date_start < DATE #eddtx# )';
    ct_tx1_ text := 'CREATE TABLE radaccts#rpdate# (
                     #chk#,
                     CONSTRAINT radaccts#rpdate#_id_pkey PRIMARY KEY (id) ) 
                     INHERITS (radius_activesession) 
                     WITH (OIDS=FALSE);                     
                     CREATE INDEX radaccts#rpdate#_account_id ON radaccts#rpdate# USING btree (account_id);
                     CREATE INDEX radaccts#rpdate#_subaccount_id ON radaccts#rpdate# USING btree (subaccount_id);
                     CREATE INDEX radaccts#rpdate#_session_status ON radaccts#rpdate# USING btree (session_status);
                     CREATE INDEX radaccts#rpdate#_acct_update ON radaccts#rpdate# USING btree (sessionid, nas_id, account_id, framed_protocol, nas_port_id);
                     CREATE INDEX radaccts#rpdate#_acct_update_date_end ON radaccts#rpdate# USING btree (sessionid, nas_id, account_id, framed_protocol, nas_port_id, date_end);
                     CREATE INDEX radaccts#rpdate#_acct_session_counters ON radaccts#rpdate# USING btree (session_time, lt_time, bytes_in, lt_bytes_in, bytes_out, lt_bytes_out, date_end);
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

CREATE INDEX  radaccts20130501_acct_session_counters ON radaccts20130501 USING btree (session_time, lt_time, bytes_in, lt_bytes_in, bytes_out, lt_bytes_out, date_end);
CREATE INDEX  radaccts20130601_acct_session_counters ON radaccts20130601 USING btree (session_time, lt_time, bytes_in, lt_bytes_in, bytes_out, lt_bytes_out, date_end);
CREATE INDEX  radaccts20130701_acct_session_counters ON radaccts20130701 USING btree (session_time, lt_time, bytes_in, lt_bytes_in, bytes_out, lt_bytes_out, date_end);
CREATE INDEX  radaccts20130801_acct_session_counters ON radaccts20130801 USING btree (session_time, lt_time, bytes_in, lt_bytes_in, bytes_out, lt_bytes_out, date_end);

  

  
  