ALTER TABLE nas_trafficnode ADD COLUMN in_index integer DEFAULT 0;

ALTER TABLE nas_trafficnode ADD COLUMN out_index integer DEFAULT 0;

ALTER TABLE nas_trafficnode ADD COLUMN src_as integer DEFAULT 0;

ALTER TABLE nas_trafficnode ADD COLUMN dst_as integer DEFAULT 0;
