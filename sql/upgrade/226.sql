CREATE TABLE "billservice_bonustransaction" (
    "id" serial NOT NULL PRIMARY KEY,
    "bill" varchar(255) NOT NULL,
    "account_id" integer NOT NULL REFERENCES "billservice_account" ("id") DEFERRABLE INITIALLY DEFERRED,
    "type_id" varchar(32) REFERENCES "billservice_transactiontype" ("internal_name") DEFERRABLE INITIALLY DEFERRED,
    "summ" numeric(20, 10) NOT NULL,
    "prev_balance" numeric(20, 5) NOT NULL,
    "description" text NOT NULL,
    "created" timestamp with time zone NOT NULL,
    "systemuser_id" integer
)
;
ALTER TABLE billservice_account ADD COLUMN bonus_ballance numeric;
ALTER TABLE billservice_account ALTER COLUMN bonus_ballance SET DEFAULT 0;

update billservice_account SET  bonus_ballance=0;

ALTER TABLE billservice_transactiontype ADD COLUMN is_bonus boolean;
ALTER TABLE billservice_transactiontype ALTER COLUMN is_bonus SET DEFAULT False;

UPDATE billservice_transactiontype SET is_bonus=False;

DELETE FROM ebsadmin_tablesettings WHERE name='TransactionTypeTable';

ALTER TABLE billservice_transaction ADD COLUMN is_bonus boolean;


CREATE OR REPLACE FUNCTION account_bonus_transaction_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN



IF (TG_OP = 'INSERT') THEN
SELECT INTO NEW.prev_balance  COALESCE(ballance, 0) FROM billservice_account WHERE id=NEW.account_id;
UPDATE billservice_account SET ballance=COALESCE(ballance, 0)+NEW.summ, bonus_ballance=COALESCE(bonus_ballance, 0)+NEW.summ WHERE id=NEW.account_id;

RETURN NEW;
ELSIF (TG_OP = 'DELETE') THEN
UPDATE billservice_account SET ballance=COALESCE(ballance, 0)-OLD.summ, bonus_ballance=COALESCE(bonus_ballance, 0)-OLD.summ WHERE id=OLD.account_id;
RETURN OLD;
ELSIF (TG_OP = 'UPDATE') THEN
SELECT INTO NEW.prev_balance  COALESCE(ballance, 0) FROM billservice_account WHERE id=NEW.account_id;
UPDATE billservice_account SET ballance=COALESCE(ballance, 0)-OLD.summ, bonus_ballance=COALESCE(bonus_ballance, 0)-OLD.summ WHERE id=OLD.account_id;
UPDATE billservice_account SET ballance=COALESCE(ballance, 0)+NEW.summ, bonus_ballance=COALESCE(bonus_ballance, 0)+NEW.summ  WHERE id=NEW.account_id;

RETURN NEW;
END IF;
RETURN NULL;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

  
  
