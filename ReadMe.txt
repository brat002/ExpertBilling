������ web-��������

������ web-�������� ������� �� ��������� ��������:

1.� ����� ������������ (settings.py) ���������� �������� ��������� �������:

	�DATABASE_ENGINE  - 'postgresql_psycopg2'
	�DATABASE_NAME  - ���  ��
	�DATABASE_USER � ��� �������������� ��
	�DATABASE_PASSWORD � ������ ������������ ��
	�DATABASE_HOST � ���� �� ������� ���������� ��
	�DATABASE_PORT � ����, �� ������� �������� ��
	�RPC_ADDRESS  - ����� RPC �������
	�RPC_USER  - ��� ������������ (�� ���������������)
	�RPC_PASSWORD  - ������ ������������ (�� ���������������)

	������:

	DATABASE_ENGINE = 'postgresql_psycopg2'         
	DATABASE_NAME = 'ebs1'             
	DATABASE_USER = 'ebs'             
	DATABASE_PASSWORD = 'ebspassword'         
	DATABASE_HOST = '127.0.0.1'
	DATABASE_PORT = '5432' 

	RPC_ADDRESS = '127.0.0.1'
	RPC_USER  = 'webadmin'
	RPC_PASSWORD = 'RPCwebadmin'

2.��� ����, ����� ���-������� ��� �������� ������� �������� ������
���������� �������� ������������ "webadmin" � ������� "RPCwebadmin" 
� �������������� ����� EBSClient (������� ����->��������������) � 
��������� ��� ������������ ������ � 127.0.0.1/32

