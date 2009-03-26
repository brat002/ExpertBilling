
SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;


CREATE PROCEDURAL LANGUAGE plpgsql;


ALTER PROCEDURAL LANGUAGE plpgsql OWNER TO mikrobill;

SET search_path = public, pg_catalog;


CREATE TYPE intbig_gkey;



CREATE FUNCTION _intbig_in(cstring) RETURNS intbig_gkey
    AS '$libdir/_int', '_intbig_in'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public._intbig_in(cstring) OWNER TO mikrobill;


CREATE FUNCTION _intbig_out(intbig_gkey) RETURNS cstring
    AS '$libdir/_int', '_intbig_out'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public._intbig_out(intbig_gkey) OWNER TO mikrobill;


CREATE TYPE intbig_gkey (
    INTERNALLENGTH = variable,
    INPUT = _intbig_in,
    OUTPUT = _intbig_out,
    ALIGNMENT = int4,
    STORAGE = plain
);


ALTER TYPE public.intbig_gkey OWNER TO mikrobill;


CREATE TYPE query_int;



CREATE FUNCTION bqarr_in(cstring) RETURNS query_int
    AS '$libdir/_int', 'bqarr_in'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.bqarr_in(cstring) OWNER TO mikrobill;


CREATE FUNCTION bqarr_out(query_int) RETURNS cstring
    AS '$libdir/_int', 'bqarr_out'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.bqarr_out(query_int) OWNER TO mikrobill;


CREATE TYPE query_int (
    INTERNALLENGTH = variable,
    INPUT = bqarr_in,
    OUTPUT = bqarr_out,
    ALIGNMENT = int4,
    STORAGE = plain
);


ALTER TYPE public.query_int OWNER TO mikrobill;


CREATE TYPE targetinfo AS (
	target oid,
	schema oid,
	nargs integer,
	argtypes oidvector,
	targetname name,
	argmodes "char"[],
	argnames text[],
	targetlang oid,
	fqname text,
	returnsset boolean,
	returntype oid
);


ALTER TYPE public.targetinfo OWNER TO postgres;


CREATE TYPE var AS (
	name text,
	varclass character(1),
	linenumber integer,
	isunique boolean,
	isconst boolean,
	isnotnull boolean,
	dtype oid,
	value text
);


ALTER TYPE public.var OWNER TO postgres;


CREATE FUNCTION _int_contained(integer[], integer[]) RETURNS boolean
    AS '$libdir/_int', '_int_contained'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public._int_contained(integer[], integer[]) OWNER TO mikrobill;


COMMENT ON FUNCTION _int_contained(integer[], integer[]) IS 'contained in';



CREATE FUNCTION _int_contains(integer[], integer[]) RETURNS boolean
    AS '$libdir/_int', '_int_contains'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public._int_contains(integer[], integer[]) OWNER TO mikrobill;


COMMENT ON FUNCTION _int_contains(integer[], integer[]) IS 'contains';



CREATE FUNCTION _int_different(integer[], integer[]) RETURNS boolean
    AS '$libdir/_int', '_int_different'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public._int_different(integer[], integer[]) OWNER TO mikrobill;


COMMENT ON FUNCTION _int_different(integer[], integer[]) IS 'different';



CREATE FUNCTION _int_inter(integer[], integer[]) RETURNS integer[]
    AS '$libdir/_int', '_int_inter'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public._int_inter(integer[], integer[]) OWNER TO mikrobill;


CREATE FUNCTION _int_overlap(integer[], integer[]) RETURNS boolean
    AS '$libdir/_int', '_int_overlap'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public._int_overlap(integer[], integer[]) OWNER TO mikrobill;


COMMENT ON FUNCTION _int_overlap(integer[], integer[]) IS 'overlaps';



CREATE FUNCTION _int_same(integer[], integer[]) RETURNS boolean
    AS '$libdir/_int', '_int_same'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public._int_same(integer[], integer[]) OWNER TO mikrobill;


COMMENT ON FUNCTION _int_same(integer[], integer[]) IS 'same as';



CREATE FUNCTION _int_union(integer[], integer[]) RETURNS integer[]
    AS '$libdir/_int', '_int_union'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public._int_union(integer[], integer[]) OWNER TO mikrobill;




CREATE FUNCTION account_transaction_trg_fn() RETURNS trigger
    AS $$
    BEGIN

        IF    (TG_OP = 'INSERT') THEN
            UPDATE billservice_account SET ballance=ballance-NEW.summ WHERE id=NEW.account_id;
            RETURN NEW;
        ELSIF (TG_OP = 'DELETE') THEN
            UPDATE billservice_account SET ballance=ballance+OLD.summ WHERE id=OLD.account_id;
            RETURN OLD;
        ELSIF (TG_OP = 'UPDATE') THEN
                UPDATE billservice_account SET ballance=ballance+OLD.summ WHERE id=OLD.account_id;
                UPDATE billservice_account SET ballance=ballance-NEW.summ WHERE id=NEW.account_id;             
                RETURN NEW;
        END IF;
    END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.account_transaction_trg_fn() OWNER TO mikrobill;




CREATE FUNCTION block_balance(account_id integer) RETURNS void
    AS $$
BEGIN
	UPDATE billservice_account SET balance_blocked=TRUE WHERE id=account_id;
RETURN;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.block_balance(account_id integer) OWNER TO postgres;


CREATE FUNCTION boolop(integer[], query_int) RETURNS boolean
    AS '$libdir/_int', 'boolop'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.boolop(integer[], query_int) OWNER TO mikrobill;


COMMENT ON FUNCTION boolop(integer[], query_int) IS 'boolean operation with array';



CREATE FUNCTION bsearch_(sortedar double precision[], value_ double precision) RETURNS integer
    AS $$
DECLARE
    high int;
    low int;
    mid int;
    leftr double precision[];
    rightr double precision[];
    l_idx double precision;
    mid_idx double precision;
BEGIN
	high := array_upper(sortedar, 1);
	low := 1;
	
	IF high IS NULL THEN
	    RETURN NULL;
	END IF;
	
	WHILE low <= high LOOP
	    mid  := (low + high) / 2;
	    IF (sortedar[mid] > value_) THEN
	        high := mid - 1;
	    ELSIF (sortedar[mid] < value_) THEN
	        low  := mid + 1;
	    ELSE
	        RETURN mid;
	    END IF;
	END LOOP; 
	   
	RETURN -1;

END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.bsearch_(sortedar double precision[], value_ double precision) OWNER TO postgres;


CREATE FUNCTION card_activate_fn(login_ character varying, pin_ character varying, nas_id_ integer, account_ip_ inet) RETURNS record
    AS $$
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
    SELECT id, sold, activated, activated_by_id, nominal, tarif_id INTO card_data_ FROM billservice_card WHERE "login"=login_ and pin=pin_ and sold is not Null and now() between start_date and end_date;
    IF card_data_ is NULL THEN
	RETURN tmp;
    ELSIF card_data_.activated_by_id IS NULL and card_data_.sold is not NULL THEN
        INSERT INTO billservice_account(username, "password", nas_id, ipn_ip_address, ipn_status, status, created, ipn_added, allow_webcab, allow_expresscards, assign_dhcp_null)
        VALUES(login_, pin_, nas_id_, account_ip_, False, True, now(), False, True, True, False) RETURNING id INTO account_id_;
      
        INSERT INTO billservice_accounttarif(account_id, tarif_id, datetime) VALUES(account_id_, card_data_.tarif_id, now());
        INSERT INTO billservice_transaction(bill, account_id, type_id, approved, tarif_id, summ, description, created)
        VALUES('Карта доступа', account_id_, 'ACCESS_CARD', True, card_data_.tarif_id, card_data_.nominal*(-1),'', now());
	UPDATE billservice_card SET activated = now(), activated_by_id = account_id_ WHERE id = card_data_.id;
	
	UPDATE billservice_account SET ipn_ip_address = account_ip_ WHERE id = account_id_;
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
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.card_activate_fn(login_ character varying, pin_ character varying, nas_id_ integer, account_ip_ inet) OWNER TO mikrobill;


CREATE FUNCTION check_allowed_users_trg_fn() RETURNS trigger
    AS $$ DECLARE counted_num_ int; 
                         allowed_num_ int := 200; 
			 BEGIN 
				SELECT count(*) INTO counted_num_ FROM billservice_account;
				IF counted_num_ + 1 > allowed_num_ THEN
				    RAISE EXCEPTION 'Amount of users[% + 1] will exceed allowed[%] for the license file!', counted_num_, allowed_num_;
				ELSE 
				    RETURN NEW;
				END IF; 
				END; $$
    LANGUAGE plpgsql;


ALTER FUNCTION public.check_allowed_users_trg_fn() OWNER TO mikrobill;


CREATE FUNCTION credit_account(account_id integer, sum double precision) RETURNS void
    AS $$
BEGIN
	UPDATE billservice_account SET ballance=ballance-sum WHERE id=account_id;
RETURN;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.credit_account(account_id integer, sum double precision) OWNER TO postgres;


CREATE FUNCTION crt_allowed_checker(allowed integer) RETURNS void
    AS $$
DECLARE

    allowed_ text := allowed::text;


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION check_allowed_users_trg_fn () RETURNS trigger AS ';


    fn_bd_tx1_ text := ' DECLARE counted_num_ int; 
                         allowed_num_ int := ';
    fn_bd_tx2_ text := '; 
			 BEGIN 
				SELECT count(*) INTO counted_num_ FROM billservice_account;
				IF counted_num_ + 1 > allowed_num_ THEN
				    RAISE EXCEPTION ';
    fn_bd_tx3_ text := 			    ', counted_num_, allowed_num_;
				ELSE 
				    RETURN NEW;
				END IF; 
				END; ';


    fn_tx2_ text := ' LANGUAGE plpgsql VOLATILE COST 100;';

    exception_ text := 'Amount of users[% + 1] will exceed allowed[%] for the license file!';
BEGIN	
        EXECUTE  fn_tx1_  || quote_literal(fn_bd_tx1_ || allowed_ || fn_bd_tx2_ || quote_literal(exception_) || fn_bd_tx3_) || fn_tx2_;
	RETURN;

END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.crt_allowed_checker(allowed integer) OWNER TO mikrobill;


CREATE FUNCTION crt_allowed_checker(allowed bigint) RETURNS void
    AS $$
DECLARE

    allowed_ text := allowed::text;


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION check_allowed_users_trg_fn () RETURNS trigger AS ';


    fn_bd_tx1_ text := ' DECLARE counted_num_ bigint; 
                         allowed_num_ bigint := ';
    fn_bd_tx2_ text := '; 
			 BEGIN 
				SELECT count(*) INTO counted_num_ FROM billservice_account;
				IF counted_num_ + 1 > allowed_num_ THEN
				    RAISE EXCEPTION ';
    fn_bd_tx3_ text := 			    ', counted_num_, allowed_num_;
				ELSE 
				    RETURN NEW;
				END IF; 
				END; ';


    fn_tx2_ text := ' LANGUAGE plpgsql VOLATILE COST 100;';

    exception_ text := 'Amount of users[% + 1] will exceed allowed[%] for the license file!';
BEGIN	
        EXECUTE  fn_tx1_  || quote_literal(fn_bd_tx1_ || allowed_ || fn_bd_tx2_ || quote_literal(exception_) || fn_bd_tx3_) || fn_tx2_;
	RETURN;

END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.crt_allowed_checker(allowed bigint) OWNER TO mikrobill;


CREATE FUNCTION debit_account(account_id integer, sum double precision) RETURNS void
    AS $$
BEGIN
	UPDATE billservice_account SET ballance=ballance+sum WHERE id=account_id;
RETURN;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.debit_account(account_id integer, sum double precision) OWNER TO postgres;





CREATE FUNCTION del_nfs_trg_fn() RETURNS trigger
    AS $$
    BEGIN
        INSERT INTO billservice_netflowstream (nas_id, account_id, tarif_id, date_start, src_addr, traffic_class_id, 
            direction, traffic_transmit_node_id, dst_addr, octets, src_port, 
            dst_port, protocol, checkouted, for_checkout) VALUES( OLD.nas_id, OLD.account_id, OLD.tarif_id, OLD.date_start, OLD.src_addr, 
            OLD.traffic_class_id, OLD.direction, OLD.traffic_transmit_node_id, OLD.dst_addr, OLD.octets, OLD.src_port, 
            OLD.dst_port, OLD.protocol, OLD.checkouted, OLD.for_checkout);
        RETURN OLD;
    END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.del_nfs_trg_fn() OWNER TO mikrobill;


CREATE FUNCTION free_unused_account_ip_trg_fn() RETURNS trigger
    AS $$
BEGIN


IF (TG_OP = 'UPDATE') THEN
    IF (NEW.vpn_ipinuse_id is Null and OLD.vpn_ipinuse_id is not Null) THEN
	DELETE FROM billservice_ipinuse WHERE id=OLD.vpn_ipinuse_id;
    END IF;
    
    IF (NEW.ipn_ipinuse_id is Null and OLD.ipn_ipinuse_id is not Null) THEN
        DELETE FROM billservice_ipinuse WHERE id=OLD.ipn_ipinuse_id;
    END IF;
    RETURN NEW;

ELSIF (TG_OP = 'DELETE') THEN
    IF (OLD.ipn_ipinuse_id is not Null) THEN
	DELETE FROM billservice_ipinuse WHERE id=OLD.ipn_ipinuse_id;
    END IF;

    IF (OLD.vpn_ipinuse_id is not Null) THEN
        DELETE FROM billservice_ipinuse WHERE id=OLD.vpn_ipinuse_id;   
    RETURN OLD;
    END IF;
    
END IF;
RETURN OLD;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.free_unused_account_ip_trg_fn() OWNER TO mikrobill;


CREATE FUNCTION free_unused_card_ip_trg_fn() RETURNS trigger
    AS $$
BEGIN


IF (TG_OP = 'DELETE') and (OLD.ipinuse_id is not Null) THEN
DELETE FROM billservice_ipinuse WHERE id=OLD.ipinuse_id;
RETURN OLD;
END IF;
RETURN OLD;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.free_unused_card_ip_trg_fn() OWNER TO mikrobill;


CREATE FUNCTION free_unused_ip_trg_fn() RETURNS trigger
    AS $$
    BEGIN

        IF    (TG_OP = 'DELETE') THEN
            DELETE FROM billservice_ipinuse WHERE id = OLD.vpn_ipinuse_id;
            DELETE FROM billservice_ipinuse WHERE id = OLD.ipn_ipinuse_id;
            RETURN OLD;

        END IF;
    END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.free_unused_ip_trg_fn() OWNER TO ebs;


CREATE FUNCTION g_int_compress(internal) RETURNS internal
    AS '$libdir/_int', 'g_int_compress'
    LANGUAGE c IMMUTABLE;


ALTER FUNCTION public.g_int_compress(internal) OWNER TO mikrobill;


CREATE FUNCTION g_int_consistent(internal, integer[], integer) RETURNS boolean
    AS '$libdir/_int', 'g_int_consistent'
    LANGUAGE c IMMUTABLE;


ALTER FUNCTION public.g_int_consistent(internal, integer[], integer) OWNER TO mikrobill;


CREATE FUNCTION g_int_decompress(internal) RETURNS internal
    AS '$libdir/_int', 'g_int_decompress'
    LANGUAGE c IMMUTABLE;


ALTER FUNCTION public.g_int_decompress(internal) OWNER TO mikrobill;


CREATE FUNCTION g_int_penalty(internal, internal, internal) RETURNS internal
    AS '$libdir/_int', 'g_int_penalty'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.g_int_penalty(internal, internal, internal) OWNER TO mikrobill;


CREATE FUNCTION g_int_picksplit(internal, internal) RETURNS internal
    AS '$libdir/_int', 'g_int_picksplit'
    LANGUAGE c IMMUTABLE;


ALTER FUNCTION public.g_int_picksplit(internal, internal) OWNER TO mikrobill;


CREATE FUNCTION g_int_same(integer[], integer[], internal) RETURNS internal
    AS '$libdir/_int', 'g_int_same'
    LANGUAGE c IMMUTABLE;


ALTER FUNCTION public.g_int_same(integer[], integer[], internal) OWNER TO mikrobill;


CREATE FUNCTION g_int_union(internal, internal) RETURNS integer[]
    AS '$libdir/_int', 'g_int_union'
    LANGUAGE c IMMUTABLE;


ALTER FUNCTION public.g_int_union(internal, internal) OWNER TO mikrobill;


CREATE FUNCTION g_intbig_compress(internal) RETURNS internal
    AS '$libdir/_int', 'g_intbig_compress'
    LANGUAGE c IMMUTABLE;


ALTER FUNCTION public.g_intbig_compress(internal) OWNER TO mikrobill;


CREATE FUNCTION g_intbig_consistent(internal, internal, integer) RETURNS boolean
    AS '$libdir/_int', 'g_intbig_consistent'
    LANGUAGE c IMMUTABLE;


ALTER FUNCTION public.g_intbig_consistent(internal, internal, integer) OWNER TO mikrobill;


CREATE FUNCTION g_intbig_decompress(internal) RETURNS internal
    AS '$libdir/_int', 'g_intbig_decompress'
    LANGUAGE c IMMUTABLE;


ALTER FUNCTION public.g_intbig_decompress(internal) OWNER TO mikrobill;


CREATE FUNCTION g_intbig_penalty(internal, internal, internal) RETURNS internal
    AS '$libdir/_int', 'g_intbig_penalty'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.g_intbig_penalty(internal, internal, internal) OWNER TO mikrobill;


CREATE FUNCTION g_intbig_picksplit(internal, internal) RETURNS internal
    AS '$libdir/_int', 'g_intbig_picksplit'
    LANGUAGE c IMMUTABLE;


ALTER FUNCTION public.g_intbig_picksplit(internal, internal) OWNER TO mikrobill;


CREATE FUNCTION g_intbig_same(internal, internal, internal) RETURNS internal
    AS '$libdir/_int', 'g_intbig_same'
    LANGUAGE c IMMUTABLE;


ALTER FUNCTION public.g_intbig_same(internal, internal, internal) OWNER TO mikrobill;


CREATE FUNCTION g_intbig_union(internal, internal) RETURNS integer[]
    AS '$libdir/_int', 'g_intbig_union'
    LANGUAGE c IMMUTABLE;


ALTER FUNCTION public.g_intbig_union(internal, internal) OWNER TO mikrobill;


CREATE FUNCTION get_cur_acct(dateat timestamp without time zone) RETURNS integer[]
    AS $$
BEGIN
RETURN ARRAY(SELECT max(id) FROM billservice_accounttarif GROUP BY account_id HAVING account_id IN (SELECT id FROM billservice_account) AND MAX(datetime) <= dateAT);
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.get_cur_acct(dateat timestamp without time zone) OWNER TO postgres;


CREATE FUNCTION get_tarif(acc_id integer) RETURNS integer
    AS $$
declare
xxx int;
begin
SELECT tarif_id INTO xxx
  FROM billservice_accounttarif WHERE account_id=acc_id and datetime<now() ORDER BY datetime DESC LIMIT 1;
RETURN xxx;
end;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.get_tarif(acc_id integer) OWNER TO postgres;


CREATE FUNCTION get_tariff_type(tarif_id integer) RETURNS character varying
    AS $$
declare
ttype character varying(255);
begin
SELECT bsap.access_type INTO ttype
  FROM billservice_accessparameters AS bsap, billservice_tariff AS bstf WHERE (bsap.id=bstf.access_parameters_id) AND (bstf.id=tarif_id) ORDER BY bsap.id LIMIT 1;
IF ttype <> 'IPN' THEN
	ttype := 'VPN';
END IF;
RETURN ttype;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.get_tariff_type(tarif_id integer) OWNER TO postgres;


CREATE FUNCTION ginint4_consistent(internal, smallint, internal) RETURNS internal
    AS '$libdir/_int', 'ginint4_consistent'
    LANGUAGE c IMMUTABLE;


ALTER FUNCTION public.ginint4_consistent(internal, smallint, internal) OWNER TO mikrobill;


CREATE FUNCTION ginint4_queryextract(internal, internal, smallint) RETURNS internal
    AS '$libdir/_int', 'ginint4_queryextract'
    LANGUAGE c IMMUTABLE;


ALTER FUNCTION public.ginint4_queryextract(internal, internal, smallint) OWNER TO mikrobill;


CREATE FUNCTION global_stat_fn(account_id_ integer, bytes_in_ bigint, bytes_out_ bigint, datetime_ timestamp without time zone, nas_id_ integer, classes_ integer[], classbytes_ bigint[]) RETURNS void
    AS $$
