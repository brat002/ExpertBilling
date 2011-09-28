CREATE INDEX billservice_accounttarif_datetime_idx
   ON billservice_accounttarif (datetime ASC NULLS LAST);

CREATE INDEX billservice_account_id_idx
   ON billservice_account (id ASC NULLS LAST);

CREATE INDEX nas_trafficclass_id_idx
   ON nas_trafficclass (id ASC NULLS LAST);

CREATE INDEX billservice_tariff_id_idx
   ON billservice_tariff (id ASC NULLS LAST);

CREATE INDEX billservice_timeperiodnodes_idx
   ON billservice_timeperiod_time_period_nodes (timeperiod_id ASC NULLS LAST);
CREATE INDEX billservice_traffictransmitnodes_timenodes_idx
   ON billservice_traffictransmitnodes_time_nodes (traffictransmitnodes_id ASC NULLS LAST);
