ALTER TABLE ebsadmin_tablesettings
   ADD COLUMN per_page integer DEFAULT 25;

UPDATE ebsadmin_tablesettings SET per_page=25;
