-- View: billservice_totaltransactionreport

-- DROP VIEW billservice_totaltransactionreport;

CREATE OR REPLACE VIEW billservice_totaltransactionreport AS 
        (        (        (        (        (         SELECT psh.id, psh.service_id, ( SELECT billservice_periodicalservice.name
                                                           FROM billservice_periodicalservice
                                                          WHERE billservice_periodicalservice.id = psh.service_id) AS service_name, 'billservice_periodicalservicehistory'::text AS "table", psh.created, ( SELECT billservice_accounttarif.tarif_id
                                                           FROM billservice_accounttarif
                                                          WHERE billservice_accounttarif.id = psh.accounttarif_id) AS tariff_id, psh.summ, psh.account_id, psh.type_id, NULL::integer AS systemuser_id, ''::character varying AS bill, ''::text AS description, NULL::timestamp without time zone AS end_promise, NULL::boolean AS promise_expired
                                                   FROM billservice_periodicalservicehistory psh
                                        UNION ALL 
                                                 SELECT transaction.id, NULL::integer AS service_id, ''::character varying AS service_name, 'billservice_transaction'::text AS "table", transaction.created, ( SELECT billservice_accounttarif.tarif_id
                                                           FROM billservice_accounttarif
                                                          WHERE billservice_accounttarif.id = transaction.accounttarif_id) AS tariff_id, transaction.summ::numeric AS summ, transaction.account_id, transaction.type_id, transaction.systemuser_id, transaction.bill, transaction.description, transaction.end_promise, transaction.promise_expired
                                                   FROM billservice_transaction transaction)
                                UNION ALL 
                                         SELECT tr.id, NULL::integer AS service_id, ''::character varying AS service_name, 'billservice_traffictransaction'::text AS "table", tr.created, ( SELECT billservice_accounttarif.tarif_id
                                                   FROM billservice_accounttarif
                                                  WHERE billservice_accounttarif.id = tr.accounttarif_id) AS tariff_id, tr.summ, tr.account_id, 'NETFLOW_BILL'::character varying AS type_id, NULL::integer AS systemuser_id, ''::character varying AS bill, ''::text AS description, NULL::timestamp without time zone AS end_promise, NULL::boolean AS promise_expired
                                           FROM billservice_traffictransaction tr)
                        UNION ALL 
                                 SELECT addst.id, addst.service_id, ( SELECT billservice_addonservice.name
                                           FROM billservice_addonservice
                                          WHERE billservice_addonservice.id = addst.service_id) AS service_name, 'billservice_addonservicetransaction'::text AS "table", addst.created, ( SELECT billservice_accounttarif.tarif_id
                                           FROM billservice_accounttarif
                                          WHERE billservice_accounttarif.id = addst.accounttarif_id) AS tariff_id, addst.summ, addst.account_id, addst.type_id, NULL::integer AS systemuser_id, ''::character varying AS bill, ''::text AS description, NULL::timestamp without time zone AS end_promise, NULL::boolean AS promise_expired
                                   FROM billservice_addonservicetransaction addst)
                UNION ALL 
                         SELECT osh.id, osh.onetimeservice_id AS service_id, ''::character varying AS service_name, 'billservice_onetimeservicehistory'::text AS "table", osh.created, ( SELECT billservice_accounttarif.tarif_id
                                   FROM billservice_accounttarif
                                  WHERE billservice_accounttarif.id = osh.accounttarif_id) AS tariff_id, osh.summ, osh.account_id, 'ONETIME_SERVICE'::character varying AS type_id, NULL::integer AS systemuser_id, ''::character varying AS bill, ''::text AS description, NULL::timestamp without time zone AS end_promise, NULL::boolean AS promise_expired
                           FROM billservice_onetimeservicehistory osh)
        UNION ALL 
                 SELECT tr.id, NULL::integer AS service_id, ''::character varying AS service_name, 'billservice_timetransaction'::text AS "table", tr.created, ( SELECT billservice_accounttarif.tarif_id
                           FROM billservice_accounttarif
                          WHERE billservice_accounttarif.id = tr.accounttarif_id) AS tariff_id, tr.summ, tr.account_id, 'TIME_ACCESS'::character varying AS type_id, NULL::integer AS systemuser_id, ''::character varying AS bill, ''::text AS description, NULL::timestamp without time zone AS end_promise, NULL::boolean AS promise_expired
                   FROM billservice_timetransaction tr)
UNION ALL 
         SELECT qi.id, NULL::integer AS service_id, ''::character varying AS service_name, 'qiwi_payment'::text AS "table", qi.created, get_tarif(qi.account_id, qi.created) AS tariff_id, qi.summ, qi.account_id, 'qiwi_payment'::character varying AS type_id, NULL::integer AS systemuser_id, qi.autoaccept::text AS bill, qi.date_accepted::text AS description, NULL::timestamp without time zone AS end_promise, NULL::boolean AS promise_expired
           FROM qiwi_invoice qi;

ALTER TABLE billservice_totaltransactionreport
  OWNER TO ebs;


