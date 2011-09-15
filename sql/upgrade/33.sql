BEGIN;
DROP TRIGGER a_set_deleted_trg on billservice_tariff;
ALTER TABLE billservice_account
  DROP CONSTRAINT billservice_account_ipnipinuse_fkey;
ALTER TABLE billservice_account
  DROP CONSTRAINT   billservice_account_vpnipinuse_fkey;
  
CREATE OR REPLACE FUNCTION billservice_account_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN

IF (TG_OP = 'DELETE') THEN
    DELETE FROM billservice_ipinuse WHERE id=OLD.ipn_ipinuse_id;
    DELETE FROM billservice_ipinuse WHERE id=OLD.vpn_ipinuse_id;
    DELETE FROM billservice_accountaddonservice WHERE account_id=OLD.id;
    DELETE FROM billservice_accountipnspeed WHERE account_id=OLD.id;
    DELETE FROM billservice_accountspeedlimit WHERE account_id=OLD.id;
    DELETE FROM billservice_accounttarif WHERE account_id=OLD.id;
    DELETE FROM billservice_accountviewednews WHERE account_id=OLD.id;
    DELETE FROM billservice_addonservicetransaction WHERE account_id=OLD.id;
    DELETE FROM billservice_balancehistory WHERE account_id=OLD.id;
    DELETE FROM billservice_document WHERE account_id=OLD.id;
    DELETE FROM billservice_groupstat WHERE account_id=OLD.id;
    DELETE FROM billservice_netflowstream WHERE account_id=OLD.id;
    DELETE FROM billservice_onetimeservicehistory WHERE account_id=OLD.id;
    DELETE FROM billservice_organization WHERE account_id=OLD.id;
    DELETE FROM billservice_periodicalservicehistory WHERE account_id=OLD.id;
    DELETE FROM billservice_shedulelog WHERE account_id=OLD.id;
    DELETE FROM billservice_subaccount WHERE account_id=OLD.id;
    DELETE FROM billservice_suspendedperiod WHERE account_id=OLD.id;
    DELETE FROM billservice_timetransaction WHERE account_id=OLD.id;
    DELETE FROM billservice_transaction WHERE account_id=OLD.id;
    DELETE FROM billservice_traffictransaction WHERE account_id=OLD.id;
    DELETE FROM billservice_x8021 WHERE account_id=OLD.id;
    DELETE FROM radius_activesession WHERE account_id=OLD.id;
    
    RETURN OLD;
END IF;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
  
CREATE TRIGGER billservice_account_trg
  BEFORE INSERT OR UPDATE OR DELETE
  ON billservice_account
  FOR EACH ROW
  EXECUTE PROCEDURE billservice_account_trg_fn();


ALTER TABLE billservice_accountaddonservice
  DROP CONSTRAINT   billservice_accountaddonservice_service_id_fkey;
  
ALTER TABLE billservice_accountaddonservice
  DROP CONSTRAINT   billservice_accountaddonservice_account_id_fkey;
  

CREATE OR REPLACE FUNCTION billservice_accountaddonservice_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN

IF (TG_OP = 'DELETE') THEN
    DELETE FROM billservice_addonservicetransaction WHERE accountaddonservice_id=OLD.id;
    RETURN OLD;
END IF;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
  
CREATE TRIGGER billservice_accountaddonservice_trg
  BEFORE INSERT OR UPDATE OR DELETE
  ON billservice_accountaddonservice
  FOR EACH ROW
  EXECUTE PROCEDURE billservice_accountaddonservice_trg_fn();

ALTER TABLE billservice_accountipnspeed
  DROP CONSTRAINT   billservice_accountipnspeed_account_id_fkey;

ALTER TABLE billservice_accountprepaystime
  DROP CONSTRAINT   account_tarif_id_refs_id_48fe22d0;
  
ALTER TABLE billservice_accountprepaystime
  DROP CONSTRAINT   billservice_accountprepaystime_prepaid_time_service_id_fkey;

