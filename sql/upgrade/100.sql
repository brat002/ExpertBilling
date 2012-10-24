CREATE TABLE billservice_accountgroup
(
  id serial NOT NULL,
  name character varying(512) NOT NULL,
  CONSTRAINT billservice_accountgroup_pkey PRIMARY KEY (id )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE billservice_accountgroup
  OWNER TO ebs;

ALTER TABLE billservice_account
   ADD COLUMN account_group_id integer;
