CREATE TABLE dynamicmodel_dynamicschema
(
  id serial NOT NULL,
  model_id integer NOT NULL,
  type_value character varying(100),
  CONSTRAINT dynamicmodel_dynamicschema_pkey PRIMARY KEY (id),
  CONSTRAINT dynamicmodel_dynamicschema_model_id_fkey FOREIGN KEY (model_id)
      REFERENCES django_content_type (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT dynamicmodel_dynamicschema_model_id_type_value_key UNIQUE (model_id, type_value)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE dynamicmodel_dynamicschema
  OWNER TO ebs;

-- Index: dynamicmodel_dynamicschema_model_id

-- DROP INDEX dynamicmodel_dynamicschema_model_id;

CREATE INDEX dynamicmodel_dynamicschema_model_id
  ON dynamicmodel_dynamicschema
  USING btree
  (model_id);

CREATE TABLE dynamicmodel_dynamicschemafield
(
  id serial NOT NULL,
  schema_id integer NOT NULL,
  name character varying(100) NOT NULL,
  verbose_name character varying(100),
  field_type character varying(100) NOT NULL,
  required boolean NOT NULL,
  CONSTRAINT dynamicmodel_dynamicschemafield_pkey PRIMARY KEY (id),
  CONSTRAINT dynamicmodel_dynamicschemafield_schema_id_fkey FOREIGN KEY (schema_id)
      REFERENCES dynamicmodel_dynamicschema (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT dynamicmodel_dynamicschemafield_schema_id_name_key UNIQUE (schema_id, name)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE dynamicmodel_dynamicschemafield
  OWNER TO ebs;

-- Index: dynamicmodel_dynamicschemafield_schema_id

-- DROP INDEX dynamicmodel_dynamicschemafield_schema_id;

CREATE INDEX dynamicmodel_dynamicschemafield_schema_id
  ON dynamicmodel_dynamicschemafield
  USING btree
  (schema_id);
  
  
INSERT INTO dynamicmodel_dynamicschema(model_id, type_value) VALUES((SELECT id FROM django_content_type WHERE app_label='billservice' and model='account'), '');
ALTER TABLE billservice_account ADD COLUMN extra_fields text;
ALTER TABLE billservice_account ALTER COLUMN extra_fields SET DEFAULT '{}'::text;
update billservice_account set extra_fields='{}';

