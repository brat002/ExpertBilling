--psql -d ebs -f SHAREDIR/contrib/_int.sql
--psql -d ebs -f SHAREDIR/contrib/int_aggregate.sql
--psql -h localhost -p 5432 -U ebs -d ebs -f /usr/share/postgresql/8.3/contrib/_int.sql
--psql -h localhost -p 5432 -U ebs -d ebs -f /usr/share/postgresql/8.3/contrib/int_aggregate.sql

ALTER TABLE billservice_traffictransmitnodes ADD COLUMN group_id integer;

ALTER TABLE billservice_trafficlimit DROP COLUMN in_direction;
ALTER TABLE billservice_trafficlimit DROP COLUMN out_direction;
ALTER TABLE billservice_trafficlimit ADD COLUMN group_id integer;

CREATE TABLE billservice_group
(
  id serial NOT NULL,
  "name" character varying(255) NOT NULL,
  direction integer NOT NULL,
  "type" integer NOT NULL,
  CONSTRAINT billservice_group_pkey PRIMARY KEY (id)
)
WITH (OIDS=FALSE);
ALTER TABLE billservice_group OWNER TO ebs;

CREATE TABLE billservice_group_trafficclass
(
  id serial NOT NULL,
  group_id integer NOT NULL,
  trafficclass_id integer NOT NULL,
  CONSTRAINT billservice_group_trafficclass_pkey PRIMARY KEY (id),
  CONSTRAINT billservice_group_trafficclass_group_id_fkey FOREIGN KEY (group_id)
      REFERENCES billservice_group (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT billservice_group_trafficclass_trafficclass_id_fkey FOREIGN KEY (trafficclass_id)
      REFERENCES nas_trafficclass (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT billservice_group_trafficclass_group_id_key UNIQUE (group_id, trafficclass_id)
)
WITH (OIDS=FALSE);
ALTER TABLE billservice_group_trafficclass OWNER TO ebs;

CREATE TABLE billservice_groupstat
(
  id serial NOT NULL,
  group_id integer NOT NULL,
  account_id integer NOT NULL,
  bytes integer NOT NULL,
  datetime timestamp without time zone NOT NULL,
  classes integer[],
  classbytes integer[],
  max_class integer,
  CONSTRAINT billservice_groupstat_pkey PRIMARY KEY (id),
  CONSTRAINT billservice_groupstat_account_id_fkey FOREIGN KEY (account_id)
      REFERENCES billservice_account (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT billservice_groupstat_group_id_fkey FOREIGN KEY (group_id)
      REFERENCES billservice_group (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT billservice_groupstat_group_id_key UNIQUE (group_id, account_id, datetime)
)
WITH (OIDS=FALSE);
ALTER TABLE billservice_groupstat OWNER TO ebs;

CREATE INDEX billservice_groupstat_account_id
  ON billservice_groupstat
  USING btree
  (account_id);

CREATE INDEX billservice_groupstat_datetime
  ON billservice_groupstat
  USING btree
  (datetime);


CREATE INDEX billservice_groupstat_gr_acc_dt_id
  ON billservice_groupstat
  USING btree
  (group_id, account_id, datetime);


CREATE TABLE billservice_globalstat
(
  id serial NOT NULL,
  account_id integer NOT NULL,
  bytes_in bigint NOT NULL DEFAULT 0,
  bytes_out bigint NOT NULL DEFAULT 0,
  datetime timestamp without time zone NOT NULL,
  nas_id integer NOT NULL,
  classes integer[],
  classbytes bigint[][],
  CONSTRAINT billservice_globalstat_pkey PRIMARY KEY (id),
  CONSTRAINT billservice_globalstat_account_id_fkey FOREIGN KEY (account_id)
      REFERENCES billservice_account (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT billservice_globalstat_acc_dt_uq_key UNIQUE (account_id, datetime)
)
WITH (OIDS=FALSE);
ALTER TABLE billservice_globalstat OWNER TO ebs;

CREATE INDEX billservice_globalstat_acc_dt_id
  ON billservice_globalstat
  USING btree
  (account_id, datetime);

CREATE INDEX billservice_globalstat_account_id
  ON billservice_globalstat
  USING btree
  (account_id);

CREATE INDEX billservice_globalstat_datetime
  ON billservice_globalstat
  USING btree
  (datetime);


CREATE OR REPLACE FUNCTION group_type1_fn(group_id_ integer, account_id_ integer, octets_ integer, datetime_ timestamp without time zone, classes_ integer[], classbytes_ integer[], max_class_ integer)
  RETURNS void AS
$BODY$
BEGIN
    INSERT INTO billservice_groupstat (group_id, account_id, bytes, datetime, classes, classbytes, max_class) VALUES (group_id_, account_id_, octets_, datetime_, classes_, classbytes_ , max_class_);
EXCEPTION WHEN unique_violation THEN
    UPDATE billservice_groupstat SET bytes=bytes+octets_ WHERE group_id=group_id_ AND account_id=account_id_ AND datetime=datetime_;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
ALTER FUNCTION group_type1_fn(integer, integer, integer, timestamp without time zone, integer[], integer[], integer) OWNER TO ebs;

CREATE OR REPLACE FUNCTION group_type2_fn(group_id_ integer, account_id_ integer, octets_ integer, datetime_ timestamp without time zone, classes_ integer[], classbytes_ integer[], max_class_ integer)
  RETURNS void AS
$BODY$
DECLARE
    old_classes_ int[];
    old_classbytes_  int[];


    i int;
    ilen int;
    j int;
    max_ int;
    maxclass_ int;
    nbytes int;
    nclass int;
    --jlen int;
BEGIN
    INSERT INTO billservice_groupstat (group_id, account_id, bytes, datetime, classes, classbytes, max_class) VALUES (group_id_, account_id_, octets_, datetime_, classes_, classbytes_ , max_class_);
EXCEPTION WHEN unique_violation THEN
    SELECT classes, classbytes INTO old_classes_ ,old_classbytes_ FROM billservice_groupstat WHERE group_id=group_id_ AND account_id=account_id_ AND datetime=datetime_ FOR UPDATE;
    ilen := icount(classes_);
    max_ := 0;
    maxclass_ := NULL;
    --jlen := icount(old_classes_);
    FOR i IN 1..ilen LOOP
        nclass := classes_[i];
        nbytes := classbytes_[i];
        j := idx(old_classes_, nclass);
        IF j = 0 THEN
	    old_classes_ := array_append(old_classes_, nclass);
	    old_classbytes_ := array_append(old_classbytes_, nbytes);
	    IF nbytes > max_ THEN
	        max_ := nbytes;
	        maxclass_ := nclass;
	    END IF;
	ELSE
	    old_classbytes_[j] := old_classbytes_[j] + nbytes;
	    IF old_classbytes_[j] > max_ THEN
	        max_ := old_classbytes_[j];
	        maxclass_ := nclass;
	    END IF;
	END IF;      
    END LOOP;    
    UPDATE billservice_groupstat SET bytes=max_, max_class=maxclass_, classes=old_classes_, classbytes=old_classbytes_ WHERE group_id=group_id_ AND account_id=account_id_ AND datetime=datetime_;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
ALTER FUNCTION group_type2_fn(integer, integer, integer, timestamp without time zone, integer[], integer[], integer) OWNER TO ebs;

CREATE OR REPLACE FUNCTION global_stat_fn(account_id_ integer, bytes_in_ bigint, bytes_out_ bigint, datetime_ timestamp without time zone, nas_id_ integer, classes_ integer[], classbytes_ bigint[])
  RETURNS void AS
$BODY$
DECLARE
    old_classes_ int[];
    old_classbytes_  bigint[][];


    i int;
    ilen int;
    j int;

    nbytes_in  bigint;
    nbytes_out bigint;
    nclass int;
    --jlen int;
BEGIN
    INSERT INTO billservice_globalstat (account_id, bytes_in, bytes_out, datetime, nas_id, classes, classbytes) VALUES (account_id_, bytes_in_, bytes_out_,datetime_, nas_id_, classes_, classbytes_);
EXCEPTION WHEN unique_violation THEN
    SELECT classes, classbytes INTO old_classes_ ,old_classbytes_ FROM billservice_globalstat WHERE account_id=account_id_ AND datetime=datetime_ FOR UPDATE;
    ilen := icount(classes_);

    --jlen := icount(old_classes_);
    FOR i IN 1..ilen LOOP
        nclass := classes_[i];
        nbytes_in  := classbytes_[i][1];
        nbytes_out := classbytes_[i][2];
        j := idx(old_classes_, nclass);
        IF j = 0 THEN
	    old_classes_ := array_append(old_classes_, nclass);
	    old_classbytes_ := array_cat(old_classbytes_, ARRAY[nbytes_in ,nbytes_out]);
	ELSE
	    old_classbytes_[j][1] := old_classbytes_[j][1] + nbytes_in;
	    old_classbytes_[j][2] := old_classbytes_[j][2] + nbytes_out;
	END IF;      
    END LOOP;    
    UPDATE billservice_globalstat SET bytes_in=bytes_in+bytes_in_, bytes_out=bytes_out+bytes_out_, classes=old_classes_, classbytes=old_classbytes_ WHERE account_id=account_id_ AND datetime=datetime_;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
ALTER FUNCTION global_stat_fn(integer, bigint, bigint, timestamp without time zone, integer, integer[], bigint[]) OWNER TO ebs;
