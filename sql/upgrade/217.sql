CREATE OR REPLACE FUNCTION radius_activesession_ins_trg_fn()
  RETURNS trigger AS
$BODY$
DECLARE
    cur_chk boolean;
    table_name text;
BEGIN
    table_name:='radaccts'||to_char(NEW.date_start, 'YYYYMM01');
    select INTO cur_chk exists(select relname from pg_class where relname = table_name::text and relkind='r');
    
    IF cur_chk = True THEN
        EXECUTE 'INSERT INTO ' || table_name || ' SELECT (' || quote_literal(NEW) || '::' || TG_RELID::regclass || ').*';
    ELSE 
        BEGIN
            PERFORM radius_activesession_trs_crt_pdb(NEW.date_start::date);
            EXECUTE 'INSERT INTO ' || table_name || ' SELECT (' || quote_literal(NEW) || '::' || TG_RELID::regclass || ').*';
        EXCEPTION 
          WHEN duplicate_table THEN
            EXECUTE 'INSERT INTO ' || table_name || ' SELECT (' || quote_literal(NEW) || '::' || TG_RELID::regclass || ').*';
        END;
     END IF;
        
        
    RETURN NULL;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
  