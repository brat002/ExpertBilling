CREATE OR REPLACE FUNCTION get_tarif(acc_id integer, dt timestamp without time zone)
  RETURNS integer AS
  $BODY$
  declare
  xxx int;
  begin
  SELECT tarif_id INTO xxx
    FROM billservice_accounttarif WHERE account_id=acc_id and datetime<dt ORDER BY datetime DESC LIMIT 1;
    RETURN xxx;
    end;
    $BODY$
      LANGUAGE plpgsql VOLATILE
        COST 100;
        
        