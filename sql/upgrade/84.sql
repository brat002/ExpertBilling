
DROP TABLE IF EXISTS auth_group_permissions;
DROP TABLE  IF EXISTS auth_group;

DROP TABLE IF EXISTS auth_permission;
DROP TABLE IF EXISTS auth_group_permissions;

DROP TABLE IF EXISTS django_content_type CASCADE;

DROP TABLE IF EXISTS auth_user_user_permissions;


DROP TABLE IF EXISTS auth_user_groups;







CREATE TABLE django_content_type
(
  id serial NOT NULL,
  name character varying(100) NOT NULL,
  app_label character varying(100) NOT NULL,
  model character varying(100) NOT NULL,
  CONSTRAINT django_content_type_pkey PRIMARY KEY (id ),
  CONSTRAINT django_content_type_app_label_model_key UNIQUE (app_label , model )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE django_content_type
  OWNER TO ebs;
  



CREATE TABLE auth_permission
(
  id serial NOT NULL,
  name character varying(50) NOT NULL,
  content_type_id integer NOT NULL,
  codename character varying(100) NOT NULL,
  CONSTRAINT auth_permission_pkey PRIMARY KEY (id ),
  CONSTRAINT content_type_id_refs_id_728de91f FOREIGN KEY (content_type_id)
      REFERENCES django_content_type (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT auth_permission_content_type_id_codename_key UNIQUE (content_type_id , codename )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE auth_permission
  OWNER TO ebs;


CREATE INDEX auth_permission_content_type_id
  ON auth_permission
  USING btree
  (content_type_id );

CREATE TABLE auth_group
(
  id serial NOT NULL,
  name character varying(80) NOT NULL,
  CONSTRAINT auth_group_pkey PRIMARY KEY (id ),
  CONSTRAINT auth_group_name_key UNIQUE (name )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE auth_group
  OWNER TO ebs;
  
CREATE TABLE auth_group_permissions
(
  id serial NOT NULL,
  group_id integer NOT NULL,
  permission_id integer NOT NULL,
  CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id ),
  CONSTRAINT auth_group_permissions_permission_id_fkey FOREIGN KEY (permission_id)
      REFERENCES auth_permission (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT group_id_refs_id_3cea63fe FOREIGN KEY (group_id)
      REFERENCES auth_group (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT auth_group_permissions_group_id_permission_id_key UNIQUE (group_id , permission_id )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE auth_group_permissions
  OWNER TO ebs;

-- Index: auth_group_permissions_group_id

-- DROP INDEX auth_group_permissions_group_id;

CREATE INDEX auth_group_permissions_group_id
  ON auth_group_permissions
  USING btree
  (group_id );

-- Index: auth_group_permissions_permission_id

-- DROP INDEX auth_group_permissions_permission_id;

CREATE INDEX auth_group_permissions_permission_id
  ON auth_group_permissions
  USING btree
  (permission_id );
  


 CREATE TABLE auth_user_user_permissions
(
  id serial NOT NULL,
  user_id integer NOT NULL,
  permission_id integer NOT NULL,
  CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id ),
  CONSTRAINT auth_user_user_permissions_permission_id_fkey FOREIGN KEY (permission_id)
      REFERENCES auth_permission (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT user_id_refs_id_dfbab7d FOREIGN KEY (user_id)
      REFERENCES auth_user (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT auth_user_user_permissions_user_id_permission_id_key UNIQUE (user_id , permission_id )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE auth_user_user_permissions
  OWNER TO ebs;

-- Index: auth_user_user_permissions_permission_id

-- DROP INDEX auth_user_user_permissions_permission_id;

CREATE INDEX auth_user_user_permissions_permission_id
  ON auth_user_user_permissions
  USING btree
  (permission_id );

-- Index: auth_user_user_permissions_user_id

-- DROP INDEX auth_user_user_permissions_user_id;

CREATE INDEX auth_user_user_permissions_user_id
  ON auth_user_user_permissions
  USING btree
  (user_id );
 
CREATE TABLE auth_user_groups
(
  id serial NOT NULL,
  user_id integer NOT NULL,
  group_id integer NOT NULL,
  CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id ),
  CONSTRAINT auth_user_groups_group_id_fkey FOREIGN KEY (group_id)
      REFERENCES auth_group (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT user_id_refs_id_7ceef80f FOREIGN KEY (user_id)
      REFERENCES auth_user (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT auth_user_groups_user_id_group_id_key UNIQUE (user_id , group_id )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE auth_user_groups
  OWNER TO ebs;

-- Index: auth_user_groups_group_id

-- DROP INDEX auth_user_groups_group_id;

CREATE INDEX auth_user_groups_group_id
  ON auth_user_groups
  USING btree
  (group_id );

-- Index: auth_user_groups_user_id

-- DROP INDEX auth_user_groups_user_id;

CREATE INDEX auth_user_groups_user_id
  ON auth_user_groups
  USING btree
  (user_id );
  
INSERT INTO auth_group VALUES (3, 'Менеджеры');
INSERT INTO auth_group VALUES (2, 'Кассиры');
INSERT INTO auth_group VALUES (4, 'Администраторы');


INSERT INTO django_content_type VALUES (1, 'permission', 'auth', 'permission');
INSERT INTO django_content_type VALUES (2, 'group', 'auth', 'group');
INSERT INTO django_content_type VALUES (3, 'user', 'auth', 'user');
INSERT INTO django_content_type VALUES (4, 'message', 'auth', 'message');
INSERT INTO django_content_type VALUES (5, 'content type', 'contenttypes', 'contenttype');
INSERT INTO django_content_type VALUES (6, 'session', 'sessions', 'session');
INSERT INTO django_content_type VALUES (7, 'site', 'sites', 'site');
INSERT INTO django_content_type VALUES (8, 'log entry', 'admin', 'logentry');
INSERT INTO django_content_type VALUES (9, 'active session', 'radius', 'activesession');
INSERT INTO django_content_type VALUES (10, 'auth log', 'radius', 'authlog');
INSERT INTO django_content_type VALUES (11, 'Сервер доступа', 'nas', 'nas');
INSERT INTO django_content_type VALUES (12, 'Класс трафика', 'nas', 'trafficclass');
INSERT INTO django_content_type VALUES (13, 'Направление трафика', 'nas', 'trafficnode');
INSERT INTO django_content_type VALUES (14, 'switch', 'nas', 'switch');
INSERT INTO django_content_type VALUES (15, 'Нода временного периода', 'billservice', 'timeperiodnode');
INSERT INTO django_content_type VALUES (16, 'Временной период', 'billservice', 'timeperiod');
INSERT INTO django_content_type VALUES (17, 'Расчетный период', 'billservice', 'settlementperiod');
INSERT INTO django_content_type VALUES (18, 'Периодическая услуга', 'billservice', 'periodicalservice');
INSERT INTO django_content_type VALUES (19, 'История по пер. услугам', 'billservice', 'periodicalservicehistory');
INSERT INTO django_content_type VALUES (20, 'Разовая услуга', 'billservice', 'onetimeservice');
INSERT INTO django_content_type VALUES (21, 'one time service history', 'billservice', 'onetimeservicehistory');
INSERT INTO django_content_type VALUES (22, 'Доступ с учётом времени', 'billservice', 'timeaccessservice');
INSERT INTO django_content_type VALUES (23, 'Период доступа', 'billservice', 'timeaccessnode');
INSERT INTO django_content_type VALUES (24, 'Параметры доступа', 'billservice', 'accessparameters');
INSERT INTO django_content_type VALUES (25, 'настройка скорости', 'billservice', 'timespeed');
INSERT INTO django_content_type VALUES (26, 'Предоплаченный трафик', 'billservice', 'prepaidtraffic');
INSERT INTO django_content_type VALUES (27, 'Доступ с учётом трафика', 'billservice', 'traffictransmitservice');
INSERT INTO django_content_type VALUES (28, 'цена за направление', 'billservice', 'traffictransmitnodes');
INSERT INTO django_content_type VALUES (29, 'Предоплаченый трафик', 'billservice', 'accountprepaystrafic');
INSERT INTO django_content_type VALUES (30, 'Предоплаченый radius трафик ', 'billservice', 'accountprepaysradiustrafic');
INSERT INTO django_content_type VALUES (31, 'Предоплаченное время пользователя', 'billservice', 'accountprepaystime');
INSERT INTO django_content_type VALUES (32, 'лимит трафика', 'billservice', 'trafficlimit');
INSERT INTO django_content_type VALUES (33, 'Тариф', 'billservice', 'tariff');
INSERT INTO django_content_type VALUES (34, 'Аккаунт', 'billservice', 'account');
INSERT INTO django_content_type VALUES (35, 'organization', 'billservice', 'organization');
INSERT INTO django_content_type VALUES (36, 'Тип проводки', 'billservice', 'transactiontype');
INSERT INTO django_content_type VALUES (37, 'Проводка', 'billservice', 'transaction');
INSERT INTO django_content_type VALUES (38, 'привязка', 'billservice', 'accounttarif');
INSERT INTO django_content_type VALUES (39, 'скорости IPN клиентов', 'billservice', 'accountipnspeed');
INSERT INTO django_content_type VALUES (41, 'Периодическая операция', 'billservice', 'shedulelog');
INSERT INTO django_content_type VALUES (43, 'system user', 'billservice', 'systemuser');
INSERT INTO django_content_type VALUES (44, 'document type', 'billservice', 'documenttype');
INSERT INTO django_content_type VALUES (45, 'template type', 'billservice', 'templatetype');
INSERT INTO django_content_type VALUES (46, 'template', 'billservice', 'template');
INSERT INTO django_content_type VALUES (47, 'card', 'billservice', 'card');
INSERT INTO django_content_type VALUES (48, 'bank data', 'billservice', 'bankdata');
INSERT INTO django_content_type VALUES (49, 'operator', 'billservice', 'operator');
INSERT INTO django_content_type VALUES (50, 'dealer', 'billservice', 'dealer');
INSERT INTO django_content_type VALUES (51, 'sale card', 'billservice', 'salecard');
INSERT INTO django_content_type VALUES (52, 'dealer pay', 'billservice', 'dealerpay');
INSERT INTO django_content_type VALUES (53, 'document', 'billservice', 'document');
INSERT INTO django_content_type VALUES (54, 'suspended period', 'billservice', 'suspendedperiod');
INSERT INTO django_content_type VALUES (55, 'group', 'billservice', 'group');
INSERT INTO django_content_type VALUES (56, 'group traffic class', 'billservice', 'grouptrafficclass');
INSERT INTO django_content_type VALUES (57, 'group stat', 'billservice', 'groupstat');
INSERT INTO django_content_type VALUES (58, 'speed limit', 'billservice', 'speedlimit');
INSERT INTO django_content_type VALUES (59, 'account speed limit', 'billservice', 'accountspeedlimit');
INSERT INTO django_content_type VALUES (60, 'ip pool', 'billservice', 'ippool');
INSERT INTO django_content_type VALUES (61, 'ip in use', 'billservice', 'ipinuse');
INSERT INTO django_content_type VALUES (62, 'traffic transaction', 'billservice', 'traffictransaction');
INSERT INTO django_content_type VALUES (63, 'tp change rule', 'billservice', 'tpchangerule');
INSERT INTO django_content_type VALUES (64, 'radius attrs', 'billservice', 'radiusattrs');
INSERT INTO django_content_type VALUES (65, 'addon service', 'billservice', 'addonservice');
INSERT INTO django_content_type VALUES (66, 'addon service tarif', 'billservice', 'addonservicetarif');
INSERT INTO django_content_type VALUES (67, 'account addon service', 'billservice', 'accountaddonservice');
INSERT INTO django_content_type VALUES (68, 'addon service transaction', 'billservice', 'addonservicetransaction');
INSERT INTO django_content_type VALUES (69, 'news', 'billservice', 'news');
INSERT INTO django_content_type VALUES (70, 'account viewed news', 'billservice', 'accountviewednews');
INSERT INTO django_content_type VALUES (72, 'sub account', 'billservice', 'subaccount');
INSERT INTO django_content_type VALUES (73, 'balance history', 'billservice', 'balancehistory');
INSERT INTO django_content_type VALUES (74, 'city', 'billservice', 'city');
INSERT INTO django_content_type VALUES (75, 'street', 'billservice', 'street');
INSERT INTO django_content_type VALUES (76, 'house', 'billservice', 'house');
INSERT INTO django_content_type VALUES (77, 'radius traffic', 'billservice', 'radiustraffic');
INSERT INTO django_content_type VALUES (78, 'radius traffic node', 'billservice', 'radiustrafficnode');
INSERT INTO django_content_type VALUES (79, 'contract template', 'billservice', 'contracttemplate');
INSERT INTO django_content_type VALUES (80, 'manufacturer', 'billservice', 'manufacturer');
INSERT INTO django_content_type VALUES (81, 'hardware type', 'billservice', 'hardwaretype');
INSERT INTO django_content_type VALUES (82, 'model', 'billservice', 'model');
INSERT INTO django_content_type VALUES (83, 'hardware', 'billservice', 'hardware');
INSERT INTO django_content_type VALUES (84, 'account hardware', 'billservice', 'accounthardware');
INSERT INTO django_content_type VALUES (85, 'total transaction report', 'billservice', 'totaltransactionreport');
INSERT INTO django_content_type VALUES (86, 'periodical service log', 'billservice', 'periodicalservicelog');
INSERT INTO django_content_type VALUES (87, 'payment', 'webmoney', 'payment');
INSERT INTO django_content_type VALUES (88, 'invoice', 'qiwi', 'invoice');
INSERT INTO django_content_type VALUES (89, 'queue', 'helpdesk', 'queue');
INSERT INTO django_content_type VALUES (90, 'ticket', 'helpdesk', 'ticket');
INSERT INTO django_content_type VALUES (91, 'follow up', 'helpdesk', 'followup');
INSERT INTO django_content_type VALUES (92, 'ticket change', 'helpdesk', 'ticketchange');
INSERT INTO django_content_type VALUES (93, 'attachment', 'helpdesk', 'attachment');
INSERT INTO django_content_type VALUES (94, 'pre set reply', 'helpdesk', 'presetreply');
INSERT INTO django_content_type VALUES (95, 'escalation exclusion', 'helpdesk', 'escalationexclusion');
INSERT INTO django_content_type VALUES (96, 'email template', 'helpdesk', 'emailtemplate');
INSERT INTO django_content_type VALUES (97, 'knowledge base category', 'helpdesk', 'kbcategory');
INSERT INTO django_content_type VALUES (98, 'knowledge base item', 'helpdesk', 'kbitem');
INSERT INTO django_content_type VALUES (99, 'saved search', 'helpdesk', 'savedsearch');
INSERT INTO django_content_type VALUES (100, 'User Settings', 'helpdesk', 'usersettings');
INSERT INTO django_content_type VALUES (101, 'ignored email', 'helpdesk', 'ignoreemail');
INSERT INTO django_content_type VALUES (102, 'ticket CC', 'helpdesk', 'ticketcc');
INSERT INTO django_content_type VALUES (103, 'log action', 'object_log', 'logaction');
INSERT INTO django_content_type VALUES (104, 'log item', 'object_log', 'logitem');
INSERT INTO django_content_type VALUES (105, 'periodical service tariff', 'billservice', 'periodicalservicetariff');


INSERT INTO auth_permission VALUES (440, 'Can add permission', 1, 'add_permission');
INSERT INTO auth_permission VALUES (441, 'Can change permission', 1, 'change_permission');
INSERT INTO auth_permission VALUES (442, 'Can delete permission', 1, 'delete_permission');
INSERT INTO auth_permission VALUES (443, 'Can add group', 2, 'add_group');
INSERT INTO auth_permission VALUES (444, 'Can change group', 2, 'change_group');
INSERT INTO auth_permission VALUES (445, 'Can delete group', 2, 'delete_group');
INSERT INTO auth_permission VALUES (446, 'Can add user', 3, 'add_user');
INSERT INTO auth_permission VALUES (447, 'Can change user', 3, 'change_user');
INSERT INTO auth_permission VALUES (448, 'Can delete user', 3, 'delete_user');
INSERT INTO auth_permission VALUES (449, 'Can add message', 4, 'add_message');
INSERT INTO auth_permission VALUES (450, 'Can change message', 4, 'change_message');
INSERT INTO auth_permission VALUES (451, 'Can delete message', 4, 'delete_message');
INSERT INTO auth_permission VALUES (452, 'Can add content type', 5, 'add_contenttype');
INSERT INTO auth_permission VALUES (453, 'Can change content type', 5, 'change_contenttype');
INSERT INTO auth_permission VALUES (454, 'Can delete content type', 5, 'delete_contenttype');
INSERT INTO auth_permission VALUES (455, 'Can add session', 6, 'add_session');
INSERT INTO auth_permission VALUES (456, 'Can change session', 6, 'change_session');
INSERT INTO auth_permission VALUES (457, 'Can delete session', 6, 'delete_session');
INSERT INTO auth_permission VALUES (458, 'Can add site', 7, 'add_site');
INSERT INTO auth_permission VALUES (459, 'Can change site', 7, 'change_site');
INSERT INTO auth_permission VALUES (460, 'Can delete site', 7, 'delete_site');
INSERT INTO auth_permission VALUES (461, 'Can add log entry', 8, 'add_logentry');
INSERT INTO auth_permission VALUES (462, 'Can change log entry', 8, 'change_logentry');
INSERT INTO auth_permission VALUES (463, 'Can delete log entry', 8, 'delete_logentry');
INSERT INTO auth_permission VALUES (464, 'Can add RADIUS сессия', 9, 'add_activesession');
INSERT INTO auth_permission VALUES (465, 'Can change RADIUS сессия', 9, 'change_activesession');
INSERT INTO auth_permission VALUES (466, 'Can delete RADIUS сессия', 9, 'delete_activesession');
INSERT INTO auth_permission VALUES (467, 'Просмотр', 9, 'activesession_view');
INSERT INTO auth_permission VALUES (468, 'Can add auth log', 10, 'add_authlog');
INSERT INTO auth_permission VALUES (469, 'Can change auth log', 10, 'change_authlog');
INSERT INTO auth_permission VALUES (470, 'Can delete auth log', 10, 'delete_authlog');
INSERT INTO auth_permission VALUES (471, 'Can add Сервер доступа', 11, 'add_nas');
INSERT INTO auth_permission VALUES (472, 'Can change Сервер доступа', 11, 'change_nas');
INSERT INTO auth_permission VALUES (473, 'Can delete Сервер доступа', 11, 'delete_nas');
INSERT INTO auth_permission VALUES (474, 'Просмотр', 11, 'nas_view');
INSERT INTO auth_permission VALUES (475, 'Can add Класс трафика', 12, 'add_trafficclass');
INSERT INTO auth_permission VALUES (476, 'Can change Класс трафика', 12, 'change_trafficclass');
INSERT INTO auth_permission VALUES (477, 'Can delete Класс трафика', 12, 'delete_trafficclass');
INSERT INTO auth_permission VALUES (478, 'Просмотр', 12, 'trafficclass_view');
INSERT INTO auth_permission VALUES (479, 'Can add Направление трафика', 13, 'add_trafficnode');
INSERT INTO auth_permission VALUES (480, 'Can change Направление трафика', 13, 'change_trafficnode');
INSERT INTO auth_permission VALUES (481, 'Can delete Направление трафика', 13, 'delete_trafficnode');
INSERT INTO auth_permission VALUES (482, 'Просмотр', 13, 'trafficnode_view');
INSERT INTO auth_permission VALUES (483, 'Can add Коммутатор', 14, 'add_switch');
INSERT INTO auth_permission VALUES (484, 'Can change Коммутатор', 14, 'change_switch');
INSERT INTO auth_permission VALUES (485, 'Can delete Коммутатор', 14, 'delete_switch');
INSERT INTO auth_permission VALUES (486, 'Просмотр', 14, 'switch_view');
INSERT INTO auth_permission VALUES (487, 'Can add Нода временного периода', 15, 'add_timeperiodnode');
INSERT INTO auth_permission VALUES (488, 'Can change Нода временного периода', 15, 'change_timeperiodnode');
INSERT INTO auth_permission VALUES (489, 'Can delete Нода временного периода', 15, 'delete_timeperiodnode');
INSERT INTO auth_permission VALUES (490, 'Просмотр нод временных периодов', 15, 'timeperiodnode_view');
INSERT INTO auth_permission VALUES (491, 'Can add Временной период', 16, 'add_timeperiod');
INSERT INTO auth_permission VALUES (492, 'Can change Временной период', 16, 'change_timeperiod');
INSERT INTO auth_permission VALUES (493, 'Can delete Временной период', 16, 'delete_timeperiod');
INSERT INTO auth_permission VALUES (494, 'Просмотр временных периодов', 16, 'timeperiod_view');
INSERT INTO auth_permission VALUES (495, 'Can add Расчетный период', 17, 'add_settlementperiod');
INSERT INTO auth_permission VALUES (496, 'Can change Расчетный период', 17, 'change_settlementperiod');
INSERT INTO auth_permission VALUES (497, 'Can delete Расчетный период', 17, 'delete_settlementperiod');
INSERT INTO auth_permission VALUES (498, 'Просмотр расчётных периодов', 17, 'settlementperiod_view');
INSERT INTO auth_permission VALUES (499, 'Can add Периодическая услуга', 18, 'add_periodicalservice');
INSERT INTO auth_permission VALUES (500, 'Can change Периодическая услуга', 18, 'change_periodicalservice');
INSERT INTO auth_permission VALUES (501, 'Can delete Периодическая услуга', 18, 'delete_periodicalservice');
INSERT INTO auth_permission VALUES (502, 'Просмотр периодических услуг', 18, 'periodicalservice_view');
INSERT INTO auth_permission VALUES (503, 'Can add История по пер. услугам', 19, 'add_periodicalservicehistory');
INSERT INTO auth_permission VALUES (504, 'Can change История по пер. услугам', 19, 'change_periodicalservicehistory');
INSERT INTO auth_permission VALUES (505, 'Can delete История по пер. услугам', 19, 'delete_periodicalservicehistory');
INSERT INTO auth_permission VALUES (506, 'Просмотр списаний', 19, 'periodicalservicehistory_view');
INSERT INTO auth_permission VALUES (507, 'Can add Разовая услуга', 20, 'add_onetimeservice');
INSERT INTO auth_permission VALUES (508, 'Can change Разовая услуга', 20, 'change_onetimeservice');
INSERT INTO auth_permission VALUES (509, 'Can delete Разовая услуга', 20, 'delete_onetimeservice');
INSERT INTO auth_permission VALUES (510, 'Просмотр услуг', 20, 'onetimeservice_view');
INSERT INTO auth_permission VALUES (511, 'Can add Списание по разовым услугам', 21, 'add_onetimeservicehistory');
INSERT INTO auth_permission VALUES (512, 'Can change Списание по разовым услугам', 21, 'change_onetimeservicehistory');
INSERT INTO auth_permission VALUES (513, 'Can delete Списание по разовым услугам', 21, 'delete_onetimeservicehistory');
INSERT INTO auth_permission VALUES (514, 'Просмотр услуг', 21, 'onetimeservicehistory_view');
INSERT INTO auth_permission VALUES (515, 'Can add Доступ с учётом времени', 22, 'add_timeaccessservice');
INSERT INTO auth_permission VALUES (516, 'Can change Доступ с учётом времени', 22, 'change_timeaccessservice');
INSERT INTO auth_permission VALUES (517, 'Can delete Доступ с учётом времени', 22, 'delete_timeaccessservice');
INSERT INTO auth_permission VALUES (518, 'Просмотр услуг доступа по времени', 22, 'timeaccessservice_view');
INSERT INTO auth_permission VALUES (519, 'Can add Период доступа', 23, 'add_timeaccessnode');
INSERT INTO auth_permission VALUES (520, 'Can change Период доступа', 23, 'change_timeaccessnode');
INSERT INTO auth_permission VALUES (521, 'Can delete Период доступа', 23, 'delete_timeaccessnode');
INSERT INTO auth_permission VALUES (522, 'Просмотр', 23, 'timeacessnode_view');
INSERT INTO auth_permission VALUES (523, 'Can add Параметры доступа', 24, 'add_accessparameters');
INSERT INTO auth_permission VALUES (524, 'Can change Параметры доступа', 24, 'change_accessparameters');
INSERT INTO auth_permission VALUES (525, 'Can delete Параметры доступа', 24, 'delete_accessparameters');
INSERT INTO auth_permission VALUES (526, 'Просмотр параметров доступа', 24, 'accessparameters_view');
INSERT INTO auth_permission VALUES (527, 'Can add Настройка скорости', 25, 'add_timespeed');
INSERT INTO auth_permission VALUES (528, 'Can change Настройка скорости', 25, 'change_timespeed');
INSERT INTO auth_permission VALUES (529, 'Can delete Настройка скорости', 25, 'delete_timespeed');
INSERT INTO auth_permission VALUES (530, 'Просмотр', 25, 'timespeed_view');
INSERT INTO auth_permission VALUES (531, 'Can add Предоплаченный трафик', 26, 'add_prepaidtraffic');
INSERT INTO auth_permission VALUES (532, 'Can change Предоплаченный трафик', 26, 'change_prepaidtraffic');
INSERT INTO auth_permission VALUES (533, 'Can delete Предоплаченный трафик', 26, 'delete_prepaidtraffic');
INSERT INTO auth_permission VALUES (534, 'Просмотр', 26, 'prepaidtraffic_view');
INSERT INTO auth_permission VALUES (535, 'Can add Доступ с учётом трафика', 27, 'add_traffictransmitservice');
INSERT INTO auth_permission VALUES (536, 'Can change Доступ с учётом трафика', 27, 'change_traffictransmitservice');
INSERT INTO auth_permission VALUES (537, 'Can delete Доступ с учётом трафика', 27, 'delete_traffictransmitservice');
INSERT INTO auth_permission VALUES (538, 'Просмотр', 27, 'traffictransmitservice_view');
INSERT INTO auth_permission VALUES (539, 'Can add Цена за направление', 28, 'add_traffictransmitnodes');
INSERT INTO auth_permission VALUES (540, 'Can change Цена за направление', 28, 'change_traffictransmitnodes');
INSERT INTO auth_permission VALUES (541, 'Can delete Цена за направление', 28, 'delete_traffictransmitnodes');
INSERT INTO auth_permission VALUES (542, 'Просмотр', 28, 'traffictransmitnodes_view');
INSERT INTO auth_permission VALUES (543, 'Can add Предоплаченый трафик', 29, 'add_accountprepaystrafic');
INSERT INTO auth_permission VALUES (544, 'Can change Предоплаченый трафик', 29, 'change_accountprepaystrafic');
INSERT INTO auth_permission VALUES (545, 'Can delete Предоплаченый трафик', 29, 'delete_accountprepaystrafic');
INSERT INTO auth_permission VALUES (546, 'Просмотр', 29, 'account_prepaystraffic_view');
INSERT INTO auth_permission VALUES (547, 'Can add Предоплаченый radius трафик ', 30, 'add_accountprepaysradiustrafic');
INSERT INTO auth_permission VALUES (548, 'Can change Предоплаченый radius трафик ', 30, 'change_accountprepaysradiustrafic');
INSERT INTO auth_permission VALUES (549, 'Can delete Предоплаченый radius трафик ', 30, 'delete_accountprepaysradiustrafic');
INSERT INTO auth_permission VALUES (550, 'Просмотр', 30, 'accountprepaysradiustraffic_view');
INSERT INTO auth_permission VALUES (551, 'Can add Предоплаченное время пользователя', 31, 'add_accountprepaystime');
INSERT INTO auth_permission VALUES (552, 'Can change Предоплаченное время пользователя', 31, 'change_accountprepaystime');
INSERT INTO auth_permission VALUES (553, 'Can delete Предоплаченное время пользователя', 31, 'delete_accountprepaystime');
INSERT INTO auth_permission VALUES (554, 'Просмотр', 31, 'accountprepaystime_view');
INSERT INTO auth_permission VALUES (555, 'Can add Лимит трафика', 32, 'add_trafficlimit');
INSERT INTO auth_permission VALUES (556, 'Can change Лимит трафика', 32, 'change_trafficlimit');
INSERT INTO auth_permission VALUES (557, 'Can delete Лимит трафика', 32, 'delete_trafficlimit');
INSERT INTO auth_permission VALUES (558, 'Просмотр', 32, 'trafficlimit_view');
INSERT INTO auth_permission VALUES (559, 'Can add Тариф', 33, 'add_tariff');
INSERT INTO auth_permission VALUES (560, 'Can change Тариф', 33, 'change_tariff');
INSERT INTO auth_permission VALUES (561, 'Can delete Тариф', 33, 'delete_tariff');
INSERT INTO auth_permission VALUES (562, 'Просмотр', 33, 'tariff_view');
INSERT INTO auth_permission VALUES (563, 'Can add Аккаунт', 34, 'add_account');
INSERT INTO auth_permission VALUES (564, 'Can change Аккаунт', 34, 'change_account');
INSERT INTO auth_permission VALUES (565, 'Can delete Аккаунт', 34, 'delete_account');
INSERT INTO auth_permission VALUES (566, 'Просмотр', 34, 'account_view');
INSERT INTO auth_permission VALUES (567, 'Получить тариф для аккаунта', 34, 'get_tariff');
INSERT INTO auth_permission VALUES (568, 'Список аккаунтов для кассира', 34, 'cashier_view');
INSERT INTO auth_permission VALUES (569, 'Can add organization', 35, 'add_organization');
INSERT INTO auth_permission VALUES (570, 'Can change organization', 35, 'change_organization');
INSERT INTO auth_permission VALUES (571, 'Can delete organization', 35, 'delete_organization');
INSERT INTO auth_permission VALUES (572, 'Просмотр организации', 35, 'organization_view');
INSERT INTO auth_permission VALUES (573, 'Can add Тип проводки', 36, 'add_transactiontype');
INSERT INTO auth_permission VALUES (574, 'Can change Тип проводки', 36, 'change_transactiontype');
INSERT INTO auth_permission VALUES (575, 'Can delete Тип проводки', 36, 'delete_transactiontype');
INSERT INTO auth_permission VALUES (576, 'Просмотр', 36, 'transactiontype_view');
INSERT INTO auth_permission VALUES (577, 'Can add Проводка', 37, 'add_transaction');
INSERT INTO auth_permission VALUES (578, 'Can change Проводка', 37, 'change_transaction');
INSERT INTO auth_permission VALUES (579, 'Can delete Проводка', 37, 'delete_transaction');
INSERT INTO auth_permission VALUES (580, 'Просмотр', 37, 'transaction_view');
INSERT INTO auth_permission VALUES (581, 'Can add Тариф аккаунта', 38, 'add_accounttarif');
INSERT INTO auth_permission VALUES (582, 'Can change Тариф аккаунта', 38, 'change_accounttarif');
INSERT INTO auth_permission VALUES (583, 'Can delete Тариф аккаунта', 38, 'delete_accounttarif');
INSERT INTO auth_permission VALUES (584, 'Просмотр', 38, 'accounttarif_view');
INSERT INTO auth_permission VALUES (585, 'Can add Скорость IPN клиента', 39, 'add_accountipnspeed');
INSERT INTO auth_permission VALUES (586, 'Can change Скорость IPN клиента', 39, 'change_accountipnspeed');
INSERT INTO auth_permission VALUES (587, 'Can delete Скорость IPN клиента', 39, 'delete_accountipnspeed');
INSERT INTO auth_permission VALUES (588, 'Can add История периодических операций', 41, 'add_shedulelog');
INSERT INTO auth_permission VALUES (589, 'Can change История периодических операций', 41, 'change_shedulelog');
INSERT INTO auth_permission VALUES (590, 'Can delete История периодических операций', 41, 'delete_shedulelog');
INSERT INTO auth_permission VALUES (591, 'Can add Пользователь системы', 43, 'add_systemuser');
INSERT INTO auth_permission VALUES (592, 'Can change Пользователь системы', 43, 'change_systemuser');
INSERT INTO auth_permission VALUES (593, 'Can delete Пользователь системы', 43, 'delete_systemuser');
INSERT INTO auth_permission VALUES (594, 'Просмотр администраторов', 43, 'systemuser_view');
INSERT INTO auth_permission VALUES (595, 'Получение любой модели методом get_model', 43, 'get_model');
INSERT INTO auth_permission VALUES (596, 'Установка IPN статуса на сервере доступаl', 43, 'actions_set');
INSERT INTO auth_permission VALUES (597, 'Серверный рендеринг документов', 43, 'documentrender');
INSERT INTO auth_permission VALUES (598, 'Тестирование данных для сервера доступа', 43, 'testcredentials');
INSERT INTO auth_permission VALUES (599, 'Получение статуса портов коммутатора', 43, 'getportsstatus');
INSERT INTO auth_permission VALUES (600, 'Установка статуса портов коммутатора', 43, 'setportsstatus');
INSERT INTO auth_permission VALUES (601, 'Список лог-файлов биллинга', 43, 'list_log_files');
INSERT INTO auth_permission VALUES (602, 'Просмотр лог-файлов биллинга', 43, 'view_log_files');
INSERT INTO auth_permission VALUES (603, 'Удаление проводок', 43, 'transactions_delete');
INSERT INTO auth_permission VALUES (604, 'Метод sp_info', 43, 'sp_info');
INSERT INTO auth_permission VALUES (605, 'Просмотр груп доступа', 43, 'auth_groups');
INSERT INTO auth_permission VALUES (606, 'Can add document type', 44, 'add_documenttype');
INSERT INTO auth_permission VALUES (607, 'Can change document type', 44, 'change_documenttype');
INSERT INTO auth_permission VALUES (608, 'Can delete document type', 44, 'delete_documenttype');
INSERT INTO auth_permission VALUES (609, 'Can add Тип шаблона', 45, 'add_templatetype');
INSERT INTO auth_permission VALUES (610, 'Can change Тип шаблона', 45, 'change_templatetype');
INSERT INTO auth_permission VALUES (611, 'Can delete Тип шаблона', 45, 'delete_templatetype');
INSERT INTO auth_permission VALUES (612, 'Просмотр', 45, 'templatetype_view');
INSERT INTO auth_permission VALUES (613, 'Can add Шаблон', 46, 'add_template');
INSERT INTO auth_permission VALUES (614, 'Can change Шаблон', 46, 'change_template');
INSERT INTO auth_permission VALUES (615, 'Can delete Шаблон', 46, 'delete_template');
INSERT INTO auth_permission VALUES (616, 'Просмотр', 46, 'template_view');
INSERT INTO auth_permission VALUES (617, 'Can add Карта', 47, 'add_card');
INSERT INTO auth_permission VALUES (618, 'Can change Карта', 47, 'change_card');
INSERT INTO auth_permission VALUES (619, 'Can delete Карта', 47, 'delete_card');
INSERT INTO auth_permission VALUES (620, 'Просмотр карт', 47, 'card_view');
INSERT INTO auth_permission VALUES (621, 'Can add Банк', 48, 'add_bankdata');
INSERT INTO auth_permission VALUES (622, 'Can change Банк', 48, 'change_bankdata');
INSERT INTO auth_permission VALUES (623, 'Can delete Банк', 48, 'delete_bankdata');
INSERT INTO auth_permission VALUES (624, 'Просмотр банков', 48, 'view');
INSERT INTO auth_permission VALUES (625, 'Can add Информация о провайдере', 49, 'add_operator');
INSERT INTO auth_permission VALUES (626, 'Can change Информация о провайдере', 49, 'change_operator');
INSERT INTO auth_permission VALUES (627, 'Can delete Информация о провайдере', 49, 'delete_operator');
INSERT INTO auth_permission VALUES (628, 'Просмотр информации о провайдере', 49, 'operator_view');
INSERT INTO auth_permission VALUES (629, 'Can add Дилер', 50, 'add_dealer');
INSERT INTO auth_permission VALUES (630, 'Can change Дилер', 50, 'change_dealer');
INSERT INTO auth_permission VALUES (631, 'Can delete Дилер', 50, 'delete_dealer');
INSERT INTO auth_permission VALUES (632, 'Просмотр', 50, 'dealer_view');
INSERT INTO auth_permission VALUES (633, 'Can add Накладная на карты', 51, 'add_salecard');
INSERT INTO auth_permission VALUES (634, 'Can change Накладная на карты', 51, 'change_salecard');
INSERT INTO auth_permission VALUES (635, 'Can delete Накладная на карты', 51, 'delete_salecard');
INSERT INTO auth_permission VALUES (636, 'Просмотр', 51, 'salecard_view');
INSERT INTO auth_permission VALUES (637, 'Can add Платёж дилера', 52, 'add_dealerpay');
INSERT INTO auth_permission VALUES (638, 'Can change Платёж дилера', 52, 'change_dealerpay');
INSERT INTO auth_permission VALUES (639, 'Can delete Платёж дилера', 52, 'delete_dealerpay');
INSERT INTO auth_permission VALUES (640, 'Просмотр', 52, 'dealerpay_view');
INSERT INTO auth_permission VALUES (641, 'Can add document', 53, 'add_document');
INSERT INTO auth_permission VALUES (642, 'Can change document', 53, 'change_document');
INSERT INTO auth_permission VALUES (643, 'Can delete document', 53, 'delete_document');
INSERT INTO auth_permission VALUES (644, 'Can add Период без списаний', 54, 'add_suspendedperiod');
INSERT INTO auth_permission VALUES (645, 'Can change Период без списаний', 54, 'change_suspendedperiod');
INSERT INTO auth_permission VALUES (646, 'Can delete Период без списаний', 54, 'delete_suspendedperiod');
INSERT INTO auth_permission VALUES (647, 'Просмотр', 54, 'view');
INSERT INTO auth_permission VALUES (648, 'Can add Группа трафика', 55, 'add_group');
INSERT INTO auth_permission VALUES (649, 'Can change Группа трафика', 55, 'change_group');
INSERT INTO auth_permission VALUES (650, 'Can delete Группа трафика', 55, 'delete_group');
INSERT INTO auth_permission VALUES (651, 'Просмотр', 55, 'view');
INSERT INTO auth_permission VALUES (652, 'Can add group traffic class', 56, 'add_grouptrafficclass');
INSERT INTO auth_permission VALUES (653, 'Can change group traffic class', 56, 'change_grouptrafficclass');
INSERT INTO auth_permission VALUES (654, 'Can delete group traffic class', 56, 'delete_grouptrafficclass');
INSERT INTO auth_permission VALUES (655, 'Can add group stat', 57, 'add_groupstat');
INSERT INTO auth_permission VALUES (656, 'Can change group stat', 57, 'change_groupstat');
INSERT INTO auth_permission VALUES (657, 'Can delete group stat', 57, 'delete_groupstat');
INSERT INTO auth_permission VALUES (658, 'Can add speed limit', 58, 'add_speedlimit');
INSERT INTO auth_permission VALUES (659, 'Can change speed limit', 58, 'change_speedlimit');
INSERT INTO auth_permission VALUES (660, 'Can delete speed limit', 58, 'delete_speedlimit');
INSERT INTO auth_permission VALUES (661, 'Can add account speed limit', 59, 'add_accountspeedlimit');
INSERT INTO auth_permission VALUES (662, 'Can change account speed limit', 59, 'change_accountspeedlimit');
INSERT INTO auth_permission VALUES (663, 'Can delete account speed limit', 59, 'delete_accountspeedlimit');
INSERT INTO auth_permission VALUES (664, 'Can add IP пул', 60, 'add_ippool');
INSERT INTO auth_permission VALUES (665, 'Can change IP пул', 60, 'change_ippool');
INSERT INTO auth_permission VALUES (666, 'Can delete IP пул', 60, 'delete_ippool');
INSERT INTO auth_permission VALUES (667, 'Просмотр', 60, 'ippool_view');
INSERT INTO auth_permission VALUES (668, 'Can add Занятый IP адрес', 61, 'add_ipinuse');
INSERT INTO auth_permission VALUES (669, 'Can change Занятый IP адрес', 61, 'change_ipinuse');
INSERT INTO auth_permission VALUES (670, 'Can delete Занятый IP адрес', 61, 'delete_ipinuse');
INSERT INTO auth_permission VALUES (671, 'Просмотр', 61, 'ipinuse_view');
INSERT INTO auth_permission VALUES (672, 'Can add Списание за трафик', 62, 'add_traffictransaction');
INSERT INTO auth_permission VALUES (673, 'Can change Списание за трафик', 62, 'change_traffictransaction');
INSERT INTO auth_permission VALUES (674, 'Can delete Списание за трафик', 62, 'delete_traffictransaction');
INSERT INTO auth_permission VALUES (675, 'Просмотр', 62, 'traffictransaction_view');
INSERT INTO auth_permission VALUES (676, 'Can add Правило смены тарифов', 63, 'add_tpchangerule');
INSERT INTO auth_permission VALUES (677, 'Can change Правило смены тарифов', 63, 'change_tpchangerule');
INSERT INTO auth_permission VALUES (678, 'Can delete Правило смены тарифов', 63, 'delete_tpchangerule');
INSERT INTO auth_permission VALUES (679, 'Просмотр', 63, 'tpchangerule_view');
INSERT INTO auth_permission VALUES (680, 'Can add Custom RADIUS атрибут', 64, 'add_radiusattrs');
INSERT INTO auth_permission VALUES (681, 'Can change Custom RADIUS атрибут', 64, 'change_radiusattrs');
INSERT INTO auth_permission VALUES (682, 'Can delete Custom RADIUS атрибут', 64, 'delete_radiusattrs');
INSERT INTO auth_permission VALUES (683, 'Просмотр', 64, 'radiusattrs_view');
INSERT INTO auth_permission VALUES (684, 'Can add Подключаемая услуга', 65, 'add_addonservice');
INSERT INTO auth_permission VALUES (685, 'Can change Подключаемая услуга', 65, 'change_addonservice');
INSERT INTO auth_permission VALUES (686, 'Can delete Подключаемая услуга', 65, 'delete_addonservice');
INSERT INTO auth_permission VALUES (687, 'Просмотр', 65, 'addonservice_view');
INSERT INTO auth_permission VALUES (688, 'Can add Разрешённая подключаемая услуга', 66, 'add_addonservicetarif');
INSERT INTO auth_permission VALUES (689, 'Can change Разрешённая подключаемая услуга', 66, 'change_addonservicetarif');
INSERT INTO auth_permission VALUES (690, 'Can delete Разрешённая подключаемая услуга', 66, 'delete_addonservicetarif');
INSERT INTO auth_permission VALUES (691, 'Просмотр', 66, 'addonservicetarif_view');
INSERT INTO auth_permission VALUES (692, 'Can add Подключённая подключаемая услуга', 67, 'add_accountaddonservice');
INSERT INTO auth_permission VALUES (693, 'Can change Подключённая подключаемая услуга', 67, 'change_accountaddonservice');
INSERT INTO auth_permission VALUES (694, 'Can delete Подключённая подключаемая услуга', 67, 'delete_accountaddonservice');
INSERT INTO auth_permission VALUES (695, 'Просмотр', 67, 'accountaddonservice_view');
INSERT INTO auth_permission VALUES (696, 'Can add Списание по подключаемой услуге', 68, 'add_addonservicetransaction');
INSERT INTO auth_permission VALUES (697, 'Can change Списание по подключаемой услуге', 68, 'change_addonservicetransaction');
INSERT INTO auth_permission VALUES (698, 'Can delete Списание по подключаемой услуге', 68, 'delete_addonservicetransaction');
INSERT INTO auth_permission VALUES (699, 'Просмотр', 68, 'accountaddonservicetransaction_view');
INSERT INTO auth_permission VALUES (700, 'Can add Новость', 69, 'add_news');
INSERT INTO auth_permission VALUES (701, 'Can change Новость', 69, 'change_news');
INSERT INTO auth_permission VALUES (702, 'Can delete Новость', 69, 'delete_news');
INSERT INTO auth_permission VALUES (703, 'Просмотр', 69, 'news_view');
INSERT INTO auth_permission VALUES (704, 'Can add account viewed news', 70, 'add_accountviewednews');
INSERT INTO auth_permission VALUES (705, 'Can change account viewed news', 70, 'change_accountviewednews');
INSERT INTO auth_permission VALUES (706, 'Can delete account viewed news', 70, 'delete_accountviewednews');
INSERT INTO auth_permission VALUES (707, 'Can add Субаккаунт', 72, 'add_subaccount');
INSERT INTO auth_permission VALUES (708, 'Can change Субаккаунт', 72, 'change_subaccount');
INSERT INTO auth_permission VALUES (709, 'Can delete Субаккаунт', 72, 'delete_subaccount');
INSERT INTO auth_permission VALUES (710, 'Просмотр', 72, 'subaccount_view');
INSERT INTO auth_permission VALUES (711, 'Получение mac адреса по IP', 72, 'getmacforip');
INSERT INTO auth_permission VALUES (712, 'Can add История изменения баланса', 73, 'add_balancehistory');
INSERT INTO auth_permission VALUES (713, 'Can change История изменения баланса', 73, 'change_balancehistory');
INSERT INTO auth_permission VALUES (714, 'Can delete История изменения баланса', 73, 'delete_balancehistory');
INSERT INTO auth_permission VALUES (715, 'Просмотр', 73, 'balancehistory_view');
INSERT INTO auth_permission VALUES (716, 'Can add Город', 74, 'add_city');
INSERT INTO auth_permission VALUES (717, 'Can change Город', 74, 'change_city');
INSERT INTO auth_permission VALUES (718, 'Can delete Город', 74, 'delete_city');
INSERT INTO auth_permission VALUES (719, 'Просмотр', 74, 'city_view');
INSERT INTO auth_permission VALUES (720, 'Can add Улица', 75, 'add_street');
INSERT INTO auth_permission VALUES (721, 'Can change Улица', 75, 'change_street');
INSERT INTO auth_permission VALUES (722, 'Can delete Улица', 75, 'delete_street');
INSERT INTO auth_permission VALUES (723, 'Просмотр', 75, 'street_view');
INSERT INTO auth_permission VALUES (724, 'Can add Дом', 76, 'add_house');
INSERT INTO auth_permission VALUES (725, 'Can change Дом', 76, 'change_house');
INSERT INTO auth_permission VALUES (726, 'Can delete Дом', 76, 'delete_house');
INSERT INTO auth_permission VALUES (727, 'Просмотр', 76, 'house_view');
INSERT INTO auth_permission VALUES (728, 'Can add Услуга тарификации RADIUS трафика', 77, 'add_radiustraffic');
INSERT INTO auth_permission VALUES (729, 'Can change Услуга тарификации RADIUS трафика', 77, 'change_radiustraffic');
INSERT INTO auth_permission VALUES (730, 'Can delete Услуга тарификации RADIUS трафика', 77, 'delete_radiustraffic');
INSERT INTO auth_permission VALUES (731, 'Просмотр', 77, 'radiustraffic_view');
INSERT INTO auth_permission VALUES (732, 'Can add Настройка тарификации RADIUS трафика', 78, 'add_radiustrafficnode');
INSERT INTO auth_permission VALUES (733, 'Can change Настройка тарификации RADIUS трафика', 78, 'change_radiustrafficnode');
INSERT INTO auth_permission VALUES (734, 'Can delete Настройка тарификации RADIUS трафика', 78, 'delete_radiustrafficnode');
INSERT INTO auth_permission VALUES (735, 'Просмотр', 78, 'radiustrafficnode_view');
INSERT INTO auth_permission VALUES (736, 'Can add Шаблон номера договора', 79, 'add_contracttemplate');
INSERT INTO auth_permission VALUES (737, 'Can change Шаблон номера договора', 79, 'change_contracttemplate');
INSERT INTO auth_permission VALUES (738, 'Can delete Шаблон номера договора', 79, 'delete_contracttemplate');
INSERT INTO auth_permission VALUES (739, 'Просмотр', 79, 'contracttemplate_view');
INSERT INTO auth_permission VALUES (740, 'Can add Производитель', 80, 'add_manufacturer');
INSERT INTO auth_permission VALUES (741, 'Can change Производитель', 80, 'change_manufacturer');
INSERT INTO auth_permission VALUES (742, 'Can delete Производитель', 80, 'delete_manufacturer');
INSERT INTO auth_permission VALUES (743, 'Просмотр', 80, 'manufacturer_view');
INSERT INTO auth_permission VALUES (744, 'Can add Тип оборудования', 81, 'add_hardwaretype');
INSERT INTO auth_permission VALUES (745, 'Can change Тип оборудования', 81, 'change_hardwaretype');
INSERT INTO auth_permission VALUES (746, 'Can delete Тип оборудования', 81, 'delete_hardwaretype');
INSERT INTO auth_permission VALUES (747, 'Просмотр', 81, 'hardwaretype_view');
INSERT INTO auth_permission VALUES (748, 'Can add Модель оборудования', 82, 'add_model');
INSERT INTO auth_permission VALUES (749, 'Can change Модель оборудования', 82, 'change_model');
INSERT INTO auth_permission VALUES (750, 'Can delete Модель оборудования', 82, 'delete_model');
INSERT INTO auth_permission VALUES (751, 'Просмотр', 82, 'model_view');
INSERT INTO auth_permission VALUES (752, 'Can add Устройство', 83, 'add_hardware');
INSERT INTO auth_permission VALUES (753, 'Can change Устройство', 83, 'change_hardware');
INSERT INTO auth_permission VALUES (754, 'Can delete Устройство', 83, 'delete_hardware');
INSERT INTO auth_permission VALUES (755, 'Просмотр', 83, 'hardware_view');
INSERT INTO auth_permission VALUES (756, 'Can add Устройство у абонента', 84, 'add_accounthardware');
INSERT INTO auth_permission VALUES (757, 'Can change Устройство у абонента', 84, 'change_accounthardware');
INSERT INTO auth_permission VALUES (758, 'Can delete Устройство у абонента', 84, 'delete_accounthardware');
INSERT INTO auth_permission VALUES (759, 'Просмотр', 84, 'accounthardware_view');
INSERT INTO auth_permission VALUES (760, 'Can add total transaction report', 85, 'add_totaltransactionreport');
INSERT INTO auth_permission VALUES (761, 'Can change total transaction report', 85, 'change_totaltransactionreport');
INSERT INTO auth_permission VALUES (762, 'Can delete total transaction report', 85, 'delete_totaltransactionreport');
INSERT INTO auth_permission VALUES (763, 'Can add periodical service log', 86, 'add_periodicalservicelog');
INSERT INTO auth_permission VALUES (764, 'Can change periodical service log', 86, 'change_periodicalservicelog');
INSERT INTO auth_permission VALUES (765, 'Can delete periodical service log', 86, 'delete_periodicalservicelog');
INSERT INTO auth_permission VALUES (766, 'Can add payment', 87, 'add_payment');
INSERT INTO auth_permission VALUES (767, 'Can change payment', 87, 'change_payment');
INSERT INTO auth_permission VALUES (768, 'Can delete payment', 87, 'delete_payment');
INSERT INTO auth_permission VALUES (769, 'Can add invoice', 88, 'add_invoice');
INSERT INTO auth_permission VALUES (770, 'Can change invoice', 88, 'change_invoice');
INSERT INTO auth_permission VALUES (771, 'Can delete invoice', 88, 'delete_invoice');
INSERT INTO auth_permission VALUES (772, 'Can add queue', 89, 'add_queue');
INSERT INTO auth_permission VALUES (773, 'Can change queue', 89, 'change_queue');
INSERT INTO auth_permission VALUES (774, 'Can delete queue', 89, 'delete_queue');
INSERT INTO auth_permission VALUES (775, 'Can add ticket', 90, 'add_ticket');
INSERT INTO auth_permission VALUES (776, 'Can change ticket', 90, 'change_ticket');
INSERT INTO auth_permission VALUES (777, 'Can delete ticket', 90, 'delete_ticket');
INSERT INTO auth_permission VALUES (778, 'Can add follow up', 91, 'add_followup');
INSERT INTO auth_permission VALUES (779, 'Can change follow up', 91, 'change_followup');
INSERT INTO auth_permission VALUES (780, 'Can delete follow up', 91, 'delete_followup');
INSERT INTO auth_permission VALUES (781, 'Can add ticket change', 92, 'add_ticketchange');
INSERT INTO auth_permission VALUES (782, 'Can change ticket change', 92, 'change_ticketchange');
INSERT INTO auth_permission VALUES (783, 'Can delete ticket change', 92, 'delete_ticketchange');
INSERT INTO auth_permission VALUES (784, 'Can add attachment', 93, 'add_attachment');
INSERT INTO auth_permission VALUES (785, 'Can change attachment', 93, 'change_attachment');
INSERT INTO auth_permission VALUES (786, 'Can delete attachment', 93, 'delete_attachment');
INSERT INTO auth_permission VALUES (787, 'Can add pre set reply', 94, 'add_presetreply');
INSERT INTO auth_permission VALUES (788, 'Can change pre set reply', 94, 'change_presetreply');
INSERT INTO auth_permission VALUES (789, 'Can delete pre set reply', 94, 'delete_presetreply');
INSERT INTO auth_permission VALUES (790, 'Can add escalation exclusion', 95, 'add_escalationexclusion');
INSERT INTO auth_permission VALUES (791, 'Can change escalation exclusion', 95, 'change_escalationexclusion');
INSERT INTO auth_permission VALUES (792, 'Can delete escalation exclusion', 95, 'delete_escalationexclusion');
INSERT INTO auth_permission VALUES (793, 'Can add email template', 96, 'add_emailtemplate');
INSERT INTO auth_permission VALUES (794, 'Can change email template', 96, 'change_emailtemplate');
INSERT INTO auth_permission VALUES (795, 'Can delete email template', 96, 'delete_emailtemplate');
INSERT INTO auth_permission VALUES (796, 'Can add knowledge base category', 97, 'add_kbcategory');
INSERT INTO auth_permission VALUES (797, 'Can change knowledge base category', 97, 'change_kbcategory');
INSERT INTO auth_permission VALUES (798, 'Can delete knowledge base category', 97, 'delete_kbcategory');
INSERT INTO auth_permission VALUES (799, 'Can add knowledge base item', 98, 'add_kbitem');
INSERT INTO auth_permission VALUES (800, 'Can change knowledge base item', 98, 'change_kbitem');
INSERT INTO auth_permission VALUES (801, 'Can delete knowledge base item', 98, 'delete_kbitem');
INSERT INTO auth_permission VALUES (802, 'Can add saved search', 99, 'add_savedsearch');
INSERT INTO auth_permission VALUES (803, 'Can change saved search', 99, 'change_savedsearch');
INSERT INTO auth_permission VALUES (804, 'Can delete saved search', 99, 'delete_savedsearch');
INSERT INTO auth_permission VALUES (805, 'Can add User Settings', 100, 'add_usersettings');
INSERT INTO auth_permission VALUES (806, 'Can change User Settings', 100, 'change_usersettings');
INSERT INTO auth_permission VALUES (807, 'Can delete User Settings', 100, 'delete_usersettings');
INSERT INTO auth_permission VALUES (808, 'Can add ignored email', 101, 'add_ignoreemail');
INSERT INTO auth_permission VALUES (809, 'Can change ignored email', 101, 'change_ignoreemail');
INSERT INTO auth_permission VALUES (810, 'Can delete ignored email', 101, 'delete_ignoreemail');
INSERT INTO auth_permission VALUES (811, 'Can add ticket CC', 102, 'add_ticketcc');
INSERT INTO auth_permission VALUES (812, 'Can change ticket CC', 102, 'change_ticketcc');
INSERT INTO auth_permission VALUES (813, 'Can delete ticket CC', 102, 'delete_ticketcc');
INSERT INTO auth_permission VALUES (814, 'Can add log action', 103, 'add_logaction');
INSERT INTO auth_permission VALUES (815, 'Can change log action', 103, 'change_logaction');
INSERT INTO auth_permission VALUES (816, 'Can delete log action', 103, 'delete_logaction');
INSERT INTO auth_permission VALUES (817, 'Can add log item', 104, 'add_logitem');
INSERT INTO auth_permission VALUES (818, 'Can change log item', 104, 'change_logitem');
INSERT INTO auth_permission VALUES (819, 'Can delete log item', 104, 'delete_logitem');
INSERT INTO auth_permission VALUES (820, 'Просмотр', 54, 'suspendedperiod_view');
INSERT INTO auth_permission VALUES (821, 'Просмотр', 55, 'group_view');
INSERT INTO auth_permission VALUES (822, 'Can add periodical service tariff', 105, 'add_periodicalservicetariff');
INSERT INTO auth_permission VALUES (823, 'Can change periodical service tariff', 105, 'change_periodicalservicetariff');
INSERT INTO auth_permission VALUES (824, 'Can delete periodical service tariff', 105, 'delete_periodicalservicetariff');
INSERT INTO auth_permission VALUES (825, 'Выполнение любого sql запроса', 43, 'rawsqlexecution');


INSERT INTO auth_group_permissions VALUES (2193, 4, 440);
INSERT INTO auth_group_permissions VALUES (2194, 4, 441);
INSERT INTO auth_group_permissions VALUES (2195, 4, 442);
INSERT INTO auth_group_permissions VALUES (2196, 4, 443);
INSERT INTO auth_group_permissions VALUES (2197, 4, 444);
INSERT INTO auth_group_permissions VALUES (2198, 4, 445);
INSERT INTO auth_group_permissions VALUES (2199, 4, 446);
INSERT INTO auth_group_permissions VALUES (2200, 4, 447);
INSERT INTO auth_group_permissions VALUES (2201, 4, 448);
INSERT INTO auth_group_permissions VALUES (2202, 4, 449);
INSERT INTO auth_group_permissions VALUES (2203, 4, 450);
INSERT INTO auth_group_permissions VALUES (2204, 4, 451);
INSERT INTO auth_group_permissions VALUES (2205, 4, 452);
INSERT INTO auth_group_permissions VALUES (2206, 4, 453);
INSERT INTO auth_group_permissions VALUES (2207, 4, 454);
INSERT INTO auth_group_permissions VALUES (2208, 4, 455);
INSERT INTO auth_group_permissions VALUES (2209, 4, 456);
INSERT INTO auth_group_permissions VALUES (2210, 4, 457);
INSERT INTO auth_group_permissions VALUES (2211, 4, 458);
INSERT INTO auth_group_permissions VALUES (2212, 4, 459);
INSERT INTO auth_group_permissions VALUES (2213, 4, 460);
INSERT INTO auth_group_permissions VALUES (2214, 4, 461);
INSERT INTO auth_group_permissions VALUES (2215, 4, 462);
INSERT INTO auth_group_permissions VALUES (2216, 4, 463);
INSERT INTO auth_group_permissions VALUES (2217, 4, 464);
INSERT INTO auth_group_permissions VALUES (2218, 4, 465);
INSERT INTO auth_group_permissions VALUES (2219, 4, 466);
INSERT INTO auth_group_permissions VALUES (2220, 4, 467);
INSERT INTO auth_group_permissions VALUES (2221, 4, 468);
INSERT INTO auth_group_permissions VALUES (2222, 4, 469);
INSERT INTO auth_group_permissions VALUES (2223, 4, 470);
INSERT INTO auth_group_permissions VALUES (2224, 4, 471);
INSERT INTO auth_group_permissions VALUES (2225, 4, 472);
INSERT INTO auth_group_permissions VALUES (2226, 4, 473);
INSERT INTO auth_group_permissions VALUES (2227, 4, 474);
INSERT INTO auth_group_permissions VALUES (2228, 4, 475);
INSERT INTO auth_group_permissions VALUES (2229, 4, 476);
INSERT INTO auth_group_permissions VALUES (2230, 4, 477);
INSERT INTO auth_group_permissions VALUES (2231, 4, 478);
INSERT INTO auth_group_permissions VALUES (2232, 4, 479);
INSERT INTO auth_group_permissions VALUES (2233, 4, 480);
INSERT INTO auth_group_permissions VALUES (2234, 4, 481);
INSERT INTO auth_group_permissions VALUES (2235, 4, 482);
INSERT INTO auth_group_permissions VALUES (2236, 4, 483);
INSERT INTO auth_group_permissions VALUES (2237, 4, 484);
INSERT INTO auth_group_permissions VALUES (2238, 4, 485);
INSERT INTO auth_group_permissions VALUES (2239, 4, 486);
INSERT INTO auth_group_permissions VALUES (2240, 4, 487);
INSERT INTO auth_group_permissions VALUES (2241, 4, 488);
INSERT INTO auth_group_permissions VALUES (2242, 4, 489);
INSERT INTO auth_group_permissions VALUES (2243, 4, 490);
INSERT INTO auth_group_permissions VALUES (2244, 4, 491);
INSERT INTO auth_group_permissions VALUES (2245, 4, 492);
INSERT INTO auth_group_permissions VALUES (2246, 4, 493);
INSERT INTO auth_group_permissions VALUES (2247, 4, 494);
INSERT INTO auth_group_permissions VALUES (2248, 4, 495);
INSERT INTO auth_group_permissions VALUES (2249, 4, 496);
INSERT INTO auth_group_permissions VALUES (2250, 4, 497);
INSERT INTO auth_group_permissions VALUES (2251, 4, 498);
INSERT INTO auth_group_permissions VALUES (2252, 4, 499);
INSERT INTO auth_group_permissions VALUES (2253, 4, 500);
INSERT INTO auth_group_permissions VALUES (2254, 4, 501);
INSERT INTO auth_group_permissions VALUES (2255, 4, 502);
INSERT INTO auth_group_permissions VALUES (2256, 4, 503);
INSERT INTO auth_group_permissions VALUES (2257, 4, 504);
INSERT INTO auth_group_permissions VALUES (2258, 4, 505);
INSERT INTO auth_group_permissions VALUES (2259, 4, 506);
INSERT INTO auth_group_permissions VALUES (2260, 4, 507);
INSERT INTO auth_group_permissions VALUES (2261, 4, 508);
INSERT INTO auth_group_permissions VALUES (2262, 4, 509);
INSERT INTO auth_group_permissions VALUES (2263, 4, 510);
INSERT INTO auth_group_permissions VALUES (2264, 4, 511);
INSERT INTO auth_group_permissions VALUES (2265, 4, 512);
INSERT INTO auth_group_permissions VALUES (2266, 4, 513);
INSERT INTO auth_group_permissions VALUES (2267, 4, 514);
INSERT INTO auth_group_permissions VALUES (2268, 4, 515);
INSERT INTO auth_group_permissions VALUES (2269, 4, 516);
INSERT INTO auth_group_permissions VALUES (2270, 4, 517);
INSERT INTO auth_group_permissions VALUES (2271, 4, 518);
INSERT INTO auth_group_permissions VALUES (2272, 4, 519);
INSERT INTO auth_group_permissions VALUES (2273, 4, 520);
INSERT INTO auth_group_permissions VALUES (2274, 4, 521);
INSERT INTO auth_group_permissions VALUES (2275, 4, 522);
INSERT INTO auth_group_permissions VALUES (2276, 4, 523);
INSERT INTO auth_group_permissions VALUES (2277, 4, 524);
INSERT INTO auth_group_permissions VALUES (2278, 4, 525);
INSERT INTO auth_group_permissions VALUES (2279, 4, 526);
INSERT INTO auth_group_permissions VALUES (2280, 4, 527);
INSERT INTO auth_group_permissions VALUES (2281, 4, 528);
INSERT INTO auth_group_permissions VALUES (2282, 4, 529);
INSERT INTO auth_group_permissions VALUES (2283, 4, 530);
INSERT INTO auth_group_permissions VALUES (2284, 4, 531);
INSERT INTO auth_group_permissions VALUES (2285, 4, 532);
INSERT INTO auth_group_permissions VALUES (2286, 4, 533);
INSERT INTO auth_group_permissions VALUES (2287, 4, 534);
INSERT INTO auth_group_permissions VALUES (2288, 4, 535);
INSERT INTO auth_group_permissions VALUES (2289, 4, 536);
INSERT INTO auth_group_permissions VALUES (2290, 4, 537);
INSERT INTO auth_group_permissions VALUES (2291, 4, 538);
INSERT INTO auth_group_permissions VALUES (2292, 4, 539);
INSERT INTO auth_group_permissions VALUES (2293, 4, 540);
INSERT INTO auth_group_permissions VALUES (2294, 4, 541);
INSERT INTO auth_group_permissions VALUES (2295, 4, 542);
INSERT INTO auth_group_permissions VALUES (2296, 4, 543);
INSERT INTO auth_group_permissions VALUES (2297, 4, 544);
INSERT INTO auth_group_permissions VALUES (2298, 4, 545);
INSERT INTO auth_group_permissions VALUES (2299, 4, 546);
INSERT INTO auth_group_permissions VALUES (2300, 4, 547);
INSERT INTO auth_group_permissions VALUES (2301, 4, 548);
INSERT INTO auth_group_permissions VALUES (2302, 4, 549);
INSERT INTO auth_group_permissions VALUES (2303, 4, 550);
INSERT INTO auth_group_permissions VALUES (2304, 4, 551);
INSERT INTO auth_group_permissions VALUES (2305, 4, 552);
INSERT INTO auth_group_permissions VALUES (2306, 4, 553);
INSERT INTO auth_group_permissions VALUES (2307, 4, 554);
INSERT INTO auth_group_permissions VALUES (2308, 4, 555);
INSERT INTO auth_group_permissions VALUES (2309, 4, 556);
INSERT INTO auth_group_permissions VALUES (2310, 4, 557);
INSERT INTO auth_group_permissions VALUES (2311, 4, 558);
INSERT INTO auth_group_permissions VALUES (2312, 4, 559);
INSERT INTO auth_group_permissions VALUES (2313, 4, 560);
INSERT INTO auth_group_permissions VALUES (2314, 4, 561);
INSERT INTO auth_group_permissions VALUES (2315, 4, 562);
INSERT INTO auth_group_permissions VALUES (2316, 4, 563);
INSERT INTO auth_group_permissions VALUES (2317, 4, 564);
INSERT INTO auth_group_permissions VALUES (2318, 4, 565);
INSERT INTO auth_group_permissions VALUES (2319, 4, 566);
INSERT INTO auth_group_permissions VALUES (2320, 4, 567);
INSERT INTO auth_group_permissions VALUES (2321, 4, 568);
INSERT INTO auth_group_permissions VALUES (2322, 4, 569);
INSERT INTO auth_group_permissions VALUES (2323, 4, 570);
INSERT INTO auth_group_permissions VALUES (2324, 4, 571);
INSERT INTO auth_group_permissions VALUES (2325, 4, 572);
INSERT INTO auth_group_permissions VALUES (2326, 4, 573);
INSERT INTO auth_group_permissions VALUES (2327, 4, 574);
INSERT INTO auth_group_permissions VALUES (2328, 4, 575);
INSERT INTO auth_group_permissions VALUES (2329, 4, 576);
INSERT INTO auth_group_permissions VALUES (2330, 4, 577);
INSERT INTO auth_group_permissions VALUES (2331, 4, 578);
INSERT INTO auth_group_permissions VALUES (2332, 4, 579);
INSERT INTO auth_group_permissions VALUES (2333, 4, 580);
INSERT INTO auth_group_permissions VALUES (2334, 4, 581);
INSERT INTO auth_group_permissions VALUES (2335, 4, 582);
INSERT INTO auth_group_permissions VALUES (2336, 4, 583);
INSERT INTO auth_group_permissions VALUES (2337, 4, 584);
INSERT INTO auth_group_permissions VALUES (2338, 4, 585);
INSERT INTO auth_group_permissions VALUES (2339, 4, 586);
INSERT INTO auth_group_permissions VALUES (2340, 4, 587);
INSERT INTO auth_group_permissions VALUES (2341, 4, 588);
INSERT INTO auth_group_permissions VALUES (2342, 4, 589);
INSERT INTO auth_group_permissions VALUES (2343, 4, 590);
INSERT INTO auth_group_permissions VALUES (2344, 4, 591);
INSERT INTO auth_group_permissions VALUES (2345, 4, 592);
INSERT INTO auth_group_permissions VALUES (2346, 4, 593);
INSERT INTO auth_group_permissions VALUES (2347, 4, 594);
INSERT INTO auth_group_permissions VALUES (2348, 4, 595);
INSERT INTO auth_group_permissions VALUES (2349, 4, 596);
INSERT INTO auth_group_permissions VALUES (2350, 4, 597);
INSERT INTO auth_group_permissions VALUES (2351, 4, 598);
INSERT INTO auth_group_permissions VALUES (2352, 4, 599);
INSERT INTO auth_group_permissions VALUES (2353, 4, 600);
INSERT INTO auth_group_permissions VALUES (2354, 4, 601);
INSERT INTO auth_group_permissions VALUES (2355, 4, 602);
INSERT INTO auth_group_permissions VALUES (2356, 4, 603);
INSERT INTO auth_group_permissions VALUES (2357, 4, 604);
INSERT INTO auth_group_permissions VALUES (2358, 4, 605);
INSERT INTO auth_group_permissions VALUES (2359, 4, 606);
INSERT INTO auth_group_permissions VALUES (2360, 4, 607);
INSERT INTO auth_group_permissions VALUES (2361, 4, 608);
INSERT INTO auth_group_permissions VALUES (2362, 4, 609);
INSERT INTO auth_group_permissions VALUES (2363, 4, 610);
INSERT INTO auth_group_permissions VALUES (2364, 4, 611);
INSERT INTO auth_group_permissions VALUES (2365, 4, 612);
INSERT INTO auth_group_permissions VALUES (2366, 4, 613);
INSERT INTO auth_group_permissions VALUES (2367, 4, 614);
INSERT INTO auth_group_permissions VALUES (2368, 4, 615);
INSERT INTO auth_group_permissions VALUES (2369, 4, 616);
INSERT INTO auth_group_permissions VALUES (2370, 4, 617);
INSERT INTO auth_group_permissions VALUES (2371, 4, 618);
INSERT INTO auth_group_permissions VALUES (2372, 4, 619);
INSERT INTO auth_group_permissions VALUES (2373, 4, 620);
INSERT INTO auth_group_permissions VALUES (2374, 4, 621);
INSERT INTO auth_group_permissions VALUES (2375, 4, 622);
INSERT INTO auth_group_permissions VALUES (2376, 4, 623);
INSERT INTO auth_group_permissions VALUES (2377, 4, 624);
INSERT INTO auth_group_permissions VALUES (2378, 4, 625);
INSERT INTO auth_group_permissions VALUES (2379, 4, 626);
INSERT INTO auth_group_permissions VALUES (2380, 4, 627);
INSERT INTO auth_group_permissions VALUES (2381, 4, 628);
INSERT INTO auth_group_permissions VALUES (2382, 4, 629);
INSERT INTO auth_group_permissions VALUES (2383, 4, 630);
INSERT INTO auth_group_permissions VALUES (2384, 4, 631);
INSERT INTO auth_group_permissions VALUES (2385, 4, 632);
INSERT INTO auth_group_permissions VALUES (2386, 4, 633);
INSERT INTO auth_group_permissions VALUES (2387, 4, 634);
INSERT INTO auth_group_permissions VALUES (2388, 4, 635);
INSERT INTO auth_group_permissions VALUES (2389, 4, 636);
INSERT INTO auth_group_permissions VALUES (2390, 4, 637);
INSERT INTO auth_group_permissions VALUES (2391, 4, 638);
INSERT INTO auth_group_permissions VALUES (2392, 4, 639);
INSERT INTO auth_group_permissions VALUES (2393, 4, 640);
INSERT INTO auth_group_permissions VALUES (2394, 4, 641);
INSERT INTO auth_group_permissions VALUES (2395, 4, 642);
INSERT INTO auth_group_permissions VALUES (2396, 4, 643);
INSERT INTO auth_group_permissions VALUES (2397, 4, 644);
INSERT INTO auth_group_permissions VALUES (2398, 4, 645);
INSERT INTO auth_group_permissions VALUES (2399, 4, 646);
INSERT INTO auth_group_permissions VALUES (2400, 4, 647);
INSERT INTO auth_group_permissions VALUES (2401, 4, 648);
INSERT INTO auth_group_permissions VALUES (2402, 4, 649);
INSERT INTO auth_group_permissions VALUES (2403, 4, 650);
INSERT INTO auth_group_permissions VALUES (2404, 4, 651);
INSERT INTO auth_group_permissions VALUES (2405, 4, 652);
INSERT INTO auth_group_permissions VALUES (2406, 4, 653);
INSERT INTO auth_group_permissions VALUES (2407, 4, 654);
INSERT INTO auth_group_permissions VALUES (2408, 4, 655);
INSERT INTO auth_group_permissions VALUES (2409, 4, 656);
INSERT INTO auth_group_permissions VALUES (2410, 4, 657);
INSERT INTO auth_group_permissions VALUES (2411, 4, 658);
INSERT INTO auth_group_permissions VALUES (2412, 4, 659);
INSERT INTO auth_group_permissions VALUES (2413, 4, 660);
INSERT INTO auth_group_permissions VALUES (2414, 4, 661);
INSERT INTO auth_group_permissions VALUES (2415, 4, 662);
INSERT INTO auth_group_permissions VALUES (2416, 4, 663);
INSERT INTO auth_group_permissions VALUES (2417, 4, 664);
INSERT INTO auth_group_permissions VALUES (2418, 4, 665);
INSERT INTO auth_group_permissions VALUES (2419, 4, 666);
INSERT INTO auth_group_permissions VALUES (2420, 4, 667);
INSERT INTO auth_group_permissions VALUES (2421, 4, 668);
INSERT INTO auth_group_permissions VALUES (2422, 4, 669);
INSERT INTO auth_group_permissions VALUES (2423, 4, 670);
INSERT INTO auth_group_permissions VALUES (2424, 4, 671);
INSERT INTO auth_group_permissions VALUES (2425, 4, 672);
INSERT INTO auth_group_permissions VALUES (2426, 4, 673);
INSERT INTO auth_group_permissions VALUES (2427, 4, 674);
INSERT INTO auth_group_permissions VALUES (2428, 4, 675);
INSERT INTO auth_group_permissions VALUES (2429, 4, 676);
INSERT INTO auth_group_permissions VALUES (2430, 4, 677);
INSERT INTO auth_group_permissions VALUES (2431, 4, 678);
INSERT INTO auth_group_permissions VALUES (2432, 4, 679);
INSERT INTO auth_group_permissions VALUES (2433, 4, 680);
INSERT INTO auth_group_permissions VALUES (2434, 4, 681);
INSERT INTO auth_group_permissions VALUES (2435, 4, 682);
INSERT INTO auth_group_permissions VALUES (2436, 4, 683);
INSERT INTO auth_group_permissions VALUES (2437, 4, 684);
INSERT INTO auth_group_permissions VALUES (2438, 4, 685);
INSERT INTO auth_group_permissions VALUES (2439, 4, 686);
INSERT INTO auth_group_permissions VALUES (2440, 4, 687);
INSERT INTO auth_group_permissions VALUES (2441, 4, 688);
INSERT INTO auth_group_permissions VALUES (2442, 4, 689);
INSERT INTO auth_group_permissions VALUES (2443, 4, 690);
INSERT INTO auth_group_permissions VALUES (2444, 4, 691);
INSERT INTO auth_group_permissions VALUES (2445, 4, 692);
INSERT INTO auth_group_permissions VALUES (2446, 4, 693);
INSERT INTO auth_group_permissions VALUES (2447, 4, 694);
INSERT INTO auth_group_permissions VALUES (2448, 4, 695);
INSERT INTO auth_group_permissions VALUES (2449, 4, 696);
INSERT INTO auth_group_permissions VALUES (2450, 4, 697);
INSERT INTO auth_group_permissions VALUES (2451, 4, 698);
INSERT INTO auth_group_permissions VALUES (2452, 4, 699);
INSERT INTO auth_group_permissions VALUES (2453, 4, 700);
INSERT INTO auth_group_permissions VALUES (2454, 4, 701);
INSERT INTO auth_group_permissions VALUES (2455, 4, 702);
INSERT INTO auth_group_permissions VALUES (2456, 4, 703);
INSERT INTO auth_group_permissions VALUES (2457, 4, 704);
INSERT INTO auth_group_permissions VALUES (2458, 4, 705);
INSERT INTO auth_group_permissions VALUES (2459, 4, 706);
INSERT INTO auth_group_permissions VALUES (2460, 4, 707);
INSERT INTO auth_group_permissions VALUES (2461, 4, 708);
INSERT INTO auth_group_permissions VALUES (2462, 4, 709);
INSERT INTO auth_group_permissions VALUES (2463, 4, 710);
INSERT INTO auth_group_permissions VALUES (2464, 4, 711);
INSERT INTO auth_group_permissions VALUES (2465, 4, 712);
INSERT INTO auth_group_permissions VALUES (2466, 4, 713);
INSERT INTO auth_group_permissions VALUES (2467, 4, 714);
INSERT INTO auth_group_permissions VALUES (2468, 4, 715);
INSERT INTO auth_group_permissions VALUES (2469, 4, 716);
INSERT INTO auth_group_permissions VALUES (2470, 4, 717);
INSERT INTO auth_group_permissions VALUES (2471, 4, 718);
INSERT INTO auth_group_permissions VALUES (2472, 4, 719);
INSERT INTO auth_group_permissions VALUES (2473, 4, 720);
INSERT INTO auth_group_permissions VALUES (2474, 4, 721);
INSERT INTO auth_group_permissions VALUES (2475, 4, 722);
INSERT INTO auth_group_permissions VALUES (2476, 4, 723);
INSERT INTO auth_group_permissions VALUES (2477, 4, 724);
INSERT INTO auth_group_permissions VALUES (2478, 4, 725);
INSERT INTO auth_group_permissions VALUES (2479, 4, 726);
INSERT INTO auth_group_permissions VALUES (2480, 4, 727);
INSERT INTO auth_group_permissions VALUES (2481, 4, 728);
INSERT INTO auth_group_permissions VALUES (2482, 4, 729);
INSERT INTO auth_group_permissions VALUES (2483, 4, 730);
INSERT INTO auth_group_permissions VALUES (2484, 4, 731);
INSERT INTO auth_group_permissions VALUES (2485, 4, 732);
INSERT INTO auth_group_permissions VALUES (2486, 4, 733);
INSERT INTO auth_group_permissions VALUES (2487, 4, 734);
INSERT INTO auth_group_permissions VALUES (2488, 4, 735);
INSERT INTO auth_group_permissions VALUES (2489, 4, 736);
INSERT INTO auth_group_permissions VALUES (2490, 4, 737);
INSERT INTO auth_group_permissions VALUES (2491, 4, 738);
INSERT INTO auth_group_permissions VALUES (2492, 4, 739);
INSERT INTO auth_group_permissions VALUES (2493, 4, 740);
INSERT INTO auth_group_permissions VALUES (2494, 4, 741);
INSERT INTO auth_group_permissions VALUES (2495, 4, 742);
INSERT INTO auth_group_permissions VALUES (2496, 4, 743);
INSERT INTO auth_group_permissions VALUES (2497, 4, 744);
INSERT INTO auth_group_permissions VALUES (2498, 4, 745);
INSERT INTO auth_group_permissions VALUES (2499, 4, 746);
INSERT INTO auth_group_permissions VALUES (2500, 4, 747);
INSERT INTO auth_group_permissions VALUES (2501, 4, 748);
INSERT INTO auth_group_permissions VALUES (2502, 4, 749);
INSERT INTO auth_group_permissions VALUES (2503, 4, 750);
INSERT INTO auth_group_permissions VALUES (2504, 4, 751);
INSERT INTO auth_group_permissions VALUES (2505, 4, 752);
INSERT INTO auth_group_permissions VALUES (2506, 4, 753);
INSERT INTO auth_group_permissions VALUES (2507, 4, 754);
INSERT INTO auth_group_permissions VALUES (2508, 4, 755);
INSERT INTO auth_group_permissions VALUES (2509, 4, 756);
INSERT INTO auth_group_permissions VALUES (2510, 4, 757);
INSERT INTO auth_group_permissions VALUES (2511, 4, 758);
INSERT INTO auth_group_permissions VALUES (2512, 4, 759);
INSERT INTO auth_group_permissions VALUES (2513, 4, 760);
INSERT INTO auth_group_permissions VALUES (2514, 4, 761);
INSERT INTO auth_group_permissions VALUES (2515, 4, 762);
INSERT INTO auth_group_permissions VALUES (2516, 4, 763);
INSERT INTO auth_group_permissions VALUES (2517, 4, 764);
INSERT INTO auth_group_permissions VALUES (2518, 4, 765);
INSERT INTO auth_group_permissions VALUES (2519, 4, 766);
INSERT INTO auth_group_permissions VALUES (2520, 4, 767);
INSERT INTO auth_group_permissions VALUES (2521, 4, 768);
INSERT INTO auth_group_permissions VALUES (2522, 4, 769);
INSERT INTO auth_group_permissions VALUES (2523, 4, 770);
INSERT INTO auth_group_permissions VALUES (2524, 4, 771);
INSERT INTO auth_group_permissions VALUES (2525, 4, 772);
INSERT INTO auth_group_permissions VALUES (2526, 4, 773);
INSERT INTO auth_group_permissions VALUES (2527, 4, 774);
INSERT INTO auth_group_permissions VALUES (2528, 4, 775);
INSERT INTO auth_group_permissions VALUES (2529, 4, 776);
INSERT INTO auth_group_permissions VALUES (2530, 4, 777);
INSERT INTO auth_group_permissions VALUES (2531, 4, 778);
INSERT INTO auth_group_permissions VALUES (2532, 4, 779);
INSERT INTO auth_group_permissions VALUES (2533, 4, 780);
INSERT INTO auth_group_permissions VALUES (2534, 4, 781);
INSERT INTO auth_group_permissions VALUES (2535, 4, 782);
INSERT INTO auth_group_permissions VALUES (2536, 4, 783);
INSERT INTO auth_group_permissions VALUES (2537, 4, 784);
INSERT INTO auth_group_permissions VALUES (2538, 4, 785);
INSERT INTO auth_group_permissions VALUES (2539, 4, 786);
INSERT INTO auth_group_permissions VALUES (2540, 4, 787);
INSERT INTO auth_group_permissions VALUES (2541, 4, 788);
INSERT INTO auth_group_permissions VALUES (2542, 4, 789);
INSERT INTO auth_group_permissions VALUES (2543, 4, 790);
INSERT INTO auth_group_permissions VALUES (2544, 4, 791);
INSERT INTO auth_group_permissions VALUES (2545, 4, 792);
INSERT INTO auth_group_permissions VALUES (2546, 4, 793);
INSERT INTO auth_group_permissions VALUES (2547, 4, 794);
INSERT INTO auth_group_permissions VALUES (2548, 4, 795);
INSERT INTO auth_group_permissions VALUES (2549, 4, 796);
INSERT INTO auth_group_permissions VALUES (2550, 4, 797);
INSERT INTO auth_group_permissions VALUES (2551, 4, 798);
INSERT INTO auth_group_permissions VALUES (2552, 4, 799);
INSERT INTO auth_group_permissions VALUES (2553, 4, 800);
INSERT INTO auth_group_permissions VALUES (2554, 4, 801);
INSERT INTO auth_group_permissions VALUES (2555, 4, 802);
INSERT INTO auth_group_permissions VALUES (2556, 4, 803);
INSERT INTO auth_group_permissions VALUES (2557, 4, 804);
INSERT INTO auth_group_permissions VALUES (2558, 4, 805);
INSERT INTO auth_group_permissions VALUES (2559, 4, 806);
INSERT INTO auth_group_permissions VALUES (2560, 4, 807);
INSERT INTO auth_group_permissions VALUES (2561, 4, 808);
INSERT INTO auth_group_permissions VALUES (2562, 4, 809);
INSERT INTO auth_group_permissions VALUES (2563, 4, 810);
INSERT INTO auth_group_permissions VALUES (2564, 4, 811);
INSERT INTO auth_group_permissions VALUES (2565, 4, 812);
INSERT INTO auth_group_permissions VALUES (2566, 4, 813);
INSERT INTO auth_group_permissions VALUES (2567, 4, 814);
INSERT INTO auth_group_permissions VALUES (2568, 4, 815);
INSERT INTO auth_group_permissions VALUES (2569, 4, 816);
INSERT INTO auth_group_permissions VALUES (2570, 4, 817);
INSERT INTO auth_group_permissions VALUES (2571, 4, 818);
INSERT INTO auth_group_permissions VALUES (2572, 4, 819);
INSERT INTO auth_group_permissions VALUES (2573, 4, 820);
INSERT INTO auth_group_permissions VALUES (2574, 4, 821);
INSERT INTO auth_group_permissions VALUES (2575, 4, 825);
INSERT INTO auth_group_permissions VALUES (1778, 2, 514);
INSERT INTO auth_group_permissions VALUES (1779, 2, 647);
INSERT INTO auth_group_permissions VALUES (1780, 2, 522);
INSERT INTO auth_group_permissions VALUES (1781, 2, 546);
INSERT INTO auth_group_permissions VALUES (1782, 2, 675);
INSERT INTO auth_group_permissions VALUES (1783, 2, 679);
INSERT INTO auth_group_permissions VALUES (1784, 2, 562);
INSERT INTO auth_group_permissions VALUES (1785, 2, 566);
INSERT INTO auth_group_permissions VALUES (1786, 2, 567);
INSERT INTO auth_group_permissions VALUES (1787, 2, 568);
INSERT INTO auth_group_permissions VALUES (1788, 2, 699);
INSERT INTO auth_group_permissions VALUES (1789, 2, 572);
INSERT INTO auth_group_permissions VALUES (1790, 2, 576);
INSERT INTO auth_group_permissions VALUES (1791, 2, 577);
INSERT INTO auth_group_permissions VALUES (1792, 2, 578);
INSERT INTO auth_group_permissions VALUES (1793, 2, 580);
INSERT INTO auth_group_permissions VALUES (1794, 2, 581);
INSERT INTO auth_group_permissions VALUES (1795, 2, 582);
INSERT INTO auth_group_permissions VALUES (1796, 2, 583);
INSERT INTO auth_group_permissions VALUES (1797, 2, 584);
INSERT INTO auth_group_permissions VALUES (1798, 2, 715);
INSERT INTO auth_group_permissions VALUES (1799, 2, 719);
INSERT INTO auth_group_permissions VALUES (1800, 2, 595);
INSERT INTO auth_group_permissions VALUES (1801, 2, 597);
INSERT INTO auth_group_permissions VALUES (1802, 2, 727);
INSERT INTO auth_group_permissions VALUES (1803, 2, 612);
INSERT INTO auth_group_permissions VALUES (1804, 2, 616);
INSERT INTO auth_group_permissions VALUES (1805, 2, 490);
INSERT INTO auth_group_permissions VALUES (1806, 2, 494);
INSERT INTO auth_group_permissions VALUES (1807, 2, 498);
INSERT INTO auth_group_permissions VALUES (1808, 2, 723);
INSERT INTO auth_group_permissions VALUES (1809, 2, 628);
INSERT INTO auth_group_permissions VALUES (1810, 2, 506);