ALTER TABLE billservice_accountprepaystrafic
  DROP CONSTRAINT   account_tarif_id_refs_id_7d07606a;
  
ALTER TABLE billservice_accountprepaystrafic
  DROP CONSTRAINT   billservice_accountprepaystrafic_prepaid_traffic_id_fkey;

ALTER TABLE billservice_accountspeedlimit
  DROP CONSTRAINT   billservice_accountspeedlimit_account_id_fkey;
  
ALTER TABLE billservice_accountspeedlimit
  DROP CONSTRAINT   billservice_accountspeedlimit_speedlimit_id_fkey;

ALTER TABLE billservice_accounttarif
  DROP CONSTRAINT   billservice_accounttarif_account_id_fkey;
  

ALTER TABLE billservice_accounttarif
  DROP CONSTRAINT   billservice_accounttarif_tarif_id_fkey;
  

CREATE OR REPLACE FUNCTION billservice_accounttarif_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN

IF (TG_OP = 'DELETE') THEN
    DELETE FROM billservice_accountprepaystime WHERE account_tarif_id=OLD.id;
    DELETE FROM billservice_accountprepaystrafic WHERE account_tarif_id=OLD.id;
    DELETE FROM billservice_addonservicetransaction WHERE accounttarif_id=OLD.id;
    DELETE FROM billservice_onetimeservicehistory WHERE accounttarif_id=OLD.id;
    DELETE FROM billservice_shedulelog WHERE accounttarif_id=OLD.id;
    
    RETURN OLD;
END IF;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
  
CREATE TRIGGER billservice_accounttarif_trg
  BEFORE INSERT OR UPDATE OR DELETE
  ON billservice_accounttarif
  FOR EACH ROW
  EXECUTE PROCEDURE billservice_accounttarif_trg_fn();

ALTER TABLE billservice_accountviewednews
  DROP CONSTRAINT   billservice_accountviewednews_account_id_fkey;
ALTER TABLE billservice_accountviewednews
  DROP CONSTRAINT   billservice_accountviewednews_news_id_fkey;

ALTER TABLE billservice_addonservice
  DROP CONSTRAINT   billservice_addonservice_nas_id_fkey;

ALTER TABLE billservice_addonservice
  DROP CONSTRAINT   billservice_addonservice_sp_period_id_fkey;
ALTER TABLE billservice_addonservice
  DROP CONSTRAINT   billservice_addonservice_timeperiod_id_fkey;
ALTER TABLE billservice_addonservice
  DROP CONSTRAINT   billservice_addonservice_wyte_period_id_fkey;

CREATE OR REPLACE FUNCTION billservice_addonservice_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN

IF (TG_OP = 'DELETE') THEN
    DELETE FROM billservice_accountaddonservice WHERE service_id=OLD.id;
    DELETE FROM billservice_addonservicetarif WHERE service_id=OLD.id;
    DELETE FROM billservice_addonservicetransaction WHERE service_id=OLD.id;
    RETURN OLD;
END IF;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

CREATE TRIGGER billservice_addonservice_trg
  BEFORE INSERT OR UPDATE OR DELETE
  ON billservice_addonservice
  FOR EACH ROW
  EXECUTE PROCEDURE billservice_addonservice_trg_fn();

ALTER TABLE billservice_addonservicetarif
  DROP CONSTRAINT   billservice_addonservicetarif_activation_count_period_id_fkey;
ALTER TABLE billservice_addonservicetarif
  DROP CONSTRAINT   billservice_addonservicetarif_service_id_fkey;
ALTER TABLE billservice_addonservicetarif
  DROP CONSTRAINT   billservice_addonservicetarif_tarif_id_fkey;


ALTER TABLE billservice_addonservicetransaction
  DROP CONSTRAINT   billservice_addonservicetransaction_account_id_fkey;
ALTER TABLE billservice_addonservicetransaction
  DROP CONSTRAINT   billservice_addonservicetransaction_accountaddonservice_id_fkey;

