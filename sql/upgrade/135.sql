DROP INDEX IF EXISTS radius_activesession_account_id;
ALTER TABLE radius_activesession DROP CONSTRAINT IF EXISTS radius_activesession_pkey;
CREATE INDEX billservice_subaccount_id_idx
  ON billservice_subaccount
  USING btree
  (id );