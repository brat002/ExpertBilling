ALTER TABLE radius_activesession ALTER nas_port_id TYPE numeric;

CREATE OR REPLACE FUNCTION card_activate_fn(login_ character varying, pin_ character varying, account_ip_ inet)
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
    -- �������� ���������� � ��������, ������� ������� � � ������� �� ���� ���� ��������
    SELECT id, sold, activated, activated_by_id, nominal, tarif_id, pin, ippool_id INTO card_data_ FROM billservice_card WHERE type=1 and "login"=login_ and sold is not Null and now() between start_date and end_date;
    -- ���� ����� ���� - return
    IF (card_data_ is NULL) THEN
    RETURN tmp;

    -- ���� ����� ��� �������, �� ��� �� ������������
    ELSIF card_data_.activated_by_id IS NULL and card_data_.sold is not NULL and card_data_.pin=pin_ THEN
    -- ������ ������������
        INSERT INTO billservice_account(username, "password", ipn_status, status, created, ipn_added, allow_webcab, allow_expresscards, assign_dhcp_null, assign_dhcp_block, allow_vpn_null, allow_vpn_block)
        VALUES(login_, pin_, False, 1, now(), False, True, True, False, False, False, False) RETURNING id INTO account_id_;
    INSERT INTO billservice_subaccount(
             account_id, username, "password", 
            ipn_added, ipn_enabled, need_resync, 
            speed, allow_addonservice,ipv4_vpn_pool_id)
    VALUES (account_id_, login_, pin_, 
            False, False, False, '', True, card_data_.ippool_id) RETURNING id INTO subaccount_id_;

    -- ���������� ������������ �����
        INSERT INTO billservice_accounttarif(account_id, tarif_id, datetime) VALUES(account_id_, card_data_.tarif_id, now());
        -- ��������� ����
        INSERT INTO billservice_transaction(bill, account_id, type_id, approved, tarif_id, summ, description, created)
        VALUES('����� �������', account_id_, 'ACCESS_CARD', True, card_data_.tarif_id, card_data_.nominal*(-1),'', now());
    -- ��������� ���������� � ��������
    UPDATE billservice_card SET activated = now(), activated_by_id = account_id_ WHERE id = card_data_.id;

    -- �������� ������ ����������
    SELECT account.id, subaccount.id, subaccount.password, subaccount.nas_id, bsat.tarif_id,  account.status, 
    account.balance_blocked, (account.ballance+account.credit) as ballance, account.disabled_by_limit, 
    tariff.active, subaccount.ipv4_vpn_pool_id,tariff.vpn_ippool_id,subaccount.vpn_ip_address INTO account_data_ 
    FROM billservice_subaccount as subaccount
    JOIN billservice_account as account ON account.id=subaccount.account_id
    JOIN billservice_accounttarif as bsat ON bsat.id=(SELECT id FROM billservice_accounttarif as acct WHERE acct.account_id=account.id and acct.datetime<=now() ORDER BY acct.datetime DESC LIMIT 1)
    JOIN billservice_tariff as tariff on tariff.id=bsat.tarif_id
    WHERE  subaccount.id=subaccount_id_;
    RETURN account_data_;
    -- ���� ����� ������� � ��� ������������
    ELSIF (card_data_.sold is not Null) AND (card_data_.activated_by_id is not Null) THEN
    SELECT account.id, subaccount.id as subaccount_id, subaccount.password, subaccount.nas_id, bsat.tarif_id,  account.status, 
    account.balance_blocked, (account.ballance+account.credit) as ballance, account.disabled_by_limit, 
    tariff.active, subaccount.ipv4_vpn_pool_id,tariff.vpn_ippool_id,subaccount.vpn_ip_address INTO account_data_
    FROM billservice_subaccount as subaccount
    JOIN billservice_account as account ON account.id=subaccount.account_id and account.id=card_data_.activated_by_id
    JOIN billservice_accounttarif as bsat ON bsat.id=(SELECT id FROM billservice_accounttarif as acct WHERE acct.account_id=account.id and acct.datetime<=now() ORDER BY acct.datetime DESC LIMIT 1)
    JOIN billservice_tariff as tariff on tariff.id=bsat.tarif_id
    WHERE subaccount.username=login_;
    UPDATE billservice_subaccount SET ipn_ip_address = account_ip_ WHERE id=account_data_.subaccount_id;
        RETURN account_data_;
    END IF; 

    RETURN tmp;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION card_activate_fn(character varying, character varying, inet) OWNER TO postgres;
