ALTER TABLE billservice_radiusattrs
   ADD COLUMN nas_id integer;
ALTER TABLE billservice_radiusattrs
   ALTER COLUMN tarif_id DROP NOT NULL;


