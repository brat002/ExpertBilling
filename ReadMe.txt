������ web-��������

������ web-�������� ������� �� ��������� ��������:

1.� ����� ������������ (settings.py) ���������� �������� ��������� �������:

	�DATABASE_ENGINE  - ������� �� 
	  ���� ��������� 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3', 'ado_mssql'.
	�DATABASE_NAME  - ���  ��
	�DATABASE_USER � ��� �������������� ��
	�DATABASE_PASSWORD � ������ ��������������
	�DATABASE_HOST � ���� �� ������� ���������� ��
	�DATABASE_PORT � ���� ��� ������ � ��
	�CHILD_ADDRESS  - ����� RPC �������

	������:

	DATABASE_ENGINE = 'postgresql_psycopg2'         
	DATABASE_NAME = 'ebs_ref_2'             
	DATABASE_USER = 'mikrobill'             
	DATABASE_PASSWORD = '1234'         
	DATABASE_HOST = '10.10.1.1'             
	DATABASE_PORT = '' 

	CHILD_ADDRESS = '127.0.0.1'

2.� ������� billservice_systemuser (��������� ������������) ���������� �������� ������������ "webadmin" � ������� �RPCwebadmin�
