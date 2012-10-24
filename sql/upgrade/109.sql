ALTER TABLE billservice_accessparameters
   ADD COLUMN max_tx character varying(64) DEFAULT '';
ALTER TABLE billservice_accessparameters
   ADD COLUMN max_rx character varying(64) DEFAULT '';

ALTER TABLE billservice_accessparameters
   ADD COLUMN burst_tx character varying(64) DEFAULT '';
ALTER TABLE billservice_accessparameters
   ADD COLUMN burst_rx character varying(64) DEFAULT '';

ALTER TABLE billservice_accessparameters
   ADD COLUMN burst_treshold_tx character varying(64) DEFAULT '';
ALTER TABLE billservice_accessparameters
   ADD COLUMN burst_treshold_rx character varying(64) DEFAULT '';

ALTER TABLE billservice_accessparameters
   ADD COLUMN burst_time_tx character varying(64) DEFAULT '';
ALTER TABLE billservice_accessparameters
   ADD COLUMN burst_time_rx character varying(64) DEFAULT '';

ALTER TABLE billservice_accessparameters
   ADD COLUMN min_tx character varying(64) DEFAULT '';
ALTER TABLE billservice_accessparameters
   ADD COLUMN min_rx character varying(64) DEFAULT '';

ALTER TABLE billservice_timespeed
   ADD COLUMN max_tx character varying(64) DEFAULT '';
ALTER TABLE billservice_timespeed
   ADD COLUMN max_rx character varying(64) DEFAULT '';

ALTER TABLE billservice_timespeed
   ADD COLUMN burst_tx character varying(64) DEFAULT '';
ALTER TABLE billservice_timespeed
   ADD COLUMN burst_rx character varying(64) DEFAULT '';

ALTER TABLE billservice_timespeed
   ADD COLUMN burst_treshold_tx character varying(64) DEFAULT '';
ALTER TABLE billservice_timespeed
   ADD COLUMN burst_treshold_rx character varying(64) DEFAULT '';

ALTER TABLE billservice_timespeed
   ADD COLUMN burst_time_tx character varying(64) DEFAULT '';
ALTER TABLE billservice_timespeed
   ADD COLUMN burst_time_rx character varying(64) DEFAULT '';

ALTER TABLE billservice_timespeed
   ADD COLUMN min_tx character varying(64) DEFAULT '';
ALTER TABLE billservice_timespeed
   ADD COLUMN min_rx character varying(64) DEFAULT '';


UPDATE billservice_accessparameters SET 
max_tx=substring(max_limit from '([0-9]+[k|M|b]?)/[0-9]+[k|M|b]?'),
max_rx = substring(max_limit from '[0-9]+[k|M|b]?/([0-9]+[k|M|b]?)'),
burst_tx = substring(burst_limit from '([0-9]+[k|M|b]?)/[0-9]+[k|M|b]?'),
burst_rx = substring(burst_limit from '[0-9]+[k|M|b]?/([0-9]+[k|M|b]?)'),
burst_treshold_tx = substring(burst_treshold from '([0-9]+[k|M|b]?)/[0-9]+[k|M|b]?'),
burst_treshold_rx = substring(burst_treshold from '[0-9]+[k|M|b?]/([0-9]+[k|M|b]?)'),
burst_time_tx = substring(burst_time from '([0-9]+[k|M|b]?)/[0-9]+[k|M|b]?'),
burst_time_rx = substring(burst_time from '[0-9]+[k|M|b]?/([0-9]+[k|M|b]?)'),
min_tx=substring(min_limit from '([0-9]+[k|M|b]?)/[0-9]+[k|M|b]?'),
min_rx = substring(min_limit from '[0-9]+[k|M|b]?/([0-9]+[k|M|b]?)');

UPDATE billservice_timespeed SET 
max_tx=substring(max_limit from '([0-9]+[k|M|b]?)/[0-9]+[k|M|b]?'),
max_rx = substring(max_limit from '[0-9]+[k|M|b]?/([0-9]+[k|M|b]?)'),
burst_tx = substring(burst_limit from '([0-9]+[k|M|b]?)/[0-9]+[k|M|b]?'),
burst_rx = substring(burst_limit from '[0-9]+[k|M|b]?/([0-9]+[k|M|b]?)'),
burst_treshold_tx = substring(burst_treshold from '([0-9]+[k|M|b]?)/[0-9]+[k|M|b]?'),
burst_treshold_rx = substring(burst_treshold from '[0-9]+[k|M|b?]/([0-9]+[k|M|b]?)'),
burst_time_tx = substring(burst_time from '([0-9]+[k|M|b]?)/[0-9]+[k|M|b]?'),
burst_time_rx = substring(burst_time from '[0-9]+[k|M|b]?/([0-9]+[k|M|b]?)'),
min_tx=substring(min_limit from '([0-9]+[k|M|b]?)/[0-9]+[k|M|b]?'),
min_rx = substring(min_limit from '[0-9]+[k|M|b]?/([0-9]+[k|M|b]?)');

UPDATE billservice_timespeed SET 
max_tx=substring(max_limit from '([0-9]+[k|M|b]?)/[0-9]+[k|M|b]?'),
max_rx = substring(max_limit from '[0-9]+[k|M|b]?/([0-9]+[k|M|b]?)'),
burst_tx = substring(burst_limit from '([0-9]+[k|M|b]?)/[0-9]+[k|M|b]?'),
burst_rx = substring(burst_limit from '[0-9]+[k|M|b]?/([0-9]+[k|M|b]?)'),
burst_treshold_tx = substring(burst_treshold from '([0-9]+[k|M|b]?)/[0-9]+[k|M|b]?'),
burst_treshold_rx = substring(burst_treshold from '[0-9]+[k|M|b?]/([0-9]+[k|M|b]?)'),
burst_time_tx = substring(burst_time from '([0-9]+[k|M|b]?)/[0-9]+[k|M|b]?'),
burst_time_rx = substring(burst_time from '[0-9]+[k|M|b]?/([0-9]+[k|M|b]?)'),
min_tx=substring(min_limit from '([0-9]+[k|M|b]?)/[0-9]+[k|M|b]?'),
min_rx = substring(min_limit from '[0-9]+[k|M|b]?/([0-9]+[k|M|b]?)');
