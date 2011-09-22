INSERT INTO billservice_transactiontype(
            "name", internal_name, is_deletable)
    VALUES ('Перевод средств через услугу перевода баланса', 'MONEY_TRANSFER_TO', False);

INSERT INTO billservice_transactiontype(
            "name", internal_name, is_deletable)
    VALUES ('Получение средств через услугу перевода баланса', 'MONEY_TRANSFER_FROM', False);
