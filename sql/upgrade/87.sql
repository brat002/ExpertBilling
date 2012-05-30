DROP TABLE IF EXISTS django_session;

CREATE TABLE django_session
(
  session_key character varying(40) NOT NULL,
  session_data text NOT NULL,
  expire_date timestamp with time zone NOT NULL,
  CONSTRAINT django_session_pkey PRIMARY KEY (session_key )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE django_session
  OWNER TO ebs;

-- Index: django_session_expire_date

-- DROP INDEX django_session_expire_date;

CREATE INDEX django_session_expire_date
  ON django_session
  USING btree
  (expire_date );


DROP TABLE IF EXISTS django_admin_log;

CREATE TABLE django_admin_log
(
  id serial NOT NULL,
  action_time timestamp with time zone NOT NULL,
  user_id integer NOT NULL,
  content_type_id integer,
  object_id text,
  object_repr character varying(200) NOT NULL,
  action_flag smallint NOT NULL,
  change_message text NOT NULL,
  CONSTRAINT django_admin_log_pkey PRIMARY KEY (id ),
  CONSTRAINT django_admin_log_content_type_id_fkey FOREIGN KEY (content_type_id)
      REFERENCES django_content_type (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT django_admin_log_user_id_fkey FOREIGN KEY (user_id)
      REFERENCES auth_user (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT django_admin_log_action_flag_check CHECK (action_flag >= 0)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE django_admin_log
  OWNER TO ebs;

-- Index: django_admin_log_content_type_id

-- DROP INDEX django_admin_log_content_type_id;

CREATE INDEX django_admin_log_content_type_id
  ON django_admin_log
  USING btree
  (content_type_id );

-- Index: django_admin_log_user_id

-- DROP INDEX django_admin_log_user_id;

CREATE INDEX django_admin_log_user_id
  ON django_admin_log
  USING btree
  (user_id );


DROP TABLE IF EXISTS auth_user_groups;

CREATE TABLE auth_user_groups
(
  id serial NOT NULL,
  user_id integer NOT NULL,
  group_id integer NOT NULL,
  CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id ),
  CONSTRAINT auth_user_groups_group_id_fkey FOREIGN KEY (group_id)
      REFERENCES auth_group (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT user_id_refs_id_7ceef80f FOREIGN KEY (user_id)
      REFERENCES auth_user (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT auth_user_groups_user_id_group_id_key UNIQUE (user_id , group_id )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE auth_user_groups
  OWNER TO ebs;

-- Index: auth_user_groups_group_id

-- DROP INDEX auth_user_groups_group_id;

CREATE INDEX auth_user_groups_group_id
  ON auth_user_groups
  USING btree
  (group_id );

-- Index: auth_user_groups_user_id

-- DROP INDEX auth_user_groups_user_id;

CREATE INDEX auth_user_groups_user_id
  ON auth_user_groups
  USING btree
  (user_id );

