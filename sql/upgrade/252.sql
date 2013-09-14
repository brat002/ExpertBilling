ALTER TABLE billservice_subaccount
   ADD COLUMN ipn_queued timestamp without time zone;

ALTER TABLE radius_activesession
   ADD COLUMN speed_change_queued timestamp without time zone;

ALTER TABLE radius_activesession
   ADD COLUMN pod_queued timestamp without time zone;