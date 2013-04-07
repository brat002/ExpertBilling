SELECT setval('getpaid_payment_id_seq',(SELECT max(id) FROM qiwi_invoice));
