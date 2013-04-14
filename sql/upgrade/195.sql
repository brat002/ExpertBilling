CREATE OR REPLACE RULE billservice_totaltransactionreport_delete AS ON DELETE TO billservice_totaltransactionreport
    DO INSTEAD(SELECT 1);