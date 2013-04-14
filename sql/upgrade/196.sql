ALTER TABLE helpdesk_followup ADD COLUMN systemuser_id integer;
ALTER TABLE helpdesk_followup ADD COLUMN account_id integer;

ALTER TABLE helpdesk_followup
  ADD CONSTRAINT helpdesk_followup_systemuser_id_fkey FOREIGN KEY (systemuser_id)
      REFERENCES billservice_systemuser (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
      
      
ALTER TABLE helpdesk_followup
  ADD CONSTRAINT helpdesk_followup_account_id_fkey FOREIGN KEY (account_id)
      REFERENCES billservice_account (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
      
UPDATE helpdesk_followup as f SET account_id = (SELECT id FROM billservice_account WHERE username=(SELECT username FROM auth_user WHERE id=f.user_id));
UPDATE helpdesk_followup as f SET systemuser_id = (SELECT id FROM billservice_systemuser WHERE username=(SELECT username FROM auth_user WHERE id=f.user_id));
ALTER TABLE helpdesk_followup DROP COLUMN user_id;

DELETE FROM helpdesk_savedsearch;

ALTER TABLE helpdesk_ticket ADD COLUMN hidden_comment text;
ALTER TABLE helpdesk_ticket ALTER COLUMN hidden_comment SET DEFAULT ''::text;

ALTER TABLE helpdesk_ticket ADD COLUMN account_id integer;

ALTER TABLE helpdesk_ticket
  ADD CONSTRAINT helpdesk_ticket_account_id_fkey FOREIGN KEY (account_id)
      REFERENCES billservice_account (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
      
UPDATE helpdesk_ticket as t SET account_id = (SELECT id FROM billservice_account WHERE username=(SELECT username FROM auth_user WHERE id=t.owner_id));

ALTER TABLE helpdesk_ticket ADD COLUMN due_date integer;
ALTER TABLE helpdesk_ticket ADD COLUMN source character varying(64);
ALTER TABLE helpdesk_ticket ALTER COLUMN source SET DEFAULT ''::character varying;