DECLARE
    old_classes_ int[];
    old_classbytes_  bigint[][];


    i int;
    ilen int;
    j int;

    nbytes_in  bigint;
    nbytes_out bigint;
    nclass int;
BEGIN
    INSERT INTO billservice_globalstat (account_id, bytes_in, bytes_out, datetime, nas_id, classes, classbytes) VALUES (account_id_, bytes_in_, bytes_out_,datetime_, nas_id_, classes_, classbytes_);
EXCEPTION WHEN unique_violation THEN
    SELECT classes, classbytes INTO old_classes_ ,old_classbytes_ FROM billservice_globalstat WHERE account_id=account_id_ AND datetime=datetime_ FOR UPDATE;
    ilen := icount(classes_);

    FOR i IN 1..ilen LOOP
        nclass := classes_[i];
        nbytes_in  := classbytes_[i][1];
        nbytes_out := classbytes_[i][2];
        j := idx(old_classes_, nclass);
        IF j = 0 THEN
	    old_classes_ := array_append(old_classes_, nclass);
	    old_classbytes_ := array_cat(old_classbytes_, ARRAY[nbytes_in ,nbytes_out]);
	ELSE
	    old_classbytes_[j][1] := old_classbytes_[j][1] + nbytes_in;
	    old_classbytes_[j][2] := old_classbytes_[j][2] + nbytes_out;
	END IF;      
    END LOOP;    
    UPDATE billservice_globalstat SET bytes_in=bytes_in+bytes_in_, bytes_out=bytes_out+bytes_out_, classes=old_classes_, classbytes=old_classbytes_ WHERE account_id=account_id_ AND datetime=datetime_;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.global_stat_fn(account_id_ integer, bytes_in_ bigint, bytes_out_ bigint, datetime_ timestamp without time zone, nas_id_ integer, classes_ integer[], classbytes_ bigint[]) OWNER TO mikrobill;


CREATE FUNCTION gpst_crt_cur_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION gpst_cur_ins (gpstr billservice_groupstat) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO gpst';
                         
    fn_bd_tx2_ text := '(group_id, account_id, bytes, datetime, classes, classbytes, max_class)
                          VALUES 
                         (gpstr.group_id, gpstr.account_id, gpstr.bytes, gpstr.datetime, gpstr.classes, gpstr.classbytes, gpstr.max_class); RETURN; END;';
                          
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';


    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION gpst_cur_datechk(gpst_date timestamp without time zone) RETURNS integer AS ';

    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    gpst_date < d_s_ THEN RETURN -1; ELSIF gpst_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';



    dt_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION gpst_cur_dt() RETURNS date AS ';
    
    onemonth_ text := '1 month';
    query_ text;
    
    prevdate_ date;
    
BEGIN    


    
        query_ :=  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;

        EXECUTE query_;


        query_ :=  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '+ interval ' || quote_literal(onemonth_) ||  ch_fn_bd_tx3_) || fn_tx2_;

        EXECUTE query_;
        
        prevdate_ := gpst_cur_dt();
        
        PERFORM gpst_crt_prev_ins(prevdate_);
        
        query_ := dt_fn_tx1_ || quote_literal(' BEGIN RETURN  DATE ' || quote_literal(datetx_) || '; END; ') || fn_tx2_;
        
        EXECUTE query_;

        
    RETURN;

END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.gpst_crt_cur_ins(datetx date) OWNER TO mikrobill;


CREATE FUNCTION gpst_crt_pdb(datetx date) RETURNS integer
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');
    datetx_e_ text := to_char((datetx + interval '1 month')::date, 'YYYYMM01');

    qt_dtx_ text;
    qt_dtx_e_ text;
    seq_tx1_ text := 'CREATE SEQUENCE gpst#rpdate#_id_seq
                      INCREMENT 1
                      MINVALUE 1
                      MAXVALUE 9223372036854775807
                      START 1
                      CACHE 1;';
    seqname_tx1_ text := 'gpst#rpdate#_id_seq';

    chk_tx1_ text := 'CHECK ( datetime >= DATE #stdtx# AND datetime < DATE #eddtx# )';
    ct_tx1_ text := 'CREATE TABLE gpst#rpdate# (
                     #chk#,
                     CONSTRAINT gpst#rpdate#_id_pkey PRIMARY KEY (id) ) 
                     INHERITS (billservice_groupstat) 
                     WITH (OIDS=FALSE);                     
                     CREATE INDEX gpst#rpdate#_datetime_id ON gpst#rpdate# USING btree (datetime);
                     CREATE INDEX gpst#rpdate#_gr_acc_dt_id ON gpst#rpdate# USING btree (group_id, account_id, datetime);
                     CREATE INDEX gpst#rpdate#_account_id ON gpst#rpdate# USING btree (account_id);
                     CREATE INDEX gpst#rpdate#_group_id ON gpst#rpdate# USING btree (group_id);
                     ';
                     
    at_tx1_ text := 'ALTER TABLE gpst#rpdate# ALTER COLUMN id SET DEFAULT nextval(#qseqname#::regclass);';

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


ALTER FUNCTION public.gpst_crt_pdb(datetx date) OWNER TO mikrobill;


CREATE FUNCTION gpst_crt_prev_ins(datetx date) RETURNS void
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


ALTER FUNCTION public.gpst_crt_prev_ins(datetx date) OWNER TO mikrobill;


CREATE FUNCTION gpst_cur_datechk(gpst_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700201'; d_e_ date := (DATE '19700201'+ interval '1 month')::date; BEGIN IF    gpst_date < d_s_ THEN RETURN -1; ELSIF gpst_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;


ALTER FUNCTION public.gpst_cur_datechk(gpst_date timestamp without time zone) OWNER TO mikrobill;


CREATE FUNCTION gpst_cur_dt() RETURNS date
    AS $$ BEGIN RETURN  DATE '19700201'; END; $$
    LANGUAGE plpgsql;


ALTER FUNCTION public.gpst_cur_dt() OWNER TO mikrobill;

SET default_tablespace = '';

SET default_with_oids = false;


CREATE TABLE billservice_groupstat (
    id integer NOT NULL,
    group_id integer NOT NULL,
    account_id integer NOT NULL,
    bytes integer NOT NULL,
    datetime timestamp without time zone NOT NULL,
    classes integer[],
    classbytes integer[],
    max_class integer
);


ALTER TABLE public.billservice_groupstat OWNER TO mikrobill;


CREATE FUNCTION gpst_cur_ins(gpstr billservice_groupstat) RETURNS void
    AS $$BEGIN 
          RETURN; END;$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.gpst_cur_ins(gpstr billservice_groupstat) OWNER TO mikrobill;


CREATE FUNCTION gpst_del_trg_fn() RETURNS trigger
    AS $$
    BEGIN
        INSERT INTO billservice_groupstat (group_id, account_id, bytes, datetime, classes, classbytes, max_class) VALUES( OLD.group_id, OLD.account_id, OLD.bytes, OLD.datetime, OLD.classes, OLD.classbytes, OLD.max_class);
        RETURN OLD;
    END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.gpst_del_trg_fn() OWNER TO mikrobill;


CREATE FUNCTION gpst_ins_trg_fn() RETURNS trigger
    AS $$
DECLARE
    cur_chk int;
    prev_chk int;
BEGIN
    cur_chk := gpst_cur_datechk(NEW.datetime);

    IF cur_chk = 0 THEN
        PERFORM gpst_cur_ins(NEW);
    ELSIF cur_chk = 1 THEN
        BEGIN
            PERFORM gpst_crt_pdb(NEW.datetime::date);
            PERFORM gpst_crt_cur_ins(NEW.datetime::date);
            EXECUTE gpst_cur_ins(NEW);
        EXCEPTION 
          WHEN duplicate_table THEN
             PERFORM gpst_crt_cur_ins(NEW.datetime::date);
             EXECUTE gpst_cur_ins(NEW);
        END;
        
        
    ELSE 
        prev_chk := gpst_prev_datechk(NEW.datetime);
        IF prev_chk = 0 THEN
            PERFORM gpst_prev_ins(NEW);
        ELSE
            BEGIN 
                PERFORM gpst_inserter(NEW);
            EXCEPTION 
              WHEN undefined_table THEN
                PERFORM gpst_crt_pdb(NEW.datetime::date);
                PERFORM gpst_inserter(NEW);
            END;
        END IF;      
    END IF;
    RETURN NULL;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.gpst_ins_trg_fn() OWNER TO mikrobill;


CREATE FUNCTION gpst_inserter(gpstr billservice_groupstat) RETURNS void
    AS $$
DECLARE
    datetx_ text := to_char(gpstr.datetime::date, 'YYYYMM01');
    insq_   text;
    ttrn_classes_ text; 
    ttrn_classbytes_ text; 
    ttrn_max_class_ int; 
 
BEGIN
    
    IF gpstr.classes IS NULL THEN
       ttrn_classes_ := '{}';
    ELSE
       ttrn_classes_ := quote_literal(gpstr.classes);
    END IF;
    IF gpstr.classbytes IS NULL THEN
       ttrn_classbytes_ := '{}';
    ELSE
       ttrn_classbytes_ := quote_literal(gpstr.classbytes);
    END IF;    
    IF gpstr.max_class IS NULL THEN
       ttrn_max_class_ := 'NULL';
    ELSE
       ttrn_max_class_ := gpstr.max_class;
    END IF;

    
    insq_ := 'INSERT INTO gpst' || datetx_ || ' (group_id, account_id, bytes, datetime, classes, classbytes, max_class) VALUES (' 
    || gpstr.group_id || ',' || gpstr.account_id || ','  || gpstr.bytes || ',' || quote_literal(gpstr.datetime) || ',' ||ttrn_classes_ || ',' || ttrn_classbytes_ || ',' ||  ttrn_max_class_ || ');';
    EXECUTE insq_;
    RETURN;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.gpst_inserter(gpstr billservice_groupstat) OWNER TO mikrobill;


CREATE FUNCTION gpst_prev_datechk(gpst_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700201'; d_e_ date := (DATE '19700201'+ interval '1 month')::date; BEGIN IF    gpst_date < d_s_ THEN RETURN -1; ELSIF gpst_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;


ALTER FUNCTION public.gpst_prev_datechk(gpst_date timestamp without time zone) OWNER TO mikrobill;


CREATE FUNCTION gpst_prev_ins(gpstr billservice_groupstat) RETURNS void
    AS $$BEGIN 
          RETURN; END;$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.gpst_prev_ins(gpstr billservice_groupstat) OWNER TO mikrobill;


CREATE FUNCTION group_type1_fn(group_id_ integer, account_id_ integer, octets_ integer, datetime_ timestamp without time zone, classes_ integer[], classbytes_ integer[], max_class_ integer) RETURNS void
    AS $$
BEGIN
    INSERT INTO billservice_groupstat (group_id, account_id, bytes, datetime, classes, classbytes, max_class) VALUES (group_id_, account_id_, octets_, datetime_, classes_, classbytes_ , max_class_);
EXCEPTION WHEN unique_violation THEN
    UPDATE billservice_groupstat SET bytes=bytes+octets_ WHERE group_id=group_id_ AND account_id=account_id_ AND datetime=datetime_;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.group_type1_fn(group_id_ integer, account_id_ integer, octets_ integer, datetime_ timestamp without time zone, classes_ integer[], classbytes_ integer[], max_class_ integer) OWNER TO mikrobill;


CREATE FUNCTION group_type2_fn(group_id_ integer, account_id_ integer, octets_ integer, datetime_ timestamp without time zone, classes_ integer[], classbytes_ integer[], max_class_ integer) RETURNS void
    AS $$
DECLARE
    old_classes_ int[];
    old_classbytes_  int[];


    i int;
    ilen int;
    j int;
    max_ int;
    maxclass_ int;
    nbytes int;
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
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.group_type2_fn(group_id_ integer, account_id_ integer, octets_ integer, datetime_ timestamp without time zone, classes_ integer[], classbytes_ integer[], max_class_ integer) OWNER TO mikrobill;


CREATE FUNCTION icount(integer[]) RETURNS integer
    AS '$libdir/_int', 'icount'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.icount(integer[]) OWNER TO mikrobill;


CREATE FUNCTION idx(integer[], integer) RETURNS integer
    AS '$libdir/_int', 'idx'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.idx(integer[], integer) OWNER TO mikrobill;


CREATE FUNCTION int_agg_final_array(integer[]) RETURNS integer[]
    AS '$libdir/int_aggregate', 'int_agg_final_array'
    LANGUAGE c;


ALTER FUNCTION public.int_agg_final_array(integer[]) OWNER TO mikrobill;


CREATE FUNCTION int_agg_state(integer[], integer) RETURNS integer[]
    AS '$libdir/int_aggregate', 'int_agg_state'
    LANGUAGE c;


ALTER FUNCTION public.int_agg_state(integer[], integer) OWNER TO mikrobill;


CREATE FUNCTION int_array_enum(integer[]) RETURNS SETOF integer
    AS '$libdir/int_aggregate', 'int_enum'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.int_array_enum(integer[]) OWNER TO mikrobill;


CREATE FUNCTION intarray_del_elem(integer[], integer) RETURNS integer[]
    AS '$libdir/_int', 'intarray_del_elem'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.intarray_del_elem(integer[], integer) OWNER TO mikrobill;


CREATE FUNCTION intarray_push_array(integer[], integer[]) RETURNS integer[]
    AS '$libdir/_int', 'intarray_push_array'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.intarray_push_array(integer[], integer[]) OWNER TO mikrobill;


CREATE FUNCTION intarray_push_elem(integer[], integer) RETURNS integer[]
    AS '$libdir/_int', 'intarray_push_elem'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.intarray_push_elem(integer[], integer) OWNER TO mikrobill;


CREATE FUNCTION intset(integer) RETURNS integer[]
    AS '$libdir/_int', 'intset'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.intset(integer) OWNER TO mikrobill;


CREATE FUNCTION intset_subtract(integer[], integer[]) RETURNS integer[]
    AS '$libdir/_int', 'intset_subtract'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.intset_subtract(integer[], integer[]) OWNER TO mikrobill;


CREATE FUNCTION intset_union_elem(integer[], integer) RETURNS integer[]
    AS '$libdir/_int', 'intset_union_elem'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.intset_union_elem(integer[], integer) OWNER TO mikrobill;


CREATE FUNCTION nfs_crt_cur_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMMDD');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION nfs_cur_ins (nfsr billservice_netflowstream) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO nfs';
                         
    fn_bd_tx2_ text := '(nas_id, account_id, tarif_id, date_start, src_addr, traffic_class_id, direction, traffic_transmit_node_id, dst_addr, octets, src_port, dst_port, protocol, checkouted, for_checkout)
                          VALUES 
                         (nfsr.nas_id, nfsr.account_id, nfsr.tarif_id, nfsr.date_start, nfsr.src_addr, 
                          nfsr.traffic_class_id, nfsr.direction, nfsr.traffic_transmit_node_id, nfsr.dst_addr, nfsr.octets, nfsr.src_port, 
                          nfsr.dst_port, nfsr.protocol, nfsr.checkouted, nfsr.for_checkout); RETURN; END;';
                          
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';


    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION nfs_cur_datechk(nfs_date timestamp without time zone) RETURNS integer AS ';

    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    nfs_date < d_s_ THEN RETURN -1; ELSIF nfs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';



	dt_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION nfs_cur_dt() RETURNS date AS ';
	
    oneday_ text := '1 day';
    query_ text;
    
    prevdate_ date;
    
BEGIN	


	
        query_ :=  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;

        EXECUTE query_;


        query_ :=  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '+ interval ' || quote_literal(oneday_) ||  ch_fn_bd_tx3_) || fn_tx2_;

        EXECUTE query_;
        
        prevdate_ := nfs_cur_dt();
        
        PERFORM nfs_crt_prev_ins(prevdate_);
        
        query_ := dt_fn_tx1_ || quote_literal(' BEGIN RETURN  DATE ' || quote_literal(datetx_) || '; END; ') || fn_tx2_;
        
        EXECUTE query_;

        
	RETURN;

END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.nfs_crt_cur_ins(datetx date) OWNER TO mikrobill;


CREATE FUNCTION nfs_crt_pdb(datetx date) RETURNS integer
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMMDD');
    datetx_e_ text := to_char((datetx + interval '1 day')::date, 'YYYYMMDD');

    qt_dtx_ text;
    qt_dtx_e_ text;
    seq_tx1_ text := 'CREATE SEQUENCE nfs#rpdate#_id_seq
                      INCREMENT 1
                      MINVALUE 1
                      MAXVALUE 9223372036854775807
                      START 1
                      CACHE 1;';
    seqname_tx1_ text := 'nfs#rpdate#_id_seq';

    chk_tx1_ text := 'CHECK ( date_start >= DATE #stdtx# AND date_start < DATE #eddtx# )';
    ct_tx1_ text := 'CREATE TABLE nfs#rpdate# (
                     #chk#,
                     CONSTRAINT nfs#rpdate#_id_pkey PRIMARY KEY (id) ) 
                     INHERITS (billservice_netflowstream) 
                     WITH (OIDS=FALSE);                     
                     CREATE INDEX nfs#rpdate#_date_start_id ON nfs#rpdate# USING btree (date_start);
                     ';
                     
    at_tx1_ text := 'ALTER TABLE nfs#rpdate# ALTER COLUMN id SET DEFAULT nextval(#qseqname#::regclass);';

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


ALTER FUNCTION public.nfs_crt_pdb(datetx date) OWNER TO ebs;


CREATE FUNCTION nfs_crt_prev_ins(datetx date) RETURNS void
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
    
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    nfs_date < d_s_ THEN RETURN -1; ELSIF nfs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';

    ch_fn_tx2_ text := ' LANGUAGE plpgsql VOLATILE COST 100;';

    qts_ text := 'CHK % % %';   
    
    oneday_ text := interval '1 day';
    query_ text;
   
BEGIN    


        EXECUTE  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;


        
        
        query_ :=  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '+ interval ' || quote_literal(oneday_) ||  ch_fn_bd_tx3_) || fn_tx2_;
        
        EXECUTE query_;
        
    RETURN;

END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.nfs_crt_prev_ins(datetx date) OWNER TO mikrobill;


