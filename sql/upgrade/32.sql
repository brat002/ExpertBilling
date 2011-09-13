DROP TRIGGER IF EXISTS acc_psh_trg
  ON billservice_periodicalservicehistory;

CREATE TRIGGER acc_psh_trg
  AFTER INSERT OR UPDATE OR DELETE
  ON billservice_periodicalservicehistory
  FOR EACH ROW
  EXECUTE PROCEDURE account_transaction_trg_fn();