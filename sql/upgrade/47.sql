CREATE OR REPLACE FUNCTION billservice_tariff_trg_fn()
  RETURNS trigger AS
$BODY$
BEGIN

IF (TG_OP = 'DELETE') THEN
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