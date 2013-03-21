INSERT INTO billservice_templatetype(id, name) VALUES(10, 'SMS сообщение о недостатке баланса');
INSERT INTO billservice_template (name, type_id, body) VALUES ('Баланс меньше', 10, 'Ваш баланс равен {{account.ballance}}. Во избежание блокировки не забудьте пополнить счёт.');
