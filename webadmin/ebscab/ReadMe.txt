«апуск web-кабинета

«апуск web-кабинета состоит из следующих действий:

1.¬ файле конфигурации (settings.py) необходимо изменить следующие строчки:

	ХDATABASE_ENGINE  - 'postgresql_psycopg2'
	ХDATABASE_NAME  - »м€  Ѕƒ
	ХDATABASE_USER Ц »м€ администратора Ѕƒ
	ХDATABASE_PASSWORD Ц ѕароль пользовател€ Ѕƒ
	ХDATABASE_HOST Ц ’ост на котором находитьс€ Ѕƒ
	ХDATABASE_PORT Ц ѕорт, на котором работает Ѕƒ
	ХRPC_ADDRESS  - јдрес RPC сервера
	ХRPC_USER  - »м€ пользовател€ (из јдминистраторов)
	ХRPC_PASSWORD  - ѕароль пользовател€ (из јдминистраторов)

	ѕример:

	DATABASE_ENGINE = 'postgresql_psycopg2'         
	DATABASE_NAME = 'ebs1'             
	DATABASE_USER = 'ebs'             
	DATABASE_PASSWORD = 'ebspassword'         
	DATABASE_HOST = '127.0.0.1'
	DATABASE_PORT = '5432' 

	RPC_ADDRESS = '127.0.0.1'
	RPC_USER  = 'webadmin'
	RPC_PASSWORD = 'RPCwebadmin'

2.ƒл€ того, чтобы веб-кабинет мог получать графики загрузки канала
необходимо добавить пользовател€ "webadmin" с паролем "RPCwebadmin" 
в јдминистраторы через EBSClient (√лавное меню->јдминистраторы) и 
разрешить ему подключатьс€ только с 127.0.0.1/32

