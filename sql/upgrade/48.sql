INSERT INTO billservice_transactiontype(name, tyle_id) VALUES('Webmoney Merchant', 'WEBMONEY_PAYMENT');

DROP TABLE webmoney_payment;
DROP TABLE webmoney_invoice;
DROP TABLE webmoney_purse;

CREATE TABLE webmoney_payment
(
  id serial NOT NULL,
  account_id integer NOT NULL,
  created timestamp with time zone NOT NULL,
  purse character varying(32) NOT NULL,
  amount numeric(9,2) DEFAULT 0,
  "mode" smallint DEFAULT 1,
  sys_invs_no integer,
  sys_trans_no integer,
  sys_trans_date timestamp with time zone,
  payer_purse character varying(13),
  payer_wm character varying(12),
  paymer_number character varying(30),
  paymer_email character varying(75),
  telepat_phonenumber character varying(30) DEFAULT '',
  telepat_orderid character varying(30),
  payment_creditdays integer,
  CONSTRAINT webmoney_payment_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
CREATE OR REPLACE FUNCTION billservice_account_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN

IF (TG_OP = 'DELETE') THEN
    DELETE FROM billservice_ipinuse WHERE id=OLD.ipn_ipinuse_id;
    DELETE FROM billservice_ipinuse WHERE id=OLD.vpn_ipinuse_id;
    DELETE FROM billservice_accountaddonservice WHERE account_id=OLD.id;
    DELETE FROM billservice_accountipnspeed WHERE account_id=OLD.id;
    DELETE FROM billservice_accountspeedlimit WHERE account_id=OLD.id;
    DELETE FROM billservice_accounttarif WHERE account_id=OLD.id;
    DELETE FROM billservice_accountviewednews WHERE account_id=OLD.id;
    DELETE FROM billservice_addonservicetransaction WHERE account_id=OLD.id;
    DELETE FROM billservice_balancehistory WHERE account_id=OLD.id;
    DELETE FROM billservice_document WHERE account_id=OLD.id;
    DELETE FROM billservice_groupstat WHERE account_id=OLD.id;
    DELETE FROM billservice_netflowstream WHERE account_id=OLD.id;
    DELETE FROM billservice_onetimeservicehistory WHERE account_id=OLD.id;
    DELETE FROM billservice_organization WHERE account_id=OLD.id;
    DELETE FROM billservice_periodicalservicehistory WHERE account_id=OLD.id;
    DELETE FROM billservice_shedulelog WHERE account_id=OLD.id;
    DELETE FROM billservice_subaccount WHERE account_id=OLD.id;
    DELETE FROM billservice_suspendedperiod WHERE account_id=OLD.id;
    DELETE FROM billservice_timetransaction WHERE account_id=OLD.id;
    DELETE FROM billservice_transaction WHERE account_id=OLD.id;
    DELETE FROM billservice_traffictransaction WHERE account_id=OLD.id;
    DELETE FROM billservice_x8021 WHERE account_id=OLD.id;
    DELETE FROM radius_activesession WHERE account_id=OLD.id;
    DELETE FROM webmoney_payment WHERE account_id=OLD.id;
    
    RETURN OLD;
END IF;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;