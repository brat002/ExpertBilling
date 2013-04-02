DROP TRIGGER billservice_account_trg ON billservice_account;

CREATE TRIGGER billservice_account_trg
  BEFORE DELETE
  ON billservice_account
  FOR EACH ROW
  EXECUTE PROCEDURE billservice_account_trg_fn();
  
  