CREATE OR REPLACE FUNCTION get_ballance_for_date(account_id_ integer, datetime_ timestamp without time zone)
  RETURNS numeric AS
$BODY$ 
BEGIN 

  RETURN  COALESCE((SELECT balance FROM billservice_balancehistory WHERE account_id=account_id_ and datetime<datetime_ ORDER BY datetime DESC LIMIT 1), 0);

  END; 

  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
