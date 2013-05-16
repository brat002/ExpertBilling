CREATE TABLE "radius_radiusstat" (
    "id" serial NOT NULL PRIMARY KEY,
    "nas_id" integer REFERENCES "nas_nas" ("id") DEFERRABLE INITIALLY DEFERRED,
    "start" integer CHECK ("start" >= 0) NOT NULL,
    "alive" integer CHECK ("alive" >= 0) NOT NULL,
    "end" integer CHECK ("end" >= 0) NOT NULL,
    "datetime" timestamp with time zone NOT NULL
)
;

CREATE INDEX "radius_radiusstat_nas_id" ON "radius_radiusstat" ("nas_id");
CREATE INDEX "radius_radiusstat_datetime" ON "radius_radiusstat" ("datetime");


CREATE OR REPLACE FUNCTION radiusstat_insert(nas_id_ integer, start_ integer, alive_ integer, end_ integer, datetime_ timestamp without time zone)
  RETURNS void AS
$BODY$ 
DECLARE
        datetime_agg_ timestamp without time zone;
        ins_tr_id_ int;
BEGIN   

    datetime_agg_ := date_trunc('minute', datetime_); 
    UPDATE radius_radiusstat SET start=COALESCE(start, 0)+COALESCE(start_,0), alive=COALESCE(alive, 0)+COALESCE(alive_, 0), "end"=COALESCE("end", 0)+COALESCE(end_, 0) WHERE nas_id=nas_id_  and datetime=datetime_agg_;
    IF NOT FOUND THEN
        INSERT INTO radius_radiusstat(nas_id, start, alive, "end", datetime) VALUES (nas_id_, COALESCE(start_,0), COALESCE(alive_,0), COALESCE(end_,0), datetime_agg_) RETURNING id INTO ins_tr_id_;
    END IF;

    RETURN;  
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;