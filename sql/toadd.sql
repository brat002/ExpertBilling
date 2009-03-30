CREATE OR REPLACE FUNCTION account_transaction_trg_fn() RETURNS trigger
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
        RETURN NULL;
    END;
$$
    LANGUAGE plpgsql;
    
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
    
    
CREATE OR REPLACE FUNCTION free_unused_account_ip_trg_fn() RETURNS trigger
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


CREATE OR REPLACE FUNCTION free_unused_card_ip_trg_fn() RETURNS trigger
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


CREATE OR REPLACE FUNCTION get_cur_acct(dateat timestamp without time zone) RETURNS integer[]
    AS $$
BEGIN
RETURN ARRAY(SELECT max(id) FROM billservice_accounttarif GROUP BY account_id HAVING account_id IN (SELECT id FROM billservice_account) AND MAX(datetime) <= dateAT);
END;
$$
    LANGUAGE plpgsql;

ALTER TABLE billservice_periodicalservicehistory ALTER COLUMN transaction_id DROP NOT NULL;
ALTER TABLE billservice_periodicalservicehistory ALTER COLUMN accounttarif_id DROP NOT NULL;


ALTER TABLE billservice_card ADD COLUMN template_id int;
ALTER TABLE billservice_card ADD COLUMN nas_id int;
ALTER TABLE billservice_card ADD COLUMN ip character varying;
ALTER TABLE billservice_card ADD COLUMN ipinuse_id int;

ALTER TABLE billservice_periodicalservice ALTER COLUMN condition DROP NOT NULL;

ALTER TABLE billservice_prepaidtraffic ADD COLUMN group_id int NOT NULL;
--ALTER TABLE billservice_prepaidtraffic DROP COLUMN in_direction;
--ALTER TABLE billservice_prepaidtraffic DROP COLUMN out_direction;
--ALTER TABLE billservice_prepaidtraffic DROP COLUMN transit_direction;