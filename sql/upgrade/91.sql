INSERT INTO billservice_transactiontype(
            name, internal_name, is_deletable)
    VALUES ('Обещанный платёж', 'PROMISE_PAYMENT', 'False');
    
INSERT INTO billservice_transactiontype(
            name, internal_name, is_deletable)
    VALUES ('Списание обещанного платёжа', 'PROMISE_DEBIT', 'False');
    
UPDATE billservice_transaction SET type_id='PROMISE_PAYMENT' WHERE promise=True;