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
    SELECT id, salecard_id, activated, activated_by_id, nominal, tarif_id, (SELECT access_type FROM billservice_accessparameters WHERE id=(SELECT access_parameters_id FROM billservice_tariff WHERE id=card.tarif_id)) as access_type, pin, ippool_id INTO card_data_ FROM billservice_card as card WHERE type=1 and "login"=login_ and salecard_id is not Null and now() between start_date and end_date;
    -- Если карты нету - return
    IF (card_data_ is NULL) THEN
    RETURN tmp;
    --["HotSpot", 'HotSpotIp+Mac', 'HotSpotIp+Password','HotSpotMac','HotSpotMac+Password']
    
    -- Если карта уже продана, но ещё не активирвоана
    ELSIF card_data_.activated_by_id IS NULL and card_data_.salecard_id is not NULL and card_data_.pin=pin_ THEN
    -- Создаём пользователя
        INSERT INTO billservice_account(username, password, ipn_status, status, created, ipn_added, allow_webcab, allow_expresscards, assign_dhcp_null, assign_dhcp_block, allow_vpn_null, allow_vpn_block)
        VALUES(login_, encrypt_pw(pin_, 'ebscryptkeytest'), False, 1, now(), False, True, True, False, False, False, False) RETURNING id INTO account_id_;
      IF card_data_.access_type='HotSpot' THEN
          INSERT INTO billservice_subaccount(
         account_id, username, password,
         ipn_added, ipn_enabled, need_resync,
         speed, allow_addonservice,ipv4_vpn_pool_id)
          VALUES (account_id_, login_, encrypt_pw(pin_, 'ebscryptkeytest'),
         False, False, False, '', True, card_data_.ippool_id) RETURNING id INTO subaccount_id_;
      ELSIF card_data_.access_type='HotSpotIp+Mac' THEN
          INSERT INTO billservice_subaccount(
         account_id, username, password,
         ipn_added, ipn_enabled, need_resync,
         speed, allow_addonservice, ipn_ip_address, ipn_mac_address, ipv4_vpn_pool_id)
          VALUES (account_id_, '', encrypt_pw('', 'ebscryptkeytest'),
         False, False, False, '', True,  account_ip_, account_mac_, card_data_.ippool_id) RETURNING id INTO subaccount_id_;
      ELSIF card_data_.access_type='HotSpotIp+Password' THEN
          INSERT INTO billservice_subaccount(
         account_id, username, password,
         ipn_added, ipn_enabled, need_resync,
         speed, allow_addonservice, ipn_ip_address, ipv4_vpn_pool_id)
          VALUES (account_id_, '', encrypt_pw(pin_, 'ebscryptkeytest'),
         False, False, False, '', True,  account_ip_, card_data_.ippool_id) RETURNING id INTO subaccount_id_;
      ELSIF card_data_.access_type='HotSpotMac' THEN
          INSERT INTO billservice_subaccount(
         account_id, username, password,
         ipn_added, ipn_enabled, need_resync,
         speed, allow_addonservice, ipn_mac_address, ipv4_vpn_pool_id)
          VALUES (account_id_, '', encrypt_pw('', 'ebscryptkeytest'),
         False, False, False, '', True, account_mac_, card_data_.ippool_id) RETURNING id INTO subaccount_id_;
      ELSIF card_data_.access_type='HotSpotMac+Password' THEN
          INSERT INTO billservice_subaccount(
         account_id, username, password, 
         ipn_added, ipn_enabled, need_resync,
         speed, allow_addonservice, ipn_mac_address, ipv4_vpn_pool_id)
          VALUES (account_id_, '', encrypt_pw(pin_, 'ebscryptkeytest'),
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
    SELECT account.id, subaccount.id, decrypt_pw(subaccount.password, 'ebscryptkeytest'), subaccount.nas_id, tariff.id,  account.status,
    account.balance_blocked, (account.ballance+account.credit) as ballance, account.disabled_by_limit,
    tariff.active, subaccount.ipv4_vpn_pool_id,tariff.vpn_ippool_id,subaccount.vpn_ip_address,subaccount.ipn_ip_address,subaccount.ipn_mac_address::text,(SELECT access_type FROM billservice_accessparameters WHERE id=(SELECT access_parameters_id FROM billservice_tariff WHERE id=card_data_.tarif_id))::text as access_type INTO account_data_ 
    FROM billservice_subaccount as subaccount
    JOIN billservice_account as account ON account.id=subaccount.account_id
    JOIN billservice_tariff as tariff on tariff.id=card_data_.tarif_id
    WHERE  subaccount.id=subaccount_id_;
    RETURN account_data_;
    -- Если карта продана и уже активирована
    ELSIF (card_data_.salecard_id is not Null) AND (card_data_.activated_by_id is not Null) THEN
    SELECT account.id, subaccount.id as subaccount_id, decrypt_pw(subaccount.password, 'ebscryptkeytest'), subaccount.nas_id, tariff.id,  account.status,
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
  OWNER TO ebs;