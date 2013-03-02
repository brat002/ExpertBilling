create extension pgcrypto;

ALTER TABLE billservice_account
   ALTER COLUMN password TYPE text;

ALTER TABLE billservice_subaccount
   ALTER COLUMN password TYPE text;

UPDATE billservice_account SET password=armor(encrypt(password::bytea, 'ebscryptkeytest', 'AES'));
UPDATE billservice_subaccount SET password=armor(encrypt(password::bytea, 'ebscryptkeytest', 'AES'));