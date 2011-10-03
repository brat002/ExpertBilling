CREATE TABLE billservice_manufacturer (
    id serial NOT NULL PRIMARY KEY,
    name text NOT NULL
)
;
CREATE TABLE billservice_hardwaretype (
    id serial NOT NULL PRIMARY KEY,
    name text NOT NULL
)
;

CREATE TABLE billservice_model (
    id serial NOT NULL PRIMARY KEY,
    manufacturer_id integer NOT NULL,
    hardwaretype_id integer NOT NULL,
    name text NOT NULL
)
;

CREATE TABLE billservice_hardware (
    id serial NOT NULL PRIMARY KEY,
    model_id integer NOT NULL,
    name varchar(500),
    sn varchar(500),
    comment text DEFAULT '',
    ipaddress text,
    macaddress varchar(32)
);



CREATE TABLE billservice_accounthardware (
    id serial NOT NULL PRIMARY KEY,
    account_id integer NOT NULL ,
    hardware_id integer NOT NULL,
    datetime timestamp without time zone NOT NULL,
    returned timestamp without time zone,
    comment text DEFAULT ''
)
;