ALTER TABLE billservice_addonservicetransaction
  DROP CONSTRAINT   billservice_addonservicetransaction_accounttarif_id_fkey;
ALTER TABLE billservice_addonservicetransaction
  DROP CONSTRAINT   billservice_addonservicetransaction_service_id_fkey;
ALTER TABLE billservice_addonservicetransaction
  DROP CONSTRAINT   billservice_addonservicetransaction_type_id_fkey;

ALTER TABLE billservice_card
  DROP CONSTRAINT   billservice_card_account_fkey;
ALTER TABLE billservice_card
  DROP CONSTRAINT   billservice_card_ipinuse_fkey;
ALTER TABLE billservice_card
  DROP CONSTRAINT   billservice_card_nas_fkey;
ALTER TABLE billservice_card
  DROP CONSTRAINT   billservice_card_tarif_fkey;
ALTER TABLE billservice_card
  DROP CONSTRAINT   billservice_card_template_fkey;

ALTER TABLE billservice_dealer
  DROP CONSTRAINT   billservice_dealer_bank_id_fkey;
ALTER TABLE billservice_dealerpay
  DROP CONSTRAINT   billservice_dealerpay_dealer_id_fkey;
ALTER TABLE billservice_dealerpay
  DROP CONSTRAINT   billservice_dealerpay_salecard_id_fkey;
  
CREATE OR REPLACE FUNCTION billservice_dealer_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN

IF (TG_OP = 'DELETE') THEN
    DELETE FROM billservice_salecard WHERE id=OLD.dealer_id;
    DELETE FROM billservice_dealerpay WHERE id=OLD.dealer_id;
    RETURN OLD;
END IF;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

CREATE TRIGGER billservice_dealer_trg
  BEFORE INSERT OR UPDATE OR DELETE
  ON billservice_dealer
  FOR EACH ROW
  EXECUTE PROCEDURE billservice_dealer_trg_fn();

ALTER TABLE billservice_document
  DROP CONSTRAINT   billservice_document_account_id_fkey;
ALTER TABLE billservice_document
  DROP CONSTRAINT   billservice_document_type_id_fkey;

ALTER TABLE billservice_group_trafficclass
  DROP CONSTRAINT   billservice_group_trafficclass_group_id_fkey;
ALTER TABLE billservice_group_trafficclass
  DROP CONSTRAINT   billservice_group_trafficclass_trafficclass_id_fkey;

ALTER TABLE billservice_groupstat
  DROP CONSTRAINT   billservice_groupstat_account_id_fkey;
ALTER TABLE billservice_groupstat
  DROP CONSTRAINT   billservice_groupstat_group_id_fkey;

ALTER TABLE billservice_ipinuse
  DROP CONSTRAINT   billservice_ipinuse_pool_id_fkey;

ALTER TABLE billservice_log
  DROP CONSTRAINT   billservice_log_systemuser_id_fkey;

ALTER TABLE billservice_netflowstream
  DROP CONSTRAINT   billservice_netflowstream_account_id_fkey;
ALTER TABLE billservice_netflowstream
  DROP CONSTRAINT   billservice_netflowstream_nas_id_fkey;
ALTER TABLE billservice_netflowstream
  DROP CONSTRAINT   billservice_netflowstream_tarif_id_fkey;
ALTER TABLE billservice_netflowstream
  DROP CONSTRAINT   billservice_netflowstream_traffic_transmit_node_id_fkey;

ALTER TABLE billservice_onetimeservice
  DROP CONSTRAINT   billservice_onetimeservice_tarif_id_fkey;

  
CREATE OR REPLACE FUNCTION billservice_onetimeservice_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN

IF (TG_OP = 'DELETE') THEN
    DELETE FROM billservice_onetimeservicehistory WHERE onetimeservice_id=OLD.id;
    RETURN OLD;
END IF;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