CREATE FUNCTION nfs_cur_datechk(nfs_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700102'; d_e_ date := (DATE '19700102'+ interval '1 day')::date; BEGIN IF    nfs_date < d_s_ THEN RETURN -1; ELSIF nfs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;


ALTER FUNCTION public.nfs_cur_datechk(nfs_date timestamp without time zone) OWNER TO mikrobill;


CREATE FUNCTION nfs_cur_dt() RETURNS date
    AS $$ BEGIN RETURN  DATE '19700102'; END; $$
    LANGUAGE plpgsql;


ALTER FUNCTION public.nfs_cur_dt() OWNER TO mikrobill;


CREATE TABLE billservice_netflowstream (
    id integer NOT NULL,
    nas_id integer,
    account_id integer NOT NULL,
    tarif_id integer NOT NULL,
    date_start timestamp without time zone DEFAULT now(),
    src_addr inet NOT NULL,
    traffic_class_id integer[],
    direction character varying(32) NOT NULL,
    traffic_transmit_node_id integer,
    dst_addr inet NOT NULL,
    octets bigint NOT NULL,
    src_port integer NOT NULL,
    dst_port integer NOT NULL,
    protocol integer NOT NULL,
    checkouted boolean DEFAULT false,
    for_checkout boolean DEFAULT false
);


ALTER TABLE public.billservice_netflowstream OWNER TO mikrobill;


CREATE FUNCTION nfs_cur_ins(nfsr billservice_netflowstream) RETURNS void
    AS $$BEGIN 
       RETURN; END;$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.nfs_cur_ins(nfsr billservice_netflowstream) OWNER TO mikrobill;


CREATE FUNCTION nfs_ins_trg_fn() RETURNS trigger
    AS $$
DECLARE
    cur_chk int;
    prev_chk int;
BEGIN
    cur_chk := nfs_cur_datechk(NEW.date_start);

    IF cur_chk = 0 THEN
        PERFORM nfs_cur_ins(NEW);
    ELSIF cur_chk = 1 THEN
        BEGIN
            PERFORM nfs_crt_pdb(NEW.date_start::date);
            PERFORM nfs_crt_cur_ins(NEW.date_start::date);
            EXECUTE nfs_cur_ins(NEW);
        EXCEPTION 
          WHEN duplicate_table THEN
             PERFORM nfs_crt_cur_ins(NEW.date_start::date);
             EXECUTE nfs_cur_ins(NEW);
        END;
        
        
    ELSE 
        prev_chk := nfs_prev_datechk(NEW.date_start);
        IF prev_chk = 0 THEN
            PERFORM nfs_prev_ins(NEW);
        ELSE
            BEGIN 
                PERFORM nfs_inserter(NEW);
            EXCEPTION 
              WHEN undefined_table THEN
                PERFORM nfs_crt_pdb(NEW.date_start::date);
                PERFORM nfs_inserter(NEW);
            END;
        END IF;      
    END IF;
    RETURN NULL;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.nfs_ins_trg_fn() OWNER TO mikrobill;


CREATE FUNCTION nfs_inserter(nfsr billservice_netflowstream) RETURNS void
    AS $$
DECLARE
    datetx_ text := to_char(nfsr.date_start::date, 'YYYYMMDD');
    insq_   text;

    ttrn_id_ text;

    
BEGIN
    
    IF nfsr.traffic_transmit_node_id IS NULL THEN
       ttrn_id_ := 'NULL';
    ELSE
       ttrn_id_ := nfsr.traffic_transmit_node_id::text;
    END IF;
    insq_ := 'INSERT INTO nfs' || datetx_ || ' (nas_id, account_id, tarif_id, date_start, src_addr, traffic_class_id, direction, traffic_transmit_node_id, dst_addr, octets, src_port, dst_port, protocol, checkouted, for_checkout) VALUES (' 
    || nfsr.nas_id || ',' || nfsr.account_id || ','  || nfsr.tarif_id || ','  || quote_literal(nfsr.date_start) || ','  || quote_literal(nfsr.src_addr) || ','  || quote_literal(nfsr.traffic_class_id) || ','  || quote_literal(nfsr.direction) || ','  || ttrn_id_ || ','  || quote_literal(nfsr.dst_addr) || ','  || nfsr.octets || ','  || nfsr.src_port || ','  || nfsr.dst_port || ','  || nfsr.protocol || ','  || nfsr.checkouted || ','  || nfsr.for_checkout || ');';
    EXECUTE insq_;
    RETURN;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.nfs_inserter(nfsr billservice_netflowstream) OWNER TO mikrobill;


CREATE FUNCTION nfs_prev_datechk(nfs_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700101'; d_e_ date := (DATE '19700101'+ interval '1 day')::date; BEGIN IF    nfs_date < d_s_ THEN RETURN -1; ELSIF nfs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;


ALTER FUNCTION public.nfs_prev_datechk(nfs_date timestamp without time zone) OWNER TO mikrobill;


CREATE FUNCTION nfs_prev_ins(nfsr billservice_netflowstream) RETURNS void
    AS $$BEGIN 
      RETURN; END;$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.nfs_prev_ins(nfsr billservice_netflowstream) OWNER TO mikrobill;


CREATE TABLE billservice_tariff (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text DEFAULT ''::text,
    access_parameters_id integer NOT NULL,
    time_access_service_id integer,
    traffic_transmit_service_id integer,
    cost double precision DEFAULT 0,
    reset_tarif_cost boolean DEFAULT false,
    settlement_period_id integer,
    ps_null_ballance_checkout boolean DEFAULT false,
    active boolean DEFAULT false,
    deleted boolean DEFAULT false,
    allow_express_pay boolean DEFAULT true
);


ALTER TABLE public.billservice_tariff OWNER TO mikrobill;


CREATE FUNCTION on_tariff_delete_fun(oldrow billservice_tariff) RETURNS record
    AS $$
        BEGIN
        IF oldrow.traffic_transmit_service_id NOTNULL THEN
            UPDATE billservice_tariff SET traffic_transmit_service_id=NULL WHERE id=oldrow.id;
            DELETE FROM billservice_traffictransmitservice WHERE id=oldrow.traffic_transmit_service_id;
        END IF;

        IF oldrow.time_access_service_id NOTNULL THEN
	    UPDATE billservice_tariff SET time_access_service_id=NULL WHERE id=oldrow.id;
            DELETE FROM billservice_timeaccessservice WHERE id=oldrow.time_access_service_id;
        END IF;

        IF oldrow.access_parameters_id NOTNULL THEN
            DELETE FROM billservice_accessparameters WHERE id=oldrow.access_parameters_id;
        END IF;
               RETURN oldrow;               
        END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.on_tariff_delete_fun(oldrow billservice_tariff) OWNER TO mikrobill;


CREATE FUNCTION psh_crt_cur_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION psh_cur_ins (pshr billservice_periodicalservicehistory) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO psh';
                         
    fn_bd_tx2_ text := '(service_id, transaction_id, datetime, accounttarif_id)
                          VALUES 
                         (pshr.service_id, pshr.transaction_id, pshr.datetime, pshr.accounttarif_id); RETURN; END;';
                          
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


ALTER FUNCTION public.psh_crt_cur_ins(datetx date) OWNER TO mikrobill;


CREATE FUNCTION psh_crt_pdb(datetx date) RETURNS integer
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
                     CREATE INDEX psh#rpdate#_transaction_id ON psh#rpdate# USING btree (transaction_id);
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


ALTER FUNCTION public.psh_crt_pdb(datetx date) OWNER TO mikrobill;


CREATE FUNCTION psh_crt_prev_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION psh_prev_ins (pshr billservice_periodicalservicehistory) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO psh';
                         
    fn_bd_tx2_ text := '(service_id, transaction_id, datetime, accounttarif_id)
                          VALUES 
                         (pshr.service_id, pshr.transaction_id, pshr.datetime, pshr.accounttarif_id); RETURN; END;';
                          
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


ALTER FUNCTION public.psh_crt_prev_ins(datetx date) OWNER TO mikrobill;


CREATE FUNCTION psh_cur_datechk(psh_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700201'; d_e_ date := (DATE '19700101'+ interval '1 month')::date; BEGIN IF    psh_date < d_s_ THEN RETURN -1; ELSIF psh_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;


ALTER FUNCTION public.psh_cur_datechk(psh_date timestamp without time zone) OWNER TO mikrobill;


CREATE FUNCTION psh_cur_dt() RETURNS date
    AS $$ BEGIN RETURN  DATE '19700201'; END; $$
    LANGUAGE plpgsql;


ALTER FUNCTION public.psh_cur_dt() OWNER TO mikrobill;


CREATE TABLE billservice_periodicalservicehistory (
    id integer NOT NULL,
    service_id integer NOT NULL,
    transaction_id integer,
    datetime timestamp without time zone DEFAULT now(),
    accounttarif_id integer
);


ALTER TABLE public.billservice_periodicalservicehistory OWNER TO mikrobill;


CREATE FUNCTION psh_cur_ins(pshr billservice_periodicalservicehistory) RETURNS void
    AS $$BEGIN 
        RETURN; END;$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.psh_cur_ins(pshr billservice_periodicalservicehistory) OWNER TO mikrobill;


CREATE FUNCTION psh_del_trg_fn() RETURNS trigger
    AS $$
    BEGIN
        INSERT INTO billservice_periodicalservicehistory (service_id, transaction_id, datetime, accounttarif_id) VALUES( OLD.service_id, OLD.transaction_id, OLD.datetime, OLD.accounttarif_id);
        RETURN OLD;
    END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.psh_del_trg_fn() OWNER TO mikrobill;


CREATE FUNCTION psh_ins_trg_fn() RETURNS trigger
    AS $$
DECLARE
    cur_chk int;
    prev_chk int;
BEGIN
    cur_chk := psh_cur_datechk(NEW.datetime);

    IF cur_chk = 0 THEN
        PERFORM psh_cur_ins(NEW);
    ELSIF cur_chk = 1 THEN
        BEGIN
            PERFORM psh_crt_pdb(NEW.datetime::date);
            PERFORM psh_crt_cur_ins(NEW.datetime::date);
            EXECUTE psh_cur_ins(NEW);
        EXCEPTION 
          WHEN duplicate_table THEN
             PERFORM psh_crt_cur_ins(NEW.datetime::date);
             EXECUTE psh_cur_ins(NEW);
        END;
        
        
    ELSE 
        prev_chk := psh_prev_datechk(NEW.datetime);
        IF prev_chk = 0 THEN
            PERFORM psh_prev_ins(NEW);
        ELSE
            BEGIN 
                PERFORM psh_inserter(NEW);
            EXCEPTION 
              WHEN undefined_table THEN
                PERFORM psh_crt_pdb(NEW.datetime::date);
                PERFORM psh_inserter(NEW);
            END;
        END IF;      
    END IF;
    RETURN NULL;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.psh_ins_trg_fn() OWNER TO mikrobill;


CREATE FUNCTION psh_inserter(pshr billservice_periodicalservicehistory) RETURNS void
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
    insq_ := 'INSERT INTO psh' || datetx_ || ' (service_id, transaction_id, datetime, accounttarif_id) VALUES (' 
    || pshr.service_id || ',' || pshr.transaction_id || ','  || quote_literal(pshr.datetime) || ','  || ttrn_actfid_ || ');';
    EXECUTE insq_;
    RETURN;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.psh_inserter(pshr billservice_periodicalservicehistory) OWNER TO mikrobill;


CREATE FUNCTION psh_prev_datechk(psh_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700101'; d_e_ date := (DATE '19700101'+ interval '1 month')::date; BEGIN IF    psh_date < d_s_ THEN RETURN -1; ELSIF psh_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;


ALTER FUNCTION public.psh_prev_datechk(psh_date timestamp without time zone) OWNER TO mikrobill;


CREATE FUNCTION psh_prev_ins(pshr billservice_periodicalservicehistory) RETURNS void
    AS $$BEGIN 
         RETURN; END;$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.psh_prev_ins(pshr billservice_periodicalservicehistory) OWNER TO mikrobill;


CREATE FUNCTION querytree(query_int) RETURNS text
    AS '$libdir/_int', 'querytree'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.querytree(query_int) OWNER TO mikrobill;


CREATE FUNCTION rboolop(query_int, integer[]) RETURNS boolean
    AS '$libdir/_int', 'rboolop'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.rboolop(query_int, integer[]) OWNER TO mikrobill;


COMMENT ON FUNCTION rboolop(query_int, integer[]) IS 'boolean operation with array';



CREATE FUNCTION rsss_crt_cur_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION rsss_cur_ins (rsssr radius_session) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO rsss';
                         
    fn_bd_tx2_ text := '(account_id, sessionid, interrim_update, date_start, date_end, caller_id, called_id, nas_id, session_time, framed_protocol, bytes_in, bytes_out, checkouted_by_time, checkouted_by_trafic, disconnect_status, framed_ip_address)
                          VALUES 
                         (rsssr.account_id, rsssr.sessionid, rsssr.interrim_update, rsssr.date_start, rsssr.date_end, rsssr.caller_id, rsssr.called_id, rsssr.nas_id, rsssr.session_time, rsssr.framed_protocol, rsssr.bytes_in, rsssr.bytes_out, rsssr.checkouted_by_time, rsssr.checkouted_by_trafic, rsssr.disconnect_status, rsssr.framed_ip_address); RETURN; END;';
                          
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';


    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION rsss_cur_datechk(rsss_date timestamp without time zone) RETURNS integer AS ';

    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    rsss_date < d_s_ THEN RETURN -1; ELSIF rsss_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';



    dt_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION rsss_cur_dt() RETURNS date AS ';
    
    onemonth_ text := '1 month';
    query_ text;
    
    prevdate_ date;
    
BEGIN    


    
        query_ :=  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;

        EXECUTE query_;


        query_ :=  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '+ interval ' || quote_literal(onemonth_) ||  ch_fn_bd_tx3_) || fn_tx2_;

        EXECUTE query_;
        
        prevdate_ := rsss_cur_dt();
        
        PERFORM rsss_crt_prev_ins(prevdate_);
        
        query_ := dt_fn_tx1_ || quote_literal(' BEGIN RETURN  DATE ' || quote_literal(datetx_) || '; END; ') || fn_tx2_;
        
        EXECUTE query_;

        
    RETURN;

END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.rsss_crt_cur_ins(datetx date) OWNER TO mikrobill;


CREATE FUNCTION rsss_crt_pdb(datetx date) RETURNS integer
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');
    datetx_e_ text := to_char((datetx + interval '1 month')::date, 'YYYYMM01');

    qt_dtx_ text;
    qt_dtx_e_ text;
    seq_tx1_ text := 'CREATE SEQUENCE rsss#rpdate#_id_seq
                      INCREMENT 1
                      MINVALUE 1
                      MAXVALUE 9223372036854775807
                      START 1
                      CACHE 1;';
    seqname_tx1_ text := 'rsss#rpdate#_id_seq';

    chk_tx1_ text := 'CHECK ( interrim_update >= DATE #stdtx# AND interrim_update < DATE #eddtx# )';
    ct_tx1_ text := 'CREATE TABLE rsss#rpdate# (
                     #chk#,
                     CONSTRAINT rsss#rpdate#_id_pkey PRIMARY KEY (id) ) 
                     INHERITS (radius_session) 
                     WITH (OIDS=FALSE);                     
                     CREATE INDEX rsss#rpdate#_interrim_update_id ON rsss#rpdate# USING btree (interrim_update);
                     CREATE INDEX rsss#rpdate#_account_id ON rsss#rpdate# USING btree (account_id);
                     ';
                     
    at_tx1_ text := 'ALTER TABLE rsss#rpdate# ALTER COLUMN id SET DEFAULT nextval(#qseqname#::regclass);';

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


ALTER FUNCTION public.rsss_crt_pdb(datetx date) OWNER TO mikrobill;


CREATE FUNCTION rsss_crt_prev_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION rsss_prev_ins (rsssr radius_session) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO rsss';
                         
    fn_bd_tx2_ text := '(account_id, sessionid, interrim_update, date_start, date_end, caller_id, called_id, nas_id, session_time, framed_protocol, bytes_in, bytes_out, checkouted_by_time, checkouted_by_trafic, disconnect_status, framed_ip_address)
                          VALUES 
                         (rsssr.account_id, rsssr.sessionid, rsssr.interrim_update, rsssr.date_start, rsssr.date_end, rsssr.caller_id, rsssr.called_id, rsssr.nas_id, rsssr.session_time, rsssr.framed_protocol, rsssr.bytes_in, rsssr.bytes_out, rsssr.checkouted_by_time, rsssr.checkouted_by_trafic, rsssr.disconnect_status, rsssr.framed_ip_address); RETURN; END;';
                          
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';


    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION rsss_prev_datechk(rsss_date timestamp without time zone) RETURNS integer AS ';

    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    rsss_date < d_s_ THEN RETURN -1; ELSIF rsss_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';

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


ALTER FUNCTION public.rsss_crt_prev_ins(datetx date) OWNER TO mikrobill;


CREATE FUNCTION rsss_cur_datechk(rsss_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700201'; d_e_ date := (DATE '19700201'+ interval '1 month')::date; BEGIN IF    rsss_date < d_s_ THEN RETURN -1; ELSIF rsss_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;


ALTER FUNCTION public.rsss_cur_datechk(rsss_date timestamp without time zone) OWNER TO mikrobill;


CREATE FUNCTION rsss_cur_dt() RETURNS date
    AS $$ BEGIN RETURN  DATE '19700201'; END; $$
    LANGUAGE plpgsql;


ALTER FUNCTION public.rsss_cur_dt() OWNER TO mikrobill;


CREATE TABLE radius_session (
    id integer NOT NULL,
    account_id integer NOT NULL,
    sessionid character varying(32) DEFAULT ''::character varying,
    interrim_update timestamp without time zone DEFAULT now(),
    date_start timestamp without time zone,
    date_end timestamp without time zone,
    caller_id character varying(255) DEFAULT ''::character varying,
    called_id character varying(255) DEFAULT ''::character varying,
    nas_id character varying(255) NOT NULL,
    session_time integer DEFAULT 0,
    framed_protocol character varying(32) NOT NULL,
    bytes_in integer DEFAULT 0,
    bytes_out integer DEFAULT 0,
    checkouted_by_time boolean DEFAULT false,
    checkouted_by_trafic boolean DEFAULT false,
    disconnect_status character varying(32),
    framed_ip_address character varying(255)
);


ALTER TABLE public.radius_session OWNER TO mikrobill;


CREATE FUNCTION rsss_cur_ins(rsssr radius_session) RETURNS void
    AS $$BEGIN 
       RETURN; END;$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.rsss_cur_ins(rsssr radius_session) OWNER TO mikrobill;


CREATE FUNCTION rsss_del_trg_fn() RETURNS trigger
    AS $$
    BEGIN
        INSERT INTO radius_session (account_id, sessionid, interrim_update, date_start, date_end, caller_id, called_id, nas_id, session_time, framed_protocol, bytes_in, bytes_out, checkouted_by_time, checkouted_by_trafic, disconnect_status, framed_ip_address) VALUES( OLD.account_id, OLD.sessionid, OLD.interrim_update, OLD.date_start, OLD.date_end, OLD.caller_id, OLD.called_id, OLD.nas_id, OLD.session_time, OLD.framed_protocol, OLD.bytes_in, OLD.bytes_out, OLD.checkouted_by_time, OLD.checkouted_by_trafic, OLD.disconnect_status, OLD.framed_ip_address);
        RETURN OLD;
    END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.rsss_del_trg_fn() OWNER TO mikrobill;


CREATE FUNCTION rsss_ins_trg_fn() RETURNS trigger
    AS $$
DECLARE
    cur_chk int;
    prev_chk int;
BEGIN
    cur_chk := rsss_cur_datechk(NEW.interrim_update);

    IF cur_chk = 0 THEN
        PERFORM rsss_cur_ins(NEW);
    ELSIF cur_chk = 1 THEN
        BEGIN
            PERFORM rsss_crt_pdb(NEW.interrim_update::date);
            PERFORM rsss_crt_cur_ins(NEW.interrim_update::date);
            EXECUTE rsss_cur_ins(NEW);
        EXCEPTION 
          WHEN duplicate_table THEN
             PERFORM rsss_crt_cur_ins(NEW.interrim_update::date);
             EXECUTE rsss_cur_ins(NEW);
        END;
        
        
    ELSE 
        prev_chk := rsss_prev_datechk(NEW.interrim_update);
        IF prev_chk = 0 THEN
            PERFORM rsss_prev_ins(NEW);
        ELSE
            BEGIN 
                PERFORM rsss_inserter(NEW);
            EXCEPTION 
              WHEN undefined_table THEN
                PERFORM rsss_crt_pdb(NEW.interrim_update::date);
                PERFORM rsss_inserter(NEW);
            END;
        END IF;      
    END IF;
    RETURN NULL;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.rsss_ins_trg_fn() OWNER TO mikrobill;


CREATE FUNCTION rsss_inserter(rsssr radius_session) RETURNS void
    AS $$
DECLARE
    datetx_ text := to_char(rsssr.interrim_update::date, 'YYYYMM01');
    insq_   text;

  
    ttrn_sessionid_ text; 
    ttrn_interrim_update_ text; 
    ttrn_date_start_ text; 
    ttrn_date_end_ text; 
    ttrn_caller_id_ text; 
    ttrn_called_id_ text; 
    ttrn_session_time_ int;
    ttrn_bytes_in_ int; 
    ttrn_bytes_out_ int; 
    ttrn_checkouted_by_time_ boolean; 
    ttrn_checkouted_by_trafic_ boolean; 
    ttrn_disconnect_status_ text; 
    ttrn_framed_ip_address_ text;  
BEGIN
    
    IF rsssr.sessionid IS NULL THEN
       ttrn_sessionid_ := quote_literal('');
    ELSE
       ttrn_sessionid_ := quote_literal(rsssr.sessionid);
    END IF;
    IF rsssr.interrim_update IS NULL THEN
       ttrn_interrim_update_ := quote_literal(now()::timestamp without time zone);
    ELSE
       ttrn_interrim_update_ := quote_literal(rsssr.interrim_update);
    END IF;
    IF rsssr.date_start IS NULL THEN
       ttrn_date_start_ := 'NULL';
    ELSE
       ttrn_date_start_ := quote_literal(rsssr.date_start);
    END IF;
    IF rsssr.date_end IS NULL THEN
       ttrn_date_end_ := 'NULL';
    ELSE
       ttrn_date_end_ := quote_literal(rsssr.date_end);
    END IF;
    IF rsssr.caller_id IS NULL THEN
       ttrn_caller_id_ := quote_literal('');
    ELSE
       ttrn_caller_id_ := quote_literal(rsssr.caller_id);
    END IF;
    IF rsssr.called_id IS NULL THEN
       ttrn_called_id_ := quote_literal('');
    ELSE
       ttrn_called_id_ := quote_literal(rsssr.called_id);
    END IF;
    IF rsssr.session_time IS NULL THEN
       ttrn_session_time_ := 0;
    ELSE
       ttrn_session_time_ := rsssr.session_time;
    END IF;
    IF rsssr.bytes_in IS NULL THEN
       ttrn_bytes_in_ := 0;
    ELSE
       ttrn_bytes_in_ := rsssr.bytes_in;
    END IF;
    IF rsssr.bytes_out IS NULL THEN
       ttrn_bytes_out_ := 0;
    ELSE
       ttrn_bytes_out_ := rsssr.bytes_out;
    END IF;
    IF rsssr.checkouted_by_time IS NULL THEN
       ttrn_checkouted_by_time_ := FALSE;
    ELSE
       ttrn_checkouted_by_time_ := rsssr.checkouted_by_time;
    END IF;
    IF rsssr.checkouted_by_trafic IS NULL THEN
       ttrn_checkouted_by_trafic_ := FALSE;
    ELSE
       ttrn_checkouted_by_trafic_ := rsssr.checkouted_by_trafic;
    END IF;    
    IF rsssr.disconnect_status IS NULL THEN
       ttrn_disconnect_status_ := 'NULL';
    ELSE
       ttrn_disconnect_status_ := quote_literal(rsssr.disconnect_status);
    END IF;
    IF rsssr.framed_ip_address IS NULL THEN
       ttrn_framed_ip_address_ := 'NULL';
    ELSE
       ttrn_framed_ip_address_ := quote_literal(rsssr.framed_ip_address);
    END IF;

    insq_ := 'INSERT INTO rsss' || datetx_ || ' (account_id, sessionid, interrim_update, date_start, date_end, caller_id, called_id, nas_id, session_time, framed_protocol, bytes_in, bytes_out, checkouted_by_time, checkouted_by_trafic, disconnect_status, framed_ip_address) VALUES ('  || rsssr.account_id || ','  || ttrn_sessionid_ || ',' || ttrn_interrim_update_ || ',' || ttrn_date_start_ || ',' || ttrn_date_end_  || ',' ||  ttrn_caller_id_ || ','  || ttrn_called_id_ || ',' || quote_literal(rsssr.nas_id) || ',' || ttrn_session_time_ || ',' || quote_literal(rsssr.framed_protocol) || ',' || ttrn_bytes_in_ || ',' || ttrn_bytes_out_ || ',' || ttrn_checkouted_by_time_ || ',' || ttrn_checkouted_by_trafic_ || ',' || ttrn_disconnect_status_ || ',' || ttrn_framed_ip_address_ || ');';
    EXECUTE insq_;
    RETURN;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.rsss_inserter(rsssr radius_session) OWNER TO mikrobill;


CREATE FUNCTION rsss_prev_datechk(rsss_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700201'; d_e_ date := (DATE '19700201'+ interval '1 month')::date; BEGIN IF    rsss_date < d_s_ THEN RETURN -1; ELSIF rsss_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;


ALTER FUNCTION public.rsss_prev_datechk(rsss_date timestamp without time zone) OWNER TO mikrobill;


CREATE FUNCTION rsss_prev_ins(rsssr radius_session) RETURNS void
    AS $$BEGIN 
        RETURN; END;$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.rsss_prev_ins(rsssr radius_session) OWNER TO mikrobill;


CREATE FUNCTION sort(integer[], text) RETURNS integer[]
    AS '$libdir/_int', 'sort'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.sort(integer[], text) OWNER TO mikrobill;


CREATE FUNCTION sort(integer[]) RETURNS integer[]
    AS '$libdir/_int', 'sort'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.sort(integer[]) OWNER TO mikrobill;


CREATE FUNCTION sort_asc(integer[]) RETURNS integer[]
    AS '$libdir/_int', 'sort_asc'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.sort_asc(integer[]) OWNER TO mikrobill;


CREATE FUNCTION sort_desc(integer[]) RETURNS integer[]
    AS '$libdir/_int', 'sort_desc'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.sort_desc(integer[]) OWNER TO mikrobill;


CREATE FUNCTION subarray(integer[], integer, integer) RETURNS integer[]
    AS '$libdir/_int', 'subarray'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.subarray(integer[], integer, integer) OWNER TO mikrobill;


CREATE FUNCTION subarray(integer[], integer) RETURNS integer[]
    AS '$libdir/_int', 'subarray'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.subarray(integer[], integer) OWNER TO mikrobill;


CREATE FUNCTION transaction_fn(bill_ character varying, account_id_ integer, type_id_ character varying, approved_ boolean, tarif_id_ integer, summ_ double precision, description_ text, created_ timestamp without time zone, ps_id_ integer, acctf_id_ integer, ps_condition_type_ integer) RETURNS void
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


ALTER FUNCTION public.transaction_fn(bill_ character varying, account_id_ integer, type_id_ character varying, approved_ boolean, tarif_id_ integer, summ_ double precision, description_ text, created_ timestamp without time zone, ps_id_ integer, acctf_id_ integer, ps_condition_type_ integer) OWNER TO mikrobill;


CREATE FUNCTION transaction_tarif(bill_ character varying, type_id_ character varying, approved_ boolean, tarif_id_ integer, summ_ double precision, description_ text, created_ timestamp without time zone, acct_datetime_ timestamp without time zone) RETURNS void
    AS $$
DECLARE
    acc_id_ int;
BEGIN
    FOR acc_id_ IN SELECT account_id FROM billservice_accounttarif WHERE datetime<acct_datetime_ AND tarif_id=tarif_id_ LOOP
	INSERT INTO billservice_transaction (bill, account_id,  type_id, approved,  tarif_id, summ, description, created) VALUES (bill_ , acc_id_, type_id_, approved_, tarif_id_, summ_, description_, created_);
    END LOOP;  
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.transaction_tarif(bill_ character varying, type_id_ character varying, approved_ boolean, tarif_id_ integer, summ_ double precision, description_ text, created_ timestamp without time zone, acct_datetime_ timestamp without time zone) OWNER TO mikrobill;


CREATE FUNCTION unblock_balance(account_id integer) RETURNS void
    AS $$
BEGIN
	UPDATE billservice_account SET balance_blocked=FALSE WHERE id=account_id;
RETURN;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.unblock_balance(account_id integer) OWNER TO postgres;


CREATE FUNCTION uniq(integer[]) RETURNS integer[]
    AS '$libdir/_int', 'uniq'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.uniq(integer[]) OWNER TO mikrobill;


CREATE AGGREGATE int_array_aggregate(integer) (
    SFUNC = int_agg_state,
    STYPE = integer[],
    FINALFUNC = int_agg_final_array
);


ALTER AGGREGATE public.int_array_aggregate(integer) OWNER TO mikrobill;


CREATE OPERATOR # (
    PROCEDURE = icount,
    RIGHTARG = integer[]
);


ALTER OPERATOR public.# (NONE, integer[]) OWNER TO mikrobill;


CREATE OPERATOR # (
    PROCEDURE = idx,
    LEFTARG = integer[],
    RIGHTARG = integer
);


ALTER OPERATOR public.# (integer[], integer) OWNER TO mikrobill;


CREATE OPERATOR & (
    PROCEDURE = _int_inter,
    LEFTARG = integer[],
    RIGHTARG = integer[],
    COMMUTATOR = &
);


ALTER OPERATOR public.& (integer[], integer[]) OWNER TO mikrobill;


CREATE OPERATOR && (
    PROCEDURE = _int_overlap,
    LEFTARG = integer[],
    RIGHTARG = integer[],
    COMMUTATOR = &&,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.&& (integer[], integer[]) OWNER TO mikrobill;


CREATE OPERATOR + (
    PROCEDURE = intarray_push_elem,
    LEFTARG = integer[],
    RIGHTARG = integer
);


ALTER OPERATOR public.+ (integer[], integer) OWNER TO mikrobill;


CREATE OPERATOR + (
    PROCEDURE = intarray_push_array,
    LEFTARG = integer[],
    RIGHTARG = integer[],
    COMMUTATOR = +
);


ALTER OPERATOR public.+ (integer[], integer[]) OWNER TO mikrobill;


CREATE OPERATOR - (
    PROCEDURE = intarray_del_elem,
    LEFTARG = integer[],
    RIGHTARG = integer
);


ALTER OPERATOR public.- (integer[], integer) OWNER TO mikrobill;


CREATE OPERATOR - (
    PROCEDURE = intset_subtract,
    LEFTARG = integer[],
    RIGHTARG = integer[]
);


ALTER OPERATOR public.- (integer[], integer[]) OWNER TO mikrobill;


CREATE OPERATOR <@ (
    PROCEDURE = _int_contained,
    LEFTARG = integer[],
    RIGHTARG = integer[],
    COMMUTATOR = @>,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.<@ (integer[], integer[]) OWNER TO mikrobill;


CREATE OPERATOR @ (
    PROCEDURE = _int_contains,
    LEFTARG = integer[],
    RIGHTARG = integer[],
    COMMUTATOR = ~,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.@ (integer[], integer[]) OWNER TO mikrobill;


CREATE OPERATOR @> (
    PROCEDURE = _int_contains,
    LEFTARG = integer[],
    RIGHTARG = integer[],
    COMMUTATOR = <@,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.@> (integer[], integer[]) OWNER TO mikrobill;


CREATE OPERATOR @@ (
    PROCEDURE = boolop,
    LEFTARG = integer[],
    RIGHTARG = query_int,
    COMMUTATOR = ~~,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.@@ (integer[], query_int) OWNER TO mikrobill;


CREATE OPERATOR | (
    PROCEDURE = intset_union_elem,
    LEFTARG = integer[],
    RIGHTARG = integer
);


ALTER OPERATOR public.| (integer[], integer) OWNER TO mikrobill;


CREATE OPERATOR | (
    PROCEDURE = _int_union,
    LEFTARG = integer[],
    RIGHTARG = integer[],
    COMMUTATOR = |
);


ALTER OPERATOR public.| (integer[], integer[]) OWNER TO mikrobill;


CREATE OPERATOR ~ (
    PROCEDURE = _int_contained,
    LEFTARG = integer[],
    RIGHTARG = integer[],
    COMMUTATOR = @,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.~ (integer[], integer[]) OWNER TO mikrobill;


CREATE OPERATOR ~~ (
    PROCEDURE = rboolop,
    LEFTARG = query_int,
    RIGHTARG = integer[],
    COMMUTATOR = @@,
    RESTRICT = contsel,
    JOIN = contjoinsel
);


ALTER OPERATOR public.~~ (query_int, integer[]) OWNER TO mikrobill;


CREATE OPERATOR CLASS gin__int_ops
    FOR TYPE integer[] USING gin AS
    STORAGE integer ,
    OPERATOR 3 &&(integer[],integer[]) ,
    OPERATOR 6 =(anyarray,anyarray) RECHECK ,
    OPERATOR 7 @>(integer[],integer[]) ,
    OPERATOR 8 <@(integer[],integer[]) RECHECK ,
    OPERATOR 13 @(integer[],integer[]) ,
    OPERATOR 14 ~(integer[],integer[]) RECHECK ,
    OPERATOR 20 @@(integer[],query_int) ,
    FUNCTION 1 btint4cmp(integer,integer) ,
    FUNCTION 2 ginarrayextract(anyarray,internal) ,
    FUNCTION 3 ginint4_queryextract(internal,internal,smallint) ,
    FUNCTION 4 ginint4_consistent(internal,smallint,internal);


ALTER OPERATOR CLASS public.gin__int_ops USING gin OWNER TO mikrobill;


CREATE OPERATOR CLASS gist__int_ops
    DEFAULT FOR TYPE integer[] USING gist AS
    OPERATOR 3 &&(integer[],integer[]) ,
    OPERATOR 6 =(anyarray,anyarray) RECHECK ,
    OPERATOR 7 @>(integer[],integer[]) ,
    OPERATOR 8 <@(integer[],integer[]) ,
    OPERATOR 13 @(integer[],integer[]) ,
    OPERATOR 14 ~(integer[],integer[]) ,
    OPERATOR 20 @@(integer[],query_int) ,
    FUNCTION 1 g_int_consistent(internal,integer[],integer) ,
    FUNCTION 2 g_int_union(internal,internal) ,
    FUNCTION 3 g_int_compress(internal) ,
    FUNCTION 4 g_int_decompress(internal) ,
    FUNCTION 5 g_int_penalty(internal,internal,internal) ,
    FUNCTION 6 g_int_picksplit(internal,internal) ,
    FUNCTION 7 g_int_same(integer[],integer[],internal);


ALTER OPERATOR CLASS public.gist__int_ops USING gist OWNER TO mikrobill;


CREATE OPERATOR CLASS gist__intbig_ops
    FOR TYPE integer[] USING gist AS
    STORAGE intbig_gkey ,
    OPERATOR 3 &&(integer[],integer[]) RECHECK ,
    OPERATOR 6 =(anyarray,anyarray) RECHECK ,
    OPERATOR 7 @>(integer[],integer[]) RECHECK ,
    OPERATOR 8 <@(integer[],integer[]) RECHECK ,
    OPERATOR 13 @(integer[],integer[]) RECHECK ,
    OPERATOR 14 ~(integer[],integer[]) RECHECK ,
    OPERATOR 20 @@(integer[],query_int) RECHECK ,
    FUNCTION 1 g_intbig_consistent(internal,internal,integer) ,
    FUNCTION 2 g_intbig_union(internal,internal) ,
    FUNCTION 3 g_intbig_compress(internal) ,
    FUNCTION 4 g_intbig_decompress(internal) ,
    FUNCTION 5 g_intbig_penalty(internal,internal,internal) ,
    FUNCTION 6 g_intbig_picksplit(internal,internal) ,
    FUNCTION 7 g_intbig_same(internal,internal,internal);


ALTER OPERATOR CLASS public.gist__intbig_ops USING gist OWNER TO mikrobill;


CREATE TABLE auth_group (
    id integer NOT NULL,
    name character varying(80) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO mikrobill;


CREATE SEQUENCE auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_group_id_seq OWNER TO mikrobill;


ALTER SEQUENCE auth_group_id_seq OWNED BY auth_group.id;



CREATE TABLE auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO mikrobill;


CREATE SEQUENCE auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_group_permissions_id_seq OWNER TO mikrobill;


ALTER SEQUENCE auth_group_permissions_id_seq OWNED BY auth_group_permissions.id;



CREATE TABLE auth_message (
    id integer NOT NULL,
    user_id integer NOT NULL,
    message text NOT NULL
);


ALTER TABLE public.auth_message OWNER TO mikrobill;


CREATE SEQUENCE auth_message_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_message_id_seq OWNER TO mikrobill;


ALTER SEQUENCE auth_message_id_seq OWNED BY auth_message.id;



CREATE TABLE auth_permission (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO mikrobill;


CREATE SEQUENCE auth_permission_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_permission_id_seq OWNER TO mikrobill;


ALTER SEQUENCE auth_permission_id_seq OWNED BY auth_permission.id;



CREATE TABLE auth_user (
    id integer NOT NULL,
    username character varying(30) NOT NULL,
    first_name character varying(30) NOT NULL,
    last_name character varying(30) NOT NULL,
    email character varying(75) NOT NULL,
    password character varying(128) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    is_superuser boolean NOT NULL,
    last_login timestamp without time zone NOT NULL,
    date_joined timestamp without time zone NOT NULL
);


ALTER TABLE public.auth_user OWNER TO mikrobill;


CREATE TABLE auth_user_groups (
    id integer NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE public.auth_user_groups OWNER TO mikrobill;


CREATE SEQUENCE auth_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_user_groups_id_seq OWNER TO mikrobill;


ALTER SEQUENCE auth_user_groups_id_seq OWNED BY auth_user_groups.id;



CREATE SEQUENCE auth_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_user_id_seq OWNER TO mikrobill;


ALTER SEQUENCE auth_user_id_seq OWNED BY auth_user.id;



CREATE TABLE auth_user_user_permissions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_user_user_permissions OWNER TO mikrobill;


CREATE SEQUENCE auth_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_user_user_permissions_id_seq OWNER TO mikrobill;


ALTER SEQUENCE auth_user_user_permissions_id_seq OWNED BY auth_user_user_permissions.id;



CREATE TABLE billservice_accessparameters (
    id integer NOT NULL,
    access_type character varying(255) NOT NULL,
    access_time_id integer NOT NULL,
    max_limit character varying(64) DEFAULT ''::character varying,
    min_limit character varying(64) DEFAULT ''::character varying,
    burst_limit character varying(64) DEFAULT ''::character varying,
    burst_treshold character varying(64) DEFAULT ''::character varying,
    burst_time character varying(64) DEFAULT ''::character varying,
    priority integer DEFAULT 8,
    ipn_for_vpn boolean DEFAULT false
);


ALTER TABLE public.billservice_accessparameters OWNER TO mikrobill;


CREATE SEQUENCE billservice_accessparameters_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_accessparameters_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_accessparameters_id_seq OWNED BY billservice_accessparameters.id;



CREATE TABLE billservice_account (
    id integer NOT NULL,
    username character varying(200) NOT NULL,
    password character varying(200) DEFAULT ''::character varying,
    fullname character varying(200) DEFAULT ''::character varying,
    email character varying(200) DEFAULT ''::character varying,
    address text DEFAULT ''::text,
    nas_id integer NOT NULL,
    vpn_ip_address inet DEFAULT '0.0.0.0'::inet,
    assign_ipn_ip_from_dhcp boolean DEFAULT false,
    ipn_ip_address inet DEFAULT '0.0.0.0'::inet,
    ipn_mac_address character varying(32) DEFAULT ''::character varying,
    ipn_status boolean DEFAULT false,
    status boolean DEFAULT false,
    suspended boolean DEFAULT true,
    created timestamp without time zone DEFAULT now(),
    ballance double precision DEFAULT 0,
    credit double precision DEFAULT 0,
    disabled_by_limit boolean DEFAULT false,
    balance_blocked boolean DEFAULT false,
    ipn_speed character varying(96) DEFAULT ''::character varying,
    vpn_speed character varying(96) DEFAULT ''::character varying,
    netmask inet DEFAULT '0.0.0.0'::inet,
    ipn_added boolean DEFAULT false,
    city character varying(255) DEFAULT ''::character varying,
    postcode character varying(255) DEFAULT ''::character varying,
    region character varying(255) DEFAULT ''::character varying,
    street character varying(255) DEFAULT ''::character varying,
    house character varying(255) DEFAULT ''::character varying,
    house_bulk character varying(255) DEFAULT ''::character varying,
    entrance character varying(255) DEFAULT ''::character varying,
    room character varying(255) DEFAULT ''::character varying,
    vlan integer,
    allow_webcab boolean DEFAULT true,
    allow_expresscards boolean DEFAULT true,
    assign_dhcp_null boolean DEFAULT true,
    assign_dhcp_block boolean DEFAULT true,
    allow_vpn_null boolean DEFAULT true,
    allow_vpn_block boolean DEFAULT true,
    passport character varying(255) DEFAULT ''::character varying,
    passport_date timestamp without time zone,
    passport_given character varying(255) DEFAULT ''::character varying,
    phone_h character varying DEFAULT ''::character varying,
    phone_m character varying DEFAULT ''::character varying,
    vpn_ipinuse_id integer,
    ipn_ipinuse_id integer
);


ALTER TABLE public.billservice_account OWNER TO mikrobill;


CREATE SEQUENCE billservice_account_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_account_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_account_id_seq OWNED BY billservice_account.id;



CREATE TABLE billservice_accountipnspeed (
    id integer NOT NULL,
    account_id integer NOT NULL,
    speed character varying(32) DEFAULT ''::character varying,
    state boolean DEFAULT false,
    static boolean DEFAULT false,
    datetime timestamp without time zone DEFAULT now()
);


ALTER TABLE public.billservice_accountipnspeed OWNER TO mikrobill;


CREATE SEQUENCE billservice_accountipnspeed_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_accountipnspeed_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_accountipnspeed_id_seq OWNED BY billservice_accountipnspeed.id;



CREATE TABLE billservice_accountprepaystime (
    id integer NOT NULL,
    account_tarif_id integer NOT NULL,
    prepaid_time_service_id integer NOT NULL,
    size integer DEFAULT 0,
    datetime timestamp without time zone DEFAULT now()
);


ALTER TABLE public.billservice_accountprepaystime OWNER TO mikrobill;


CREATE SEQUENCE billservice_accountprepaystime_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_accountprepaystime_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_accountprepaystime_id_seq OWNED BY billservice_accountprepaystime.id;



CREATE TABLE billservice_accountprepaystrafic (
    id integer NOT NULL,
    account_tarif_id integer NOT NULL,
    prepaid_traffic_id integer NOT NULL,
    size double precision DEFAULT 0,
    datetime timestamp without time zone DEFAULT now()
);


ALTER TABLE public.billservice_accountprepaystrafic OWNER TO mikrobill;


CREATE SEQUENCE billservice_accountprepaystrafic_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_accountprepaystrafic_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_accountprepaystrafic_id_seq OWNED BY billservice_accountprepaystrafic.id;



CREATE TABLE billservice_accountspeedlimit (
    id integer NOT NULL,
    account_id integer NOT NULL,
    speedlimit_id integer NOT NULL
);


ALTER TABLE public.billservice_accountspeedlimit OWNER TO mikrobill;


CREATE SEQUENCE billservice_accountspeedlimit_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_accountspeedlimit_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_accountspeedlimit_id_seq OWNED BY billservice_accountspeedlimit.id;



CREATE TABLE billservice_accounttarif (
    id integer NOT NULL,
    account_id integer NOT NULL,
    tarif_id integer NOT NULL,
    datetime timestamp without time zone
);


ALTER TABLE public.billservice_accounttarif OWNER TO mikrobill;


CREATE SEQUENCE billservice_accounttarif_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_accounttarif_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_accounttarif_id_seq OWNED BY billservice_accounttarif.id;



CREATE TABLE billservice_bankdata (
    id integer NOT NULL,
    bank character varying(255) NOT NULL,
    bankcode character varying(40) NOT NULL,
    rs character varying(60) NOT NULL,
    currency character varying(40) NOT NULL
);


ALTER TABLE public.billservice_bankdata OWNER TO mikrobill;


CREATE SEQUENCE billservice_bankdata_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_bankdata_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_bankdata_id_seq OWNED BY billservice_bankdata.id;



CREATE TABLE billservice_card (
    id integer NOT NULL,
    series integer NOT NULL,
    pin character varying(255) DEFAULT ''::character varying NOT NULL,
    sold timestamp without time zone,
    nominal double precision DEFAULT 0,
    activated timestamp without time zone,
    activated_by_id integer,
    start_date timestamp without time zone,
    end_date timestamp without time zone,
    disabled boolean DEFAULT false,
    created timestamp without time zone,
    template_id integer,
    account_id integer,
    tarif_id integer,
    nas_id integer,
    login character varying DEFAULT ''::character varying,
    ip character varying,
    ipinuse_id integer
);


ALTER TABLE public.billservice_card OWNER TO mikrobill;


CREATE SEQUENCE billservice_card_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_card_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_card_id_seq OWNED BY billservice_card.id;



CREATE TABLE billservice_dealer (
    id integer NOT NULL,
    organization character varying(400) NOT NULL,
    unp character varying(255) NOT NULL,
    okpo character varying(255) NOT NULL,
    contactperson character varying(255) NOT NULL,
    director character varying(255) NOT NULL,
    phone character varying(255) NOT NULL,
    fax character varying(255) NOT NULL,
    postaddress character varying(400) NOT NULL,
    uraddress character varying(400) NOT NULL,
    email character varying(255) NOT NULL,
    bank_id integer NOT NULL,
    prepayment real,
    paydeffer integer,
    discount real,
    always_sell_cards boolean DEFAULT false NOT NULL,
    deleted boolean DEFAULT false
);


ALTER TABLE public.billservice_dealer OWNER TO mikrobill;


CREATE SEQUENCE billservice_dealer_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_dealer_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_dealer_id_seq OWNED BY billservice_dealer.id;



CREATE TABLE billservice_dealerpay (
    id integer NOT NULL,
    dealer_id integer NOT NULL,
    pay double precision NOT NULL,
    salecard_id integer,
    created timestamp with time zone NOT NULL
);


ALTER TABLE public.billservice_dealerpay OWNER TO mikrobill;


CREATE SEQUENCE billservice_dealerpay_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_dealerpay_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_dealerpay_id_seq OWNED BY billservice_dealerpay.id;



CREATE TABLE billservice_document (
    id integer NOT NULL,
    account_id integer,
    type_id integer NOT NULL,
    body text NOT NULL
);


ALTER TABLE public.billservice_document OWNER TO mikrobill;


CREATE SEQUENCE billservice_document_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_document_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_document_id_seq OWNED BY billservice_document.id;



CREATE TABLE billservice_documenttype (
    id integer NOT NULL,
    name character varying(255) NOT NULL
);


ALTER TABLE public.billservice_documenttype OWNER TO mikrobill;


CREATE SEQUENCE billservice_documenttype_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_documenttype_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_documenttype_id_seq OWNED BY billservice_documenttype.id;



CREATE TABLE billservice_globalstat (
    id integer NOT NULL,
    account_id integer NOT NULL,
    bytes_in bigint DEFAULT 0 NOT NULL,
    bytes_out bigint DEFAULT 0 NOT NULL,
    datetime timestamp without time zone NOT NULL,
    nas_id integer NOT NULL,
    classes integer[],
    classbytes bigint[]
);


ALTER TABLE public.billservice_globalstat OWNER TO mikrobill;


CREATE SEQUENCE billservice_globalstat_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_globalstat_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_globalstat_id_seq OWNED BY billservice_globalstat.id;



CREATE TABLE billservice_group (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    direction integer NOT NULL,
    type integer NOT NULL
);


ALTER TABLE public.billservice_group OWNER TO mikrobill;


CREATE SEQUENCE billservice_group_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_group_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_group_id_seq OWNED BY billservice_group.id;



CREATE TABLE billservice_group_trafficclass (
    id integer NOT NULL,
    group_id integer NOT NULL,
    trafficclass_id integer NOT NULL
);


ALTER TABLE public.billservice_group_trafficclass OWNER TO mikrobill;


CREATE SEQUENCE billservice_group_trafficclass_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_group_trafficclass_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_group_trafficclass_id_seq OWNED BY billservice_group_trafficclass.id;



CREATE SEQUENCE billservice_groupstat_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_groupstat_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_groupstat_id_seq OWNED BY billservice_groupstat.id;



SELECT pg_catalog.setval('billservice_groupstat_id_seq', 1302, true);



CREATE TABLE billservice_ipinuse (
    id integer NOT NULL,
    pool_id integer NOT NULL,
    ip character varying(255) NOT NULL,
    datetime timestamp with time zone NOT NULL
);


ALTER TABLE public.billservice_ipinuse OWNER TO mikrobill;


CREATE SEQUENCE billservice_ipinuse_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_ipinuse_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_ipinuse_id_seq OWNED BY billservice_ipinuse.id;



SELECT pg_catalog.setval('billservice_ipinuse_id_seq', 192, true);



CREATE TABLE billservice_ippool (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    type integer NOT NULL,
    start_ip inet NOT NULL,
    end_ip inet NOT NULL
);


ALTER TABLE public.billservice_ippool OWNER TO mikrobill;


CREATE SEQUENCE billservice_ippool_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_ippool_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_ippool_id_seq OWNED BY billservice_ippool.id;



SELECT pg_catalog.setval('billservice_ippool_id_seq', 4, true);



CREATE SEQUENCE billservice_netflowstream_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_netflowstream_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_netflowstream_id_seq OWNED BY billservice_netflowstream.id;



CREATE TABLE billservice_onetimeservice (
    id integer NOT NULL,
    tarif_id integer NOT NULL,
    name character varying(255) NOT NULL,
    cost double precision NOT NULL
);


ALTER TABLE public.billservice_onetimeservice OWNER TO mikrobill;


CREATE SEQUENCE billservice_onetimeservice_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_onetimeservice_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_onetimeservice_id_seq OWNED BY billservice_onetimeservice.id;



CREATE TABLE billservice_onetimeservicehistory (
    id integer NOT NULL,
    accounttarif_id integer NOT NULL,
    onetimeservice_id integer NOT NULL,
    datetime timestamp without time zone NOT NULL,
    transaction_id integer
);


ALTER TABLE public.billservice_onetimeservicehistory OWNER TO mikrobill;


CREATE SEQUENCE billservice_onetimeservicehistory_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_onetimeservicehistory_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_onetimeservicehistory_id_seq OWNED BY billservice_onetimeservicehistory.id;



CREATE TABLE billservice_operator (
    id integer NOT NULL,
    organization character varying(255) NOT NULL,
    unp character varying(40) NOT NULL,
    okpo character varying(40) NOT NULL,
    contactperson character varying(255) NOT NULL,
    director character varying(255) NOT NULL,
    phone character varying(40) NOT NULL,
    postaddress character varying(255) NOT NULL,
    uraddress character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    fax character varying(40) NOT NULL,
    bank_id integer NOT NULL
);


ALTER TABLE public.billservice_operator OWNER TO mikrobill;


CREATE SEQUENCE billservice_operator_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_operator_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_operator_id_seq OWNED BY billservice_operator.id;



CREATE TABLE billservice_organization (
    id integer NOT NULL,
    account_id integer NOT NULL,
    name character varying(255) DEFAULT ''::character varying,
    uraddress character varying(255) DEFAULT ''::character varying,
    okpo character varying(255) DEFAULT ''::character varying,
    unp character varying(255) DEFAULT ''::character varying,
    bank_id integer NOT NULL,
    phone character varying(255) DEFAULT ''::character varying,
    fax character varying(255) DEFAULT ''::character varying
);


ALTER TABLE public.billservice_organization OWNER TO mikrobill;


CREATE SEQUENCE billservice_organization_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_organization_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_organization_id_seq OWNED BY billservice_organization.id;



CREATE TABLE billservice_periodicalservice (
    id integer NOT NULL,
    tarif_id integer NOT NULL,
    name character varying(255) NOT NULL,
    settlement_period_id integer NOT NULL,
    cost double precision NOT NULL,
    cash_method character varying(255) NOT NULL,
    condition integer DEFAULT 0 NOT NULL,
    created timestamp without time zone
);


ALTER TABLE public.billservice_periodicalservice OWNER TO mikrobill;


CREATE SEQUENCE billservice_periodicalservice_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_periodicalservice_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_periodicalservice_id_seq OWNED BY billservice_periodicalservice.id;



CREATE SEQUENCE billservice_periodicalservicehistory_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_periodicalservicehistory_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_periodicalservicehistory_id_seq OWNED BY billservice_periodicalservicehistory.id;



CREATE TABLE billservice_ports (
    id integer NOT NULL,
    port integer NOT NULL,
    protocol integer NOT NULL,
    name character varying(64) DEFAULT ''::character varying,
    description character varying(255) DEFAULT ''::character varying
);


ALTER TABLE public.billservice_ports OWNER TO mikrobill;


CREATE SEQUENCE billservice_ports_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_ports_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_ports_id_seq OWNED BY billservice_ports.id;



CREATE TABLE billservice_prepaidtraffic (
    id integer NOT NULL,
    traffic_transmit_service_id integer NOT NULL,
    size double precision DEFAULT 0,
    group_id integer NOT NULL
);


ALTER TABLE public.billservice_prepaidtraffic OWNER TO mikrobill;


CREATE SEQUENCE billservice_prepaidtraffic_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_prepaidtraffic_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_prepaidtraffic_id_seq OWNED BY billservice_prepaidtraffic.id;



SELECT pg_catalog.setval('billservice_prepaidtraffic_id_seq', 9, true);



CREATE TABLE billservice_rawnetflowstream (
    id integer NOT NULL,
    nas_id integer NOT NULL,
    date_start timestamp without time zone NOT NULL,
    src_addr inet NOT NULL,
    traffic_class_id integer,
    direction character varying(32) NOT NULL,
    dst_addr inet NOT NULL,
    next_hop inet NOT NULL,
    in_index integer NOT NULL,
    out_index integer NOT NULL,
    packets bigint NOT NULL,
    octets bigint NOT NULL,
    src_port integer NOT NULL,
    dst_port integer NOT NULL,
    tcp_flags integer NOT NULL,
    protocol integer NOT NULL,
    tos integer NOT NULL,
    source_as integer NOT NULL,
    dst_as integer NOT NULL,
    src_netmask_length integer NOT NULL,
    dst_netmask_length integer NOT NULL,
    fetched boolean DEFAULT false,
    account_id integer NOT NULL,
    store boolean DEFAULT false
);


ALTER TABLE public.billservice_rawnetflowstream OWNER TO mikrobill;


CREATE SEQUENCE billservice_rawnetflowstream_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_rawnetflowstream_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_rawnetflowstream_id_seq OWNED BY billservice_rawnetflowstream.id;



CREATE TABLE billservice_salecard (
    id integer NOT NULL,
    dealer_id integer NOT NULL,
    sum_for_pay double precision NOT NULL,
    paydeffer integer NOT NULL,
    discount double precision NOT NULL,
    discount_sum double precision NOT NULL,
    prepayment double precision NOT NULL,
    created timestamp with time zone NOT NULL
);


ALTER TABLE public.billservice_salecard OWNER TO mikrobill;


CREATE TABLE billservice_salecard_cards (
    id integer NOT NULL,
    salecard_id integer NOT NULL,
    card_id integer NOT NULL
);


ALTER TABLE public.billservice_salecard_cards OWNER TO mikrobill;


CREATE SEQUENCE billservice_salecard_cards_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_salecard_cards_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_salecard_cards_id_seq OWNED BY billservice_salecard_cards.id;



CREATE SEQUENCE billservice_salecard_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_salecard_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_salecard_id_seq OWNED BY billservice_salecard.id;



CREATE TABLE billservice_settlementperiod (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    time_start timestamp without time zone NOT NULL,
    length integer NOT NULL,
    length_in character varying(255) DEFAULT ''::character varying,
    autostart boolean DEFAULT false
);


ALTER TABLE public.billservice_settlementperiod OWNER TO mikrobill;


CREATE SEQUENCE billservice_settlementperiod_id_seq
    START WITH 11
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_settlementperiod_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_settlementperiod_id_seq OWNED BY billservice_settlementperiod.id;



CREATE TABLE billservice_shedulelog (
    id integer NOT NULL,
    account_id integer NOT NULL,
    ballance_checkout timestamp without time zone,
    prepaid_traffic_reset timestamp without time zone,
    prepaid_traffic_accrued timestamp without time zone,
    prepaid_time_reset timestamp without time zone,
    prepaid_time_accrued timestamp without time zone,
    balance_blocked timestamp without time zone,
    accounttarif_id integer
);


ALTER TABLE public.billservice_shedulelog OWNER TO postgres;


CREATE SEQUENCE billservice_shedulelog_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_shedulelog_id_seq OWNER TO postgres;


ALTER SEQUENCE billservice_shedulelog_id_seq OWNED BY billservice_shedulelog.id;



CREATE TABLE billservice_speedlimit (
    id integer NOT NULL,
    limit_id integer NOT NULL,
    max_tx integer NOT NULL,
    max_rx integer NOT NULL,
    burst_tx integer NOT NULL,
    burst_rx integer NOT NULL,
    burst_treshold_tx integer NOT NULL,
    burst_treshold_rx integer NOT NULL,
    burst_time_tx integer NOT NULL,
    burst_time_rx integer NOT NULL,
    min_tx integer NOT NULL,
    min_rx integer NOT NULL,
    priority integer NOT NULL
);


ALTER TABLE public.billservice_speedlimit OWNER TO mikrobill;


CREATE SEQUENCE billservice_speedlimit_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_speedlimit_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_speedlimit_id_seq OWNED BY billservice_speedlimit.id;



CREATE TABLE billservice_suspendedperiod (
    id integer NOT NULL,
    account_id integer NOT NULL,
    start_date timestamp with time zone NOT NULL,
    end_date timestamp with time zone NOT NULL
);


ALTER TABLE public.billservice_suspendedperiod OWNER TO mikrobill;


CREATE SEQUENCE billservice_suspendedperiod_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_suspendedperiod_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_suspendedperiod_id_seq OWNED BY billservice_suspendedperiod.id;



CREATE TABLE billservice_systemuser (
    id integer NOT NULL,
    username character varying(255) NOT NULL,
    password character varying(255) DEFAULT ''::character varying,
    last_ip character varying(64),
    last_login timestamp without time zone,
    description text DEFAULT ''::text,
    created timestamp without time zone,
    status boolean DEFAULT false,
    host character varying(255) DEFAULT '0.0.0.0/0'::character varying
);


ALTER TABLE public.billservice_systemuser OWNER TO mikrobill;


CREATE SEQUENCE billservice_systemuser_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_systemuser_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_systemuser_id_seq OWNED BY billservice_systemuser.id;



CREATE SEQUENCE billservice_tariff_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_tariff_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_tariff_id_seq OWNED BY billservice_tariff.id;



CREATE TABLE billservice_template (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    type_id integer NOT NULL,
    body text NOT NULL
);


ALTER TABLE public.billservice_template OWNER TO mikrobill;


CREATE SEQUENCE billservice_template_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_template_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_template_id_seq OWNED BY billservice_template.id;



CREATE TABLE billservice_timeaccessnode (
    id integer NOT NULL,
    time_access_service_id integer NOT NULL,
    time_period_id integer NOT NULL,
    cost double precision DEFAULT 0
);


ALTER TABLE public.billservice_timeaccessnode OWNER TO mikrobill;


CREATE SEQUENCE billservice_timeaccessnode_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_timeaccessnode_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_timeaccessnode_id_seq OWNED BY billservice_timeaccessnode.id;



CREATE TABLE billservice_timeaccessservice (
    id integer NOT NULL,
    prepaid_time integer DEFAULT 0,
    reset_time boolean DEFAULT false
);


ALTER TABLE public.billservice_timeaccessservice OWNER TO mikrobill;


CREATE SEQUENCE billservice_timeaccessservice_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_timeaccessservice_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_timeaccessservice_id_seq OWNED BY billservice_timeaccessservice.id;



CREATE TABLE billservice_timeperiod (
    id integer NOT NULL,
    name character varying(255) NOT NULL
);


ALTER TABLE public.billservice_timeperiod OWNER TO mikrobill;


CREATE SEQUENCE billservice_timeperiod_id_seq
    START WITH 15
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_timeperiod_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_timeperiod_id_seq OWNED BY billservice_timeperiod.id;



CREATE TABLE billservice_timeperiod_time_period_nodes (
    id integer NOT NULL,
    timeperiod_id integer NOT NULL,
    timeperiodnode_id integer NOT NULL
);


ALTER TABLE public.billservice_timeperiod_time_period_nodes OWNER TO mikrobill;


CREATE SEQUENCE billservice_timeperiod_time_period_nodes_id_seq
    START WITH 31
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_timeperiod_time_period_nodes_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_timeperiod_time_period_nodes_id_seq OWNED BY billservice_timeperiod_time_period_nodes.id;



CREATE TABLE billservice_timeperiodnode (
    id integer NOT NULL,
    name character varying(255) DEFAULT ''::character varying,
    time_start timestamp without time zone NOT NULL,
    length integer NOT NULL,
    repeat_after character varying(255) DEFAULT ''::character varying
);


ALTER TABLE public.billservice_timeperiodnode OWNER TO mikrobill;


CREATE SEQUENCE billservice_timeperiodnode_id_seq
    START WITH 27
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_timeperiodnode_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_timeperiodnode_id_seq OWNED BY billservice_timeperiodnode.id;



CREATE TABLE billservice_timespeed (
    id integer NOT NULL,
    access_parameters_id integer NOT NULL,
    time_id integer NOT NULL,
    max_limit character varying(64) DEFAULT ''::character varying,
    min_limit character varying(64) DEFAULT ''::character varying,
    burst_limit character varying(64) DEFAULT ''::character varying,
    burst_treshold character varying(64) DEFAULT ''::character varying,
    burst_time character varying(64) DEFAULT ''::character varying,
    priority integer DEFAULT 8
);


ALTER TABLE public.billservice_timespeed OWNER TO mikrobill;


CREATE SEQUENCE billservice_timespeed_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_timespeed_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_timespeed_id_seq OWNED BY billservice_timespeed.id;



CREATE TABLE billservice_trafficlimit (
    id integer NOT NULL,
    tarif_id integer NOT NULL,
    name character varying(255) NOT NULL,
    settlement_period_id integer,
    size double precision NOT NULL,
    mode boolean NOT NULL,
    group_id integer NOT NULL,
    action integer
);


ALTER TABLE public.billservice_trafficlimit OWNER TO mikrobill;


CREATE SEQUENCE billservice_trafficlimit_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_trafficlimit_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_trafficlimit_id_seq OWNED BY billservice_trafficlimit.id;



CREATE TABLE billservice_trafficlimit_traffic_class (
    id integer NOT NULL,
    trafficlimit_id integer NOT NULL,
    trafficclass_id integer NOT NULL
);


ALTER TABLE public.billservice_trafficlimit_traffic_class OWNER TO mikrobill;


CREATE SEQUENCE billservice_trafficlimit_traffic_class_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_trafficlimit_traffic_class_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_trafficlimit_traffic_class_id_seq OWNED BY billservice_trafficlimit_traffic_class.id;



CREATE TABLE billservice_traffictransmitnodes (
    id integer NOT NULL,
    traffic_transmit_service_id integer NOT NULL,
    cost double precision DEFAULT 0,
    edge_start double precision DEFAULT 0,
    edge_end double precision DEFAULT 0,
    group_id integer,
    in_direction boolean DEFAULT false,
    out_direction boolean DEFAULT false
);


ALTER TABLE public.billservice_traffictransmitnodes OWNER TO mikrobill;


CREATE TABLE billservice_traffictransmitnodes_group (
    id integer NOT NULL,
    traffictransmitnodes_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE public.billservice_traffictransmitnodes_group OWNER TO mikrobill;


CREATE SEQUENCE billservice_traffictransmitnodes_group_id_seq
    START WITH 12
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_traffictransmitnodes_group_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_traffictransmitnodes_group_id_seq OWNED BY billservice_traffictransmitnodes_group.id;



CREATE SEQUENCE billservice_traffictransmitnodes_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_traffictransmitnodes_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_traffictransmitnodes_id_seq OWNED BY billservice_traffictransmitnodes.id;



CREATE TABLE billservice_traffictransmitnodes_time_nodes (
    id integer NOT NULL,
    traffictransmitnodes_id integer NOT NULL,
    timeperiod_id integer NOT NULL
);


ALTER TABLE public.billservice_traffictransmitnodes_time_nodes OWNER TO mikrobill;


CREATE SEQUENCE billservice_traffictransmitnodes_time_nodes_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_traffictransmitnodes_time_nodes_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_traffictransmitnodes_time_nodes_id_seq OWNED BY billservice_traffictransmitnodes_time_nodes.id;



CREATE TABLE billservice_traffictransmitnodes_traffic_class (
    id integer NOT NULL,
    traffictransmitnodes_id integer NOT NULL,
    trafficclass_id integer NOT NULL
);


ALTER TABLE public.billservice_traffictransmitnodes_traffic_class OWNER TO mikrobill;


CREATE SEQUENCE billservice_traffictransmitnodes_traffic_class_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_traffictransmitnodes_traffic_class_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_traffictransmitnodes_traffic_class_id_seq OWNED BY billservice_traffictransmitnodes_traffic_class.id;



CREATE TABLE billservice_traffictransmitservice (
    id integer NOT NULL,
    reset_traffic boolean DEFAULT false,
    cash_method character varying(32) DEFAULT 'SUMM'::character varying,
    period_check character varying(32) DEFAULT 'SP_START'::character varying
);


ALTER TABLE public.billservice_traffictransmitservice OWNER TO mikrobill;


CREATE SEQUENCE billservice_traffictransmitservice_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_traffictransmitservice_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_traffictransmitservice_id_seq OWNED BY billservice_traffictransmitservice.id;



CREATE SEQUENCE billservice_transaction_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_transaction_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_transaction_id_seq OWNED BY billservice_transaction.id;



CREATE TABLE billservice_transactiontype (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    internal_name character varying(32) NOT NULL
);


ALTER TABLE public.billservice_transactiontype OWNER TO mikrobill;


CREATE SEQUENCE billservice_transactiontype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_transactiontype_id_seq OWNER TO mikrobill;


ALTER SEQUENCE billservice_transactiontype_id_seq OWNED BY billservice_transactiontype.id;



CREATE TABLE django_admin_log (
    id integer NOT NULL,
    action_time timestamp without time zone NOT NULL,
    user_id integer NOT NULL,
    content_type_id integer,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE public.django_admin_log OWNER TO mikrobill;


CREATE SEQUENCE django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.django_admin_log_id_seq OWNER TO mikrobill;


ALTER SEQUENCE django_admin_log_id_seq OWNED BY django_admin_log.id;



CREATE TABLE django_content_type (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO mikrobill;


CREATE SEQUENCE django_content_type_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.django_content_type_id_seq OWNER TO mikrobill;


ALTER SEQUENCE django_content_type_id_seq OWNED BY django_content_type.id;



CREATE TABLE django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp without time zone NOT NULL
);


ALTER TABLE public.django_session OWNER TO mikrobill;


CREATE TABLE django_site (
    id integer NOT NULL,
    domain character varying(100) NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE public.django_site OWNER TO mikrobill;


CREATE SEQUENCE django_site_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.django_site_id_seq OWNER TO mikrobill;


ALTER SEQUENCE django_site_id_seq OWNED BY django_site.id;



CREATE SEQUENCE gpst20090101_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.gpst20090101_id_seq OWNER TO mikrobill;


ALTER TABLE billservice_groupstat ALTER COLUMN id SET DEFAULT nextval('billservice_groupstat_id_seq'::regclass);



CREATE TABLE gpst20090101 (
    id integer DEFAULT nextval('gpst20090101_id_seq'::regclass),
    CONSTRAINT gpst20090101_datetime_check CHECK (((datetime >= '2009-01-01'::date) AND (datetime < '2009-02-01'::date)))
)
INHERITS (billservice_groupstat);


ALTER TABLE public.gpst20090101 OWNER TO mikrobill;


CREATE SEQUENCE gpst20090201_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.gpst20090201_id_seq OWNER TO mikrobill;


CREATE TABLE gpst20090201 (
    id integer DEFAULT nextval('gpst20090201_id_seq'::regclass),
    CONSTRAINT gpst20090201_datetime_check CHECK (((datetime >= '2009-02-01'::date) AND (datetime < '2009-03-01'::date)))
)
INHERITS (billservice_groupstat);


ALTER TABLE public.gpst20090201 OWNER TO mikrobill;


CREATE SEQUENCE gpst20090301_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.gpst20090301_id_seq OWNER TO mikrobill;


CREATE TABLE gpst20090301 (
    id integer DEFAULT nextval('gpst20090301_id_seq'::regclass),
    CONSTRAINT gpst20090301_datetime_check CHECK (((datetime >= '2009-03-01'::date) AND (datetime < '2009-04-01'::date)))
)
INHERITS (billservice_groupstat);


ALTER TABLE public.gpst20090301 OWNER TO mikrobill;


CREATE TABLE nas_nas (
    id integer NOT NULL,
    type character varying(32) NOT NULL,
    name character varying(255) NOT NULL,
    ipaddress character varying(255) NOT NULL,
    secret character varying(255) NOT NULL,
    login character varying(255) DEFAULT 'admin'::character varying,
    password character varying(255) NOT NULL,
    allow_pptp boolean DEFAULT true,
    allow_pppoe boolean DEFAULT true,
    allow_ipn boolean DEFAULT true,
    user_add_action text,
    user_enable_action text,
    user_disable_action text,
    user_delete_action text,
    vpn_speed_action text DEFAULT ''::text,
    ipn_speed_action text DEFAULT ''::text,
    reset_action text DEFAULT ''::text,
    confstring text DEFAULT ''::text,
    multilink boolean DEFAULT false,
    identify character varying
);


ALTER TABLE public.nas_nas OWNER TO mikrobill;


CREATE SEQUENCE nas_nas_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.nas_nas_id_seq OWNER TO mikrobill;


ALTER SEQUENCE nas_nas_id_seq OWNED BY nas_nas.id;



CREATE TABLE nas_trafficclass (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    weight integer NOT NULL,
    color character varying(16) DEFAULT '#FFFFFF'::character varying,
    store boolean DEFAULT true,
    passthrough boolean DEFAULT true
);


ALTER TABLE public.nas_trafficclass OWNER TO mikrobill;


CREATE SEQUENCE nas_trafficclass_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.nas_trafficclass_id_seq OWNER TO mikrobill;


ALTER SEQUENCE nas_trafficclass_id_seq OWNED BY nas_trafficclass.id;



CREATE TABLE nas_trafficnode (
    id integer NOT NULL,
    traffic_class_id integer NOT NULL,
    name character varying(255) NOT NULL,
    direction character varying(32) NOT NULL,
    protocol integer DEFAULT 0,
    src_ip inet DEFAULT '0.0.0.0'::inet,
    src_mask inet DEFAULT '0.0.0.0'::inet,
    src_port integer DEFAULT 0,
    dst_ip inet DEFAULT '0.0.0.0'::inet,
    dst_mask inet DEFAULT '0.0.0.0'::inet,
    dst_port integer DEFAULT 0,
    next_hop inet DEFAULT '0.0.0.0'::inet
);


ALTER TABLE public.nas_trafficnode OWNER TO mikrobill;


CREATE SEQUENCE nas_trafficnode_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.nas_trafficnode_id_seq OWNER TO mikrobill;


ALTER SEQUENCE nas_trafficnode_id_seq OWNED BY nas_trafficnode.id;



SELECT pg_catalog.setval('nas_trafficnode_id_seq', 22, true);

ALTER TABLE billservice_netflowstream ALTER COLUMN id SET DEFAULT nextval('billservice_netflowstream_id_seq'::regclass);


ALTER TABLE billservice_periodicalservicehistory ALTER COLUMN id SET DEFAULT nextval('billservice_periodicalservicehistory_id_seq'::regclass);




CREATE TABLE radius_activesession (
    id integer NOT NULL,
    account_id integer NOT NULL,
    sessionid character varying(255),
    interrim_update timestamp without time zone DEFAULT now(),
    date_start timestamp without time zone,
    date_end timestamp without time zone,
    caller_id character varying(255),
    called_id character varying(255),
    nas_id character varying(255) NOT NULL,
    session_time integer DEFAULT 0,
    framed_protocol character varying(32) NOT NULL,
    bytes_in bigint,
    bytes_out bigint,
    session_status character varying(32),
    speed_string character varying(255),
    framed_ip_address character varying(255)
);


ALTER TABLE public.radius_activesession OWNER TO mikrobill;


CREATE SEQUENCE radius_activesession_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.radius_activesession_id_seq OWNER TO mikrobill;


ALTER SEQUENCE radius_activesession_id_seq OWNED BY radius_activesession.id;



CREATE SEQUENCE radius_session_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.radius_session_id_seq OWNER TO mikrobill;


ALTER SEQUENCE radius_session_id_seq OWNED BY radius_session.id;



SELECT pg_catalog.setval('radius_session_id_seq', 80527, true);



ALTER TABLE radius_session ALTER COLUMN id SET DEFAULT nextval('radius_session_id_seq'::regclass);




ALTER TABLE auth_group ALTER COLUMN id SET DEFAULT nextval('auth_group_id_seq'::regclass);



ALTER TABLE auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('auth_group_permissions_id_seq'::regclass);



ALTER TABLE auth_message ALTER COLUMN id SET DEFAULT nextval('auth_message_id_seq'::regclass);



ALTER TABLE auth_permission ALTER COLUMN id SET DEFAULT nextval('auth_permission_id_seq'::regclass);



ALTER TABLE auth_user ALTER COLUMN id SET DEFAULT nextval('auth_user_id_seq'::regclass);



ALTER TABLE auth_user_groups ALTER COLUMN id SET DEFAULT nextval('auth_user_groups_id_seq'::regclass);



ALTER TABLE auth_user_user_permissions ALTER COLUMN id SET DEFAULT nextval('auth_user_user_permissions_id_seq'::regclass);



ALTER TABLE billservice_accessparameters ALTER COLUMN id SET DEFAULT nextval('billservice_accessparameters_id_seq'::regclass);



ALTER TABLE billservice_account ALTER COLUMN id SET DEFAULT nextval('billservice_account_id_seq'::regclass);



ALTER TABLE billservice_accountipnspeed ALTER COLUMN id SET DEFAULT nextval('billservice_accountipnspeed_id_seq'::regclass);



ALTER TABLE billservice_accountprepaystime ALTER COLUMN id SET DEFAULT nextval('billservice_accountprepaystime_id_seq'::regclass);



ALTER TABLE billservice_accountprepaystrafic ALTER COLUMN id SET DEFAULT nextval('billservice_accountprepaystrafic_id_seq'::regclass);



ALTER TABLE billservice_accountspeedlimit ALTER COLUMN id SET DEFAULT nextval('billservice_accountspeedlimit_id_seq'::regclass);



ALTER TABLE billservice_accounttarif ALTER COLUMN id SET DEFAULT nextval('billservice_accounttarif_id_seq'::regclass);



ALTER TABLE billservice_bankdata ALTER COLUMN id SET DEFAULT nextval('billservice_bankdata_id_seq'::regclass);



ALTER TABLE billservice_card ALTER COLUMN id SET DEFAULT nextval('billservice_card_id_seq'::regclass);



ALTER TABLE billservice_dealer ALTER COLUMN id SET DEFAULT nextval('billservice_dealer_id_seq'::regclass);



ALTER TABLE billservice_dealerpay ALTER COLUMN id SET DEFAULT nextval('billservice_dealerpay_id_seq'::regclass);



ALTER TABLE billservice_document ALTER COLUMN id SET DEFAULT nextval('billservice_document_id_seq'::regclass);



ALTER TABLE billservice_documenttype ALTER COLUMN id SET DEFAULT nextval('billservice_documenttype_id_seq'::regclass);



ALTER TABLE billservice_globalstat ALTER COLUMN id SET DEFAULT nextval('billservice_globalstat_id_seq'::regclass);



ALTER TABLE billservice_group ALTER COLUMN id SET DEFAULT nextval('billservice_group_id_seq'::regclass);



ALTER TABLE billservice_group_trafficclass ALTER COLUMN id SET DEFAULT nextval('billservice_group_trafficclass_id_seq'::regclass);



ALTER TABLE billservice_ipinuse ALTER COLUMN id SET DEFAULT nextval('billservice_ipinuse_id_seq'::regclass);



ALTER TABLE billservice_ippool ALTER COLUMN id SET DEFAULT nextval('billservice_ippool_id_seq'::regclass);



ALTER TABLE billservice_onetimeservice ALTER COLUMN id SET DEFAULT nextval('billservice_onetimeservice_id_seq'::regclass);



ALTER TABLE billservice_onetimeservicehistory ALTER COLUMN id SET DEFAULT nextval('billservice_onetimeservicehistory_id_seq'::regclass);



ALTER TABLE billservice_operator ALTER COLUMN id SET DEFAULT nextval('billservice_operator_id_seq'::regclass);



ALTER TABLE billservice_organization ALTER COLUMN id SET DEFAULT nextval('billservice_organization_id_seq'::regclass);



ALTER TABLE billservice_periodicalservice ALTER COLUMN id SET DEFAULT nextval('billservice_periodicalservice_id_seq'::regclass);



ALTER TABLE billservice_ports ALTER COLUMN id SET DEFAULT nextval('billservice_ports_id_seq'::regclass);



ALTER TABLE billservice_prepaidtraffic ALTER COLUMN id SET DEFAULT nextval('billservice_prepaidtraffic_id_seq'::regclass);



ALTER TABLE billservice_rawnetflowstream ALTER COLUMN id SET DEFAULT nextval('billservice_rawnetflowstream_id_seq'::regclass);



ALTER TABLE billservice_salecard ALTER COLUMN id SET DEFAULT nextval('billservice_salecard_id_seq'::regclass);



ALTER TABLE billservice_salecard_cards ALTER COLUMN id SET DEFAULT nextval('billservice_salecard_cards_id_seq'::regclass);



ALTER TABLE billservice_settlementperiod ALTER COLUMN id SET DEFAULT nextval('billservice_settlementperiod_id_seq'::regclass);



ALTER TABLE billservice_shedulelog ALTER COLUMN id SET DEFAULT nextval('billservice_shedulelog_id_seq'::regclass);



ALTER TABLE billservice_speedlimit ALTER COLUMN id SET DEFAULT nextval('billservice_speedlimit_id_seq'::regclass);



ALTER TABLE billservice_suspendedperiod ALTER COLUMN id SET DEFAULT nextval('billservice_suspendedperiod_id_seq'::regclass);



ALTER TABLE billservice_systemuser ALTER COLUMN id SET DEFAULT nextval('billservice_systemuser_id_seq'::regclass);



ALTER TABLE billservice_tariff ALTER COLUMN id SET DEFAULT nextval('billservice_tariff_id_seq'::regclass);



ALTER TABLE billservice_template ALTER COLUMN id SET DEFAULT nextval('billservice_template_id_seq'::regclass);



ALTER TABLE billservice_timeaccessnode ALTER COLUMN id SET DEFAULT nextval('billservice_timeaccessnode_id_seq'::regclass);



ALTER TABLE billservice_timeaccessservice ALTER COLUMN id SET DEFAULT nextval('billservice_timeaccessservice_id_seq'::regclass);



ALTER TABLE billservice_timeperiod ALTER COLUMN id SET DEFAULT nextval('billservice_timeperiod_id_seq'::regclass);



ALTER TABLE billservice_timeperiod_time_period_nodes ALTER COLUMN id SET DEFAULT nextval('billservice_timeperiod_time_period_nodes_id_seq'::regclass);



ALTER TABLE billservice_timeperiodnode ALTER COLUMN id SET DEFAULT nextval('billservice_timeperiodnode_id_seq'::regclass);



ALTER TABLE billservice_timespeed ALTER COLUMN id SET DEFAULT nextval('billservice_timespeed_id_seq'::regclass);



ALTER TABLE billservice_trafficlimit ALTER COLUMN id SET DEFAULT nextval('billservice_trafficlimit_id_seq'::regclass);



ALTER TABLE billservice_trafficlimit_traffic_class ALTER COLUMN id SET DEFAULT nextval('billservice_trafficlimit_traffic_class_id_seq'::regclass);



ALTER TABLE billservice_traffictransmitnodes ALTER COLUMN id SET DEFAULT nextval('billservice_traffictransmitnodes_id_seq'::regclass);



ALTER TABLE billservice_traffictransmitnodes_time_nodes ALTER COLUMN id SET DEFAULT nextval('billservice_traffictransmitnodes_time_nodes_id_seq'::regclass);



ALTER TABLE billservice_traffictransmitnodes_traffic_class ALTER COLUMN id SET DEFAULT nextval('billservice_traffictransmitnodes_traffic_class_id_seq'::regclass);



ALTER TABLE billservice_traffictransmitservice ALTER COLUMN id SET DEFAULT nextval('billservice_traffictransmitservice_id_seq'::regclass);



ALTER TABLE billservice_transaction ALTER COLUMN id SET DEFAULT nextval('billservice_transaction_id_seq'::regclass);



ALTER TABLE billservice_transactiontype ALTER COLUMN id SET DEFAULT nextval('billservice_transactiontype_id_seq'::regclass);



ALTER TABLE django_admin_log ALTER COLUMN id SET DEFAULT nextval('django_admin_log_id_seq'::regclass);



ALTER TABLE django_content_type ALTER COLUMN id SET DEFAULT nextval('django_content_type_id_seq'::regclass);



ALTER TABLE django_site ALTER COLUMN id SET DEFAULT nextval('django_site_id_seq'::regclass);



ALTER TABLE nas_nas ALTER COLUMN id SET DEFAULT nextval('nas_nas_id_seq'::regclass);



ALTER TABLE nas_trafficclass ALTER COLUMN id SET DEFAULT nextval('nas_trafficclass_id_seq'::regclass);



ALTER TABLE nas_trafficnode ALTER COLUMN id SET DEFAULT nextval('nas_trafficnode_id_seq'::regclass);



ALTER TABLE radius_activesession ALTER COLUMN id SET DEFAULT nextval('radius_activesession_id_seq'::regclass);



ALTER TABLE temp_classinf ALTER COLUMN id SET DEFAULT nextval('temp_classinf_id_seq'::regclass);




COPY auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);



ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);



ALTER TABLE ONLY auth_message
    ADD CONSTRAINT auth_message_pkey PRIMARY KEY (id);



ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_key UNIQUE (content_type_id, codename);



ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);



ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);



ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_key UNIQUE (user_id, group_id);



ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);



ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);



ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_key UNIQUE (user_id, permission_id);



ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);



ALTER TABLE ONLY billservice_accessparameters
    ADD CONSTRAINT billservice_accessparameters_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_account
    ADD CONSTRAINT billservice_account_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_account
    ADD CONSTRAINT billservice_account_username_key UNIQUE (username);



ALTER TABLE ONLY billservice_accountipnspeed
    ADD CONSTRAINT billservice_accountipnspeed_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_accountprepaystime
    ADD CONSTRAINT billservice_accountprepaystime_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_accountprepaystrafic
    ADD CONSTRAINT billservice_accountprepaystrafic_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_accountspeedlimit
    ADD CONSTRAINT billservice_accountspeedlimit_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_accounttarif
    ADD CONSTRAINT billservice_accounttarif_acc_dt_uq_key UNIQUE (account_id, datetime);



ALTER TABLE ONLY billservice_accounttarif
    ADD CONSTRAINT billservice_accounttarif_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_bankdata
    ADD CONSTRAINT billservice_bankdata_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_card
    ADD CONSTRAINT billservice_card_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_dealer
    ADD CONSTRAINT billservice_dealer_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_dealerpay
    ADD CONSTRAINT billservice_dealerpay_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_document
    ADD CONSTRAINT billservice_document_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_documenttype
    ADD CONSTRAINT billservice_documenttype_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_globalstat
    ADD CONSTRAINT billservice_globalstat_acc_dt_uq_key UNIQUE (account_id, datetime);



ALTER TABLE ONLY billservice_globalstat
    ADD CONSTRAINT billservice_globalstat_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_group
    ADD CONSTRAINT billservice_group_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_group_trafficclass
    ADD CONSTRAINT billservice_group_trafficclass_group_id_key UNIQUE (group_id, trafficclass_id);



ALTER TABLE ONLY billservice_group_trafficclass
    ADD CONSTRAINT billservice_group_trafficclass_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_groupstat
    ADD CONSTRAINT billservice_groupstat_group_id_key UNIQUE (group_id, account_id, datetime);



ALTER TABLE ONLY billservice_groupstat
    ADD CONSTRAINT billservice_groupstat_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_netflowstream
    ADD CONSTRAINT billservice_netflowstream_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_onetimeservice
    ADD CONSTRAINT billservice_onetimeservice_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_onetimeservicehistory
    ADD CONSTRAINT billservice_onetimeservicehistory_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_operator
    ADD CONSTRAINT billservice_operator_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_organization
    ADD CONSTRAINT billservice_organization_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_periodicalservice
    ADD CONSTRAINT billservice_periodicalservice_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_periodicalservicehistory
    ADD CONSTRAINT billservice_periodicalservicehistory_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_ports
    ADD CONSTRAINT billservice_ports_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_prepaidtraffic
    ADD CONSTRAINT billservice_prepaidtraffic_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_prepaidtraffic_traffic_class
    ADD CONSTRAINT billservice_prepaidtraffic_traffic_class_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_prepaidtraffic_traffic_class
    ADD CONSTRAINT billservice_prepaidtraffic_traffic_class_prepaidtraffic_id_key UNIQUE (prepaidtraffic_id, trafficclass_id);



ALTER TABLE ONLY billservice_rawnetflowstream
    ADD CONSTRAINT billservice_rawnetflowstream_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_salecard_cards
    ADD CONSTRAINT billservice_salecard_cards_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_salecard_cards
    ADD CONSTRAINT billservice_salecard_cards_salecard_id_key UNIQUE (salecard_id, card_id);



ALTER TABLE ONLY billservice_salecard
    ADD CONSTRAINT billservice_salecard_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_settlementperiod
    ADD CONSTRAINT billservice_settlementperiod_name_key UNIQUE (name);



ALTER TABLE ONLY billservice_settlementperiod
    ADD CONSTRAINT billservice_settlementperiod_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_shedulelog
    ADD CONSTRAINT billservice_shedulelog_account_id_key UNIQUE (account_id);



ALTER TABLE ONLY billservice_shedulelog
    ADD CONSTRAINT billservice_shedulelog_accounttarif_id UNIQUE (accounttarif_id);



ALTER TABLE ONLY billservice_shedulelog
    ADD CONSTRAINT billservice_shedulelog_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_speedlimit
    ADD CONSTRAINT billservice_speedlimit_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_suspendedperiod
    ADD CONSTRAINT billservice_suspendedperiod_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_systemuser
    ADD CONSTRAINT billservice_systemuser_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_systemuser
    ADD CONSTRAINT billservice_systemuser_username_key UNIQUE (username);



ALTER TABLE ONLY billservice_tariff
    ADD CONSTRAINT billservice_tariff_name_key UNIQUE (name);



ALTER TABLE ONLY billservice_tariff
    ADD CONSTRAINT billservice_tariff_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_template
    ADD CONSTRAINT billservice_template_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_timeaccessnode
    ADD CONSTRAINT billservice_timeaccessnode_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_timeaccessservice
    ADD CONSTRAINT billservice_timeaccessservice_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_timeperiod
    ADD CONSTRAINT billservice_timeperiod_name_key UNIQUE (name);



ALTER TABLE ONLY billservice_timeperiod
    ADD CONSTRAINT billservice_timeperiod_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_timeperiod_time_period_nodes
    ADD CONSTRAINT billservice_timeperiod_time_period_nodes_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_timeperiod_time_period_nodes
    ADD CONSTRAINT billservice_timeperiod_time_period_nodes_timeperiod_id_key UNIQUE (timeperiod_id, timeperiodnode_id);



ALTER TABLE ONLY billservice_timeperiodnode
    ADD CONSTRAINT billservice_timeperiodnode_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_timespeed
    ADD CONSTRAINT billservice_timespeed_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_trafficlimit
    ADD CONSTRAINT billservice_trafficlimit_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_trafficlimit_traffic_class
    ADD CONSTRAINT billservice_trafficlimit_traffic_class_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_trafficlimit_traffic_class
    ADD CONSTRAINT billservice_trafficlimit_traffic_class_trafficlimit_id_key UNIQUE (trafficlimit_id, trafficclass_id);



ALTER TABLE ONLY billservice_traffictransmitnodes_group
    ADD CONSTRAINT billservice_traffictransmitnodes_group_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_traffictransmitnodes_group
    ADD CONSTRAINT billservice_traffictransmitnodes_group_tr_traffictransmitnodes_ UNIQUE (traffictransmitnodes_id, group_id);



ALTER TABLE ONLY billservice_traffictransmitnodes
    ADD CONSTRAINT billservice_traffictransmitnodes_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_traffictransmitnodes_time_nodes
    ADD CONSTRAINT billservice_traffictransmitnodes_ti_traffictransmitnodes_id_key UNIQUE (traffictransmitnodes_id, timeperiod_id);



ALTER TABLE ONLY billservice_traffictransmitnodes_time_nodes
    ADD CONSTRAINT billservice_traffictransmitnodes_time_nodes_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_traffictransmitnodes_traffic_class
    ADD CONSTRAINT billservice_traffictransmitnodes_tr_traffictransmitnodes_id_key UNIQUE (traffictransmitnodes_id, trafficclass_id);



ALTER TABLE ONLY billservice_traffictransmitnodes_traffic_class
    ADD CONSTRAINT billservice_traffictransmitnodes_traffic_class_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_traffictransmitservice
    ADD CONSTRAINT billservice_traffictransmitservice_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_transaction
    ADD CONSTRAINT billservice_transaction_pkey PRIMARY KEY (id);



ALTER TABLE ONLY billservice_transactiontype
    ADD CONSTRAINT billservice_transactiontype_internal_name_key UNIQUE (internal_name);



ALTER TABLE ONLY billservice_transactiontype
    ADD CONSTRAINT billservice_transactiontype_name_key UNIQUE (name);



ALTER TABLE ONLY billservice_transactiontype
    ADD CONSTRAINT billservice_transactiontype_pkey PRIMARY KEY (id);



ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);



ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_app_label_key UNIQUE (app_label, model);



ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);



ALTER TABLE ONLY django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);



ALTER TABLE ONLY django_site
    ADD CONSTRAINT django_site_pkey PRIMARY KEY (id);



ALTER TABLE ONLY gpst20090101
    ADD CONSTRAINT gpst20090101_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY gpst20090201
    ADD CONSTRAINT gpst20090201_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY gpst20090301
    ADD CONSTRAINT gpst20090301_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nas_nas
    ADD CONSTRAINT nas_nas_name_key UNIQUE (name);



ALTER TABLE ONLY nas_nas
    ADD CONSTRAINT nas_nas_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nas_trafficclass
    ADD CONSTRAINT nas_trafficclass_name_key UNIQUE (name);



ALTER TABLE ONLY nas_trafficclass
    ADD CONSTRAINT nas_trafficclass_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nas_trafficclass
    ADD CONSTRAINT nas_trafficclass_weight_key UNIQUE (weight);



ALTER TABLE ONLY nas_trafficnode
    ADD CONSTRAINT nas_trafficnode_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20081223
    ADD CONSTRAINT nfs20081223_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090105
    ADD CONSTRAINT nfs20090105_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090106
    ADD CONSTRAINT nfs20090106_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090107
    ADD CONSTRAINT nfs20090107_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090108
    ADD CONSTRAINT nfs20090108_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090109
    ADD CONSTRAINT nfs20090109_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090110
    ADD CONSTRAINT nfs20090110_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090111
    ADD CONSTRAINT nfs20090111_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090112
    ADD CONSTRAINT nfs20090112_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090113
    ADD CONSTRAINT nfs20090113_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090114
    ADD CONSTRAINT nfs20090114_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090115
    ADD CONSTRAINT nfs20090115_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090116
    ADD CONSTRAINT nfs20090116_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090117
    ADD CONSTRAINT nfs20090117_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090118
    ADD CONSTRAINT nfs20090118_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090119
    ADD CONSTRAINT nfs20090119_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090120
    ADD CONSTRAINT nfs20090120_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090122
    ADD CONSTRAINT nfs20090122_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090123
    ADD CONSTRAINT nfs20090123_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090124
    ADD CONSTRAINT nfs20090124_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090125
    ADD CONSTRAINT nfs20090125_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090126
    ADD CONSTRAINT nfs20090126_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090216
    ADD CONSTRAINT nfs20090216_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090218
    ADD CONSTRAINT nfs20090218_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090219
    ADD CONSTRAINT nfs20090219_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090220
    ADD CONSTRAINT nfs20090220_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090221
    ADD CONSTRAINT nfs20090221_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090223
    ADD CONSTRAINT nfs20090223_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090323
    ADD CONSTRAINT nfs20090323_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY nfs20090324
    ADD CONSTRAINT nfs20090324_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY psh20090201
    ADD CONSTRAINT psh20090201_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY psh20090301
    ADD CONSTRAINT psh20090301_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY radius_activesession
    ADD CONSTRAINT radius_activesession_pkey PRIMARY KEY (id);



ALTER TABLE ONLY radius_session
    ADD CONSTRAINT radius_session_pkey PRIMARY KEY (id);



ALTER TABLE ONLY rsss20081101
    ADD CONSTRAINT rsss20081101_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY temp_classinf
    ADD CONSTRAINT temp_classinf_pkey PRIMARY KEY (id);



ALTER TABLE ONLY tsct20081101
    ADD CONSTRAINT tsct20081101_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY tsct20081201
    ADD CONSTRAINT tsct20081201_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY tsct20090101
    ADD CONSTRAINT tsct20090101_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY tsct20090201
    ADD CONSTRAINT tsct20090201_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY tsct20090301
    ADD CONSTRAINT tsct20090301_id_pkey PRIMARY KEY (id);



ALTER TABLE ONLY z_date_tmp
    ADD CONSTRAINT z_date_tmp_pkey PRIMARY KEY (id);



ALTER TABLE ONLY ztm53
    ADD CONSTRAINT ztmp53_pr_key PRIMARY KEY (id);



ALTER TABLE ONLY ztm54
    ADD CONSTRAINT ztmp54_pr_key PRIMARY KEY (id);



ALTER TABLE ONLY ztm55
    ADD CONSTRAINT ztmp55_pr_key PRIMARY KEY (id);



ALTER TABLE ONLY ztm57
    ADD CONSTRAINT ztmp57_pr_key PRIMARY KEY (id);



ALTER TABLE ONLY ztm58
    ADD CONSTRAINT ztmp58_pr_key PRIMARY KEY (id);



ALTER TABLE ONLY ztm59
    ADD CONSTRAINT ztmp59_pr_key PRIMARY KEY (id);



ALTER TABLE ONLY ztm52
    ADD CONSTRAINT ztmp_pr_key PRIMARY KEY (id);



CREATE INDEX auth_message_user_id ON auth_message USING btree (user_id);



CREATE INDEX auth_permission_content_type_id ON auth_permission USING btree (content_type_id);



CREATE INDEX billservice_accessparameters_access_time_id ON billservice_accessparameters USING btree (access_time_id);



CREATE INDEX billservice_account_ipn_ip_address ON billservice_account USING btree (ipn_ip_address);



CREATE INDEX billservice_account_nas_id ON billservice_account USING btree (nas_id);



CREATE INDEX billservice_account_vpn_ip_address ON billservice_account USING btree (vpn_ip_address);



CREATE INDEX billservice_accountipnspeed_account_id ON billservice_accountipnspeed USING btree (account_id);



CREATE INDEX billservice_accountprepaystime_account_tarif_id ON billservice_accountprepaystime USING btree (account_tarif_id);



CREATE INDEX billservice_accountprepaystime_prepaid_time_service_id ON billservice_accountprepaystime USING btree (prepaid_time_service_id);



CREATE INDEX billservice_accountprepaystrafic_account_tarif_id ON billservice_accountprepaystrafic USING btree (account_tarif_id);



CREATE INDEX billservice_accountprepaystrafic_prepaid_traffic_id ON billservice_accountprepaystrafic USING btree (prepaid_traffic_id);



CREATE INDEX billservice_accountspeedlimit_account_id ON billservice_accountspeedlimit USING btree (account_id);



CREATE INDEX billservice_accountspeedlimit_speedlimit_id ON billservice_accountspeedlimit USING btree (speedlimit_id);



CREATE INDEX billservice_accounttarif_account_id ON billservice_accounttarif USING btree (account_id);



CREATE INDEX billservice_accounttarif_tarif_id ON billservice_accounttarif USING btree (tarif_id);



CREATE INDEX billservice_card_activated_by_id ON billservice_card USING btree (activated_by_id);



CREATE INDEX billservice_dealer_bank_id ON billservice_dealer USING btree (bank_id);



CREATE INDEX billservice_dealerpay_dealer_id ON billservice_dealerpay USING btree (dealer_id);



CREATE INDEX billservice_dealerpay_salecard_id ON billservice_dealerpay USING btree (salecard_id);



CREATE INDEX billservice_document_account_id ON billservice_document USING btree (account_id);



CREATE INDEX billservice_document_type_id ON billservice_document USING btree (type_id);



CREATE INDEX billservice_globalstat_acc_dt_id ON billservice_globalstat USING btree (account_id, datetime);



CREATE INDEX billservice_globalstat_account_id ON billservice_globalstat USING btree (account_id);



CREATE INDEX billservice_globalstat_datetime ON billservice_globalstat USING btree (datetime);



CREATE INDEX billservice_netflowstream_account_id ON billservice_netflowstream USING btree (account_id);



CREATE INDEX billservice_netflowstream_nas_id ON billservice_netflowstream USING btree (nas_id);



CREATE INDEX billservice_netflowstream_tarif_id ON billservice_netflowstream USING btree (tarif_id);



CREATE INDEX billservice_netflowstream_traffic_class_id ON billservice_netflowstream USING btree (traffic_class_id);



CREATE INDEX billservice_netflowstream_traffic_transmit_node_id ON billservice_netflowstream USING btree (traffic_transmit_node_id);



CREATE INDEX billservice_onetimeservice_tarif_id ON billservice_onetimeservice USING btree (tarif_id);



CREATE INDEX billservice_onetimeservicehistory_accounttarif_id ON billservice_onetimeservicehistory USING btree (accounttarif_id);



CREATE INDEX billservice_onetimeservicehistory_onetimeservice_id ON billservice_onetimeservicehistory USING btree (onetimeservice_id);



CREATE INDEX billservice_periodicalservice_settlement_period_id ON billservice_periodicalservice USING btree (settlement_period_id);



CREATE INDEX billservice_periodicalservice_tarif_id ON billservice_periodicalservice USING btree (tarif_id);



CREATE INDEX billservice_periodicalservicehistory_service_id ON billservice_periodicalservicehistory USING btree (service_id);



CREATE INDEX billservice_periodicalservicehistory_transaction_id ON billservice_periodicalservicehistory USING btree (transaction_id);



CREATE INDEX billservice_prepaidtraffic_traffic_transmit_service_id ON billservice_prepaidtraffic USING btree (traffic_transmit_service_id);



CREATE INDEX billservice_rawnetflowstream_nas_id ON billservice_rawnetflowstream USING btree (nas_id);



CREATE INDEX billservice_rawnetflowstream_traffic_class_id ON billservice_rawnetflowstream USING btree (traffic_class_id);



CREATE INDEX billservice_salecard_dealer_id ON billservice_salecard USING btree (dealer_id);



CREATE INDEX billservice_speedlimit_limit_id ON billservice_speedlimit USING btree (limit_id);



CREATE INDEX billservice_suspendedperiod_account_id ON billservice_suspendedperiod USING btree (account_id);



CREATE INDEX billservice_tariff_access_parameters_id ON billservice_tariff USING btree (access_parameters_id);



CREATE INDEX billservice_tariff_settlement_period_id ON billservice_tariff USING btree (settlement_period_id);



CREATE INDEX billservice_tariff_time_access_service_id ON billservice_tariff USING btree (time_access_service_id);



CREATE INDEX billservice_tariff_traffic_transmit_service_id ON billservice_tariff USING btree (traffic_transmit_service_id);



CREATE INDEX billservice_template_type_id ON billservice_template USING btree (type_id);



CREATE INDEX billservice_timeaccessnode_time_access_service_id ON billservice_timeaccessnode USING btree (time_access_service_id);



CREATE INDEX billservice_timeaccessnode_time_period_id ON billservice_timeaccessnode USING btree (time_period_id);



CREATE INDEX billservice_timespeed_access_parameters_id ON billservice_timespeed USING btree (access_parameters_id);



CREATE INDEX billservice_timespeed_time_id ON billservice_timespeed USING btree (time_id);



CREATE INDEX billservice_trafficlimit_settlement_period_id ON billservice_trafficlimit USING btree (settlement_period_id);



CREATE INDEX billservice_trafficlimit_tarif_id ON billservice_trafficlimit USING btree (tarif_id);



CREATE INDEX billservice_traffictransmitnodes_traffic_transmit_service_id ON billservice_traffictransmitnodes USING btree (traffic_transmit_service_id);



CREATE INDEX billservice_transaction_account_id ON billservice_transaction USING btree (account_id);



CREATE INDEX billservice_transaction_tarif_id ON billservice_transaction USING btree (tarif_id);



CREATE INDEX django_admin_log_content_type_id ON django_admin_log USING btree (content_type_id);



CREATE INDEX django_admin_log_user_id ON django_admin_log USING btree (user_id);



CREATE INDEX fki_billservice_card_account_fkey ON billservice_card USING btree (account_id);



CREATE INDEX fki_billservice_card_tarif_fkey ON billservice_card USING btree (tarif_id);



CREATE INDEX fki_billservice_onetimeservicehistory_transaction_id_fkey ON billservice_onetimeservicehistory USING btree (transaction_id);



CREATE INDEX fki_billservice_operator_bank_id ON billservice_operator USING btree (bank_id);



CREATE INDEX gpst20090101_account_id ON gpst20090101 USING btree (account_id);



CREATE INDEX gpst20090101_datetime_id ON gpst20090101 USING btree (datetime);



CREATE INDEX gpst20090101_gr_acc_dt_id ON gpst20090101 USING btree (group_id, account_id, datetime);



CREATE INDEX gpst20090101_group_id ON gpst20090101 USING btree (group_id);



CREATE INDEX gpst20090201_account_id ON gpst20090201 USING btree (account_id);



CREATE INDEX gpst20090201_datetime_id ON gpst20090201 USING btree (datetime);



CREATE INDEX gpst20090201_gr_acc_dt_id ON gpst20090201 USING btree (group_id, account_id, datetime);



CREATE INDEX gpst20090201_group_id ON gpst20090201 USING btree (group_id);



CREATE INDEX gpst20090301_account_id ON gpst20090301 USING btree (account_id);



CREATE INDEX gpst20090301_datetime_id ON gpst20090301 USING btree (datetime);



CREATE INDEX gpst20090301_gr_acc_dt_id ON gpst20090301 USING btree (group_id, account_id, datetime);



CREATE INDEX gpst20090301_group_id ON gpst20090301 USING btree (group_id);



CREATE INDEX nas_trafficnode_traffic_class_id ON nas_trafficnode USING btree (traffic_class_id);



CREATE INDEX nfs20081223_date_start_id ON nfs20081223 USING btree (date_start);



CREATE INDEX nfs20090105_date_start_id ON nfs20090105 USING btree (date_start);



CREATE INDEX nfs20090106_date_start_id ON nfs20090106 USING btree (date_start);



CREATE INDEX nfs20090107_date_start_id ON nfs20090107 USING btree (date_start);



CREATE INDEX nfs20090108_date_start_id ON nfs20090108 USING btree (date_start);



CREATE INDEX nfs20090109_date_start_id ON nfs20090109 USING btree (date_start);



CREATE INDEX nfs20090110_date_start_id ON nfs20090110 USING btree (date_start);



CREATE INDEX nfs20090111_date_start_id ON nfs20090111 USING btree (date_start);



CREATE INDEX nfs20090112_date_start_id ON nfs20090112 USING btree (date_start);



CREATE INDEX nfs20090113_date_start_id ON nfs20090113 USING btree (date_start);



CREATE INDEX nfs20090114_date_start_id ON nfs20090114 USING btree (date_start);



CREATE INDEX nfs20090115_date_start_id ON nfs20090115 USING btree (date_start);



CREATE INDEX nfs20090116_date_start_id ON nfs20090116 USING btree (date_start);



CREATE INDEX nfs20090117_date_start_id ON nfs20090117 USING btree (date_start);



CREATE INDEX nfs20090118_date_start_id ON nfs20090118 USING btree (date_start);



CREATE INDEX nfs20090119_date_start_id ON nfs20090119 USING btree (date_start);



CREATE INDEX nfs20090120_date_start_id ON nfs20090120 USING btree (date_start);



CREATE INDEX nfs20090122_date_start_id ON nfs20090122 USING btree (date_start);



CREATE INDEX nfs20090123_date_start_id ON nfs20090123 USING btree (date_start);



CREATE INDEX nfs20090124_date_start_id ON nfs20090124 USING btree (date_start);



CREATE INDEX nfs20090125_date_start_id ON nfs20090125 USING btree (date_start);



CREATE INDEX nfs20090126_date_start_id ON nfs20090126 USING btree (date_start);



CREATE INDEX nfs20090216_date_start_id ON nfs20090216 USING btree (date_start);



CREATE INDEX nfs20090218_date_start_id ON nfs20090218 USING btree (date_start);



CREATE INDEX nfs20090219_date_start_id ON nfs20090219 USING btree (date_start);



CREATE INDEX nfs20090220_date_start_id ON nfs20090220 USING btree (date_start);



CREATE INDEX nfs20090221_date_start_id ON nfs20090221 USING btree (date_start);



CREATE INDEX nfs20090223_date_start_id ON nfs20090223 USING btree (date_start);



CREATE INDEX nfs20090323_date_start_id ON nfs20090323 USING btree (date_start);



CREATE INDEX nfs20090324_date_start_id ON nfs20090324 USING btree (date_start);



CREATE INDEX psh20090201_datetime_id ON psh20090201 USING btree (datetime);



CREATE INDEX psh20090301_datetime_id ON psh20090301 USING btree (datetime);



CREATE INDEX radius_activesession_account_id ON radius_activesession USING btree (account_id);



CREATE INDEX rsss20081101_account_id ON rsss20081101 USING btree (account_id);



CREATE INDEX rsss20081101_interrim_update_id ON rsss20081101 USING btree (interrim_update);



CREATE INDEX tsct20081101_created_id ON tsct20081101 USING btree (created);



CREATE INDEX tsct20081201_created_id ON tsct20081201 USING btree (created);



CREATE INDEX tsct20090101_created_id ON tsct20090101 USING btree (created);



CREATE INDEX tsct20090201_created_id ON tsct20090201 USING btree (created);



CREATE INDEX tsct20090301_created_id ON tsct20090301 USING btree (created);



CREATE INDEX z_date_tmp_ed_date_idx ON z_date_tmp USING btree (ed_date);



CREATE INDEX z_date_tmp_st_date_idx ON z_date_tmp USING btree (st_date);



CREATE TRIGGER acc_trans_trg
    AFTER INSERT OR DELETE OR UPDATE ON billservice_transaction
    FOR EACH ROW
    EXECUTE PROCEDURE account_transaction_trg_fn();



CREATE TRIGGER del_nfs_trg
    AFTER DELETE ON billservice_netflowstream
    FOR EACH ROW
    EXECUTE PROCEDURE del_nfs_trg_fn();



CREATE TRIGGER gpst_del_trg
    AFTER DELETE ON billservice_groupstat
    FOR EACH ROW
    EXECUTE PROCEDURE gpst_del_trg_fn();



CREATE TRIGGER gpst_ins_trg
    BEFORE INSERT ON billservice_groupstat
    FOR EACH ROW
    EXECUTE PROCEDURE gpst_ins_trg_fn();



CREATE TRIGGER ins_account_trg
    BEFORE INSERT ON billservice_account
    FOR EACH ROW
    EXECUTE PROCEDURE check_allowed_users_trg_fn();



CREATE TRIGGER ins_nfs_trg
    BEFORE INSERT ON billservice_netflowstream
    FOR EACH ROW
    EXECUTE PROCEDURE nfs_ins_trg_fn();



CREATE TRIGGER psh_del_trg
    AFTER DELETE ON billservice_periodicalservicehistory
    FOR EACH ROW
    EXECUTE PROCEDURE psh_del_trg_fn();



CREATE TRIGGER psh_ins_trg
    BEFORE INSERT ON billservice_periodicalservicehistory
    FOR EACH ROW
    EXECUTE PROCEDURE psh_ins_trg_fn();



CREATE TRIGGER rsss_del_trg
    AFTER DELETE ON radius_session
    FOR EACH ROW
    EXECUTE PROCEDURE rsss_del_trg_fn();



CREATE TRIGGER rsss_ins_trg
    BEFORE INSERT ON radius_session
    FOR EACH ROW
    EXECUTE PROCEDURE rsss_ins_trg_fn();



CREATE TRIGGER ztm59_ins_trg
    BEFORE INSERT ON ztm59
    FOR EACH ROW
    EXECUTE PROCEDURE ztm59_ins_trg_fn();



ALTER TABLE ONLY radius_activesession
    ADD CONSTRAINT account_id_refs_id_16c70393 FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY radius_session
    ADD CONSTRAINT account_id_refs_id_600b3363 FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_accountprepaystime
    ADD CONSTRAINT account_tarif_id_refs_id_48fe22d0 FOREIGN KEY (account_tarif_id) REFERENCES billservice_accounttarif(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_accountprepaystrafic
    ADD CONSTRAINT account_tarif_id_refs_id_7d07606a FOREIGN KEY (account_tarif_id) REFERENCES billservice_accounttarif(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_fkey FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY auth_message
    ADD CONSTRAINT auth_message_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_fkey FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_accessparameters
    ADD CONSTRAINT billservice_accessparameters_access_time_id_fkey FOREIGN KEY (access_time_id) REFERENCES billservice_timeperiod(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_account
    ADD CONSTRAINT billservice_account_nas_id_fkey FOREIGN KEY (nas_id) REFERENCES nas_nas(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_accountipnspeed
    ADD CONSTRAINT billservice_accountipnspeed_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_accountprepaystime
    ADD CONSTRAINT billservice_accountprepaystime_prepaid_time_service_id_fkey FOREIGN KEY (prepaid_time_service_id) REFERENCES billservice_timeaccessservice(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_accountprepaystrafic
    ADD CONSTRAINT billservice_accountprepaystrafic_prepaid_traffic_id_fkey FOREIGN KEY (prepaid_traffic_id) REFERENCES billservice_prepaidtraffic(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_accountspeedlimit
    ADD CONSTRAINT billservice_accountspeedlimit_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;



ALTER TABLE ONLY billservice_accountspeedlimit
    ADD CONSTRAINT billservice_accountspeedlimit_speedlimit_id_fkey FOREIGN KEY (speedlimit_id) REFERENCES billservice_speedlimit(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;



ALTER TABLE ONLY billservice_accounttarif
    ADD CONSTRAINT billservice_accounttarif_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_accounttarif
    ADD CONSTRAINT billservice_accounttarif_tarif_id_fkey FOREIGN KEY (tarif_id) REFERENCES billservice_tariff(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_card
    ADD CONSTRAINT billservice_card_account_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_card
    ADD CONSTRAINT billservice_card_tarif_fkey FOREIGN KEY (tarif_id) REFERENCES billservice_tariff(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_dealer
    ADD CONSTRAINT billservice_dealer_bank_id_fkey FOREIGN KEY (bank_id) REFERENCES billservice_bankdata(id) DEFERRABLE INITIALLY DEFERRED;



ALTER TABLE ONLY billservice_dealerpay
    ADD CONSTRAINT billservice_dealerpay_dealer_id_fkey FOREIGN KEY (dealer_id) REFERENCES billservice_dealer(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_dealerpay
    ADD CONSTRAINT billservice_dealerpay_salecard_id_fkey FOREIGN KEY (salecard_id) REFERENCES billservice_salecard(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_document
    ADD CONSTRAINT billservice_document_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) DEFERRABLE INITIALLY DEFERRED;



ALTER TABLE ONLY billservice_document
    ADD CONSTRAINT billservice_document_type_id_fkey FOREIGN KEY (type_id) REFERENCES billservice_documenttype(id) DEFERRABLE INITIALLY DEFERRED;



ALTER TABLE ONLY billservice_globalstat
    ADD CONSTRAINT billservice_globalstat_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) DEFERRABLE INITIALLY DEFERRED;



ALTER TABLE ONLY billservice_group_trafficclass
    ADD CONSTRAINT billservice_group_trafficclass_group_id_fkey FOREIGN KEY (group_id) REFERENCES billservice_group(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;



ALTER TABLE ONLY billservice_group_trafficclass
    ADD CONSTRAINT billservice_group_trafficclass_trafficclass_id_fkey FOREIGN KEY (trafficclass_id) REFERENCES nas_trafficclass(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;



ALTER TABLE ONLY billservice_groupstat
    ADD CONSTRAINT billservice_groupstat_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) DEFERRABLE INITIALLY DEFERRED;



ALTER TABLE ONLY billservice_groupstat
    ADD CONSTRAINT billservice_groupstat_group_id_fkey FOREIGN KEY (group_id) REFERENCES billservice_group(id) DEFERRABLE INITIALLY DEFERRED;



ALTER TABLE ONLY billservice_netflowstream
    ADD CONSTRAINT billservice_netflowstream_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_netflowstream
    ADD CONSTRAINT billservice_netflowstream_nas_id_fkey FOREIGN KEY (nas_id) REFERENCES nas_nas(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_netflowstream
    ADD CONSTRAINT billservice_netflowstream_tarif_id_fkey FOREIGN KEY (tarif_id) REFERENCES billservice_tariff(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_netflowstream
    ADD CONSTRAINT billservice_netflowstream_traffic_transmit_node_id_fkey FOREIGN KEY (traffic_transmit_node_id) REFERENCES billservice_traffictransmitnodes(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_onetimeservice
    ADD CONSTRAINT billservice_onetimeservice_tarif_id_fkey FOREIGN KEY (tarif_id) REFERENCES billservice_tariff(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_onetimeservicehistory
    ADD CONSTRAINT billservice_onetimeservicehistory_accounttarif_id_fkey FOREIGN KEY (accounttarif_id) REFERENCES billservice_accounttarif(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_onetimeservicehistory
    ADD CONSTRAINT billservice_onetimeservicehistory_transaction_id_fkey FOREIGN KEY (transaction_id) REFERENCES billservice_transaction(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_operator
    ADD CONSTRAINT billservice_operator_bank_id FOREIGN KEY (bank_id) REFERENCES billservice_bankdata(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_organization
    ADD CONSTRAINT billservice_organization_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;



ALTER TABLE ONLY billservice_periodicalservice
    ADD CONSTRAINT billservice_periodicalservice_settlement_period_id_fkey FOREIGN KEY (settlement_period_id) REFERENCES billservice_settlementperiod(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_periodicalservice
    ADD CONSTRAINT billservice_periodicalservice_tarif_id_fkey FOREIGN KEY (tarif_id) REFERENCES billservice_tariff(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_prepaidtraffic_traffic_class
    ADD CONSTRAINT billservice_prepaidtraffic_traffic_class_prepaidtraffic_id_fkey FOREIGN KEY (prepaidtraffic_id) REFERENCES billservice_prepaidtraffic(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_prepaidtraffic_traffic_class
    ADD CONSTRAINT billservice_prepaidtraffic_traffic_class_trafficclass_id_fkey FOREIGN KEY (trafficclass_id) REFERENCES nas_trafficclass(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_rawnetflowstream
    ADD CONSTRAINT billservice_rawnetflowstream_nas_id_fkey FOREIGN KEY (nas_id) REFERENCES nas_nas(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_rawnetflowstream
    ADD CONSTRAINT billservice_rawnetflowstream_traffic_class_id_fkey FOREIGN KEY (traffic_class_id) REFERENCES nas_trafficclass(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_salecard_cards
    ADD CONSTRAINT billservice_salecard_cards_card_id_fkey FOREIGN KEY (card_id) REFERENCES billservice_card(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_salecard_cards
    ADD CONSTRAINT billservice_salecard_cards_salecard_id_fkey FOREIGN KEY (salecard_id) REFERENCES billservice_salecard(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_salecard
    ADD CONSTRAINT billservice_salecard_dealer_id_fkey FOREIGN KEY (dealer_id) REFERENCES billservice_dealer(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_shedulelog
    ADD CONSTRAINT billservice_shedulelog_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_shedulelog
    ADD CONSTRAINT billservice_shedulelog_accounttarif_id_fkey FOREIGN KEY (accounttarif_id) REFERENCES billservice_accounttarif(id) DEFERRABLE INITIALLY DEFERRED;



ALTER TABLE ONLY billservice_speedlimit
    ADD CONSTRAINT billservice_speedlimit_limit_id_fkey FOREIGN KEY (limit_id) REFERENCES billservice_trafficlimit(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;



ALTER TABLE ONLY billservice_suspendedperiod
    ADD CONSTRAINT billservice_suspendedperiod_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) DEFERRABLE INITIALLY DEFERRED;



ALTER TABLE ONLY billservice_tariff
    ADD CONSTRAINT billservice_tariff_access_parameters_id_fkey FOREIGN KEY (access_parameters_id) REFERENCES billservice_accessparameters(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_tariff
    ADD CONSTRAINT billservice_tariff_settlement_period_id_fkey FOREIGN KEY (settlement_period_id) REFERENCES billservice_settlementperiod(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_tariff
    ADD CONSTRAINT billservice_tariff_time_access_service_id_fkey FOREIGN KEY (time_access_service_id) REFERENCES billservice_timeaccessservice(id);



ALTER TABLE ONLY billservice_tariff
    ADD CONSTRAINT billservice_tariff_traffic_transmit_service_id_fkey FOREIGN KEY (traffic_transmit_service_id) REFERENCES billservice_traffictransmitservice(id);



ALTER TABLE ONLY billservice_template
    ADD CONSTRAINT billservice_template_type_id_fkey FOREIGN KEY (type_id) REFERENCES billservice_documenttype(id) DEFERRABLE INITIALLY DEFERRED;



ALTER TABLE ONLY billservice_timeaccessnode
    ADD CONSTRAINT billservice_timeaccessnode_time_access_service_id_fkey FOREIGN KEY (time_access_service_id) REFERENCES billservice_timeaccessservice(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_timeaccessnode
    ADD CONSTRAINT billservice_timeaccessnode_time_period_id_fkey FOREIGN KEY (time_period_id) REFERENCES billservice_timeperiod(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_timeperiod_time_period_nodes
    ADD CONSTRAINT billservice_timeperiod_time_period_nodes_timeperiod_id_fkey FOREIGN KEY (timeperiod_id) REFERENCES billservice_timeperiod(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_timeperiod_time_period_nodes
    ADD CONSTRAINT billservice_timeperiod_time_period_nodes_timeperiodnode_id_fkey FOREIGN KEY (timeperiodnode_id) REFERENCES billservice_timeperiodnode(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_timespeed
    ADD CONSTRAINT billservice_timespeed_access_parameters_id_fkey FOREIGN KEY (access_parameters_id) REFERENCES billservice_accessparameters(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_timespeed
    ADD CONSTRAINT billservice_timespeed_time_id_fkey FOREIGN KEY (time_id) REFERENCES billservice_timeperiod(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_trafficlimit
    ADD CONSTRAINT billservice_trafficlimit_group_id_fkey FOREIGN KEY (group_id) REFERENCES billservice_group(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_trafficlimit
    ADD CONSTRAINT billservice_trafficlimit_settlement_period_id_fkey FOREIGN KEY (settlement_period_id) REFERENCES billservice_settlementperiod(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_trafficlimit
    ADD CONSTRAINT billservice_trafficlimit_tarif_id_fkey FOREIGN KEY (tarif_id) REFERENCES billservice_tariff(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_trafficlimit_traffic_class
    ADD CONSTRAINT billservice_trafficlimit_traffic_class_trafficclass_id_fkey FOREIGN KEY (trafficclass_id) REFERENCES nas_trafficclass(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_trafficlimit_traffic_class
    ADD CONSTRAINT billservice_trafficlimit_traffic_class_trafficlimit_id_fkey FOREIGN KEY (trafficlimit_id) REFERENCES billservice_trafficlimit(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_traffictransmitnodes
    ADD CONSTRAINT billservice_traffictransmitnod_traffic_transmit_service_id_fkey FOREIGN KEY (traffic_transmit_service_id) REFERENCES billservice_traffictransmitservice(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_traffictransmitnodes_time_nodes
    ADD CONSTRAINT billservice_traffictransmitnodes__traffictransmitnodes_id_fkey1 FOREIGN KEY (traffictransmitnodes_id) REFERENCES billservice_traffictransmitnodes(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_traffictransmitnodes_group
    ADD CONSTRAINT billservice_traffictransmitnodes_group_group_id_fkey FOREIGN KEY (group_id) REFERENCES billservice_group(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_traffictransmitnodes
    ADD CONSTRAINT billservice_traffictransmitnodes_group_id_fkey FOREIGN KEY (group_id) REFERENCES billservice_group(id);



ALTER TABLE ONLY billservice_traffictransmitnodes_group
    ADD CONSTRAINT billservice_traffictransmitnodes_group_traffictransmitnodes_id_ FOREIGN KEY (traffictransmitnodes_id) REFERENCES billservice_traffictransmitnodes(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_traffictransmitnodes_traffic_class
    ADD CONSTRAINT billservice_traffictransmitnodes_t_traffictransmitnodes_id_fkey FOREIGN KEY (traffictransmitnodes_id) REFERENCES billservice_traffictransmitnodes(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_traffictransmitnodes_time_nodes
    ADD CONSTRAINT billservice_traffictransmitnodes_time_nodes_timeperiod_id_fkey FOREIGN KEY (timeperiod_id) REFERENCES billservice_timeperiod(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_traffictransmitnodes_traffic_class
    ADD CONSTRAINT billservice_traffictransmitnodes_traffic_c_trafficclass_id_fkey FOREIGN KEY (trafficclass_id) REFERENCES nas_trafficclass(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_transaction
    ADD CONSTRAINT billservice_transaction_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_transaction
    ADD CONSTRAINT billservice_transaction_tarif_id_fkey FOREIGN KEY (tarif_id) REFERENCES billservice_tariff(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT content_type_id_refs_id_728de91f FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_fkey FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY nas_trafficnode
    ADD CONSTRAINT nas_trafficnode_traffic_class_id_fkey FOREIGN KEY (traffic_class_id) REFERENCES nas_trafficclass(id) ON DELETE CASCADE DEFERRABLE;



ALTER TABLE ONLY billservice_prepaidtraffic
    ADD CONSTRAINT traffic_transmit_service_id_refs_id_4797c3b9 FOREIGN KEY (traffic_transmit_service_id) REFERENCES billservice_traffictransmitservice(id) ON DELETE CASCADE DEFERRABLE;



REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;



