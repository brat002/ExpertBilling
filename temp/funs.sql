CREATE OR REPLACE FUNCTION transaction_fn(bill_ character varying, account_id_ integer, type_id_ character varying, approved_ boolean, tarif_id_ integer, summ_ double precision, description_ text, created_ timestamp without time zone, ps_id_ integer, acctf_id_ integer, ps_condition_type_ integer) RETURNS void
    AS $$
DECLARE
    new_summ_ double precision;
    tr_id_ int;
BEGIN
    SELECT INTO new_summ_ summ_*(NOT EXISTS (SELECT id FROM billservice_suspendedperiod WHERE account_id=account_id AND (created_ BETWEEN start_date AND end_date)))::int;
    IF (ps_condition_type_ = 1) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance => 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    ELSIF (ps_condition_type_ = 2) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance < 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    END IF; 
    IF (new_summ_ > 0) THEN
        INSERT INTO billservice_transaction (bill, account_id,  type_id, approved,  tarif_id, summ, description, created) VALUES (bill_ , account_id_ ,  type_id_, approved_,  tarif_id_, new_summ_, description_, created_) RETURNING id INTO tr_id_;
    END IF;
    INSERT INTO billservice_periodicalservicehistory (service_id, transaction_id, accounttarif_id,  datetime) VALUES (ps_id_, tr_id_, acctf_id_, created_);
END;
$$
    LANGUAGE plpgsql;
    
CREATE OR REPLACE FUNCTION nfs_crt_prev_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMMDD');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION nfs_prev_ins (nfsr billservice_netflowstream) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO nfs';
                         
    fn_bd_tx2_ text := '(nas_id, account_id, tarif_id, date_start, src_addr, traffic_class_id, direction, traffic_transmit_node_id, dst_addr, octets, src_port, dst_port, protocol, checkouted, for_checkout)
                          VALUES 
                         (nfsr.nas_id, nfsr.account_id, nfsr.tarif_id, nfsr.date_start, nfsr.src_addr, 
                          nfsr.traffic_class_id, nfsr.direction, nfsr.traffic_transmit_node_id, nfsr.dst_addr, nfsr.octets, nfsr.src_port, 
                          nfsr.dst_port, nfsr.protocol, nfsr.checkouted, nfsr.for_checkout); RETURN; END;';
                          
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';


    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION nfs_prev_datechk(nfs_date timestamp without time zone) RETURNS integer AS ';

    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    --ch_fn_bd_tx2_ text := '; d_e_ date := DATE ';
    --ch_fn_bd_tx3_ text := 'IF    nfs_date < d_s_ THEN RETURN -1; ELSIF nfs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';
    
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    nfs_date < d_s_ THEN RETURN -1; ELSIF nfs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';

    ch_fn_tx2_ text := ' LANGUAGE plpgsql VOLATILE COST 100;';

    qts_ text := 'CHK % % %';
    
    
   oneday_ text := interval '1 day';
   query_ text;
BEGIN    


        EXECUTE  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;


        --EXECUTE  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '; BEGIN ' || ch_fn_bd_tx3_) || ch_fn_tx2_;
        
        
        query_ :=  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '+ interval ' || quote_literal(oneday_) ||  ch_fn_bd_tx3_) || fn_tx2_;
        
        EXECUTE query_;
        
    RETURN;

END;
$$
    LANGUAGE plpgsql;