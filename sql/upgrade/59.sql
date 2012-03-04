DROP TABLE IF EXISTS billservice_periodicalservicelog;
CREATE TABLE "billservice_periodicalservicelog" (
    "id" serial NOT NULL PRIMARY KEY,
    "service_id" integer NOT NULL,
    "accounttarif_id" integer NOT NULL,
    "datetime" timestamp without time zone NOT NULL
);
CREATE INDEX "billservice_periodicalservicelog_service_id" ON "billservice_periodicalservicelog" ("service_id");
CREATE INDEX "billservice_periodicalservicelog_accounttarif_id" ON "billservice_periodicalservicelog" ("accounttarif_id");

CREATE OR REPLACE FUNCTION periodicaltr_fn(ps_id_ integer, acctf_id_ integer, account_id_ integer, type_id_ character varying, summ_ numeric, created_ timestamp without time zone, ps_condition_type_ integer)
  RETURNS numeric AS
$BODY$
DECLARE
    new_summ_ decimal;
    pslog_id integer;
BEGIN
    SELECT  summ_*(NOT EXISTS (SELECT id FROM billservice_suspendedperiod WHERE account_id=account_id_ AND (created_ BETWEEN start_date AND end_date)))::int INTO new_summ_;
    IF (ps_condition_type_ = 1) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance+credit >= 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    ELSIF (ps_condition_type_ = 2) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance+credit < 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    ELSIF (ps_condition_type_ = 3) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance+credit > 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    END IF; 
    IF (new_summ_<>0) THEN 
      INSERT INTO billservice_periodicalservicehistory (service_id, accounttarif_id,account_id, type_id, summ, datetime) VALUES (ps_id_, acctf_id_, account_id_, type_id_, new_summ_, created_);
    END IF;
    SELECT  id INTO pslog_id FROM billservice_periodicalservicelog WHERE service_id=ps_id_ and accounttarif_id=acctf_id_;
    IF (pslog_id is Null) THEN
      INSERT INTO billservice_periodicalservicelog(service_id, accounttarif_id, datetime) VALUES(ps_id_, acctf_id_, created_);
    ELSE
      UPDATE billservice_periodicalservicelog SET datetime=created_ WHERE id=pslog_id;  
    END IF;
    RETURN  new_summ_;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

INSERT INTO billservice_periodicalservicelog(service_id, accounttarif_id, datetime) SELECT service_id,accounttarif_id,max(created) FROM billservice_periodicalservicehistory GROUP BY service_id,accounttarif_id;

ALTER TABLE billservice_radiustraffic ALTER prepaid_value TYPE numeric;
