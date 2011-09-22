CREATE TABLE nas_switch (
    id serial NOT NULL PRIMARY KEY,
    manufacturer varchar(250) DEFAULT '',
    model varchar(500) DEFAULT '',
    name varchar(500) DEFAULT '',
    sn varchar(500) DEFAULT '',
    city_id integer,
    street_id integer,
    house_id integer,
    place text DEFAULT '',
    comment text DEFAULT '',
    ports_count integer,
    broken_ports text DEFAULT '',
    uplink_ports text DEFAULT '',
    protected_ports text DEFAULT '',
    monitored_ports text DEFAULT '',
    disabled_ports text DEFAULT '',
    snmp_support boolean DEFAULT False,
    snmp_version varchar(10),
    snmp_community varchar(128) DEFAULT '',
    ipaddress inet,
    macaddress varchar(32),
    management_method integer,
    option82 boolean DEFAULT False,
    option82_auth_type integer,
    secret varchar(128) DEFAULT '',
    identify varchar(128) DEFAULT '',
    username varchar(256) DEFAULT '',
    password varchar(256) DEFAULT '',
    enable_port text DEFAULT '',
    disable_port text DEFAULT '',
    option82_template text DEFAULT '',
    remote_id text DEFAULT ''
)
;



