CREATE TABLE object_log_logaction
(
  "name" character varying(128) NOT NULL,
  "template" character varying(128) NOT NULL,
  CONSTRAINT object_log_logaction_pkey PRIMARY KEY (name)
)
WITH (
  OIDS=FALSE
);

INSERT INTO object_log_logaction (name, template) VALUES ('EDIT', 'object_log/edit.html');
INSERT INTO object_log_logaction (name, template) VALUES ('CREATE', 'object_log/add.html');
INSERT INTO object_log_logaction (name, template) VALUES ('DELETE', 'object_log/delete.html');
INSERT INTO object_log_logaction (name, template) VALUES ('RAWSQL', 'object_log/rawsql.html');

CREATE TABLE object_log_logitem
(
  id serial NOT NULL,
  action_id character varying(128) NOT NULL,
  "timestamp" timestamp with time zone NOT NULL,
  user_id integer NOT NULL,
  object_type1_id integer,
  object_id1 integer,
  object_type2_id integer,
  object_id2 integer,
  object_type3_id integer,
  object_id3 integer,
  serialized_data text,
  CONSTRAINT object_log_logitem_pkey PRIMARY KEY (id),
  CONSTRAINT object_log_logitem_action_id_fkey FOREIGN KEY (action_id)
      REFERENCES object_log_logaction ("name") MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT object_log_logitem_object_id1_check CHECK (object_id1 >= 0),
  CONSTRAINT object_log_logitem_object_id2_check CHECK (object_id2 >= 0),
  CONSTRAINT object_log_logitem_object_id3_check CHECK (object_id3 >= 0)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE object_log_logitem OWNER TO ebs;



