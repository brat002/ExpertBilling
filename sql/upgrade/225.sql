ALTER TABLE nas_trafficnode ADD COLUMN src_ip  inet DEFAULT '0.0.0.0/0'::inet;
DELETE FROM ebsadmin_tablesettings WHERE name='TrafficNodeTable';