INSERT INTO billservice_transactiontype(
            name, internal_name, is_deletable)
    VALUES ('Platezhka UA', 'payments.platezhkaua', False);

CREATE INDEX "billservice_account_deleted" ON "billservice_account" ("deleted");
CREATE INDEX "billservice_periodicalservice_deleted" ON "billservice_periodicalservice" ("deleted");


