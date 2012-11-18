DROP TRIGGER billservice_timeperiod_trg ON billservice_timeperiod;
ALTER TABLE billservice_timeperiodnode
   ADD COLUMN time_period_id integer;

update billservice_timeperiodnode as tpn SET time_period_id = (SELECT timeperiod_id FROM billservice_timeperiod_time_period_nodes WHERE timeperiodnode_id=tpn.id);

DELETE FROM billservice_timeperiodnode WHERE time_period_id is NULL;

ALTER TABLE billservice_timeperiodnode
   ALTER COLUMN time_period_id SET NOT NULL;

ALTER TABLE billservice_timeperiodnode
  ADD CONSTRAINT billservice_timeperiodnode_time_period_id_fkey FOREIGN KEY (time_period_id)
      REFERENCES billservice_timeperiod (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;
      