ALTER TABLE billservice_trafficlimit ADD COLUMN speedlimit_id integer;
ALTER TABLE billservice_trafficlimit
  ADD CONSTRAINT billservice_trafficlimit_speedlimit_id_fkey FOREIGN KEY (speedlimit_id)
      REFERENCES billservice_speedlimit (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;

UPDATE billservice_trafficlimit as tl SET speedlimit_id=(SELECT id FROM billservice_speedlimit WHERE tl.id=limit_id);
ALTER TABLE billservice_speedlimit DROP COLUMN limit_id;
