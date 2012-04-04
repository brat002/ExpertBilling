DROP FUNCTION traftrans_ins_trg_fn();

CREATE OR REPLACE FUNCTION traftrans_ins_trg_fn()
  RETURNS trigger AS
$BODY$
DECLARE
    cur_chk int;
    prev_chk int;
BEGIN



BEGIN
    
    EXECUTE traftrans_inserter(NEW);
EXCEPTION 
  WHEN undefined_table THEN
     EXECUTE  traftrans_crt_pdb(NEW.created::date);
     EXECUTE  traftrans_inserter(NEW);
END;
   
    RETURN NULL;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION traftrans_ins_trg_fn() OWNER TO ebs;


