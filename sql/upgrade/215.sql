CREATE OR REPLACE FUNCTION free_unused_subaccount_ip_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN


IF (TG_OP = 'DELETE') THEN
    IF (OLD.ipn_ipinuse_id is not Null) THEN
        DELETE FROM billservice_ipinuse WHERE id=OLD.ipn_ipinuse_id;
    END IF;

    IF (OLD.vpn_ipinuse_id is not Null) THEN
        DELETE FROM billservice_ipinuse WHERE id=OLD.vpn_ipinuse_id;   
    END IF;

    IF (OLD.vpn_ipv6_ipinuse_id is not Null) THEN
        DELETE FROM billservice_ipinuse WHERE id=OLD.vpn_ipv6_ipinuse_id;   
    
    
    END IF;
    RETURN OLD;
    
END IF;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION free_unused_subaccount_ip_trg_fn()
  OWNER TO ebs;

DROP TRIGGER free_unused_account_ip_trg ON billservice_subaccount;
CREATE TRIGGER free_unused_account_ip_trg
  AFTER DELETE
  ON billservice_subaccount
  FOR EACH ROW
  EXECUTE PROCEDURE free_unused_subaccount_ip_trg_fn();
  
  