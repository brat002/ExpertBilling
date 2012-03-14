DROP VIEW IF EXISTS billservice_totaltransactionreport;
CREATE OR REPLACE VIEW billservice_totaltransactionreport(id, service_id, service_name, "table", created,tariff_id,summ,account_id,type_id,systemuser_id,bill,description,end_promise, promise_expired) AS
SELECT psh.id, 
	psh.service_id,
	(select name from billservice_periodicalservice where id=psh.service_id),
	'billservice_periodicalservicehistory',
	psh.created, 
	(SELECT tarif_id FROM billservice_accounttarif where id=psh.accounttarif_id) as tarif,
	psh.summ, 
	psh.account_id,
	psh.type_id, 
	Null,'','',Null,Null
FROM billservice_periodicalservicehistory as psh
UNION ALL
SELECT transaction.id,
	NULL,
	'',
	'billservice_transaction',
	transaction.created,  
	(SELECT tarif_id FROM billservice_accounttarif where id=transaction.accounttarif_id) as tarif,
	transaction.summ*(-1),
	transaction.account_id, 
	transaction.type_id as type,
	transaction.systemuser_id,
	transaction.bill,transaction.description,end_promise,promise_expired
FROM billservice_transaction as transaction
UNION ALL
SELECT tr.id, 
	NULL,
	'',
	'billservice_traffictransaction',
	tr.created, 
	(SELECT tarif_id FROM billservice_accounttarif where id=tr.accounttarif_id) as tarif, 
	tr.summ, tr.account_id,
	'NETFLOW_BILL',
	Null,'','',Null,Null
FROM billservice_traffictransaction as tr
UNION ALL
SELECT addst.id, 
	addst.service_id,
	(select name from billservice_addonservice where id=addst.service_id),
    'billservice_addonservicetransaction',
	addst.created, 
	(SELECT tarif_id FROM billservice_accounttarif where id=addst.accounttarif_id) as tarif,
	addst.summ,
	addst.account_id
	,addst.type_id,
	Null,'','',Null,Null
FROM billservice_addonservicetransaction as addst
UNION ALL
SELECT osh.id, 
	osh.onetimeservice_id,
	'',
	'billservice_onetimeservicehistory',
        osh.created,
        (SELECT tarif_id FROM billservice_accounttarif where id=osh.accounttarif_id) as tarif,
        osh.summ, 
        osh.account_id, 
        'ONETIME_SERVICE',Null,'','',Null,Null
            FROM billservice_onetimeservicehistory as osh 
UNION ALL
SELECT tr.id, 
	NULL,
	'',
	'billservice_timetransaction',
	tr.created, 
	(SELECT tarif_id FROM billservice_accounttarif where id=tr.accounttarif_id) as tarif,
	tr.summ, 
	tr.account_id, 
	'TIME_ACCESS',Null,'','',Null,Null
            FROM billservice_timetransaction as tr 
UNION ALL
SELECT qi.id as id, 
	NULL,
	'',
	'qiwi_payment',
	qi.created,
	get_tarif(qi.account_id,qi.created) as tarif,
	qi.summ,
	qi.account_id,
	'qiwi_payment',Null,qi.autoaccept::text, qi.date_accepted::text ,Null,Null
            FROM qiwi_invoice as qi            
;

