CREATE OR REPLACE FUNCTION get_dublicates_count(tr_id integer)
  RETURNS integer AS
$BODY$
declare

begin

RETURN (SELECT count(*) FROM billservice_transaction WHERE id=tr_id);
end;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION get_dublicates_count(integer)
  OWNER TO ebs;

CREATE OR REPLACE FUNCTION get_max_transaction_id()
  RETURNS integer AS
$BODY$
declare

begin

RETURN (SELECT max(id) FROM billservice_transaction);
end;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION get_max_transaction_id()
  OWNER TO ebs;
  
update billservice_transaction as t 
SET id=1+get_max_transaction_id() WHERE get_dublicates_count(id)>1;
