ALTER TABLE billservice_tariff
   ADD COLUMN allow_userblock boolean DEFAULT False;

update billservice_tariff SET userblock=False;

ALTER TABLE billservice_tariff
   ADD COLUMN userblock_cost numeric DEFAULT 0;

update billservice_tariff SET userblock_cost=0;

ALTER TABLE billservice_tariff
   ADD COLUMN userblock_require_balance boolean DEFAULT False;

update billservice_tariff SET userblock_require_balance=False;

ALTER TABLE billservice_tariff
   ADD COLUMN userblock_max_days integer DEFAULT 0;

update billservice_tariff SET userblock_max_days=0;


ALTER TABLE billservice_tariff
   ADD COLUMN allow_ballance_transfer boolean DEFAULT False;

update billservice_tariff SET allow_ballance_transfer=False;
