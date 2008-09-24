--
-- PostgreSQL database dump
--

-- Started on 2008-09-24 22:32:01

SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

--
-- TOC entry 481 (class 2612 OID 125641)
-- Name: plpgsql; Type: PROCEDURAL LANGUAGE; Schema: -; Owner: -
--

CREATE PROCEDURAL LANGUAGE plpgsql;


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 1653 (class 1259 OID 125642)
-- Dependencies: 6
-- Name: auth_group; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE auth_group (
    id integer NOT NULL,
    name character varying(80) NOT NULL
);


--
-- TOC entry 1654 (class 1259 OID 125645)
-- Dependencies: 6
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


--
-- TOC entry 1655 (class 1259 OID 125648)
-- Dependencies: 6
-- Name: auth_message; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE auth_message (
    id integer NOT NULL,
    user_id integer NOT NULL,
    message text NOT NULL
);


--
-- TOC entry 1656 (class 1259 OID 125654)
-- Dependencies: 6
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE auth_permission (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


--
-- TOC entry 1657 (class 1259 OID 125657)
-- Dependencies: 6
-- Name: auth_user; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE auth_user (
    id integer NOT NULL,
    username character varying(30) NOT NULL,
    first_name character varying(30) NOT NULL,
    last_name character varying(30) NOT NULL,
    email character varying(75) NOT NULL,
    password character varying(128) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    is_superuser boolean NOT NULL,
    last_login timestamp without time zone NOT NULL,
    date_joined timestamp without time zone NOT NULL
);


--
-- TOC entry 1658 (class 1259 OID 125660)
-- Dependencies: 6
-- Name: auth_user_groups; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE auth_user_groups (
    id integer NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


--
-- TOC entry 1659 (class 1259 OID 125663)
-- Dependencies: 6
-- Name: auth_user_user_permissions; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE auth_user_user_permissions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


--
-- TOC entry 1660 (class 1259 OID 125666)
-- Dependencies: 2036 2037 2038 2039 2040 2041 2042 6
-- Name: billservice_accessparameters; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_accessparameters (
    id integer NOT NULL,
    access_type character varying(255) NOT NULL,
    access_time_id integer NOT NULL,
    max_limit character varying(64) DEFAULT ''::character varying,
    min_limit character varying(64) DEFAULT ''::character varying,
    burst_limit character varying(64) DEFAULT ''::character varying,
    burst_treshold character varying(64) DEFAULT ''::character varying,
    burst_time character varying(64) DEFAULT ''::character varying,
    priority integer DEFAULT 8,
    ipn_for_vpn boolean DEFAULT false
);


--
-- TOC entry 1661 (class 1259 OID 125679)
-- Dependencies: 2044 2045 2046 2047 2048 2049 2050 2051 2052 2053 2054 2055 2056 2057 2058 2059 2060 2061 2062 6
-- Name: billservice_account; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_account (
    id integer NOT NULL,
    username character varying(200) NOT NULL,
    password character varying(200) DEFAULT ''::character varying,
    fullname character varying(200) DEFAULT ''::character varying,
    email character varying(200) DEFAULT ''::character varying,
    address text DEFAULT ''::text,
    nas_id integer NOT NULL,
    vpn_ip_address inet DEFAULT '0.0.0.0'::inet,
    assign_ipn_ip_from_dhcp boolean DEFAULT false,
    ipn_ip_address inet DEFAULT '0.0.0.0'::inet,
    ipn_mac_address character varying(32) DEFAULT ''::character varying,
    ipn_status boolean DEFAULT false,
    status boolean DEFAULT false,
    suspended boolean DEFAULT true,
    created timestamp without time zone DEFAULT now(),
    ballance double precision DEFAULT 0,
    credit double precision DEFAULT 0,
    disabled_by_limit boolean DEFAULT false,
    balance_blocked boolean DEFAULT false,
    ipn_speed character varying(96) DEFAULT ''::character varying,
    vpn_speed character varying(96) DEFAULT ''::character varying,
    netmask inet DEFAULT '0.0.0.0'::inet
);


--
-- TOC entry 1662 (class 1259 OID 125704)
-- Dependencies: 2064 2065 2066 2067 6
-- Name: billservice_accountipnspeed; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_accountipnspeed (
    id integer NOT NULL,
    account_id integer NOT NULL,
    speed character varying(32) DEFAULT ''::character varying,
    state boolean DEFAULT false,
    static boolean DEFAULT false,
    datetime timestamp without time zone DEFAULT now()
);


--
-- TOC entry 1663 (class 1259 OID 125711)
-- Dependencies: 2069 2070 6
-- Name: billservice_accountprepaystime; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_accountprepaystime (
    id integer NOT NULL,
    account_tarif_id integer NOT NULL,
    prepaid_time_service_id integer NOT NULL,
    size integer DEFAULT 0,
    datetime timestamp without time zone DEFAULT now()
);


--
-- TOC entry 1664 (class 1259 OID 125716)
-- Dependencies: 2072 2073 6
-- Name: billservice_accountprepaystrafic; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_accountprepaystrafic (
    id integer NOT NULL,
    account_tarif_id integer NOT NULL,
    prepaid_traffic_id integer NOT NULL,
    size double precision DEFAULT 0,
    datetime timestamp without time zone DEFAULT now()
);


--
-- TOC entry 1665 (class 1259 OID 125721)
-- Dependencies: 6
-- Name: billservice_accounttarif; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_accounttarif (
    id integer NOT NULL,
    account_id integer NOT NULL,
    tarif_id integer NOT NULL,
    datetime timestamp without time zone
);


--
-- TOC entry 1666 (class 1259 OID 125724)
-- Dependencies: 2076 2077 6
-- Name: billservice_card; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_card (
    id integer NOT NULL,
    card_group_id integer NOT NULL,
    series integer NOT NULL,
    pin character varying(255) NOT NULL,
    sold timestamp without time zone,
    nominal double precision DEFAULT 0,
    activated timestamp without time zone,
    activated_by_id integer,
    start_date timestamp without time zone,
    end_date timestamp without time zone,
    disabled boolean DEFAULT false
);


--
-- TOC entry 1667 (class 1259 OID 125729)
-- Dependencies: 2079 6
-- Name: billservice_cardgroup; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_cardgroup (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    disabled boolean DEFAULT false
);


--
-- TOC entry 1668 (class 1259 OID 125733)
-- Dependencies: 2081 2082 2083 6
-- Name: billservice_netflowstream; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_netflowstream (
    id integer NOT NULL,
    nas_id integer,
    account_id integer NOT NULL,
    tarif_id integer NOT NULL,
    date_start timestamp without time zone DEFAULT now(),
    src_addr inet NOT NULL,
    traffic_class_id integer,
    direction character varying(32) NOT NULL,
    traffic_transmit_node_id integer,
    dst_addr inet NOT NULL,
    octets integer NOT NULL,
    src_port integer NOT NULL,
    dst_port integer NOT NULL,
    protocol integer NOT NULL,
    checkouted boolean DEFAULT false,
    for_checkout boolean DEFAULT false
);


--
-- TOC entry 1669 (class 1259 OID 125742)
-- Dependencies: 2085 2086 6
-- Name: billservice_onetimeservice; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_onetimeservice (
    id integer NOT NULL,
    name character varying(255) DEFAULT ''::character varying,
    cost double precision DEFAULT 0
);


--
-- TOC entry 1670 (class 1259 OID 125747)
-- Dependencies: 6
-- Name: billservice_onetimeservicehistory; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_onetimeservicehistory (
    id integer NOT NULL,
    accounttarif_id integer NOT NULL,
    onetimeservice_id integer NOT NULL,
    datetime timestamp without time zone NOT NULL
);


--
-- TOC entry 1671 (class 1259 OID 125750)
-- Dependencies: 2089 2090 6
-- Name: billservice_periodicalservice; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_periodicalservice (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    settlement_period_id integer NOT NULL,
    cost double precision DEFAULT 0,
    cash_method character varying(255) DEFAULT 'AT_START'::character varying
);


--
-- TOC entry 1672 (class 1259 OID 125758)
-- Dependencies: 2092 6
-- Name: billservice_periodicalservicehistory; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_periodicalservicehistory (
    id integer NOT NULL,
    service_id integer NOT NULL,
    transaction_id integer NOT NULL,
    datetime timestamp without time zone DEFAULT now()
);


--
-- TOC entry 1673 (class 1259 OID 125762)
-- Dependencies: 2094 2095 6
-- Name: billservice_ports; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_ports (
    id integer NOT NULL,
    port integer NOT NULL,
    protocol integer NOT NULL,
    name character varying(64) DEFAULT ''::character varying,
    description character varying(255) DEFAULT ''::character varying
);


--
-- TOC entry 1674 (class 1259 OID 125767)
-- Dependencies: 2097 2098 2099 2100 6
-- Name: billservice_prepaidtraffic; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_prepaidtraffic (
    id integer NOT NULL,
    traffic_transmit_service_id integer NOT NULL,
    in_direction boolean DEFAULT true,
    out_direction boolean DEFAULT true,
    transit_direction boolean DEFAULT true,
    size double precision DEFAULT 0
);


--
-- TOC entry 1675 (class 1259 OID 125774)
-- Dependencies: 6
-- Name: billservice_prepaidtraffic_traffic_class; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_prepaidtraffic_traffic_class (
    id integer NOT NULL,
    prepaidtraffic_id integer NOT NULL,
    trafficclass_id integer NOT NULL
);


--
-- TOC entry 1676 (class 1259 OID 125777)
-- Dependencies: 2103 6
-- Name: billservice_rawnetflowstream; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_rawnetflowstream (
    id integer NOT NULL,
    nas_id integer NOT NULL,
    date_start timestamp without time zone NOT NULL,
    src_addr inet NOT NULL,
    traffic_class_id integer,
    direction character varying(32) NOT NULL,
    dst_addr inet NOT NULL,
    next_hop inet NOT NULL,
    in_index integer NOT NULL,
    out_index integer NOT NULL,
    packets integer NOT NULL,
    octets integer NOT NULL,
    src_port integer NOT NULL,
    dst_port integer NOT NULL,
    tcp_flags integer NOT NULL,
    protocol integer NOT NULL,
    tos integer NOT NULL,
    source_as integer NOT NULL,
    dst_as integer NOT NULL,
    src_netmask_length integer NOT NULL,
    dst_netmask_length integer NOT NULL,
    fetched boolean DEFAULT false,
    account_id integer NOT NULL
);


--
-- TOC entry 1677 (class 1259 OID 125784)
-- Dependencies: 2105 2106 6
-- Name: billservice_settlementperiod; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_settlementperiod (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    time_start timestamp without time zone NOT NULL,
    length integer NOT NULL,
    length_in character varying(255) DEFAULT ''::character varying,
    autostart boolean DEFAULT false
);


--
-- TOC entry 1678 (class 1259 OID 125792)
-- Dependencies: 6
-- Name: billservice_shedulelog; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_shedulelog (
    id integer NOT NULL,
    account_id integer NOT NULL,
    ballance_checkout timestamp without time zone,
    prepaid_traffic_reset timestamp without time zone,
    prepaid_traffic_accrued timestamp without time zone,
    prepaid_time_reset timestamp without time zone,
    prepaid_time_accrued timestamp without time zone,
    balance_blocked timestamp without time zone
);


--
-- TOC entry 1679 (class 1259 OID 125795)
-- Dependencies: 2109 2110 2111 2112 6
-- Name: billservice_systemuser; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_systemuser (
    id integer NOT NULL,
    username character varying(255) NOT NULL,
    password character varying(255) DEFAULT ''::character varying,
    last_ip character varying(64),
    last_login timestamp without time zone,
    description text DEFAULT ''::text,
    created timestamp without time zone,
    status boolean DEFAULT false,
    host character varying(255) DEFAULT '0.0.0.0/0'::character varying
);


--
-- TOC entry 1680 (class 1259 OID 125805)
-- Dependencies: 2114 2115 2116 2117 2118 2119 6
-- Name: billservice_tariff; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_tariff (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text DEFAULT ''::text,
    access_parameters_id integer NOT NULL,
    time_access_service_id integer,
    traffic_transmit_service_id integer,
    cost double precision DEFAULT 0,
    reset_tarif_cost boolean DEFAULT false,
    settlement_period_id integer,
    ps_null_ballance_checkout boolean DEFAULT false,
    active boolean DEFAULT false,
    deleted boolean DEFAULT false
);


--
-- TOC entry 1681 (class 1259 OID 125817)
-- Dependencies: 6
-- Name: billservice_tariff_onetime_services; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_tariff_onetime_services (
    id integer NOT NULL,
    tariff_id integer NOT NULL,
    onetimeservice_id integer NOT NULL
);


--
-- TOC entry 1682 (class 1259 OID 125820)
-- Dependencies: 6
-- Name: billservice_tariff_periodical_services; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_tariff_periodical_services (
    id integer NOT NULL,
    tariff_id integer NOT NULL,
    periodicalservice_id integer NOT NULL
);


--
-- TOC entry 1683 (class 1259 OID 125823)
-- Dependencies: 6
-- Name: billservice_tariff_traffic_limit; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_tariff_traffic_limit (
    id integer NOT NULL,
    tariff_id integer NOT NULL,
    trafficlimit_id integer NOT NULL
);


--
-- TOC entry 1684 (class 1259 OID 125826)
-- Dependencies: 2124 6
-- Name: billservice_timeaccessnode; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_timeaccessnode (
    id integer NOT NULL,
    time_access_service_id integer NOT NULL,
    time_period_id integer NOT NULL,
    cost double precision DEFAULT 0
);


--
-- TOC entry 1685 (class 1259 OID 125830)
-- Dependencies: 2126 2127 6
-- Name: billservice_timeaccessservice; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_timeaccessservice (
    id integer NOT NULL,
    prepaid_time integer DEFAULT 0,
    reset_time boolean DEFAULT false
);


--
-- TOC entry 1686 (class 1259 OID 125835)
-- Dependencies: 6
-- Name: billservice_timeperiod; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_timeperiod (
    id integer NOT NULL,
    name character varying(255) NOT NULL
);


--
-- TOC entry 1687 (class 1259 OID 125838)
-- Dependencies: 6
-- Name: billservice_timeperiod_time_period_nodes; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_timeperiod_time_period_nodes (
    id integer NOT NULL,
    timeperiod_id integer NOT NULL,
    timeperiodnode_id integer NOT NULL
);


--
-- TOC entry 1688 (class 1259 OID 125841)
-- Dependencies: 2131 2132 6
-- Name: billservice_timeperiodnode; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_timeperiodnode (
    id integer NOT NULL,
    name character varying(255) DEFAULT ''::character varying,
    time_start timestamp without time zone NOT NULL,
    length integer NOT NULL,
    repeat_after character varying(255) DEFAULT ''::character varying
);


--
-- TOC entry 1689 (class 1259 OID 125849)
-- Dependencies: 2134 2135 2136 2137 2138 2139 6
-- Name: billservice_timespeed; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_timespeed (
    id integer NOT NULL,
    access_parameters_id integer NOT NULL,
    time_id integer NOT NULL,
    max_limit character varying(64) DEFAULT ''::character varying,
    min_limit character varying(64) DEFAULT ''::character varying,
    burst_limit character varying(64) DEFAULT ''::character varying,
    burst_treshold character varying(64) DEFAULT ''::character varying,
    burst_time character varying(64) DEFAULT ''::character varying,
    priority integer DEFAULT 8
);


--
-- TOC entry 1690 (class 1259 OID 125858)
-- Dependencies: 2141 2142 2143 2144 2145 6
-- Name: billservice_trafficlimit; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_trafficlimit (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    settlement_period_id integer,
    size bigint DEFAULT 0,
    in_direction boolean DEFAULT true,
    out_direction boolean DEFAULT true,
    transit_direction boolean DEFAULT true,
    mode boolean DEFAULT false
);


--
-- TOC entry 1691 (class 1259 OID 125866)
-- Dependencies: 6
-- Name: billservice_trafficlimit_traffic_class; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_trafficlimit_traffic_class (
    id integer NOT NULL,
    trafficlimit_id integer NOT NULL,
    trafficclass_id integer NOT NULL
);


--
-- TOC entry 1692 (class 1259 OID 125869)
-- Dependencies: 2148 2149 2150 2151 2152 6
-- Name: billservice_traffictransmitnodes; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_traffictransmitnodes (
    id integer NOT NULL,
    traffic_transmit_service_id integer NOT NULL,
    cost double precision DEFAULT 0,
    edge_start double precision DEFAULT 0,
    edge_end double precision DEFAULT 0,
    in_direction boolean DEFAULT true,
    out_direction boolean DEFAULT true
);


--
-- TOC entry 1693 (class 1259 OID 125877)
-- Dependencies: 6
-- Name: billservice_traffictransmitnodes_time_nodes; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_traffictransmitnodes_time_nodes (
    id integer NOT NULL,
    traffictransmitnodes_id integer NOT NULL,
    timeperiod_id integer NOT NULL
);


--
-- TOC entry 1694 (class 1259 OID 125880)
-- Dependencies: 6
-- Name: billservice_traffictransmitnodes_traffic_class; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_traffictransmitnodes_traffic_class (
    id integer NOT NULL,
    traffictransmitnodes_id integer NOT NULL,
    trafficclass_id integer NOT NULL
);


--
-- TOC entry 1695 (class 1259 OID 125883)
-- Dependencies: 2156 2157 2158 6
-- Name: billservice_traffictransmitservice; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_traffictransmitservice (
    id integer NOT NULL,
    reset_traffic boolean DEFAULT false,
    cash_method character varying(32) DEFAULT 'SUMM'::character varying,
    period_check character varying(32) DEFAULT 'SP_START'::character varying
);


--
-- TOC entry 1696 (class 1259 OID 125889)
-- Dependencies: 6
-- Name: billservice_transaction; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_transaction (
    id integer NOT NULL,
    bill character varying(255),
    account_id integer NOT NULL,
    type_id character varying,
    approved boolean,
    tarif_id integer,
    summ double precision,
    description text,
    created timestamp without time zone
);


--
-- TOC entry 1697 (class 1259 OID 125895)
-- Dependencies: 6
-- Name: billservice_transactiontype; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE billservice_transactiontype (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    internal_name character varying(32) NOT NULL
);


--
-- TOC entry 1698 (class 1259 OID 125898)
-- Dependencies: 2163 6
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE django_admin_log (
    id integer NOT NULL,
    action_time timestamp without time zone NOT NULL,
    user_id integer NOT NULL,
    content_type_id integer,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


--
-- TOC entry 1699 (class 1259 OID 125905)
-- Dependencies: 6
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE django_content_type (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


--
-- TOC entry 1700 (class 1259 OID 125908)
-- Dependencies: 6
-- Name: django_session; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp without time zone NOT NULL
);


--
-- TOC entry 1701 (class 1259 OID 125914)
-- Dependencies: 6
-- Name: django_site; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE django_site (
    id integer NOT NULL,
    domain character varying(100) NOT NULL,
    name character varying(50) NOT NULL
);


--
-- TOC entry 1702 (class 1259 OID 125917)
-- Dependencies: 2166 2167 2168 2169 2170 2171 2172 2173 2174 6
-- Name: nas_nas; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE nas_nas (
    id integer NOT NULL,
    type character varying(32) NOT NULL,
    name character varying(255) NOT NULL,
    ipaddress character varying(255) NOT NULL,
    secret character varying(255) NOT NULL,
    login character varying(255) DEFAULT 'admin'::character varying,
    password character varying(255) NOT NULL,
    allow_pptp boolean DEFAULT true,
    allow_pppoe boolean DEFAULT true,
    allow_ipn boolean DEFAULT true,
    user_add_action text,
    user_enable_action text,
    user_disable_action text,
    user_delete_action text,
    vpn_speed_action text DEFAULT ''::text,
    ipn_speed_action text DEFAULT ''::text,
    reset_action text DEFAULT ''::text,
    confstring text DEFAULT ''::text,
    multilink boolean DEFAULT false
);


--
-- TOC entry 1703 (class 1259 OID 125932)
-- Dependencies: 2176 2177 2178 6
-- Name: nas_trafficclass; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE nas_trafficclass (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    weight integer NOT NULL,
    color character varying(16) DEFAULT '#FFFFFF'::character varying,
    store boolean DEFAULT true,
    passthrough boolean DEFAULT true
);


--
-- TOC entry 1704 (class 1259 OID 125938)
-- Dependencies: 2180 2181 2182 2183 2184 2185 2186 2188 6
-- Name: nas_trafficnode; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE nas_trafficnode (
    id integer NOT NULL,
    traffic_class_id integer NOT NULL,
    name character varying(255) NOT NULL,
    direction character varying(32) NOT NULL,
    protocol integer DEFAULT 0,
    src_ip inet DEFAULT '0.0.0.0'::inet,
    src_mask inet DEFAULT '0.0.0.0'::inet,
    src_port integer DEFAULT 0,
    dst_ip inet DEFAULT '0.0.0.0'::inet,
    dst_mask inet DEFAULT '0.0.0.0'::inet,
    dst_port integer DEFAULT 0,
    next_hop inet DEFAULT '0.0.0.0'::inet
);


--
-- TOC entry 1705 (class 1259 OID 125952)
-- Dependencies: 2189 2190 6
-- Name: radius_activesession; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE radius_activesession (
    id integer NOT NULL,
    account_id integer NOT NULL,
    sessionid character varying(255),
    interrim_update timestamp without time zone DEFAULT now(),
    date_start timestamp without time zone,
    date_end timestamp without time zone,
    caller_id character varying(255),
    called_id character varying(255),
    nas_id character varying(255) NOT NULL,
    session_time integer DEFAULT 0,
    framed_protocol character varying(32) NOT NULL,
    bytes_in integer,
    bytes_out integer,
    session_status character varying(32),
    speed_string character varying(255),
    framed_ip_address character varying(255)
);


--
-- TOC entry 1706 (class 1259 OID 125960)
-- Dependencies: 2192 2193 2194 2195 2196 2197 2198 2199 2200 6
-- Name: radius_session; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE radius_session (
    id integer NOT NULL,
    account_id integer NOT NULL,
    sessionid character varying(32) DEFAULT ''::character varying,
    interrim_update timestamp without time zone DEFAULT now(),
    date_start timestamp without time zone NOT NULL,
    date_end timestamp without time zone,
    caller_id character varying(255) DEFAULT ''::character varying,
    called_id character varying(255) DEFAULT ''::character varying,
    nas_id character varying(255) NOT NULL,
    session_time integer DEFAULT 0,
    framed_protocol character varying(32) NOT NULL,
    bytes_in integer DEFAULT 0,
    bytes_out integer DEFAULT 0,
    checkouted_by_time boolean DEFAULT false,
    checkouted_by_trafic boolean DEFAULT false,
    disconnect_status character varying(32),
    framed_ip_address character varying(255)
);


--
-- TOC entry 423 (class 1247 OID 125977)
-- Dependencies: 6 1707
-- Name: targetinfo; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE targetinfo AS (
	target oid,
	schema oid,
	nargs integer,
	argtypes oidvector,
	targetname name,
	argmodes "char"[],
	argnames text[],
	targetlang oid,
	fqname text,
	returnsset boolean,
	returntype oid
);


--
-- TOC entry 425 (class 1247 OID 125980)
-- Dependencies: 6 1708
-- Name: var; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE var AS (
	name text,
	varclass character(1),
	linenumber integer,
	isunique boolean,
	isconst boolean,
	isnotnull boolean,
	dtype oid,
	value text
);


--
-- TOC entry 28 (class 1255 OID 168414)
-- Dependencies: 481 6
-- Name: append_netflow(integer, inet, inet, inet, integer, integer, integer, integer, integer, integer, integer, integer, integer, integer, integer, integer, integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION append_netflow(nas_id_ integer, src_addr_ inet, dst_addr_ inet, next_hop_ inet, in_index_ integer, out_index_ integer, packets_ integer, octets_ integer, src_port_ integer, dst_port_ integer, tcp_flags_ integer, protocol_ integer, tos_ integer, source_as_ integer, dst_as_ integer, src_netmask_length_ integer, dst_netmask_length_ integer) RETURNS integer
    AS $$
DECLARE
	mmatch BOOLEAN;
	nasclass RECORD;
	nasnode RECORD;
	checkOK BOOLEAN;
	retint integer;
	dir0 character varying(32);
	curtime TIMESTAMP WITHOUT TIME ZONE;
	acc_id integer;
BEGIN
mmatch:=FALSE;
retint := 0;
FOR nasclass IN SELECT * FROM nas_trafficclass ORDER BY weight, passthrough LOOP
	SELECT id INTO acc_id FROM billservice_account WHERE (nas_id=nas_id_) AND (vpn_ip_address=src_addr_ OR vpn_ip_address=dst_addr_ OR ipn_ip_address=src_addr_ OR ipn_ip_address=dst_addr_) LIMIT 1;
	IF (acc_id NOTNULL) THEN
		checkOK := FALSE;
		FOR nasnode IN SELECT * FROM nas_trafficnode WHERE traffic_class_id=nasclass.id ORDER BY direction DESC LOOP
			IF (nasnode.src_ip >>= src_addr_) AND (nasnode.dst_ip >>= dst_addr_) AND ((nasnode.next_hop = next_hop_) OR (nasnode.next_hop = inet '0.0.0.0')) AND ((nasnode.src_port = src_port_) OR (nasnode.src_port=0)) AND ((nasnode.dst_port = dst_port_) OR (nasnode.dst_port=0)) AND ((nasnode.protocol=protocol_) OR (nasnode.protocol=0)) THEN
				checkOK := TRUE;
				dir0 := nasnode.direction;
				EXIT;
			END IF;
		END LOOP;
		IF (checkOK IS TRUE) AND (mmatch IS FALSE) THEN
			IF (nasclass.passthrough=FALSE)  THEN
				mmatch := TRUE;
			END IF;

			INSERT INTO billservice_rawnetflowstream (nas_id, date_start, src_addr, dst_addr, traffic_class_id, direction, next_hop,in_index, out_index,packets, octets,src_port,dst_port,tcp_flags,protocol,tos, source_as, dst_as, src_netmask_length, dst_netmask_length, fetched, account_id)
				VALUES (nas_id_, CURRENT_TIMESTAMP,src_addr_, dst_addr_, nasclass.id, dir0, next_hop_, in_index_, out_index_, packets_, octets_, src_port_, dst_port_, tcp_flags_, protocol_, tos_, source_as_, dst_as_, src_netmask_length_, dst_netmask_length_, FALSE, acc_id);
			retint := retint + 1;
		END IF;
	END IF;
END LOOP;

RETURN retint;	
END;
$$
    LANGUAGE plpgsql;


--
-- TOC entry 29 (class 1255 OID 168417)
-- Dependencies: 481 6
-- Name: append_netflow2(integer, inet, inet, inet, integer, integer, integer, integer, integer, integer, integer, integer, integer, integer, integer, integer, integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION append_netflow2(nas_id_ integer, src_addr_ inet, dst_addr_ inet, next_hop_ inet, in_index_ integer, out_index_ integer, packets_ integer, octets_ integer, src_port_ integer, dst_port_ integer, tcp_flags_ integer, protocol_ integer, tos_ integer, source_as_ integer, dst_as_ integer, src_netmask_length_ integer, dst_netmask_length_ integer) RETURNS integer
    AS $$
DECLARE
	mmatch BOOLEAN;
	nasclass RECORD;
	nasnode RECORD;
	retint integer;
	curtime TIMESTAMP WITHOUT TIME ZONE;
	acc_id integer;
BEGIN
mmatch:=FALSE;
retint := 0;
FOR nasclass IN SELECT * FROM nas_trafficclass ORDER BY weight, passthrough LOOP
	SELECT id INTO acc_id FROM billservice_account WHERE (nas_id=nas_id_) AND (vpn_ip_address=src_addr_ OR vpn_ip_address=dst_addr_ OR ipn_ip_address=src_addr_ OR ipn_ip_address=dst_addr_) LIMIT 1;
	IF (acc_id NOTNULL) THEN	
		SELECT * INTO nasnode FROM nas_trafficnode WHERE (traffic_class_id=nasclass.id) AND (src_ip >>= src_addr_) AND (dst_ip >>= dst_addr_) AND ((next_hop = next_hop_) OR (next_hop = inet '0.0.0.0')) AND ((src_port = src_port_) OR (src_port=0)) AND ((dst_port = dst_port_) OR (dst_port=0)) AND ((protocol=protocol_) OR (protocol=0)) ORDER BY direction DESC LIMIT 1;
		IF (nasnode NOTNULL) AND (mmatch IS FALSE) THEN
			IF (nasclass.passthrough=FALSE)  THEN
				mmatch := TRUE;
			END IF;

			INSERT INTO billservice_rawnetflowstream (nas_id, date_start, src_addr, dst_addr, traffic_class_id, direction, next_hop,in_index, out_index,packets, octets,src_port,dst_port,tcp_flags,protocol,tos, source_as, dst_as, src_netmask_length, dst_netmask_length, fetched, account_id)
				VALUES (nas_id_, CURRENT_TIMESTAMP,src_addr_, dst_addr_, nasclass.id, nasnode.direction, next_hop_, in_index_, out_index_, packets_, octets_, src_port_, dst_port_, tcp_flags_, protocol_, tos_, source_as_, dst_as_, src_netmask_length_, dst_netmask_length_, FALSE, acc_id);
			retint := retint + 1;
		END IF;
	END IF;
END LOOP;

RETURN retint;	
END;
$$
    LANGUAGE plpgsql;


--
-- TOC entry 20 (class 1255 OID 125981)
-- Dependencies: 6 481
-- Name: block_balance(integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION block_balance(account_id integer) RETURNS void
    AS $$
BEGIN
	UPDATE billservice_account SET balance_blocked=TRUE WHERE id=account_id;
RETURN;
END;
$$
    LANGUAGE plpgsql;


--
-- TOC entry 21 (class 1255 OID 125982)
-- Dependencies: 481 6
-- Name: credit_account(integer, double precision); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION credit_account(account_id integer, sum double precision) RETURNS void
    AS $$
BEGIN
	UPDATE billservice_account SET ballance=ballance-sum WHERE id=account_id;
RETURN;
END;
$$
    LANGUAGE plpgsql;


--
-- TOC entry 22 (class 1255 OID 125983)
-- Dependencies: 6 481
-- Name: debit_account(integer, double precision); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION debit_account(account_id integer, sum double precision) RETURNS void
    AS $$
BEGIN
	UPDATE billservice_account SET ballance=ballance+sum WHERE id=account_id;
RETURN;
END;
$$
    LANGUAGE plpgsql;


--
-- TOC entry 23 (class 1255 OID 125984)
-- Dependencies: 6 481
-- Name: get_tarif(integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION get_tarif(acc_id integer) RETURNS integer
    AS $$
declare
xxx int;
begin
SELECT tarif_id INTO xxx
  FROM billservice_accounttarif WHERE account_id=acc_id and datetime<now() ORDER BY datetime DESC LIMIT 1;
RETURN xxx;
end;
$$
    LANGUAGE plpgsql;


--
-- TOC entry 24 (class 1255 OID 125985)
-- Dependencies: 6 481
-- Name: get_tarif(integer, timestamp with time zone); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION get_tarif(acc_id integer, stamp timestamp with time zone) RETURNS integer
    AS $$
declare
xxx int;
begin
SELECT tarif_id INTO xxx
  FROM billservice_accounttarif WHERE account_id=acc_id and datetime<stamp ORDER BY datetime DESC LIMIT 1;
RETURN xxx;
end;
$$
    LANGUAGE plpgsql;


--
-- TOC entry 25 (class 1255 OID 125986)
-- Dependencies: 481 6
-- Name: get_tariff_type(integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION get_tariff_type(tarif_id integer) RETURNS character varying
    AS $$
declare
ttype character varying(255);
begin
SELECT bsap.access_type INTO ttype
  FROM billservice_accessparameters AS bsap, billservice_tariff AS bstf WHERE (bsap.id=bstf.access_parameters_id) AND (bstf.id=tarif_id) ORDER BY bsap.id LIMIT 1;
IF ttype <> 'IPN' THEN
	ttype := 'VPN';
END IF;
RETURN ttype;
END;
$$
    LANGUAGE plpgsql;


--
-- TOC entry 26 (class 1255 OID 125987)
-- Dependencies: 6 361 481
-- Name: on_tariff_delete_fun(billservice_tariff); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION on_tariff_delete_fun(oldrow billservice_tariff) RETURNS record
    AS $$
        BEGIN
        IF oldrow.traffic_transmit_service_id NOTNULL THEN
            DELETE FROM billservice_traffictransmitservice WHERE id=oldrow.traffic_transmit_service_id;
        END IF;

        IF oldrow.time_access_service_id NOTNULL THEN
            DELETE FROM billservice_timeaccessservice WHERE id=oldrow.time_access_service_id;
        END IF;

        IF oldrow.access_parameters_id NOTNULL THEN
            DELETE FROM billservice_accessparameters WHERE id=oldrow.access_parameters_id;
        END IF;
               RETURN oldrow;               
        END;
$$
    LANGUAGE plpgsql;


--
-- TOC entry 27 (class 1255 OID 125988)
-- Dependencies: 6 481
-- Name: unblock_balance(integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION unblock_balance(account_id integer) RETURNS void
    AS $$
BEGIN
	UPDATE billservice_account SET balance_blocked=FALSE WHERE id=account_id;
RETURN;
END;
$$
    LANGUAGE plpgsql;


--
-- TOC entry 1709 (class 1259 OID 125989)
-- Dependencies: 6 1653
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2480 (class 0 OID 0)
-- Dependencies: 1709
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE auth_group_id_seq OWNED BY auth_group.id;


--
-- TOC entry 1710 (class 1259 OID 125991)
-- Dependencies: 6 1654
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2481 (class 0 OID 0)
-- Dependencies: 1710
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE auth_group_permissions_id_seq OWNED BY auth_group_permissions.id;


--
-- TOC entry 1711 (class 1259 OID 125993)
-- Dependencies: 1655 6
-- Name: auth_message_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE auth_message_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2482 (class 0 OID 0)
-- Dependencies: 1711
-- Name: auth_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE auth_message_id_seq OWNED BY auth_message.id;


--
-- TOC entry 1712 (class 1259 OID 125995)
-- Dependencies: 1656 6
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE auth_permission_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2483 (class 0 OID 0)
-- Dependencies: 1712
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE auth_permission_id_seq OWNED BY auth_permission.id;


--
-- TOC entry 1713 (class 1259 OID 125997)
-- Dependencies: 6 1658
-- Name: auth_user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE auth_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2484 (class 0 OID 0)
-- Dependencies: 1713
-- Name: auth_user_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE auth_user_groups_id_seq OWNED BY auth_user_groups.id;


--
-- TOC entry 1714 (class 1259 OID 125999)
-- Dependencies: 1657 6
-- Name: auth_user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE auth_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2485 (class 0 OID 0)
-- Dependencies: 1714
-- Name: auth_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE auth_user_id_seq OWNED BY auth_user.id;


--
-- TOC entry 1715 (class 1259 OID 126001)
-- Dependencies: 6 1659
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE auth_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2486 (class 0 OID 0)
-- Dependencies: 1715
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE auth_user_user_permissions_id_seq OWNED BY auth_user_user_permissions.id;


--
-- TOC entry 1716 (class 1259 OID 126003)
-- Dependencies: 6 1660
-- Name: billservice_accessparameters_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_accessparameters_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2487 (class 0 OID 0)
-- Dependencies: 1716
-- Name: billservice_accessparameters_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_accessparameters_id_seq OWNED BY billservice_accessparameters.id;


--
-- TOC entry 1717 (class 1259 OID 126005)
-- Dependencies: 1661 6
-- Name: billservice_account_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_account_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2488 (class 0 OID 0)
-- Dependencies: 1717
-- Name: billservice_account_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_account_id_seq OWNED BY billservice_account.id;


--
-- TOC entry 1718 (class 1259 OID 126007)
-- Dependencies: 1662 6
-- Name: billservice_accountipnspeed_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_accountipnspeed_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2489 (class 0 OID 0)
-- Dependencies: 1718
-- Name: billservice_accountipnspeed_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_accountipnspeed_id_seq OWNED BY billservice_accountipnspeed.id;


--
-- TOC entry 1719 (class 1259 OID 126009)
-- Dependencies: 6 1663
-- Name: billservice_accountprepaystime_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_accountprepaystime_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2490 (class 0 OID 0)
-- Dependencies: 1719
-- Name: billservice_accountprepaystime_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_accountprepaystime_id_seq OWNED BY billservice_accountprepaystime.id;


--
-- TOC entry 1720 (class 1259 OID 126011)
-- Dependencies: 6 1664
-- Name: billservice_accountprepaystrafic_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_accountprepaystrafic_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2491 (class 0 OID 0)
-- Dependencies: 1720
-- Name: billservice_accountprepaystrafic_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_accountprepaystrafic_id_seq OWNED BY billservice_accountprepaystrafic.id;


--
-- TOC entry 1721 (class 1259 OID 126013)
-- Dependencies: 6 1665
-- Name: billservice_accounttarif_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_accounttarif_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2492 (class 0 OID 0)
-- Dependencies: 1721
-- Name: billservice_accounttarif_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_accounttarif_id_seq OWNED BY billservice_accounttarif.id;


--
-- TOC entry 1722 (class 1259 OID 126015)
-- Dependencies: 1666 6
-- Name: billservice_card_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_card_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2493 (class 0 OID 0)
-- Dependencies: 1722
-- Name: billservice_card_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_card_id_seq OWNED BY billservice_card.id;


--
-- TOC entry 1723 (class 1259 OID 126017)
-- Dependencies: 1667 6
-- Name: billservice_cardgroup_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_cardgroup_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2494 (class 0 OID 0)
-- Dependencies: 1723
-- Name: billservice_cardgroup_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_cardgroup_id_seq OWNED BY billservice_cardgroup.id;


--
-- TOC entry 1724 (class 1259 OID 126019)
-- Dependencies: 1668 6
-- Name: billservice_netflowstream_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_netflowstream_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2495 (class 0 OID 0)
-- Dependencies: 1724
-- Name: billservice_netflowstream_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_netflowstream_id_seq OWNED BY billservice_netflowstream.id;


--
-- TOC entry 1725 (class 1259 OID 126021)
-- Dependencies: 1669 6
-- Name: billservice_onetimeservice_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_onetimeservice_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2496 (class 0 OID 0)
-- Dependencies: 1725
-- Name: billservice_onetimeservice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_onetimeservice_id_seq OWNED BY billservice_onetimeservice.id;


--
-- TOC entry 1726 (class 1259 OID 126023)
-- Dependencies: 6 1670
-- Name: billservice_onetimeservicehistory_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_onetimeservicehistory_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2497 (class 0 OID 0)
-- Dependencies: 1726
-- Name: billservice_onetimeservicehistory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_onetimeservicehistory_id_seq OWNED BY billservice_onetimeservicehistory.id;


--
-- TOC entry 1727 (class 1259 OID 126025)
-- Dependencies: 6 1671
-- Name: billservice_periodicalservice_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_periodicalservice_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2498 (class 0 OID 0)
-- Dependencies: 1727
-- Name: billservice_periodicalservice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_periodicalservice_id_seq OWNED BY billservice_periodicalservice.id;


--
-- TOC entry 1728 (class 1259 OID 126027)
-- Dependencies: 6 1672
-- Name: billservice_periodicalservicehistory_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_periodicalservicehistory_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2499 (class 0 OID 0)
-- Dependencies: 1728
-- Name: billservice_periodicalservicehistory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_periodicalservicehistory_id_seq OWNED BY billservice_periodicalservicehistory.id;


--
-- TOC entry 1729 (class 1259 OID 126029)
-- Dependencies: 6 1673
-- Name: billservice_ports_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_ports_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2500 (class 0 OID 0)
-- Dependencies: 1729
-- Name: billservice_ports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_ports_id_seq OWNED BY billservice_ports.id;


--
-- TOC entry 1730 (class 1259 OID 126031)
-- Dependencies: 6 1674
-- Name: billservice_prepaidtraffic_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_prepaidtraffic_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2501 (class 0 OID 0)
-- Dependencies: 1730
-- Name: billservice_prepaidtraffic_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_prepaidtraffic_id_seq OWNED BY billservice_prepaidtraffic.id;


--
-- TOC entry 1731 (class 1259 OID 126033)
-- Dependencies: 6 1675
-- Name: billservice_prepaidtraffic_traffic_class_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_prepaidtraffic_traffic_class_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2502 (class 0 OID 0)
-- Dependencies: 1731
-- Name: billservice_prepaidtraffic_traffic_class_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_prepaidtraffic_traffic_class_id_seq OWNED BY billservice_prepaidtraffic_traffic_class.id;


--
-- TOC entry 1732 (class 1259 OID 126035)
-- Dependencies: 6 1676
-- Name: billservice_rawnetflowstream_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_rawnetflowstream_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2503 (class 0 OID 0)
-- Dependencies: 1732
-- Name: billservice_rawnetflowstream_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_rawnetflowstream_id_seq OWNED BY billservice_rawnetflowstream.id;


--
-- TOC entry 1733 (class 1259 OID 126037)
-- Dependencies: 1677 6
-- Name: billservice_settlementperiod_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_settlementperiod_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2504 (class 0 OID 0)
-- Dependencies: 1733
-- Name: billservice_settlementperiod_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_settlementperiod_id_seq OWNED BY billservice_settlementperiod.id;


--
-- TOC entry 1734 (class 1259 OID 126039)
-- Dependencies: 1678 6
-- Name: billservice_shedulelog_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_shedulelog_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2505 (class 0 OID 0)
-- Dependencies: 1734
-- Name: billservice_shedulelog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_shedulelog_id_seq OWNED BY billservice_shedulelog.id;


--
-- TOC entry 1735 (class 1259 OID 126041)
-- Dependencies: 1679 6
-- Name: billservice_systemuser_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_systemuser_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2506 (class 0 OID 0)
-- Dependencies: 1735
-- Name: billservice_systemuser_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_systemuser_id_seq OWNED BY billservice_systemuser.id;


--
-- TOC entry 1736 (class 1259 OID 126043)
-- Dependencies: 1680 6
-- Name: billservice_tariff_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_tariff_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2507 (class 0 OID 0)
-- Dependencies: 1736
-- Name: billservice_tariff_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_tariff_id_seq OWNED BY billservice_tariff.id;


--
-- TOC entry 1737 (class 1259 OID 126045)
-- Dependencies: 1681 6
-- Name: billservice_tariff_onetime_services_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_tariff_onetime_services_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2508 (class 0 OID 0)
-- Dependencies: 1737
-- Name: billservice_tariff_onetime_services_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_tariff_onetime_services_id_seq OWNED BY billservice_tariff_onetime_services.id;


--
-- TOC entry 1738 (class 1259 OID 126047)
-- Dependencies: 6 1682
-- Name: billservice_tariff_periodical_services_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_tariff_periodical_services_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2509 (class 0 OID 0)
-- Dependencies: 1738
-- Name: billservice_tariff_periodical_services_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_tariff_periodical_services_id_seq OWNED BY billservice_tariff_periodical_services.id;


--
-- TOC entry 1739 (class 1259 OID 126049)
-- Dependencies: 6 1683
-- Name: billservice_tariff_traffic_limit_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_tariff_traffic_limit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2510 (class 0 OID 0)
-- Dependencies: 1739
-- Name: billservice_tariff_traffic_limit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_tariff_traffic_limit_id_seq OWNED BY billservice_tariff_traffic_limit.id;


--
-- TOC entry 1740 (class 1259 OID 126051)
-- Dependencies: 1684 6
-- Name: billservice_timeaccessnode_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_timeaccessnode_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2511 (class 0 OID 0)
-- Dependencies: 1740
-- Name: billservice_timeaccessnode_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_timeaccessnode_id_seq OWNED BY billservice_timeaccessnode.id;


--
-- TOC entry 1741 (class 1259 OID 126053)
-- Dependencies: 6 1685
-- Name: billservice_timeaccessservice_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_timeaccessservice_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2512 (class 0 OID 0)
-- Dependencies: 1741
-- Name: billservice_timeaccessservice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_timeaccessservice_id_seq OWNED BY billservice_timeaccessservice.id;


--
-- TOC entry 1742 (class 1259 OID 126055)
-- Dependencies: 6 1686
-- Name: billservice_timeperiod_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_timeperiod_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2513 (class 0 OID 0)
-- Dependencies: 1742
-- Name: billservice_timeperiod_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_timeperiod_id_seq OWNED BY billservice_timeperiod.id;


--
-- TOC entry 1743 (class 1259 OID 126057)
-- Dependencies: 1687 6
-- Name: billservice_timeperiod_time_period_nodes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_timeperiod_time_period_nodes_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2514 (class 0 OID 0)
-- Dependencies: 1743
-- Name: billservice_timeperiod_time_period_nodes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_timeperiod_time_period_nodes_id_seq OWNED BY billservice_timeperiod_time_period_nodes.id;


--
-- TOC entry 1744 (class 1259 OID 126059)
-- Dependencies: 1688 6
-- Name: billservice_timeperiodnode_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_timeperiodnode_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2515 (class 0 OID 0)
-- Dependencies: 1744
-- Name: billservice_timeperiodnode_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_timeperiodnode_id_seq OWNED BY billservice_timeperiodnode.id;


--
-- TOC entry 1745 (class 1259 OID 126061)
-- Dependencies: 6 1689
-- Name: billservice_timespeed_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_timespeed_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2516 (class 0 OID 0)
-- Dependencies: 1745
-- Name: billservice_timespeed_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_timespeed_id_seq OWNED BY billservice_timespeed.id;


--
-- TOC entry 1746 (class 1259 OID 126063)
-- Dependencies: 6 1690
-- Name: billservice_trafficlimit_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_trafficlimit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2517 (class 0 OID 0)
-- Dependencies: 1746
-- Name: billservice_trafficlimit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_trafficlimit_id_seq OWNED BY billservice_trafficlimit.id;


--
-- TOC entry 1747 (class 1259 OID 126065)
-- Dependencies: 6 1691
-- Name: billservice_trafficlimit_traffic_class_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_trafficlimit_traffic_class_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2518 (class 0 OID 0)
-- Dependencies: 1747
-- Name: billservice_trafficlimit_traffic_class_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_trafficlimit_traffic_class_id_seq OWNED BY billservice_trafficlimit_traffic_class.id;


--
-- TOC entry 1748 (class 1259 OID 126067)
-- Dependencies: 6 1692
-- Name: billservice_traffictransmitnodes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_traffictransmitnodes_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2519 (class 0 OID 0)
-- Dependencies: 1748
-- Name: billservice_traffictransmitnodes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_traffictransmitnodes_id_seq OWNED BY billservice_traffictransmitnodes.id;


--
-- TOC entry 1749 (class 1259 OID 126069)
-- Dependencies: 1693 6
-- Name: billservice_traffictransmitnodes_time_nodes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_traffictransmitnodes_time_nodes_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2520 (class 0 OID 0)
-- Dependencies: 1749
-- Name: billservice_traffictransmitnodes_time_nodes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_traffictransmitnodes_time_nodes_id_seq OWNED BY billservice_traffictransmitnodes_time_nodes.id;


--
-- TOC entry 1750 (class 1259 OID 126071)
-- Dependencies: 6 1694
-- Name: billservice_traffictransmitnodes_traffic_class_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_traffictransmitnodes_traffic_class_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2521 (class 0 OID 0)
-- Dependencies: 1750
-- Name: billservice_traffictransmitnodes_traffic_class_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_traffictransmitnodes_traffic_class_id_seq OWNED BY billservice_traffictransmitnodes_traffic_class.id;


--
-- TOC entry 1751 (class 1259 OID 126073)
-- Dependencies: 6 1695
-- Name: billservice_traffictransmitservice_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_traffictransmitservice_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2522 (class 0 OID 0)
-- Dependencies: 1751
-- Name: billservice_traffictransmitservice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_traffictransmitservice_id_seq OWNED BY billservice_traffictransmitservice.id;


--
-- TOC entry 1752 (class 1259 OID 126075)
-- Dependencies: 1696 6
-- Name: billservice_transaction_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_transaction_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2523 (class 0 OID 0)
-- Dependencies: 1752
-- Name: billservice_transaction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_transaction_id_seq OWNED BY billservice_transaction.id;


--
-- TOC entry 1753 (class 1259 OID 126077)
-- Dependencies: 6 1697
-- Name: billservice_transactiontype_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE billservice_transactiontype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2524 (class 0 OID 0)
-- Dependencies: 1753
-- Name: billservice_transactiontype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE billservice_transactiontype_id_seq OWNED BY billservice_transactiontype.id;


--
-- TOC entry 1754 (class 1259 OID 126079)
-- Dependencies: 6 1698
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2525 (class 0 OID 0)
-- Dependencies: 1754
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE django_admin_log_id_seq OWNED BY django_admin_log.id;


--
-- TOC entry 1755 (class 1259 OID 126081)
-- Dependencies: 1699 6
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE django_content_type_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2526 (class 0 OID 0)
-- Dependencies: 1755
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE django_content_type_id_seq OWNED BY django_content_type.id;


--
-- TOC entry 1756 (class 1259 OID 126083)
-- Dependencies: 6 1701
-- Name: django_site_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE django_site_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2527 (class 0 OID 0)
-- Dependencies: 1756
-- Name: django_site_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE django_site_id_seq OWNED BY django_site.id;


--
-- TOC entry 1757 (class 1259 OID 126085)
-- Dependencies: 6 1702
-- Name: nas_nas_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE nas_nas_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2528 (class 0 OID 0)
-- Dependencies: 1757
-- Name: nas_nas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE nas_nas_id_seq OWNED BY nas_nas.id;


--
-- TOC entry 1758 (class 1259 OID 126087)
-- Dependencies: 6 1703
-- Name: nas_trafficclass_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE nas_trafficclass_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2529 (class 0 OID 0)
-- Dependencies: 1758
-- Name: nas_trafficclass_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE nas_trafficclass_id_seq OWNED BY nas_trafficclass.id;


--
-- TOC entry 1759 (class 1259 OID 126089)
-- Dependencies: 6 1704
-- Name: nas_trafficnode_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE nas_trafficnode_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2530 (class 0 OID 0)
-- Dependencies: 1759
-- Name: nas_trafficnode_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE nas_trafficnode_id_seq OWNED BY nas_trafficnode.id;


--
-- TOC entry 1760 (class 1259 OID 126091)
-- Dependencies: 6 1705
-- Name: radius_activesession_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE radius_activesession_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2531 (class 0 OID 0)
-- Dependencies: 1760
-- Name: radius_activesession_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE radius_activesession_id_seq OWNED BY radius_activesession.id;


--
-- TOC entry 1761 (class 1259 OID 126093)
-- Dependencies: 6 1706
-- Name: radius_session_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE radius_session_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 2532 (class 0 OID 0)
-- Dependencies: 1761
-- Name: radius_session_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE radius_session_id_seq OWNED BY radius_session.id;


--
-- TOC entry 2029 (class 2604 OID 126095)
-- Dependencies: 1709 1653
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE auth_group ALTER COLUMN id SET DEFAULT nextval('auth_group_id_seq'::regclass);


--
-- TOC entry 2030 (class 2604 OID 126096)
-- Dependencies: 1710 1654
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('auth_group_permissions_id_seq'::regclass);


--
-- TOC entry 2031 (class 2604 OID 126097)
-- Dependencies: 1711 1655
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE auth_message ALTER COLUMN id SET DEFAULT nextval('auth_message_id_seq'::regclass);


--
-- TOC entry 2032 (class 2604 OID 126098)
-- Dependencies: 1712 1656
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE auth_permission ALTER COLUMN id SET DEFAULT nextval('auth_permission_id_seq'::regclass);


--
-- TOC entry 2033 (class 2604 OID 126099)
-- Dependencies: 1714 1657
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE auth_user ALTER COLUMN id SET DEFAULT nextval('auth_user_id_seq'::regclass);


--
-- TOC entry 2034 (class 2604 OID 126100)
-- Dependencies: 1713 1658
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE auth_user_groups ALTER COLUMN id SET DEFAULT nextval('auth_user_groups_id_seq'::regclass);


--
-- TOC entry 2035 (class 2604 OID 126101)
-- Dependencies: 1715 1659
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE auth_user_user_permissions ALTER COLUMN id SET DEFAULT nextval('auth_user_user_permissions_id_seq'::regclass);


--
-- TOC entry 2043 (class 2604 OID 126102)
-- Dependencies: 1716 1660
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_accessparameters ALTER COLUMN id SET DEFAULT nextval('billservice_accessparameters_id_seq'::regclass);


--
-- TOC entry 2063 (class 2604 OID 126103)
-- Dependencies: 1717 1661
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_account ALTER COLUMN id SET DEFAULT nextval('billservice_account_id_seq'::regclass);


--
-- TOC entry 2068 (class 2604 OID 126104)
-- Dependencies: 1718 1662
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_accountipnspeed ALTER COLUMN id SET DEFAULT nextval('billservice_accountipnspeed_id_seq'::regclass);


--
-- TOC entry 2071 (class 2604 OID 126105)
-- Dependencies: 1719 1663
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_accountprepaystime ALTER COLUMN id SET DEFAULT nextval('billservice_accountprepaystime_id_seq'::regclass);


--
-- TOC entry 2074 (class 2604 OID 126106)
-- Dependencies: 1720 1664
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_accountprepaystrafic ALTER COLUMN id SET DEFAULT nextval('billservice_accountprepaystrafic_id_seq'::regclass);


--
-- TOC entry 2075 (class 2604 OID 126107)
-- Dependencies: 1721 1665
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_accounttarif ALTER COLUMN id SET DEFAULT nextval('billservice_accounttarif_id_seq'::regclass);


--
-- TOC entry 2078 (class 2604 OID 126108)
-- Dependencies: 1722 1666
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_card ALTER COLUMN id SET DEFAULT nextval('billservice_card_id_seq'::regclass);


--
-- TOC entry 2080 (class 2604 OID 126109)
-- Dependencies: 1723 1667
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_cardgroup ALTER COLUMN id SET DEFAULT nextval('billservice_cardgroup_id_seq'::regclass);


--
-- TOC entry 2084 (class 2604 OID 126110)
-- Dependencies: 1724 1668
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_netflowstream ALTER COLUMN id SET DEFAULT nextval('billservice_netflowstream_id_seq'::regclass);


--
-- TOC entry 2087 (class 2604 OID 126111)
-- Dependencies: 1725 1669
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_onetimeservice ALTER COLUMN id SET DEFAULT nextval('billservice_onetimeservice_id_seq'::regclass);


--
-- TOC entry 2088 (class 2604 OID 126112)
-- Dependencies: 1726 1670
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_onetimeservicehistory ALTER COLUMN id SET DEFAULT nextval('billservice_onetimeservicehistory_id_seq'::regclass);


--
-- TOC entry 2091 (class 2604 OID 126113)
-- Dependencies: 1727 1671
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_periodicalservice ALTER COLUMN id SET DEFAULT nextval('billservice_periodicalservice_id_seq'::regclass);


--
-- TOC entry 2093 (class 2604 OID 126114)
-- Dependencies: 1728 1672
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_periodicalservicehistory ALTER COLUMN id SET DEFAULT nextval('billservice_periodicalservicehistory_id_seq'::regclass);


--
-- TOC entry 2096 (class 2604 OID 126115)
-- Dependencies: 1729 1673
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_ports ALTER COLUMN id SET DEFAULT nextval('billservice_ports_id_seq'::regclass);


--
-- TOC entry 2101 (class 2604 OID 126116)
-- Dependencies: 1730 1674
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_prepaidtraffic ALTER COLUMN id SET DEFAULT nextval('billservice_prepaidtraffic_id_seq'::regclass);


--
-- TOC entry 2102 (class 2604 OID 126117)
-- Dependencies: 1731 1675
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_prepaidtraffic_traffic_class ALTER COLUMN id SET DEFAULT nextval('billservice_prepaidtraffic_traffic_class_id_seq'::regclass);


--
-- TOC entry 2104 (class 2604 OID 126118)
-- Dependencies: 1732 1676
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_rawnetflowstream ALTER COLUMN id SET DEFAULT nextval('billservice_rawnetflowstream_id_seq'::regclass);


--
-- TOC entry 2107 (class 2604 OID 126119)
-- Dependencies: 1733 1677
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_settlementperiod ALTER COLUMN id SET DEFAULT nextval('billservice_settlementperiod_id_seq'::regclass);


--
-- TOC entry 2108 (class 2604 OID 126120)
-- Dependencies: 1734 1678
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_shedulelog ALTER COLUMN id SET DEFAULT nextval('billservice_shedulelog_id_seq'::regclass);


--
-- TOC entry 2113 (class 2604 OID 126121)
-- Dependencies: 1735 1679
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_systemuser ALTER COLUMN id SET DEFAULT nextval('billservice_systemuser_id_seq'::regclass);


--
-- TOC entry 2120 (class 2604 OID 126122)
-- Dependencies: 1736 1680
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_tariff ALTER COLUMN id SET DEFAULT nextval('billservice_tariff_id_seq'::regclass);


--
-- TOC entry 2121 (class 2604 OID 126123)
-- Dependencies: 1737 1681
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_tariff_onetime_services ALTER COLUMN id SET DEFAULT nextval('billservice_tariff_onetime_services_id_seq'::regclass);


--
-- TOC entry 2122 (class 2604 OID 126124)
-- Dependencies: 1738 1682
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_tariff_periodical_services ALTER COLUMN id SET DEFAULT nextval('billservice_tariff_periodical_services_id_seq'::regclass);


--
-- TOC entry 2123 (class 2604 OID 126125)
-- Dependencies: 1739 1683
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_tariff_traffic_limit ALTER COLUMN id SET DEFAULT nextval('billservice_tariff_traffic_limit_id_seq'::regclass);


--
-- TOC entry 2125 (class 2604 OID 126126)
-- Dependencies: 1740 1684
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_timeaccessnode ALTER COLUMN id SET DEFAULT nextval('billservice_timeaccessnode_id_seq'::regclass);


--
-- TOC entry 2128 (class 2604 OID 126127)
-- Dependencies: 1741 1685
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_timeaccessservice ALTER COLUMN id SET DEFAULT nextval('billservice_timeaccessservice_id_seq'::regclass);


--
-- TOC entry 2129 (class 2604 OID 126128)
-- Dependencies: 1742 1686
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_timeperiod ALTER COLUMN id SET DEFAULT nextval('billservice_timeperiod_id_seq'::regclass);


--
-- TOC entry 2130 (class 2604 OID 126129)
-- Dependencies: 1743 1687
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_timeperiod_time_period_nodes ALTER COLUMN id SET DEFAULT nextval('billservice_timeperiod_time_period_nodes_id_seq'::regclass);


--
-- TOC entry 2133 (class 2604 OID 126130)
-- Dependencies: 1744 1688
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_timeperiodnode ALTER COLUMN id SET DEFAULT nextval('billservice_timeperiodnode_id_seq'::regclass);


--
-- TOC entry 2140 (class 2604 OID 126131)
-- Dependencies: 1745 1689
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_timespeed ALTER COLUMN id SET DEFAULT nextval('billservice_timespeed_id_seq'::regclass);


--
-- TOC entry 2146 (class 2604 OID 126132)
-- Dependencies: 1746 1690
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_trafficlimit ALTER COLUMN id SET DEFAULT nextval('billservice_trafficlimit_id_seq'::regclass);


--
-- TOC entry 2147 (class 2604 OID 126133)
-- Dependencies: 1747 1691
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_trafficlimit_traffic_class ALTER COLUMN id SET DEFAULT nextval('billservice_trafficlimit_traffic_class_id_seq'::regclass);


--
-- TOC entry 2153 (class 2604 OID 126134)
-- Dependencies: 1748 1692
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_traffictransmitnodes ALTER COLUMN id SET DEFAULT nextval('billservice_traffictransmitnodes_id_seq'::regclass);


--
-- TOC entry 2154 (class 2604 OID 126135)
-- Dependencies: 1749 1693
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_traffictransmitnodes_time_nodes ALTER COLUMN id SET DEFAULT nextval('billservice_traffictransmitnodes_time_nodes_id_seq'::regclass);


--
-- TOC entry 2155 (class 2604 OID 126136)
-- Dependencies: 1750 1694
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_traffictransmitnodes_traffic_class ALTER COLUMN id SET DEFAULT nextval('billservice_traffictransmitnodes_traffic_class_id_seq'::regclass);


--
-- TOC entry 2159 (class 2604 OID 126137)
-- Dependencies: 1751 1695
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_traffictransmitservice ALTER COLUMN id SET DEFAULT nextval('billservice_traffictransmitservice_id_seq'::regclass);


--
-- TOC entry 2160 (class 2604 OID 126138)
-- Dependencies: 1752 1696
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_transaction ALTER COLUMN id SET DEFAULT nextval('billservice_transaction_id_seq'::regclass);


--
-- TOC entry 2161 (class 2604 OID 126139)
-- Dependencies: 1753 1697
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE billservice_transactiontype ALTER COLUMN id SET DEFAULT nextval('billservice_transactiontype_id_seq'::regclass);


--
-- TOC entry 2162 (class 2604 OID 126140)
-- Dependencies: 1754 1698
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE django_admin_log ALTER COLUMN id SET DEFAULT nextval('django_admin_log_id_seq'::regclass);


--
-- TOC entry 2164 (class 2604 OID 126141)
-- Dependencies: 1755 1699
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE django_content_type ALTER COLUMN id SET DEFAULT nextval('django_content_type_id_seq'::regclass);


--
-- TOC entry 2165 (class 2604 OID 126142)
-- Dependencies: 1756 1701
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE django_site ALTER COLUMN id SET DEFAULT nextval('django_site_id_seq'::regclass);


--
-- TOC entry 2175 (class 2604 OID 126143)
-- Dependencies: 1757 1702
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE nas_nas ALTER COLUMN id SET DEFAULT nextval('nas_nas_id_seq'::regclass);


--
-- TOC entry 2179 (class 2604 OID 126144)
-- Dependencies: 1758 1703
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE nas_trafficclass ALTER COLUMN id SET DEFAULT nextval('nas_trafficclass_id_seq'::regclass);


--
-- TOC entry 2187 (class 2604 OID 126145)
-- Dependencies: 1759 1704
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE nas_trafficnode ALTER COLUMN id SET DEFAULT nextval('nas_trafficnode_id_seq'::regclass);


--
-- TOC entry 2191 (class 2604 OID 126146)
-- Dependencies: 1760 1705
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE radius_activesession ALTER COLUMN id SET DEFAULT nextval('radius_activesession_id_seq'::regclass);


--
-- TOC entry 2201 (class 2604 OID 126147)
-- Dependencies: 1761 1706
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE radius_session ALTER COLUMN id SET DEFAULT nextval('radius_session_id_seq'::regclass);


--
-- TOC entry 2203 (class 2606 OID 126149)
-- Dependencies: 1653 1653
-- Name: auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- TOC entry 2207 (class 2606 OID 126151)
-- Dependencies: 1654 1654 1654
-- Name: auth_group_permissions_group_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_key UNIQUE (group_id, permission_id);


--
-- TOC entry 2209 (class 2606 OID 126153)
-- Dependencies: 1654 1654
-- Name: auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- TOC entry 2205 (class 2606 OID 126155)
-- Dependencies: 1653 1653
-- Name: auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- TOC entry 2211 (class 2606 OID 126157)
-- Dependencies: 1655 1655
-- Name: auth_message_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY auth_message
    ADD CONSTRAINT auth_message_pkey PRIMARY KEY (id);


--
-- TOC entry 2215 (class 2606 OID 126159)
-- Dependencies: 1656 1656 1656
-- Name: auth_permission_content_type_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_key UNIQUE (content_type_id, codename);


--
-- TOC entry 2217 (class 2606 OID 126161)
-- Dependencies: 1656 1656
-- Name: auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- TOC entry 2223 (class 2606 OID 126163)
-- Dependencies: 1658 1658
-- Name: auth_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);


--
-- TOC entry 2225 (class 2606 OID 126165)
-- Dependencies: 1658 1658 1658
-- Name: auth_user_groups_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_key UNIQUE (user_id, group_id);


--
-- TOC entry 2219 (class 2606 OID 126167)
-- Dependencies: 1657 1657
-- Name: auth_user_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);


--
-- TOC entry 2227 (class 2606 OID 126169)
-- Dependencies: 1659 1659
-- Name: auth_user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);


--
-- TOC entry 2229 (class 2606 OID 126171)
-- Dependencies: 1659 1659 1659
-- Name: auth_user_user_permissions_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_key UNIQUE (user_id, permission_id);


--
-- TOC entry 2221 (class 2606 OID 126173)
-- Dependencies: 1657 1657
-- Name: auth_user_username_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);


--
-- TOC entry 2232 (class 2606 OID 126175)
-- Dependencies: 1660 1660
-- Name: billservice_accessparameters_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_accessparameters
    ADD CONSTRAINT billservice_accessparameters_pkey PRIMARY KEY (id);


--
-- TOC entry 2236 (class 2606 OID 126177)
-- Dependencies: 1661 1661
-- Name: billservice_account_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_account
    ADD CONSTRAINT billservice_account_pkey PRIMARY KEY (id);


--
-- TOC entry 2238 (class 2606 OID 126179)
-- Dependencies: 1661 1661
-- Name: billservice_account_username_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_account
    ADD CONSTRAINT billservice_account_username_key UNIQUE (username);


--
-- TOC entry 2242 (class 2606 OID 126181)
-- Dependencies: 1662 1662
-- Name: billservice_accountipnspeed_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_accountipnspeed
    ADD CONSTRAINT billservice_accountipnspeed_pkey PRIMARY KEY (id);


--
-- TOC entry 2245 (class 2606 OID 126183)
-- Dependencies: 1663 1663
-- Name: billservice_accountprepaystime_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_accountprepaystime
    ADD CONSTRAINT billservice_accountprepaystime_pkey PRIMARY KEY (id);


--
-- TOC entry 2249 (class 2606 OID 126185)
-- Dependencies: 1664 1664
-- Name: billservice_accountprepaystrafic_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_accountprepaystrafic
    ADD CONSTRAINT billservice_accountprepaystrafic_pkey PRIMARY KEY (id);


--
-- TOC entry 2253 (class 2606 OID 126187)
-- Dependencies: 1665 1665
-- Name: billservice_accounttarif_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_accounttarif
    ADD CONSTRAINT billservice_accounttarif_pkey PRIMARY KEY (id);


--
-- TOC entry 2258 (class 2606 OID 126189)
-- Dependencies: 1666 1666
-- Name: billservice_card_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_card
    ADD CONSTRAINT billservice_card_pkey PRIMARY KEY (id);


--
-- TOC entry 2260 (class 2606 OID 126191)
-- Dependencies: 1667 1667
-- Name: billservice_cardgroup_name_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_cardgroup
    ADD CONSTRAINT billservice_cardgroup_name_key UNIQUE (name);


--
-- TOC entry 2262 (class 2606 OID 126193)
-- Dependencies: 1667 1667
-- Name: billservice_cardgroup_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_cardgroup
    ADD CONSTRAINT billservice_cardgroup_pkey PRIMARY KEY (id);


--
-- TOC entry 2266 (class 2606 OID 126195)
-- Dependencies: 1668 1668
-- Name: billservice_netflowstream_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_netflowstream
    ADD CONSTRAINT billservice_netflowstream_pkey PRIMARY KEY (id);


--
-- TOC entry 2271 (class 2606 OID 126197)
-- Dependencies: 1669 1669
-- Name: billservice_onetimeservice_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_onetimeservice
    ADD CONSTRAINT billservice_onetimeservice_pkey PRIMARY KEY (id);


--
-- TOC entry 2275 (class 2606 OID 126199)
-- Dependencies: 1670 1670
-- Name: billservice_onetimeservicehistory_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_onetimeservicehistory
    ADD CONSTRAINT billservice_onetimeservicehistory_pkey PRIMARY KEY (id);


--
-- TOC entry 2277 (class 2606 OID 126201)
-- Dependencies: 1671 1671
-- Name: billservice_periodicalservice_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_periodicalservice
    ADD CONSTRAINT billservice_periodicalservice_pkey PRIMARY KEY (id);


--
-- TOC entry 2280 (class 2606 OID 126203)
-- Dependencies: 1672 1672
-- Name: billservice_periodicalservicehistory_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_periodicalservicehistory
    ADD CONSTRAINT billservice_periodicalservicehistory_pkey PRIMARY KEY (id);


--
-- TOC entry 2284 (class 2606 OID 126205)
-- Dependencies: 1673 1673
-- Name: billservice_ports_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_ports
    ADD CONSTRAINT billservice_ports_pkey PRIMARY KEY (id);


--
-- TOC entry 2286 (class 2606 OID 126207)
-- Dependencies: 1674 1674
-- Name: billservice_prepaidtraffic_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_prepaidtraffic
    ADD CONSTRAINT billservice_prepaidtraffic_pkey PRIMARY KEY (id);


--
-- TOC entry 2289 (class 2606 OID 126209)
-- Dependencies: 1675 1675
-- Name: billservice_prepaidtraffic_traffic_class_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_prepaidtraffic_traffic_class
    ADD CONSTRAINT billservice_prepaidtraffic_traffic_class_pkey PRIMARY KEY (id);


--
-- TOC entry 2291 (class 2606 OID 126211)
-- Dependencies: 1675 1675 1675
-- Name: billservice_prepaidtraffic_traffic_class_prepaidtraffic_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_prepaidtraffic_traffic_class
    ADD CONSTRAINT billservice_prepaidtraffic_traffic_class_prepaidtraffic_id_key UNIQUE (prepaidtraffic_id, trafficclass_id);


--
-- TOC entry 2294 (class 2606 OID 126213)
-- Dependencies: 1676 1676
-- Name: billservice_rawnetflowstream_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_rawnetflowstream
    ADD CONSTRAINT billservice_rawnetflowstream_pkey PRIMARY KEY (id);


--
-- TOC entry 2297 (class 2606 OID 126215)
-- Dependencies: 1677 1677
-- Name: billservice_settlementperiod_name_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_settlementperiod
    ADD CONSTRAINT billservice_settlementperiod_name_key UNIQUE (name);


--
-- TOC entry 2299 (class 2606 OID 126217)
-- Dependencies: 1677 1677
-- Name: billservice_settlementperiod_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_settlementperiod
    ADD CONSTRAINT billservice_settlementperiod_pkey PRIMARY KEY (id);


--
-- TOC entry 2301 (class 2606 OID 126219)
-- Dependencies: 1678 1678
-- Name: billservice_shedulelog_account_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_shedulelog
    ADD CONSTRAINT billservice_shedulelog_account_id_key UNIQUE (account_id);


--
-- TOC entry 2303 (class 2606 OID 126221)
-- Dependencies: 1678 1678
-- Name: billservice_shedulelog_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_shedulelog
    ADD CONSTRAINT billservice_shedulelog_pkey PRIMARY KEY (id);


--
-- TOC entry 2305 (class 2606 OID 126223)
-- Dependencies: 1679 1679
-- Name: billservice_systemuser_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_systemuser
    ADD CONSTRAINT billservice_systemuser_pkey PRIMARY KEY (id);


--
-- TOC entry 2307 (class 2606 OID 126225)
-- Dependencies: 1679 1679
-- Name: billservice_systemuser_username_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_systemuser
    ADD CONSTRAINT billservice_systemuser_username_key UNIQUE (username);


--
-- TOC entry 2310 (class 2606 OID 126227)
-- Dependencies: 1680 1680
-- Name: billservice_tariff_name_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_tariff
    ADD CONSTRAINT billservice_tariff_name_key UNIQUE (name);


--
-- TOC entry 2317 (class 2606 OID 126229)
-- Dependencies: 1681 1681
-- Name: billservice_tariff_onetime_services_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_tariff_onetime_services
    ADD CONSTRAINT billservice_tariff_onetime_services_pkey PRIMARY KEY (id);


--
-- TOC entry 2319 (class 2606 OID 126231)
-- Dependencies: 1681 1681 1681
-- Name: billservice_tariff_onetime_services_tariff_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_tariff_onetime_services
    ADD CONSTRAINT billservice_tariff_onetime_services_tariff_id_key UNIQUE (tariff_id, onetimeservice_id);


--
-- TOC entry 2321 (class 2606 OID 126233)
-- Dependencies: 1682 1682
-- Name: billservice_tariff_periodical_services_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_tariff_periodical_services
    ADD CONSTRAINT billservice_tariff_periodical_services_pkey PRIMARY KEY (id);


--
-- TOC entry 2323 (class 2606 OID 126235)
-- Dependencies: 1682 1682 1682
-- Name: billservice_tariff_periodical_services_tariff_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_tariff_periodical_services
    ADD CONSTRAINT billservice_tariff_periodical_services_tariff_id_key UNIQUE (tariff_id, periodicalservice_id);


--
-- TOC entry 2312 (class 2606 OID 126237)
-- Dependencies: 1680 1680
-- Name: billservice_tariff_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_tariff
    ADD CONSTRAINT billservice_tariff_pkey PRIMARY KEY (id);


--
-- TOC entry 2325 (class 2606 OID 126239)
-- Dependencies: 1683 1683
-- Name: billservice_tariff_traffic_limit_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_tariff_traffic_limit
    ADD CONSTRAINT billservice_tariff_traffic_limit_pkey PRIMARY KEY (id);


--
-- TOC entry 2327 (class 2606 OID 126241)
-- Dependencies: 1683 1683 1683
-- Name: billservice_tariff_traffic_limit_tariff_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_tariff_traffic_limit
    ADD CONSTRAINT billservice_tariff_traffic_limit_tariff_id_key UNIQUE (tariff_id, trafficlimit_id);


--
-- TOC entry 2329 (class 2606 OID 126243)
-- Dependencies: 1684 1684
-- Name: billservice_timeaccessnode_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_timeaccessnode
    ADD CONSTRAINT billservice_timeaccessnode_pkey PRIMARY KEY (id);


--
-- TOC entry 2333 (class 2606 OID 126245)
-- Dependencies: 1685 1685
-- Name: billservice_timeaccessservice_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_timeaccessservice
    ADD CONSTRAINT billservice_timeaccessservice_pkey PRIMARY KEY (id);


--
-- TOC entry 2335 (class 2606 OID 126247)
-- Dependencies: 1686 1686
-- Name: billservice_timeperiod_name_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_timeperiod
    ADD CONSTRAINT billservice_timeperiod_name_key UNIQUE (name);


--
-- TOC entry 2337 (class 2606 OID 126249)
-- Dependencies: 1686 1686
-- Name: billservice_timeperiod_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_timeperiod
    ADD CONSTRAINT billservice_timeperiod_pkey PRIMARY KEY (id);


--
-- TOC entry 2339 (class 2606 OID 126251)
-- Dependencies: 1687 1687
-- Name: billservice_timeperiod_time_period_nodes_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_timeperiod_time_period_nodes
    ADD CONSTRAINT billservice_timeperiod_time_period_nodes_pkey PRIMARY KEY (id);


--
-- TOC entry 2341 (class 2606 OID 126253)
-- Dependencies: 1687 1687 1687
-- Name: billservice_timeperiod_time_period_nodes_timeperiod_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_timeperiod_time_period_nodes
    ADD CONSTRAINT billservice_timeperiod_time_period_nodes_timeperiod_id_key UNIQUE (timeperiod_id, timeperiodnode_id);


--
-- TOC entry 2343 (class 2606 OID 126255)
-- Dependencies: 1688 1688
-- Name: billservice_timeperiodnode_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_timeperiodnode
    ADD CONSTRAINT billservice_timeperiodnode_pkey PRIMARY KEY (id);


--
-- TOC entry 2346 (class 2606 OID 126257)
-- Dependencies: 1689 1689
-- Name: billservice_timespeed_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_timespeed
    ADD CONSTRAINT billservice_timespeed_pkey PRIMARY KEY (id);


--
-- TOC entry 2349 (class 2606 OID 126259)
-- Dependencies: 1690 1690
-- Name: billservice_trafficlimit_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_trafficlimit
    ADD CONSTRAINT billservice_trafficlimit_pkey PRIMARY KEY (id);


--
-- TOC entry 2352 (class 2606 OID 126261)
-- Dependencies: 1691 1691
-- Name: billservice_trafficlimit_traffic_class_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_trafficlimit_traffic_class
    ADD CONSTRAINT billservice_trafficlimit_traffic_class_pkey PRIMARY KEY (id);


--
-- TOC entry 2354 (class 2606 OID 126263)
-- Dependencies: 1691 1691 1691
-- Name: billservice_trafficlimit_traffic_class_trafficlimit_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_trafficlimit_traffic_class
    ADD CONSTRAINT billservice_trafficlimit_traffic_class_trafficlimit_id_key UNIQUE (trafficlimit_id, trafficclass_id);


--
-- TOC entry 2356 (class 2606 OID 126265)
-- Dependencies: 1692 1692
-- Name: billservice_traffictransmitnodes_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_traffictransmitnodes
    ADD CONSTRAINT billservice_traffictransmitnodes_pkey PRIMARY KEY (id);


--
-- TOC entry 2359 (class 2606 OID 126267)
-- Dependencies: 1693 1693 1693
-- Name: billservice_traffictransmitnodes_ti_traffictransmitnodes_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_traffictransmitnodes_time_nodes
    ADD CONSTRAINT billservice_traffictransmitnodes_ti_traffictransmitnodes_id_key UNIQUE (traffictransmitnodes_id, timeperiod_id);


--
-- TOC entry 2361 (class 2606 OID 126269)
-- Dependencies: 1693 1693
-- Name: billservice_traffictransmitnodes_time_nodes_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_traffictransmitnodes_time_nodes
    ADD CONSTRAINT billservice_traffictransmitnodes_time_nodes_pkey PRIMARY KEY (id);


--
-- TOC entry 2363 (class 2606 OID 126271)
-- Dependencies: 1694 1694 1694
-- Name: billservice_traffictransmitnodes_tr_traffictransmitnodes_id_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_traffictransmitnodes_traffic_class
    ADD CONSTRAINT billservice_traffictransmitnodes_tr_traffictransmitnodes_id_key UNIQUE (traffictransmitnodes_id, trafficclass_id);


--
-- TOC entry 2365 (class 2606 OID 126273)
-- Dependencies: 1694 1694
-- Name: billservice_traffictransmitnodes_traffic_class_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_traffictransmitnodes_traffic_class
    ADD CONSTRAINT billservice_traffictransmitnodes_traffic_class_pkey PRIMARY KEY (id);


--
-- TOC entry 2367 (class 2606 OID 126275)
-- Dependencies: 1695 1695
-- Name: billservice_traffictransmitservice_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_traffictransmitservice
    ADD CONSTRAINT billservice_traffictransmitservice_pkey PRIMARY KEY (id);


--
-- TOC entry 2370 (class 2606 OID 126277)
-- Dependencies: 1696 1696
-- Name: billservice_transaction_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_transaction
    ADD CONSTRAINT billservice_transaction_pkey PRIMARY KEY (id);


--
-- TOC entry 2373 (class 2606 OID 126279)
-- Dependencies: 1697 1697
-- Name: billservice_transactiontype_internal_name_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_transactiontype
    ADD CONSTRAINT billservice_transactiontype_internal_name_key UNIQUE (internal_name);


--
-- TOC entry 2375 (class 2606 OID 126281)
-- Dependencies: 1697 1697
-- Name: billservice_transactiontype_name_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_transactiontype
    ADD CONSTRAINT billservice_transactiontype_name_key UNIQUE (name);


--
-- TOC entry 2377 (class 2606 OID 126283)
-- Dependencies: 1697 1697
-- Name: billservice_transactiontype_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY billservice_transactiontype
    ADD CONSTRAINT billservice_transactiontype_pkey PRIMARY KEY (id);


--
-- TOC entry 2380 (class 2606 OID 126285)
-- Dependencies: 1698 1698
-- Name: django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- TOC entry 2383 (class 2606 OID 126287)
-- Dependencies: 1699 1699 1699
-- Name: django_content_type_app_label_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_app_label_key UNIQUE (app_label, model);


--
-- TOC entry 2385 (class 2606 OID 126289)
-- Dependencies: 1699 1699
-- Name: django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- TOC entry 2387 (class 2606 OID 126291)
-- Dependencies: 1700 1700
-- Name: django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- TOC entry 2389 (class 2606 OID 126293)
-- Dependencies: 1701 1701
-- Name: django_site_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY django_site
    ADD CONSTRAINT django_site_pkey PRIMARY KEY (id);


--
-- TOC entry 2391 (class 2606 OID 126295)
-- Dependencies: 1702 1702
-- Name: nas_nas_name_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY nas_nas
    ADD CONSTRAINT nas_nas_name_key UNIQUE (name);


--
-- TOC entry 2393 (class 2606 OID 126297)
-- Dependencies: 1702 1702
-- Name: nas_nas_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY nas_nas
    ADD CONSTRAINT nas_nas_pkey PRIMARY KEY (id);


--
-- TOC entry 2395 (class 2606 OID 126299)
-- Dependencies: 1703 1703
-- Name: nas_trafficclass_name_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY nas_trafficclass
    ADD CONSTRAINT nas_trafficclass_name_key UNIQUE (name);


--
-- TOC entry 2397 (class 2606 OID 126301)
-- Dependencies: 1703 1703
-- Name: nas_trafficclass_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY nas_trafficclass
    ADD CONSTRAINT nas_trafficclass_pkey PRIMARY KEY (id);


--
-- TOC entry 2399 (class 2606 OID 126303)
-- Dependencies: 1703 1703
-- Name: nas_trafficclass_weight_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY nas_trafficclass
    ADD CONSTRAINT nas_trafficclass_weight_key UNIQUE (weight);


--
-- TOC entry 2401 (class 2606 OID 126305)
-- Dependencies: 1704 1704
-- Name: nas_trafficnode_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY nas_trafficnode
    ADD CONSTRAINT nas_trafficnode_pkey PRIMARY KEY (id);


--
-- TOC entry 2405 (class 2606 OID 126307)
-- Dependencies: 1705 1705
-- Name: radius_activesession_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY radius_activesession
    ADD CONSTRAINT radius_activesession_pkey PRIMARY KEY (id);


--
-- TOC entry 2408 (class 2606 OID 126309)
-- Dependencies: 1706 1706
-- Name: radius_session_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY radius_session
    ADD CONSTRAINT radius_session_pkey PRIMARY KEY (id);


--
-- TOC entry 2212 (class 1259 OID 126310)
-- Dependencies: 1655
-- Name: auth_message_user_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX auth_message_user_id ON auth_message USING btree (user_id);


--
-- TOC entry 2213 (class 1259 OID 126311)
-- Dependencies: 1656
-- Name: auth_permission_content_type_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX auth_permission_content_type_id ON auth_permission USING btree (content_type_id);


--
-- TOC entry 2230 (class 1259 OID 126312)
-- Dependencies: 1660
-- Name: billservice_accessparameters_access_time_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_accessparameters_access_time_id ON billservice_accessparameters USING btree (access_time_id);


--
-- TOC entry 2233 (class 1259 OID 176258)
-- Dependencies: 1661
-- Name: billservice_account_ipn_ip_address; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_account_ipn_ip_address ON billservice_account USING btree (ipn_ip_address);


--
-- TOC entry 2234 (class 1259 OID 126313)
-- Dependencies: 1661
-- Name: billservice_account_nas_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_account_nas_id ON billservice_account USING btree (nas_id);


--
-- TOC entry 2239 (class 1259 OID 176257)
-- Dependencies: 1661
-- Name: billservice_account_vpn_ip_address; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_account_vpn_ip_address ON billservice_account USING btree (vpn_ip_address);


--
-- TOC entry 2240 (class 1259 OID 126314)
-- Dependencies: 1662
-- Name: billservice_accountipnspeed_account_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_accountipnspeed_account_id ON billservice_accountipnspeed USING btree (account_id);


--
-- TOC entry 2243 (class 1259 OID 126315)
-- Dependencies: 1663
-- Name: billservice_accountprepaystime_account_tarif_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_accountprepaystime_account_tarif_id ON billservice_accountprepaystime USING btree (account_tarif_id);


--
-- TOC entry 2246 (class 1259 OID 126316)
-- Dependencies: 1663
-- Name: billservice_accountprepaystime_prepaid_time_service_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_accountprepaystime_prepaid_time_service_id ON billservice_accountprepaystime USING btree (prepaid_time_service_id);


--
-- TOC entry 2247 (class 1259 OID 126317)
-- Dependencies: 1664
-- Name: billservice_accountprepaystrafic_account_tarif_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_accountprepaystrafic_account_tarif_id ON billservice_accountprepaystrafic USING btree (account_tarif_id);


--
-- TOC entry 2250 (class 1259 OID 126318)
-- Dependencies: 1664
-- Name: billservice_accountprepaystrafic_prepaid_traffic_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_accountprepaystrafic_prepaid_traffic_id ON billservice_accountprepaystrafic USING btree (prepaid_traffic_id);


--
-- TOC entry 2251 (class 1259 OID 126319)
-- Dependencies: 1665
-- Name: billservice_accounttarif_account_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_accounttarif_account_id ON billservice_accounttarif USING btree (account_id);


--
-- TOC entry 2254 (class 1259 OID 126320)
-- Dependencies: 1665
-- Name: billservice_accounttarif_tarif_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_accounttarif_tarif_id ON billservice_accounttarif USING btree (tarif_id);


--
-- TOC entry 2255 (class 1259 OID 126321)
-- Dependencies: 1666
-- Name: billservice_card_activated_by_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_card_activated_by_id ON billservice_card USING btree (activated_by_id);


--
-- TOC entry 2256 (class 1259 OID 126322)
-- Dependencies: 1666
-- Name: billservice_card_card_group_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_card_card_group_id ON billservice_card USING btree (card_group_id);


--
-- TOC entry 2263 (class 1259 OID 126323)
-- Dependencies: 1668
-- Name: billservice_netflowstream_account_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_netflowstream_account_id ON billservice_netflowstream USING btree (account_id);


--
-- TOC entry 2264 (class 1259 OID 126324)
-- Dependencies: 1668
-- Name: billservice_netflowstream_nas_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_netflowstream_nas_id ON billservice_netflowstream USING btree (nas_id);


--
-- TOC entry 2267 (class 1259 OID 126325)
-- Dependencies: 1668
-- Name: billservice_netflowstream_tarif_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_netflowstream_tarif_id ON billservice_netflowstream USING btree (tarif_id);


--
-- TOC entry 2268 (class 1259 OID 126326)
-- Dependencies: 1668
-- Name: billservice_netflowstream_traffic_class_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_netflowstream_traffic_class_id ON billservice_netflowstream USING btree (traffic_class_id);


--
-- TOC entry 2269 (class 1259 OID 126327)
-- Dependencies: 1668
-- Name: billservice_netflowstream_traffic_transmit_node_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_netflowstream_traffic_transmit_node_id ON billservice_netflowstream USING btree (traffic_transmit_node_id);


--
-- TOC entry 2272 (class 1259 OID 126328)
-- Dependencies: 1670
-- Name: billservice_onetimeservicehistory_accounttarif_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_onetimeservicehistory_accounttarif_id ON billservice_onetimeservicehistory USING btree (accounttarif_id);


--
-- TOC entry 2273 (class 1259 OID 126329)
-- Dependencies: 1670
-- Name: billservice_onetimeservicehistory_onetimeservice_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_onetimeservicehistory_onetimeservice_id ON billservice_onetimeservicehistory USING btree (onetimeservice_id);


--
-- TOC entry 2278 (class 1259 OID 126330)
-- Dependencies: 1671
-- Name: billservice_periodicalservice_settlement_period_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_periodicalservice_settlement_period_id ON billservice_periodicalservice USING btree (settlement_period_id);


--
-- TOC entry 2281 (class 1259 OID 126331)
-- Dependencies: 1672
-- Name: billservice_periodicalservicehistory_service_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_periodicalservicehistory_service_id ON billservice_periodicalservicehistory USING btree (service_id);


--
-- TOC entry 2282 (class 1259 OID 126332)
-- Dependencies: 1672
-- Name: billservice_periodicalservicehistory_transaction_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_periodicalservicehistory_transaction_id ON billservice_periodicalservicehistory USING btree (transaction_id);


--
-- TOC entry 2287 (class 1259 OID 126333)
-- Dependencies: 1674
-- Name: billservice_prepaidtraffic_traffic_transmit_service_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_prepaidtraffic_traffic_transmit_service_id ON billservice_prepaidtraffic USING btree (traffic_transmit_service_id);


--
-- TOC entry 2292 (class 1259 OID 126334)
-- Dependencies: 1676
-- Name: billservice_rawnetflowstream_nas_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_rawnetflowstream_nas_id ON billservice_rawnetflowstream USING btree (nas_id);


--
-- TOC entry 2295 (class 1259 OID 126335)
-- Dependencies: 1676
-- Name: billservice_rawnetflowstream_traffic_class_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_rawnetflowstream_traffic_class_id ON billservice_rawnetflowstream USING btree (traffic_class_id);


--
-- TOC entry 2308 (class 1259 OID 126336)
-- Dependencies: 1680
-- Name: billservice_tariff_access_parameters_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_tariff_access_parameters_id ON billservice_tariff USING btree (access_parameters_id);


--
-- TOC entry 2313 (class 1259 OID 126337)
-- Dependencies: 1680
-- Name: billservice_tariff_settlement_period_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_tariff_settlement_period_id ON billservice_tariff USING btree (settlement_period_id);


--
-- TOC entry 2314 (class 1259 OID 126338)
-- Dependencies: 1680
-- Name: billservice_tariff_time_access_service_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_tariff_time_access_service_id ON billservice_tariff USING btree (time_access_service_id);


--
-- TOC entry 2315 (class 1259 OID 126339)
-- Dependencies: 1680
-- Name: billservice_tariff_traffic_transmit_service_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_tariff_traffic_transmit_service_id ON billservice_tariff USING btree (traffic_transmit_service_id);


--
-- TOC entry 2330 (class 1259 OID 126340)
-- Dependencies: 1684
-- Name: billservice_timeaccessnode_time_access_service_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_timeaccessnode_time_access_service_id ON billservice_timeaccessnode USING btree (time_access_service_id);


--
-- TOC entry 2331 (class 1259 OID 126341)
-- Dependencies: 1684
-- Name: billservice_timeaccessnode_time_period_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_timeaccessnode_time_period_id ON billservice_timeaccessnode USING btree (time_period_id);


--
-- TOC entry 2344 (class 1259 OID 126342)
-- Dependencies: 1689
-- Name: billservice_timespeed_access_parameters_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_timespeed_access_parameters_id ON billservice_timespeed USING btree (access_parameters_id);


--
-- TOC entry 2347 (class 1259 OID 126343)
-- Dependencies: 1689
-- Name: billservice_timespeed_time_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_timespeed_time_id ON billservice_timespeed USING btree (time_id);


--
-- TOC entry 2350 (class 1259 OID 126344)
-- Dependencies: 1690
-- Name: billservice_trafficlimit_settlement_period_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_trafficlimit_settlement_period_id ON billservice_trafficlimit USING btree (settlement_period_id);


--
-- TOC entry 2357 (class 1259 OID 126345)
-- Dependencies: 1692
-- Name: billservice_traffictransmitnodes_traffic_transmit_service_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_traffictransmitnodes_traffic_transmit_service_id ON billservice_traffictransmitnodes USING btree (traffic_transmit_service_id);


--
-- TOC entry 2368 (class 1259 OID 126346)
-- Dependencies: 1696
-- Name: billservice_transaction_account_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_transaction_account_id ON billservice_transaction USING btree (account_id);


--
-- TOC entry 2371 (class 1259 OID 126347)
-- Dependencies: 1696
-- Name: billservice_transaction_tarif_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX billservice_transaction_tarif_id ON billservice_transaction USING btree (tarif_id);


--
-- TOC entry 2378 (class 1259 OID 126348)
-- Dependencies: 1698
-- Name: django_admin_log_content_type_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX django_admin_log_content_type_id ON django_admin_log USING btree (content_type_id);


--
-- TOC entry 2381 (class 1259 OID 126349)
-- Dependencies: 1698
-- Name: django_admin_log_user_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX django_admin_log_user_id ON django_admin_log USING btree (user_id);


--
-- TOC entry 2402 (class 1259 OID 126350)
-- Dependencies: 1704
-- Name: nas_trafficnode_traffic_class_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX nas_trafficnode_traffic_class_id ON nas_trafficnode USING btree (traffic_class_id);


--
-- TOC entry 2403 (class 1259 OID 126351)
-- Dependencies: 1705
-- Name: radius_activesession_account_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX radius_activesession_account_id ON radius_activesession USING btree (account_id);


--
-- TOC entry 2406 (class 1259 OID 126352)
-- Dependencies: 1706
-- Name: radius_session_account_id; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE INDEX radius_session_account_id ON radius_session USING btree (account_id);


--
-- TOC entry 1837 (class 2618 OID 126353)
-- Dependencies: 1680 1680 1680 26
-- Name: on_tariff_delete_rule; Type: RULE; Schema: public; Owner: -
--

CREATE RULE on_tariff_delete_rule AS ON DELETE TO billservice_tariff DO SELECT on_tariff_delete_fun(old.*) AS on_tariff_delete_fun;


--
-- TOC entry 2473 (class 2606 OID 126354)
-- Dependencies: 2235 1661 1705
-- Name: account_id_refs_id_16c70393; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY radius_activesession
    ADD CONSTRAINT account_id_refs_id_16c70393 FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2474 (class 2606 OID 126359)
-- Dependencies: 1706 2235 1661
-- Name: account_id_refs_id_600b3363; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY radius_session
    ADD CONSTRAINT account_id_refs_id_600b3363 FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2420 (class 2606 OID 126364)
-- Dependencies: 2252 1663 1665
-- Name: account_tarif_id_refs_id_48fe22d0; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_accountprepaystime
    ADD CONSTRAINT account_tarif_id_refs_id_48fe22d0 FOREIGN KEY (account_tarif_id) REFERENCES billservice_accounttarif(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2422 (class 2606 OID 126369)
-- Dependencies: 2252 1665 1664
-- Name: account_tarif_id_refs_id_7d07606a; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_accountprepaystrafic
    ADD CONSTRAINT account_tarif_id_refs_id_7d07606a FOREIGN KEY (account_tarif_id) REFERENCES billservice_accounttarif(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2409 (class 2606 OID 126374)
-- Dependencies: 2204 1653 1654
-- Name: auth_group_permissions_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_fkey FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2410 (class 2606 OID 126379)
-- Dependencies: 2216 1654 1656
-- Name: auth_group_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2411 (class 2606 OID 126384)
-- Dependencies: 2218 1655 1657
-- Name: auth_message_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_message
    ADD CONSTRAINT auth_message_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2413 (class 2606 OID 126389)
-- Dependencies: 1658 1653 2204
-- Name: auth_user_groups_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_fkey FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2414 (class 2606 OID 126394)
-- Dependencies: 1658 2218 1657
-- Name: auth_user_groups_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2415 (class 2606 OID 126399)
-- Dependencies: 1656 2216 1659
-- Name: auth_user_user_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2416 (class 2606 OID 126404)
-- Dependencies: 1659 1657 2218
-- Name: auth_user_user_permissions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2417 (class 2606 OID 126409)
-- Dependencies: 1660 2336 1686
-- Name: billservice_accessparameters_access_time_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_accessparameters
    ADD CONSTRAINT billservice_accessparameters_access_time_id_fkey FOREIGN KEY (access_time_id) REFERENCES billservice_timeperiod(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2418 (class 2606 OID 126414)
-- Dependencies: 1702 1661 2392
-- Name: billservice_account_nas_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_account
    ADD CONSTRAINT billservice_account_nas_id_fkey FOREIGN KEY (nas_id) REFERENCES nas_nas(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2419 (class 2606 OID 126419)
-- Dependencies: 1661 2235 1662
-- Name: billservice_accountipnspeed_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_accountipnspeed
    ADD CONSTRAINT billservice_accountipnspeed_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2421 (class 2606 OID 126424)
-- Dependencies: 2332 1685 1663
-- Name: billservice_accountprepaystime_prepaid_time_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_accountprepaystime
    ADD CONSTRAINT billservice_accountprepaystime_prepaid_time_service_id_fkey FOREIGN KEY (prepaid_time_service_id) REFERENCES billservice_timeaccessservice(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2423 (class 2606 OID 126429)
-- Dependencies: 2285 1674 1664
-- Name: billservice_accountprepaystrafic_prepaid_traffic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_accountprepaystrafic
    ADD CONSTRAINT billservice_accountprepaystrafic_prepaid_traffic_id_fkey FOREIGN KEY (prepaid_traffic_id) REFERENCES billservice_prepaidtraffic(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2424 (class 2606 OID 126434)
-- Dependencies: 1661 2235 1665
-- Name: billservice_accounttarif_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_accounttarif
    ADD CONSTRAINT billservice_accounttarif_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2425 (class 2606 OID 126439)
-- Dependencies: 1680 1665 2311
-- Name: billservice_accounttarif_tarif_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_accounttarif
    ADD CONSTRAINT billservice_accounttarif_tarif_id_fkey FOREIGN KEY (tarif_id) REFERENCES billservice_tariff(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2426 (class 2606 OID 126444)
-- Dependencies: 1666 2235 1661
-- Name: billservice_card_activated_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_card
    ADD CONSTRAINT billservice_card_activated_by_id_fkey FOREIGN KEY (activated_by_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2427 (class 2606 OID 126449)
-- Dependencies: 2261 1666 1667
-- Name: billservice_card_card_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_card
    ADD CONSTRAINT billservice_card_card_group_id_fkey FOREIGN KEY (card_group_id) REFERENCES billservice_cardgroup(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2428 (class 2606 OID 126454)
-- Dependencies: 2235 1668 1661
-- Name: billservice_netflowstream_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_netflowstream
    ADD CONSTRAINT billservice_netflowstream_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2429 (class 2606 OID 126459)
-- Dependencies: 1668 1702 2392
-- Name: billservice_netflowstream_nas_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_netflowstream
    ADD CONSTRAINT billservice_netflowstream_nas_id_fkey FOREIGN KEY (nas_id) REFERENCES nas_nas(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2430 (class 2606 OID 126464)
-- Dependencies: 1668 2311 1680
-- Name: billservice_netflowstream_tarif_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_netflowstream
    ADD CONSTRAINT billservice_netflowstream_tarif_id_fkey FOREIGN KEY (tarif_id) REFERENCES billservice_tariff(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2431 (class 2606 OID 126469)
-- Dependencies: 2396 1668 1703
-- Name: billservice_netflowstream_traffic_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_netflowstream
    ADD CONSTRAINT billservice_netflowstream_traffic_class_id_fkey FOREIGN KEY (traffic_class_id) REFERENCES nas_trafficclass(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2432 (class 2606 OID 126474)
-- Dependencies: 2355 1668 1692
-- Name: billservice_netflowstream_traffic_transmit_node_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_netflowstream
    ADD CONSTRAINT billservice_netflowstream_traffic_transmit_node_id_fkey FOREIGN KEY (traffic_transmit_node_id) REFERENCES billservice_traffictransmitnodes(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2433 (class 2606 OID 126479)
-- Dependencies: 1665 1670 2252
-- Name: billservice_onetimeservicehistory_accounttarif_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_onetimeservicehistory
    ADD CONSTRAINT billservice_onetimeservicehistory_accounttarif_id_fkey FOREIGN KEY (accounttarif_id) REFERENCES billservice_accounttarif(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2434 (class 2606 OID 126484)
-- Dependencies: 2270 1669 1670
-- Name: billservice_onetimeservicehistory_onetimeservice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_onetimeservicehistory
    ADD CONSTRAINT billservice_onetimeservicehistory_onetimeservice_id_fkey FOREIGN KEY (onetimeservice_id) REFERENCES billservice_onetimeservice(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2435 (class 2606 OID 126489)
-- Dependencies: 1677 2298 1671
-- Name: billservice_periodicalservice_settlement_period_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_periodicalservice
    ADD CONSTRAINT billservice_periodicalservice_settlement_period_id_fkey FOREIGN KEY (settlement_period_id) REFERENCES billservice_settlementperiod(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2436 (class 2606 OID 126494)
-- Dependencies: 2276 1672 1671
-- Name: billservice_periodicalservicehistory_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_periodicalservicehistory
    ADD CONSTRAINT billservice_periodicalservicehistory_service_id_fkey FOREIGN KEY (service_id) REFERENCES billservice_periodicalservice(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2438 (class 2606 OID 126499)
-- Dependencies: 1674 2285 1675
-- Name: billservice_prepaidtraffic_traffic_class_prepaidtraffic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_prepaidtraffic_traffic_class
    ADD CONSTRAINT billservice_prepaidtraffic_traffic_class_prepaidtraffic_id_fkey FOREIGN KEY (prepaidtraffic_id) REFERENCES billservice_prepaidtraffic(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2439 (class 2606 OID 126504)
-- Dependencies: 2396 1675 1703
-- Name: billservice_prepaidtraffic_traffic_class_trafficclass_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_prepaidtraffic_traffic_class
    ADD CONSTRAINT billservice_prepaidtraffic_traffic_class_trafficclass_id_fkey FOREIGN KEY (trafficclass_id) REFERENCES nas_trafficclass(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2442 (class 2606 OID 168421)
-- Dependencies: 2235 1676 1661
-- Name: billservice_rawnetflowstream_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_rawnetflowstream
    ADD CONSTRAINT billservice_rawnetflowstream_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2440 (class 2606 OID 126509)
-- Dependencies: 1702 1676 2392
-- Name: billservice_rawnetflowstream_nas_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_rawnetflowstream
    ADD CONSTRAINT billservice_rawnetflowstream_nas_id_fkey FOREIGN KEY (nas_id) REFERENCES nas_nas(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2441 (class 2606 OID 126514)
-- Dependencies: 1703 1676 2396
-- Name: billservice_rawnetflowstream_traffic_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_rawnetflowstream
    ADD CONSTRAINT billservice_rawnetflowstream_traffic_class_id_fkey FOREIGN KEY (traffic_class_id) REFERENCES nas_trafficclass(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2443 (class 2606 OID 126519)
-- Dependencies: 1678 2235 1661
-- Name: billservice_shedulelog_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_shedulelog
    ADD CONSTRAINT billservice_shedulelog_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2444 (class 2606 OID 126524)
-- Dependencies: 1680 1660 2231
-- Name: billservice_tariff_access_parameters_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_tariff
    ADD CONSTRAINT billservice_tariff_access_parameters_id_fkey FOREIGN KEY (access_parameters_id) REFERENCES billservice_accessparameters(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2448 (class 2606 OID 126529)
-- Dependencies: 2270 1669 1681
-- Name: billservice_tariff_onetime_services_onetimeservice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_tariff_onetime_services
    ADD CONSTRAINT billservice_tariff_onetime_services_onetimeservice_id_fkey FOREIGN KEY (onetimeservice_id) REFERENCES billservice_onetimeservice(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2449 (class 2606 OID 126534)
-- Dependencies: 2311 1680 1681
-- Name: billservice_tariff_onetime_services_tariff_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_tariff_onetime_services
    ADD CONSTRAINT billservice_tariff_onetime_services_tariff_id_fkey FOREIGN KEY (tariff_id) REFERENCES billservice_tariff(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2450 (class 2606 OID 126539)
-- Dependencies: 1671 1682 2276
-- Name: billservice_tariff_periodical_service_periodicalservice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_tariff_periodical_services
    ADD CONSTRAINT billservice_tariff_periodical_service_periodicalservice_id_fkey FOREIGN KEY (periodicalservice_id) REFERENCES billservice_periodicalservice(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2451 (class 2606 OID 126544)
-- Dependencies: 1682 1680 2311
-- Name: billservice_tariff_periodical_services_tariff_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_tariff_periodical_services
    ADD CONSTRAINT billservice_tariff_periodical_services_tariff_id_fkey FOREIGN KEY (tariff_id) REFERENCES billservice_tariff(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2445 (class 2606 OID 126549)
-- Dependencies: 2298 1677 1680
-- Name: billservice_tariff_settlement_period_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_tariff
    ADD CONSTRAINT billservice_tariff_settlement_period_id_fkey FOREIGN KEY (settlement_period_id) REFERENCES billservice_settlementperiod(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2446 (class 2606 OID 126554)
-- Dependencies: 1680 1685 2332
-- Name: billservice_tariff_time_access_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_tariff
    ADD CONSTRAINT billservice_tariff_time_access_service_id_fkey FOREIGN KEY (time_access_service_id) REFERENCES billservice_timeaccessservice(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2452 (class 2606 OID 126559)
-- Dependencies: 2311 1680 1683
-- Name: billservice_tariff_traffic_limit_tariff_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_tariff_traffic_limit
    ADD CONSTRAINT billservice_tariff_traffic_limit_tariff_id_fkey FOREIGN KEY (tariff_id) REFERENCES billservice_tariff(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2453 (class 2606 OID 126564)
-- Dependencies: 1690 1683 2348
-- Name: billservice_tariff_traffic_limit_trafficlimit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_tariff_traffic_limit
    ADD CONSTRAINT billservice_tariff_traffic_limit_trafficlimit_id_fkey FOREIGN KEY (trafficlimit_id) REFERENCES billservice_trafficlimit(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2447 (class 2606 OID 126569)
-- Dependencies: 2366 1695 1680
-- Name: billservice_tariff_traffic_transmit_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_tariff
    ADD CONSTRAINT billservice_tariff_traffic_transmit_service_id_fkey FOREIGN KEY (traffic_transmit_service_id) REFERENCES billservice_traffictransmitservice(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2454 (class 2606 OID 126574)
-- Dependencies: 1684 1685 2332
-- Name: billservice_timeaccessnode_time_access_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_timeaccessnode
    ADD CONSTRAINT billservice_timeaccessnode_time_access_service_id_fkey FOREIGN KEY (time_access_service_id) REFERENCES billservice_timeaccessservice(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2455 (class 2606 OID 126579)
-- Dependencies: 1686 2336 1684
-- Name: billservice_timeaccessnode_time_period_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_timeaccessnode
    ADD CONSTRAINT billservice_timeaccessnode_time_period_id_fkey FOREIGN KEY (time_period_id) REFERENCES billservice_timeperiod(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2456 (class 2606 OID 126584)
-- Dependencies: 1687 1686 2336
-- Name: billservice_timeperiod_time_period_nodes_timeperiod_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_timeperiod_time_period_nodes
    ADD CONSTRAINT billservice_timeperiod_time_period_nodes_timeperiod_id_fkey FOREIGN KEY (timeperiod_id) REFERENCES billservice_timeperiod(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2457 (class 2606 OID 126589)
-- Dependencies: 2342 1687 1688
-- Name: billservice_timeperiod_time_period_nodes_timeperiodnode_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_timeperiod_time_period_nodes
    ADD CONSTRAINT billservice_timeperiod_time_period_nodes_timeperiodnode_id_fkey FOREIGN KEY (timeperiodnode_id) REFERENCES billservice_timeperiodnode(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2458 (class 2606 OID 126594)
-- Dependencies: 1660 1689 2231
-- Name: billservice_timespeed_access_parameters_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_timespeed
    ADD CONSTRAINT billservice_timespeed_access_parameters_id_fkey FOREIGN KEY (access_parameters_id) REFERENCES billservice_accessparameters(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2459 (class 2606 OID 126599)
-- Dependencies: 1686 1689 2336
-- Name: billservice_timespeed_time_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_timespeed
    ADD CONSTRAINT billservice_timespeed_time_id_fkey FOREIGN KEY (time_id) REFERENCES billservice_timeperiod(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2460 (class 2606 OID 126604)
-- Dependencies: 1677 1690 2298
-- Name: billservice_trafficlimit_settlement_period_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_trafficlimit
    ADD CONSTRAINT billservice_trafficlimit_settlement_period_id_fkey FOREIGN KEY (settlement_period_id) REFERENCES billservice_settlementperiod(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2461 (class 2606 OID 126609)
-- Dependencies: 1703 1691 2396
-- Name: billservice_trafficlimit_traffic_class_trafficclass_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_trafficlimit_traffic_class
    ADD CONSTRAINT billservice_trafficlimit_traffic_class_trafficclass_id_fkey FOREIGN KEY (trafficclass_id) REFERENCES nas_trafficclass(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2462 (class 2606 OID 126614)
-- Dependencies: 1690 2348 1691
-- Name: billservice_trafficlimit_traffic_class_trafficlimit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_trafficlimit_traffic_class
    ADD CONSTRAINT billservice_trafficlimit_traffic_class_trafficlimit_id_fkey FOREIGN KEY (trafficlimit_id) REFERENCES billservice_trafficlimit(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2463 (class 2606 OID 126619)
-- Dependencies: 1692 2366 1695
-- Name: billservice_traffictransmitnod_traffic_transmit_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_traffictransmitnodes
    ADD CONSTRAINT billservice_traffictransmitnod_traffic_transmit_service_id_fkey FOREIGN KEY (traffic_transmit_service_id) REFERENCES billservice_traffictransmitservice(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2464 (class 2606 OID 126624)
-- Dependencies: 1692 2355 1693
-- Name: billservice_traffictransmitnodes__traffictransmitnodes_id_fkey1; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_traffictransmitnodes_time_nodes
    ADD CONSTRAINT billservice_traffictransmitnodes__traffictransmitnodes_id_fkey1 FOREIGN KEY (traffictransmitnodes_id) REFERENCES billservice_traffictransmitnodes(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2466 (class 2606 OID 126629)
-- Dependencies: 1694 2355 1692
-- Name: billservice_traffictransmitnodes_t_traffictransmitnodes_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_traffictransmitnodes_traffic_class
    ADD CONSTRAINT billservice_traffictransmitnodes_t_traffictransmitnodes_id_fkey FOREIGN KEY (traffictransmitnodes_id) REFERENCES billservice_traffictransmitnodes(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2465 (class 2606 OID 126634)
-- Dependencies: 1686 2336 1693
-- Name: billservice_traffictransmitnodes_time_nodes_timeperiod_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_traffictransmitnodes_time_nodes
    ADD CONSTRAINT billservice_traffictransmitnodes_time_nodes_timeperiod_id_fkey FOREIGN KEY (timeperiod_id) REFERENCES billservice_timeperiod(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2467 (class 2606 OID 126639)
-- Dependencies: 2396 1703 1694
-- Name: billservice_traffictransmitnodes_traffic_c_trafficclass_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_traffictransmitnodes_traffic_class
    ADD CONSTRAINT billservice_traffictransmitnodes_traffic_c_trafficclass_id_fkey FOREIGN KEY (trafficclass_id) REFERENCES nas_trafficclass(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2468 (class 2606 OID 126644)
-- Dependencies: 1661 2235 1696
-- Name: billservice_transaction_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_transaction
    ADD CONSTRAINT billservice_transaction_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2469 (class 2606 OID 126649)
-- Dependencies: 1680 2311 1696
-- Name: billservice_transaction_tarif_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_transaction
    ADD CONSTRAINT billservice_transaction_tarif_id_fkey FOREIGN KEY (tarif_id) REFERENCES billservice_tariff(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2412 (class 2606 OID 126654)
-- Dependencies: 2384 1699 1656
-- Name: content_type_id_refs_id_728de91f; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT content_type_id_refs_id_728de91f FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2470 (class 2606 OID 126659)
-- Dependencies: 2384 1698 1699
-- Name: django_admin_log_content_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_fkey FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2471 (class 2606 OID 126664)
-- Dependencies: 1698 1657 2218
-- Name: django_admin_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2472 (class 2606 OID 126669)
-- Dependencies: 1704 2396 1703
-- Name: nas_trafficnode_traffic_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY nas_trafficnode
    ADD CONSTRAINT nas_trafficnode_traffic_class_id_fkey FOREIGN KEY (traffic_class_id) REFERENCES nas_trafficclass(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2437 (class 2606 OID 126674)
-- Dependencies: 1674 1695 2366
-- Name: traffic_transmit_service_id_refs_id_4797c3b9; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY billservice_prepaidtraffic
    ADD CONSTRAINT traffic_transmit_service_id_refs_id_4797c3b9 FOREIGN KEY (traffic_transmit_service_id) REFERENCES billservice_traffictransmitservice(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2479 (class 0 OID 0)
-- Dependencies: 6
-- Name: public; Type: ACL; Schema: -; Owner: -
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2008-09-24 22:32:02

--
-- PostgreSQL database dump complete
--

