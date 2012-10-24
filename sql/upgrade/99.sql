ALTER TABLE billservice_account ADD COLUMN promise_summ integer;
ALTER TABLE billservice_account ALTER COLUMN promise_summ SET DEFAULT 0;

ALTER TABLE billservice_account ADD COLUMN allow_block_after_summ boolean;
ALTER TABLE billservice_account ADD COLUMN block_after_summ integer;
ALTER TABLE billservice_account ALTER COLUMN block_after_summ SET DEFAULT 0;
ALTER TABLE billservice_account ADD COLUMN promise_days integer;
ALTER TABLE billservice_account ALTER COLUMN promise_days SET DEFAULT 0;
ALTER TABLE billservice_account ADD COLUMN promise_min_ballance integer;
ALTER TABLE billservice_account ALTER COLUMN promise_min_ballance SET DEFAULT 0;
