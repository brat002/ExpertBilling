ALTER TABLE billservice_balancehistory
  DROP CONSTRAINT billservice_balancehistory_account_id_fkey;

ALTER TABLE billservice_balancehistory
  ADD CONSTRAINT billservice_balancehistory_account_id_fkey FOREIGN KEY (account_id)
      REFERENCES billservice_account (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;

