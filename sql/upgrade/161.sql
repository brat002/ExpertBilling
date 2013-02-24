ALTER TABLE billservice_radiusattrs
   ADD COLUMN account_status integer DEFAULT 0;


UPDATE billservice_radiusattrs SET account_status=0;

ALTER TABLE billservice_radiusattrs
   ALTER COLUMN account_status SET NOT NULL;

