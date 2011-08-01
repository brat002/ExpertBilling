DROP TABLE IF EXISTS  auth_group CASCADE;
CREATE TABLE auth_group
(
  id serial NOT NULL,
  "name" character varying(80) NOT NULL,
  CONSTRAINT auth_group_pkey PRIMARY KEY (id),
  CONSTRAINT auth_group_name_key UNIQUE (name)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE auth_group OWNER TO ebs;

DROP TABLE   IF EXISTS  django_content_type CASCADE;

CREATE TABLE django_content_type
(
  id serial NOT NULL,
  "name" character varying(100) NOT NULL,
  app_label character varying(100) NOT NULL,
  model character varying(100) NOT NULL,
  CONSTRAINT django_content_type_pkey PRIMARY KEY (id),
  CONSTRAINT django_content_type_app_label_key UNIQUE (app_label, model)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE django_content_type OWNER TO ebs;
DROP TABLE   IF EXISTS  auth_user CASCADE;

CREATE TABLE auth_user
(
  id serial NOT NULL,
  username character varying(256) NOT NULL,
  first_name character varying(256) NOT NULL,
  last_name character varying(256) NOT NULL,
  email character varying(75) NOT NULL,
  "password" character varying(128) NOT NULL,
  is_staff boolean NOT NULL,
  is_active boolean NOT NULL,
  is_superuser boolean NOT NULL,
  last_login timestamp without time zone NOT NULL,
  date_joined timestamp without time zone NOT NULL,
  CONSTRAINT auth_user_pkey PRIMARY KEY (id),
  CONSTRAINT auth_user_username_key UNIQUE (username)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE auth_user OWNER TO ebs;

DROP TABLE   IF EXISTS  auth_permission CASCADE;

CREATE TABLE auth_permission
(
  id serial NOT NULL,
  "name" character varying(150) NOT NULL,
  content_type_id integer NOT NULL,
  codename character varying(100) NOT NULL,
  CONSTRAINT auth_permission_pkey PRIMARY KEY (id),
  CONSTRAINT auth_permission_content_type_id_fkey FOREIGN KEY (content_type_id)
      REFERENCES django_content_type (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT auth_permission_content_type_id_key UNIQUE (content_type_id, codename)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE auth_permission OWNER TO ebs;

DROP TABLE   IF EXISTS  auth_group_permissions CASCADE;

CREATE TABLE auth_group_permissions
(
  id serial NOT NULL,
  group_id integer NOT NULL,
  permission_id integer NOT NULL,
  CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id),
  CONSTRAINT auth_group_permissions_group_id_fkey FOREIGN KEY (group_id)
      REFERENCES auth_group (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT auth_group_permissions_permission_id_fkey FOREIGN KEY (permission_id)
      REFERENCES auth_permission (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT auth_group_permissions_group_id_key UNIQUE (group_id, permission_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE auth_group_permissions OWNER TO ebs;

DROP TABLE   IF EXISTS  auth_message CASCADE;

CREATE TABLE auth_message
(
  id serial NOT NULL,
  user_id integer NOT NULL,
  message text NOT NULL,
  CONSTRAINT auth_message_pkey PRIMARY KEY (id),
  CONSTRAINT auth_message_user_id_fkey FOREIGN KEY (user_id)
      REFERENCES auth_user (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
)
WITH (
  OIDS=FALSE
);
ALTER TABLE auth_message OWNER TO ebs;

DROP TABLE   IF EXISTS  auth_permission CASCADE;

CREATE TABLE auth_permission
(
  id serial NOT NULL,
  "name" character varying(50) NOT NULL,
  content_type_id integer NOT NULL,
  codename character varying(100) NOT NULL,
  CONSTRAINT auth_permission_pkey PRIMARY KEY (id),
  CONSTRAINT auth_permission_content_type_id_fkey FOREIGN KEY (content_type_id)
      REFERENCES django_content_type (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT auth_permission_content_type_id_key UNIQUE (content_type_id, codename)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE auth_permission OWNER TO ebs;

DROP  TABLE   IF EXISTS  django_admin_log CASCADE;

CREATE TABLE django_admin_log
(
  id serial NOT NULL,
  action_time timestamp without time zone NOT NULL,
  user_id integer NOT NULL,
  content_type_id integer,
  object_id text,
  object_repr character varying(200) NOT NULL,
  action_flag smallint NOT NULL,
  change_message text NOT NULL,
  CONSTRAINT django_admin_log_pkey PRIMARY KEY (id),
  CONSTRAINT django_admin_log_content_type_id_fkey FOREIGN KEY (content_type_id)
      REFERENCES django_content_type (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE  DEFERRABLE INITIALLY IMMEDIATE,
  CONSTRAINT django_admin_log_user_id_fkey FOREIGN KEY (user_id)
      REFERENCES auth_user (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE  DEFERRABLE INITIALLY IMMEDIATE,
  CONSTRAINT django_admin_log_action_flag_check CHECK (action_flag >= 0)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE django_admin_log OWNER TO ebs;

-- Index: django_admin_log_content_type_id

-- DROP INDEX django_admin_log_content_type_id;

CREATE INDEX django_admin_log_content_type_id
  ON django_admin_log
  USING btree
  (content_type_id);

-- Index: django_admin_log_user_id

-- DROP INDEX django_admin_log_user_id;

CREATE INDEX django_admin_log_user_id
  ON django_admin_log
  USING btree
  (user_id);
  
DROP TABLE   IF EXISTS  django_session CASCADE;

CREATE TABLE django_session
(
  session_key character varying(40) NOT NULL,
  session_data text NOT NULL,
  expire_date timestamp without time zone NOT NULL,
  CONSTRAINT django_session_pkey PRIMARY KEY (session_key)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE django_session OWNER TO ebs;


DROP TABLE   IF EXISTS  django_site CASCADE;

CREATE TABLE django_site
(
  id serial NOT NULL,
  "domain" character varying(100) NOT NULL,
  "name" character varying(50) NOT NULL,
  CONSTRAINT django_site_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE django_site OWNER TO ebs;

INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (1, 'Can add permission', 1, 'add_permission');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (2, 'Can change permission', 1, 'change_permission');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (3, 'Can delete permission', 1, 'delete_permission');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (4, 'Can add group', 2, 'add_group');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (5, 'Can change group', 2, 'change_group');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (6, 'Can delete group', 2, 'delete_group');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (7, 'Can add user', 3, 'add_user');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (8, 'Can change user', 3, 'change_user');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (9, 'Can delete user', 3, 'delete_user');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (10, 'Can add message', 4, 'add_message');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (11, 'Can change message', 4, 'change_message');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (12, 'Can delete message', 4, 'delete_message');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (13, 'Can add content type', 5, 'add_contenttype');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (14, 'Can change content type', 5, 'change_contenttype');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (15, 'Can delete content type', 5, 'delete_contenttype');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (16, 'Can add session', 6, 'add_session');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (17, 'Can change session', 6, 'change_session');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (18, 'Can delete session', 6, 'delete_session');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (19, 'Can add site', 7, 'add_site');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (20, 'Can change site', 7, 'change_site');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (21, 'Can delete site', 7, 'delete_site');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (22, 'Can add log entry', 8, 'add_logentry');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (23, 'Can change log entry', 8, 'change_logentry');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (24, 'Can delete log entry', 8, 'delete_logentry');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (25, 'Can add session', 9, 'add_session');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (26, 'Can change session', 9, 'change_session');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (27, 'Can delete session', 9, 'delete_session');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (28, 'Can add active session', 10, 'add_activesession');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (29, 'Can change active session', 10, 'change_activesession');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (30, 'Can delete active session', 10, 'delete_activesession');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (31, 'Can add auth log', 63, 'add_authlog');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (32, 'Can change auth log', 63, 'change_authlog');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (33, 'Can delete auth log', 63, 'delete_authlog');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (34, 'Can add Сервер доступа', 11, 'add_nas');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (35, 'Can change Сервер доступа', 11, 'change_nas');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (36, 'Can delete Сервер доступа', 11, 'delete_nas');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (37, 'Can add Класс трафика', 12, 'add_trafficclass');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (38, 'Can change Класс трафика', 12, 'change_trafficclass');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (39, 'Can delete Класс трафика', 12, 'delete_trafficclass');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (40, 'Can add Направление трафика', 13, 'add_trafficnode');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (41, 'Can change Направление трафика', 13, 'change_trafficnode');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (42, 'Can delete Направление трафика', 13, 'delete_trafficnode');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (43, 'Can add Нода временного периода', 14, 'add_timeperiodnode');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (44, 'Can change Нода временного периода', 14, 'change_timeperiodnode');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (45, 'Can delete Нода временного периода', 14, 'delete_timeperiodnode');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (46, 'Can add Временной период', 15, 'add_timeperiod');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (47, 'Can change Временной период', 15, 'change_timeperiod');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (48, 'Can delete Временной период', 15, 'delete_timeperiod');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (49, 'Can add Расчётный период', 16, 'add_settlementperiod');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (50, 'Can change Расчётный период', 16, 'change_settlementperiod');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (51, 'Can delete Расчётный период', 16, 'delete_settlementperiod');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (52, 'Can add Периодическая услуга', 17, 'add_periodicalservice');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (53, 'Can change Периодическая услуга', 17, 'change_periodicalservice');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (54, 'Can delete Периодическая услуга', 17, 'delete_periodicalservice');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (55, 'Can add История проводок по пер. услугам', 18, 'add_periodicalservicehistory');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (56, 'Can change История проводок по пер. услугам', 18, 'change_periodicalservicehistory');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (57, 'Can delete История проводок по пер. услугам', 18, 'delete_periodicalservicehistory');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (58, 'Can add Разовый платеж', 19, 'add_onetimeservice');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (59, 'Can change Разовый платеж', 19, 'change_onetimeservice');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (60, 'Can delete Разовый платеж', 19, 'delete_onetimeservice');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (61, 'Can add one time service history', 39, 'add_onetimeservicehistory');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (62, 'Can change one time service history', 39, 'change_onetimeservicehistory');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (63, 'Can delete one time service history', 39, 'delete_onetimeservicehistory');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (64, 'Can add Доступ с учётом времени', 20, 'add_timeaccessservice');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (65, 'Can change Доступ с учётом времени', 20, 'change_timeaccessservice');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (66, 'Can delete Доступ с учётом времени', 20, 'delete_timeaccessservice');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (67, 'Can add Период доступа', 21, 'add_timeaccessnode');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (68, 'Can change Период доступа', 21, 'change_timeaccessnode');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (69, 'Can delete Период доступа', 21, 'delete_timeaccessnode');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (70, 'Can add Параметры доступа', 22, 'add_accessparameters');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (71, 'Can change Параметры доступа', 22, 'change_accessparameters');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (72, 'Can delete Параметры доступа', 22, 'delete_accessparameters');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (73, 'Can add настройка скорости', 23, 'add_timespeed');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (74, 'Can change настройка скорости', 23, 'change_timespeed');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (75, 'Can delete настройка скорости', 23, 'delete_timespeed');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (76, 'Can add Предоплаченный трафик', 24, 'add_prepaidtraffic');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (77, 'Can change Предоплаченный трафик', 24, 'change_prepaidtraffic');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (78, 'Can delete Предоплаченный трафик', 24, 'delete_prepaidtraffic');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (79, 'Can add Доступ с учётом трафика', 25, 'add_traffictransmitservice');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (80, 'Can change Доступ с учётом трафика', 25, 'change_traffictransmitservice');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (81, 'Can delete Доступ с учётом трафика', 25, 'delete_traffictransmitservice');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (82, 'Can add цена за направление', 26, 'add_traffictransmitnodes');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (83, 'Can change цена за направление', 26, 'change_traffictransmitnodes');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (84, 'Can delete цена за направление', 26, 'delete_traffictransmitnodes');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (176, 'Can change account speed limit', 57, 'change_accountspeedlimit');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (85, 'Can add Предоплаченый трафик пользователя', 27, 'add_accountprepaystrafic');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (86, 'Can change Предоплаченый трафик пользователя', 27, 'change_accountprepaystrafic');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (87, 'Can delete Предоплаченый трафик пользователя', 27, 'delete_accountprepaystrafic');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (88, 'Can add Предоплаченый radius трафик пользователя', 84, 'add_accountprepaysradiustrafic');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (89, 'Can change Предоплаченый radius трафик ', 84, 'change_accountprepaysradiustrafic');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (90, 'Can delete Предоплаченый radius трафик ', 84, 'delete_accountprepaysradiustrafic');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (91, 'Can add Предоплаченное время пользователя', 28, 'add_accountprepaystime');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (92, 'Can change Предоплаченное время пользователя', 28, 'change_accountprepaystime');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (93, 'Can delete Предоплаченное время пользователя', 28, 'delete_accountprepaystime');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (94, 'Can add лимит трафика', 29, 'add_trafficlimit');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (95, 'Can change лимит трафика', 29, 'change_trafficlimit');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (96, 'Can delete лимит трафика', 29, 'delete_trafficlimit');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (97, 'Can add Тариф', 30, 'add_tariff');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (98, 'Can change Тариф', 30, 'change_tariff');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (99, 'Can delete Тариф', 30, 'delete_tariff');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (100, 'Can add Аккаунт', 31, 'add_account');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (101, 'Can change Аккаунт', 31, 'change_account');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (102, 'Can delete Аккаунт', 31, 'delete_account');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (103, 'Can add organization', 49, 'add_organization');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (104, 'Can change organization', 49, 'change_organization');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (105, 'Can delete organization', 49, 'delete_organization');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (106, 'Can add Тип проводки', 32, 'add_transactiontype');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (107, 'Can change Тип проводки', 32, 'change_transactiontype');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (108, 'Can delete Тип проводки', 32, 'delete_transactiontype');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (109, 'Can add Проводка', 33, 'add_transaction');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (110, 'Can change Проводка', 33, 'change_transaction');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (111, 'Can delete Проводка', 33, 'delete_transaction');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (112, 'Can add привязка', 34, 'add_accounttarif');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (113, 'Can change привязка', 34, 'change_accounttarif');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (114, 'Can delete привязка', 34, 'delete_accounttarif');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (115, 'Can add скорости IPN клиентов', 35, 'add_accountipnspeed');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (116, 'Can change скорости IPN клиентов', 35, 'change_accountipnspeed');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (117, 'Can delete скорости IPN клиентов', 35, 'delete_accountipnspeed');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (118, 'Can add NetFlow статистика', 37, 'add_netflowstream');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (119, 'Can change NetFlow статистика', 37, 'change_netflowstream');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (120, 'Can delete NetFlow статистика', 37, 'delete_netflowstream');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (121, 'Can add Периодическая операция', 38, 'add_shedulelog');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (122, 'Can change Периодическая операция', 38, 'change_shedulelog');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (123, 'Can delete Периодическая операция', 38, 'delete_shedulelog');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (124, 'Can add system group', 64, 'add_systemgroup');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (125, 'Can change system group', 64, 'change_systemgroup');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (126, 'Can delete system group', 64, 'delete_systemgroup');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (127, 'Can add system user', 40, 'add_systemuser');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (128, 'Can change system user', 40, 'change_systemuser');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (129, 'Can delete system user', 40, 'delete_systemuser');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (130, 'Can add ports', 41, 'add_ports');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (131, 'Can change ports', 41, 'change_ports');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (132, 'Can delete ports', 41, 'delete_ports');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (133, 'Can add document type', 50, 'add_documenttype');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (134, 'Can change document type', 50, 'change_documenttype');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (135, 'Can delete document type', 50, 'delete_documenttype');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (136, 'Can add template type', 83, 'add_templatetype');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (137, 'Can change template type', 83, 'change_templatetype');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (138, 'Can delete template type', 83, 'delete_templatetype');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (139, 'Can add template', 51, 'add_template');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (140, 'Can change template', 51, 'change_template');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (141, 'Can delete template', 51, 'delete_template');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (142, 'Can add card', 43, 'add_card');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (143, 'Can change card', 43, 'change_card');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (144, 'Can delete card', 43, 'delete_card');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (145, 'Can add bank data', 45, 'add_bankdata');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (146, 'Can change bank data', 45, 'change_bankdata');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (147, 'Can delete bank data', 45, 'delete_bankdata');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (148, 'Can add operator', 44, 'add_operator');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (149, 'Can change operator', 44, 'change_operator');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (150, 'Can delete operator', 44, 'delete_operator');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (151, 'Can add dealer', 46, 'add_dealer');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (152, 'Can change dealer', 46, 'change_dealer');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (153, 'Can delete dealer', 46, 'delete_dealer');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (154, 'Can add sale card', 47, 'add_salecard');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (155, 'Can change sale card', 47, 'change_salecard');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (156, 'Can delete sale card', 47, 'delete_salecard');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (157, 'Can add dealer pay', 48, 'add_dealerpay');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (158, 'Can change dealer pay', 48, 'change_dealerpay');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (159, 'Can delete dealer pay', 48, 'delete_dealerpay');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (160, 'Can add document', 52, 'add_document');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (161, 'Can change document', 52, 'change_document');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (162, 'Can delete document', 52, 'delete_document');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (163, 'Can add suspended period', 53, 'add_suspendedperiod');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (164, 'Can change suspended period', 53, 'change_suspendedperiod');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (165, 'Can delete suspended period', 53, 'delete_suspendedperiod');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (166, 'Can add group', 54, 'add_group');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (167, 'Can change group', 54, 'change_group');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (168, 'Can delete group', 54, 'delete_group');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (169, 'Can add group stat', 55, 'add_groupstat');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (170, 'Can change group stat', 55, 'change_groupstat');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (171, 'Can delete group stat', 55, 'delete_groupstat');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (172, 'Can add speed limit', 56, 'add_speedlimit');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (173, 'Can change speed limit', 56, 'change_speedlimit');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (174, 'Can delete speed limit', 56, 'delete_speedlimit');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (175, 'Can add account speed limit', 57, 'add_accountspeedlimit');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (177, 'Can delete account speed limit', 57, 'delete_accountspeedlimit');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (178, 'Can add ip pool', 58, 'add_ippool');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (179, 'Can change ip pool', 58, 'change_ippool');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (180, 'Can delete ip pool', 58, 'delete_ippool');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (181, 'Can add ip in use', 59, 'add_ipinuse');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (182, 'Can change ip in use', 59, 'change_ipinuse');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (183, 'Can delete ip in use', 59, 'delete_ipinuse');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (184, 'Can add traffic transaction', 65, 'add_traffictransaction');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (185, 'Can change traffic transaction', 65, 'change_traffictransaction');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (186, 'Can delete traffic transaction', 65, 'delete_traffictransaction');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (187, 'Can add tp change rule', 66, 'add_tpchangerule');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (188, 'Can change tp change rule', 66, 'change_tpchangerule');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (189, 'Can delete tp change rule', 66, 'delete_tpchangerule');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (190, 'Can add radius attrs', 67, 'add_radiusattrs');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (191, 'Can change radius attrs', 67, 'change_radiusattrs');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (192, 'Can delete radius attrs', 67, 'delete_radiusattrs');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (193, 'Can add x8021', 68, 'add_x8021');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (194, 'Can change x8021', 68, 'change_x8021');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (195, 'Can delete x8021', 68, 'delete_x8021');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (196, 'Can add addon service', 69, 'add_addonservice');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (197, 'Can change addon service', 69, 'change_addonservice');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (198, 'Can delete addon service', 69, 'delete_addonservice');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (199, 'Can add addon service tarif', 70, 'add_addonservicetarif');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (200, 'Can change addon service tarif', 70, 'change_addonservicetarif');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (201, 'Can delete addon service tarif', 70, 'delete_addonservicetarif');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (202, 'Can add account addon service', 71, 'add_accountaddonservice');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (203, 'Can change account addon service', 71, 'change_accountaddonservice');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (204, 'Can delete account addon service', 71, 'delete_accountaddonservice');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (205, 'Can add addon service transaction', 72, 'add_addonservicetransaction');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (206, 'Can change addon service transaction', 72, 'change_addonservicetransaction');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (207, 'Can delete addon service transaction', 72, 'delete_addonservicetransaction');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (208, 'Can add account attributes', 73, 'add_accountattributes');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (209, 'Can change account attributes', 73, 'change_accountattributes');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (210, 'Can delete account attributes', 73, 'delete_accountattributes');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (211, 'Can add account attributes data', 74, 'add_accountattributesdata');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (212, 'Can change account attributes data', 74, 'change_accountattributesdata');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (213, 'Can delete account attributes data', 74, 'delete_accountattributesdata');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (214, 'Can add news', 75, 'add_news');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (215, 'Can change news', 75, 'change_news');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (216, 'Can delete news', 75, 'delete_news');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (217, 'Can add account viewed news', 76, 'add_accountviewednews');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (218, 'Can change account viewed news', 76, 'change_accountviewednews');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (219, 'Can delete account viewed news', 76, 'delete_accountviewednews');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (220, 'Can add log', 77, 'add_log');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (221, 'Can change log', 77, 'change_log');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (222, 'Can delete log', 77, 'delete_log');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (223, 'Can add sub account', 78, 'add_subaccount');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (224, 'Can change sub account', 78, 'change_subaccount');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (225, 'Can delete sub account', 78, 'delete_subaccount');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (226, 'Can add balance history', 79, 'add_balancehistory');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (227, 'Can change balance history', 79, 'change_balancehistory');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (228, 'Can delete balance history', 79, 'delete_balancehistory');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (229, 'Can add city', 80, 'add_city');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (230, 'Can change city', 80, 'change_city');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (231, 'Can delete city', 80, 'delete_city');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (232, 'Can add street', 81, 'add_street');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (233, 'Can change street', 81, 'change_street');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (234, 'Can delete street', 81, 'delete_street');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (235, 'Can add house', 82, 'add_house');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (236, 'Can change house', 82, 'change_house');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (237, 'Can delete house', 82, 'delete_house');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (238, 'Can add radius traffic', 85, 'add_radiustraffic');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (239, 'Can change radius traffic', 85, 'change_radiustraffic');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (240, 'Can delete radius traffic', 85, 'delete_radiustraffic');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (241, 'Can add radius traffic node', 86, 'add_radiustrafficnode');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (242, 'Can change radius traffic node', 86, 'change_radiustrafficnode');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (243, 'Can delete radius traffic node', 86, 'delete_radiustrafficnode');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (244, 'Can add purse', 87, 'add_purse');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (245, 'Can change purse', 87, 'change_purse');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (246, 'Can delete purse', 87, 'delete_purse');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (247, 'Can add invoice', 88, 'add_invoice');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (248, 'Can change invoice', 88, 'change_invoice');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (249, 'Can delete invoice', 88, 'delete_invoice');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (250, 'Can add payment', 89, 'add_payment');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (251, 'Can change payment', 89, 'change_payment');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (252, 'Can delete payment', 89, 'delete_payment');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (253, 'Can add invoice', 90, 'add_invoice');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (254, 'Can change invoice', 90, 'change_invoice');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (255, 'Can delete invoice', 90, 'delete_invoice');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (256, 'Can add queue', 62, 'add_queue');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (257, 'Can change queue', 62, 'change_queue');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (258, 'Can delete queue', 62, 'delete_queue');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (259, 'Can add ticket', 61, 'add_ticket');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (260, 'Can change ticket', 61, 'change_ticket');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (261, 'Can delete ticket', 61, 'delete_ticket');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (262, 'Can add follow up', 91, 'add_followup');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (263, 'Can change follow up', 91, 'change_followup');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (264, 'Can delete follow up', 91, 'delete_followup');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (265, 'Can add ticket change', 92, 'add_ticketchange');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (266, 'Can change ticket change', 92, 'change_ticketchange');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (267, 'Can delete ticket change', 92, 'delete_ticketchange');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (268, 'Can add attachment', 93, 'add_attachment');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (269, 'Can change attachment', 93, 'change_attachment');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (270, 'Can delete attachment', 93, 'delete_attachment');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (271, 'Can add pre set reply', 94, 'add_presetreply');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (272, 'Can change pre set reply', 94, 'change_presetreply');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (273, 'Can delete pre set reply', 94, 'delete_presetreply');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (274, 'Can add escalation exclusion', 95, 'add_escalationexclusion');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (275, 'Can change escalation exclusion', 95, 'change_escalationexclusion');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (276, 'Can delete escalation exclusion', 95, 'delete_escalationexclusion');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (277, 'Can add email template', 96, 'add_emailtemplate');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (278, 'Can change email template', 96, 'change_emailtemplate');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (279, 'Can delete email template', 96, 'delete_emailtemplate');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (280, 'Can add knowledge base category', 97, 'add_kbcategory');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (281, 'Can change knowledge base category', 97, 'change_kbcategory');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (282, 'Can delete knowledge base category', 97, 'delete_kbcategory');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (283, 'Can add knowledge base item', 98, 'add_kbitem');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (284, 'Can change knowledge base item', 98, 'change_kbitem');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (285, 'Can delete knowledge base item', 98, 'delete_kbitem');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (286, 'Can add saved search', 99, 'add_savedsearch');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (287, 'Can change saved search', 99, 'change_savedsearch');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (288, 'Can delete saved search', 99, 'delete_savedsearch');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (289, 'Can add User Settings', 100, 'add_usersettings');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (290, 'Can change User Settings', 100, 'change_usersettings');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (291, 'Can delete User Settings', 100, 'delete_usersettings');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (292, 'Can add ignored email', 101, 'add_ignoreemail');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (293, 'Can change ignored email', 101, 'change_ignoreemail');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (294, 'Can delete ignored email', 101, 'delete_ignoreemail');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (295, 'Can add ticket CC', 102, 'add_ticketcc');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (296, 'Can change ticket CC', 102, 'change_ticketcc');
INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (297, 'Can delete ticket CC', 102, 'delete_ticketcc');
