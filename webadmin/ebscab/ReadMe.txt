Запуск web-кабинета

Запуск web-кабинета состоит из следующих действий:

1.В файле конфигурации (settings.py) необходимо изменить следующие строчки:

	•DATABASE_ENGINE  - 'postgresql_psycopg2'
	•DATABASE_NAME  - Имя  БД
	•DATABASE_USER – Имя администратора БД
	•DATABASE_PASSWORD – Пароль пользователя БД
	•DATABASE_HOST – Хост на котором находиться БД
	•DATABASE_PORT – Порт, на котором работает БД
	•RPC_ADDRESS  - Адрес RPC сервера
	•RPC_USER  - Имя пользователя (из Администраторов)
	•RPC_PASSWORD  - Пароль пользователя (из Администраторов)

	Пример:

	DATABASE_ENGINE = 'postgresql_psycopg2'         
	DATABASE_NAME = 'ebs1'             
	DATABASE_USER = 'ebs'             
	DATABASE_PASSWORD = 'ebspassword'         
	DATABASE_HOST = '127.0.0.1'
	DATABASE_PORT = '5432' 

	RPC_ADDRESS = '127.0.0.1'
	RPC_USER  = 'webadmin'
	RPC_PASSWORD = 'RPCwebadmin'

2.Для того, чтобы веб-кабинет мог получать графики загрузки канала
необходимо добавить пользователя "webadmin" с паролем "RPCwebadmin" 
в Администраторы через EBSClient (Главное меню->Администраторы) и 
разрешить ему подключаться только с 127.0.0.1/32

