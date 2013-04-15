ALTER TABLE helpdesk_savedsearch ADD COLUMN systemuser_id integer;
ALTER TABLE helpdesk_savedsearch
  ADD CONSTRAINT helpdesk_savedsearch_systemuser_id_fkey FOREIGN KEY (systemuser_id)
      REFERENCES billservice_systemuser (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
      