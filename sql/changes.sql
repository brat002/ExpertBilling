--06.04.2009
ALTER TABLE billservice_shedulelog
DROP CONSTRAINT billservice_shedulelog_accounttarif_id_fkey;

ALTER TABLE billservice_shedulelog
ADD CONSTRAINT billservice_shedulelog_accounttarif_id_fkey FOREIGN KEY (accounttarif_id)
REFERENCES billservice_accounttarif (id) MATCH SIMPLE
ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;


ALTER TABLE billservice_shedulelog
DROP CONSTRAINT billservice_shedulelog_account_id_fkey

ALTER TABLE billservice_shedulelog
ADD CONSTRAINT billservice_shedulelog_account_id_fkey FOREIGN KEY (account_id)
REFERENCES billservice_account (id) MATCH SIMPLE
ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE;
