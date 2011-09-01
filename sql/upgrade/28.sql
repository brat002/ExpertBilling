ALTER TABLE billservice_tariff
   DROP COLUMN userblock_require_balance;

ALTER TABLE billservice_tariff
   ADD COLUMN userblock_require_balance numeric DEFAULT 0;

update billservice_tariff set userblock_require_balance=0;