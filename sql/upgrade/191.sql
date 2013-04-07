ALTER TABLE helpdesk_ticket ADD COLUMN source character varying(64);
ALTER TABLE helpdesk_ticket ALTER COLUMN source SET DEFAULT ''::character varying;
ALTER TABLE helpdesk_ticket
   ADD COLUMN tags text DEFAULT '';
