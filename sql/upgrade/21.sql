ALTER TABLE billservice_transactiontype
   ADD COLUMN is_deletable boolean DEFAULT True;

UPDATE billservice_transactiontype SET is_deletable=False;
