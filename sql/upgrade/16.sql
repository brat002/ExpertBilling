ALTER TABLE billservice_ipinuse
   ADD COLUMN disabled timestamp without time zone;

ALTER TABLE billservice_ipinuse
   ADD COLUMN dynamic boolean DEFAULT False;

UPDATE billservice_ipinuse SET dynamic=False;
