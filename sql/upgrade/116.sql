ALTER TABLE nas_switch RENAME TO billservice_switch;
ALTER TABLE billservice_switch ADD COLUMN manufacturer_id integer;
ALTER TABLE billservice_switch ALTER COLUMN manufacturer_id SET DEFAULT NULL ;

ALTER TABLE billservice_switch ADD COLUMN model_id integer;
ALTER TABLE billservice_switch ALTER COLUMN model_id SET DEFAULT NULL ;

ALTER TABLE billservice_switch ADD COLUMN city text;
ALTER TABLE billservice_switch ALTER COLUMN city SET DEFAULT ''::text;

ALTER TABLE billservice_switch ADD COLUMN street text;
ALTER TABLE billservice_switch ALTER COLUMN street SET DEFAULT ''::text;

ALTER TABLE billservice_switch ADD COLUMN house text;
ALTER TABLE billservice_switch ALTER COLUMN house SET DEFAULT ''::text;