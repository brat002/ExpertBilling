ALTER TABLE billservice_transaction
  ADD CONSTRAINT billservice_transaction_id_pkey PRIMARY KEY (id);

BEGIN;
CREATE TABLE "getpaid_payment" (
    "id" serial NOT NULL PRIMARY KEY,
    "amount" numeric(20, 4) NOT NULL,
    "currency" varchar(3) NOT NULL,
    "status" varchar(20) NOT NULL,
    "backend" varchar(50) NOT NULL,
    "created_on" timestamp with time zone NOT NULL,
    "paid_on" timestamp with time zone,
    "amount_paid" numeric(20, 4) NOT NULL,
    "order_id" integer NOT NULL REFERENCES "billservice_transaction" ("id") DEFERRABLE INITIALLY DEFERRED
)
;
COMMIT;
