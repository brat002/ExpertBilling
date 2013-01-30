DROP INDEX IF EXISTS billservice_account_ipn_ip_address;
DROP INDEX IF EXISTS billservice_account_nas_id;
DROP INDEX IF EXISTS billservice_account_vpn_ip_address;
DROP INDEX IF EXISTS fki_billservice_account_ipnipinuse_fkey;
DROP INDEX IF EXISTS fki_billservice_account_vpnipinuse_fkey;
CREATE INDEX billservice_account_username_idx
   ON billservice_account USING btree (username ASC NULLS LAST);


CREATE INDEX billservice_account_fullname_idx
   ON billservice_account USING btree (fullname ASC NULLS LAST);
   
CREATE INDEX billservice_account_contactperson_idx
   ON billservice_account USING btree (contactperson ASC NULLS LAST);
   
CREATE INDEX billservice_account_contract_idx
   ON billservice_account USING btree (contract ASC NULLS LAST);
   
CREATE INDEX billservice_permission_name_app_idx
   ON billservice_permission (internal_name ASC NULLS LAST, name ASC NULLS LAST);
CREATE INDEX billservice_card_series_idx
   ON billservice_card (series ASC NULLS LAST);
   

CREATE INDEX billservice_card_series_idx
  ON billservice_card
  USING btree
  (series COLLATE pg_catalog."default" );