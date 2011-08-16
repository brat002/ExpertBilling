ALTER TABLE billservice_tariff
   ADD COLUMN vpn_ippool_id integer;
ALTER TABLE billservice_tariff ADD CONSTRAINT billservice_tariff_vpn_ippool_id_fkey FOREIGN KEY (vpn_ippool_id) REFERENCES billservice_ippool (id)
   ON UPDATE NO ACTION ON DELETE CASCADE;
CREATE INDEX fki_billservice_tariff_vpn_ippool_id_fkey ON billservice_tariff(vpn_ippool_id);


