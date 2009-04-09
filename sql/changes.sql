--06.04.2009
ALTER TABLE billservice_shedulelog
DROP CONSTRAINT billservice_shedulelog_accounttarif_id_fkey;

ALTER TABLE billservice_shedulelog
ADD CONSTRAINT billservice_shedulelog_accounttarif_id_fkey FOREIGN KEY (accounttarif_id)
REFERENCES billservice_accounttarif (id) MATCH SIMPLE
ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;


ALTER TABLE billservice_shedulelog
DROP CONSTRAINT billservice_shedulelog_account_id_fkey

ALTER TABLE billservice_shedulelog
ADD CONSTRAINT billservice_shedulelog_account_id_fkey FOREIGN KEY (account_id)
REFERENCES billservice_account (id) MATCH SIMPLE
ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE billservice_traffictransmitnodes
  DROP CONSTRAINT billservice_traffictransmitnodes_group_id_fkey ;

ALTER TABLE billservice_traffictransmitnodes
  ADD CONSTRAINT billservice_traffictransmitnodes_group_id_fkey FOREIGN KEY (group_id)
      REFERENCES billservice_group (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE;
      
CREATE OR REPLACE FUNCTION clear_tariff_services_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN


IF (TG_OP = 'DELETE') THEN
    IF (OLD.traffic_transmit_service_id is not Null) THEN
        DELETE FROM billservice_traffictransmitservice WHERE id=OLD.traffic_transmit_service_id;
    END IF;

    IF (OLD.time_access_service_id is not Null) THEN
        DELETE FROM billservice_timeaccessservice WHERE id=OLD.time_access_service_id;   
    RETURN OLD;
    END IF;
    
END IF;
RETURN OLD;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;


CREATE TRIGGER clear_tariff_services_trg
  BEFORE DELETE
  ON billservice_tariff
  FOR EACH ROW
  EXECUTE PROCEDURE clear_tariff_services_trg_fn();

--7.04.2009
ALTER TABLE billservice_systemuser
   ADD COLUMN "role" integer;
ALTER TABLE billservice_systemuser
   ALTER COLUMN "role" SET NOT NULL;
   
UPDATE billservice_systemuser SET role = 0 WHERE id>0;

--08.04.2009
ALTER TABLE radius_activesession
   ALTER COLUMN interrim_update DROP DEFAULT;
ALTER TABLE billservice_transaction
   ADD COLUMN systemuser_id integer;
   
ALTER TABLE billservice_transaction ADD CONSTRAINT billservice_systemuser_fkey FOREIGN KEY (systemuser_id) REFERENCES billservice_systemuser (id)
   ON UPDATE NO ACTION ON DELETE SET NULL
   DEFERRABLE;
CREATE INDEX fki_billservice_systemuser_fkey ON billservice_transaction(systemuser_id);

ALTER TABLE billservice_transaction
   ADD COLUMN promise boolean;
ALTER TABLE billservice_transaction
   ALTER COLUMN promise SET DEFAULT False;
   
ALTER TABLE billservice_transaction
   ADD COLUMN end_promise timestamp without time zone;


ALTER TABLE billservice_transaction
   ADD COLUMN promise_expired boolean;
ALTER TABLE billservice_transaction
   ALTER COLUMN promise_expired SET DEFAULT False;

-- !!! 
ALTER TABLE billservice_transaction
  ADD CONSTRAINT billservice_transaction_tarif_id_fkey FOREIGN KEY (tarif_id)
      REFERENCES billservice_tariff (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL DEFERRABLE INITIALLY IMMEDIATE;
      

INSERT INTO billservice_transactiontype(
             "name", internal_name)
    VALUES ('Операция проведена кассиром', 'CASSA_TRANSACTION');
    
