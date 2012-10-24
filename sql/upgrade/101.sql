COMMIT;

CREATE OR REPLACE FUNCTION account_transaction_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN
return NEW;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION account_transaction_trg_fn()
  OWNER TO ebs;
  
UPDATE billservice_transaction SET summ=(-1)*summ;
UPDATE billservice_traffictransaction SET summ=(-1)*summ;
UPDATE billservice_timetransaction SET summ=(-1)*summ;
UPDATE billservice_addonservicetransaction SET summ=(-1)*summ;
UPDATE billservice_periodicalservicehistory SET summ=(-1)*summ;



CREATE OR REPLACE FUNCTION account_transaction_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN

IF (TG_OP = 'INSERT') THEN
UPDATE billservice_account SET ballance=COALESCE(ballance, 0)+NEW.summ WHERE id=NEW.account_id;
RETURN NEW;
ELSIF (TG_OP = 'DELETE') THEN
UPDATE billservice_account SET ballance=COALESCE(ballance, 0)-OLD.summ WHERE id=OLD.account_id;
RETURN OLD;
ELSIF (TG_OP = 'UPDATE') THEN
UPDATE billservice_account SET ballance=COALESCE(ballance, 0)-OLD.summ WHERE id=OLD.account_id;
UPDATE billservice_account SET ballance=COALESCE(ballance, 0)+NEW.summ WHERE id=NEW.account_id;
RETURN NEW;
END IF;
RETURN NULL;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION account_transaction_trg_fn()
  OWNER TO ebs;
DROP FUNCTION card_activate_fn(character varying, character varying, integer, inet);

-- Function: card_activate_fn(character varying, character varying, inet, text)

-- DROP FUNCTION card_activate_fn(character varying, character varying, inet, text);

CREATE OR REPLACE FUNCTION card_activate_fn(login_ character varying, pin_ character varying, account_ip_ inet, account_mac_ text)
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
    SELECT id, sold, activated, activated_by_id, nominal, tarif_id, (SELECT access_type FROM billservice_accessparameters WHERE id=(SELECT access_parameters_id FROM billservice_tariff WHERE id=card.tarif_id)) as access_type, pin, ippool_id INTO card_data_ FROM billservice_card as card WHERE type=1 and "login"=login_ and sold is not Null and now() between start_date and end_date;
    -- Если карты нету - return
    IF (card_data_ is NULL) THEN
    RETURN tmp;
    --["HotSpot", 'HotSpotIp+Mac', 'HotSpotIp+Password','HotSpotMac','HotSpotMac+Password']
    
    -- Если карта уже продана, но ещё не активирвоана
    ELSIF card_data_.activated_by_id IS NULL and card_data_.sold is not NULL and card_data_.pin=pin_ THEN
    -- Создаём пользователя
        INSERT INTO billservice_account(username, "password", ipn_status, status, created, ipn_added, allow_webcab, allow_expresscards, assign_dhcp_null, assign_dhcp_block, allow_vpn_null, allow_vpn_block)
        VALUES(login_, pin_, False, 1, now(), False, True, True, False, False, False, False) RETURNING id INTO account_id_;
      IF card_data_.access_type='HotSpot' THEN
          INSERT INTO billservice_subaccount(
         account_id, username, "password",
         ipn_added, ipn_enabled, need_resync,
         speed, allow_addonservice,ipv4_vpn_pool_id)
          VALUES (account_id_, login_, pin_,
         False, False, False, '', True, card_data_.ippool_id) RETURNING id INTO subaccount_id_;
      ELSIF card_data_.access_type='HotSpotIp+Mac' THEN
          INSERT INTO billservice_subaccount(
         account_id, username, "password",
         ipn_added, ipn_enabled, need_resync,
         speed, allow_addonservice, ipn_ip_address, ipn_mac_address, ipv4_vpn_pool_id)
          VALUES (account_id_, '', '',
         False, False, False, '', True,  account_ip_, account_mac_, card_data_.ippool_id) RETURNING id INTO subaccount_id_;
      ELSIF card_data_.access_type='HotSpotIp+Password' THEN
          INSERT INTO billservice_subaccount(
         account_id, username, "password",
         ipn_added, ipn_enabled, need_resync,
         speed, allow_addonservice, ipn_ip_address, ipv4_vpn_pool_id)
          VALUES (account_id_, '', pin,
         False, False, False, '', True,  account_ip_, card_data_.ippool_id) RETURNING id INTO subaccount_id_;
      ELSIF card_data_.access_type='HotSpotMac' THEN
          INSERT INTO billservice_subaccount(
         account_id, username, "password",
         ipn_added, ipn_enabled, need_resync,
         speed, allow_addonservice, ipn_mac_address, ipv4_vpn_pool_id)
          VALUES (account_id_, '', '',
         False, False, False, '', True, account_mac_, card_data_.ippool_id) RETURNING id INTO subaccount_id_;
      ELSIF card_data_.access_type='HotSpotMac+Password' THEN
          INSERT INTO billservice_subaccount(
         account_id, username, "password",
         ipn_added, ipn_enabled, need_resync,
         speed, allow_addonservice, ipn_mac_address, ipv4_vpn_pool_id)
          VALUES (account_id_, '', pin,
         False, False, False, '', True,  account_mac_, card_data_.ippool_id) RETURNING id INTO subaccount_id_;
      END IF;  

    -- Добавлеяем пользователю тариф
        INSERT INTO billservice_accounttarif(account_id, tarif_id, datetime) VALUES(account_id_, card_data_.tarif_id, now());
        -- Пополняем счёт
        INSERT INTO billservice_transaction(bill, account_id, type_id, approved, tarif_id, summ, description, created)
        VALUES('HotSpot карта #'||card_data_.id, account_id_, 'HOTSPOT_CARD', True, card_data_.tarif_id, card_data_.nominal,'', now());
    -- Обновляем информацию о карточке
    UPDATE billservice_card SET activated = now(), activated_by_id = account_id_ WHERE id = card_data_.id;

    -- Выбираем нужную информацию
    SELECT account.id, subaccount.id, subaccount.password, subaccount.nas_id, tariff.id,  account.status,
    account.balance_blocked, (account.ballance+account.credit) as ballance, account.disabled_by_limit,
    tariff.active, subaccount.ipv4_vpn_pool_id,tariff.vpn_ippool_id,subaccount.vpn_ip_address,subaccount.ipn_ip_address,subaccount.ipn_mac_address::text,(SELECT access_type FROM billservice_accessparameters WHERE id=(SELECT access_parameters_id FROM billservice_tariff WHERE id=card_data_.tarif_id))::text as access_type INTO account_data_
    FROM billservice_subaccount as subaccount
    JOIN billservice_account as account ON account.id=subaccount.account_id
    JOIN billservice_tariff as tariff on tariff.id=card_data_.tarif_id
    WHERE  subaccount.id=subaccount_id_;
    RETURN account_data_;
    -- Если карта продана и уже активирована
    ELSIF (card_data_.sold is not Null) AND (card_data_.activated_by_id is not Null) THEN
    SELECT account.id, subaccount.id as subaccount_id, subaccount.password, subaccount.nas_id, tariff.id,  account.status,
    account.balance_blocked, (account.ballance+account.credit) as ballance, account.disabled_by_limit,
    tariff.active, subaccount.ipv4_vpn_pool_id,tariff.vpn_ippool_id,subaccount.vpn_ip_address, subaccount.ipn_ip_address,subaccount.ipn_mac_address::text,(SELECT access_type FROM billservice_accessparameters WHERE id=(SELECT access_parameters_id FROM billservice_tariff WHERE id=card_data_.tarif_id))::text as access_type INTO account_data_
    FROM billservice_subaccount as subaccount
    JOIN billservice_account as account ON account.id=subaccount.account_id and account.id=card_data_.activated_by_id
    JOIN billservice_tariff as tariff on tariff.id=card_data_.tarif_id
    WHERE subaccount.username=login_;
        RETURN account_data_;
    END IF;

    RETURN tmp;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION card_activate_fn(character varying, character varying, inet, text)
  OWNER TO postgres;

