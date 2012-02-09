ALTER TABLE billservice_document
   ADD COLUMN date_start timestamp without time zone DEFAULT now();

ALTER TABLE billservice_document
   ADD COLUMN date_end timestamp without time zone;

ALTER TABLE billservice_document
   ADD COLUMN contractnumber text DEFAULT '';
