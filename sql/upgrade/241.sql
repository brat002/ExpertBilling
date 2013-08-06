CREATE TABLE ebsadmin_comment
(
  id serial NOT NULL,
  content_type_id integer,
  object_id integer,
  comment text NOT NULL,
  created timestamp with time zone,
  done_date timestamp with time zone,
  done_systemuser_id integer,
  due_date timestamp with time zone,
  deleted timestamp with time zone,
  done_comment text DEFAULT ''::text,
  CONSTRAINT ebsadmin_comment_pkey PRIMARY KEY (id),
  CONSTRAINT ebsadmin_comment_content_type_id_fkey FOREIGN KEY (content_type_id)
      REFERENCES django_content_type (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT ebsadmin_comment_done_systemuser_id_fkey FOREIGN KEY (done_systemuser_id)
      REFERENCES billservice_systemuser (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT ebsadmin_comment_object_id_check CHECK (object_id >= 0)
)
WITH (
  OIDS=FALSE
);