CREATE TRIGGER acc_bns_trs_trg
AFTER INSERT OR UPDATE OR DELETE
ON billservice_bonustransaction
FOR EACH ROW
EXECUTE PROCEDURE account_bonus_transaction_trg_fn();
  
  
DROP VIEW billservice_totaltransactionreport;
CREATE OR REPLACE VIEW billservice_totaltransactionreport AS 
        (        (        (        (        (         SELECT psh.id, psh.service_id, NULL::boolean as is_bonus, ( SELECT billservice_periodicalservice.name
                                                           FROM billservice_periodicalservice
                                                          WHERE billservice_periodicalservice.id = psh.service_id) AS service_name, 'billservice_periodicalservicehistory'::text AS "table", psh.created, ( SELECT billservice_accounttarif.tarif_id
                                                           FROM billservice_accounttarif
                                                          WHERE billservice_accounttarif.id = psh.accounttarif_id) AS tariff_id, psh.summ, psh.account_id, psh.type_id, NULL::integer AS systemuser_id, ''::character varying AS bill, ''::text AS description, NULL::timestamp without time zone AS end_promise, NULL::boolean AS promise_expired, prev_balance::numeric as prev_balance
                                                   FROM billservice_periodicalservicehistory psh
                                        UNION ALL 
                                                 SELECT transaction.id, NULL::integer AS service_id, transaction.is_bonus, ''::character varying AS service_name, 'billservice_transaction'::text AS "table", transaction.created, ( SELECT billservice_accounttarif.tarif_id
                                                           FROM billservice_accounttarif
                                                          WHERE billservice_accounttarif.id = transaction.accounttarif_id) AS tariff_id, transaction.summ::numeric AS summ, transaction.account_id, transaction.type_id, transaction.systemuser_id, transaction.bill, transaction.description, transaction.end_promise, transaction.promise_expired, prev_balance::numeric as prev_balance
                                                   FROM billservice_transaction transaction)
                                UNION ALL 
                                         SELECT tr.id, NULL::integer AS service_id, NULL::boolean as is_bonus, ''::character varying AS service_name, 'billservice_traffictransaction'::text AS "table", tr.created, ( SELECT billservice_accounttarif.tarif_id
                                                   FROM billservice_accounttarif
                                                  WHERE billservice_accounttarif.id = tr.accounttarif_id) AS tariff_id, tr.summ, tr.account_id, 'NETFLOW_BILL'::character varying AS type_id, NULL::integer AS systemuser_id, ''::character varying AS bill, ''::text AS description, NULL::timestamp without time zone AS end_promise, NULL::boolean AS promise_expired, prev_balance::numeric as prev_balance
                                           FROM billservice_traffictransaction tr)
                        UNION ALL 
                                 SELECT addst.id, addst.service_id, NULL::boolean as is_bonus, ( SELECT billservice_addonservice.name
                                           FROM billservice_addonservice
                                          WHERE billservice_addonservice.id = addst.service_id) AS service_name, 'billservice_addonservicetransaction'::text AS "table", addst.created, ( SELECT billservice_accounttarif.tarif_id
                                           FROM billservice_accounttarif
                                          WHERE billservice_accounttarif.id = addst.accounttarif_id) AS tariff_id, addst.summ, addst.account_id, addst.type_id, NULL::integer AS systemuser_id, ''::character varying AS bill, ''::text AS description, NULL::timestamp without time zone AS end_promise, NULL::boolean AS promise_expired, prev_balance::numeric as prev_balance
                                   FROM billservice_addonservicetransaction addst)
                UNION ALL 
                         SELECT osh.id, osh.onetimeservice_id AS service_id, NULL::boolean as is_bonus, ''::character varying AS service_name, 'billservice_onetimeservicehistory'::text AS "table", osh.created, ( SELECT billservice_accounttarif.tarif_id
                                   FROM billservice_accounttarif
                                  WHERE billservice_accounttarif.id = osh.accounttarif_id) AS tariff_id, osh.summ, osh.account_id, 'ONETIME_SERVICE'::character varying AS type_id, NULL::integer AS systemuser_id, ''::character varying AS bill, ''::text AS description, NULL::timestamp without time zone AS end_promise, NULL::boolean AS promise_expired, prev_balance::numeric as prev_balance
                           FROM billservice_onetimeservicehistory osh)
        UNION ALL 
                 SELECT tr.id, NULL::integer AS service_id, NULL::boolean as is_bonus, ''::character varying AS service_name, 'billservice_timetransaction'::text AS "table", tr.created, ( SELECT billservice_accounttarif.tarif_id
                           FROM billservice_accounttarif
                          WHERE billservice_accounttarif.id = tr.accounttarif_id) AS tariff_id, tr.summ, tr.account_id, 'TIME_ACCESS'::character varying AS type_id, NULL::integer AS systemuser_id, ''::character varying AS bill, ''::text AS description, NULL::timestamp without time zone AS end_promise, NULL::boolean AS promise_expired, prev_balance::numeric as prev_balance
                   FROM billservice_timetransaction tr)
UNION ALL 
         SELECT qi.id, NULL::integer AS service_id, NULL::boolean as is_bonus, ''::character varying AS service_name, 'qiwi_payment'::text AS "table", qi.created, get_tarif(qi.account_id, qi.created) AS tariff_id, qi.summ, qi.account_id, 'qiwi_payment'::character varying AS type_id, NULL::integer AS systemuser_id, qi.autoaccept::text AS bill, qi.date_accepted::text AS description, NULL::timestamp without time zone AS end_promise, NULL::boolean AS promise_expired, prev_balance::numeric as prev_balance
           FROM qiwi_invoice qi;

CREATE OR REPLACE RULE billservice_totaltransactionreport_delete AS ON DELETE TO billservice_totaltransactionreport
    DO INSTEAD(SELECT 1);
    