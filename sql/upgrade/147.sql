update billservice_systemuser set is_superuser=True WHERE username='admin';
DELETE FROM billservice_systemuser WHERE username='webadmin';