CREATE TRIGGER billservice_onetimeservice_trg
  BEFORE INSERT OR UPDATE OR DELETE
  ON billservice_onetimeservice
  FOR EACH ROW
  EXECUTE PROCEDURE billservice_onetimeservice_trg_fn();

ALTER TABLE billservice_onetimeservicehistory
  DROP CONSTRAINT   billservice_onetimeservicehistory_accounttarif_id_fkey;
ALTER TABLE billservice_onetimeservicehistory
  DROP CONSTRAINT   billservice_onetimeservicehistory_onetimeservice_id_fkey;
ALTER TABLE billservice_onetimeservicehistory
  DROP CONSTRAINT   billservice_onetimeservicehistory_transaction_id_fkey;

ALTER TABLE billservice_operator
  DROP CONSTRAINT   billservice_operator_bank_id;

ALTER TABLE billservice_organization
  DROP CONSTRAINT   billservice_organization_account_id_fkey;

ALTER TABLE billservice_periodicalservice
  DROP CONSTRAINT   billservice_periodicalservice_settlement_period_id_fkey;
ALTER TABLE billservice_periodicalservice
  DROP CONSTRAINT   billservice_periodicalservice_tarif_id_fkey;    


CREATE OR REPLACE FUNCTION billservice_periodicalservice_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN

IF (TG_OP = 'DELETE') THEN
    DELETE FROM billservice_periodicalservicehistory WHERE service_id=OLD.id;
    RETURN OLD;
END IF;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

CREATE TRIGGER billservice_periodicalservice_trg
  BEFORE INSERT OR UPDATE OR DELETE
  ON billservice_periodicalservice
  FOR EACH ROW
  EXECUTE PROCEDURE billservice_periodicalservice_trg_fn();

ALTER TABLE billservice_periodicalservicehistory
  DROP CONSTRAINT   billservice_periodicalservicehistory_account_id_fkey;

ALTER TABLE billservice_prepaidtraffic
  DROP CONSTRAINT   billservice_prepaidtraffic_group_id_fkey;
ALTER TABLE billservice_prepaidtraffic
  DROP CONSTRAINT   traffic_transmit_service_id_refs_id_4797c3b9;  

ALTER TABLE billservice_radiusattrs
  DROP CONSTRAINT   billservice_radiusattrs_tarif_id_fkey;  

ALTER TABLE billservice_radiustrafficnode
  DROP CONSTRAINT   billservice_radiustrafficnode_radiustraffic_id_fkey;
ALTER TABLE billservice_radiustrafficnode
  DROP CONSTRAINT   billservice_radiustrafficnode_timeperiod_id_fkey;

ALTER TABLE billservice_salecard
  DROP CONSTRAINT   billservice_salecard_dealer_id_fkey;
  
CREATE OR REPLACE FUNCTION billservice_salecard_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN

IF (TG_OP = 'DELETE') THEN
    DELETE FROM billservice_salecard_cards WHERE salecard_id=OLD.id;
    UPDATE billservice_card SET sold=NULL WHERE id IN (SELECT card_id FROM billservice_salecard_cards WHERE salecard_id=OLD.id);
    RETURN OLD;
END IF;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

CREATE TRIGGER billservice_salecard_trg
  BEFORE INSERT OR UPDATE OR DELETE
  ON billservice_salecard
  FOR EACH ROW
  EXECUTE PROCEDURE billservice_salecard_trg_fn();

ALTER TABLE billservice_salecard_cards
  DROP CONSTRAINT   billservice_salecard_cards_salecard_id_fkey;

ALTER TABLE billservice_shedulelog
  DROP CONSTRAINT   billservice_shedulelog_account_id_fkey;
ALTER TABLE billservice_shedulelog
  DROP CONSTRAINT   billservice_shedulelog_accounttarif_id_fkey;

ALTER TABLE billservice_speedlimit
  DROP CONSTRAINT   billservice_speedlimit_limit_id_fkey;

