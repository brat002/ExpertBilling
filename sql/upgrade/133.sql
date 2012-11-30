ALTER TABLE object_log_logitem ADD COLUMN changed_data text;
ALTER TABLE object_log_logitem ALTER COLUMN changed_data SET DEFAULT ''::text;

