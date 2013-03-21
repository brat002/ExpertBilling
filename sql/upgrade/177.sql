-- Table: sendsms_message

DROP TABLE  IF EXISTS sendsms_message CASCADE;

CREATE TABLE sendsms_message
(
  id serial NOT NULL,
  account_id integer NOT NULL,
  "to" character varying(64) NOT NULL,
  body text NOT NULL,
  flash boolean NOT NULL,
  backend character varying(128) NOT NULL,
  created timestamp with time zone NOT NULL,
  sended timestamp with time zone,
  publish_date timestamp with time zone,
  response text,
  CONSTRAINT sendsms_message_pkey PRIMARY KEY (id),
  CONSTRAINT sendsms_message_account_id_fkey FOREIGN KEY (account_id)
      REFERENCES billservice_account (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
)
WITH (
  OIDS=FALSE
);
ALTER TABLE sendsms_message
  OWNER TO ebs;

-- Index: sendsms_message_account_id

-- DROP INDEX sendsms_message_account_id;

CREATE INDEX sendsms_message_account_id
  ON sendsms_message
  USING btree
  (account_id);

-- Index: sendsms_message_publish_date

-- DROP INDEX sendsms_message_publish_date;

CREATE INDEX sendsms_message_publish_date
  ON sendsms_message
  USING btree
  (publish_date);


