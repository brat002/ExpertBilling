CREATE TABLE "billservice_transactiontype_allowed_systemusers" (
    "id" serial NOT NULL PRIMARY KEY,
    "transactiontype_id" integer NOT NULL,
    "systemuser_id" integer NOT NULL,
    UNIQUE ("transactiontype_id", "systemuser_id")
);
ALTER TABLE "billservice_transactiontype_allowed_systemusers" ADD CONSTRAINT "transactiontype_id_refs_id_65733b4a" FOREIGN KEY ("transactiontype_id") REFERENCES "billservice_transactiontype" ("id") DEFERRABLE INITIALLY DEFERRED;


