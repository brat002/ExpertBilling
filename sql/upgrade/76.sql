ALTER TABLE billservice_groupstat
   ADD COLUMN accounttarif_id integer;

ALTER TABLE billservice_globalstat
   ADD COLUMN accounttarif_id integer;
   
ALTER TABLE billservice_groupstat DROP CONSTRAINT billservice_groupstat_group_id_key;