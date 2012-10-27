ALTER TABLE billservice_periodicalservicelog ADD COLUMN last_billed boolean;
ALTER TABLE billservice_periodicalservicelog ALTER COLUMN last_billed SET DEFAULT false;
UPDATE billservice_periodicalservicelog as pl SET last_billed=(SELECT periodical_billed FROM billservice_accounttarif where id=pl.accounttarif_id);