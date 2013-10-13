CREATE TABLE billservice_registrationrequest
(
  id serial NOT NULL,
  email character varying(75) NOT NULL,
  fullname character varying(512) NOT NULL,
  address character varying(1024) NOT NULL,
  phone character varying(64) NOT NULL,
  datetime timestamp with time zone NOT NULL,
  CONSTRAINT billservice_registrationrequest_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);

INSERT INTO billservice_permission(
            name, internal_name, ordering, app)
    VALUES ('Просматривать запрос на подключение', 'view_registrationrequest', 400, 'billservice');
INSERT INTO billservice_permission(
            name, internal_name, ordering, app)
    VALUES ('Удалять запрос на подключение', 'delete_registrationrequest', 401, 'billservice');

    