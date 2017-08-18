alter table billservice_radiusattrs add column attribute varchar(255) NOT NULL;
alter table billservice_radiusattrs ALTER COLUMN vendor DROP NOT NULL;
alter table billservice_radiusattrs ALTER COLUMN attrid DROP NOT NULL;