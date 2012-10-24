ALTER TABLE billservice_account DROP COLUMN IF EXISTS last_balance_null;
DROP TRIGGER IF EXISTS last_balance_null_trg ON billservice_account;