ALTER TABLE billservice_subaccount
  DROP CONSTRAINT   billservice_subaccount_account_id_fkey;
ALTER TABLE billservice_subaccount
  DROP CONSTRAINT   billservice_subaccount_ipnipinuse_fkey;
ALTER TABLE billservice_subaccount
  DROP CONSTRAINT   billservice_subaccount_ipv6_vpnipinuse_fkey;
ALTER TABLE billservice_subaccount
  DROP CONSTRAINT   billservice_subaccount_vpnipinuse_fkey;

CREATE OR REPLACE FUNCTION billservice_subaccount_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN

IF (TG_OP = 'DELETE') THEN
    DELETE FROM billservice_ipinuse WHERE id=OLD.vpn_ipinuse_id;
    DELETE FROM billservice_ipinuse WHERE id=OLD.ipn_ipinuse_id;
    DELETE FROM billservice_ipinuse WHERE id=OLD.vpn_ipv6_ipinuse_id;
    DELETE FROM billservice_accountaddonservice WHERE subaccount_id=OLD.id;
    DELETE FROM radius_activesession WHERE subaccount_id=OLD.id;
    DELETE FROM radius_authlog WHERE subaccount_id=OLD.id;
    
    RETURN OLD;
END IF;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

CREATE TRIGGER billservice_subaccount_trg
  BEFORE INSERT OR UPDATE OR DELETE
  ON billservice_subaccount
  FOR EACH ROW
  EXECUTE PROCEDURE billservice_subaccount_trg_fn();

ALTER TABLE billservice_suspendedperiod
  DROP CONSTRAINT   billservice_suspendedperiod_account_id_fkey;

ALTER TABLE billservice_tariff
  DROP CONSTRAINT   billservice_tariff_settlement_period_id_fkey;
ALTER TABLE billservice_tariff
  DROP CONSTRAINT   billservice_tariff_time_access_service_id_fkey;
ALTER TABLE billservice_tariff
  DROP CONSTRAINT   billservice_tariff_traffic_transmit_service_id_fkey;
ALTER TABLE billservice_tariff
  DROP CONSTRAINT   billservice_tariff_vpn_ippool_id_fkey;
  
CREATE OR REPLACE FUNCTION billservice_tariff_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN

IF (TG_OP = 'DELETE') THEN
    DELETE FROM billservice_accountprepaystime WHERE tarif_id=OLD.id;
    DELETE FROM billservice_accountprepaystrafic WHERE tarif_id=OLD.id;
    DELETE FROM billservice_accounttarif WHERE tarif_id=OLD.id;
    DELETE FROM billservice_addonservicetarif WHERE tarif_id=OLD.id;
    DELETE FROM billservice_onetimeservice WHERE tarif_id=OLD.id;
    DELETE FROM billservice_periodicalservice WHERE tarif_id=OLD.id;
    DELETE FROM billservice_radiusattrs WHERE tarif_id=OLD.id;
    DELETE FROM billservice_traffictransmitservice WHERE id=OLD.traffic_transmit_service_id;
    DELETE FROM billservice_timeaccessservice WHERE id=OLD.time_access_service_id;
    DELETE FROM billservice_radiustraffic WHERE id=OLD.radius_traffic_transmit_service_id;
    DELETE FROM billservice_accessparameters WHERE id=OLD.access_parameters_id;
    DELETE FROM billservice_trafficlimit WHERE tarif_id=OLD.id;

    RETURN OLD;
END IF;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

CREATE TRIGGER billservice_tariff_trg
  BEFORE INSERT OR UPDATE OR DELETE
  ON billservice_tariff
  FOR EACH ROW
  EXECUTE PROCEDURE billservice_tariff_trg_fn();


 ALTER TABLE billservice_timeaccessnode
  DROP CONSTRAINT   billservice_timeaccessnode_time_period_id_fkey;

ALTER TABLE billservice_timetransaction
  DROP CONSTRAINT   billservice_timetransaction_account_id_fkey;
