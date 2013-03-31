ALTER TABLE auth_user ALTER COLUMN username TYPE character varying(256);
ALTER TABLE auth_user ALTER COLUMN first_name TYPE character varying(256);
ALTER TABLE auth_user ALTER COLUMN last_name TYPE character varying(256);
ALTER TABLE billservice_account ALTER COLUMN extra_fields SET DEFAULT '{}'::text;

