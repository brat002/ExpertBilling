-- Function: free_unused_account_ip_trg_fn()

-- DROP FUNCTION free_unused_account_ip_trg_fn();

CREATE OR REPLACE FUNCTION free_unused_subaccount_ip_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN


IF (TG_OP = 'UPDATE') THEN
    IF (NEW.vpn_ipinuse_id is Null and OLD.vpn_ipinuse_id is not Null) THEN
        DELETE FROM billservice_ipinuse WHERE id=OLD.vpn_ipinuse_id;
    END IF;
    
    IF (NEW.ipn_ipinuse_id is Null and OLD.ipn_ipinuse_id is not Null) THEN
        DELETE FROM billservice_ipinuse WHERE id=OLD.ipn_ipinuse_id;
    END IF;

    IF (NEW.vpn_ipv6_ipinuse_id is Null and OLD.vpn_ipv6_ipinuse_id is not Null) THEN
        DELETE FROM billservice_ipinuse WHERE id=OLD.vpn_ipv6_ipinuse_id;
    END IF;
    
    RETURN NEW;

ELSIF (TG_OP = 'DELETE') THEN
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
RETURN OLD;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION free_unused_account_ip_trg_fn() OWNER TO ebs;

-- Trigger: free_unused_account_ip_trg on billservice_account

-- DROP TRIGGER free_unused_account_ip_trg ON billservice_account;

CREATE TRIGGER free_unused_account_ip_trg
  AFTER UPDATE OR DELETE
  ON billservice_subaccount
  FOR EACH ROW
  EXECUTE PROCEDURE free_unused_subaccount_ip_trg_fn();


