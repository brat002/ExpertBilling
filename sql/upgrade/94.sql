CREATE INDEX CONCURRENTLY billservice_balancehistory_account_id_idx
   ON billservice_balancehistory (account_id ASC NULLS LAST);
CREATE INDEX CONCURRENTLY billservice_balancehistory_datetime
   ON billservice_balancehistory (datetime ASC NULLS LAST);
   
CREATE INDEX CONCURRENTLY radius_authlog_account_id
   ON radius_authlog (account_id ASC NULLS LAST);


CREATE INDEX CONCURRENTLY radius_authlog_datetime_idx
   ON radius_authlog (datetime ASC NULLS LAST);
   
