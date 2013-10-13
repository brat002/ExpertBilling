ALTER TABLE billservice_ipinuse ADD COLUMN last_update timestamp without time zone;
update billservice_ipinuse SET last_update=now() WHERE id in (SELECT ipinuse_id FROM radius_activesession WHERE session_status='ACTIVE' and ipinuse_id is not null);

