«апуск web-кабинета

«апуск web-кабинета состоит из следующих действий:

1.¬ файле конфигурации (settings.py) необходимо изменить следующие строчки:

	ХDATABASE_ENGINE  - ƒрайвер Ѕƒ 
	  ¬иды драйверов 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3', 'ado_mssql'.
	ХDATABASE_NAME  - »м€  Ѕƒ
	ХDATABASE_USER Ц »м€ администратора Ѕƒ
	ХDATABASE_PASSWORD Ц ѕароль администратора
	ХDATABASE_HOST Ц ’ост на котором находитьс€ Ѕƒ
	ХDATABASE_PORT Ц ѕорт дл€ работы с Ѕƒ
	ХCHILD_ADDRESS  - јдрес RPC сервера

	ѕример:

	DATABASE_ENGINE = 'postgresql_psycopg2'         
	DATABASE_NAME = 'ebs_ref_2'             
	DATABASE_USER = 'mikrobill'             
	DATABASE_PASSWORD = '1234'         
	DATABASE_HOST = '10.10.1.1'             
	DATABASE_PORT = '' 

	CHILD_ADDRESS = '127.0.0.1'

2.¬ таблицу billservice_systemuser (—истемные пользователи) необходимо добавить пользовател€ "webadmin" с паролем УRPCwebadminФ
