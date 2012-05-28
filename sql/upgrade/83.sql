ALTER TABLE billservice_systemuser DROP COLUMN role;
DROP TABLE IF EXISTS billservice_log;
DROP TABLE  IF EXISTS billservice_netflowstream;
DROP TABLE billservice_systemuser_group;
DROP TABLE  IF EXISTS billservice_systemgroup CASCADE;
