INSERT INTO django_site(
            "domain", "name")
    VALUES ('localhost', 'localhost');

DROP TABLE helpdesk_ticketchange CASCADE;

CREATE TABLE helpdesk_ticketchange
(
  id serial NOT NULL,
  followup_id integer NOT NULL,
  field character varying(100) NOT NULL,
  old_value text,
  new_value text,
  CONSTRAINT helpdesk_ticketchange_pkey PRIMARY KEY (id),
  CONSTRAINT helpdesk_ticketchange_followup_id_fkey FOREIGN KEY (followup_id)
      REFERENCES helpdesk_followup (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
)
WITH (
  OIDS=FALSE
);
ALTER TABLE helpdesk_ticketchange OWNER TO postgres;

-- Index: helpdesk_ticketchange_followup_id

-- DROP INDEX IF EXISTS  helpdesk_ticketchange_followup_id;

CREATE INDEX helpdesk_ticketchange_followup_id
  ON helpdesk_ticketchange
  USING btree
  (followup_id);


DROP TABLE helpdesk_attachment CASCADE;


CREATE TABLE helpdesk_attachment
(
  id serial NOT NULL,
  followup_id integer NOT NULL,
  file character varying(100) NOT NULL,
  filename character varying(100) NOT NULL,
  mime_type character varying(30) NOT NULL,
  size integer NOT NULL,
  CONSTRAINT helpdesk_attachment_pkey PRIMARY KEY (id),
  CONSTRAINT helpdesk_attachment_followup_id_fkey FOREIGN KEY (followup_id)
      REFERENCES helpdesk_followup (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
)
WITH (
  OIDS=FALSE
);
ALTER TABLE helpdesk_attachment OWNER TO postgres;

-- Index: helpdesk_attachment_followup_id

-- DROP INDEX IF EXISTS  helpdesk_attachment_followup_id;

CREATE INDEX helpdesk_attachment_followup_id
  ON helpdesk_attachment
  USING btree
  (followup_id);


DROP TABLE helpdesk_followup CASCADE;

CREATE TABLE helpdesk_followup
(
  id serial NOT NULL,
  ticket_id integer NOT NULL,
  date timestamp with time zone NOT NULL,
  title character varying(200),
  "comment" text,
  public boolean NOT NULL,
  user_id integer,
  new_status integer,
  CONSTRAINT helpdesk_followup_pkey PRIMARY KEY (id),
  CONSTRAINT helpdesk_followup_ticket_id_fkey FOREIGN KEY (ticket_id)
      REFERENCES helpdesk_ticket (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT helpdesk_followup_user_id_fkey FOREIGN KEY (user_id)
      REFERENCES auth_user (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
)
WITH (
  OIDS=FALSE
);
ALTER TABLE helpdesk_followup OWNER TO postgres;

-- Index: helpdesk_followup_ticket_id

DROP INDEX IF EXISTS  helpdesk_followup_ticket_id;

CREATE INDEX helpdesk_followup_ticket_id
  ON helpdesk_followup
  USING btree
  (ticket_id);

-- Index: helpdesk_followup_user_id

DROP INDEX IF EXISTS  helpdesk_followup_user_id;

CREATE INDEX helpdesk_followup_user_id
  ON helpdesk_followup
  USING btree
  (user_id);



DROP TABLE helpdesk_ticket CASCADE;

CREATE TABLE helpdesk_ticket
(
  id serial NOT NULL,
  title character varying(200) NOT NULL,
  queue_id integer NOT NULL,
  owner_id integer,
  created timestamp with time zone NOT NULL,
  modified timestamp with time zone NOT NULL,
  submitter_email character varying(75),
  assigned_to_id integer,
  status integer NOT NULL,
  on_hold boolean NOT NULL,
  description text,
  resolution text,
  priority integer NOT NULL,
  last_escalation timestamp with time zone,
  notify_owner boolean DEFAULT true,
  CONSTRAINT helpdesk_ticket_pkey PRIMARY KEY (id),
  CONSTRAINT helpdesk_ticket_assigned_to_id_fkey FOREIGN KEY (assigned_to_id)
      REFERENCES auth_user (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT helpdesk_ticket_queue_id_fkey FOREIGN KEY (queue_id)
      REFERENCES helpdesk_queue (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT helpdesk_ticket_submitter_id_fkey FOREIGN KEY (owner_id)
      REFERENCES auth_user (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
)
WITH (
  OIDS=FALSE
);
ALTER TABLE helpdesk_ticket OWNER TO postgres;

-- Index: helpdesk_ticket_assigned_to_id

DROP INDEX IF EXISTS  helpdesk_ticket_assigned_to_id;

CREATE INDEX helpdesk_ticket_assigned_to_id
  ON helpdesk_ticket
  USING btree
  (assigned_to_id);

-- Index: helpdesk_ticket_queue_id

DROP INDEX IF EXISTS  helpdesk_ticket_queue_id;

CREATE INDEX helpdesk_ticket_queue_id
  ON helpdesk_ticket
  USING btree
  (queue_id);

-- Index: helpdesk_ticket_submitter_id
DROP INDEX IF EXISTS  helpdesk_ticket_submitter_id;

CREATE INDEX helpdesk_ticket_submitter_id
  ON helpdesk_ticket
  USING btree
  (owner_id);

