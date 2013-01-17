DROP TABLE IF EXISTS django_content_type CASCADE;
CREATE TABLE "django_content_type" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(100) NOT NULL,
    "app_label" varchar(100) NOT NULL,
    "model" varchar(100) NOT NULL,
    UNIQUE ("app_label", "model")
)
;

DROP TABLE IF EXISTS auth_permission CASCADE;
CREATE TABLE auth_permission
(
  id serial NOT NULL,
  name character varying(150) NOT NULL,
  content_type_id integer NOT NULL,
  codename character varying(100) NOT NULL,
  CONSTRAINT auth_permission_pkey PRIMARY KEY (id ),
  CONSTRAINT content_type_id_refs_id_728de91f FOREIGN KEY (content_type_id)
      REFERENCES django_content_type (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT auth_permission_content_type_id_codename_key UNIQUE (content_type_id , codename )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE auth_permission
  OWNER TO ebs;

-- Index: auth_permission_content_type_id

-- DROP INDEX auth_permission_content_type_id;

CREATE INDEX auth_permission_content_type_id
  ON auth_permission
  USING btree
  (content_type_id );

