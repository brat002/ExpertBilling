DROP TABLE billservice_notificationssettings;
CREATE TABLE billservice_notificationssettings
(
  id serial NOT NULL,
  payment_notifications boolean NOT NULL,
  payment_notifications_template text NOT NULL,
  balance_notifications boolean NOT NULL,
  balance_edge double precision NOT NULL,
  balance_notifications_each integer NOT NULL,
  balance_notifications_limit integer NOT NULL,
  balance_notifications_template text NOT NULL,
  notification_type character varying(64) NOT NULL,
  backend character varying(64) NOT NULL,
  CONSTRAINT billservice_notificationssettings_pkey PRIMARY KEY (id )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE billservice_notificationssettings
  OWNER TO ebs;
CREATE TABLE billservice_notificationssettings_tariffs
(
  id serial NOT NULL,
  notificationssettings_id integer NOT NULL,
  tariff_id integer NOT NULL,
  CONSTRAINT billservice_notificationssettings_tariffs_pkey PRIMARY KEY (id ),
  CONSTRAINT billservice_notificationssettings_tariffs_tariff_id_fkey FOREIGN KEY (tariff_id)
      REFERENCES billservice_tariff (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT notificationssettings_id_refs_id_f7fe282f FOREIGN KEY (notificationssettings_id)
      REFERENCES billservice_notificationssettings (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT billservice_notificationssett_notificationssettings_id_tari_key UNIQUE (notificationssettings_id , tariff_id )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE billservice_notificationssettings_tariffs
  OWNER TO ebs;

-- Index: billservice_notificationssettings_tariffs_notificationssett3105

-- DROP INDEX billservice_notificationssettings_tariffs_notificationssett3105;

CREATE INDEX billservice_notificationssettings_tariffs_notificationssett3105
  ON billservice_notificationssettings_tariffs
  USING btree
  (notificationssettings_id );
  

CREATE INDEX billservice_notificationssettings_tariffs_tariff_id
  ON billservice_notificationssettings_tariffs
  USING btree
  (tariff_id );
  
CREATE TABLE billservice_accountnotification
(
  id serial NOT NULL,
  account_id integer NOT NULL,
  notificationsettings_id integer NOT NULL,
  ballance_notification_count integer NOT NULL,
  ballance_notification_last_date timestamp with time zone,
  payment_notification_last_date timestamp with time zone,
  CONSTRAINT billservice_accountnotification_pkey PRIMARY KEY (id ),
  CONSTRAINT billservice_accountnotification_account_id_fkey FOREIGN KEY (account_id)
      REFERENCES billservice_account (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT billservice_accountnotification_notificationsettings_id_fkey FOREIGN KEY (notificationsettings_id)
      REFERENCES billservice_notificationssettings (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
)
WITH (
  OIDS=FALSE
);
ALTER TABLE billservice_accountnotification
  OWNER TO ebs;

-- Index: billservice_accountnotification_account_id

-- DROP INDEX billservice_accountnotification_account_id;

CREATE INDEX billservice_accountnotification_account_id
  ON billservice_accountnotification
  USING btree
  (account_id );

-- Index: billservice_accountnotification_notificationsettings_id

-- DROP INDEX billservice_accountnotification_notificationsettings_id;

CREATE INDEX billservice_accountnotification_notificationsettings_id
  ON billservice_accountnotification
  USING btree
  (notificationsettings_id );
  