DROP TABLE billservice_trafficlimit_traffic_class;

ALTER TABLE billservice_traffictransaction
  DROP CONSTRAINT   billservice_traffictransaction_account_id_fkey;

ALTER TABLE billservice_transaction
  DROP CONSTRAINT   billservice_systemuser_fkey;

ALTER TABLE billservice_x8021
  DROP CONSTRAINT   billservice_x8021_account_id_fkey;
ALTER TABLE billservice_x8021
  DROP CONSTRAINT   billservice_x8021_nas_id_fkey;

CREATE OR REPLACE FUNCTION nas_trafficclass_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN

IF (TG_OP = 'DELETE') THEN
    DELETE FROM nas_trafficnode WHERE traffic_class_id=OLD.id;
    DELETE FROM billservice_group_trafficclass WHERE trafficclass_id=OLD.id;
    DELETE FROM billservice_traffictransmitnodes_traffic_class WHERE trafficclass_id=OLD.id;
    RETURN OLD;
END IF;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

CREATE TRIGGER nas_trafficclass_trg
  BEFORE INSERT OR UPDATE OR DELETE
  ON nas_trafficclass
  FOR EACH ROW
  EXECUTE PROCEDURE nas_trafficclass_trg_fn();

CREATE OR REPLACE FUNCTION billservice_traffictransmitservice_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN

IF (TG_OP = 'DELETE') THEN
    DELETE FROM billservice_traffictransmitnodes WHERE traffic_transmit_service_id_id=OLD.id;
    RETURN OLD;
END IF;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

CREATE TRIGGER billservice_traffictransmitservice_trg
  BEFORE INSERT OR UPDATE OR DELETE
  ON billservice_traffictransmitservice
  FOR EACH ROW
  EXECUTE PROCEDURE billservice_traffictransmitservice_trg_fn();

CREATE OR REPLACE FUNCTION billservice_traffictransmitnodes_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN

IF (TG_OP = 'DELETE') THEN
    DELETE FROM billservice_traffictransmitnodes_time_nodes WHERE traffictransmitnodes_id=OLD.id;
    DELETE FROM billservice_traffictransmitnodes_traffic_class WHERE traffictransmitnodes_id=OLD.id;
    RETURN OLD;
END IF;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

CREATE TRIGGER billservice_traffictransmitnodes_trg
  BEFORE INSERT OR UPDATE OR DELETE
  ON billservice_traffictransmitnodes
  FOR EACH ROW
  EXECUTE PROCEDURE billservice_traffictransmitnodes_trg_fn();



CREATE OR REPLACE FUNCTION billservice_timeaccessservice_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN

IF (TG_OP = 'DELETE') THEN
    DELETE FROM billservice_timeaccessnode WHERE time_access_service_id=OLD.id;
    RETURN OLD;
END IF;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

CREATE TRIGGER billservice_timeaccessservice_trg
  BEFORE INSERT OR UPDATE OR DELETE
  ON billservice_timeaccessservice
  FOR EACH ROW
  EXECUTE PROCEDURE billservice_timeaccessservice_trg_fn();

CREATE OR REPLACE FUNCTION billservice_timeperiod_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN

IF (TG_OP = 'DELETE') THEN
    DELETE FROM billservice_timeaccessnode WHERE time_period_id=OLD.id;
    DELETE FROM billservice_traffictransmitnodes_time_nodes WHERE timeperiod_id=OLD.id;
    DELETE FROM billservice_timeperiod_time_period_nodes WHERE timeperiod_id=OLD.id;
    DELETE FROM billservice_timespeed WHERE time_id=OLD.id;
    RETURN OLD;
END IF;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

CREATE TRIGGER billservice_timeperiod_trg
  BEFORE INSERT OR UPDATE OR DELETE
  ON billservice_timeperiod
  FOR EACH ROW
  EXECUTE PROCEDURE billservice_timeperiod_trg_fn();


COMMIT;

