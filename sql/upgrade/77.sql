DROP TABLE IF EXISTS auth_user CASCADE;
CREATE TABLE auth_user
(
  id serial NOT NULL,
  username character varying(256) NOT NULL,
  first_name character varying(256) NOT NULL,
  last_name character varying(256) NOT NULL,
  email character varying(75) NOT NULL,
  password character varying(128) NOT NULL,
  is_staff boolean NOT NULL,
  is_active boolean NOT NULL,
  is_superuser boolean NOT NULL,
  last_login timestamp without time zone NOT NULL,
  date_joined timestamp without time zone NOT NULL,
  CONSTRAINT auth_user_pkey PRIMARY KEY (id ),
  CONSTRAINT auth_user_username_key UNIQUE (username )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE auth_user
  OWNER TO ebs;