DROP FUNCTION credit_account(integer, numeric);
DROP FUNCTION debit_account(integer, numeric);
DROP FUNCTION get_tariff_type(integer);
DROP FUNCTION on_tariff_delete_fun(billservice_tariff);
CREATE OR REPLACE FUNCTION periodicaltr_fn(ps_id_ integer, acctf_id_ integer, account_id_ integer, type_id_ character varying, summ_ numeric, created_ timestamp without time zone, ps_condition_type_ integer)
  RETURNS numeric AS
$BODY$
DECLARE
    new_summ_ decimal;
    pslog_id integer;
BEGIN
    SELECT INTO new_summ_ summ_*(NOT EXISTS (SELECT id FROM billservice_suspendedperiod WHERE account_id=account_id_ AND (created_ BETWEEN start_date AND end_date)))::int;
    IF (ps_condition_type_ = 1) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(COALESCE((SELECT balance FROM billservice_balancehistory WHERE account_id=account_id_ and datetime<_created ORDER BY datetime DESC LIMIT 1),0)+credit >= 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    ELSIF (ps_condition_type_ = 2) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(COALESCE((SELECT balance FROM billservice_balancehistory WHERE account_id=account_id_ and datetime<_created ORDER BY datetime DESC LIMIT 1),0)+credit < 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    ELSIF (ps_condition_type_ = 3) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(COALESCE((SELECT balance FROM billservice_balancehistory WHERE account_id=account_id_ and datetime<_created ORDER BY datetime DESC LIMIT 1),0)+credit > 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    END IF; 
    IF (new_summ_<>0) THEN 
      INSERT INTO billservice_periodicalservicehistory (service_id, accounttarif_id,account_id, type_id, summ, created) VALUES (ps_id_, acctf_id_, account_id_, type_id_, (-1)*new_summ_, created_);
    END IF;
    SELECT  id FROM billservice_periodicalservicelog WHERE service_id=ps_id_ and accounttarif_id=acctf_id_ INTO pslog_id;
    IF (pslog_id is Null) THEN
      INSERT INTO billservice_periodicalservicelog(service_id, accounttarif_id, datetime) VALUES(ps_id_, acctf_id_, created_);
    ELSE
      UPDATE billservice_periodicalservicelog SET datetime=created_ WHERE id=pslog_id;  
    END IF;
    RETURN  new_summ_;
    
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION periodicaltr_fn(integer, integer, integer, character varying, numeric, timestamp without time zone, integer)
  OWNER TO ebs;


CREATE OR REPLACE FUNCTION transaction_block_sum(account_id_ integer, start_date_ timestamp without time zone, end_date_ timestamp without time zone)
  RETURNS numeric AS
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
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION transaction_block_sum(integer, timestamp without time zone, timestamp without time zone)
  OWNER TO ebs;


COMMIT;
