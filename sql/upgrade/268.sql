ALTER TABLE radius_activesession
   ADD COLUMN need_time_co boolean DEFAULT False;

ALTER TABLE radius_activesession
   ADD COLUMN need_traffic_co boolean DEFAULT False;
   