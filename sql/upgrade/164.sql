DROP TABLE IF EXISTS getpaid_payment CASCADE;

CREATE TABLE getpaid_payment
(
  id serial NOT NULL,
  account_id integer NOT NULL,
  amount numeric(20,4) NOT NULL,
  currency character varying(3) NOT NULL,
  status character varying(20) NOT NULL,
  backend character varying(50) NOT NULL,
  created_on timestamp with time zone NOT NULL,
  paid_on timestamp with time zone,
  amount_paid numeric(20,4) NOT NULL,
  external_id character varying(64),
  description character varying(128),
  order_id integer,
  CONSTRAINT getpaid_payment_pkey PRIMARY KEY (id),
  CONSTRAINT getpaid_payment_order_id_fkey FOREIGN KEY (order_id)
      REFERENCES billservice_transaction (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
)
WITH (
  OIDS=FALSE
);
CREATE INDEX IF NOT EXISTS getpaid_payment
  OWNER TO ebs;

-- Index: getpaid_payment_created_on

-- DROP INDEX getpaid_payment_created_on;

CREATE INDEX IF NOT EXISTS getpaid_payment_created_on
  ON getpaid_payment
  USING btree
  (created_on);

-- Index: getpaid_payment_order_id

-- DROP INDEX getpaid_payment_order_id;

CREATE INDEX IF NOT EXISTS getpaid_payment_order_id
  ON getpaid_payment
  USING btree
  (order_id);

-- Index: getpaid_payment_paid_on

-- DROP INDEX getpaid_payment_paid_on;

CREATE INDEX IF NOT EXISTS getpaid_payment_paid_on
  ON getpaid_payment
  USING btree
  (paid_on);

-- Index: getpaid_payment_status

-- DROP INDEX getpaid_payment_status;

CREATE INDEX IF NOT EXISTS getpaid_payment_status
  ON getpaid_payment
  USING btree
  (status COLLATE pg_catalog."default");

-- Index: getpaid_payment_status_like

-- DROP INDEX getpaid_payment_status_like;

CREATE INDEX IF NOT EXISTS getpaid_payment_status_like
  ON getpaid_payment
  USING btree
  (status COLLATE pg_catalog."default" varchar_pattern_ops);
  
  