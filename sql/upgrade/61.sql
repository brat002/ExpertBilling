CREATE OR REPLACE FUNCTION psh_ins_trg_fn()
  RETURNS trigger AS
$BODY$
DECLARE
    cur_chk int;
    prev_chk int;
BEGIN



BEGIN
EXECUTE psh_inserter(NEW);
    
EXCEPTION 
  WHEN undefined_table THEN
     EXECUTE  psh_crt_pdb(NEW.created::date);
     EXECUTE  psh_inserter(NEW);
END;
   
    RETURN NULL;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION psh_ins_trg_fn() OWNER TO ebs;
