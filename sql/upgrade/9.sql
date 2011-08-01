ALTER TABLE billservice_subaccount ADD COLUMN vlan integer;
ALTER TABLE billservice_subaccount ALTER COLUMN vlan SET DEFAULT 0;

ALTER TABLE billservice_subaccount ADD COLUMN vpn_ipv6_ip_address inet;
ALTER TABLE billservice_subaccount ALTER COLUMN vpn_ipv6_ip_address SET DEFAULT '::'::inet;

ALTER TABLE billservice_subaccount ADD COLUMN ipn_ipv6_ip_address inet;
ALTER TABLE billservice_subaccount ALTER COLUMN ipn_ipv6_ip_address SET DEFAULT '::'::inet;

ALTER TABLE billservice_subaccount ADD COLUMN vpn_ipv6_ipinuse_id integer;

ALTER TABLE billservice_subaccount ADD COLUMN allow_mac_update boolean;
ALTER TABLE billservice_subaccount ALTER COLUMN allow_mac_update SET DEFAULT false;

ALTER TABLE billservice_accountprepaystrafic ADD COLUMN "current" boolean;
ALTER TABLE billservice_accountprepaystrafic ALTER COLUMN "current" SET DEFAULT false;

ALTER TABLE billservice_accountprepaysradiustrafic ADD COLUMN "current" boolean;
ALTER TABLE billservice_accountprepaysradiustrafic ALTER COLUMN "current" SET DEFAULT false;

ALTER TABLE billservice_accountprepaysradiustrafic ADD COLUMN reseted boolean;
ALTER TABLE billservice_accountprepaysradiustrafic ALTER COLUMN reseted SET DEFAULT false;

ALTER TABLE billservice_accountprepaystrafic ADD COLUMN reseted boolean;
ALTER TABLE billservice_accountprepaystrafic ALTER COLUMN reseted SET DEFAULT false;

ALTER TABLE billservice_accountprepaystime ADD COLUMN reseted boolean;
ALTER TABLE billservice_accountprepaystime ALTER COLUMN reseted SET DEFAULT false;


