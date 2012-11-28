--
-- PostgreSQL database dump
--

-- Started on 2009-08-29 17:57:19

SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

--
-- TOC entry 728 (class 2612 OID 4630615)
-- Name: plpgsql; Type: PROCEDURAL LANGUAGE; Schema: -; Owner: ebs
--

CREATE PROCEDURAL LANGUAGE plpgsql;


ALTER PROCEDURAL LANGUAGE plpgsql OWNER TO ebs;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 1942 (class 1259 OID 4630735)
-- Dependencies: 6
-- Name: auth_group; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE auth_group (
    id integer NOT NULL,
    name character varying(80) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO ebs;

--
-- TOC entry 1944 (class 1259 OID 4630740)
-- Dependencies: 6
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO ebs;

--
-- TOC entry 1946 (class 1259 OID 4630745)
-- Dependencies: 6
-- Name: auth_message; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE auth_message (
    id integer NOT NULL,
    user_id integer NOT NULL,
    message text NOT NULL
);


ALTER TABLE public.auth_message OWNER TO ebs;

--
-- TOC entry 1948 (class 1259 OID 4630753)
-- Dependencies: 6
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE auth_permission (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO ebs;

--
-- TOC entry 1950 (class 1259 OID 4630758)
-- Dependencies: 6
-- Name: auth_user; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
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


ALTER TABLE public.auth_user OWNER TO ebs;

--
-- TOC entry 1951 (class 1259 OID 4630761)
-- Dependencies: 6
-- Name: auth_user_groups; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE auth_user_groups (
    id integer NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE public.auth_user_groups OWNER TO ebs;

--
-- TOC entry 1954 (class 1259 OID 4630768)
-- Dependencies: 6
-- Name: auth_user_user_permissions; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE auth_user_user_permissions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_user_user_permissions OWNER TO ebs;

--
-- TOC entry 1956 (class 1259 OID 4630773)
-- Dependencies: 2387 2388 2389 2390 2391 2392 2393 6
-- Name: billservice_accessparameters; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
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


ALTER TABLE public.billservice_accessparameters OWNER TO ebs;

--
-- TOC entry 1958 (class 1259 OID 4630788)
-- Dependencies: 2395 2396 2397 2398 2399 2400 2401 2402 2403 2404 2405 2406 2407 2408 2409 2410 2411 2412 2413 2414 2415 2416 2417 2418 2419 2420 2421 2422 2423 2424 2425 2426 2427 2428 2429 2430 2431 2432 2434 2435 2436 2437 2438 2439 2440 6
-- Name: billservice_account; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
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
    suspended boolean DEFAULT true,
    created timestamp without time zone DEFAULT now(),
    ballance numeric DEFAULT 0,
    credit numeric DEFAULT 0,
    disabled_by_limit boolean DEFAULT false,
    balance_blocked boolean DEFAULT false,
    ipn_speed character varying(96) DEFAULT ''::character varying,
    vpn_speed character varying(96) DEFAULT ''::character varying,
    netmask inet DEFAULT '0.0.0.0/0'::inet,
    ipn_added boolean DEFAULT false,
    city character varying(255) DEFAULT ''::character varying,
    postcode character varying(255) DEFAULT ''::character varying,
    region character varying(255) DEFAULT ''::character varying,
    street character varying(255) DEFAULT ''::character varying,
    house character varying(255) DEFAULT ''::character varying,
    house_bulk character varying(255) DEFAULT ''::character varying,
    entrance character varying(255) DEFAULT ''::character varying,
    room character varying(255) DEFAULT ''::character varying,
    vlan integer,
    allow_webcab boolean DEFAULT true,
    allow_expresscards boolean DEFAULT true,
    assign_dhcp_null boolean DEFAULT true,
    assign_dhcp_block boolean DEFAULT true,
    allow_vpn_null boolean DEFAULT true,
    allow_vpn_block boolean DEFAULT true,
    passport character varying(255) DEFAULT ''::character varying,
    passport_given character varying(255) DEFAULT ''::character varying,
    phone_h character varying DEFAULT ''::character varying,
    phone_m character varying DEFAULT ''::character varying,
    vpn_ipinuse_id integer,
    ipn_ipinuse_id integer,
    associate_pptp_ipn_ip boolean DEFAULT false NOT NULL,
    associate_pppoe_mac boolean DEFAULT false NOT NULL,
    contactperson_phone character varying DEFAULT ''::character varying,
    comment character varying,
    "row" character varying DEFAULT ''::character varying,
    elevator_direction character varying DEFAULT ''::character varying,
    status integer DEFAULT 1,
    contactperson character varying DEFAULT ''::character varying,
    passport_date character varying DEFAULT ''::character varying
);


ALTER TABLE public.billservice_account OWNER TO ebs;

--
-- TOC entry 2085 (class 1259 OID 4632768)
-- Dependencies: 2605 2606 6
-- Name: billservice_accountaddonservice; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_accountaddonservice (
    id integer NOT NULL,
    service_id integer NOT NULL,
    account_id integer NOT NULL,
    activated timestamp without time zone NOT NULL,
    deactivated timestamp without time zone,
    action_status boolean DEFAULT false,
    speed_status boolean DEFAULT false,
    temporary_blocked timestamp without time zone,
    last_checkout timestamp without time zone
);


ALTER TABLE public.billservice_accountaddonservice OWNER TO ebs;

--
-- TOC entry 1960 (class 1259 OID 4630834)
-- Dependencies: 2441 2442 2443 2444 6
-- Name: billservice_accountipnspeed; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_accountipnspeed (
    id integer NOT NULL,
    account_id integer NOT NULL,
    speed character varying(32) DEFAULT ''::character varying,
    state boolean DEFAULT false,
    static boolean DEFAULT false,
    datetime timestamp without time zone DEFAULT now()
);


ALTER TABLE public.billservice_accountipnspeed OWNER TO ebs;

--
-- TOC entry 1962 (class 1259 OID 4630843)
-- Dependencies: 2446 2447 6
-- Name: billservice_accountprepaystime; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_accountprepaystime (
    id integer NOT NULL,
    account_tarif_id integer NOT NULL,
    prepaid_time_service_id integer NOT NULL,
    size integer DEFAULT 0,
    datetime timestamp without time zone DEFAULT now()
);


ALTER TABLE public.billservice_accountprepaystime OWNER TO ebs;

--
-- TOC entry 1964 (class 1259 OID 4630850)
-- Dependencies: 2449 2451 6
-- Name: billservice_accountprepaystrafic; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_accountprepaystrafic (
    id integer NOT NULL,
    account_tarif_id integer NOT NULL,
    prepaid_traffic_id integer NOT NULL,
    size bigint DEFAULT 0,
    datetime timestamp without time zone DEFAULT now()
);


ALTER TABLE public.billservice_accountprepaystrafic OWNER TO ebs;

--
-- TOC entry 1966 (class 1259 OID 4630857)
-- Dependencies: 6
-- Name: billservice_accountspeedlimit; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_accountspeedlimit (
    id integer NOT NULL,
    account_id integer NOT NULL,
    speedlimit_id integer NOT NULL
);


ALTER TABLE public.billservice_accountspeedlimit OWNER TO ebs;

--
-- TOC entry 1968 (class 1259 OID 4630862)
-- Dependencies: 2454 6
-- Name: billservice_accounttarif; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_accounttarif (
    id integer NOT NULL,
    account_id integer NOT NULL,
    tarif_id integer NOT NULL,
    datetime timestamp without time zone,
    periodical_billed boolean DEFAULT false
);


ALTER TABLE public.billservice_accounttarif OWNER TO ebs;

--
-- TOC entry 2081 (class 1259 OID 4632694)
-- Dependencies: 2579 2580 2581 2582 2583 2584 2585 2586 2587 2588 2589 2590 2591 2592 2593 2594 2595 2596 2597 2598 2599 2600 2601 6
-- Name: billservice_addonservice; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_addonservice (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    allow_activation boolean DEFAULT false,
    service_type character varying(32) NOT NULL,
    sp_type character varying(32) DEFAULT ''::character varying,
    sp_period_id integer NOT NULL,
    timeperiod_id integer NOT NULL,
    cost numeric DEFAULT 0,
    cancel_subscription boolean DEFAULT false,
    wyte_period_id integer,
    wyte_cost numeric,
    action boolean DEFAULT false,
    nas_id integer,
    service_activation_action character varying(8000) DEFAULT ''::character varying,
    service_deactivation_action character varying(8000) DEFAULT ''::character varying,
    deactivate_service_for_blocked_account boolean DEFAULT false,
    change_speed boolean DEFAULT false,
    change_speed_type character varying(32) DEFAULT 'abs'::character varying,
    speed_units character varying(32) DEFAULT 'Kbps'::character varying,
    max_tx integer DEFAULT 0,
    max_rx integer DEFAULT 0,
    burst_tx integer DEFAULT 0,
    burst_rx integer DEFAULT 0,
    burst_treshold_tx integer DEFAULT 0,
    burst_treshold_rx integer DEFAULT 0,
    burst_time_tx integer DEFAULT 0,
    burst_time_rx integer DEFAULT 0,
    min_tx integer DEFAULT 0,
    min_rx integer DEFAULT 0,
    priority integer DEFAULT 8,
    comment character varying DEFAULT ''::character varying
);


ALTER TABLE public.billservice_addonservice OWNER TO ebs;

--
-- TOC entry 2083 (class 1259 OID 4632741)
-- Dependencies: 2603 6
-- Name: billservice_addonservicetarif; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_addonservicetarif (
    id integer NOT NULL,
    tarif_id integer NOT NULL,
    service_id integer NOT NULL,
    activation_count integer DEFAULT 0,
    activation_count_period_id integer
);


ALTER TABLE public.billservice_addonservicetarif OWNER TO ebs;

--
-- TOC entry 2087 (class 1259 OID 4632791)
-- Dependencies: 6
-- Name: billservice_addonservicetransaction; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_addonservicetransaction (
    id integer NOT NULL,
    service_id integer NOT NULL,
    service_type character varying(32) NOT NULL,
    account_id integer NOT NULL,
    accountaddonservice_id integer NOT NULL,
    accounttarif_id integer NOT NULL,
    summ numeric NOT NULL,
    created timestamp without time zone NOT NULL,
    type_id character varying(255) NOT NULL
);


ALTER TABLE public.billservice_addonservicetransaction OWNER TO ebs;

--
-- TOC entry 1970 (class 1259 OID 4630867)
-- Dependencies: 2456 2457 2458 2459 6
-- Name: billservice_bankdata; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_bankdata (
    id integer NOT NULL,
    bank character varying(255) DEFAULT ''::character varying,
    bankcode character varying(40) DEFAULT ''::character varying,
    rs character varying(60) DEFAULT ''::character varying,
    currency character varying(40) DEFAULT ''::character varying
);


ALTER TABLE public.billservice_bankdata OWNER TO ebs;

--
-- TOC entry 1972 (class 1259 OID 4630872)
-- Dependencies: 2460 2461 2462 2464 6
-- Name: billservice_card; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_card (
    id integer NOT NULL,
    series integer NOT NULL,
    pin character varying(255) DEFAULT ''::character varying NOT NULL,
    sold timestamp without time zone,
    nominal numeric DEFAULT 0,
    activated timestamp without time zone,
    activated_by_id integer,
    start_date timestamp without time zone,
    end_date timestamp without time zone,
    disabled boolean DEFAULT false,
    created timestamp without time zone,
    template_id integer,
    account_id integer,
    tarif_id integer,
    nas_id integer,
    login character varying DEFAULT ''::character varying,
    ip character varying,
    ipinuse_id integer
);


ALTER TABLE public.billservice_card OWNER TO ebs;

--
-- TOC entry 1974 (class 1259 OID 4630884)
-- Dependencies: 2465 2466 6
-- Name: billservice_dealer; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_dealer (
    id integer NOT NULL,
    organization character varying(400) NOT NULL,
    unp character varying(255) NOT NULL,
    okpo character varying(255) NOT NULL,
    contactperson character varying(255) NOT NULL,
    director character varying(255) NOT NULL,
    phone character varying(255) NOT NULL,
    fax character varying(255) NOT NULL,
    postaddress character varying(400) NOT NULL,
    uraddress character varying(400) NOT NULL,
    email character varying(255) NOT NULL,
    bank_id integer NOT NULL,
    prepayment numeric,
    paydeffer integer,
    discount numeric,
    always_sell_cards boolean DEFAULT false NOT NULL,
    deleted boolean DEFAULT false
);


ALTER TABLE public.billservice_dealer OWNER TO ebs;

--
-- TOC entry 1976 (class 1259 OID 4630894)
-- Dependencies: 6
-- Name: billservice_dealerpay; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_dealerpay (
    id integer NOT NULL,
    dealer_id integer NOT NULL,
    pay numeric NOT NULL,
    salecard_id integer,
    created timestamp with time zone NOT NULL
);


ALTER TABLE public.billservice_dealerpay OWNER TO ebs;

--
-- TOC entry 1978 (class 1259 OID 4630899)
-- Dependencies: 6
-- Name: billservice_document; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_document (
    id integer NOT NULL,
    account_id integer,
    type_id integer NOT NULL,
    body text NOT NULL
);


ALTER TABLE public.billservice_document OWNER TO ebs;

--
-- TOC entry 1980 (class 1259 OID 4630907)
-- Dependencies: 6
-- Name: billservice_documenttype; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_documenttype (
    id integer NOT NULL,
    name character varying(255) NOT NULL
);


ALTER TABLE public.billservice_documenttype OWNER TO ebs;

--
-- TOC entry 1982 (class 1259 OID 4630912)
-- Dependencies: 2471 2472 6
-- Name: billservice_globalstat; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_globalstat (
    id integer NOT NULL,
    account_id integer NOT NULL,
    bytes_in bigint DEFAULT 0 NOT NULL,
    bytes_out bigint DEFAULT 0 NOT NULL,
    datetime timestamp without time zone NOT NULL,
    nas_id integer NOT NULL,
    classes integer[],
    classbytes bigint[]
);


ALTER TABLE public.billservice_globalstat OWNER TO ebs;

--
-- TOC entry 1984 (class 1259 OID 4630922)
-- Dependencies: 6
-- Name: billservice_group; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_group (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    direction integer NOT NULL,
    type integer NOT NULL
);


ALTER TABLE public.billservice_group OWNER TO ebs;

--
-- TOC entry 1986 (class 1259 OID 4630927)
-- Dependencies: 6
-- Name: billservice_group_trafficclass; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_group_trafficclass (
    id integer NOT NULL,
    group_id integer NOT NULL,
    trafficclass_id integer NOT NULL
);


ALTER TABLE public.billservice_group_trafficclass OWNER TO ebs;

--
-- TOC entry 1937 (class 1259 OID 4630644)
-- Dependencies: 6
-- Name: billservice_groupstat; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_groupstat (
    id integer NOT NULL,
    group_id integer NOT NULL,
    account_id integer NOT NULL,
    bytes bigint NOT NULL,
    datetime timestamp without time zone NOT NULL,
    classes integer[],
    classbytes bigint[],
    max_class integer
);


ALTER TABLE public.billservice_groupstat OWNER TO ebs;

--
-- TOC entry 1989 (class 1259 OID 4630934)
-- Dependencies: 6
-- Name: billservice_ipinuse; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_ipinuse (
    id integer NOT NULL,
    pool_id integer NOT NULL,
    ip character varying(255) NOT NULL,
    datetime timestamp with time zone NOT NULL
);


ALTER TABLE public.billservice_ipinuse OWNER TO ebs;

--
-- TOC entry 1991 (class 1259 OID 4630939)
-- Dependencies: 6
-- Name: billservice_ippool; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_ippool (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    type integer NOT NULL,
    start_ip inet NOT NULL,
    end_ip inet NOT NULL
);


ALTER TABLE public.billservice_ippool OWNER TO ebs;

--
-- TOC entry 1938 (class 1259 OID 4630663)
-- Dependencies: 2355 2356 2357 6
-- Name: billservice_netflowstream; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_netflowstream (
    id integer NOT NULL,
    nas_id integer,
    account_id integer NOT NULL,
    tarif_id integer NOT NULL,
    date_start timestamp without time zone DEFAULT now(),
    src_addr inet NOT NULL,
    traffic_class_id integer[],
    direction character varying(32) NOT NULL,
    traffic_transmit_node_id integer,
    dst_addr inet NOT NULL,
    octets bigint NOT NULL,
    src_port integer NOT NULL,
    dst_port integer NOT NULL,
    protocol integer NOT NULL,
    checkouted boolean DEFAULT false,
    for_checkout boolean DEFAULT false
);


ALTER TABLE public.billservice_netflowstream OWNER TO ebs;

--
-- TOC entry 1994 (class 1259 OID 4630949)
-- Dependencies: 6
-- Name: billservice_onetimeservice; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_onetimeservice (
    id integer NOT NULL,
    tarif_id integer NOT NULL,
    name character varying(255) NOT NULL,
    cost numeric NOT NULL
);


ALTER TABLE public.billservice_onetimeservice OWNER TO ebs;

--
-- TOC entry 1996 (class 1259 OID 4630954)
-- Dependencies: 6
-- Name: billservice_onetimeservicehistory; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_onetimeservicehistory (
    id integer NOT NULL,
    accounttarif_id integer NOT NULL,
    onetimeservice_id integer,
    datetime timestamp without time zone NOT NULL,
    transaction_id integer,
    summ numeric,
    account_id integer
);


ALTER TABLE public.billservice_onetimeservicehistory OWNER TO ebs;

--
-- TOC entry 1998 (class 1259 OID 4630959)
-- Dependencies: 6
-- Name: billservice_operator; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_operator (
    id integer NOT NULL,
    organization character varying(255) NOT NULL,
    unp character varying(40) NOT NULL,
    okpo character varying(40) NOT NULL,
    contactperson character varying(255) NOT NULL,
    director character varying(255) NOT NULL,
    phone character varying(40) NOT NULL,
    postaddress character varying(255) NOT NULL,
    uraddress character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    fax character varying(40) NOT NULL,
    bank_id integer
);


ALTER TABLE public.billservice_operator OWNER TO ebs;

--
-- TOC entry 2000 (class 1259 OID 4630967)
-- Dependencies: 2481 2482 2483 2484 2485 2486 6
-- Name: billservice_organization; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_organization (
    id integer NOT NULL,
    account_id integer NOT NULL,
    name character varying(255) DEFAULT ''::character varying,
    uraddress character varying(255) DEFAULT ''::character varying,
    okpo character varying(255) DEFAULT ''::character varying,
    unp character varying(255) DEFAULT ''::character varying,
    bank_id integer NOT NULL,
    phone character varying(255) DEFAULT ''::character varying,
    fax character varying(255) DEFAULT ''::character varying
);


ALTER TABLE public.billservice_organization OWNER TO ebs;

--
-- TOC entry 2002 (class 1259 OID 4630981)
-- Dependencies: 2488 6
-- Name: billservice_periodicalservice; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_periodicalservice (
    id integer NOT NULL,
    tarif_id integer NOT NULL,
    name character varying(255) NOT NULL,
    settlement_period_id integer NOT NULL,
    cost numeric NOT NULL,
    cash_method character varying(255) NOT NULL,
    condition integer DEFAULT 0 NOT NULL,
    created timestamp without time zone
);


ALTER TABLE public.billservice_periodicalservice OWNER TO ebs;

--
-- TOC entry 1940 (class 1259 OID 4630696)
-- Dependencies: 2368 6
-- Name: billservice_periodicalservicehistory; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_periodicalservicehistory (
    id integer NOT NULL,
    service_id integer,
    transaction_id integer,
    datetime timestamp without time zone DEFAULT now(),
    accounttarif_id integer,
    summ numeric,
    account_id integer,
    type_id character varying
);


ALTER TABLE public.billservice_periodicalservicehistory OWNER TO ebs;

--
-- TOC entry 2005 (class 1259 OID 4630992)
-- Dependencies: 2490 2491 6
-- Name: billservice_ports; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_ports (
    id integer NOT NULL,
    port integer NOT NULL,
    protocol integer NOT NULL,
    name character varying(64) DEFAULT ''::character varying,
    description character varying(255) DEFAULT ''::character varying
);


ALTER TABLE public.billservice_ports OWNER TO ebs;

--
-- TOC entry 2007 (class 1259 OID 4630999)
-- Dependencies: 2494 6
-- Name: billservice_prepaidtraffic; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_prepaidtraffic (
    id integer NOT NULL,
    traffic_transmit_service_id integer NOT NULL,
    size bigint DEFAULT 0,
    group_id integer NOT NULL
);


ALTER TABLE public.billservice_prepaidtraffic OWNER TO ebs;

--
-- TOC entry 2077 (class 1259 OID 4632564)
-- Dependencies: 2576 6
-- Name: billservice_radiusattrs; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_radiusattrs (
    id integer NOT NULL,
    tarif_id integer NOT NULL,
    vendor integer DEFAULT 0,
    attrid integer NOT NULL,
    value character varying(255) NOT NULL
);


ALTER TABLE public.billservice_radiusattrs OWNER TO ebs;

--
-- TOC entry 2009 (class 1259 OID 4631005)
-- Dependencies: 6
-- Name: billservice_salecard; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_salecard (
    id integer NOT NULL,
    dealer_id integer NOT NULL,
    sum_for_pay numeric NOT NULL,
    paydeffer integer NOT NULL,
    discount numeric NOT NULL,
    discount_sum numeric NOT NULL,
    prepayment numeric NOT NULL,
    created timestamp with time zone NOT NULL
);


ALTER TABLE public.billservice_salecard OWNER TO ebs;

--
-- TOC entry 2010 (class 1259 OID 4631008)
-- Dependencies: 6
-- Name: billservice_salecard_cards; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_salecard_cards (
    id integer NOT NULL,
    salecard_id integer NOT NULL,
    card_id integer NOT NULL
);


ALTER TABLE public.billservice_salecard_cards OWNER TO ebs;

--
-- TOC entry 2013 (class 1259 OID 4631015)
-- Dependencies: 2497 2498 6
-- Name: billservice_settlementperiod; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_settlementperiod (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    time_start timestamp without time zone NOT NULL,
    length integer NOT NULL,
    length_in character varying(255) DEFAULT ''::character varying,
    autostart boolean DEFAULT false
);


ALTER TABLE public.billservice_settlementperiod OWNER TO ebs;

--
-- TOC entry 2015 (class 1259 OID 4631025)
-- Dependencies: 6
-- Name: billservice_shedulelog; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE billservice_shedulelog (
    id integer NOT NULL,
    account_id integer NOT NULL,
    ballance_checkout timestamp without time zone,
    prepaid_traffic_reset timestamp without time zone,
    prepaid_traffic_accrued timestamp without time zone,
    prepaid_time_reset timestamp without time zone,
    prepaid_time_accrued timestamp without time zone,
    balance_blocked timestamp without time zone,
    accounttarif_id integer
);


ALTER TABLE public.billservice_shedulelog OWNER TO postgres;

--
-- TOC entry 2017 (class 1259 OID 4631030)
-- Dependencies: 2502 2503 6
-- Name: billservice_speedlimit; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_speedlimit (
    id integer NOT NULL,
    limit_id integer NOT NULL,
    max_tx integer NOT NULL,
    max_rx integer NOT NULL,
    burst_tx integer NOT NULL,
    burst_rx integer NOT NULL,
    burst_treshold_tx integer NOT NULL,
    burst_treshold_rx integer NOT NULL,
    burst_time_tx integer NOT NULL,
    burst_time_rx integer NOT NULL,
    min_tx integer NOT NULL,
    min_rx integer NOT NULL,
    priority integer NOT NULL,
    speed_units character varying(10) DEFAULT 'Kbps'::character varying NOT NULL,
    change_speed_type character varying(20) DEFAULT 'add'::character varying
);


ALTER TABLE public.billservice_speedlimit OWNER TO ebs;

--
-- TOC entry 2019 (class 1259 OID 4631035)
-- Dependencies: 6
-- Name: billservice_suspendedperiod; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_suspendedperiod (
    id integer NOT NULL,
    account_id integer NOT NULL,
    start_date timestamp without time zone NOT NULL,
    end_date timestamp without time zone
);


ALTER TABLE public.billservice_suspendedperiod OWNER TO ebs;

--
-- TOC entry 2021 (class 1259 OID 4631040)
-- Dependencies: 2505 2506 2507 2508 6
-- Name: billservice_systemuser; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
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
    host character varying(255) DEFAULT '0.0.0.0/0'::character varying,
    role integer
);


ALTER TABLE public.billservice_systemuser OWNER TO ebs;

--
-- TOC entry 1939 (class 1259 OID 4630677)
-- Dependencies: 2359 2360 2361 2362 2363 2364 2366 2367 6
-- Name: billservice_tariff; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_tariff (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text DEFAULT ''::text,
    access_parameters_id integer NOT NULL,
    time_access_service_id integer,
    traffic_transmit_service_id integer,
    cost numeric DEFAULT 0,
    reset_tarif_cost boolean DEFAULT false,
    settlement_period_id integer,
    ps_null_ballance_checkout boolean DEFAULT false,
    active boolean DEFAULT false,
    deleted boolean DEFAULT false,
    allow_express_pay boolean DEFAULT true,
    require_tarif_cost boolean DEFAULT false
);


ALTER TABLE public.billservice_tariff OWNER TO ebs;

--
-- TOC entry 2024 (class 1259 OID 4631054)
-- Dependencies: 6
-- Name: billservice_template; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_template (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    type_id integer NOT NULL,
    body text NOT NULL
);


ALTER TABLE public.billservice_template OWNER TO ebs;

--
-- TOC entry 2026 (class 1259 OID 4631062)
-- Dependencies: 2512 6
-- Name: billservice_timeaccessnode; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_timeaccessnode (
    id integer NOT NULL,
    time_access_service_id integer NOT NULL,
    time_period_id integer NOT NULL,
    cost numeric DEFAULT 0
);


ALTER TABLE public.billservice_timeaccessnode OWNER TO ebs;

--
-- TOC entry 2028 (class 1259 OID 4631068)
-- Dependencies: 2513 2514 6
-- Name: billservice_timeaccessservice; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_timeaccessservice (
    id integer NOT NULL,
    prepaid_time integer DEFAULT 0,
    reset_time boolean DEFAULT false
);


ALTER TABLE public.billservice_timeaccessservice OWNER TO ebs;

--
-- TOC entry 2030 (class 1259 OID 4631075)
-- Dependencies: 6
-- Name: billservice_timeperiod; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_timeperiod (
    id integer NOT NULL,
    name character varying(255) NOT NULL
);


ALTER TABLE public.billservice_timeperiod OWNER TO ebs;

--
-- TOC entry 2032 (class 1259 OID 4631080)
-- Dependencies: 6
-- Name: billservice_timeperiod_time_period_nodes; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_timeperiod_time_period_nodes (
    id integer NOT NULL,
    timeperiod_id integer NOT NULL,
    timeperiodnode_id integer NOT NULL
);


ALTER TABLE public.billservice_timeperiod_time_period_nodes OWNER TO ebs;

--
-- TOC entry 2034 (class 1259 OID 4631085)
-- Dependencies: 2518 2519 6
-- Name: billservice_timeperiodnode; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_timeperiodnode (
    id integer NOT NULL,
    name character varying(255) DEFAULT ''::character varying,
    time_start timestamp without time zone NOT NULL,
    length integer NOT NULL,
    repeat_after character varying(255) DEFAULT ''::character varying
);


ALTER TABLE public.billservice_timeperiodnode OWNER TO ebs;

--
-- TOC entry 2036 (class 1259 OID 4631095)
-- Dependencies: 2521 2522 2523 2524 2525 2526 6
-- Name: billservice_timespeed; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
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


ALTER TABLE public.billservice_timespeed OWNER TO ebs;

--
-- TOC entry 2073 (class 1259 OID 4632062)
-- Dependencies: 6
-- Name: billservice_timetransaction; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_timetransaction (
    id integer NOT NULL,
    timeaccessservice_id integer NOT NULL,
    account_id integer,
    accounttarif_id integer NOT NULL,
    summ numeric NOT NULL,
    datetime timestamp without time zone NOT NULL
);


ALTER TABLE public.billservice_timetransaction OWNER TO ebs;

--
-- TOC entry 2075 (class 1259 OID 4632150)
-- Dependencies: 2574 6
-- Name: billservice_tpchangerule; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_tpchangerule (
    id integer NOT NULL,
    from_tariff_id integer NOT NULL,
    to_tariff_id integer NOT NULL,
    disabled boolean NOT NULL,
    cost numeric NOT NULL,
    ballance_min double precision NOT NULL,
    settlement_period_id integer DEFAULT 0
);


ALTER TABLE public.billservice_tpchangerule OWNER TO ebs;

--
-- TOC entry 2038 (class 1259 OID 4631106)
-- Dependencies: 6
-- Name: billservice_trafficlimit; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_trafficlimit (
    id integer NOT NULL,
    tarif_id integer NOT NULL,
    name character varying(255) NOT NULL,
    settlement_period_id integer,
    size bigint NOT NULL,
    mode boolean NOT NULL,
    group_id integer NOT NULL,
    action integer
);


ALTER TABLE public.billservice_trafficlimit OWNER TO ebs;

--
-- TOC entry 2040 (class 1259 OID 4631111)
-- Dependencies: 6
-- Name: billservice_trafficlimit_traffic_class; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_trafficlimit_traffic_class (
    id integer NOT NULL,
    trafficlimit_id integer NOT NULL,
    trafficclass_id integer NOT NULL
);


ALTER TABLE public.billservice_trafficlimit_traffic_class OWNER TO ebs;

--
-- TOC entry 2071 (class 1259 OID 4632039)
-- Dependencies: 6
-- Name: billservice_traffictransaction; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_traffictransaction (
    id integer NOT NULL,
    traffictransmitservice_id integer,
    account_id integer,
    accounttarif_id integer NOT NULL,
    summ numeric NOT NULL,
    datetime timestamp without time zone NOT NULL
);


ALTER TABLE public.billservice_traffictransaction OWNER TO ebs;

--
-- TOC entry 2042 (class 1259 OID 4631116)
-- Dependencies: 2530 2531 2533 6
-- Name: billservice_traffictransmitnodes; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_traffictransmitnodes (
    id integer NOT NULL,
    traffic_transmit_service_id integer NOT NULL,
    cost numeric DEFAULT 0,
    edge_start double precision DEFAULT 0,
    edge_end double precision DEFAULT 0,
    group_id integer
);


ALTER TABLE public.billservice_traffictransmitnodes OWNER TO ebs;

--
-- TOC entry 2044 (class 1259 OID 4631124)
-- Dependencies: 6
-- Name: billservice_traffictransmitnodes_time_nodes; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_traffictransmitnodes_time_nodes (
    id integer NOT NULL,
    traffictransmitnodes_id integer NOT NULL,
    timeperiod_id integer NOT NULL
);


ALTER TABLE public.billservice_traffictransmitnodes_time_nodes OWNER TO ebs;

--
-- TOC entry 2046 (class 1259 OID 4631129)
-- Dependencies: 6
-- Name: billservice_traffictransmitnodes_traffic_class; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_traffictransmitnodes_traffic_class (
    id integer NOT NULL,
    traffictransmitnodes_id integer NOT NULL,
    trafficclass_id integer NOT NULL
);


ALTER TABLE public.billservice_traffictransmitnodes_traffic_class OWNER TO ebs;

--
-- TOC entry 2048 (class 1259 OID 4631134)
-- Dependencies: 2536 2537 2538 6
-- Name: billservice_traffictransmitservice; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_traffictransmitservice (
    id integer NOT NULL,
    reset_traffic boolean DEFAULT false,
    cash_method character varying(32) DEFAULT 'SUMM'::character varying,
    period_check character varying(32) DEFAULT 'SP_START'::character varying
);


ALTER TABLE public.billservice_traffictransmitservice OWNER TO ebs;

--
-- TOC entry 2050 (class 1259 OID 4631142)
-- Dependencies: 2541 2542 6
-- Name: billservice_transaction; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_transaction (
    id integer NOT NULL,
    bill character varying(255),
    account_id integer,
    type_id character varying,
    approved boolean,
    tarif_id integer,
    summ numeric,
    description text,
    created timestamp without time zone,
    systemuser_id integer,
    promise boolean DEFAULT false,
    end_promise timestamp without time zone,
    promise_expired boolean DEFAULT false,
    accounttarif_id integer
);


ALTER TABLE public.billservice_transaction OWNER TO ebs;

--
-- TOC entry 2052 (class 1259 OID 4631150)
-- Dependencies: 6
-- Name: billservice_transactiontype; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_transactiontype (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    internal_name character varying(32) NOT NULL
);


ALTER TABLE public.billservice_transactiontype OWNER TO ebs;

--
-- TOC entry 2079 (class 1259 OID 4632662)
-- Dependencies: 6
-- Name: billservice_x8021; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE billservice_x8021 (
    id integer NOT NULL,
    account_id integer,
    nas_id integer NOT NULL,
    port smallint,
    typeauth character varying(32) NOT NULL,
    vlan_accept integer,
    vlan_reject integer,
    simpleauth boolean NOT NULL
);


ALTER TABLE public.billservice_x8021 OWNER TO ebs;

--
-- TOC entry 2054 (class 1259 OID 4631155)
-- Dependencies: 2545 6
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
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


ALTER TABLE public.django_admin_log OWNER TO ebs;

--
-- TOC entry 2056 (class 1259 OID 4631164)
-- Dependencies: 6
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE django_content_type (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO ebs;

--
-- TOC entry 2058 (class 1259 OID 4631169)
-- Dependencies: 6
-- Name: django_session; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp without time zone NOT NULL
);


ALTER TABLE public.django_session OWNER TO ebs;

--
-- TOC entry 2059 (class 1259 OID 4631175)
-- Dependencies: 6
-- Name: django_site; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE django_site (
    id integer NOT NULL,
    domain character varying(100) NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE public.django_site OWNER TO ebs;



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
    multilink boolean DEFAULT false,
    identify character varying
);


ALTER TABLE public.nas_nas OWNER TO ebs;

--
-- TOC entry 2063 (class 1259 OID 4631198)
-- Dependencies: 2558 2559 2560 6
-- Name: nas_trafficclass; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE nas_trafficclass (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    weight integer NOT NULL,
    color character varying(16) DEFAULT '#FFFFFF'::character varying,
    store boolean DEFAULT true,
    passthrough boolean DEFAULT true
);


ALTER TABLE public.nas_trafficclass OWNER TO ebs;

--
-- TOC entry 2065 (class 1259 OID 4631206)
-- Dependencies: 2562 2563 2564 2565 2566 2567 6
-- Name: nas_trafficnode; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE nas_trafficnode (
    id integer NOT NULL,
    traffic_class_id integer NOT NULL,
    name character varying(255) NOT NULL,
    direction character varying(32) NOT NULL,
    protocol integer DEFAULT 0,
    src_ip inet DEFAULT '0.0.0.0/0'::inet,
    src_port integer DEFAULT 0,
    dst_ip inet DEFAULT '0.0.0.0/0'::inet,
    dst_port integer DEFAULT 0,
    next_hop inet DEFAULT '0.0.0.0'::inet
);


ALTER TABLE public.nas_trafficnode OWNER TO ebs;

--
-- TOC entry 2067 (class 1259 OID 4631222)
-- Dependencies: 2569 6
-- Name: radius_activesession; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE radius_activesession (
    id integer NOT NULL,
    account_id integer NOT NULL,
    sessionid character varying(255),
    interrim_update timestamp without time zone,
    date_start timestamp without time zone,
    date_end timestamp without time zone,
    caller_id character varying(255),
    called_id character varying(255),
    nas_id character varying(255) NOT NULL,
    session_time integer DEFAULT 0,
    framed_protocol character varying(32) NOT NULL,
    bytes_in bigint,
    bytes_out bigint,
    session_status character varying(32),
    speed_string character varying(255),
    framed_ip_address character varying(255),
    nas_int_id integer
);


ALTER TABLE public.radius_activesession OWNER TO ebs;

--
-- TOC entry 1941 (class 1259 OID 4630711)
-- Dependencies: 2370 2371 2372 2373 2374 2375 2376 2377 2378 6
-- Name: radius_session; Type: TABLE; Schema: public; Owner: ebs; Tablespace: 
--

CREATE TABLE radius_session (
    id integer NOT NULL,
    account_id integer NOT NULL,
    sessionid character varying(32) DEFAULT ''::character varying,
    interrim_update timestamp without time zone DEFAULT now(),
    date_start timestamp without time zone,
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
    framed_ip_address character varying(255),
    transaction_id bigint
);


ALTER TABLE public.radius_session OWNER TO ebs;

--
-- TOC entry 96 (class 1255 OID 4630624)
-- Dependencies: 728 6
-- Name: account_transaction_trg_fn(); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION account_transaction_trg_fn() RETURNS trigger
    AS $$
BEGIN

IF (TG_OP = 'INSERT') THEN
UPDATE billservice_account SET ballance=ballance-NEW.summ WHERE id=NEW.account_id;
RETURN NEW;
ELSIF (TG_OP = 'DELETE') THEN
UPDATE billservice_account SET ballance=ballance+OLD.summ WHERE id=OLD.account_id;
RETURN OLD;
ELSIF (TG_OP = 'UPDATE') THEN
UPDATE billservice_account SET ballance=ballance+OLD.summ WHERE id=OLD.account_id;
UPDATE billservice_account SET ballance=ballance-NEW.summ WHERE id=NEW.account_id;
RETURN NEW;
END IF;
RETURN NULL;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.account_transaction_trg_fn() OWNER TO ebs;

--
-- TOC entry 163 (class 1255 OID 4632125)
-- Dependencies: 728 6
-- Name: accountipnspeed_ins_fn(integer, character varying, boolean, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION accountipnspeed_ins_fn(account_id_ integer, speed_ character varying, state_ boolean, datetime_ timestamp without time zone) RETURNS void
    AS $$ 
BEGIN
    UPDATE billservice_accountipnspeed SET speed=speed_, state=state_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_accountipnspeed(account_id, speed, state, datetime) VALUES(account_id_, speed_, state_, datetime_);
    END IF;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.accountipnspeed_ins_fn(account_id_ integer, speed_ character varying, state_ boolean, datetime_ timestamp without time zone) OWNER TO postgres;


CREATE FUNCTION block_balance(account_id integer) RETURNS void
    AS $$
BEGIN
    UPDATE billservice_account SET balance_blocked=TRUE WHERE id=account_id;
RETURN;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.block_balance(account_id integer) OWNER TO postgres;

--
-- TOC entry 54 (class 1255 OID 283154)
-- Dependencies: 6 454
-- Name: boolop(integer[], query_int); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION boolop(integer[], query_int) RETURNS boolean
    AS '$libdir/_int', 'boolop'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.boolop(integer[], query_int) OWNER TO ebs;

--
-- TOC entry 3131 (class 0 OID 0)
-- Dependencies: 54
-- Name: FUNCTION boolop(integer[], query_int); Type: COMMENT; Schema: public; Owner: ebs
--

COMMENT ON FUNCTION boolop(integer[], query_int) IS 'boolean operation with array';


--
-- TOC entry 175 (class 1255 OID 4630626)
-- Dependencies: 6 728
-- Name: card_activate_fn(character varying, character varying, integer, inet); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION card_activate_fn(login_ character varying, pin_ character varying, nas_id_ integer, account_ip_ inet) RETURNS record
    AS $$
DECLARE
    tarif_id_ int;
    account_id_ int;
    card_id_ int;
    sold_ timestamp without time zone;
    activated_ timestamp without time zone;
    card_data_ record;
    account_data_ record;
    tmp record;
BEGIN
    -- Получаем финормацию о карточке, которая прдана и у которой не истёк срок годности
    SELECT id, sold, activated, activated_by_id, nominal, tarif_id INTO card_data_ FROM billservice_card WHERE "login"=login_ and pin=pin_ and sold is not Null and now() between start_date and end_date;
    -- Если карты нету - return
    IF card_data_ is NULL THEN
	RETURN tmp;
    -- Если карта уже продана, но ещё не активирвоана
    ELSIF card_data_.activated_by_id IS NULL and card_data_.sold is not NULL THEN
	-- Создаём пользователя
        INSERT INTO billservice_account(username, "password", nas_id, ipn_ip_address, ipn_status, status, created, ipn_added, allow_webcab, allow_expresscards, assign_dhcp_null, assign_dhcp_block, allow_vpn_null, allow_vpn_block)
        VALUES(login_, pin_, nas_id_, account_ip_, False, True, now(), False, True, True, False, False, False, False) RETURNING id INTO account_id_;
      
	-- Добавлеяем пользователю тариф
        INSERT INTO billservice_accounttarif(account_id, tarif_id, datetime) VALUES(account_id_, card_data_.tarif_id, now());
        -- Пополняем счёт
        INSERT INTO billservice_transaction(bill, account_id, type_id, approved, tarif_id, summ, description, created)
        VALUES('Карта доступа', account_id_, 'ACCESS_CARD', True, card_data_.tarif_id, card_data_.nominal*(-1),'', now());
	-- Обновляем информацию о карточке
	UPDATE billservice_card SET activated = now(), activated_by_id = account_id_ WHERE id = card_data_.id;
	
	-- Обновляем информацию о IP-адресе пользователя
	UPDATE billservice_account SET ipn_ip_address = account_ip_ WHERE id = account_id_;
	-- Выбираем нужную информацию
	SELECT account.id, account.password, account.nas_id, bsat.tarif_id,  account.status, 
	account.balance_blocked, (account.ballance+account.credit) as ballance, account.disabled_by_limit, 
	tariff.active INTO account_data_ 
	FROM billservice_account as account
	JOIN billservice_accounttarif as bsat ON bsat.account_id=account.id
	JOIN billservice_tariff as tariff on tariff.id=bsat.tarif_id
	WHERE  account.id=account_id_ AND 
	account.ballance+account.credit>0
	ORDER BY bsat.datetime DESC LIMIT 1;
	RETURN account_data_;
    -- Если карта продана и уже активирована
    ELSIF (card_data_.sold is not Null) AND (card_data_.activated_by_id is not Null) THEN
	SELECT account.id, account.password, account.nas_id, bsat.tarif_id,  account.status, 
	account.balance_blocked, (account.ballance+account.credit) as ballance, account.disabled_by_limit, 
	tariff.active INTO account_data_
	FROM billservice_account as account
	JOIN billservice_accounttarif as bsat ON bsat.account_id=account.id
	JOIN billservice_tariff as tariff on tariff.id=bsat.tarif_id
	WHERE  bsat.datetime<now() and account.id=card_data_.activated_by_id AND 
	account.ballance+account.credit>0
	AND
	((account.balance_blocked=False and account.disabled_by_limit=False and account.status=True))=True 
	ORDER BY bsat.datetime DESC LIMIT 1;
	RETURN account_data_;
    END IF; 

    RETURN tmp;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.card_activate_fn(login_ character varying, pin_ character varying, nas_id_ integer, account_ip_ inet) OWNER TO ebs;

--
-- TOC entry 98 (class 1255 OID 4630627)
-- Dependencies: 6 728
-- Name: check_allowed_users_trg_fn(); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION check_allowed_users_trg_fn() RETURNS trigger
    AS $$
DECLARE counted_num_ bigint;
  allowed_num_ bigint := 0;
BEGIN
  allowed_num_ := return_allowed();
  SELECT count(*) INTO counted_num_ FROM billservice_account;
  IF counted_num_ + 1 > allowed_num_ THEN
  RAISE EXCEPTION 'Amount of users[% + 1] will exceed allowed[%] for the license file!', counted_num_, allowed_num_;
  ELSE
  RETURN NEW;
  END IF;
  END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.check_allowed_users_trg_fn() OWNER TO ebs;

--
-- TOC entry 155 (class 1255 OID 4631997)
-- Dependencies: 728 6
-- Name: clear_tariff_services_trg_fn(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION clear_tariff_services_trg_fn() RETURNS trigger
    AS $$
BEGIN
	
	IF OLD.traffic_transmit_service_id NOTNULL THEN
	    DELETE FROM billservice_traffictransmitservice WHERE id=OLD.traffic_transmit_service_id;
	END IF;
	
	IF OLD.time_access_service_id NOTNULL THEN
	    DELETE FROM billservice_timeaccessservice WHERE id=OLD.time_access_service_id;   
	RETURN OLD;
	END IF;
	
	 IF OLD.access_parameters_id NOTNULL THEN
            DELETE FROM billservice_accessparameters WHERE id=OLD.access_parameters_id;
        END IF;
RETURN OLD;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.clear_tariff_services_trg_fn() OWNER TO postgres;

--
-- TOC entry 168 (class 1255 OID 4632554)
-- Dependencies: 728 6
-- Name: credit_account(integer, numeric); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION credit_account(account_id integer, sum numeric) RETURNS void
    AS $$
BEGIN
	UPDATE billservice_account SET ballance=ballance-sum WHERE id=account_id;
RETURN;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.credit_account(account_id integer, sum numeric) OWNER TO postgres;

--
-- TOC entry 101 (class 1255 OID 4630629)
-- Dependencies: 6 728
-- Name: crt_allowed_checker(bigint); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION crt_allowed_checker(allowed bigint) RETURNS void
    AS $$
DECLARE    
allowed_ text := allowed::text;    
prev_ bigint  := 0;    
fn_tx1_    text := 'CREATE OR REPLACE FUNCTION return_allowed() RETURNS bigint AS ';    
fn_bd_tx1_ text := ' BEGIN RETURN ';    
fn_bd_tx2_ text := '; END;';    
fn_tx2_ text := ' LANGUAGE plpgsql VOLATILE COST 100;';
BEGIN        
prev_ := return_allowed();    
IF prev_ != allowed THEN    	
EXECUTE  fn_tx1_  || quote_literal(fn_bd_tx1_ || allowed_ || fn_bd_tx2_ ) || fn_tx2_;    
END IF;    
RETURN;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.crt_allowed_checker(allowed bigint) OWNER TO ebs;

--
-- TOC entry 169 (class 1255 OID 4632555)
-- Dependencies: 728 6
-- Name: debit_account(integer, numeric); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION debit_account(account_id integer, sum numeric) RETURNS void
    AS $$
BEGIN
	UPDATE billservice_account SET ballance=ballance+sum WHERE id=account_id;
RETURN;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.debit_account(account_id integer, sum numeric) OWNER TO postgres;


-- TOC entry 99 (class 1255 OID 4630631)
-- Dependencies: 6 728
-- Name: del_nfs_trg_fn(); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION del_nfs_trg_fn() RETURNS trigger
    AS $$
    BEGIN
        INSERT INTO billservice_netflowstream (nas_id, account_id, tarif_id, date_start, src_addr, traffic_class_id, 
            direction, traffic_transmit_node_id, dst_addr, octets, src_port, 
            dst_port, protocol, checkouted, for_checkout) VALUES( OLD.nas_id, OLD.account_id, OLD.tarif_id, OLD.date_start, OLD.src_addr, 
            OLD.traffic_class_id, OLD.direction, OLD.traffic_transmit_node_id, OLD.dst_addr, OLD.octets, OLD.src_port, 
            OLD.dst_port, OLD.protocol, OLD.checkouted, OLD.for_checkout);
        RETURN OLD;
    END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.del_nfs_trg_fn() OWNER TO ebs;



CREATE FUNCTION free_unused_account_ip_trg_fn() RETURNS trigger
    AS $$
BEGIN


IF (TG_OP = 'UPDATE') THEN
    IF (NEW.vpn_ipinuse_id is Null and OLD.vpn_ipinuse_id is not Null) THEN
        DELETE FROM billservice_ipinuse WHERE id=OLD.vpn_ipinuse_id;
    END IF;
    
    IF (NEW.ipn_ipinuse_id is Null and OLD.ipn_ipinuse_id is not Null) THEN
        DELETE FROM billservice_ipinuse WHERE id=OLD.ipn_ipinuse_id;
    END IF;
    RETURN NEW;

ELSIF (TG_OP = 'DELETE') THEN
    IF (OLD.ipn_ipinuse_id is not Null) THEN
        DELETE FROM billservice_ipinuse WHERE id=OLD.ipn_ipinuse_id;
    END IF;

    IF (OLD.vpn_ipinuse_id is not Null) THEN
        DELETE FROM billservice_ipinuse WHERE id=OLD.vpn_ipinuse_id;   
    RETURN OLD;
    END IF;
    
END IF;
RETURN OLD;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.free_unused_account_ip_trg_fn() OWNER TO ebs;

--
-- TOC entry 103 (class 1255 OID 4630633)
-- Dependencies: 6 728
-- Name: free_unused_card_ip_trg_fn(); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION free_unused_card_ip_trg_fn() RETURNS trigger
    AS $$
BEGIN


IF (TG_OP = 'DELETE') and (OLD.ipinuse_id is not Null) THEN
DELETE FROM billservice_ipinuse WHERE id=OLD.ipinuse_id;
RETURN OLD;
END IF;
RETURN OLD;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.free_unused_card_ip_trg_fn() OWNER TO ebs;

--
-- TOC entry 104 (class 1255 OID 4630634)
-- Dependencies: 6 728
-- Name: free_unused_ip_trg_fn(); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION free_unused_ip_trg_fn() RETURNS trigger
    AS $$
    BEGIN

        IF    (TG_OP = 'DELETE') THEN
            DELETE FROM billservice_ipinuse WHERE id = OLD.vpn_ipinuse_id;
            DELETE FROM billservice_ipinuse WHERE id = OLD.ipn_ipinuse_id;
            RETURN OLD;

        END IF;
    END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.free_unused_ip_trg_fn() OWNER TO ebs;


--
-- TOC entry 105 (class 1255 OID 4630635)
-- Dependencies: 728 6
-- Name: get_cur_acct(timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION get_cur_acct(dateat timestamp without time zone) RETURNS integer[]
    AS $$
BEGIN
RETURN ARRAY(SELECT max(id) FROM billservice_accounttarif GROUP BY account_id HAVING account_id IN (SELECT id FROM billservice_account) AND MAX(datetime) <= dateAT);
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.get_cur_acct(dateat timestamp without time zone) OWNER TO postgres;

--
-- TOC entry 106 (class 1255 OID 4630636)
-- Dependencies: 6 728
-- Name: get_tarif(integer); Type: FUNCTION; Schema: public; Owner: postgres
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


ALTER FUNCTION public.get_tarif(acc_id integer) OWNER TO postgres;

--
-- TOC entry 107 (class 1255 OID 4630637)
-- Dependencies: 6 728
-- Name: get_tariff_type(integer); Type: FUNCTION; Schema: public; Owner: postgres
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


ALTER FUNCTION public.get_tariff_type(tarif_id integer) OWNER TO postgres;


--
-- TOC entry 108 (class 1255 OID 4630638)
-- Dependencies: 6 728
-- Name: global_stat_fn(integer, bigint, bigint, timestamp without time zone, integer, integer[], bigint[]); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION global_stat_fn(account_id_ integer, bytes_in_ bigint, bytes_out_ bigint, datetime_ timestamp without time zone, nas_id_ integer, classes_ integer[], classbytes_ bigint[]) RETURNS void
    AS $$
DECLARE
    old_classes_ int[];
    old_classbytes_  bigint[][];


    i int;
    ilen int;
    j int;

    nbytes_in  bigint;
    nbytes_out bigint;
    nclass int;
BEGIN
    INSERT INTO billservice_globalstat (account_id, bytes_in, bytes_out, datetime, nas_id, classes, classbytes) VALUES (account_id_, bytes_in_, bytes_out_,datetime_, nas_id_, classes_, classbytes_);
EXCEPTION WHEN unique_violation THEN
    SELECT classes, classbytes INTO old_classes_ ,old_classbytes_ FROM billservice_globalstat WHERE account_id=account_id_ AND datetime=datetime_ FOR UPDATE;
    ilen := icount(classes_);

    FOR i IN 1..ilen LOOP
        nclass := classes_[i];
        nbytes_in  := classbytes_[i][1];
        nbytes_out := classbytes_[i][2];
        j := idx(old_classes_, nclass);
        IF j = 0 THEN
	    old_classes_ := array_append(old_classes_, nclass);
	    old_classbytes_ := array_cat(old_classbytes_, ARRAY[nbytes_in ,nbytes_out]);
	ELSE
	    old_classbytes_[j][1] := old_classbytes_[j][1] + nbytes_in;
	    old_classbytes_[j][2] := old_classbytes_[j][2] + nbytes_out;
	END IF;      
    END LOOP;    
    UPDATE billservice_globalstat SET bytes_in=bytes_in+bytes_in_, bytes_out=bytes_out+bytes_out_, classes=old_classes_, classbytes=old_classbytes_ WHERE account_id=account_id_ AND datetime=datetime_;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.global_stat_fn(account_id_ integer, bytes_in_ bigint, bytes_out_ bigint, datetime_ timestamp without time zone, nas_id_ integer, classes_ integer[], classbytes_ bigint[]) OWNER TO ebs;

--
-- TOC entry 109 (class 1255 OID 4630639)
-- Dependencies: 728 6
-- Name: gpst_crt_cur_ins(date); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION gpst_crt_cur_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION gpst_cur_ins (gpstr billservice_groupstat) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO gpst';
                         
    fn_bd_tx2_ text := '(group_id, account_id, bytes, datetime, classes, classbytes, max_class)
                          VALUES 
                         (gpstr.group_id, gpstr.account_id, gpstr.bytes, gpstr.datetime, gpstr.classes, gpstr.classbytes, gpstr.max_class); RETURN; END;';
                          
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';


    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION gpst_cur_datechk(gpst_date timestamp without time zone) RETURNS integer AS ';

    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    gpst_date < d_s_ THEN RETURN -1; ELSIF gpst_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';



    dt_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION gpst_cur_dt() RETURNS date AS ';
    
    onemonth_ text := '1 month';
    query_ text;
    
    prevdate_ date;
    
BEGIN    


    
        query_ :=  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;

        EXECUTE query_;


        query_ :=  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '+ interval ' || quote_literal(onemonth_) ||  ch_fn_bd_tx3_) || fn_tx2_;

        EXECUTE query_;
        
        prevdate_ := gpst_cur_dt();
        
        PERFORM gpst_crt_prev_ins(prevdate_);
        
        query_ := dt_fn_tx1_ || quote_literal(' BEGIN RETURN  DATE ' || quote_literal(datetx_) || '; END; ') || fn_tx2_;
        
        EXECUTE query_;

        
    RETURN;

END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.gpst_crt_cur_ins(datetx date) OWNER TO ebs;

--
-- TOC entry 110 (class 1255 OID 4630640)
-- Dependencies: 728 6
-- Name: gpst_crt_pdb(date); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION gpst_crt_pdb(datetx date) RETURNS integer
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');
    datetx_e_ text := to_char((datetx + interval '1 month')::date, 'YYYYMM01');

    qt_dtx_ text;
    qt_dtx_e_ text;
    seq_tx1_ text := 'CREATE SEQUENCE gpst#rpdate#_id_seq
                      INCREMENT 1
                      MINVALUE 1
                      MAXVALUE 9223372036854775807
                      START 1
                      CACHE 1;';
    seqname_tx1_ text := 'gpst#rpdate#_id_seq';

    chk_tx1_ text := 'CHECK ( datetime >= DATE #stdtx# AND datetime < DATE #eddtx# )';
    ct_tx1_ text := 'CREATE TABLE gpst#rpdate# (
                     #chk#,
                     CONSTRAINT gpst#rpdate#_id_pkey PRIMARY KEY (id) ) 
                     INHERITS (billservice_groupstat) 
                     WITH (OIDS=FALSE);                     
                     CREATE INDEX gpst#rpdate#_datetime_id ON gpst#rpdate# USING btree (datetime);
                     CREATE INDEX gpst#rpdate#_gr_acc_dt_id ON gpst#rpdate# USING btree (group_id, account_id, datetime);
                     CREATE INDEX gpst#rpdate#_account_id ON gpst#rpdate# USING btree (account_id);
                     CREATE INDEX gpst#rpdate#_group_id ON gpst#rpdate# USING btree (group_id);
                     ';
                     
    at_tx1_ text := 'ALTER TABLE gpst#rpdate# ALTER COLUMN id SET DEFAULT nextval(#qseqname#::regclass);';

    chk_       text;
    seq_query_ text;
    ct_query_  text;
    seqn_      text;
    at_query_  text;


BEGIN    
    seq_query_ := replace(seq_tx1_, '#rpdate#', datetx_);
    EXECUTE seq_query_;
    qt_dtx_    := quote_literal(datetx_);
    qt_dtx_e_  := quote_literal(datetx_e_);
    chk_       := replace(chk_tx1_, '#stdtx#', qt_dtx_ );
    chk_       := replace(chk_, '#eddtx#', qt_dtx_e_ );
    ct_query_  := replace(ct_tx1_, '#rpdate#', datetx_);
    ct_query_  := replace(ct_query_, '#chk#', chk_);
    EXECUTE ct_query_;
    seqn_        := replace(seqname_tx1_, '#rpdate#', datetx_);
    at_query_    := replace(at_tx1_, '#rpdate#', datetx_);
    at_query_    := replace(at_query_, '#qseqname#', quote_literal(seqn_));
    EXECUTE at_query_;
    RETURN 0;

END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.gpst_crt_pdb(datetx date) OWNER TO ebs;

--
-- TOC entry 111 (class 1255 OID 4630641)
-- Dependencies: 728 6
-- Name: gpst_crt_prev_ins(date); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION gpst_crt_prev_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION gpst_prev_ins (gpstr billservice_groupstat) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO gpst';
                         
    fn_bd_tx2_ text := '(group_id, account_id, bytes, datetime, classes, classbytes, max_class)
                          VALUES 
                         (gpstr.group_id, gpstr.account_id, gpstr.bytes, gpstr.datetime, gpstr.classes, gpstr.classbytes, gpstr.max_class); RETURN; END;';
                          
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';


    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION gpst_prev_datechk(gpst_date timestamp without time zone) RETURNS integer AS ';

    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    gpst_date < d_s_ THEN RETURN -1; ELSIF gpst_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';

    ch_fn_tx2_ text := ' LANGUAGE plpgsql VOLATILE COST 100;';

    qts_ text := 'CHK % % %';
    
    onemonth_ text := '1 month';
    query_ text;
    
BEGIN    

        EXECUTE  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;


        query_ :=  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '+ interval ' || quote_literal(onemonth_) ||  ch_fn_bd_tx3_) || fn_tx2_;
        
        EXECUTE query_;
        
    RETURN;

END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.gpst_crt_prev_ins(datetx date) OWNER TO ebs;

--
-- TOC entry 112 (class 1255 OID 4630642)
-- Dependencies: 6 728
-- Name: gpst_cur_datechk(timestamp without time zone); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION gpst_cur_datechk(gpst_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700201'; d_e_ date := (DATE '19700201'+ interval '1 month')::date; BEGIN IF    gpst_date < d_s_ THEN RETURN -1; ELSIF gpst_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;


ALTER FUNCTION public.gpst_cur_datechk(gpst_date timestamp without time zone) OWNER TO ebs;

--
-- TOC entry 113 (class 1255 OID 4630643)
-- Dependencies: 728 6
-- Name: gpst_cur_dt(); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION gpst_cur_dt() RETURNS date
    AS $$ BEGIN RETURN  DATE '19700201'; END; $$
    LANGUAGE plpgsql;


ALTER FUNCTION public.gpst_cur_dt() OWNER TO ebs;

--
-- TOC entry 114 (class 1255 OID 4630650)
-- Dependencies: 728 6 464
-- Name: gpst_cur_ins(billservice_groupstat); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION gpst_cur_ins(gpstr billservice_groupstat) RETURNS void
    AS $$BEGIN 
          RETURN; END;$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.gpst_cur_ins(gpstr billservice_groupstat) OWNER TO ebs;

--
-- TOC entry 115 (class 1255 OID 4630651)
-- Dependencies: 6 728
-- Name: gpst_del_trg_fn(); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION gpst_del_trg_fn() RETURNS trigger
    AS $$
    BEGIN
        INSERT INTO billservice_groupstat (group_id, account_id, bytes, datetime, classes, classbytes, max_class) VALUES( OLD.group_id, OLD.account_id, OLD.bytes, OLD.datetime, OLD.classes, OLD.classbytes, OLD.max_class);
        RETURN OLD;
    END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.gpst_del_trg_fn() OWNER TO ebs;

--
-- TOC entry 116 (class 1255 OID 4630652)
-- Dependencies: 728 6
-- Name: gpst_ins_trg_fn(); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION gpst_ins_trg_fn() RETURNS trigger
    AS $$
DECLARE
    cur_chk int;
    prev_chk int;
BEGIN
    cur_chk := gpst_cur_datechk(NEW.datetime);

    IF cur_chk = 0 THEN
        PERFORM gpst_cur_ins(NEW);
    ELSIF cur_chk = 1 THEN
        BEGIN
            PERFORM gpst_crt_pdb(NEW.datetime::date);
            PERFORM gpst_crt_cur_ins(NEW.datetime::date);
            EXECUTE gpst_cur_ins(NEW);
        EXCEPTION 
          WHEN duplicate_table THEN
             PERFORM gpst_crt_cur_ins(NEW.datetime::date);
             EXECUTE gpst_cur_ins(NEW);
        END;
        
        
    ELSE 
        prev_chk := gpst_prev_datechk(NEW.datetime);
        IF prev_chk = 0 THEN
            PERFORM gpst_prev_ins(NEW);
        ELSE
            BEGIN 
                PERFORM gpst_inserter(NEW);
            EXCEPTION 
              WHEN undefined_table THEN
                PERFORM gpst_crt_pdb(NEW.datetime::date);
                PERFORM gpst_inserter(NEW);
            END;
        END IF;      
    END IF;
    RETURN NULL;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.gpst_ins_trg_fn() OWNER TO ebs;

--
-- TOC entry 117 (class 1255 OID 4630653)
-- Dependencies: 6 728 464
-- Name: gpst_inserter(billservice_groupstat); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION gpst_inserter(gpstr billservice_groupstat) RETURNS void
    AS $$
DECLARE
    datetx_ text := to_char(gpstr.datetime::date, 'YYYYMM01');
    insq_   text;
    ttrn_classes_ text; 
    ttrn_classbytes_ text; 
    ttrn_max_class_ int; 
 
BEGIN
    
    IF gpstr.classes IS NULL THEN
       ttrn_classes_ := '{}';
    ELSE
       ttrn_classes_ := quote_literal(gpstr.classes);
    END IF;
    IF gpstr.classbytes IS NULL THEN
       ttrn_classbytes_ := '{}';
    ELSE
       ttrn_classbytes_ := quote_literal(gpstr.classbytes);
    END IF;    
    IF gpstr.max_class IS NULL THEN
       ttrn_max_class_ := 'NULL';
    ELSE
       ttrn_max_class_ := gpstr.max_class;
    END IF;

    
    insq_ := 'INSERT INTO gpst' || datetx_ || ' (group_id, account_id, bytes, datetime, classes, classbytes, max_class) VALUES (' 
    || gpstr.group_id || ',' || gpstr.account_id || ','  || gpstr.bytes || ',' || quote_literal(gpstr.datetime) || ',' ||ttrn_classes_ || ',' || ttrn_classbytes_ || ',' ||  ttrn_max_class_ || ');';
    EXECUTE insq_;
    RETURN;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.gpst_inserter(gpstr billservice_groupstat) OWNER TO ebs;

--
-- TOC entry 118 (class 1255 OID 4630654)
-- Dependencies: 6 728
-- Name: gpst_prev_datechk(timestamp without time zone); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION gpst_prev_datechk(gpst_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700201'; d_e_ date := (DATE '19700201'+ interval '1 month')::date; BEGIN IF    gpst_date < d_s_ THEN RETURN -1; ELSIF gpst_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;


ALTER FUNCTION public.gpst_prev_datechk(gpst_date timestamp without time zone) OWNER TO ebs;

--
-- TOC entry 119 (class 1255 OID 4630655)
-- Dependencies: 728 6 464
-- Name: gpst_prev_ins(billservice_groupstat); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION gpst_prev_ins(gpstr billservice_groupstat) RETURNS void
    AS $$BEGIN 
          RETURN; END;$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.gpst_prev_ins(gpstr billservice_groupstat) OWNER TO ebs;

--
-- TOC entry 166 (class 1255 OID 4632146)
-- Dependencies: 6 728
-- Name: group_type1_fn(integer, integer, bigint, timestamp without time zone, integer[], bigint[], integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION group_type1_fn(group_id_ integer, account_id_ integer, octets_ bigint, datetime_ timestamp without time zone, classes_ integer[], classbytes_ bigint[], max_class_ integer) RETURNS void
    AS $$
BEGIN    
INSERT INTO billservice_groupstat (group_id, account_id, bytes, datetime, classes, classbytes, max_class) VALUES (group_id_, account_id_, octets_, datetime_, classes_, classbytes_ , max_class_);
EXCEPTION WHEN unique_violation THEN    
UPDATE billservice_groupstat SET bytes=bytes+octets_ WHERE group_id=group_id_ AND account_id=account_id_ AND datetime=datetime_;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.group_type1_fn(group_id_ integer, account_id_ integer, octets_ bigint, datetime_ timestamp without time zone, classes_ integer[], classbytes_ bigint[], max_class_ integer) OWNER TO postgres;

--
-- TOC entry 167 (class 1255 OID 4632147)
-- Dependencies: 6 728
-- Name: group_type2_fn(integer, integer, bigint, timestamp without time zone, integer[], bigint[], integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION group_type2_fn(group_id_ integer, account_id_ integer, octets_ bigint, datetime_ timestamp without time zone, classes_ integer[], classbytes_ bigint[], max_class_ integer) RETURNS void
    AS $$
DECLARE
    old_classes_ int[];
    old_classbytes_  bigint[];


    i int;
    ilen int;
    j int;
    max_ bigint;
    maxclass_ int;
    nbytes bigint;
    nclass int;
    --jlen int;
BEGIN
    INSERT INTO billservice_groupstat (group_id, account_id, bytes, datetime, classes, classbytes, max_class) VALUES (group_id_, account_id_, octets_, datetime_, classes_, classbytes_ , max_class_);
EXCEPTION WHEN unique_violation THEN
    SELECT classes, classbytes INTO old_classes_ ,old_classbytes_ FROM billservice_groupstat WHERE group_id=group_id_ AND account_id=account_id_ AND datetime=datetime_ FOR UPDATE;
    ilen := icount(classes_);
    max_ := 0;
    maxclass_ := NULL;
    --jlen := icount(old_classes_);
    FOR i IN 1..ilen LOOP
        nclass := classes_[i];
        nbytes := classbytes_[i];
        j := idx(old_classes_, nclass);
        IF j = 0 THEN
	    old_classes_ := array_append(old_classes_, nclass);
	    old_classbytes_ := array_append(old_classbytes_, nbytes);
	    IF nbytes > max_ THEN
	        max_ := nbytes;
	        maxclass_ := nclass;
	    END IF;
	ELSE
	    old_classbytes_[j] := old_classbytes_[j] + nbytes;
	    IF old_classbytes_[j] > max_ THEN
	        max_ := old_classbytes_[j];
	        maxclass_ := nclass;
	    END IF;
	END IF;      
    END LOOP;    
    UPDATE billservice_groupstat SET bytes=max_, max_class=maxclass_, classes=old_classes_, classbytes=old_classbytes_ WHERE group_id=group_id_ AND account_id=account_id_ AND datetime=datetime_;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.group_type2_fn(group_id_ integer, account_id_ integer, octets_ bigint, datetime_ timestamp without time zone, classes_ integer[], classbytes_ bigint[], max_class_ integer) OWNER TO postgres;



CREATE FUNCTION nfs_crt_cur_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMMDD');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION nfs_cur_ins (nfsr billservice_netflowstream) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO nfs';
                         
    fn_bd_tx2_ text := '(nas_id, account_id, tarif_id, date_start, src_addr, traffic_class_id, direction, traffic_transmit_node_id, dst_addr, octets, src_port, dst_port, protocol, checkouted, for_checkout)
                          VALUES 
                         (nfsr.nas_id, nfsr.account_id, nfsr.tarif_id, nfsr.date_start, nfsr.src_addr, 
                          nfsr.traffic_class_id, nfsr.direction, nfsr.traffic_transmit_node_id, nfsr.dst_addr, nfsr.octets, nfsr.src_port, 
                          nfsr.dst_port, nfsr.protocol, nfsr.checkouted, nfsr.for_checkout); RETURN; END;';
                          
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';


    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION nfs_cur_datechk(nfs_date timestamp without time zone) RETURNS integer AS ';

    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    nfs_date < d_s_ THEN RETURN -1; ELSIF nfs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';



    dt_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION nfs_cur_dt() RETURNS date AS ';
    
    oneday_ text := '1 day';
    query_ text;
    
    prevdate_ date;
    
BEGIN    


    
        query_ :=  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;

        EXECUTE query_;


        query_ :=  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '+ interval ' || quote_literal(oneday_) ||  ch_fn_bd_tx3_) || fn_tx2_;

        EXECUTE query_;
        
        prevdate_ := nfs_cur_dt();
        
        PERFORM nfs_crt_prev_ins(prevdate_);
        
        query_ := dt_fn_tx1_ || quote_literal(' BEGIN RETURN  DATE ' || quote_literal(datetx_) || '; END; ') || fn_tx2_;
        
        EXECUTE query_;

        
    RETURN;

END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.nfs_crt_cur_ins(datetx date) OWNER TO ebs;

--
-- TOC entry 121 (class 1255 OID 4630659)
-- Dependencies: 6 728
-- Name: nfs_crt_pdb(date); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION nfs_crt_pdb(datetx date) RETURNS integer
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMMDD');
    datetx_e_ text := to_char((datetx + interval '1 day')::date, 'YYYYMMDD');

    qt_dtx_ text;
    qt_dtx_e_ text;
    seq_tx1_ text := 'CREATE SEQUENCE nfs#rpdate#_id_seq
                      INCREMENT 1
                      MINVALUE 1
                      MAXVALUE 9223372036854775807
                      START 1
                      CACHE 1;';
    seqname_tx1_ text := 'nfs#rpdate#_id_seq';

    chk_tx1_ text := 'CHECK ( date_start >= DATE #stdtx# AND date_start < DATE #eddtx# )';
    ct_tx1_ text := 'CREATE TABLE nfs#rpdate# (
                     #chk#,
                     CONSTRAINT nfs#rpdate#_id_pkey PRIMARY KEY (id) ) 
                     INHERITS (billservice_netflowstream) 
                     WITH (OIDS=FALSE);                     
                     CREATE INDEX nfs#rpdate#_date_start_id ON nfs#rpdate# USING btree (date_start);
                     ';
                     
    at_tx1_ text := 'ALTER TABLE nfs#rpdate# ALTER COLUMN id SET DEFAULT nextval(#qseqname#::regclass);';

    chk_       text;
    seq_query_ text;
    ct_query_  text;
    seqn_      text;
    at_query_  text;


BEGIN    
    seq_query_ := replace(seq_tx1_, '#rpdate#', datetx_);
    EXECUTE seq_query_;
    qt_dtx_    := quote_literal(datetx_);
    qt_dtx_e_  := quote_literal(datetx_e_);
    chk_       := replace(chk_tx1_, '#stdtx#', qt_dtx_ );
    chk_       := replace(chk_, '#eddtx#', qt_dtx_e_ );
    ct_query_  := replace(ct_tx1_, '#rpdate#', datetx_);
    ct_query_  := replace(ct_query_, '#chk#', chk_);
    EXECUTE ct_query_;
    seqn_        := replace(seqname_tx1_, '#rpdate#', datetx_);
    at_query_    := replace(at_tx1_, '#rpdate#', datetx_);
    at_query_    := replace(at_query_, '#qseqname#', quote_literal(seqn_));
    EXECUTE at_query_;
    RETURN 0;

END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.nfs_crt_pdb(datetx date) OWNER TO ebs;

--
-- TOC entry 122 (class 1255 OID 4630660)
-- Dependencies: 728 6
-- Name: nfs_crt_prev_ins(date); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION nfs_crt_prev_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMMDD');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION nfs_prev_ins (nfsr billservice_netflowstream) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO nfs';
                         
    fn_bd_tx2_ text := '(nas_id, account_id, tarif_id, date_start, src_addr, traffic_class_id, direction, traffic_transmit_node_id, dst_addr, octets, src_port, dst_port, protocol, checkouted, for_checkout)
                          VALUES 
                         (nfsr.nas_id, nfsr.account_id, nfsr.tarif_id, nfsr.date_start, nfsr.src_addr, 
                          nfsr.traffic_class_id, nfsr.direction, nfsr.traffic_transmit_node_id, nfsr.dst_addr, nfsr.octets, nfsr.src_port, 
                          nfsr.dst_port, nfsr.protocol, nfsr.checkouted, nfsr.for_checkout); RETURN; END;';
                          
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';


    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION nfs_prev_datechk(nfs_date timestamp without time zone) RETURNS integer AS ';

    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    nfs_date < d_s_ THEN RETURN -1; ELSIF nfs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';

    ch_fn_tx2_ text := ' LANGUAGE plpgsql VOLATILE COST 100;';

    qts_ text := 'CHK % % %';   
    
    oneday_ text := interval '1 day';
    query_ text;
   
BEGIN    


        EXECUTE  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;


        
        
        query_ :=  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '+ interval ' || quote_literal(oneday_) ||  ch_fn_bd_tx3_) || fn_tx2_;
        
        EXECUTE query_;
        
    RETURN;

END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.nfs_crt_prev_ins(datetx date) OWNER TO ebs;

--
-- TOC entry 123 (class 1255 OID 4630661)
-- Dependencies: 728 6
-- Name: nfs_cur_datechk(timestamp without time zone); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION nfs_cur_datechk(nfs_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700102'; d_e_ date := (DATE '19700102'+ interval '1 day')::date; BEGIN IF    nfs_date < d_s_ THEN RETURN -1; ELSIF nfs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;


ALTER FUNCTION public.nfs_cur_datechk(nfs_date timestamp without time zone) OWNER TO ebs;

--
-- TOC entry 124 (class 1255 OID 4630662)
-- Dependencies: 728 6
-- Name: nfs_cur_dt(); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION nfs_cur_dt() RETURNS date
    AS $$ BEGIN RETURN  DATE '19700102'; END; $$
    LANGUAGE plpgsql;


ALTER FUNCTION public.nfs_cur_dt() OWNER TO ebs;

--
-- TOC entry 125 (class 1255 OID 4630672)
-- Dependencies: 6 728 466
-- Name: nfs_cur_ins(billservice_netflowstream); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION nfs_cur_ins(nfsr billservice_netflowstream) RETURNS void
    AS $$BEGIN 
       RETURN; END;$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.nfs_cur_ins(nfsr billservice_netflowstream) OWNER TO ebs;

--
-- TOC entry 126 (class 1255 OID 4630673)
-- Dependencies: 728 6
-- Name: nfs_ins_trg_fn(); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION nfs_ins_trg_fn() RETURNS trigger
    AS $$
DECLARE
    cur_chk int;
    prev_chk int;
BEGIN
    cur_chk := nfs_cur_datechk(NEW.date_start);

    IF cur_chk = 0 THEN
        PERFORM nfs_cur_ins(NEW);
    ELSIF cur_chk = 1 THEN
        BEGIN
            PERFORM nfs_crt_pdb(NEW.date_start::date);
            PERFORM nfs_crt_cur_ins(NEW.date_start::date);
            EXECUTE nfs_cur_ins(NEW);
        EXCEPTION 
          WHEN duplicate_table THEN
             PERFORM nfs_crt_cur_ins(NEW.date_start::date);
             EXECUTE nfs_cur_ins(NEW);
        END;
        
        
    ELSE 
        prev_chk := nfs_prev_datechk(NEW.date_start);
        IF prev_chk = 0 THEN
            PERFORM nfs_prev_ins(NEW);
        ELSE
            BEGIN 
                PERFORM nfs_inserter(NEW);
            EXCEPTION 
              WHEN undefined_table THEN
                PERFORM nfs_crt_pdb(NEW.date_start::date);
                PERFORM nfs_inserter(NEW);
            END;
        END IF;      
    END IF;
    RETURN NULL;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.nfs_ins_trg_fn() OWNER TO ebs;

--
-- TOC entry 127 (class 1255 OID 4630674)
-- Dependencies: 728 6 466
-- Name: nfs_inserter(billservice_netflowstream); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION nfs_inserter(nfsr billservice_netflowstream) RETURNS void
    AS $$
DECLARE
    datetx_ text := to_char(nfsr.date_start::date, 'YYYYMMDD');
    insq_   text;

    ttrn_id_ text;

    
BEGIN
    
    IF nfsr.traffic_transmit_node_id IS NULL THEN
       ttrn_id_ := 'NULL';
    ELSE
       ttrn_id_ := nfsr.traffic_transmit_node_id::text;
    END IF;
    insq_ := 'INSERT INTO nfs' || datetx_ || ' (nas_id, account_id, tarif_id, date_start, src_addr, traffic_class_id, direction, traffic_transmit_node_id, dst_addr, octets, src_port, dst_port, protocol, checkouted, for_checkout) VALUES (' 
    || nfsr.nas_id || ',' || nfsr.account_id || ','  || nfsr.tarif_id || ','  || quote_literal(nfsr.date_start) || ','  || quote_literal(nfsr.src_addr) || ','  || quote_literal(nfsr.traffic_class_id) || ','  || quote_literal(nfsr.direction) || ','  || ttrn_id_ || ','  || quote_literal(nfsr.dst_addr) || ','  || nfsr.octets || ','  || nfsr.src_port || ','  || nfsr.dst_port || ','  || nfsr.protocol || ','  || nfsr.checkouted || ','  || nfsr.for_checkout || ');';
    EXECUTE insq_;
    RETURN;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.nfs_inserter(nfsr billservice_netflowstream) OWNER TO ebs;

--
-- TOC entry 128 (class 1255 OID 4630675)
-- Dependencies: 6 728
-- Name: nfs_prev_datechk(timestamp without time zone); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION nfs_prev_datechk(nfs_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700101'; d_e_ date := (DATE '19700101'+ interval '1 day')::date; BEGIN IF    nfs_date < d_s_ THEN RETURN -1; ELSIF nfs_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;


ALTER FUNCTION public.nfs_prev_datechk(nfs_date timestamp without time zone) OWNER TO ebs;

--
-- TOC entry 129 (class 1255 OID 4630676)
-- Dependencies: 728 466 6
-- Name: nfs_prev_ins(billservice_netflowstream); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION nfs_prev_ins(nfsr billservice_netflowstream) RETURNS void
    AS $$BEGIN 
      RETURN; END;$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.nfs_prev_ins(nfsr billservice_netflowstream) OWNER TO ebs;

--
-- TOC entry 130 (class 1255 OID 4630690)
-- Dependencies: 6 469 728
-- Name: on_tariff_delete_fun(billservice_tariff); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION on_tariff_delete_fun(oldrow billservice_tariff) RETURNS record
    AS $$
        BEGIN
        IF oldrow.traffic_transmit_service_id NOTNULL THEN
            UPDATE billservice_tariff SET traffic_transmit_service_id=NULL WHERE id=oldrow.id;
            DELETE FROM billservice_traffictransmitservice WHERE id=oldrow.traffic_transmit_service_id;
        END IF;

        IF oldrow.time_access_service_id NOTNULL THEN
	    UPDATE billservice_tariff SET time_access_service_id=NULL WHERE id=oldrow.id;
            DELETE FROM billservice_timeaccessservice WHERE id=oldrow.time_access_service_id;
        END IF;

        IF oldrow.access_parameters_id NOTNULL THEN
            DELETE FROM billservice_accessparameters WHERE id=oldrow.access_parameters_id;
        END IF;
               RETURN oldrow;               
        END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.on_tariff_delete_fun(oldrow billservice_tariff) OWNER TO ebs;

--
-- TOC entry 170 (class 1255 OID 4632556)
-- Dependencies: 728 6
-- Name: periodicaltr_fn(integer, integer, integer, character varying, numeric, timestamp without time zone, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION periodicaltr_fn(ps_id_ integer, acctf_id_ integer, account_id_ integer, type_id_ character varying, summ_ numeric, created_ timestamp without time zone, ps_condition_type_ integer) RETURNS void
    AS $$
DECLARE
    new_summ_ decimal;
BEGIN
    SELECT INTO new_summ_ summ_*(NOT EXISTS (SELECT id FROM billservice_suspendedperiod WHERE account_id=account_id AND (created_ BETWEEN start_date AND end_date)))::int;
    IF (ps_condition_type_ = 1) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance >= 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    ELSIF (ps_condition_type_ = 2) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance < 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    END IF; 
    INSERT INTO billservice_periodicalservicehistory (service_id, accounttarif_id,account_id, type_id, summ, datetime) VALUES (ps_id_, acctf_id_, account_id_, type_id_, new_summ_, created_);
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.periodicaltr_fn(ps_id_ integer, acctf_id_ integer, account_id_ integer, type_id_ character varying, summ_ numeric, created_ timestamp without time zone, ps_condition_type_ integer) OWNER TO postgres;

--
-- TOC entry 156 (class 1255 OID 4630691)
-- Dependencies: 728 6
-- Name: psh_crt_cur_ins(date); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION psh_crt_cur_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION psh_cur_ins (pshr billservice_periodicalservicehistory) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO psh';
                         
    fn_bd_tx2_ text := '(service_id, account_id, accounttarif_id, type_id, summ, datetime)
                          VALUES 
                         (pshr.service_id, pshr.account_id, pshr.accounttarif_id, pshr.type_id, pshr.summ, pshr.datetime); RETURN; END;';
                          
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';


    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION psh_cur_datechk(psh_date timestamp without time zone) RETURNS integer AS ';

    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    psh_date < d_s_ THEN RETURN -1; ELSIF psh_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';



    dt_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION psh_cur_dt() RETURNS date AS ';
    
    onemonth_ text := '1 month';
    query_ text;
    
    prevdate_ date;
    
BEGIN    


    
        query_ :=  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;

        EXECUTE query_;


        query_ :=  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '+ interval ' || quote_literal(onemonth_) ||  ch_fn_bd_tx3_) || fn_tx2_;

        EXECUTE query_;
        
        prevdate_ := psh_cur_dt();
        
        PERFORM psh_crt_prev_ins(prevdate_);
        
        query_ := dt_fn_tx1_ || quote_literal(' BEGIN RETURN  DATE ' || quote_literal(datetx_) || '; END; ') || fn_tx2_;
        
        EXECUTE query_;

        
    RETURN;

END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.psh_crt_cur_ins(datetx date) OWNER TO ebs;

--
-- TOC entry 177 (class 1255 OID 4630692)
-- Dependencies: 6 728
-- Name: psh_crt_pdb(date); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION psh_crt_pdb(datetx date) RETURNS integer
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');
    datetx_e_ text := to_char((datetx + interval '1 month')::date, 'YYYYMM01');

    qt_dtx_ text;
    qt_dtx_e_ text;
    seq_tx1_ text := 'CREATE SEQUENCE psh#rpdate#_id_seq
                      INCREMENT 1
                      MINVALUE 1
                      MAXVALUE 9223372036854775807
                      START 1
                      CACHE 1;';
    seqname_tx1_ text := 'psh#rpdate#_id_seq';

    chk_tx1_ text := 'CHECK ( datetime >= DATE #stdtx# AND datetime < DATE #eddtx# )';
    ct_tx1_ text := 'CREATE TABLE psh#rpdate# (
                     #chk#,
                     CONSTRAINT psh#rpdate#_id_pkey PRIMARY KEY (id) ) 
                     INHERITS (billservice_periodicalservicehistory) 
                     WITH (OIDS=FALSE);                     
                     CREATE INDEX psh#rpdate#_datetime_id ON psh#rpdate# USING btree (datetime);
                     CREATE INDEX psh#rpdate#_service_id ON psh#rpdate# USING btree (service_id);
                     CREATE INDEX psh#rpdate#_accounttarif_id ON psh#rpdate# USING btree (accounttarif_id);
                     CREATE TRIGGER acc_psh_trg AFTER UPDATE OR DELETE ON psh#rpdate# FOR EACH ROW EXECUTE PROCEDURE account_transaction_trg_fn();
                     ';
                     
    at_tx1_ text := 'ALTER TABLE psh#rpdate# ALTER COLUMN id SET DEFAULT nextval(#qseqname#::regclass);';

    chk_       text;
    seq_query_ text;
    ct_query_  text;
    seqn_      text;
    at_query_  text;


BEGIN    
    seq_query_ := replace(seq_tx1_, '#rpdate#', datetx_);
    EXECUTE seq_query_;
    qt_dtx_    := quote_literal(datetx_);
    qt_dtx_e_  := quote_literal(datetx_e_);
    chk_       := replace(chk_tx1_, '#stdtx#', qt_dtx_ );
    chk_       := replace(chk_, '#eddtx#', qt_dtx_e_ );
    ct_query_  := replace(ct_tx1_, '#rpdate#', datetx_);
    ct_query_  := replace(ct_query_, '#chk#', chk_);
    EXECUTE ct_query_;
    seqn_        := replace(seqname_tx1_, '#rpdate#', datetx_);
    at_query_    := replace(at_tx1_, '#rpdate#', datetx_);
    at_query_    := replace(at_query_, '#qseqname#', quote_literal(seqn_));
    EXECUTE at_query_;
    RETURN 0;

END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.psh_crt_pdb(datetx date) OWNER TO ebs;

--
-- TOC entry 134 (class 1255 OID 4630693)
-- Dependencies: 728 6
-- Name: psh_crt_prev_ins(date); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION psh_crt_prev_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION psh_prev_ins (pshr billservice_periodicalservicehistory) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO psh';
                         
    fn_bd_tx2_ text := '(service_id, account_id, accounttarif_id,type_id, summ, datetime)
                          VALUES 
                         (pshr.service_id, pshr.account_id, pshr.accounttarif_id, pshr.type_id, pshr.summ, pshr.datetime); RETURN; END;';
                          
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';


    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION psh_prev_datechk(psh_date timestamp without time zone) RETURNS integer AS ';

    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    psh_date < d_s_ THEN RETURN -1; ELSIF psh_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';

    ch_fn_tx2_ text := ' LANGUAGE plpgsql VOLATILE COST 100;';

    qts_ text := 'CHK % % %';
    
    onemonth_ text := '1 month';
    query_ text;
BEGIN    

        EXECUTE  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;


        query_ :=  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '+ interval ' || quote_literal(onemonth_) ||  ch_fn_bd_tx3_) || fn_tx2_;
        
        EXECUTE query_;
        
    RETURN;

END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.psh_crt_prev_ins(datetx date) OWNER TO ebs;

--
-- TOC entry 135 (class 1255 OID 4630694)
-- Dependencies: 728 6
-- Name: psh_cur_datechk(timestamp without time zone); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION psh_cur_datechk(psh_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700201'; d_e_ date := (DATE '19700101'+ interval '1 month')::date; BEGIN IF    psh_date < d_s_ THEN RETURN -1; ELSIF psh_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;


ALTER FUNCTION public.psh_cur_datechk(psh_date timestamp without time zone) OWNER TO ebs;

--
-- TOC entry 131 (class 1255 OID 4630695)
-- Dependencies: 728 6
-- Name: psh_cur_dt(); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION psh_cur_dt() RETURNS date
    AS $$ BEGIN RETURN  DATE '19700201'; END; $$
    LANGUAGE plpgsql;


ALTER FUNCTION public.psh_cur_dt() OWNER TO ebs;

--
-- TOC entry 132 (class 1255 OID 4630700)
-- Dependencies: 728 6 471
-- Name: psh_cur_ins(billservice_periodicalservicehistory); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION psh_cur_ins(pshr billservice_periodicalservicehistory) RETURNS void
    AS $$BEGIN 
        RETURN; END;$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.psh_cur_ins(pshr billservice_periodicalservicehistory) OWNER TO ebs;

--
-- TOC entry 133 (class 1255 OID 4630701)
-- Dependencies: 728 6
-- Name: psh_del_trg_fn(); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION psh_del_trg_fn() RETURNS trigger
    AS $$
    BEGIN
        INSERT INTO billservice_periodicalservicehistory (service_id, transaction_id, datetime, accounttarif_id) VALUES( OLD.service_id, OLD.transaction_id, OLD.datetime, OLD.accounttarif_id);
        RETURN OLD;
    END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.psh_del_trg_fn() OWNER TO ebs;

--
-- TOC entry 136 (class 1255 OID 4630702)
-- Dependencies: 728 6
-- Name: psh_ins_trg_fn(); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION psh_ins_trg_fn() RETURNS trigger
    AS $$
DECLARE
    cur_chk int;
    prev_chk int;
BEGIN
    cur_chk := psh_cur_datechk(NEW.datetime);

    IF cur_chk = 0 THEN
        PERFORM psh_cur_ins(NEW);
    ELSIF cur_chk = 1 THEN
        BEGIN
            PERFORM psh_crt_pdb(NEW.datetime::date);
            PERFORM psh_crt_cur_ins(NEW.datetime::date);
            EXECUTE psh_cur_ins(NEW);
        EXCEPTION 
          WHEN duplicate_table THEN
             PERFORM psh_crt_cur_ins(NEW.datetime::date);
             EXECUTE psh_cur_ins(NEW);
        END;
        
        
    ELSE 
        prev_chk := psh_prev_datechk(NEW.datetime);
        IF prev_chk = 0 THEN
            PERFORM psh_prev_ins(NEW);
        ELSE
            BEGIN 
                PERFORM psh_inserter(NEW);
            EXCEPTION 
              WHEN undefined_table THEN
                PERFORM psh_crt_pdb(NEW.datetime::date);
                PERFORM psh_inserter(NEW);
            END;
        END IF;      
    END IF;
    RETURN NULL;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.psh_ins_trg_fn() OWNER TO ebs;

--
-- TOC entry 140 (class 1255 OID 4630703)
-- Dependencies: 728 471 6
-- Name: psh_inserter(billservice_periodicalservicehistory); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION psh_inserter(pshr billservice_periodicalservicehistory) RETURNS void
    AS $$
DECLARE
    datetx_ text := to_char(pshr.datetime::date, 'YYYYMM01');
    insq_   text;

    ttrn_actfid_ text;    
BEGIN
    
    IF pshr.accounttarif_id IS NULL THEN
       ttrn_actfid_ := 'NULL';
    ELSE
       ttrn_actfid_ := pshr.accounttarif_id::text;
    END IF;
    insq_ := 'INSERT INTO psh' || datetx_ || ' (service_id, account_id, accounttarif_id, type_id, summ, datetime) VALUES (' 
    || pshr.service_id || ',' || pshr.account_id || ',' || pshr.accounttarif_id || ','  || quote_literal(pshr.type_id) || ',' || pshr.summ || ','  || quote_literal(pshr.datetime) || ');';
    EXECUTE insq_;
    RETURN;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.psh_inserter(pshr billservice_periodicalservicehistory) OWNER TO ebs;

--
-- TOC entry 139 (class 1255 OID 4630704)
-- Dependencies: 728 6
-- Name: psh_prev_datechk(timestamp without time zone); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION psh_prev_datechk(psh_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700101'; d_e_ date := (DATE '19700101'+ interval '1 month')::date; BEGIN IF    psh_date < d_s_ THEN RETURN -1; ELSIF psh_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;


ALTER FUNCTION public.psh_prev_datechk(psh_date timestamp without time zone) OWNER TO ebs;

--
-- TOC entry 137 (class 1255 OID 4630705)
-- Dependencies: 728 6 471
-- Name: psh_prev_ins(billservice_periodicalservicehistory); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION psh_prev_ins(pshr billservice_periodicalservicehistory) RETURNS void
    AS $$BEGIN 
         RETURN; END;$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.psh_prev_ins(pshr billservice_periodicalservicehistory) OWNER TO ebs;

--
-- TOC entry 51 (class 1255 OID 283153)
-- Dependencies: 6 454
-- Name: querytree(query_int); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION querytree(query_int) RETURNS text
    AS '$libdir/_int', 'querytree'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.querytree(query_int) OWNER TO ebs;

--
-- TOC entry 50 (class 1255 OID 283155)
-- Dependencies: 454 6
-- Name: rboolop(query_int, integer[]); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION rboolop(query_int, integer[]) RETURNS boolean
    AS '$libdir/_int', 'rboolop'
    LANGUAGE c IMMUTABLE STRICT;


ALTER FUNCTION public.rboolop(query_int, integer[]) OWNER TO ebs;

--
-- TOC entry 3132 (class 0 OID 0)
-- Dependencies: 50
-- Name: FUNCTION rboolop(query_int, integer[]); Type: COMMENT; Schema: public; Owner: ebs
--

COMMENT ON FUNCTION rboolop(query_int, integer[]) IS 'boolean operation with array';


--
-- TOC entry 162 (class 1255 OID 4632127)
-- Dependencies: 6 728
-- Name: return_allowed(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION return_allowed() RETURNS bigint
    AS $$ BEGIN RETURN 32; END;$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.return_allowed() OWNER TO postgres;

--
-- TOC entry 138 (class 1255 OID 4630706)
-- Dependencies: 6 728
-- Name: rsss_crt_cur_ins(date); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION rsss_crt_cur_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION rsss_cur_ins (rsssr radius_session) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO rsss';
                         
    fn_bd_tx2_ text := '(account_id, sessionid, interrim_update, date_start, date_end, caller_id, called_id, nas_id, session_time, framed_protocol, bytes_in, bytes_out, checkouted_by_time, checkouted_by_trafic, disconnect_status, framed_ip_address)
                          VALUES 
                         (rsssr.account_id, rsssr.sessionid, rsssr.interrim_update, rsssr.date_start, rsssr.date_end, rsssr.caller_id, rsssr.called_id, rsssr.nas_id, rsssr.session_time, rsssr.framed_protocol, rsssr.bytes_in, rsssr.bytes_out, rsssr.checkouted_by_time, rsssr.checkouted_by_trafic, rsssr.disconnect_status, rsssr.framed_ip_address); RETURN; END;';
                          
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';


    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION rsss_cur_datechk(rsss_date timestamp without time zone) RETURNS integer AS ';

    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    rsss_date < d_s_ THEN RETURN -1; ELSIF rsss_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';



    dt_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION rsss_cur_dt() RETURNS date AS ';
    
    onemonth_ text := '1 month';
    query_ text;
    
    prevdate_ date;
    
BEGIN    


    
        query_ :=  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;

        EXECUTE query_;


        query_ :=  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '+ interval ' || quote_literal(onemonth_) ||  ch_fn_bd_tx3_) || fn_tx2_;

        EXECUTE query_;
        
        prevdate_ := rsss_cur_dt();
        
        PERFORM rsss_crt_prev_ins(prevdate_);
        
        query_ := dt_fn_tx1_ || quote_literal(' BEGIN RETURN  DATE ' || quote_literal(datetx_) || '; END; ') || fn_tx2_;
        
        EXECUTE query_;

        
    RETURN;

END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.rsss_crt_cur_ins(datetx date) OWNER TO ebs;

--
-- TOC entry 141 (class 1255 OID 4630707)
-- Dependencies: 728 6
-- Name: rsss_crt_pdb(date); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION rsss_crt_pdb(datetx date) RETURNS integer
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');
    datetx_e_ text := to_char((datetx + interval '1 month')::date, 'YYYYMM01');

    qt_dtx_ text;
    qt_dtx_e_ text;
    seq_tx1_ text := 'CREATE SEQUENCE rsss#rpdate#_id_seq
                      INCREMENT 1
                      MINVALUE 1
                      MAXVALUE 9223372036854775807
                      START 1
                      CACHE 1;';
    seqname_tx1_ text := 'rsss#rpdate#_id_seq';

    chk_tx1_ text := 'CHECK ( interrim_update >= DATE #stdtx# AND interrim_update < DATE #eddtx# )';
    ct_tx1_ text := 'CREATE TABLE rsss#rpdate# (
                     #chk#,
                     CONSTRAINT rsss#rpdate#_id_pkey PRIMARY KEY (id) ) 
                     INHERITS (radius_session) 
                     WITH (OIDS=FALSE);                     
                     CREATE INDEX rsss#rpdate#_interrim_update_id ON rsss#rpdate# USING btree (interrim_update);
                     CREATE INDEX rsss#rpdate#_account_id ON rsss#rpdate# USING btree (account_id);
                     ';
                     
    at_tx1_ text := 'ALTER TABLE rsss#rpdate# ALTER COLUMN id SET DEFAULT nextval(#qseqname#::regclass);';

    chk_       text;
    seq_query_ text;
    ct_query_  text;
    seqn_      text;
    at_query_  text;


BEGIN    
    seq_query_ := replace(seq_tx1_, '#rpdate#', datetx_);
    EXECUTE seq_query_;
    qt_dtx_    := quote_literal(datetx_);
    qt_dtx_e_  := quote_literal(datetx_e_);
    chk_       := replace(chk_tx1_, '#stdtx#', qt_dtx_ );
    chk_       := replace(chk_, '#eddtx#', qt_dtx_e_ );
    ct_query_  := replace(ct_tx1_, '#rpdate#', datetx_);
    ct_query_  := replace(ct_query_, '#chk#', chk_);
    EXECUTE ct_query_;
    seqn_        := replace(seqname_tx1_, '#rpdate#', datetx_);
    at_query_    := replace(at_tx1_, '#rpdate#', datetx_);
    at_query_    := replace(at_query_, '#qseqname#', quote_literal(seqn_));
    EXECUTE at_query_;
    RETURN 0;

END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.rsss_crt_pdb(datetx date) OWNER TO ebs;

--
-- TOC entry 142 (class 1255 OID 4630708)
-- Dependencies: 6 728
-- Name: rsss_crt_prev_ins(date); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION rsss_crt_prev_ins(datetx date) RETURNS void
    AS $$
DECLARE

    datetx_ text := to_char(datetx, 'YYYYMM01');


    fn_tx1_    text := 'CREATE OR REPLACE FUNCTION rsss_prev_ins (rsssr radius_session) RETURNS void AS ';

    fn_bd_tx1_ text := 'BEGIN 
                         INSERT INTO rsss';
                         
    fn_bd_tx2_ text := '(account_id, sessionid, interrim_update, date_start, date_end, caller_id, called_id, nas_id, session_time, framed_protocol, bytes_in, bytes_out, checkouted_by_time, checkouted_by_trafic, disconnect_status, framed_ip_address)
                          VALUES 
                         (rsssr.account_id, rsssr.sessionid, rsssr.interrim_update, rsssr.date_start, rsssr.date_end, rsssr.caller_id, rsssr.called_id, rsssr.nas_id, rsssr.session_time, rsssr.framed_protocol, rsssr.bytes_in, rsssr.bytes_out, rsssr.checkouted_by_time, rsssr.checkouted_by_trafic, rsssr.disconnect_status, rsssr.framed_ip_address); RETURN; END;';
                          
    fn_tx2_    text := ' LANGUAGE plpgsql VOLATILE COST 100;';


    ch_fn_tx1_ text := 'CREATE OR REPLACE FUNCTION rsss_prev_datechk(rsss_date timestamp without time zone) RETURNS integer AS ';

    ch_fn_bd_tx1_ text := ' DECLARE d_s_ date := DATE ';
    ch_fn_bd_tx2_ text := '; d_e_ date := (DATE ';
    ch_fn_bd_tx3_ text := ')::date; BEGIN IF    rsss_date < d_s_ THEN RETURN -1; ELSIF rsss_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; ';

    ch_fn_tx2_ text := ' LANGUAGE plpgsql VOLATILE COST 100;';

    qts_ text := 'CHK % % %';
    
    onemonth_ text := '1 month';
    query_ text;
    
BEGIN    

        EXECUTE  fn_tx1_  || quote_literal(fn_bd_tx1_ || datetx_ || fn_bd_tx2_) || fn_tx2_;


        query_ :=  ch_fn_tx1_  || quote_literal(ch_fn_bd_tx1_ || quote_literal(datetx_) || ch_fn_bd_tx2_ || quote_literal(datetx_) || '+ interval ' || quote_literal(onemonth_) ||  ch_fn_bd_tx3_) || fn_tx2_;
        
        EXECUTE query_;
        
    RETURN;

END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.rsss_crt_prev_ins(datetx date) OWNER TO ebs;

--
-- TOC entry 143 (class 1255 OID 4630709)
-- Dependencies: 6 728
-- Name: rsss_cur_datechk(timestamp without time zone); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION rsss_cur_datechk(rsss_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700201'; d_e_ date := (DATE '19700201'+ interval '1 month')::date; BEGIN IF    rsss_date < d_s_ THEN RETURN -1; ELSIF rsss_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;


ALTER FUNCTION public.rsss_cur_datechk(rsss_date timestamp without time zone) OWNER TO ebs;

--
-- TOC entry 144 (class 1255 OID 4630710)
-- Dependencies: 6 728
-- Name: rsss_cur_dt(); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION rsss_cur_dt() RETURNS date
    AS $$ BEGIN RETURN  DATE '19700201'; END; $$
    LANGUAGE plpgsql;


ALTER FUNCTION public.rsss_cur_dt() OWNER TO ebs;

--
-- TOC entry 145 (class 1255 OID 4630726)
-- Dependencies: 473 728 6
-- Name: rsss_cur_ins(radius_session); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION rsss_cur_ins(rsssr radius_session) RETURNS void
    AS $$BEGIN 
       RETURN; END;$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.rsss_cur_ins(rsssr radius_session) OWNER TO ebs;

--
-- TOC entry 146 (class 1255 OID 4630727)
-- Dependencies: 728 6
-- Name: rsss_del_trg_fn(); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION rsss_del_trg_fn() RETURNS trigger
    AS $$
    BEGIN
        INSERT INTO radius_session (account_id, sessionid, interrim_update, date_start, date_end, caller_id, called_id, nas_id, session_time, framed_protocol, bytes_in, bytes_out, checkouted_by_time, checkouted_by_trafic, disconnect_status, framed_ip_address) VALUES( OLD.account_id, OLD.sessionid, OLD.interrim_update, OLD.date_start, OLD.date_end, OLD.caller_id, OLD.called_id, OLD.nas_id, OLD.session_time, OLD.framed_protocol, OLD.bytes_in, OLD.bytes_out, OLD.checkouted_by_time, OLD.checkouted_by_trafic, OLD.disconnect_status, OLD.framed_ip_address);
        RETURN OLD;
    END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.rsss_del_trg_fn() OWNER TO ebs;

--
-- TOC entry 147 (class 1255 OID 4630728)
-- Dependencies: 6 728
-- Name: rsss_ins_trg_fn(); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION rsss_ins_trg_fn() RETURNS trigger
    AS $$
DECLARE
    cur_chk int;
    prev_chk int;
BEGIN
    cur_chk := rsss_cur_datechk(NEW.interrim_update);

    IF cur_chk = 0 THEN
        PERFORM rsss_cur_ins(NEW);
    ELSIF cur_chk = 1 THEN
        BEGIN
            PERFORM rsss_crt_pdb(NEW.interrim_update::date);
            PERFORM rsss_crt_cur_ins(NEW.interrim_update::date);
            EXECUTE rsss_cur_ins(NEW);
        EXCEPTION 
          WHEN duplicate_table THEN
             PERFORM rsss_crt_cur_ins(NEW.interrim_update::date);
             EXECUTE rsss_cur_ins(NEW);
        END;
        
        
    ELSE 
        prev_chk := rsss_prev_datechk(NEW.interrim_update);
        IF prev_chk = 0 THEN
            PERFORM rsss_prev_ins(NEW);
        ELSE
            BEGIN 
                PERFORM rsss_inserter(NEW);
            EXCEPTION 
              WHEN undefined_table THEN
                PERFORM rsss_crt_pdb(NEW.interrim_update::date);
                PERFORM rsss_inserter(NEW);
            END;
        END IF;      
    END IF;
    RETURN NULL;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.rsss_ins_trg_fn() OWNER TO ebs;

--
-- TOC entry 148 (class 1255 OID 4630729)
-- Dependencies: 6 728 473
-- Name: rsss_inserter(radius_session); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION rsss_inserter(rsssr radius_session) RETURNS void
    AS $$
DECLARE
    datetx_ text := to_char(rsssr.interrim_update::date, 'YYYYMM01');
    insq_   text;

  
    ttrn_sessionid_ text; 
    ttrn_interrim_update_ text; 
    ttrn_date_start_ text; 
    ttrn_date_end_ text; 
    ttrn_caller_id_ text; 
    ttrn_called_id_ text; 
    ttrn_session_time_ int;
    ttrn_bytes_in_ int; 
    ttrn_bytes_out_ int; 
    ttrn_checkouted_by_time_ boolean; 
    ttrn_checkouted_by_trafic_ boolean; 
    ttrn_disconnect_status_ text; 
    ttrn_framed_ip_address_ text;  
BEGIN
    
    IF rsssr.sessionid IS NULL THEN
       ttrn_sessionid_ := quote_literal('');
    ELSE
       ttrn_sessionid_ := quote_literal(rsssr.sessionid);
    END IF;
    IF rsssr.interrim_update IS NULL THEN
       ttrn_interrim_update_ := quote_literal(now()::timestamp without time zone);
    ELSE
       ttrn_interrim_update_ := quote_literal(rsssr.interrim_update);
    END IF;
    IF rsssr.date_start IS NULL THEN
       ttrn_date_start_ := 'NULL';
    ELSE
       ttrn_date_start_ := quote_literal(rsssr.date_start);
    END IF;
    IF rsssr.date_end IS NULL THEN
       ttrn_date_end_ := 'NULL';
    ELSE
       ttrn_date_end_ := quote_literal(rsssr.date_end);
    END IF;
    IF rsssr.caller_id IS NULL THEN
       ttrn_caller_id_ := quote_literal('');
    ELSE
       ttrn_caller_id_ := quote_literal(rsssr.caller_id);
    END IF;
    IF rsssr.called_id IS NULL THEN
       ttrn_called_id_ := quote_literal('');
    ELSE
       ttrn_called_id_ := quote_literal(rsssr.called_id);
    END IF;
    IF rsssr.session_time IS NULL THEN
       ttrn_session_time_ := 0;
    ELSE
       ttrn_session_time_ := rsssr.session_time;
    END IF;
    IF rsssr.bytes_in IS NULL THEN
       ttrn_bytes_in_ := 0;
    ELSE
       ttrn_bytes_in_ := rsssr.bytes_in;
    END IF;
    IF rsssr.bytes_out IS NULL THEN
       ttrn_bytes_out_ := 0;
    ELSE
       ttrn_bytes_out_ := rsssr.bytes_out;
    END IF;
    IF rsssr.checkouted_by_time IS NULL THEN
       ttrn_checkouted_by_time_ := FALSE;
    ELSE
       ttrn_checkouted_by_time_ := rsssr.checkouted_by_time;
    END IF;
    IF rsssr.checkouted_by_trafic IS NULL THEN
       ttrn_checkouted_by_trafic_ := FALSE;
    ELSE
       ttrn_checkouted_by_trafic_ := rsssr.checkouted_by_trafic;
    END IF;    
    IF rsssr.disconnect_status IS NULL THEN
       ttrn_disconnect_status_ := 'NULL';
    ELSE
       ttrn_disconnect_status_ := quote_literal(rsssr.disconnect_status);
    END IF;
    IF rsssr.framed_ip_address IS NULL THEN
       ttrn_framed_ip_address_ := 'NULL';
    ELSE
       ttrn_framed_ip_address_ := quote_literal(rsssr.framed_ip_address);
    END IF;

    insq_ := 'INSERT INTO rsss' || datetx_ || ' (account_id, sessionid, interrim_update, date_start, date_end, caller_id, called_id, nas_id, session_time, framed_protocol, bytes_in, bytes_out, checkouted_by_time, checkouted_by_trafic, disconnect_status, framed_ip_address) VALUES ('  || rsssr.account_id || ','  || ttrn_sessionid_ || ',' || ttrn_interrim_update_ || ',' || ttrn_date_start_ || ',' || ttrn_date_end_  || ',' ||  ttrn_caller_id_ || ','  || ttrn_called_id_ || ',' || quote_literal(rsssr.nas_id) || ',' || ttrn_session_time_ || ',' || quote_literal(rsssr.framed_protocol) || ',' || ttrn_bytes_in_ || ',' || ttrn_bytes_out_ || ',' || ttrn_checkouted_by_time_ || ',' || ttrn_checkouted_by_trafic_ || ',' || ttrn_disconnect_status_ || ',' || ttrn_framed_ip_address_ || ');';
    EXECUTE insq_;
    RETURN;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.rsss_inserter(rsssr radius_session) OWNER TO ebs;

--
-- TOC entry 149 (class 1255 OID 4630730)
-- Dependencies: 728 6
-- Name: rsss_prev_datechk(timestamp without time zone); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION rsss_prev_datechk(rsss_date timestamp without time zone) RETURNS integer
    AS $$ DECLARE d_s_ date := DATE '19700201'; d_e_ date := (DATE '19700201'+ interval '1 month')::date; BEGIN IF    rsss_date < d_s_ THEN RETURN -1; ELSIF rsss_date < d_e_ THEN RETURN 0; ELSE RETURN 1; END IF; END; $$
    LANGUAGE plpgsql;


ALTER FUNCTION public.rsss_prev_datechk(rsss_date timestamp without time zone) OWNER TO ebs;

--
-- TOC entry 150 (class 1255 OID 4630731)
-- Dependencies: 728 473 6
-- Name: rsss_prev_ins(radius_session); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION rsss_prev_ins(rsssr radius_session) RETURNS void
    AS $$BEGIN 
        RETURN; END;$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.rsss_prev_ins(rsssr radius_session) OWNER TO ebs;

--
-- TOC entry 178 (class 1255 OID 4632584)
-- Dependencies: 728 6
-- Name: set_deleted_trg_fn(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION set_deleted_trg_fn() RETURNS trigger
    AS $$
BEGIN
	IF OLD.deleted IS TRUE THEN
	    RETURN OLD;
	ELSE
        UPDATE billservice_tariff SET deleted=TRUE WHERE id=OLD.id;
	    RETURN NULL;
	END IF;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.set_deleted_trg_fn() OWNER TO postgres;

--
-- TOC entry 172 (class 1255 OID 4632557)
-- Dependencies: 728 6
-- Name: shedulelog_blocked_fn(integer, integer, timestamp without time zone, numeric); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION shedulelog_blocked_fn(account_id_ integer, accounttarif_id_ integer, blocked_ timestamp without time zone, cost_ numeric) RETURNS void
    AS $$ 
BEGIN
	UPDATE billservice_account SET balance_blocked=True WHERE id=account_id_ and ballance+credit<cost_;
    UPDATE billservice_shedulelog SET balance_blocked=blocked_, accounttarif_id=accounttarif_id_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_shedulelog(account_id, accounttarif_id, balance_blocked) VALUES(account_id_,accounttarif_id_, blocked_);
    END IF;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.shedulelog_blocked_fn(account_id_ integer, accounttarif_id_ integer, blocked_ timestamp without time zone, cost_ numeric) OWNER TO postgres;

--
-- TOC entry 161 (class 1255 OID 4632119)
-- Dependencies: 6 728
-- Name: shedulelog_co_fn(integer, integer, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION shedulelog_co_fn(account_id_ integer, accounttarif_id_ integer, checkout_ timestamp without time zone) RETURNS void
    AS $$ 
BEGIN
    UPDATE billservice_shedulelog SET ballance_checkout=checkout_, accounttarif_id=accounttarif_id_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_shedulelog(account_id, accounttarif_id, ballance_checkout) VALUES(account_id_,accounttarif_id_, checkout_);
    END IF;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.shedulelog_co_fn(account_id_ integer, accounttarif_id_ integer, checkout_ timestamp without time zone) OWNER TO postgres;

--
-- TOC entry 160 (class 1255 OID 4632124)
-- Dependencies: 6 728
-- Name: shedulelog_time_credit_fn(integer, integer, integer, integer, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION shedulelog_time_credit_fn(account_id_ integer, accounttarif_id_ integer, taccs_id_ integer, size_ integer, datetime_ timestamp without time zone) RETURNS void
    AS $$ 
BEGIN	
	UPDATE billservice_accountprepaystime SET size=size+size_, datetime=datetime_ WHERE account_tarif_id=accounttarif_id_; -- AND??
	IF NOT FOUND THEN
		INSERT INTO billservice_accountprepaystime (account_tarif_id, size, datetime, prepaid_time_service_id) VALUES(accounttarif_id_, size_, datetime_, taccs_id_);
    END IF;
	UPDATE billservice_shedulelog SET prepaid_time_accrued=datetime_, accounttarif_id=accounttarif_id_ WHERE account_id=account_id_;
	IF NOT FOUND THEN
    	INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_time_accrued) VALUES(account_id_,accounttarif_id_, datetime_);
	END IF;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.shedulelog_time_credit_fn(account_id_ integer, accounttarif_id_ integer, taccs_id_ integer, size_ integer, datetime_ timestamp without time zone) OWNER TO postgres;

--
-- TOC entry 165 (class 1255 OID 4632122)
-- Dependencies: 6 728
-- Name: shedulelog_time_reset_fn(integer, integer, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION shedulelog_time_reset_fn(account_id_ integer, accounttarif_id_ integer, reset_ timestamp without time zone) RETURNS void
    AS $$ 
BEGIN
	DELETE FROM billservice_accountprepaystime WHERE account_tarif_id=accounttarif_id_;
    UPDATE billservice_shedulelog SET prepaid_time_reset=reset_, accounttarif_id=accounttarif_id_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_time_reset) VALUES(account_id_,accounttarif_id_, reset_);
    END IF;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.shedulelog_time_reset_fn(account_id_ integer, accounttarif_id_ integer, reset_ timestamp without time zone) OWNER TO postgres;

--
-- TOC entry 174 (class 1255 OID 4632561)
-- Dependencies: 728 6
-- Name: shedulelog_tr_credit_fn(integer, integer, integer, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION shedulelog_tr_credit_fn(account_id_ integer, accounttarif_id_ integer, trts_id_ integer, datetime_ timestamp without time zone) RETURNS void
    AS $$ 
DECLARE
	prepaid_tr_id_ int;
	size_ bigint;
	count_ int := 0;
BEGIN
	
	FOR prepaid_tr_id_, size_ IN SELECT id, size FROM billservice_prepaidtraffic WHERE traffic_transmit_service_id=trts_id_ LOOP
		UPDATE billservice_accountprepaystrafic SET size=size+size_, datetime=datetime_ WHERE account_tarif_id=accounttarif_id_ AND prepaid_traffic_id=prepaid_tr_id_;
		IF NOT FOUND THEN
			INSERT INTO billservice_accountprepaystrafic (account_tarif_id, prepaid_traffic_id, size, datetime) VALUES(accounttarif_id_, prepaid_tr_id_, size_, datetime_);
        END IF;
        count_ := count_ + 1;
    END LOOP;
    IF count_ > 0 THEN
    	UPDATE billservice_shedulelog SET prepaid_traffic_accrued=datetime_, accounttarif_id=accounttarif_id_ WHERE account_id=account_id_;
    	IF NOT FOUND THEN
        	INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_traffic_accrued) VALUES(account_id_,accounttarif_id_, datetime_);
    	END IF;
   	END IF;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.shedulelog_tr_credit_fn(account_id_ integer, accounttarif_id_ integer, trts_id_ integer, datetime_ timestamp without time zone) OWNER TO postgres;

--
-- TOC entry 164 (class 1255 OID 4632121)
-- Dependencies: 728 6
-- Name: shedulelog_tr_reset_fn(integer, integer, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION shedulelog_tr_reset_fn(account_id_ integer, accounttarif_id_ integer, reset_ timestamp without time zone) RETURNS void
    AS $$ 
BEGIN
	DELETE FROM billservice_accountprepaystrafic WHERE account_tarif_id=accounttarif_id_;
    UPDATE billservice_shedulelog SET prepaid_traffic_reset=reset_, accounttarif_id=accounttarif_id_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_shedulelog(account_id, accounttarif_id, prepaid_traffic_reset) VALUES(account_id_,accounttarif_id_, reset_);
    END IF;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.shedulelog_tr_reset_fn(account_id_ integer, accounttarif_id_ integer, reset_ timestamp without time zone) OWNER TO postgres;



CREATE FUNCTION speedlimit_ins_fn(splimit_id_ integer, account_id_ integer) RETURNS void
    AS $$ 
BEGIN
    UPDATE billservice_accountspeedlimit SET speedlimit_id=splimit_id_ WHERE account_id=account_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_accountspeedlimit(account_id, speedlimit_id) VALUES(account_id_,splimit_id_);
    END IF;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.speedlimit_ins_fn(splimit_id_ integer, account_id_ integer) OWNER TO postgres;

--
-- TOC entry 65 (class 1255 OID 283180)
-- Dependencies: 6
-- Name: subarray(integer[], integer, integer); Type: FUNCTION; Schema: public; Owner: ebs
--


CREATE FUNCTION tftrans_ins_trg_fn() RETURNS trigger
    AS $$ 
BEGIN
    NEW.datetime := date_trunc('minute', NEW.datetime) - interval '1 min' * (date_part('min', NEW.datetime)::int % 5); 
    UPDATE billservice_traffictransaction SET summ=summ+NEW.summ WHERE traffictransmitservice_id=NEW.traffictransmitservice_id AND account_id=NEW.account_id AND datetime=NEW.datetime;
    IF FOUND THEN
        RETURN NULL;
    ELSE
        RETURN NEW;
    END IF;
    
END;
$$
    LANGUAGE plpgsql;


CREATE FUNCTION timetransaction_insert(taccs_id_ integer, accounttarif_id_ integer, account_id_ integer, summ_ numeric, datetime_ timestamp without time zone, sessionid_ character varying, interrim_update_ timestamp without time zone) RETURNS void
    AS $$ 
DECLARE
	datetime_agg_ timestamp without time zone;
	ins_tr_id_ int;
BEGIN	

    datetime_agg_ := date_trunc('minute', datetime_) - interval '1 min' * (date_part('min', datetime_)::int % 5); 
    UPDATE billservice_timetransaction SET summ=summ+summ_ WHERE timeaccessservice_id=taccs_id_ AND account_id=account_id_ AND datetime=datetime_agg_ RETURNING id INTO ins_tr_id_;
    IF NOT FOUND THEN
        INSERT INTO billservice_timetransaction(timeaccessservice_id, accounttarif_id, account_id, summ, datetime) VALUES (taccs_id_, accounttarif_id_, account_id_, summ_, datetime_agg_) RETURNING id INTO ins_tr_id_;
    END IF;
	UPDATE radius_session SET transaction_id=ins_tr_id_ WHERE account_id=account_id_ AND sessionid=sessionid_ AND interrim_update=interrim_update_;
    RETURN;  
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.timetransaction_insert(taccs_id_ integer, accounttarif_id_ integer, account_id_ integer, summ_ numeric, datetime_ timestamp without time zone, sessionid_ character varying, interrim_update_ timestamp without time zone) OWNER TO postgres;

--
-- TOC entry 158 (class 1255 OID 4632085)
-- Dependencies: 728 6
-- Name: tmtrans_ins_trg_fn(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION tmtrans_ins_trg_fn() RETURNS trigger
    AS $$ 
BEGIN
    NEW.datetime := date_trunc('minute', NEW.datetime) - interval '1 min' * (date_part('min', NEW.datetime)::int % 5); 
    UPDATE billservice_timetransaction SET summ=summ+NEW.summ WHERE timeaccessservice_id=NEW.timeaccessservice_id AND account_id=NEW.account_id AND datetime=NEW.datetime;
    IF FOUND THEN
        RETURN NULL;
    ELSE
        RETURN NEW;
    END IF;
    
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.tmtrans_ins_trg_fn() OWNER TO postgres;

--
-- TOC entry 154 (class 1255 OID 4632012)
-- Dependencies: 6 728
-- Name: trans_acctf_ins_trg_fn(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION trans_acctf_ins_trg_fn() RETURNS trigger
    AS $$ 
BEGIN
    IF NEW.accounttarif_id IS NULL THEN
        SELECT INTO NEW.accounttarif_id ba.id FROM billservice_accounttarif AS ba WHERE ba.account_id = NEW.account_id AND ba.datetime < NEW.created ORDER BY ba.datetime DESC LIMIT 1;
    END IF;
    RETURN NEW;    
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.trans_acctf_ins_trg_fn() OWNER TO postgres;

--
-- TOC entry 171 (class 1255 OID 4632559)
-- Dependencies: 6 728
-- Name: transaction_block_sum(integer, timestamp without time zone, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION transaction_block_sum(account_id_ integer, start_date_ timestamp without time zone, end_date_ timestamp without time zone) RETURNS numeric
    AS $$ 
DECLARE
    start_date_5m_ timestamp without time zone;
    result_ decimal;
BEGIN
    start_date_5m_ := date_trunc('minute', start_date_) - interval '1 min' * (date_part('min', start_date_)::int % 5); 
    SELECT INTO result_ sum(ssum) FROM (SELECT sum(summ) AS ssum FROM billservice_transaction WHERE account_id=account_id_ AND (summ > 0) AND (created BETWEEN start_date_ AND end_date_) UNION ALL SELECT sum(summ) AS ssum FROM billservice_traffictransaction WHERE account_id=account_id_ AND (summ > 0) AND (datetime BETWEEN start_date_ AND end_date_) UNION ALL SELECT sum(summ) AS ssum FROM billservice_timetransaction WHERE account_id=account_id_ AND (summ > 0) AND (datetime BETWEEN start_date_ AND end_date_) UNION ALL SELECT sum(summ) AS ssum FROM billservice_periodicalservicehistory WHERE account_id=account_id_ AND (summ > 0) AND (datetime BETWEEN start_date_ AND end_date_)  UNION ALL SELECT sum(summ) AS ssum FROM billservice_onetimeservicehistory WHERE account_id=account_id_ AND (summ > 0) AND (datetime BETWEEN start_date_ AND end_date_)) AS ts_union ;
    RETURN result_;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.transaction_block_sum(account_id_ integer, start_date_ timestamp without time zone, end_date_ timestamp without time zone) OWNER TO postgres;

--
-- TOC entry 151 (class 1255 OID 4630732)
-- Dependencies: 728 6
-- Name: transaction_fn(character varying, integer, character varying, boolean, integer, double precision, text, timestamp without time zone, integer, integer, integer); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION transaction_fn(bill_ character varying, account_id_ integer, type_id_ character varying, approved_ boolean, tarif_id_ integer, summ_ double precision, description_ text, created_ timestamp without time zone, ps_id_ integer, acctf_id_ integer, ps_condition_type_ integer) RETURNS void
    AS $$
DECLARE
    new_summ_ double precision;
    tr_id_ int;
BEGIN
    SELECT INTO new_summ_ summ_*(NOT EXISTS (SELECT id FROM billservice_suspendedperiod WHERE account_id=account_id AND (created_ BETWEEN start_date AND end_date)))::int;
    IF (ps_condition_type_ = 1) AND (new_summ_ > 0) THEN
	SELECT new_summ_*(ballance >= 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    ELSIF (ps_condition_type_ = 2) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance < 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    END IF; 
    IF (new_summ_ > 0) THEN
        INSERT INTO billservice_transaction (bill, account_id,  type_id, approved,  tarif_id, summ, description, created) VALUES (bill_ , account_id_ ,  type_id_, approved_,  tarif_id_, new_summ_, description_, created_) RETURNING id INTO tr_id_;
    END IF;
    INSERT INTO billservice_periodicalservicehistory (service_id, transaction_id, accounttarif_id,  datetime) VALUES (ps_id_, tr_id_, acctf_id_, created_);
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.transaction_fn(bill_ character varying, account_id_ integer, type_id_ character varying, approved_ boolean, tarif_id_ integer, summ_ double precision, description_ text, created_ timestamp without time zone, ps_id_ integer, acctf_id_ integer, ps_condition_type_ integer) OWNER TO ebs;

--
-- TOC entry 173 (class 1255 OID 4632560)
-- Dependencies: 728 6
-- Name: transaction_sum(integer, integer, timestamp without time zone, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION transaction_sum(account_id_ integer, acctf_id_ integer, start_date_ timestamp without time zone, end_date_ timestamp without time zone) RETURNS numeric
    AS $$ 
DECLARE
    start_date_5m_ timestamp without time zone;
    result_ decimal;
BEGIN
    start_date_5m_ := date_trunc('minute', start_date_) - interval '1 min' * (date_part('min', start_date_)::int % 5); 
    SELECT INTO result_ sum(ssum) FROM (SELECT sum(summ) AS ssum FROM billservice_transaction WHERE account_id=account_id_ AND (accounttarif_id=acctf_id_) AND (summ > 0)  AND (created > start_date_ AND created < end_date_) UNION ALL SELECT sum(summ) AS ssum FROM billservice_traffictransaction WHERE account_id=account_id_ AND (accounttarif_id=acctf_id_) AND (summ > 0)  AND (datetime > start_date_ AND datetime < end_date_)UNION ALL SELECT sum(summ) AS ssum FROM billservice_timetransaction WHERE account_id=account_id_ AND (accounttarif_id=acctf_id_) AND (summ > 0)  AND (datetime > start_date_ AND datetime < end_date_)  UNION ALL SELECT sum(summ) AS ssum FROM billservice_periodicalservicehistory WHERE account_id=account_id_ AND (accounttarif_id=acctf_id_) AND (summ > 0)  AND (datetime > start_date_ AND datetime < end_date_)  UNION ALL SELECT sum(summ) AS ssum FROM billservice_onetimeservicehistory WHERE account_id=account_id_ AND (accounttarif_id=acctf_id_) AND (summ > 0)  AND (datetime > start_date_ AND datetime < end_date_)) AS ts_union ;
    RETURN result_;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.transaction_sum(account_id_ integer, acctf_id_ integer, start_date_ timestamp without time zone, end_date_ timestamp without time zone) OWNER TO postgres;

--
-- TOC entry 152 (class 1255 OID 4630733)
-- Dependencies: 728 6
-- Name: transaction_tarif(character varying, character varying, boolean, integer, double precision, text, timestamp without time zone, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: ebs
--

CREATE FUNCTION transaction_tarif(bill_ character varying, type_id_ character varying, approved_ boolean, tarif_id_ integer, summ_ double precision, description_ text, created_ timestamp without time zone, acct_datetime_ timestamp without time zone) RETURNS void
    AS $$
DECLARE
    acc_id_ int;
BEGIN
    FOR acc_id_ IN SELECT account_id FROM billservice_accounttarif WHERE datetime<acct_datetime_ AND tarif_id=tarif_id_ LOOP
	INSERT INTO billservice_transaction (bill, account_id,  type_id, approved,  tarif_id, summ, description, created) VALUES (bill_ , acc_id_, type_id_, approved_, tarif_id_, summ_, description_, created_);
    END LOOP;  
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.transaction_tarif(bill_ character varying, type_id_ character varying, approved_ boolean, tarif_id_ integer, summ_ double precision, description_ text, created_ timestamp without time zone, acct_datetime_ timestamp without time zone) OWNER TO ebs;

--
-- TOC entry 153 (class 1255 OID 4630734)
-- Dependencies: 728 6
-- Name: unblock_balance(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION unblock_balance(account_id integer) RETURNS void
    AS $$
BEGIN
    UPDATE billservice_account SET balance_blocked=FALSE WHERE id=account_id;
RETURN;
END;
$$
    LANGUAGE plpgsql;


ALTER FUNCTION public.unblock_balance(account_id integer) OWNER TO postgres;


--
-- TOC entry 1943 (class 1259 OID 4630738)
-- Dependencies: 6 1942
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_group_id_seq OWNER TO ebs;

--
-- TOC entry 3133 (class 0 OID 0)
-- Dependencies: 1943
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE auth_group_id_seq OWNED BY auth_group.id;


--
-- TOC entry 3134 (class 0 OID 0)
-- Dependencies: 1943
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('auth_group_id_seq', 1, false);


--
-- TOC entry 1945 (class 1259 OID 4630743)
-- Dependencies: 6 1944
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_group_permissions_id_seq OWNER TO ebs;

--
-- TOC entry 3135 (class 0 OID 0)
-- Dependencies: 1945
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE auth_group_permissions_id_seq OWNED BY auth_group_permissions.id;


--
-- TOC entry 3136 (class 0 OID 0)
-- Dependencies: 1945
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('auth_group_permissions_id_seq', 1, false);


--
-- TOC entry 1947 (class 1259 OID 4630751)
-- Dependencies: 6 1946
-- Name: auth_message_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE auth_message_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_message_id_seq OWNER TO ebs;

--
-- TOC entry 3137 (class 0 OID 0)
-- Dependencies: 1947
-- Name: auth_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE auth_message_id_seq OWNED BY auth_message.id;


--
-- TOC entry 3138 (class 0 OID 0)
-- Dependencies: 1947
-- Name: auth_message_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('auth_message_id_seq', 1, false);


--
-- TOC entry 1949 (class 1259 OID 4630756)
-- Dependencies: 6 1948
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE auth_permission_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_permission_id_seq OWNER TO ebs;

--
-- TOC entry 3139 (class 0 OID 0)
-- Dependencies: 1949
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE auth_permission_id_seq OWNED BY auth_permission.id;


--
-- TOC entry 3140 (class 0 OID 0)
-- Dependencies: 1949
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('auth_permission_id_seq', 139, true);


--
-- TOC entry 1952 (class 1259 OID 4630764)
-- Dependencies: 1951 6
-- Name: auth_user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE auth_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_user_groups_id_seq OWNER TO ebs;

--
-- TOC entry 3141 (class 0 OID 0)
-- Dependencies: 1952
-- Name: auth_user_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE auth_user_groups_id_seq OWNED BY auth_user_groups.id;


--
-- TOC entry 3142 (class 0 OID 0)
-- Dependencies: 1952
-- Name: auth_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('auth_user_groups_id_seq', 1, false);


--
-- TOC entry 1953 (class 1259 OID 4630766)
-- Dependencies: 1950 6
-- Name: auth_user_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE auth_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_user_id_seq OWNER TO ebs;

--
-- TOC entry 3143 (class 0 OID 0)
-- Dependencies: 1953
-- Name: auth_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE auth_user_id_seq OWNED BY auth_user.id;


--
-- TOC entry 3144 (class 0 OID 0)
-- Dependencies: 1953
-- Name: auth_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('auth_user_id_seq', 1, false);


--
-- TOC entry 1955 (class 1259 OID 4630771)
-- Dependencies: 6 1954
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE auth_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_user_user_permissions_id_seq OWNER TO ebs;

--
-- TOC entry 3145 (class 0 OID 0)
-- Dependencies: 1955
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE auth_user_user_permissions_id_seq OWNED BY auth_user_user_permissions.id;


--
-- TOC entry 3146 (class 0 OID 0)
-- Dependencies: 1955
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('auth_user_user_permissions_id_seq', 1, false);


--
-- TOC entry 1957 (class 1259 OID 4630786)
-- Dependencies: 6 1956
-- Name: billservice_accessparameters_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_accessparameters_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_accessparameters_id_seq OWNER TO ebs;

--
-- TOC entry 3147 (class 0 OID 0)
-- Dependencies: 1957
-- Name: billservice_accessparameters_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_accessparameters_id_seq OWNED BY billservice_accessparameters.id;


--
-- TOC entry 3148 (class 0 OID 0)
-- Dependencies: 1957
-- Name: billservice_accessparameters_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_accessparameters_id_seq', 4, true);


--
-- TOC entry 1959 (class 1259 OID 4630832)
-- Dependencies: 1958 6
-- Name: billservice_account_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_account_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_account_id_seq OWNER TO ebs;

--
-- TOC entry 3149 (class 0 OID 0)
-- Dependencies: 1959
-- Name: billservice_account_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_account_id_seq OWNED BY billservice_account.id;


--
-- TOC entry 3150 (class 0 OID 0)
-- Dependencies: 1959
-- Name: billservice_account_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_account_id_seq', 7, true);


--
-- TOC entry 2084 (class 1259 OID 4632766)
-- Dependencies: 6 2085
-- Name: billservice_accountaddonservice_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_accountaddonservice_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_accountaddonservice_id_seq OWNER TO ebs;

--
-- TOC entry 3151 (class 0 OID 0)
-- Dependencies: 2084
-- Name: billservice_accountaddonservice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_accountaddonservice_id_seq OWNED BY billservice_accountaddonservice.id;


--
-- TOC entry 3152 (class 0 OID 0)
-- Dependencies: 2084
-- Name: billservice_accountaddonservice_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_accountaddonservice_id_seq', 1, false);


--
-- TOC entry 1961 (class 1259 OID 4630841)
-- Dependencies: 6 1960
-- Name: billservice_accountipnspeed_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_accountipnspeed_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_accountipnspeed_id_seq OWNER TO ebs;

--
-- TOC entry 3153 (class 0 OID 0)
-- Dependencies: 1961
-- Name: billservice_accountipnspeed_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_accountipnspeed_id_seq OWNED BY billservice_accountipnspeed.id;


--
-- TOC entry 3154 (class 0 OID 0)
-- Dependencies: 1961
-- Name: billservice_accountipnspeed_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_accountipnspeed_id_seq', 1, false);


--
-- TOC entry 1963 (class 1259 OID 4630848)
-- Dependencies: 6 1962
-- Name: billservice_accountprepaystime_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_accountprepaystime_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_accountprepaystime_id_seq OWNER TO ebs;

--
-- TOC entry 3155 (class 0 OID 0)
-- Dependencies: 1963
-- Name: billservice_accountprepaystime_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_accountprepaystime_id_seq OWNED BY billservice_accountprepaystime.id;


--
-- TOC entry 3156 (class 0 OID 0)
-- Dependencies: 1963
-- Name: billservice_accountprepaystime_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_accountprepaystime_id_seq', 1, false);


--
-- TOC entry 1965 (class 1259 OID 4630855)
-- Dependencies: 1964 6
-- Name: billservice_accountprepaystrafic_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_accountprepaystrafic_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_accountprepaystrafic_id_seq OWNER TO ebs;

--
-- TOC entry 3157 (class 0 OID 0)
-- Dependencies: 1965
-- Name: billservice_accountprepaystrafic_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_accountprepaystrafic_id_seq OWNED BY billservice_accountprepaystrafic.id;


--
-- TOC entry 3158 (class 0 OID 0)
-- Dependencies: 1965
-- Name: billservice_accountprepaystrafic_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_accountprepaystrafic_id_seq', 1, false);


--
-- TOC entry 1967 (class 1259 OID 4630860)
-- Dependencies: 6 1966
-- Name: billservice_accountspeedlimit_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_accountspeedlimit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_accountspeedlimit_id_seq OWNER TO ebs;

--
-- TOC entry 3159 (class 0 OID 0)
-- Dependencies: 1967
-- Name: billservice_accountspeedlimit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_accountspeedlimit_id_seq OWNED BY billservice_accountspeedlimit.id;


--
-- TOC entry 3160 (class 0 OID 0)
-- Dependencies: 1967
-- Name: billservice_accountspeedlimit_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_accountspeedlimit_id_seq', 1, false);


--
-- TOC entry 1969 (class 1259 OID 4630865)
-- Dependencies: 1968 6
-- Name: billservice_accounttarif_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_accounttarif_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_accounttarif_id_seq OWNER TO ebs;

--
-- TOC entry 3161 (class 0 OID 0)
-- Dependencies: 1969
-- Name: billservice_accounttarif_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_accounttarif_id_seq OWNED BY billservice_accounttarif.id;


--
-- TOC entry 3162 (class 0 OID 0)
-- Dependencies: 1969
-- Name: billservice_accounttarif_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_accounttarif_id_seq', 6, true);


--
-- TOC entry 2080 (class 1259 OID 4632692)
-- Dependencies: 6 2081
-- Name: billservice_addonservice_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_addonservice_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_addonservice_id_seq OWNER TO ebs;

--
-- TOC entry 3163 (class 0 OID 0)
-- Dependencies: 2080
-- Name: billservice_addonservice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_addonservice_id_seq OWNED BY billservice_addonservice.id;


--
-- TOC entry 3164 (class 0 OID 0)
-- Dependencies: 2080
-- Name: billservice_addonservice_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_addonservice_id_seq', 1, false);


--
-- TOC entry 2082 (class 1259 OID 4632739)
-- Dependencies: 2083 6
-- Name: billservice_addonservicetarif_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_addonservicetarif_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_addonservicetarif_id_seq OWNER TO ebs;

--
-- TOC entry 3165 (class 0 OID 0)
-- Dependencies: 2082
-- Name: billservice_addonservicetarif_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_addonservicetarif_id_seq OWNED BY billservice_addonservicetarif.id;


--
-- TOC entry 3166 (class 0 OID 0)
-- Dependencies: 2082
-- Name: billservice_addonservicetarif_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_addonservicetarif_id_seq', 1, false);


--
-- TOC entry 2086 (class 1259 OID 4632789)
-- Dependencies: 6 2087
-- Name: billservice_addonservicetransaction_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_addonservicetransaction_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_addonservicetransaction_id_seq OWNER TO ebs;

--
-- TOC entry 3167 (class 0 OID 0)
-- Dependencies: 2086
-- Name: billservice_addonservicetransaction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_addonservicetransaction_id_seq OWNED BY billservice_addonservicetransaction.id;


--
-- TOC entry 3168 (class 0 OID 0)
-- Dependencies: 2086
-- Name: billservice_addonservicetransaction_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_addonservicetransaction_id_seq', 1, false);


--
-- TOC entry 1971 (class 1259 OID 4630870)
-- Dependencies: 6 1970
-- Name: billservice_bankdata_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_bankdata_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_bankdata_id_seq OWNER TO ebs;

--
-- TOC entry 3169 (class 0 OID 0)
-- Dependencies: 1971
-- Name: billservice_bankdata_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_bankdata_id_seq OWNED BY billservice_bankdata.id;


--
-- TOC entry 3170 (class 0 OID 0)
-- Dependencies: 1971
-- Name: billservice_bankdata_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_bankdata_id_seq', 1, false);


--
-- TOC entry 1973 (class 1259 OID 4630882)
-- Dependencies: 1972 6
-- Name: billservice_card_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_card_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_card_id_seq OWNER TO ebs;

--
-- TOC entry 3171 (class 0 OID 0)
-- Dependencies: 1973
-- Name: billservice_card_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_card_id_seq OWNED BY billservice_card.id;


--
-- TOC entry 3172 (class 0 OID 0)
-- Dependencies: 1973
-- Name: billservice_card_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_card_id_seq', 1, false);


--
-- TOC entry 1975 (class 1259 OID 4630892)
-- Dependencies: 1974 6
-- Name: billservice_dealer_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_dealer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_dealer_id_seq OWNER TO ebs;

--
-- TOC entry 3173 (class 0 OID 0)
-- Dependencies: 1975
-- Name: billservice_dealer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_dealer_id_seq OWNED BY billservice_dealer.id;


--
-- TOC entry 3174 (class 0 OID 0)
-- Dependencies: 1975
-- Name: billservice_dealer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_dealer_id_seq', 1, false);


--
-- TOC entry 1977 (class 1259 OID 4630897)
-- Dependencies: 1976 6
-- Name: billservice_dealerpay_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_dealerpay_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_dealerpay_id_seq OWNER TO ebs;

--
-- TOC entry 3175 (class 0 OID 0)
-- Dependencies: 1977
-- Name: billservice_dealerpay_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_dealerpay_id_seq OWNED BY billservice_dealerpay.id;


--
-- TOC entry 3176 (class 0 OID 0)
-- Dependencies: 1977
-- Name: billservice_dealerpay_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_dealerpay_id_seq', 1, false);


--
-- TOC entry 1979 (class 1259 OID 4630905)
-- Dependencies: 1978 6
-- Name: billservice_document_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_document_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_document_id_seq OWNER TO ebs;

--
-- TOC entry 3177 (class 0 OID 0)
-- Dependencies: 1979
-- Name: billservice_document_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_document_id_seq OWNED BY billservice_document.id;


--
-- TOC entry 3178 (class 0 OID 0)
-- Dependencies: 1979
-- Name: billservice_document_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_document_id_seq', 1, false);


--
-- TOC entry 1981 (class 1259 OID 4630910)
-- Dependencies: 6 1980
-- Name: billservice_documenttype_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_documenttype_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_documenttype_id_seq OWNER TO ebs;

--
-- TOC entry 3179 (class 0 OID 0)
-- Dependencies: 1981
-- Name: billservice_documenttype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_documenttype_id_seq OWNED BY billservice_documenttype.id;


--
-- TOC entry 3180 (class 0 OID 0)
-- Dependencies: 1981
-- Name: billservice_documenttype_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_documenttype_id_seq', 8, true);


--
-- TOC entry 1983 (class 1259 OID 4630920)
-- Dependencies: 1982 6
-- Name: billservice_globalstat_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_globalstat_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_globalstat_id_seq OWNER TO ebs;

--
-- TOC entry 3181 (class 0 OID 0)
-- Dependencies: 1983
-- Name: billservice_globalstat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_globalstat_id_seq OWNED BY billservice_globalstat.id;


--
-- TOC entry 3182 (class 0 OID 0)
-- Dependencies: 1983
-- Name: billservice_globalstat_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_globalstat_id_seq', 1, false);


--
-- TOC entry 1985 (class 1259 OID 4630925)
-- Dependencies: 6 1984
-- Name: billservice_group_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_group_id_seq OWNER TO ebs;

--
-- TOC entry 3183 (class 0 OID 0)
-- Dependencies: 1985
-- Name: billservice_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_group_id_seq OWNED BY billservice_group.id;


--
-- TOC entry 3184 (class 0 OID 0)
-- Dependencies: 1985
-- Name: billservice_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_group_id_seq', 1, false);


--
-- TOC entry 1987 (class 1259 OID 4630930)
-- Dependencies: 1986 6
-- Name: billservice_group_trafficclass_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_group_trafficclass_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_group_trafficclass_id_seq OWNER TO ebs;

--
-- TOC entry 3185 (class 0 OID 0)
-- Dependencies: 1987
-- Name: billservice_group_trafficclass_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_group_trafficclass_id_seq OWNED BY billservice_group_trafficclass.id;


--
-- TOC entry 3186 (class 0 OID 0)
-- Dependencies: 1987
-- Name: billservice_group_trafficclass_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_group_trafficclass_id_seq', 1, false);


--
-- TOC entry 1988 (class 1259 OID 4630932)
-- Dependencies: 1937 6
-- Name: billservice_groupstat_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_groupstat_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_groupstat_id_seq OWNER TO ebs;

--
-- TOC entry 3187 (class 0 OID 0)
-- Dependencies: 1988
-- Name: billservice_groupstat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_groupstat_id_seq OWNED BY billservice_groupstat.id;


--
-- TOC entry 3188 (class 0 OID 0)
-- Dependencies: 1988
-- Name: billservice_groupstat_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_groupstat_id_seq', 1, false);


--
-- TOC entry 1990 (class 1259 OID 4630937)
-- Dependencies: 6 1989
-- Name: billservice_ipinuse_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_ipinuse_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_ipinuse_id_seq OWNER TO ebs;

--
-- TOC entry 3189 (class 0 OID 0)
-- Dependencies: 1990
-- Name: billservice_ipinuse_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_ipinuse_id_seq OWNED BY billservice_ipinuse.id;


--
-- TOC entry 3190 (class 0 OID 0)
-- Dependencies: 1990
-- Name: billservice_ipinuse_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_ipinuse_id_seq', 6, true);


--
-- TOC entry 1992 (class 1259 OID 4630945)
-- Dependencies: 6 1991
-- Name: billservice_ippool_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_ippool_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_ippool_id_seq OWNER TO ebs;

--
-- TOC entry 3191 (class 0 OID 0)
-- Dependencies: 1992
-- Name: billservice_ippool_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_ippool_id_seq OWNED BY billservice_ippool.id;


--
-- TOC entry 3192 (class 0 OID 0)
-- Dependencies: 1992
-- Name: billservice_ippool_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_ippool_id_seq', 1, true);


--
-- TOC entry 1993 (class 1259 OID 4630947)
-- Dependencies: 6 1938
-- Name: billservice_netflowstream_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_netflowstream_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_netflowstream_id_seq OWNER TO ebs;

--
-- TOC entry 3193 (class 0 OID 0)
-- Dependencies: 1993
-- Name: billservice_netflowstream_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_netflowstream_id_seq OWNED BY billservice_netflowstream.id;


--
-- TOC entry 3194 (class 0 OID 0)
-- Dependencies: 1993
-- Name: billservice_netflowstream_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_netflowstream_id_seq', 1, false);


--
-- TOC entry 1995 (class 1259 OID 4630952)
-- Dependencies: 1994 6
-- Name: billservice_onetimeservice_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_onetimeservice_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_onetimeservice_id_seq OWNER TO ebs;

--
-- TOC entry 3195 (class 0 OID 0)
-- Dependencies: 1995
-- Name: billservice_onetimeservice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_onetimeservice_id_seq OWNED BY billservice_onetimeservice.id;


--
-- TOC entry 3196 (class 0 OID 0)
-- Dependencies: 1995
-- Name: billservice_onetimeservice_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_onetimeservice_id_seq', 1, false);


--
-- TOC entry 1997 (class 1259 OID 4630957)
-- Dependencies: 1996 6
-- Name: billservice_onetimeservicehistory_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_onetimeservicehistory_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_onetimeservicehistory_id_seq OWNER TO ebs;

--
-- TOC entry 3197 (class 0 OID 0)
-- Dependencies: 1997
-- Name: billservice_onetimeservicehistory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_onetimeservicehistory_id_seq OWNED BY billservice_onetimeservicehistory.id;


--
-- TOC entry 3198 (class 0 OID 0)
-- Dependencies: 1997
-- Name: billservice_onetimeservicehistory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_onetimeservicehistory_id_seq', 1, false);


--
-- TOC entry 1999 (class 1259 OID 4630965)
-- Dependencies: 6 1998
-- Name: billservice_operator_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_operator_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_operator_id_seq OWNER TO ebs;

--
-- TOC entry 3199 (class 0 OID 0)
-- Dependencies: 1999
-- Name: billservice_operator_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_operator_id_seq OWNED BY billservice_operator.id;


--
-- TOC entry 3200 (class 0 OID 0)
-- Dependencies: 1999
-- Name: billservice_operator_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_operator_id_seq', 1, false);


--
-- TOC entry 2001 (class 1259 OID 4630979)
-- Dependencies: 6 2000
-- Name: billservice_organization_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_organization_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_organization_id_seq OWNER TO ebs;

--
-- TOC entry 3201 (class 0 OID 0)
-- Dependencies: 2001
-- Name: billservice_organization_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_organization_id_seq OWNED BY billservice_organization.id;


--
-- TOC entry 3202 (class 0 OID 0)
-- Dependencies: 2001
-- Name: billservice_organization_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_organization_id_seq', 1, false);


--
-- TOC entry 2003 (class 1259 OID 4630988)
-- Dependencies: 6 2002
-- Name: billservice_periodicalservice_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_periodicalservice_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_periodicalservice_id_seq OWNER TO ebs;

--
-- TOC entry 3203 (class 0 OID 0)
-- Dependencies: 2003
-- Name: billservice_periodicalservice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_periodicalservice_id_seq OWNED BY billservice_periodicalservice.id;


--
-- TOC entry 3204 (class 0 OID 0)
-- Dependencies: 2003
-- Name: billservice_periodicalservice_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_periodicalservice_id_seq', 1, false);


--
-- TOC entry 2004 (class 1259 OID 4630990)
-- Dependencies: 1940 6
-- Name: billservice_periodicalservicehistory_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_periodicalservicehistory_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_periodicalservicehistory_id_seq OWNER TO ebs;

--
-- TOC entry 3205 (class 0 OID 0)
-- Dependencies: 2004
-- Name: billservice_periodicalservicehistory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_periodicalservicehistory_id_seq OWNED BY billservice_periodicalservicehistory.id;


--
-- TOC entry 3206 (class 0 OID 0)
-- Dependencies: 2004
-- Name: billservice_periodicalservicehistory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_periodicalservicehistory_id_seq', 1, false);


--
-- TOC entry 2006 (class 1259 OID 4630997)
-- Dependencies: 2005 6
-- Name: billservice_ports_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_ports_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_ports_id_seq OWNER TO ebs;

--
-- TOC entry 3207 (class 0 OID 0)
-- Dependencies: 2006
-- Name: billservice_ports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_ports_id_seq OWNED BY billservice_ports.id;


--
-- TOC entry 3208 (class 0 OID 0)
-- Dependencies: 2006
-- Name: billservice_ports_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_ports_id_seq', 45174, true);


--
-- TOC entry 2008 (class 1259 OID 4631003)
-- Dependencies: 2007 6
-- Name: billservice_prepaidtraffic_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_prepaidtraffic_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_prepaidtraffic_id_seq OWNER TO ebs;

--
-- TOC entry 3209 (class 0 OID 0)
-- Dependencies: 2008
-- Name: billservice_prepaidtraffic_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_prepaidtraffic_id_seq OWNED BY billservice_prepaidtraffic.id;


--
-- TOC entry 3210 (class 0 OID 0)
-- Dependencies: 2008
-- Name: billservice_prepaidtraffic_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_prepaidtraffic_id_seq', 1, false);


--
-- TOC entry 2076 (class 1259 OID 4632562)
-- Dependencies: 2077 6
-- Name: billservice_radiusattrs_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_radiusattrs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_radiusattrs_id_seq OWNER TO ebs;

--
-- TOC entry 3211 (class 0 OID 0)
-- Dependencies: 2076
-- Name: billservice_radiusattrs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_radiusattrs_id_seq OWNED BY billservice_radiusattrs.id;


--
-- TOC entry 3212 (class 0 OID 0)
-- Dependencies: 2076
-- Name: billservice_radiusattrs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_radiusattrs_id_seq', 1, false);


--
-- TOC entry 2011 (class 1259 OID 4631011)
-- Dependencies: 6 2010
-- Name: billservice_salecard_cards_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_salecard_cards_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_salecard_cards_id_seq OWNER TO ebs;

--
-- TOC entry 3213 (class 0 OID 0)
-- Dependencies: 2011
-- Name: billservice_salecard_cards_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_salecard_cards_id_seq OWNED BY billservice_salecard_cards.id;


--
-- TOC entry 3214 (class 0 OID 0)
-- Dependencies: 2011
-- Name: billservice_salecard_cards_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_salecard_cards_id_seq', 1, false);


--
-- TOC entry 2012 (class 1259 OID 4631013)
-- Dependencies: 6 2009
-- Name: billservice_salecard_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_salecard_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_salecard_id_seq OWNER TO ebs;

--
-- TOC entry 3215 (class 0 OID 0)
-- Dependencies: 2012
-- Name: billservice_salecard_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_salecard_id_seq OWNED BY billservice_salecard.id;


--
-- TOC entry 3216 (class 0 OID 0)
-- Dependencies: 2012
-- Name: billservice_salecard_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_salecard_id_seq', 1, false);


--
-- TOC entry 2014 (class 1259 OID 4631023)
-- Dependencies: 6 2013
-- Name: billservice_settlementperiod_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_settlementperiod_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_settlementperiod_id_seq OWNER TO ebs;

--
-- TOC entry 3217 (class 0 OID 0)
-- Dependencies: 2014
-- Name: billservice_settlementperiod_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_settlementperiod_id_seq OWNED BY billservice_settlementperiod.id;


--
-- TOC entry 3218 (class 0 OID 0)
-- Dependencies: 2014
-- Name: billservice_settlementperiod_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_settlementperiod_id_seq', 1, true);


--
-- TOC entry 2016 (class 1259 OID 4631028)
-- Dependencies: 6 2015
-- Name: billservice_shedulelog_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE billservice_shedulelog_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_shedulelog_id_seq OWNER TO postgres;

--
-- TOC entry 3219 (class 0 OID 0)
-- Dependencies: 2016
-- Name: billservice_shedulelog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE billservice_shedulelog_id_seq OWNED BY billservice_shedulelog.id;


--
-- TOC entry 3220 (class 0 OID 0)
-- Dependencies: 2016
-- Name: billservice_shedulelog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('billservice_shedulelog_id_seq', 3, true);


--
-- TOC entry 2018 (class 1259 OID 4631033)
-- Dependencies: 6 2017
-- Name: billservice_speedlimit_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_speedlimit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_speedlimit_id_seq OWNER TO ebs;

--
-- TOC entry 3221 (class 0 OID 0)
-- Dependencies: 2018
-- Name: billservice_speedlimit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_speedlimit_id_seq OWNED BY billservice_speedlimit.id;


--
-- TOC entry 3222 (class 0 OID 0)
-- Dependencies: 2018
-- Name: billservice_speedlimit_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_speedlimit_id_seq', 1, false);


--
-- TOC entry 2020 (class 1259 OID 4631038)
-- Dependencies: 2019 6
-- Name: billservice_suspendedperiod_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_suspendedperiod_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_suspendedperiod_id_seq OWNER TO ebs;

--
-- TOC entry 3223 (class 0 OID 0)
-- Dependencies: 2020
-- Name: billservice_suspendedperiod_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_suspendedperiod_id_seq OWNED BY billservice_suspendedperiod.id;


--
-- TOC entry 3224 (class 0 OID 0)
-- Dependencies: 2020
-- Name: billservice_suspendedperiod_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_suspendedperiod_id_seq', 1, false);


--
-- TOC entry 2022 (class 1259 OID 4631050)
-- Dependencies: 6 2021
-- Name: billservice_systemuser_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_systemuser_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_systemuser_id_seq OWNER TO ebs;

--
-- TOC entry 3225 (class 0 OID 0)
-- Dependencies: 2022
-- Name: billservice_systemuser_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_systemuser_id_seq OWNED BY billservice_systemuser.id;


--
-- TOC entry 3226 (class 0 OID 0)
-- Dependencies: 2022
-- Name: billservice_systemuser_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_systemuser_id_seq', 3, true);


--
-- TOC entry 2023 (class 1259 OID 4631052)
-- Dependencies: 1939 6
-- Name: billservice_tariff_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_tariff_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_tariff_id_seq OWNER TO ebs;

--
-- TOC entry 3227 (class 0 OID 0)
-- Dependencies: 2023
-- Name: billservice_tariff_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_tariff_id_seq OWNED BY billservice_tariff.id;


--
-- TOC entry 3228 (class 0 OID 0)
-- Dependencies: 2023
-- Name: billservice_tariff_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_tariff_id_seq', 4, true);


--
-- TOC entry 2025 (class 1259 OID 4631060)
-- Dependencies: 6 2024
-- Name: billservice_template_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_template_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_template_id_seq OWNER TO ebs;

--
-- TOC entry 3229 (class 0 OID 0)
-- Dependencies: 2025
-- Name: billservice_template_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_template_id_seq OWNED BY billservice_template.id;


--
-- TOC entry 3230 (class 0 OID 0)
-- Dependencies: 2025
-- Name: billservice_template_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_template_id_seq', 1, false);


--
-- TOC entry 2027 (class 1259 OID 4631066)
-- Dependencies: 6 2026
-- Name: billservice_timeaccessnode_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_timeaccessnode_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_timeaccessnode_id_seq OWNER TO ebs;

--
-- TOC entry 3231 (class 0 OID 0)
-- Dependencies: 2027
-- Name: billservice_timeaccessnode_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_timeaccessnode_id_seq OWNED BY billservice_timeaccessnode.id;


--
-- TOC entry 3232 (class 0 OID 0)
-- Dependencies: 2027
-- Name: billservice_timeaccessnode_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_timeaccessnode_id_seq', 1, false);


--
-- TOC entry 2029 (class 1259 OID 4631073)
-- Dependencies: 2028 6
-- Name: billservice_timeaccessservice_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_timeaccessservice_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_timeaccessservice_id_seq OWNER TO ebs;

--
-- TOC entry 3233 (class 0 OID 0)
-- Dependencies: 2029
-- Name: billservice_timeaccessservice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_timeaccessservice_id_seq OWNED BY billservice_timeaccessservice.id;


--
-- TOC entry 3234 (class 0 OID 0)
-- Dependencies: 2029
-- Name: billservice_timeaccessservice_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_timeaccessservice_id_seq', 1, false);


--
-- TOC entry 2031 (class 1259 OID 4631078)
-- Dependencies: 2030 6
-- Name: billservice_timeperiod_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_timeperiod_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_timeperiod_id_seq OWNER TO ebs;

--
-- TOC entry 3235 (class 0 OID 0)
-- Dependencies: 2031
-- Name: billservice_timeperiod_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_timeperiod_id_seq OWNED BY billservice_timeperiod.id;


--
-- TOC entry 3236 (class 0 OID 0)
-- Dependencies: 2031
-- Name: billservice_timeperiod_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_timeperiod_id_seq', 6, true);


--
-- TOC entry 2033 (class 1259 OID 4631083)
-- Dependencies: 2032 6
-- Name: billservice_timeperiod_time_period_nodes_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_timeperiod_time_period_nodes_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_timeperiod_time_period_nodes_id_seq OWNER TO ebs;

--
-- TOC entry 3237 (class 0 OID 0)
-- Dependencies: 2033
-- Name: billservice_timeperiod_time_period_nodes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_timeperiod_time_period_nodes_id_seq OWNED BY billservice_timeperiod_time_period_nodes.id;


--
-- TOC entry 3238 (class 0 OID 0)
-- Dependencies: 2033
-- Name: billservice_timeperiod_time_period_nodes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_timeperiod_time_period_nodes_id_seq', 11, true);


--
-- TOC entry 2035 (class 1259 OID 4631093)
-- Dependencies: 2034 6
-- Name: billservice_timeperiodnode_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_timeperiodnode_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_timeperiodnode_id_seq OWNER TO ebs;

--
-- TOC entry 3239 (class 0 OID 0)
-- Dependencies: 2035
-- Name: billservice_timeperiodnode_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_timeperiodnode_id_seq OWNED BY billservice_timeperiodnode.id;


--
-- TOC entry 3240 (class 0 OID 0)
-- Dependencies: 2035
-- Name: billservice_timeperiodnode_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_timeperiodnode_id_seq', 11, true);


--
-- TOC entry 2037 (class 1259 OID 4631104)
-- Dependencies: 2036 6
-- Name: billservice_timespeed_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_timespeed_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_timespeed_id_seq OWNER TO ebs;

--
-- TOC entry 3241 (class 0 OID 0)
-- Dependencies: 2037
-- Name: billservice_timespeed_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_timespeed_id_seq OWNED BY billservice_timespeed.id;


--
-- TOC entry 3242 (class 0 OID 0)
-- Dependencies: 2037
-- Name: billservice_timespeed_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_timespeed_id_seq', 1, false);


--
-- TOC entry 2072 (class 1259 OID 4632060)
-- Dependencies: 2073 6
-- Name: billservice_timetransaction_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_timetransaction_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_timetransaction_id_seq OWNER TO ebs;

--
-- TOC entry 3243 (class 0 OID 0)
-- Dependencies: 2072
-- Name: billservice_timetransaction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_timetransaction_id_seq OWNED BY billservice_timetransaction.id;


--
-- TOC entry 3244 (class 0 OID 0)
-- Dependencies: 2072
-- Name: billservice_timetransaction_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_timetransaction_id_seq', 1, false);


--
-- TOC entry 2074 (class 1259 OID 4632148)
-- Dependencies: 2075 6
-- Name: billservice_tpchangerule_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_tpchangerule_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_tpchangerule_id_seq OWNER TO ebs;

--
-- TOC entry 3245 (class 0 OID 0)
-- Dependencies: 2074
-- Name: billservice_tpchangerule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_tpchangerule_id_seq OWNED BY billservice_tpchangerule.id;


--
-- TOC entry 3246 (class 0 OID 0)
-- Dependencies: 2074
-- Name: billservice_tpchangerule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_tpchangerule_id_seq', 1, false);


--
-- TOC entry 2039 (class 1259 OID 4631109)
-- Dependencies: 2038 6
-- Name: billservice_trafficlimit_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_trafficlimit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_trafficlimit_id_seq OWNER TO ebs;

--
-- TOC entry 3247 (class 0 OID 0)
-- Dependencies: 2039
-- Name: billservice_trafficlimit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_trafficlimit_id_seq OWNED BY billservice_trafficlimit.id;


--
-- TOC entry 3248 (class 0 OID 0)
-- Dependencies: 2039
-- Name: billservice_trafficlimit_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_trafficlimit_id_seq', 1, false);


--
-- TOC entry 2041 (class 1259 OID 4631114)
-- Dependencies: 6 2040
-- Name: billservice_trafficlimit_traffic_class_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_trafficlimit_traffic_class_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_trafficlimit_traffic_class_id_seq OWNER TO ebs;

--
-- TOC entry 3249 (class 0 OID 0)
-- Dependencies: 2041
-- Name: billservice_trafficlimit_traffic_class_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_trafficlimit_traffic_class_id_seq OWNED BY billservice_trafficlimit_traffic_class.id;


--
-- TOC entry 3250 (class 0 OID 0)
-- Dependencies: 2041
-- Name: billservice_trafficlimit_traffic_class_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_trafficlimit_traffic_class_id_seq', 1, false);


--
-- TOC entry 2070 (class 1259 OID 4632037)
-- Dependencies: 2071 6
-- Name: billservice_traffictransaction_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_traffictransaction_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_traffictransaction_id_seq OWNER TO ebs;

--
-- TOC entry 3251 (class 0 OID 0)
-- Dependencies: 2070
-- Name: billservice_traffictransaction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_traffictransaction_id_seq OWNED BY billservice_traffictransaction.id;


--
-- TOC entry 3252 (class 0 OID 0)
-- Dependencies: 2070
-- Name: billservice_traffictransaction_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_traffictransaction_id_seq', 1, false);


--
-- TOC entry 2043 (class 1259 OID 4631122)
-- Dependencies: 6 2042
-- Name: billservice_traffictransmitnodes_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_traffictransmitnodes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_traffictransmitnodes_id_seq OWNER TO ebs;

--
-- TOC entry 3253 (class 0 OID 0)
-- Dependencies: 2043
-- Name: billservice_traffictransmitnodes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_traffictransmitnodes_id_seq OWNED BY billservice_traffictransmitnodes.id;


--
-- TOC entry 3254 (class 0 OID 0)
-- Dependencies: 2043
-- Name: billservice_traffictransmitnodes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_traffictransmitnodes_id_seq', 1, false);


--
-- TOC entry 2045 (class 1259 OID 4631127)
-- Dependencies: 6 2044
-- Name: billservice_traffictransmitnodes_time_nodes_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_traffictransmitnodes_time_nodes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_traffictransmitnodes_time_nodes_id_seq OWNER TO ebs;

--
-- TOC entry 3255 (class 0 OID 0)
-- Dependencies: 2045
-- Name: billservice_traffictransmitnodes_time_nodes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_traffictransmitnodes_time_nodes_id_seq OWNED BY billservice_traffictransmitnodes_time_nodes.id;


--
-- TOC entry 3256 (class 0 OID 0)
-- Dependencies: 2045
-- Name: billservice_traffictransmitnodes_time_nodes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_traffictransmitnodes_time_nodes_id_seq', 1, false);


--
-- TOC entry 2047 (class 1259 OID 4631132)
-- Dependencies: 6 2046
-- Name: billservice_traffictransmitnodes_traffic_class_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_traffictransmitnodes_traffic_class_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_traffictransmitnodes_traffic_class_id_seq OWNER TO ebs;

--
-- TOC entry 3257 (class 0 OID 0)
-- Dependencies: 2047
-- Name: billservice_traffictransmitnodes_traffic_class_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_traffictransmitnodes_traffic_class_id_seq OWNED BY billservice_traffictransmitnodes_traffic_class.id;


--
-- TOC entry 3258 (class 0 OID 0)
-- Dependencies: 2047
-- Name: billservice_traffictransmitnodes_traffic_class_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_traffictransmitnodes_traffic_class_id_seq', 1, false);


--
-- TOC entry 2049 (class 1259 OID 4631140)
-- Dependencies: 6 2048
-- Name: billservice_traffictransmitservice_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_traffictransmitservice_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_traffictransmitservice_id_seq OWNER TO ebs;

--
-- TOC entry 3259 (class 0 OID 0)
-- Dependencies: 2049
-- Name: billservice_traffictransmitservice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_traffictransmitservice_id_seq OWNED BY billservice_traffictransmitservice.id;


--
-- TOC entry 3260 (class 0 OID 0)
-- Dependencies: 2049
-- Name: billservice_traffictransmitservice_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_traffictransmitservice_id_seq', 1, false);


--
-- TOC entry 2051 (class 1259 OID 4631148)
-- Dependencies: 2050 6
-- Name: billservice_transaction_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_transaction_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_transaction_id_seq OWNER TO ebs;

--
-- TOC entry 3261 (class 0 OID 0)
-- Dependencies: 2051
-- Name: billservice_transaction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_transaction_id_seq OWNED BY billservice_transaction.id;


--
-- TOC entry 3262 (class 0 OID 0)
-- Dependencies: 2051
-- Name: billservice_transaction_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_transaction_id_seq', 1, true);


--
-- TOC entry 2053 (class 1259 OID 4631153)
-- Dependencies: 6 2052
-- Name: billservice_transactiontype_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_transactiontype_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_transactiontype_id_seq OWNER TO ebs;

--
-- TOC entry 3263 (class 0 OID 0)
-- Dependencies: 2053
-- Name: billservice_transactiontype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_transactiontype_id_seq OWNED BY billservice_transactiontype.id;


--
-- TOC entry 3264 (class 0 OID 0)
-- Dependencies: 2053
-- Name: billservice_transactiontype_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_transactiontype_id_seq', 18, true);


--
-- TOC entry 2078 (class 1259 OID 4632660)
-- Dependencies: 6 2079
-- Name: billservice_x8021_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE billservice_x8021_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.billservice_x8021_id_seq OWNER TO ebs;

--
-- TOC entry 3265 (class 0 OID 0)
-- Dependencies: 2078
-- Name: billservice_x8021_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE billservice_x8021_id_seq OWNED BY billservice_x8021.id;


--
-- TOC entry 3266 (class 0 OID 0)
-- Dependencies: 2078
-- Name: billservice_x8021_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('billservice_x8021_id_seq', 1, false);


--
-- TOC entry 2055 (class 1259 OID 4631162)
-- Dependencies: 6 2054
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.django_admin_log_id_seq OWNER TO ebs;

--
-- TOC entry 3267 (class 0 OID 0)
-- Dependencies: 2055
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE django_admin_log_id_seq OWNED BY django_admin_log.id;


--
-- TOC entry 3268 (class 0 OID 0)
-- Dependencies: 2055
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('django_admin_log_id_seq', 1, false);


--
-- TOC entry 2057 (class 1259 OID 4631167)
-- Dependencies: 2056 6
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE django_content_type_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.django_content_type_id_seq OWNER TO ebs;

--
-- TOC entry 3269 (class 0 OID 0)
-- Dependencies: 2057
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE django_content_type_id_seq OWNED BY django_content_type.id;


--
-- TOC entry 3270 (class 0 OID 0)
-- Dependencies: 2057
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('django_content_type_id_seq', 60, true);


--
-- TOC entry 2060 (class 1259 OID 4631178)
-- Dependencies: 2059 6
-- Name: django_site_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE django_site_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.django_site_id_seq OWNER TO ebs;

--
-- TOC entry 3271 (class 0 OID 0)
-- Dependencies: 2060
-- Name: django_site_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE django_site_id_seq OWNED BY django_site.id;


--
-- TOC entry 3272 (class 0 OID 0)
-- Dependencies: 2060
-- Name: django_site_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('django_site_id_seq', 2, true);


--
-- TOC entry 2062 (class 1259 OID 4631196)
-- Dependencies: 2061 6
-- Name: nas_nas_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE nas_nas_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.nas_nas_id_seq OWNER TO ebs;

--
-- TOC entry 3273 (class 0 OID 0)
-- Dependencies: 2062
-- Name: nas_nas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE nas_nas_id_seq OWNED BY nas_nas.id;


--
-- TOC entry 3274 (class 0 OID 0)
-- Dependencies: 2062
-- Name: nas_nas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('nas_nas_id_seq', 1, true);


--
-- TOC entry 2064 (class 1259 OID 4631204)
-- Dependencies: 6 2063
-- Name: nas_trafficclass_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE nas_trafficclass_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.nas_trafficclass_id_seq OWNER TO ebs;

--
-- TOC entry 3275 (class 0 OID 0)
-- Dependencies: 2064
-- Name: nas_trafficclass_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE nas_trafficclass_id_seq OWNED BY nas_trafficclass.id;


--
-- TOC entry 3276 (class 0 OID 0)
-- Dependencies: 2064
-- Name: nas_trafficclass_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('nas_trafficclass_id_seq', 1, false);


--
-- TOC entry 2066 (class 1259 OID 4631218)
-- Dependencies: 6 2065
-- Name: nas_trafficnode_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE nas_trafficnode_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.nas_trafficnode_id_seq OWNER TO ebs;

--
-- TOC entry 3277 (class 0 OID 0)
-- Dependencies: 2066
-- Name: nas_trafficnode_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE nas_trafficnode_id_seq OWNED BY nas_trafficnode.id;


--
-- TOC entry 3278 (class 0 OID 0)
-- Dependencies: 2066
-- Name: nas_trafficnode_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('nas_trafficnode_id_seq', 1, false);


--
-- TOC entry 2068 (class 1259 OID 4631230)
-- Dependencies: 6 2067
-- Name: radius_activesession_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE radius_activesession_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.radius_activesession_id_seq OWNER TO ebs;

--
-- TOC entry 3279 (class 0 OID 0)
-- Dependencies: 2068
-- Name: radius_activesession_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE radius_activesession_id_seq OWNED BY radius_activesession.id;


--
-- TOC entry 3280 (class 0 OID 0)
-- Dependencies: 2068
-- Name: radius_activesession_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('radius_activesession_id_seq', 1, false);


--
-- TOC entry 2069 (class 1259 OID 4631232)
-- Dependencies: 1941 6
-- Name: radius_session_id_seq; Type: SEQUENCE; Schema: public; Owner: ebs
--

CREATE SEQUENCE radius_session_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.radius_session_id_seq OWNER TO ebs;

--
-- TOC entry 3281 (class 0 OID 0)
-- Dependencies: 2069
-- Name: radius_session_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ebs
--

ALTER SEQUENCE radius_session_id_seq OWNED BY radius_session.id;


--
-- TOC entry 3282 (class 0 OID 0)
-- Dependencies: 2069
-- Name: radius_session_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ebs
--

SELECT pg_catalog.setval('radius_session_id_seq', 1, false);


--
-- TOC entry 2380 (class 2604 OID 4631235)
-- Dependencies: 1943 1942
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE auth_group ALTER COLUMN id SET DEFAULT nextval('auth_group_id_seq'::regclass);


--
-- TOC entry 2381 (class 2604 OID 4631236)
-- Dependencies: 1945 1944
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('auth_group_permissions_id_seq'::regclass);


--
-- TOC entry 2382 (class 2604 OID 4631237)
-- Dependencies: 1947 1946
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE auth_message ALTER COLUMN id SET DEFAULT nextval('auth_message_id_seq'::regclass);


--
-- TOC entry 2383 (class 2604 OID 4631238)
-- Dependencies: 1949 1948
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE auth_permission ALTER COLUMN id SET DEFAULT nextval('auth_permission_id_seq'::regclass);


--
-- TOC entry 2384 (class 2604 OID 4631239)
-- Dependencies: 1953 1950
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE auth_user ALTER COLUMN id SET DEFAULT nextval('auth_user_id_seq'::regclass);


--
-- TOC entry 2385 (class 2604 OID 4631240)
-- Dependencies: 1952 1951
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE auth_user_groups ALTER COLUMN id SET DEFAULT nextval('auth_user_groups_id_seq'::regclass);


--
-- TOC entry 2386 (class 2604 OID 4631241)
-- Dependencies: 1955 1954
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE auth_user_user_permissions ALTER COLUMN id SET DEFAULT nextval('auth_user_user_permissions_id_seq'::regclass);


--
-- TOC entry 2394 (class 2604 OID 4631242)
-- Dependencies: 1957 1956
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_accessparameters ALTER COLUMN id SET DEFAULT nextval('billservice_accessparameters_id_seq'::regclass);


--
-- TOC entry 2433 (class 2604 OID 4631243)
-- Dependencies: 1959 1958
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_account ALTER COLUMN id SET DEFAULT nextval('billservice_account_id_seq'::regclass);


--
-- TOC entry 2604 (class 2604 OID 4632771)
-- Dependencies: 2084 2085 2085
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_accountaddonservice ALTER COLUMN id SET DEFAULT nextval('billservice_accountaddonservice_id_seq'::regclass);


--
-- TOC entry 2445 (class 2604 OID 4631244)
-- Dependencies: 1961 1960
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_accountipnspeed ALTER COLUMN id SET DEFAULT nextval('billservice_accountipnspeed_id_seq'::regclass);


--
-- TOC entry 2448 (class 2604 OID 4631245)
-- Dependencies: 1963 1962
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_accountprepaystime ALTER COLUMN id SET DEFAULT nextval('billservice_accountprepaystime_id_seq'::regclass);


--
-- TOC entry 2450 (class 2604 OID 4631246)
-- Dependencies: 1965 1964
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_accountprepaystrafic ALTER COLUMN id SET DEFAULT nextval('billservice_accountprepaystrafic_id_seq'::regclass);


--
-- TOC entry 2452 (class 2604 OID 4631247)
-- Dependencies: 1967 1966
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_accountspeedlimit ALTER COLUMN id SET DEFAULT nextval('billservice_accountspeedlimit_id_seq'::regclass);


--
-- TOC entry 2453 (class 2604 OID 4631248)
-- Dependencies: 1969 1968
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_accounttarif ALTER COLUMN id SET DEFAULT nextval('billservice_accounttarif_id_seq'::regclass);


--
-- TOC entry 2578 (class 2604 OID 4632697)
-- Dependencies: 2081 2080 2081
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_addonservice ALTER COLUMN id SET DEFAULT nextval('billservice_addonservice_id_seq'::regclass);


--
-- TOC entry 2602 (class 2604 OID 4632744)
-- Dependencies: 2083 2082 2083
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_addonservicetarif ALTER COLUMN id SET DEFAULT nextval('billservice_addonservicetarif_id_seq'::regclass);


--
-- TOC entry 2607 (class 2604 OID 4632794)
-- Dependencies: 2087 2086 2087
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_addonservicetransaction ALTER COLUMN id SET DEFAULT nextval('billservice_addonservicetransaction_id_seq'::regclass);


--
-- TOC entry 2455 (class 2604 OID 4631249)
-- Dependencies: 1971 1970
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_bankdata ALTER COLUMN id SET DEFAULT nextval('billservice_bankdata_id_seq'::regclass);


--
-- TOC entry 2463 (class 2604 OID 4631250)
-- Dependencies: 1973 1972
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_card ALTER COLUMN id SET DEFAULT nextval('billservice_card_id_seq'::regclass);


--
-- TOC entry 2467 (class 2604 OID 4631251)
-- Dependencies: 1975 1974
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_dealer ALTER COLUMN id SET DEFAULT nextval('billservice_dealer_id_seq'::regclass);


--
-- TOC entry 2468 (class 2604 OID 4631252)
-- Dependencies: 1977 1976
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_dealerpay ALTER COLUMN id SET DEFAULT nextval('billservice_dealerpay_id_seq'::regclass);


--
-- TOC entry 2469 (class 2604 OID 4631253)
-- Dependencies: 1979 1978
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_document ALTER COLUMN id SET DEFAULT nextval('billservice_document_id_seq'::regclass);


--
-- TOC entry 2470 (class 2604 OID 4631254)
-- Dependencies: 1981 1980
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_documenttype ALTER COLUMN id SET DEFAULT nextval('billservice_documenttype_id_seq'::regclass);


--
-- TOC entry 2473 (class 2604 OID 4631255)
-- Dependencies: 1983 1982
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_globalstat ALTER COLUMN id SET DEFAULT nextval('billservice_globalstat_id_seq'::regclass);


--
-- TOC entry 2474 (class 2604 OID 4631256)
-- Dependencies: 1985 1984
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_group ALTER COLUMN id SET DEFAULT nextval('billservice_group_id_seq'::regclass);


--
-- TOC entry 2475 (class 2604 OID 4631257)
-- Dependencies: 1987 1986
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_group_trafficclass ALTER COLUMN id SET DEFAULT nextval('billservice_group_trafficclass_id_seq'::regclass);


--
-- TOC entry 2354 (class 2604 OID 4631180)
-- Dependencies: 1988 1937
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_groupstat ALTER COLUMN id SET DEFAULT nextval('billservice_groupstat_id_seq'::regclass);


--
-- TOC entry 2476 (class 2604 OID 4631258)
-- Dependencies: 1990 1989
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_ipinuse ALTER COLUMN id SET DEFAULT nextval('billservice_ipinuse_id_seq'::regclass);


--
-- TOC entry 2477 (class 2604 OID 4631259)
-- Dependencies: 1992 1991
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_ippool ALTER COLUMN id SET DEFAULT nextval('billservice_ippool_id_seq'::regclass);


--
-- TOC entry 2358 (class 2604 OID 4631220)
-- Dependencies: 1993 1938
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_netflowstream ALTER COLUMN id SET DEFAULT nextval('billservice_netflowstream_id_seq'::regclass);


--
-- TOC entry 2478 (class 2604 OID 4631260)
-- Dependencies: 1995 1994
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_onetimeservice ALTER COLUMN id SET DEFAULT nextval('billservice_onetimeservice_id_seq'::regclass);


--
-- TOC entry 2479 (class 2604 OID 4631261)
-- Dependencies: 1997 1996
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_onetimeservicehistory ALTER COLUMN id SET DEFAULT nextval('billservice_onetimeservicehistory_id_seq'::regclass);


--
-- TOC entry 2480 (class 2604 OID 4631262)
-- Dependencies: 1999 1998
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_operator ALTER COLUMN id SET DEFAULT nextval('billservice_operator_id_seq'::regclass);


--
-- TOC entry 2487 (class 2604 OID 4631263)
-- Dependencies: 2001 2000
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_organization ALTER COLUMN id SET DEFAULT nextval('billservice_organization_id_seq'::regclass);


--
-- TOC entry 2489 (class 2604 OID 4631264)
-- Dependencies: 2003 2002
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_periodicalservice ALTER COLUMN id SET DEFAULT nextval('billservice_periodicalservice_id_seq'::regclass);


--
-- TOC entry 2369 (class 2604 OID 4631221)
-- Dependencies: 2004 1940
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_periodicalservicehistory ALTER COLUMN id SET DEFAULT nextval('billservice_periodicalservicehistory_id_seq'::regclass);


--
-- TOC entry 2492 (class 2604 OID 4631265)
-- Dependencies: 2006 2005
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_ports ALTER COLUMN id SET DEFAULT nextval('billservice_ports_id_seq'::regclass);


--
-- TOC entry 2493 (class 2604 OID 4631266)
-- Dependencies: 2008 2007
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_prepaidtraffic ALTER COLUMN id SET DEFAULT nextval('billservice_prepaidtraffic_id_seq'::regclass);


--
-- TOC entry 2575 (class 2604 OID 4632567)
-- Dependencies: 2077 2076 2077
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_radiusattrs ALTER COLUMN id SET DEFAULT nextval('billservice_radiusattrs_id_seq'::regclass);


--
-- TOC entry 2495 (class 2604 OID 4631267)
-- Dependencies: 2012 2009
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_salecard ALTER COLUMN id SET DEFAULT nextval('billservice_salecard_id_seq'::regclass);


--
-- TOC entry 2496 (class 2604 OID 4631268)
-- Dependencies: 2011 2010
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_salecard_cards ALTER COLUMN id SET DEFAULT nextval('billservice_salecard_cards_id_seq'::regclass);


--
-- TOC entry 2499 (class 2604 OID 4631269)
-- Dependencies: 2014 2013
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_settlementperiod ALTER COLUMN id SET DEFAULT nextval('billservice_settlementperiod_id_seq'::regclass);


--
-- TOC entry 2500 (class 2604 OID 4631270)
-- Dependencies: 2016 2015
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE billservice_shedulelog ALTER COLUMN id SET DEFAULT nextval('billservice_shedulelog_id_seq'::regclass);


--
-- TOC entry 2501 (class 2604 OID 4631271)
-- Dependencies: 2018 2017
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_speedlimit ALTER COLUMN id SET DEFAULT nextval('billservice_speedlimit_id_seq'::regclass);


--
-- TOC entry 2504 (class 2604 OID 4631272)
-- Dependencies: 2020 2019
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_suspendedperiod ALTER COLUMN id SET DEFAULT nextval('billservice_suspendedperiod_id_seq'::regclass);


--
-- TOC entry 2509 (class 2604 OID 4631273)
-- Dependencies: 2022 2021
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_systemuser ALTER COLUMN id SET DEFAULT nextval('billservice_systemuser_id_seq'::regclass);


--
-- TOC entry 2365 (class 2604 OID 4631274)
-- Dependencies: 2023 1939
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_tariff ALTER COLUMN id SET DEFAULT nextval('billservice_tariff_id_seq'::regclass);


--
-- TOC entry 2510 (class 2604 OID 4631275)
-- Dependencies: 2025 2024
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_template ALTER COLUMN id SET DEFAULT nextval('billservice_template_id_seq'::regclass);


--
-- TOC entry 2511 (class 2604 OID 4631276)
-- Dependencies: 2027 2026
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_timeaccessnode ALTER COLUMN id SET DEFAULT nextval('billservice_timeaccessnode_id_seq'::regclass);


--
-- TOC entry 2515 (class 2604 OID 4631277)
-- Dependencies: 2029 2028
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_timeaccessservice ALTER COLUMN id SET DEFAULT nextval('billservice_timeaccessservice_id_seq'::regclass);


--
-- TOC entry 2516 (class 2604 OID 4631278)
-- Dependencies: 2031 2030
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_timeperiod ALTER COLUMN id SET DEFAULT nextval('billservice_timeperiod_id_seq'::regclass);


--
-- TOC entry 2517 (class 2604 OID 4631279)
-- Dependencies: 2033 2032
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_timeperiod_time_period_nodes ALTER COLUMN id SET DEFAULT nextval('billservice_timeperiod_time_period_nodes_id_seq'::regclass);


--
-- TOC entry 2520 (class 2604 OID 4631280)
-- Dependencies: 2035 2034
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_timeperiodnode ALTER COLUMN id SET DEFAULT nextval('billservice_timeperiodnode_id_seq'::regclass);


--
-- TOC entry 2527 (class 2604 OID 4631281)
-- Dependencies: 2037 2036
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_timespeed ALTER COLUMN id SET DEFAULT nextval('billservice_timespeed_id_seq'::regclass);


--
-- TOC entry 2572 (class 2604 OID 4632065)
-- Dependencies: 2073 2072 2073
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_timetransaction ALTER COLUMN id SET DEFAULT nextval('billservice_timetransaction_id_seq'::regclass);


--
-- TOC entry 2573 (class 2604 OID 4632153)
-- Dependencies: 2074 2075 2075
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_tpchangerule ALTER COLUMN id SET DEFAULT nextval('billservice_tpchangerule_id_seq'::regclass);


--
-- TOC entry 2528 (class 2604 OID 4631282)
-- Dependencies: 2039 2038
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_trafficlimit ALTER COLUMN id SET DEFAULT nextval('billservice_trafficlimit_id_seq'::regclass);


--
-- TOC entry 2529 (class 2604 OID 4631283)
-- Dependencies: 2041 2040
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_trafficlimit_traffic_class ALTER COLUMN id SET DEFAULT nextval('billservice_trafficlimit_traffic_class_id_seq'::regclass);


--
-- TOC entry 2571 (class 2604 OID 4632042)
-- Dependencies: 2071 2070 2071
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_traffictransaction ALTER COLUMN id SET DEFAULT nextval('billservice_traffictransaction_id_seq'::regclass);


--
-- TOC entry 2532 (class 2604 OID 4631284)
-- Dependencies: 2043 2042
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_traffictransmitnodes ALTER COLUMN id SET DEFAULT nextval('billservice_traffictransmitnodes_id_seq'::regclass);


--
-- TOC entry 2534 (class 2604 OID 4631285)
-- Dependencies: 2045 2044
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_traffictransmitnodes_time_nodes ALTER COLUMN id SET DEFAULT nextval('billservice_traffictransmitnodes_time_nodes_id_seq'::regclass);


--
-- TOC entry 2535 (class 2604 OID 4631286)
-- Dependencies: 2047 2046
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_traffictransmitnodes_traffic_class ALTER COLUMN id SET DEFAULT nextval('billservice_traffictransmitnodes_traffic_class_id_seq'::regclass);


--
-- TOC entry 2539 (class 2604 OID 4631287)
-- Dependencies: 2049 2048
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_traffictransmitservice ALTER COLUMN id SET DEFAULT nextval('billservice_traffictransmitservice_id_seq'::regclass);


--
-- TOC entry 2540 (class 2604 OID 4631288)
-- Dependencies: 2051 2050
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_transaction ALTER COLUMN id SET DEFAULT nextval('billservice_transaction_id_seq'::regclass);


--
-- TOC entry 2543 (class 2604 OID 4631289)
-- Dependencies: 2053 2052
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_transactiontype ALTER COLUMN id SET DEFAULT nextval('billservice_transactiontype_id_seq'::regclass);


--
-- TOC entry 2577 (class 2604 OID 4632665)
-- Dependencies: 2079 2078 2079
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE billservice_x8021 ALTER COLUMN id SET DEFAULT nextval('billservice_x8021_id_seq'::regclass);


--
-- TOC entry 2544 (class 2604 OID 4631290)
-- Dependencies: 2055 2054
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE django_admin_log ALTER COLUMN id SET DEFAULT nextval('django_admin_log_id_seq'::regclass);


--
-- TOC entry 2546 (class 2604 OID 4631291)
-- Dependencies: 2057 2056
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE django_content_type ALTER COLUMN id SET DEFAULT nextval('django_content_type_id_seq'::regclass);


--
-- TOC entry 2547 (class 2604 OID 4631292)
-- Dependencies: 2060 2059
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE django_site ALTER COLUMN id SET DEFAULT nextval('django_site_id_seq'::regclass);


--
-- TOC entry 2557 (class 2604 OID 4631293)
-- Dependencies: 2062 2061
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE nas_nas ALTER COLUMN id SET DEFAULT nextval('nas_nas_id_seq'::regclass);


--
-- TOC entry 2561 (class 2604 OID 4631294)
-- Dependencies: 2064 2063
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE nas_trafficclass ALTER COLUMN id SET DEFAULT nextval('nas_trafficclass_id_seq'::regclass);


--
-- TOC entry 2568 (class 2604 OID 4631295)
-- Dependencies: 2066 2065
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE nas_trafficnode ALTER COLUMN id SET DEFAULT nextval('nas_trafficnode_id_seq'::regclass);


--
-- TOC entry 2570 (class 2604 OID 4631296)
-- Dependencies: 2068 2067
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE radius_activesession ALTER COLUMN id SET DEFAULT nextval('radius_activesession_id_seq'::regclass);


--
-- TOC entry 2379 (class 2604 OID 4631234)
-- Dependencies: 2069 1941
-- Name: id; Type: DEFAULT; Schema: public; Owner: ebs
--

ALTER TABLE radius_session ALTER COLUMN id SET DEFAULT nextval('radius_session_id_seq'::regclass);


--
-- TOC entry 3050 (class 0 OID 4630735)
-- Dependencies: 1942
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY auth_group (id, name) FROM stdin;
\.


--
-- TOC entry 3051 (class 0 OID 4630740)
-- Dependencies: 1944
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- TOC entry 3052 (class 0 OID 4630745)
-- Dependencies: 1946
-- Data for Name: auth_message; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY auth_message (id, user_id, message) FROM stdin;
\.


--
-- TOC entry 3053 (class 0 OID 4630753)
-- Dependencies: 1948
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add permission	1	add_permission
2	Can change permission	1	change_permission
3	Can delete permission	1	delete_permission
4	Can add group	2	add_group
5	Can change group	2	change_group
6	Can delete group	2	delete_group
7	Can add user	3	add_user
8	Can change user	3	change_user
9	Can delete user	3	delete_user
10	Can add message	4	add_message
11	Can change message	4	change_message
12	Can delete message	4	delete_message
13	Can add content type	5	add_contenttype
14	Can change content type	5	change_contenttype
15	Can delete content type	5	delete_contenttype
16	Can add session	6	add_session
17	Can change session	6	change_session
18	Can delete session	6	delete_session
19	Can add site	7	add_site
20	Can change site	7	change_site
21	Can delete site	7	delete_site
22	Can add log entry	8	add_logentry
23	Can change log entry	8	change_logentry
24	Can delete log entry	8	delete_logentry
25	Can add session	9	add_session
26	Can change session	9	change_session
27	Can delete session	9	delete_session
28	Can add active session	10	add_activesession
29	Can change active session	10	change_activesession
30	Can delete active session	10	delete_activesession
31	Can add Сервер доступа	11	add_nas
32	Can change Сервер доступа	11	change_nas
33	Can delete Сервер доступа	11	delete_nas
34	Can add Класс трафика	12	add_trafficclass
35	Can change Класс трафика	12	change_trafficclass
36	Can delete Класс трафика	12	delete_trafficclass
37	Can add Направление трафика	13	add_trafficnode
38	Can change Направление трафика	13	change_trafficnode
39	Can delete Направление трафика	13	delete_trafficnode
40	Can add Нода временного периода	14	add_timeperiodnode
41	Can change Нода временного периода	14	change_timeperiodnode
42	Can delete Нода временного периода	14	delete_timeperiodnode
43	Can add Временной период	15	add_timeperiod
44	Can change Временной период	15	change_timeperiod
45	Can delete Временной период	15	delete_timeperiod
46	Can add Расчётный период	16	add_settlementperiod
47	Can change Расчётный период	16	change_settlementperiod
48	Can delete Расчётный период	16	delete_settlementperiod
49	Can add Периодическая услуга	17	add_periodicalservice
50	Can change Периодическая услуга	17	change_periodicalservice
51	Can delete Периодическая услуга	17	delete_periodicalservice
52	Can add История проводок по пер. услугам	18	add_periodicalservicehistory
53	Can change История проводок по пер. услугам	18	change_periodicalservicehistory
54	Can delete История проводок по пер. услугам	18	delete_periodicalservicehistory
55	Can add Разовый платеж	19	add_onetimeservice
56	Can change Разовый платеж	19	change_onetimeservice
57	Can delete Разовый платеж	19	delete_onetimeservice
58	Can add Доступ с учётом времени	20	add_timeaccessservice
59	Can change Доступ с учётом времени	20	change_timeaccessservice
60	Can delete Доступ с учётом времени	20	delete_timeaccessservice
61	Can add Период доступа	21	add_timeaccessnode
62	Can change Период доступа	21	change_timeaccessnode
63	Can delete Период доступа	21	delete_timeaccessnode
64	Can add Параметры доступа	22	add_accessparameters
65	Can change Параметры доступа	22	change_accessparameters
66	Can delete Параметры доступа	22	delete_accessparameters
67	Can add настройка скорости	23	add_timespeed
68	Can change настройка скорости	23	change_timespeed
69	Can delete настройка скорости	23	delete_timespeed
70	Can add Предоплаченный трафик	24	add_prepaidtraffic
71	Can change Предоплаченный трафик	24	change_prepaidtraffic
72	Can delete Предоплаченный трафик	24	delete_prepaidtraffic
73	Can add Доступ с учётом трафика	25	add_traffictransmitservice
74	Can change Доступ с учётом трафика	25	change_traffictransmitservice
75	Can delete Доступ с учётом трафика	25	delete_traffictransmitservice
76	Can add цена за направление	26	add_traffictransmitnodes
77	Can change цена за направление	26	change_traffictransmitnodes
78	Can delete цена за направление	26	delete_traffictransmitnodes
79	Can add Предоплаченый трафик пользователя	27	add_accountprepaystrafic
80	Can change Предоплаченый трафик пользователя	27	change_accountprepaystrafic
81	Can delete Предоплаченый трафик пользователя	27	delete_accountprepaystrafic
82	Can add Предоплаченное время пользователя	28	add_accountprepaystime
83	Can change Предоплаченное время пользователя	28	change_accountprepaystime
84	Can delete Предоплаченное время пользователя	28	delete_accountprepaystime
85	Can add лимит трафика	29	add_trafficlimit
86	Can change лимит трафика	29	change_trafficlimit
87	Can delete лимит трафика	29	delete_trafficlimit
88	Can add Тариф	30	add_tariff
89	Can change Тариф	30	change_tariff
90	Can delete Тариф	30	delete_tariff
91	Can add Аккаунт	31	add_account
92	Can change Аккаунт	31	change_account
93	Can delete Аккаунт	31	delete_account
94	Can add тип проводки	32	add_transactiontype
95	Can change тип проводки	32	change_transactiontype
96	Can delete тип проводки	32	delete_transactiontype
97	Can add Проводка	33	add_transaction
98	Can change Проводка	33	change_transaction
99	Can delete Проводка	33	delete_transaction
100	Can add привязка	34	add_accounttarif
101	Can change привязка	34	change_accounttarif
102	Can delete привязка	34	delete_accounttarif
103	Can add скорости IPN клиентов	35	add_accountipnspeed
104	Can change скорости IPN клиентов	35	change_accountipnspeed
105	Can delete скорости IPN клиентов	35	delete_accountipnspeed
109	Can add NetFlow статистика	37	add_netflowstream
110	Can change NetFlow статистика	37	change_netflowstream
111	Can delete NetFlow статистика	37	delete_netflowstream
112	Can add Периодическая операция	38	add_shedulelog
113	Can change Периодическая операция	38	change_shedulelog
114	Can delete Периодическая операция	38	delete_shedulelog
115	Can add one time service history	39	add_onetimeservicehistory
116	Can change one time service history	39	change_onetimeservicehistory
117	Can delete one time service history	39	delete_onetimeservicehistory
118	Can add system user	40	add_systemuser
119	Can change system user	40	change_systemuser
120	Can delete system user	40	delete_systemuser
121	Can add ports	41	add_ports
122	Can change ports	41	change_ports
123	Can delete ports	41	delete_ports
139	Can add sale card	47	add_salecard
140	Can change sale card	47	change_salecard
141	Can delete sale card	47	delete_salecard
127	Can add card	43	add_card
128	Can change card	43	change_card
129	Can delete card	43	delete_card
130	Can add operator	44	add_operator
131	Can change operator	44	change_operator
132	Can delete operator	44	delete_operator
133	Can add bank data	45	add_bankdata
134	Can change bank data	45	change_bankdata
135	Can delete bank data	45	delete_bankdata
136	Can add dealer	46	add_dealer
137	Can change dealer	46	change_dealer
138	Can delete dealer	46	delete_dealer
\.


--
-- TOC entry 3054 (class 0 OID 4630758)
-- Dependencies: 1950
-- Data for Name: auth_user; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY auth_user (id, username, first_name, last_name, email, password, is_staff, is_active, is_superuser, last_login, date_joined) FROM stdin;
\.


--
-- TOC entry 3055 (class 0 OID 4630761)
-- Dependencies: 1951
-- Data for Name: auth_user_groups; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY auth_user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- TOC entry 3056 (class 0 OID 4630768)
-- Dependencies: 1954
-- Data for Name: auth_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY auth_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- TOC entry 3057 (class 0 OID 4630773)
-- Dependencies: 1956
-- Data for Name: billservice_accessparameters; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_accessparameters (id, access_type, access_time_id, max_limit, min_limit, burst_limit, burst_treshold, burst_time, priority, ipn_for_vpn) FROM stdin;
2	PPTP	1	0/0	0/0	0/0	0/0	0/0	8	f
4	PPTP	1	0/0	0/0	0/0	0/0	0/0	8	f
\.


--
-- TOC entry 3058 (class 0 OID 4630788)
-- Dependencies: 1958
-- Data for Name: billservice_account; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_account (id, username, password, fullname, email, address, nas_id, vpn_ip_address, assign_ipn_ip_from_dhcp, ipn_ip_address, ipn_mac_address, ipn_status, suspended, created, ballance, credit, disabled_by_limit, balance_blocked, ipn_speed, vpn_speed, netmask, ipn_added, city, postcode, region, street, house, house_bulk, entrance, room, vlan, allow_webcab, allow_expresscards, assign_dhcp_null, assign_dhcp_block, allow_vpn_null, allow_vpn_block, passport, passport_given, phone_h, phone_m, vpn_ipinuse_id, ipn_ipinuse_id, associate_pptp_ipn_ip, associate_pppoe_mac, contactperson_phone, comment, "row", elevator_direction, status, contactperson, passport_date) FROM stdin;
\.


--
-- TOC entry 3119 (class 0 OID 4632768)
-- Dependencies: 2085
-- Data for Name: billservice_accountaddonservice; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_accountaddonservice (id, service_id, account_id, activated, deactivated, action_status, speed_status, temporary_blocked, last_checkout) FROM stdin;
\.


--
-- TOC entry 3059 (class 0 OID 4630834)
-- Dependencies: 1960
-- Data for Name: billservice_accountipnspeed; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_accountipnspeed (id, account_id, speed, state, static, datetime) FROM stdin;
\.


--
-- TOC entry 3060 (class 0 OID 4630843)
-- Dependencies: 1962
-- Data for Name: billservice_accountprepaystime; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_accountprepaystime (id, account_tarif_id, prepaid_time_service_id, size, datetime) FROM stdin;
\.


--
-- TOC entry 3061 (class 0 OID 4630850)
-- Dependencies: 1964
-- Data for Name: billservice_accountprepaystrafic; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_accountprepaystrafic (id, account_tarif_id, prepaid_traffic_id, size, datetime) FROM stdin;
\.


--
-- TOC entry 3062 (class 0 OID 4630857)
-- Dependencies: 1966
-- Data for Name: billservice_accountspeedlimit; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_accountspeedlimit (id, account_id, speedlimit_id) FROM stdin;
\.


--
-- TOC entry 3063 (class 0 OID 4630862)
-- Dependencies: 1968
-- Data for Name: billservice_accounttarif; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_accounttarif (id, account_id, tarif_id, datetime, periodical_billed) FROM stdin;
\.


--
-- TOC entry 3117 (class 0 OID 4632694)
-- Dependencies: 2081
-- Data for Name: billservice_addonservice; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_addonservice (id, name, allow_activation, service_type, sp_type, sp_period_id, timeperiod_id, cost, cancel_subscription, wyte_period_id, wyte_cost, action, nas_id, service_activation_action, service_deactivation_action, deactivate_service_for_blocked_account, change_speed, change_speed_type, speed_units, max_tx, max_rx, burst_tx, burst_rx, burst_treshold_tx, burst_treshold_rx, burst_time_tx, burst_time_rx, min_tx, min_rx, priority, comment) FROM stdin;
\.


--
-- TOC entry 3118 (class 0 OID 4632741)
-- Dependencies: 2083
-- Data for Name: billservice_addonservicetarif; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_addonservicetarif (id, tarif_id, service_id, activation_count, activation_count_period_id) FROM stdin;
\.


--
-- TOC entry 3120 (class 0 OID 4632791)
-- Dependencies: 2087
-- Data for Name: billservice_addonservicetransaction; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_addonservicetransaction (id, service_id, service_type, account_id, accountaddonservice_id, accounttarif_id, summ, created, type_id) FROM stdin;
\.


--
-- TOC entry 3064 (class 0 OID 4630867)
-- Dependencies: 1970
-- Data for Name: billservice_bankdata; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_bankdata (id, bank, bankcode, rs, currency) FROM stdin;
\.


--
-- TOC entry 3065 (class 0 OID 4630872)
-- Dependencies: 1972
-- Data for Name: billservice_card; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_card (id, series, pin, sold, nominal, activated, activated_by_id, start_date, end_date, disabled, created, template_id, account_id, tarif_id, nas_id, login, ip, ipinuse_id) FROM stdin;
\.


--
-- TOC entry 3066 (class 0 OID 4630884)
-- Dependencies: 1974
-- Data for Name: billservice_dealer; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_dealer (id, organization, unp, okpo, contactperson, director, phone, fax, postaddress, uraddress, email, bank_id, prepayment, paydeffer, discount, always_sell_cards, deleted) FROM stdin;
\.


--
-- TOC entry 3067 (class 0 OID 4630894)
-- Dependencies: 1976
-- Data for Name: billservice_dealerpay; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_dealerpay (id, dealer_id, pay, salecard_id, created) FROM stdin;
\.


--
-- TOC entry 3068 (class 0 OID 4630899)
-- Dependencies: 1978
-- Data for Name: billservice_document; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_document (id, account_id, type_id, body) FROM stdin;
\.


--
-- TOC entry 3069 (class 0 OID 4630907)
-- Dependencies: 1980
-- Data for Name: billservice_documenttype; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_documenttype (id, name) FROM stdin;
1	Договор на подключение физ. лиц
2	Договор на подключение юр. лиц
3	Счёт фактура
4	Акт выполненных работ
5	Кассовый чек
6	Накладная на карточки экспресс-оплаты
7	Карты экспресс-оплаты
\.


--
-- TOC entry 3070 (class 0 OID 4630912)
-- Dependencies: 1982
-- Data for Name: billservice_globalstat; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_globalstat (id, account_id, bytes_in, bytes_out, datetime, nas_id, classes, classbytes) FROM stdin;
\.


--
-- TOC entry 3071 (class 0 OID 4630922)
-- Dependencies: 1984
-- Data for Name: billservice_group; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_group (id, name, direction, type) FROM stdin;
\.


--
-- TOC entry 3072 (class 0 OID 4630927)
-- Dependencies: 1986
-- Data for Name: billservice_group_trafficclass; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_group_trafficclass (id, group_id, trafficclass_id) FROM stdin;
\.


--
-- TOC entry 3045 (class 0 OID 4630644)
-- Dependencies: 1937
-- Data for Name: billservice_groupstat; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_groupstat (id, group_id, account_id, bytes, datetime, classes, classbytes, max_class) FROM stdin;
\.


--
-- TOC entry 3073 (class 0 OID 4630934)
-- Dependencies: 1989
-- Data for Name: billservice_ipinuse; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_ipinuse (id, pool_id, ip, datetime) FROM stdin;
\.


--
-- TOC entry 3074 (class 0 OID 4630939)
-- Dependencies: 1991
-- Data for Name: billservice_ippool; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_ippool (id, name, type, start_ip, end_ip) FROM stdin;
1	VPN 192.168.12.0/24	0	192.168.12.2	192.168.12.254
\.


--
-- TOC entry 3046 (class 0 OID 4630663)
-- Dependencies: 1938
-- Data for Name: billservice_netflowstream; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_netflowstream (id, nas_id, account_id, tarif_id, date_start, src_addr, traffic_class_id, direction, traffic_transmit_node_id, dst_addr, octets, src_port, dst_port, protocol, checkouted, for_checkout) FROM stdin;
\.


--
-- TOC entry 3075 (class 0 OID 4630949)
-- Dependencies: 1994
-- Data for Name: billservice_onetimeservice; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_onetimeservice (id, tarif_id, name, cost) FROM stdin;
\.


--
-- TOC entry 3076 (class 0 OID 4630954)
-- Dependencies: 1996
-- Data for Name: billservice_onetimeservicehistory; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_onetimeservicehistory (id, accounttarif_id, onetimeservice_id, datetime, transaction_id, summ, account_id) FROM stdin;
\.


--
-- TOC entry 3077 (class 0 OID 4630959)
-- Dependencies: 1998
-- Data for Name: billservice_operator; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_operator (id, organization, unp, okpo, contactperson, director, phone, postaddress, uraddress, email, fax, bank_id) FROM stdin;
\.


--
-- TOC entry 3078 (class 0 OID 4630967)
-- Dependencies: 2000
-- Data for Name: billservice_organization; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_organization (id, account_id, name, uraddress, okpo, unp, bank_id, phone, fax) FROM stdin;
\.


--
-- TOC entry 3079 (class 0 OID 4630981)
-- Dependencies: 2002
-- Data for Name: billservice_periodicalservice; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_periodicalservice (id, tarif_id, name, settlement_period_id, cost, cash_method, condition, created) FROM stdin;
\.


--
-- TOC entry 3048 (class 0 OID 4630696)
-- Dependencies: 1940
-- Data for Name: billservice_periodicalservicehistory; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_periodicalservicehistory (id, service_id, transaction_id, datetime, accounttarif_id, summ, account_id, type_id) FROM stdin;
\.


--
-- TOC entry 3080 (class 0 OID 4630992)
-- Dependencies: 2005
-- Data for Name: billservice_ports; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_ports (id, port, protocol, name, description) FROM stdin;
38801	1	6	tcpmux	TCP Port Service Multiplexer rfc-1078
38802	1	17	tcpmux	TCP Port Service Multiplexer rfc-1078
38803	2	6	compressnet	Management Utility
38804	2	17	compressnet	Management Utility
38805	3	6	compressnet	Compression Process
38806	3	17	compressnet	Compression Process
38807	4	6	echo	AppleTalk Echo Protocol
38808	4	17	echo	AppleTalk Echo Protocol
38809	5	6	rje	Remote Job Entry
38810	5	17	rje	Remote Job Entry
38811	6	37	zip	Zone Information Protocol
38812	7	6	echo	Echo
38813	7	17	echo	Echo
38814	8	6		Unassigned
38815	8	17		Unassigned
38816	9	6	discard	Discard; alias=sink null
38817	9	17	discard	Discard; alias=sink null
38818	10	6		Unassigned
38819	10	17		Unassigned
38820	11	6	systat	Active Users; alias=users
38821	11	17	systat	Active Users; alias=users
38822	12	6		Unassigned
38823	12	17		Unassigned
38824	13	6	daytime	Daytime
38825	13	17	daytime	Daytime
38826	14	6		Unassigned
38827	14	17		Unassigned
38828	15	6		Unassigned [was netstat]
38829	15	17		Unassigned [was netstat]
38830	16	6		Unassigned
38831	16	17		Unassigned
38832	17	6	qotd	Quote of the Day; alias=quote
38833	18	6	msp	Message Send Protocol
38834	18	17	msp	Message Send Protocol
38835	19	6	chargen	Character Generator; alias=ttytst source
38836	19	17	chargen	Character Generator; alias=ttytst source
38837	20	6	ftp-data	File Transfer [Default Data]
38838	21	6	ftp	File Transfer [Control] connection dialog
38839	22	6	ssh	Secure Shell Login
38840	22	17	pcanywhere	PC Anywhere
38841	23	6	telnet	Telnet
38842	24	6	priv-mail	Any private mail system
38843	25	6	smtp	Simple Mail Transfer; alias=mail
38844	26	6		Unassigned
38845	26	17		Unassigned
38846	27	6	nswfe	NSW User System FE
38847	28	6		Unassigned
38848	28	17		Unassigned
38849	29	6	msgicp	MSG ICP
38850	30	6		Unassigned
38851	30	17		Unassigned
38852	31	6	msgauth	MSG Authentication
38853	32	6		Unassigned
38854	32	17		Unassigned
38855	33	6	dsp	Display Support Protocol
38856	33	17	dsp	Display Support Protocol
38857	34	6		Unassigned
38858	34	17		Unassigned
38859	35	6	priv-print	Any private printer server
38860	35	17	priv-print	Any private printer server
38861	36	6		Unassigned
38862	36	17		Unassigned
38863	37	6	time	Time; alias=timeserver
38864	37	17	time	Time; alias=timeserver
38865	38	6	rap	Remote Access Protocol
38866	38	17	rap	Remote Access Protocol
38867	39	6	rlp	Resource Location Protocol; alias=resource
38868	39	17	rlp	Resource Location Protocol; alias=resource
38869	40	6		Unassigned
38870	40	17		Unassigned
38871	41	6	graphics	Graphics
38872	41	17	graphics	Graphics
38873	41	6	deepthroat	Deep Throat Trpjan Horse
38874	41	17	deepthroat	Deep Throat Trpjan Horse
38875	42	6	nameserver	Host Name Server; alias=nameserver
38876	42	17	nameserver	Host Name Server; alias=nameserver
38877	43	6	nicname	Who Is; alias=nicname
38878	43	17	nicname	Who Is; alias=nicname
38879	44	6	mpm-flags	MPM FLAGS Protocol
38880	44	17	mpm-flags	MPM FLAGS Protocol
38881	45	6	mpm	Message Processing Module [recv]
38882	45	17	mpm	Message Processing Module [recv]
38883	46	6	mpm-snd	MPM [default send]
38884	46	17	mpm-snd	MPM [default send]
38885	47	6	ni-ftp	NI FTP
38886	47	17	ni-ftp	NI FTP
38887	48	6	auditd	Digital Audit Daemon
38888	48	17	auditd	Digital Audit Daemon
38889	49	6	tacacs	Login Host Protocol (TACACS)
38890	49	17	tacacs	Login Host Protocol (TACACS)
38891	50	6	re-mail-ck	Remote Mail Checking Protocol
38892	50	17	re-mail-ck	Remote Mail Checking Protocol
38893	51	6	la-maint	IMP Logical Address Maintenance
38894	51	17	la-maint	IMP Logical Address Maintenance
38895	52	6	xns-time	XNS Time Protocol
38896	52	17	xns-time	XNS Time Protocol
38897	53	6	domain	Domain Name Server
38898	53	17	domain	Domain Name Server
38899	54	6	xns-ch	XNS Clearinghouse
38900	54	17	xns-ch	XNS Clearinghouse
38901	55	6	isi-gl	ISI Graphics Language
38902	55	17	isi-gl	ISI Graphics Language
38903	56	6	xns-auth	XNS Authentication
38904	56	17	xns-auth	XNS Authentication
38905	57	6	priv-term	Any private terminal access
38906	57	17	priv-term	Any private terminal access
38907	58	6	xns-mail	XNS Mail
38908	58	17	xns-mail	XNS Mail
38909	59	6	priv-file	Any private file service
38910	59	17	priv-file	Any private file service
38911	60	6		Unassigned
38912	60	17		Unassigned
38913	61	6	ni-mail	NI MAIL
38914	61	17	ni-mail	NI MAIL
38915	62	6	acas	ACA Services
38916	62	17	acas	ACA Services
38917	63	6	via-ftp / whois++	VIA Systems - FTP / whois++
38918	63	17	via-ftp / whois++	VIA Systems - FTP / whois++
38919	64	6	covia	Communications Integrator (Cl)
38920	64	17	covia	Communications Integrator (Cl)
38921	65	6	tacacs-ds	TACACS-Database Service
38922	65	17	tacacs-ds	TACACS-Database Service
38923	66	6	sql*net	Oracle SQL*NET
38924	66	17	sql*net	Oracle SQL*NET
38925	67	6	bootps	DHCP BOOTP Protocol Server
38926	67	17	bootps	DHCP BOOTP Protocol Server
38927	68	6	bootpc	DHCP BOOTP Protocol Client
38928	68	17	bootpc	DHCP BOOTP Protocol Client
38929	69	6	tftp	Trivial File Transfer
38930	69	17	tftp	Trivial File Transfer
38931	70	6	gopher	Gopher
38932	70	17	gopher	Gopher
38933	71	6	netrjs-1	Remote Job Service
38934	71	17	netrjs-1	Remote Job Service
38935	72	6	netrjs-2	Remote Job Service
38936	72	17	netrjs-2	Remote Job Service
38937	73	6	netrjs-3	Remote Job Service
38938	73	17	netrjs-3	Remote Job Service
38939	74	6	netrjs-4	Remote Job Service
38940	74	17	netrjs-4	Remote Job Service
38941	75	17	priv-dial	Any private dial out service
38942	76	6	deos	Distributed External Object Store
38943	76	17	deos	Distributed External Object Store
38944	77	6	priv-rjs	Any private RJE service
38945	77	17	priv-rjs	Any private RJE service
38946	78	6	vettcp	Vettcp
38947	78	17	vettcp	Vettcp
38948	79	6	finger	Finger
38949	79	17	finger	Finger
38950	80	6	WWW	World Wide Web HTTP
38951	80	17	WWW	World Wide Web HTTP
38952	81	6	hosts2-ns	HOSTS2 Name Server
38953	81	17	hosts2-ns	HOSTS2 Name Server
38954	82	6	xfer	XFER Utility
38955	82	17	xfer	XFER Utility
38956	83	6	mit-ml-dev	MIT ML Device
38957	83	17	mit-ml-dev	MIT ML Device
38958	84	6	ctf	Common Trace Facility
38959	84	17	ctf	Common Trace Facility
38960	85	6	mit-nil-dev	MIT ML Device
38961	85	17	mit-nil-dev	MIT ML Device
38962	86	6	mfcobol	Micro Focus Cobol
38963	86	17	mfcobol	Micro Focus Cobol
38964	87	6	ttylink	Any private terminal link; alias=ttylink
38965	87	17	ttylink	Any private terminal link; alias=ttylink
38966	88	6	kerberos-sec	Kerberos(v5) krb5
38967	88	17	kerberos-sec	Kerberos(v5) krb5
38968	89	6	su-mit-tg	SU/MIT Telnet Gateway
38969	89	17	su-mit-tg	SU/MIT Telnet Gateway
38970	90	6	DNSIX	DNSIX Security Attribute Token Map
38971	90	17	DNSIX	DNSIX Security Attribute Token Map
38972	91	6	mit-dov	MIT Dover Spooler
38973	91	17	mit-dov	MIT Dover Spooler
38974	92	6	npp	Network Printing Protocol
38975	92	17	npp	Network Printing Protocol
38976	93	6	dcp	Device Control Protocol
38977	93	17	dcp	Device Control Protocol
38978	94	6	objcall	Tivoli Object Dispatcher
38979	94	17	objcall	Tivoli Object Dispatcher
38980	95	6	supdup	BSD supupd(8)
38981	96	6	dixie	DIXIE Protocol Specification
38982	96	17	dixie	DIXIE Protocol Specification
38983	97	6	swift-rvf	Swift Remote Virtual File Protocol
38984	97	17	swift-rvf	Swift Remote Virtual File Protocol
38985	98	6	linuxconf	linuxconf
38986	98	17	tacnews	TAC News
38987	99	6	metagram	Metagram Relay
38988	99	17	metagram	Metagram Relay
38989	100	6	newacct	[unauthorized use]
38990	101	6	hostriame	NIC Host Name Server; alias=hostname
38991	101	17	hostriame	NIC Host Name Server; alias=hostname
38992	102	6	iso-tsap	ISO-TSAP Class 0
38993	102	17	iso-tsap	ISO-TSAP Class 0
38994	103	6	gppitnp	Genesis Point-to-point Trans Net or X400 ISO Email; alias=webster
38995	103	17	gppitnp	Genesis Point-to-point Trans Net or X400 ISO Email; alias=webster
38996	104	6	acr-nema	ACR-NEMA Digital Imag. & Comm. 300
38997	104	17	acr-nema	ACR-NEMA Digital Imag. & Comm. 300
38998	105	6	csnet-ns	Mailbox Name Nameserver
38999	105	17	csnet-ns	Mailbox Name Nameserver
39000	106	6	3com-tsmux	3COM-TSMUX Eudora compatible PW changer
39001	106	17	3com-tsmux	3COM-TSMUX Eudora compatible PW changer
39002	107	6	rtelnet	Remote Telnet Service
39003	107	17	rtelnet	Remote Telnet Service
39004	108	6	snagas	SNA Gateway Access Server
39005	108	17	snagas	SNA Gateway Access Server
39006	109	6	pop2	Post Office Protocol - Ver 2; alias=postoffice
39007	109	17	pop2	Post Office Protocol - Ver 2; alias=postoffice
39008	110	6	pop3	Post Office Protocol - Ver 3; alias=postoffice
39009	110	17	pop3	Post Office Protocol - Ver 3; alias=postoffice
39010	111	6	sunrpc	SUN Remote Procedure Call rpcbind
39011	111	17	sunrpc	SUN Remote Procedure Call rpcbind
39012	112	6	mcidas	McIDAS Data Transmission Protocol
39013	112	17	mcidas	McIDAS Data Transmission Protocol
39014	113	6	auth	ident, tap, Authentication Service
39015	113	17	auth	ident, tap, Authentication Service
39016	114	6	audionews	Audio News Multicast
39017	114	17	audionews	Audio News Multicast
39018	115	6	sftp	Simple File Transfer Protocol
39019	115	17	sftp	Simple File Transfer Protocol
39020	116	6	ansanotify	ANSA REX Notify
39021	116	17	ansanotify	ANSA REX Notify
39022	117	6	uucp-path	UUCP Path Service
39023	117	17	uucp-path	UUCP Path Service
39024	118	6	sqIserv	SQL Services
39025	118	17	sqIserv	SQL Services
39026	119	6	nntp	Network News Transfer Protocol; alias=usenet
39027	119	17	nntp	Network News Transfer Protocol; alias=usenet
39028	120	6	cfdptkt	CFDPTKT
39029	120	17	cfdptkt	CFDPTKT
39030	121	6	erpc	Encore Expedited Remote Pro.Call
39031	121	17	erpc	Encore Expedited Remote Pro.Call
39032	121	6	jammerkilla	BO Jammer Killa Trojan Horse
39033	121	17	jammerkilla	BO Jammer Killa Trojan Horse
39034	122	6	smakynet	SMAKYNET
39035	122	17	smakynet	SMAKYNET
39036	123	6	ntp	Network Time Protocol; alias=ntpd ntp
39037	123	17	ntp	Network Time Protocol; alias=ntpd ntp
39038	124	6	ansatrader	ANSA REX Trader
39039	124	17	ansatrader	ANSA REX Trader
39040	125	6	locus-map	Locus PC-Interface Net Map Server
39041	125	17	locus-map	Locus PC-Interface Net Map Server
39042	126	6	nxedit	NXEdit - Previously: Unisys Unitary Login
39043	126	17	nxedit	NXEdit - Previously: Unisys Unitary Login
39044	127	6	locus-con	Locus PC-Interface Conn Server
39045	127	17	locus-con	Locus PC-Interface Conn Server
39046	128	6	gss-xlicen	GSS X License Verification
39047	128	17	gss-xlicen	GSS X License Verification
39048	129	6	pwdgen	Password Generator Protocol
39049	129	17	pwdgen	Password Generator Protocol
39050	130	6	cisco-fna	Cisco FNATIVE
39051	130	17	cisco-fna	Cisco FNATIVE
39052	131	6	cisco-tna	Cisco TNATIVE
39053	131	17	cisco-tna	Cisco TNATIVE
39054	132	6	cisco-sys	Cisco SYSMAINT
39055	132	17	cisco-sys	Cisco SYSMAINT
39056	133	6	statsrv	Statistics Service
39057	133	17	statsrv	Statistics Service
39058	134	6	ingres-net	INGRES-NET Service
39059	134	17	ingres-net	INGRES-NET Service
39060	135	6	loc-srv / epmap	Location Service / DCE endpoint resolution
39061	135	17	loc-srv / epmap	Location Service / DCE endpoint resolution
39062	136	6	profile	PROFILE Naming System
39063	136	17	profile	PROFILE Naming System
39064	137	6	netbios-ns	NetBIOS Name Service
39065	137	17	netbios-ns	NetBIOS Name Service
39066	138	6	netbios-dgm	NetBIOS Datagram Service
39067	138	17	netbios-dgm	NetBIOS Datagram Service
39068	139	6	netbios-ssn	NetBIOS Session Service
39069	139	17	netbios-ssn	NetBIOS Session Service
39070	140	6	emfis-data	EMFIS Data Service
39071	140	17	emfis-data	EMFIS Data Service
39072	141	6	emfis-cntl	EMFIS Control Service
39073	141	17	emfis-cntl	EMFIS Control Service
39074	142	6	bl-idm	Britton-Lee IDM
39075	142	17	bl-idm	Britton-Lee IDM
39076	143	6	imap2	Internet Message Access Protocol v2
39077	143	17	imap2	Internet Message Access Protocol v2
39078	144	6	NeWs	
39079	144	17	NeWs	
39080	145	6	uaac	UAAC Protocol
39081	145	17	uaac	UAAC Protocol
39082	146	6	iso-ip0	ISO-IP0
39083	146	17	iso-ip0	ISO-IP0
39084	147	6	iso-ip	ISO-IP
39085	147	17	iso-ip	ISO-IP
39086	148	6	cronus / jargon	CRONUS-SUPPORT / Jargon
39087	148	17	cronus / jargon	CRONUS-SUPPORT / Jargon
39088	149	6	aed-512	AED 512 Emulation Service
39089	149	17	aed-512	AED 512 Emulation Service
39090	150	6	sql-net	SQL-NET
39091	150	17	sql-net	SQL-NET
39092	151	6	hems	HEMS
39093	151	17	hems	HEMS
39094	152	6	bftp	Background File Transfer Program
39095	152	17	bftp	Background File Transfer Program
39096	153	6	sgmp	SGMP; alias=sgmp
39097	153	17	sgmp	SGMP; alias=sgmp
39098	154	6	netsc-prod	Netscape
39099	154	17	netsc-prod	Netscape
39100	155	6	netsc-dev	Netscape
39101	155	17	netsc-dev	Netscape
39102	156	6	sqlsrv	SQL Service
39103	156	17	sqlsrv	SQL Service
39104	157	6	knet-cmp	KNET/VM Command Message Protocol
39105	157	17	knet-cmp	KNET/VM Command Message Protocol
39106	158	6	pcmail-srv	PCMail Server; alias=repository
39107	158	17	pcmail-srv	PCMail Server; alias=repository
39108	159	6	nss-routing	NSS-Routing
39109	159	17	nss-routing	NSS-Routing
39110	160	6	sginp-traps	SGMP-TRAPS
39111	160	17	sginp-traps	SGMP-TRAPS
39112	161	6	sump	SNMP; alias=snmp
39113	161	17	sump	SNMP; alias=snmp
39114	162	6	snmptrap	SNMP-trap
39115	162	17	snmptrap	SNMP-trap
39116	163	6	cmip-man	CMIP TCP Manager
39117	163	17	cmip-man	CMIP TCP Manager
39118	164	6	cmip/smip-agent	CMIP TCP Agent
39119	164	17	cmip/smip-agent	CMIP TCP Agent
39120	165	6	xns-courier	Xerox
39121	165	17	xns-courier	Xerox
39122	166	6	s-net	Sirius Systems
39123	166	17	s-net	Sirius Systems
39124	167	6	namp	NAMP
39125	167	17	namp	NAMP
39126	168	6	rsvd	RSVD
39127	168	17	rsvd	RSVD
39128	169	6	send	SEND
39129	169	17	send	SEND
39130	170	6	print-srv	Network PostScript
39131	170	17	print-srv	Network PostScript
39132	171	6	multiplex	Network Innovations Multiplex
39133	171	17	multiplex	Network Innovations Multiplex
39134	172	6	cl-1	Network Innovations CL/1
39135	172	17	cl-1	Network Innovations CL/1
39136	173	6	xyplex-mux	Xyplex
39137	173	17	xyplex-mux	Xyplex
39138	174	6	mailq	MAILQ
39139	174	17	mailq	MAILQ
39140	175	6	vmnet	VMNET
39141	175	17	vmnet	VMNET
39142	176	6	genrad-mux	GENRAD-MUX
39143	176	17	genrad-mux	GENRAD-MUX
39144	177	6	xdmcp	X Display Manager Control Protocol
39145	177	17	xdmcp	X Display Manager Control Protocol
39146	178	6	nextstep	NextStep Window Server
39147	178	17	nextstep	NextStep Window Server
39148	179	6	bgp	Border Gateway Protocol
39149	179	17	bgp	Border Gateway Protocol
39150	180	6	ris	Intergraph
39151	180	17	ris	Intergraph
39152	181	6	unify	Unify
39153	181	17	unify	Unify
39154	182	6	audit	Unisys Audit SITP
39155	182	17	audit	Unisys Audit SITP
39156	183	6	ocbinder	OCBinder
39157	183	17	ocbinder	OCBinder
39158	184	6	ocserver	OCServer
39159	184	17	ocserver	OCServer
39160	185	6	remote-kis	Remote-KIS
39161	185	17	remote-kis	Remote-KIS
39162	186	6	kis	KIS Protocol
39163	186	17	kis	KIS Protocol
39164	187	6	aci	Application Communication Interface
39165	187	17	aci	Application Communication Interface
39166	188	6	mumps	Plus Five's MUMPS
39167	188	17	mumps	Plus Five's MUMPS
39168	189	6	qft	Queued File Transport
39169	189	17	qft	Queued File Transport
39170	190	6	gacp/cacp	Gateway Access Control Protocol
39171	190	17	gacp/cacp	Gateway Access Control Protocol
39172	191	6	prospero	Prospero Directory Service
39173	191	17	prospero	Prospero Directory Service
39174	192	6	osu-nms	OSU Network Monitoring System
39175	192	17	osu-nms	OSU Network Monitoring System
39176	193	6	srmp	Spider Remote Monitoring Protocol
39177	193	17	srmp	Spider Remote Monitoring Protocol
39178	194	6	irc	Internet Relay Chat Protocol
39179	194	17	irc	Internet Relay Chat Protocol
39180	195	6	dn6-nlm-aud	DNSIX Network Level Module Audit
39181	195	17	dn6-nlm-aud	DNSIX Network Level Module Audit
39182	196	6	dn6-smm-red	DNSIX Session Mgt Module Audit Redir
39183	196	17	dn6-smm-red	DNSIX Session Mgt Module Audit Redir
39184	197	6	dls	Directory Location Service
39185	197	17	dls	Directory Location Service
39186	198	6	dls-mon	Directory Location Service Monitor
39187	198	17	dls-mon	Directory Location Service Monitor
39188	199	6	smux	SNMP Unix Multiplexer
39189	199	17	smux	SNMP Unix Multiplexer
39190	200	6	src	IBM System Resource Controller
39191	200	17	src	IBM System Resource Controller
39192	201	6	at-rtmp	AppleTalk Routing Maintenance
39193	201	17	at-rtmp	AppleTalk Routing Maintenance
39194	202	6	at-nbp	AppleTalk Name Binding
39195	202	17	at-nbp	AppleTalk Name Binding
39196	203	6	at-3	AppleTalk Unused
39197	203	17	at-3	AppleTalk Unused
39198	204	6	at-echo	AppleTalk Echo
39199	204	17	at-echo	AppleTalk Echo
39200	205	6	at-5	AppleTalk Unused
39201	205	17	at-5	AppleTalk Unused
39202	206	6	at-zis	AppleTalk Zone Information
39203	206	17	at-zis	AppleTalk Zone Information
39204	207	6	at-7	AppleTalk Unused
39205	207	17	at-7	AppleTalk Unused
39206	208	6	at-8	AppleTalk Unused
39207	208	17	at-8	AppleTalk Unused
39208	209	6	tam / qmtp	Trivial Authenticated Mail Protocol / The Quick Transfer Protocol
39209	209	17	tam / qmtp	Trivial Authenticated Mail Protocol / The Quick Transfer Protocol
39210	210	6	z39.50	wais, ANSI Z39.50
39211	210	17	z39.50	wais, ANSI Z39.50
39212	211	6	914c/g	Texas Instruments 914C/G Terminal
39213	211	17	914c/g	Texas Instruments 914C/G Terminal
39214	212	6	anet	ATEXSSTR
39215	212	17	anet	ATEXSSTR
39216	213	6	ipx	IPX
39217	213	17	ipx	IPX
39218	214	6	vmpwscs	VM PWSCS
39219	214	17	vmpwscs	VM PWSCS
39220	215	6	softpc	Insignia Solutions
39221	215	17	softpc	Insignia Solutions
39222	216	6	Atls / CAIlic	(Access Technology / Computer Associates ) License Server
39223	216	17	Atls / CAIlic	(Access Technology / Computer Associates ) License Server
39224	217	6	dbase	dBASE UNIX
39225	217	17	dbase	dBASE UNIX
39226	218	6	mpp	Netix Message Posting Protocol
39227	218	17	mpp	Netix Message Posting Protocol
39228	219	6	uarps	Unisys ARPs
39229	219	17	uarps	Unisys ARPs
39230	220	6	imap3	Interactive Mail Access Protocol v3
39231	220	17	imap3	Interactive Mail Access Protocol v3
39232	221	6	fln-spx	Berkeley rlogind with SPX auth
39233	221	17	fln-spx	Berkeley rlogind with SPX auth
39234	222	6	rsh-spx	Berkeley rshd. with SPX auth, Possible conflicy with "Masqdialer"
39235	222	17	rsh-spx	Berkeley rshd. with SPX auth, Possible conflicy with "Masqdialer"
39236	223	6	cdc	Certificate Distribution Center
39237	223	17	cdc	Certificate Distribution Center
39238	224	6	masqdialer	masqdialer
39239	224	17	masqdialer	masqdialer
39240	242	6	direct	Direct
39241	242	17	direct	Direct
39242	243	6	sur-meas	Survey Measurement
39243	243	17	sur-meas	Survey Measurement
39244	244	6	dayna	dayna
39245	244	17	dayna	dayna
39246	245	6	link	LINK
39247	245	17	link	LINK
39248	246	6	dsp3270	Display Systems Protocol
39249	246	17	dsp3270	Display Systems Protocol
39250	247	6	subntbcst_tftp	SUBNTBCST_TFTP
39251	247	17	subntbcst_tftp	SUBNTBCST_TFTP
39252	248	6	bhfhs	bhfhs
39253	248	17	bhfhs	bhfhs
39254	256	6	rap	RAP
39255	256	17	rap	RAP
39256	257	6	set	Secure Electronic Transaction
39257	257	17	set	Secure Electronic Transaction
39258	258	6	yak-chat	Yak Winsock Personal Chat
39259	258	17	yak-chat	Yak Winsock Personal Chat
39260	259	6	escro-gen	Efficient Short Romote Operations
39261	259	17	escro-gen	Efficient Short Romote Operations
39262	260	6	openport	Openport
39263	260	17	openport	Openport
39264	261	6	nsiiops	IIOP Name Service TLS/SSL
39265	261	17	nsiiops	IIOP Name Service TLS/SSL
39266	262	6	arcisdms	Arcisdms
39267	262	17	arcisdms	Arcisdms
39268	263	6	hdap	HDAP
39269	263	17	hdap	HDAP
39270	264	6	bgmp	BGMP
39271	264	17	bgmp	BGMP
39272	265	6	x-bone-ctl	X-Bone CTL
39273	265	17	x-bone-ctl	X-Bone CTL
39274	267	6	td-service	Tobit David Service Layer
39275	267	17	td-service	Tobit David Service Layer
39276	268	6	td-replica	Tobit David Replica
39277	268	17	td-replica	Tobit David Replica
39278	280	6	http-mgmt	http-mgmt
39279	280	17	http-mgmt	http-mgmt
39280	281	6	personal-link	Personal-Link
39281	281	17	personal-link	Personal-Link
39282	282	6	cableport-ax	Cable Port A/X
39283	282	17	cableport-ax	Cable Port A/X
39284	283	6	rescap	rescap
39285	283	17	rescap	rescap
39286	284	6	corerjd	corerjd
39287	284	17	corerjd	corerjd
39288	285	6		Unassigned
39289	285	17		Unassigned
39290	286	6	fxp-1	FXP-1
39291	286	17	fxp-1	FXP-1
39292	287	6	k-block	K-Block
39293	287	17	k-block	K-Block
39294	308	6	novastorbakcup	Novastor Backup
39295	308	17	novastorbakcup	Novastor Backup
39296	309	6	entrusttime	EntrustTime
39297	309	17	entrusttime	EntrustTime
39298	310	6	bhmds	bhmds
39299	310	17	bhmds	bhmds
39300	311	6	asip-webadmin	AppleShare IP WebAdmin
39301	311	17	asip-webadmin	AppleShare IP WebAdmin
39302	312	6	vslmp	VSLMP
39303	312	17	vslmp	VSLMP
39304	313	6	magenta-logic	netfusion.co.uk
39305	313	17	magenta-logic	netfusion.co.uk
39306	314	6	opalis-robot	Opalis Robot
39307	314	17	opalis-robot	Opalis Robot
39308	315	6	dpsi	DPSI
39309	315	17	dpsi	DPSI
39310	316	6	decauth	decAuth
39311	316	17	decauth	decAuth
39312	317	6	zannet	Zannet
39313	317	17	zannet	Zannet
39314	318	6	pkix-timestamp	PKIX TimeStamp
39315	318	17	pkix-timestamp	PKIX TimeStamp
39316	319	6	ptp-event	PTP Event
39317	319	17	ptp-event	PTP Event
39318	320	6	ptp-general	PTP General
39319	320	17	ptp-general	PTP General
39320	321	6	pip	PIP
39321	321	17	pip	PIP
39322	322	6	rtsps	RTSPS
39323	322	17	rtsps	RTSPS
39324	333	6	texar	Texar Security Port
39325	333	17	texar	Texar Security Port
39326	344	6	pdap	Propero Data Access Protocol
39327	344	17	pdap	Propero Data Access Protocol
39328	345	6	pawserv	Perf Analysis Workbench
39329	345	17	pawserv	Perf Analysis Workbench
39330	346	6	zserv	Zebra server
39331	346	17	zserv	Zebra server
39332	347	6	fatserv	Fatmen Server
39333	347	17	fatserv	Fatmen Server
39334	348	6	csi-sgwp	Cabletron Management Protocol
39335	348	17	csi-sgwp	Cabletron Management Protocol
39336	349	6	mftp	mftp
39337	349	17	mftp	mftp
39338	350	6	matip-type-a	MATIP Type A
39339	350	17	matip-type-a	MATIP Type A
39340	351	6	matip-type-b	MATIP Type B or bhoetty
39341	351	17	matip-type-b	MATIP Type B or bhoetty
39342	352	6	dtag-ste-sb	DTAG or bhoedap4
39343	352	17	dtag-ste-sb	DTAG or bhoedap4
39344	353	6	ndsauth	NDSAUTH
39345	353	17	ndsauth	NDSAUTH
39346	354	6	bh611	bh611
39347	354	17	bh611	bh611
39348	355	6	datex-asn	DATEX-ASN
39349	355	17	datex-asn	DATEX-ASN
39350	356	6	cloanto-net-1	Cloanto Net 1
39351	356	17	cloanto-net-1	Cloanto Net 1
39352	357	6	bhevent	bhevent
39353	357	17	bhevent	bhevent
39354	358	6	shrinkwrap	Shrinkwrap
39355	358	17	shrinkwrap	Shrinkwrap
39356	359	6	tenebris_nts	Tenebris Network Trace Service
39357	359	17	tenebris_nts	Tenebris Network Trace Service
39358	360	6	scoi2odialog	scoi2odialog
39359	360	17	scoi2odialog	scoi2odialog
39360	361	6	semantix	Semantix
39361	361	17	semantix	Semantix
39362	362	6	srssend	SRS Send
39363	362	17	srssend	SRS Send
39364	363	6	rsvp_tunnel	RSVP Tunnel
39365	363	17	rsvp_tunnel	RSVP Tunnel
39366	364	6	aurora_tunnel	Aurora CMGR
39367	364	17	aurora_tunnel	Aurora CMGR
39368	365	6	dtk	Deception Tool Kit (lame www.all.net)
39369	365	17	dtk	Deception Tool Kit (lame www.all.net)
39370	366	6	odmr	ODMR (On-Demand Mail Relay)
39371	366	17	odmr	ODMR (On-Demand Mail Relay)
39372	367	6	mortgageware	MortgageWare
39373	367	17	mortgageware	MortgageWare
39374	368	6	qbikgdp	QbikGDP
39375	368	17	qbikgdp	QbikGDP
39376	369	6	rpc2portmap	rpc2portmap
39377	369	17	rpc2portmap	rpc2portmap
39378	370	6	codaauth2	codaauth2
39379	370	17	codaauth2	codaauth2
39380	371	6	clearcase	Clearcase
39381	371	17	clearcase	Clearcase
39382	372	6	ulistserv / ulistproc	UNIX Listserv / ListProcessor
39383	372	17	ulistserv / ulistproc	UNIX Listserv / ListProcessor
39384	373	6	legent-1	Legent Corporation (now Computer Associates)
39385	373	17	legent-1	Legent Corporation (now Computer Associates)
39386	374	6	legent-2	Legent Corporation (now Computer Associates)
39387	374	17	legent-2	Legent Corporation (now Computer Associates)
39388	375	6	hassle	Hassle
39389	375	17	hassle	Hassle
39390	376	6	nip	Amiga Envoy Network Inquiry Protocol
39391	376	17	nip	Amiga Envoy Network Inquiry Protocol
39392	377	6	tnETOS	NEC Corporation
39393	377	17	tnETOS	NEC Corporation
39394	378	6	dsETOS	NEC Corporation
39395	378	17	dsETOS	NEC Corporation
39396	379	6	is99c	TIA/EIA/IS-99 modem client
39397	379	17	is99c	TIA/EIA/IS-99 modem client
39398	380	6	is99s	TIA/EIA/IS-99 modem server
39399	380	17	is99s	TIA/EIA/IS-99 modem server
39400	381	6	hp-collector	HP performance data collector
39401	381	17	hp-collector	HP performance data collector
39402	382	6	hp-managed-node	HP performance data managed node
39403	382	17	hp-managed-node	HP performance data managed node
39404	383	6	hp-alarm-mgr	HP performance data alarm manager
39405	383	17	hp-alarm-mgr	HP performance data alarm manager
39406	384	6	arns	A Remote Network Server System
39407	384	17	arns	A Remote Network Server System
39408	385	6	ibm-app	IBM Application
39409	385	17	ibm-app	IBM Application
39410	386	6	asa	ASA Message Router Object Def.
39411	386	17	asa	ASA Message Router Object Def.
39412	387	6	aurp	AppleTalk Update-Based Routing Protocol
39413	387	17	aurp	AppleTalk Update-Based Routing Protocol
39414	388	6	unidata-ldm	Unidata LDM Version 4
39415	388	17	unidata-ldm	Unidata LDM Version 4
39416	389	6	ldap	Lightweight Directory Access Protocol
39417	389	17	ldap	Lightweight Directory Access Protocol
39418	390	6	uis	UIS
39419	390	17	uis	UIS
39420	391	6	synotics-relay	SynOptics SNMP Relay Port
39421	391	17	synotics-relay	SynOptics SNMP Relay Port
39422	392	6	synotics-broker	SynOptics Port Broker Port
39423	392	17	synotics-broker	SynOptics Port Broker Port
39424	393	6	dis	Data Interpretation System
39425	393	17	dis	Data Interpretation System
39426	394	6	embl-ndt	EMBL Nucleic Data Transfer
39427	394	17	embl-ndt	EMBL Nucleic Data Transfer
39428	395	6	netcp	NETscout Control Protocol
39429	395	17	netcp	NETscout Control Protocol
39430	396	6	netware-ip	Novell Netware over IP
39431	396	17	netware-ip	Novell Netware over IP
39432	397	6	mptn	Multi Protocol Trans. Net.
39433	397	17	mptn	Multi Protocol Trans. Net.
39434	398	6	krypolan	Kryptolan
39435	398	17	krypolan	Kryptolan
39436	399	6	iso-tsap-c2	ISO Transport Class 2 Non-Control over TCO
39437	399	17	iso-tsap-c2	ISO Transport Class 2 Non-Control over TCO
39438	400	6	work-sol	Workstation Solutions
39439	400	17	work-sol	Workstation Solutions
39440	401	6	ups	Uninterruptible Power Supply
39441	401	17	ups	Uninterruptible Power Supply
39442	402	6	genie	Genie Protocol
39443	402	17	genie	Genie Protocol
39444	403	6	decap	decap
39445	403	17	decap	decap
39446	404	6	nced	nced
39447	404	17	nced	nced
39448	405	6	ncld	ncld
39449	405	17	ncld	ncld
39450	406	6	imsp	Interactive Mail Support Protocol
39451	406	17	imsp	Interactive Mail Support Protocol
39452	407	6	timbuktu	Timbuktu
39453	407	17	timbuktu	Timbuktu
39454	408	6	prm-sm	Prospero Resource Manager Sys. Man.
39455	408	17	prm-sm	Prospero Resource Manager Sys. Man.
39456	409	6	prm-nm	Prospero Resource Manager Node Man.
39457	409	17	prm-nm	Prospero Resource Manager Node Man.
39458	410	6	decladebug	DECLadebug Remote Debug Protocol
39459	410	17	decladebug	DECLadebug Remote Debug Protocol
39460	411	6	rmt	Remote MT Protocol
39461	411	17	rmt	Remote MT Protocol
39462	412	6	synoptics-trap	Trap Convention Port
39463	412	17	synoptics-trap	Trap Convention Port
39464	413	6	smsp	SMSP
39465	413	17	smsp	SMSP
39466	414	6	infoseek	InfoSeek
39467	414	17	infoseek	InfoSeek
39468	415	6	bnet	BNet
39469	415	17	bnet	BNet
39470	416	6	silverplatter	Silverplatter
39471	416	17	silverplatter	Silverplatter
39472	417	6	onmux	Onmux
39473	417	17	onmux	Onmux
39474	418	6	hyper-g	Hyper-G
39475	418	17	hyper-g	Hyper-G
39476	419	6	ariel1	Ariel
39477	419	17	ariel1	Ariel
39478	420	6	smpte	SMPTE
39479	420	17	smpte	SMPTE
39480	421	6	ariel2	Ariel
39481	421	17	ariel2	Ariel
39482	422	6	ariel3	Ariel
39483	422	17	ariel3	Ariel
39484	423	6	opc-job-start	IBM Operations Planning and Control Start
39485	423	17	opc-job-start	IBM Operations Planning and Control Start
39486	424	6	opc-job-track	IBM Operations Planning and Control Track
39487	424	17	opc-job-track	IBM Operations Planning and Control Track
39488	425	6	icad-el	ICAD
39489	425	17	icad-el	ICAD
39490	426	6	smartsdp	smartsdp
39491	426	17	smartsdp	smartsdp
39492	427	6	svrloc	Server Location
39493	427	17	svrloc	Server Location
39494	428	6	ocs_cmu	OCS_CMU
39495	428	17	ocs_cmu	OCS_CMU
39496	429	6	ocs_amu	OCS_AMU
39497	429	17	ocs_amu	OCS_AMU
39498	430	6	utmpsd	UTMPSD
39499	430	17	utmpsd	UTMPSD
39500	431	6	utmpcd	UTMPCD
39501	431	17	utmpcd	UTMPCD
39502	432	6	iasd	IASD
39503	432	17	iasd	IASD
39504	433	6	nnsp	usenet, Network News Transfer
39505	433	17	nnsp	usenet, Network News Transfer
39506	434	6	mobile-agent	MobileIP-Agent
39507	434	17	mobile-agent	MobileIP-Agent
39508	435	6	mobile-mn	MobilIP-MN
39509	435	17	mobile-mn	MobilIP-MN
39510	436	6	dna-cml	DNA-CML
39511	436	17	dna-cml	DNA-CML
39512	437	6	comscm	comscm
39513	437	17	comscm	comscm
39514	438	6	dsfgw	dsfgw
39515	438	17	dsfgw	dsfgw
39516	439	6	dasp	dasp
39517	439	17	dasp	dasp
39518	440	6	sgcp	sgcp
39519	440	17	sgcp	sgcp
39520	441	6	decvms-sysmgt	decvms-sysmgt
39521	441	17	decvms-sysmgt	decvms-sysmgt
39522	442	6	cvc_hostd	cvc_hostd
39523	442	17	cvc_hostd	cvc_hostd
39524	443	6	https	http protocol over TLS/SSL
39525	443	17	https	http protocol over TLS/SSL
39526	444	6	snpp	Simple Network Paging Protocol
39527	444	17	snpp	Simple Network Paging Protocol
39528	445	6	microsoft-ds	Microsoft-DS
39529	445	17	microsoft-ds	Microsoft-DS
39530	446	6	ddm-rdb	DDM-RDB
39531	446	17	ddm-rdb	DDM-RDB
39532	447	6	ddm-dfm	DDM-RFM
39533	447	17	ddm-dfm	DDM-RFM
39534	448	6	ddm-ssl	aam-byte
39535	448	17	ddm-ssl	aam-byte
39536	449	6	as-servermap	AS Server Mapper
39537	449	17	as-servermap	AS Server Mapper
39538	450	6	tserver	TServer
39539	450	17	tserver	TServer
39540	451	6	sfs-smp-net	Cray Network Semaphore server
39541	451	17	sfs-smp-net	Cray Network Semaphore server
39542	452	6	sfs-config	Cray SFS config server
39543	452	17	sfs-config	Cray SFS config server
39544	453	6	creativeserver	CreativeServer
39545	453	17	creativeserver	CreativeServer
39546	454	6	contentserver	ContentServer
39547	454	17	contentserver	ContentServer
39548	455	6	creativepartnr	CreativePartnr
39549	455	17	creativepartnr	CreativePartnr
39550	456	6	macon-tcp/udp	macon-tcp/udp
39551	456	17	macon-tcp/udp	macon-tcp/udp
39552	456	6	HackerParadise	Hackers Paradise Trojan
39553	456	17	HackerParadise	Hackers Paradise Trojan
39554	457	6	scohelp	scohelp
39555	457	17	scohelp	scohelp
39556	458	6	appleqtc	Apple Quick Time TV/Conferencing
39557	458	17	appleqtc	Apple Quick Time TV/Conferencing
39558	459	6	ampr-rcmd	ampr-rcmd
39559	459	17	ampr-rcmd	ampr-rcmd
39560	460	6	skronk	skronk
39561	460	17	skronk	skronk
39562	461	6	datasurfsrv	DataRampSrv
39563	461	17	datasurfsrv	DataRampSrv
39564	462	6	datasurfsrvsec	DataRampSrvSec
39565	462	17	datasurfsrvsec	DataRampSrvSec
39566	463	6	alpes	alpes
39567	463	17	alpes	alpes
39568	464	6	kpasswd	kerberos (v5)
39569	464	17	kpasswd	kerberos (v5)
39570	465	6	smtps	smtp protocol over TLS/SSL (was ssmtp)
39571	465	17	smtps	smtp protocol over TLS/SSL (was ssmtp)
39572	466	6	digital-vrc	digital-vrc
39573	466	17	digital-vrc	digital-vrc
39574	467	6	mylex-mapd	mylex-mapd
39575	467	17	mylex-mapd	mylex-mapd
39576	468	6	photuris	proturis
39577	468	17	photuris	proturis
39578	469	6	rcp	Radio Control Protocol
39579	469	17	rcp	Radio Control Protocol
39580	470	6	scx-proxy	scx-proxy
39581	470	17	scx-proxy	scx-proxy
39582	471	6	mondex	Mondex
39583	471	17	mondex	Mondex
39584	472	6	ljk-login	ljk-login
39585	472	17	ljk-login	ljk-login
39586	473	6	hybrid-pop	hybrid-pop
39587	473	17	hybrid-pop	hybrid-pop
39588	474	6	tn-tl-w1	tn-tl-w1
39589	474	17	tn-tl-w1	tn-tl-w1
39590	475	6	tcpnethaspsrv	tcpnethaspsrv
39591	475	17	tcpnethaspsrv	tcpnethaspsrv
39592	476	6	tn-tl-fd1	tn-tl-fd1
39593	476	17	tn-tl-fd1	tn-tl-fd1
39594	477	6	ss7ns	ss7ns
39595	477	17	ss7ns	ss7ns
39596	478	6	spsc	spsc
39597	478	17	spsc	spsc
39598	479	6	iafserver	iafserver
39599	479	17	iafserver	iafserver
39600	480	6	iafdbase	iafdbase
39601	480	17	iafdbase	iafdbase
39602	481	6	des/ph	Ph service
39603	481	17	des/ph	Ph service
39604	482	6	bgs-nsi/xlog	
39605	482	17	bgs-nsi/xlog	
39606	483	6	ulpnet	ulpnet
39607	483	17	ulpnet	ulpnet
39608	484	6	integra-sme	Integra Software Management Environment
39609	484	17	integra-sme	Integra Software Management Environment
39610	485	6	powerburst	Air Soft Power Burst
39611	485	17	powerburst	Air Soft Power Burst
39612	486	6	sstat/avian	
39613	486	17	sstat/avian	
39614	487	6	saft	saft Simple Asynchronous File Transfer
39615	487	17	saft	saft Simple Asynchronous File Transfer
39616	488	6	gss-http	gss-http
39617	488	17	gss-http	gss-http
39618	489	6	nest-protocol	nest-protocol
39619	489	17	nest-protocol	nest-protocol
39620	490	6	micom-pfs	micom-pfs
39621	490	17	micom-pfs	micom-pfs
39622	491	6	go-login	go-login
39623	491	17	go-login	go-login
39624	492	6	ticf-1	Transport Independent Convergence for FNA
39625	492	17	ticf-1	Transport Independent Convergence for FNA
39626	493	6	ticf-2	Transport Independent Convergence for FNA
39627	493	17	ticf-2	Transport Independent Convergence for FNA
39628	494	6	pov-ray	POV-Ray
39629	494	17	pov-ray	POV-Ray
39630	495	6	intecourier	intecourier
39631	495	17	intecourier	intecourier
39632	496	6	pim-rp-disc	PIM-RP-DISC
39633	496	17	pim-rp-disc	PIM-RP-DISC
39634	497	6	dantz	dantz
39635	497	17	dantz	dantz
39636	498	6	siam	siam
39637	498	17	siam	siam
39638	499	6	iso-ill	ISO ILL Protocol
39639	499	17	iso-ill	ISO ILL Protocol
39640	500	6	isakmp	internet Secuirty Association and Key management protocol
39641	500	17	isakmp	internet Secuirty Association and Key management protocol
39642	501	6	stmf	STMF
39643	501	17	stmf	STMF
39644	502	6	asa-appl-proto	asa-appl-proto
39645	502	17	asa-appl-proto	asa-appl-proto
39646	503	6	intrinsa	Intrinsa
39647	503	17	intrinsa	Intrinsa
39648	504	6	citadel	citadel
39649	504	17	citadel	citadel
39650	505	6	mailbox-lm	mailbox-lm
39651	505	17	mailbox-lm	mailbox-lm
39652	506	6	ohimsrv	ohimsrv
39653	506	17	ohimsrv	ohimsrv
39654	507	6	crs	crs
39655	507	17	crs	crs
39656	508	6	xvttp	xvttp
39657	508	17	xvttp	xvttp
39658	509	6	snare	snare
39659	509	17	snare	snare
39660	510	6	fcp	FirstClass Protocol
39661	510	17	fcp	FirstClass Protocol
39662	511	6	passgo	PassGo
39663	511	17	passgo	PassGo
39664	512	6	print / exec	BSD rexecd, Windows NT Server and Windows NT Workstation version 4.0 can send LPD client print jobs from any available reserved port between 512 and 1023. See also description for ports 721 to 73 1
39665	512	17	biff	comsat
39666	513	6	login	BSD rlogind
39667	513	17	who	BSD rwhod
39668	514	6	shell	BSD rshd
39669	514	17	syslog	BSD syslogd
39670	515	6	printer	Spooler. The print server LP1 service will listen on tcp port 515 for incoming connections
39671	515	17	printer	Spooler. The print server LP1 service will listen on tcp port 515 for incoming connections
39672	516	6	videotex	videotex
39673	516	17	videotex	videotex
39674	517	6	talk	Like tenex link, but across computers, BSD talkd
39675	517	17	talk	Like tenex link, but across computers, BSD talkd
39676	518	6	ntalk	talkd
39677	518	17	ntalk	talkd
39678	519	6	utime	Unixtime
39679	519	17	utime	Unixtime
39680	520	6	efs	Extended file name server
39681	520	17	route	Local routing process (on site); uses variant of Xerox NS routing information protocol;alias=router routed
39682	521	6	ripng	ripng
39683	521	17	ripng	ripng
39684	522	6	ulp	User Location Service
39685	522	17	ulp	User Location Service
39686	523	6	ibm-db2	IBM-DB2
39687	523	17	ibm-db2	IBM-DB2
39688	524	6	ncp	NCP
39689	524	17	ncp	NCP
39690	525	6	timed	Timeserver
39691	525	17	timed	Timeserver
39692	526	6	tempo	Newdate
39693	526	17	tempo	Newdate
39694	527	6	stx	Stock IXChange
39695	527	17	stx	Stock IXChange
39696	528	6	custix	Customer IXChange
39697	528	17	custix	Customer IXChange
39698	529	6	irc-serv	IRC-SERV
39699	529	17	irc-serv	IRC-SERV
39700	530	6	courier	RPC
39701	530	17	courier	RPC
39702	531	6	conference	Chat
39703	531	17	rvd-control	MIT disk
39704	531	6	irc	IRC
39705	532	6	netnews	Readnews
39706	532	17	netnews	Readnews
39707	533	6	netwall	For emergency broadcasts
39708	533	17	netwall	For emergency broadcasts
39709	534	6	mm-admin	MegaMedia Admin
39710	534	17	mm-admin	MegaMedia Admin
39711	535	6	iiop	iiop
39712	535	17	iiop	iiop
39713	536	6	opalis-rdv	opalis-rdv
39714	536	17	opalis-rdv	opalis-rdv
39715	537	6	nmsp	Networked Media Streaming Protocol
39716	537	17	nmsp	Networked Media Streaming Protocol
39717	538	6	gdomap	gdomap
39718	538	17	gdomap	gdomap
39719	539	6	apertus-ldp	Apertus Technologies Load Determination
39720	539	17	apertus-ldp	Apertus Technologies Load Determination
39721	540	6	uucp	Uucpd
39722	540	17	uucp	Uucpd
39723	541	6	uucp-rlogin	uucp-rlogin
39724	541	17	uucp-rlogin	uucp-rlogin
39725	542	6	commerce	commerce
39726	542	17	commerce	commerce
39727	543	6	klogin	kerberos (v4/v5)
39728	543	17	klogin	kerberos (v4/v5)
39729	544	6	kshell	kerberos (v4/v5), Krcmd; alias=cmd
39730	544	17	kshell	kerberos (v4/v5), Krcmd; alias=cmd
39731	545	6	ekshal	kerberos encryptd remote shell -kfall
39732	545	17	appleqtsrvr	Apple Quick Time Server
39733	546	6	dhcpv6-client	DHCPv6 Client
39734	546	17	dhcpv6-client	DHCPv6 Client
39735	547	6	dhcpv6-server	DHCPv6 Server
39736	547	17	dhcpv6-server	DHCPv6 Server
39737	548	6	afpovertcp	AFP over TCP
39738	548	17	afpovertcp	AFP over TCP
39739	549	6	ifdp	IDFP
39740	549	17	ifdp	IDFP
39741	550	6	new-rwho	New-who
39742	550	17	new-rwho	New-who
39743	551	6	cybercash	cybercash
39744	551	17	cybercash	cybercash
39745	552	6	deviceshare	deviceshare
39746	552	17	deviceshare	deviceshare
39747	553	6	pirp	pirp
39748	553	17	pirp	pirp
39749	554	6	rtsp	Real Time Stream Control Protocol
39750	554	17	rtsp	Real Time Stream Control Protocol
39751	555	6	dsf	phAse Zero(Stealth Spy) Trojan (Win 9x, NT) as well as dsf
45168	53001	17	remoteshut	Remote Shutdown Trojan Horse
39752	555	17	dsf	phAse Zero(Stealth Spy) Trojan (Win 9x, NT) as well as dsf
39753	556	6	remotefs	Rfs server; alias=rfs_server rfs, Brunhoff remote filesystem
39754	556	17	remotefs	Rfs server; alias=rfs_server rfs, Brunhoff remote filesystem
39755	557	6	openvms-sysipc	openvms-sysipc
39756	557	17	openvms-sysipc	openvms-sysipc
39757	558	6	sdnskmp	SDNSKMP
39758	558	17	sdnskmp	SDNSKMP
39759	559	6	teedtap	TEEDTAP
39760	559	17	teedtap	TEEDTAP
39761	560	6	rmonitor	Rmonitord
39762	560	17	rmonitor	Rmonitord
39763	561	6	monitor	
39764	561	17	monitor	
39765	562	6	chshell	Chcmd
39766	562	17	chshell	Chcmd
39767	563	6	nntps	nntp protocol over TLS/SSL (was snntp)
39768	563	17	nntps	nntp protocol over TLS/SSL (was snntp)
39769	564	6	9pfs	Plan 9 file service
39770	564	17	9pfs	Plan 9 file service
39771	565	6	whoami	Whoami
39772	565	17	whoami	Whoami
39773	566	6	streettalk	streettalk
39774	566	17	streettalk	streettalk
39775	567	6	banyan-rpc	banyan-rpc
39776	567	17	banyan-rpc	banyan-rpc
39777	568	6	ms-shuttle	Microsoft Shuttle
39778	568	17	ms-shuttle	Microsoft Shuttle
39779	569	6	ms-rome	Microsoft Rome
39780	569	17	ms-rome	Microsoft Rome
39781	570	6	meter	Demon
39782	570	17	meter	Demon
39783	571	6	umeter	Udemon
39784	571	17	umeter	Udemon
39785	572	6	sonar	sonar
39786	572	17	sonar	sonar
39787	573	6	banyan-vip	banyan-vip
39788	573	17	banyan-vip	banyan-vip
39789	574	6	ftp-agent	FTP Software Agent System
39790	574	17	ftp-agent	FTP Software Agent System
39791	575	6	vemmi	VEMMI
39792	575	17	vemmi	VEMMI
39793	576	6	ipcd	ipcd
39794	576	17	ipcd	ipcd
39795	577	6	vnas	vnas
39796	577	17	vnas	vnas
39797	578	6	ipdd	ipdd
39798	578	17	ipdd	ipdd
39799	579	6	decbsrv	decbsrv
39800	579	17	decbsrv	decbsrv
39801	580	6	sntp-heartbeat	SNTP HEARTBEAT
39802	580	17	sntp-heartbeat	SNTP HEARTBEAT
39803	581	6	bdp	Bundle Discovery Protocol
39804	581	17	bdp	Bundle Discovery Protocol
39805	582	6	scc-security	SCC Security
39806	582	17	scc-security	SCC Security
39807	583	6	philips-vc	Philips Video-Conferencing
39808	583	17	philips-vc	Philips Video-Conferencing
39809	584	6	keyserver	Key Server
39810	584	17	keyserver	Key Server
39811	585	6	imap4-ssl	IMAP4+SSL (Use of 585 is not recommended, use 993 instead)
39812	585	17	imap4-ssl	IMAP4+SSL (Use of 585 is not recommended, use 993 instead)
39813	586	6	password-chg	Password Change
39814	586	17	password-chg	Password Change
39815	587	6	submission	Submission
39816	587	17	submission	Submission
39817	588	6	cal	CAL
39818	588	17	cal	CAL
39819	589	6	eyelink	EyeLink
39820	589	17	eyelink	EyeLink
39821	590	6	tns-cml	TNS CML
39822	590	17	tns-cml	TNS CML
39823	591	6	http-alt	Filemaker - HTTP Alternative
39824	591	17	http-alt	Filemaker - HTTP Alternative
39825	592	6	eudora-set	Eudora Set
39826	592	17	eudora-set	Eudora Set
39827	593	6	http-rpc-epmap	HTTP RPC Ep Map
39828	593	17	http-rpc-epmap	HTTP RPC Ep Map
39829	594	6	tpip	TPIP
39830	594	17	tpip	TPIP
39831	595	6	cab-protocol	CAB Protocol
39832	595	17	cab-protocol	CAB Protocol
39833	596	6	smsd	SMSD
39834	596	17	smsd	SMSD
39835	597	6	ptcnameservice	PTC Name Service
39836	597	17	ptcnameservice	PTC Name Service
39837	598	6	sco-websrvrmg3	SCO Web Server Manager 3
39838	598	17	sco-websrvrmg3	SCO Web Server Manager 3
39839	599	6	acp	Aeolon Core Protocol
39840	599	17	acp	Aeolon Core Protocol
39841	600	6	ipcserver	Sun IPC server
39842	600	17	ipcserver	Sun IPC server
39843	606	6	urm	Cray Unified Resource Manager
39844	606	17	urm	Cray Unified Resource Manager
39845	607	6	nqs	Nqs
39846	607	17	nqs	Nqs
39847	608	6	sift-uft	Sender-Initiated/Unsolicited File Transfer
39848	608	17	sift-uft	Sender-Initiated/Unsolicited File Transfer
39849	609	6	npmp-trap	npmp-trap @microsoft.com
39850	609	17	npmp-trap	npmp-trap @microsoft.com
39851	610	6	npmp-local	npmp-local @microsoft.com
39852	610	17	npmp-local	npmp-local @microsoft.com
39853	611	6	npmp-gui	npmp-gui @microsoft.com
39854	611	17	npmp-gui	npmp-gui @microsoft.com
39855	612	6	hmmp-ind	HMMP Indication @microsoft.com
39856	612	17	hmmp-ind	HMMP Indication @microsoft.com
39857	613	6	hmmp-op	HMMP Operation@microsoft.com
39858	613	17	hmmp-op	HMMP Operation@microsoft.com
39859	614	6	sshell	SSLshell @quick.com.au
39860	614	17	sshell	SSLshell @quick.com.au
39861	615	6	sco-inetmgr	Internet Configuration Manager
39862	615	17	sco-inetmgr	Internet Configuration Manager
39863	616	6	sco-sysmgr	SCO System Administration Server
39864	616	17	sco-sysmgr	SCO System Administration Server
39865	617	6	sco-dtmgr	SCO Desktop Administration Server
39866	617	17	sco-dtmgr	SCO Desktop Administration Server
39867	618	6	dei-icda	DEI-ICDA @Quetico.tbaytel.net
39868	618	17	dei-icda	DEI-ICDA @Quetico.tbaytel.net
39869	619	6	digital-evm	Digital EVM
39870	620	6	sco-websrvrmgr	SCO WebServer Manager
39871	620	17	sco-websrvrmgr	SCO WebServer Manager
39872	621	6	escp-ip	ESCP @pobox.com
39873	621	17	escp-ip	ESCP @pobox.com
39874	622	6	collaborator	Collaborator @opteamasoft.com
39875	622	17	collaborator	Collaborator @opteamasoft.com
39876	623	6	aux_bus_shunt	Aux Bus Shunt @ccm.jf.intel.com
39877	623	17	aux_bus_shunt	Aux Bus Shunt @ccm.jf.intel.com
39878	624	6	cryptoadmin	Crypto Admin @cyberus.ca
39879	624	17	cryptoadmin	Crypto Admin @cyberus.ca
39880	625	6	dec_dlm	DEC DLM
39881	625	17	dec_dlm	DEC DLM
39882	626	6	asia	ASIA @apple.com
39883	626	17	asia	ASIA @apple.com
39884	627	6	passgo-tivioli	CKS & TIVIOLI @ckshq.com
39885	627	17	passgo-tivioli	CKS & TIVIOLI @ckshq.com
39886	628	6	qmqp	Qmail Quick mail Queueing
39887	628	17	qmqp	Qmail Quick mail Queueing
39888	629	6	3com-amp3	3Com AMP3
39889	629	17	3com-amp3	3Com AMP3
39890	630	6	rda	RDA
39891	630	17	rda	RDA
39892	631	6	ipp	IPP (Internet Printing Protocol)
39893	631	17	ipp	IPP (Internet Printing Protocol)
39894	632	6	bmpp	bmpp
39895	632	17	bmpp	bmpp
39896	633	6	servstat	Service Status update (Sterling Software)
39897	633	17	servstat	Service Status update (Sterling Software)
39898	634	6	ginad	ginad @eis.calstate.edu
39899	634	17	ginad	ginad @eis.calstate.edu
39900	635	6	rlzdbase	RLZ DBase @netcom.com
39901	635	17	rlzdbase	RLZ DBase @netcom.com
39902	635	17	mount	NFS mount Service
39903	636	6	ldaps	ldap protocol over TLS/SSL (was sldap) @xcert.com
39904	636	17	ldaps	ldap protocol over TLS/SSL (was sldap) @xcert.com
39905	637	6	lanserver	lanserver @VNET.IBM.COM
39906	637	17	lanserver	lanserver @VNET.IBM.COM
39907	638	6	mcns-sec	mcns-sec
39908	638	17	mcns-sec	mcns-sec
39909	639	6	msdp	MSDP
39910	639	17	msdp	MSDP
39911	640	6	entrust-sps	entrust-sps
39912	640	17	entrust-sps	entrust-sps
39913	640	17	pcnfs	PC-NFS DOS Authentication
39914	641	6	repcmd	repcmd
39915	641	17	repcmd	repcmd
39916	642	6	esro-emsdp	ESPR-EMSDP V1.3
39917	642	17	esro-emsdp	ESPR-EMSDP V1.3
39918	643	6	sanity	SANity
39919	643	17	sanity	SANity
39920	644	6	dwr	dwr
39921	644	17	dwr	dwr
39922	645	6	pssc	PSSC
39923	645	17	pssc	PSSC
39924	646	6	ldp	LDP
39925	646	17	ldp	LDP
39926	647	6	dhcp-failover	DHCP Failover
39927	647	17	dhcp-failover	DHCP Failover
39928	648	6	rrp	Registry Registrar Protocol (RRP)
39929	648	17	rrp	Registry Registrar Protocol (RRP)
39930	649	6	aminet	Aminet
39931	649	17	aminet	Aminet
39932	650	6	obex	OBEX
39933	650	17	obex	OBEX
39934	650	17	bwnfs	BW-NFS DOS Authentication
39935	651	6	ieee-mms	IEEE MMS
39936	651	17	ieee-mms	IEEE MMS
39937	652	6	udlr-dtcp	UDLR_DTCP
39938	652	17	udlr-dtcp	UDLR_DTCP
39939	653	6	repscmd	RepCmd
39940	653	17	repscmd	RepCmd
39941	654	6	aodv	AODV
39942	654	17	aodv	AODV
39943	655	6	tinc	TINC
39944	655	17	tinc	TINC
39945	656	6	spmp	SPMP
39946	656	17	spmp	SPMP
39947	657	6	rmc	RMC
39948	657	17	rmc	RMC
39949	658	6	tenfold	TenFold
39950	658	17	tenfold	TenFold
39951	659	6	url-rendezous	URL Rendezous
39952	659	17	url-rendezous	URL Rendezous
39953	660	6	mac-srvr-admin	MacOS Server Admin
39954	660	17	mac-srvr-admin	MacOS Server Admin
39955	661	6	hap	HAP
39956	661	17	hap	HAP
39957	662	6	pftp	PFTP
39958	662	17	pftp	PFTP
39959	663	6	purenoise	PureNoise
39960	663	17	purenoise	PureNoise
39961	664	6	secure-aux-bus	Secure Aux Bus
39962	664	17	secure-aux-bus	Secure Aux Bus
39963	665	6	sun-dr	Sun DR
39964	665	17	sun-dr	Sun DR
39965	666	6	mdqs	
39966	666	17	mdqs	
39967	666	6	ftpattack	FTP Attack Trojan
39968	666	17	ftpattack	FTP Attack Trojan
39969	666	6	satanz	Satanz Backdoor Trojan
39970	666	17	satanz	Satanz Backdoor Trojan
39971	666	6	doom	Doom Id Software
39972	666	17	doom	Doom Id Software
39973	667	6	disclose	campaign contribution disclosures-SDR Technologies @lambda.com
39974	667	17	disclose	campaign contribution disclosures-SDR Technologies @lambda.com
39975	668	6	mecomm	MeComm @esd1.esd.de
39976	668	17	mecomm	MeComm @esd1.esd.de
39977	669	6	meregister	MeRegister
39978	669	17	meregister	MeRegister
39979	670	6	vacdsm-sws	VACDSM-SWS
39980	670	17	vacdsm-sws	VACDSM-SWS
39981	671	6	vacdsm-app	VACDSM-APP
39982	671	17	vacdsm-app	VACDSM-APP
39983	672	6	vpps-qua	VPPS-QUA
39984	672	17	vpps-qua	VPPS-QUA
39985	673	6	cimplex	CIMPLEX @cesi.com
39986	673	17	cimplex	CIMPLEX @cesi.com
39987	674	6	acap	ACAP @innosoft.com
39988	674	17	acap	ACAP @innosoft.com
39989	675	6	dctp	DCTP @ansa.co.uk
39990	675	17	dctp	DCTP @ansa.co.uk
39991	676	6	vpps-via	VPPS Via @cesi.com
39992	676	17	vpps-via	VPPS Via @cesi.com
39993	677	6	vpp	Virtual Presense Protocol
39994	677	17	vpp	Virtual Presense Protocol
39995	678	6	ggf-ncp	GNU Gereration Foundation NCP
39996	678	17	ggf-ncp	GNU Gereration Foundation NCP
39997	679	6	mrm	MRM
39998	679	17	mrm	MRM
39999	680	6	entrust-aaas	entrust-aas
40000	680	17	entrust-aaas	entrust-aas
40001	681	6	entrust-aams	entrust-aams
40002	681	17	entrust-aams	entrust-aams
40003	682	6	xfr	XFR
40004	682	17	xfr	XFR
40005	683	6	corba-iiop	COBRA IIOP
40006	683	17	corba-iiop	COBRA IIOP
40007	684	6	corbra-iiop-ssl	COBRA IIOP SSL
40008	684	17	corbra-iiop-ssl	COBRA IIOP SSL
40009	685	6	mdc-portmapper	MDC Port Mapper
40010	685	17	mdc-portmapper	MDC Port Mapper
40011	686	6	hcp-wismar	Hardware Control Protocol Wismar
40012	686	17	hcp-wismar	Hardware Control Protocol Wismar
40013	687	6	asipregistry	AppleShare IP Registry
40014	687	17	asipregistry	AppleShare IP Registry
40015	688	6	realm-rusd	REALM-RUSD
40016	688	17	realm-rusd	REALM-RUSD
40017	689	6	nmap	NMAP
40018	689	17	nmap	NMAP
40019	690	6	vatp	VATP
40020	690	17	vatp	VATP
40021	691	6	msexch-routing	MS Exchange Routing
40022	691	17	msexch-routing	MS Exchange Routing
40023	692	6	hyperwave-isp	Hyperwave-ISP
40024	692	17	hyperwave-isp	Hyperwave-ISP
40025	693	6	connendp	connendp
40026	693	17	connendp	connendp
40027	694	6	ha-cluster	ha-cluster
40028	694	17	ha-cluster	ha-cluster
40029	695	6	ieee-mms-ssl	IEEE-MMS-SSL
40030	695	17	ieee-mms-ssl	IEEE-MMS-SSL
40031	696	6	rushd	RUSHD
40032	696	17	rushd	RUSHD
40033	700	6	bphone	BuddyPhone Internet telephony as well as the TCP range 5000-5111
40034	700	17	bphone	BuddyPhone Internet telephony as well as the TCP range 5000-5111
40035	704	6	elcsd	Errlog copy/server daemon
40036	704	17	elcsd	Errlog copy/server daemon
40037	705	6	agentx	AgentX for SNMP @acec.com
40038	705	17	agentx	AgentX for SNMP @acec.com
40039	706	0		Unassigned
40040	707	6	borland-dsj	Borland DSJ
40041	707	17	borland-dsj	Borland DSJ
40042	708	0		Unassigned
40043	709	6	entrust-kmsh	Entrust Key Management Service Handler, Nortel DES auth network see 389/tcp
40044	709	17	entrust-kmsh	Entrust Key Management Service Handler, Nortel DES auth network see 389/tcp
40045	710	6	entrust-ash	Entrust Administration Service Handler @entrust.com
40046	710	17	entrust-ash	Entrust Administration Service Handler @entrust.com
40047	711	6	cisco-tdp	Cisco TDP
40048	711	17	cisco-tdp	Cisco TDP
40049	729	6	netviewdm1	IBM NetView DM/6000 Server/Client
40050	729	17	netviewdm1	IBM NetView DM/6000 Server/Client
40051	730	6	netviewdm2	IBM NetView DM/6000 send/tcp
40052	730	17	netviewdm2	IBM NetView DM/6000 send/tcp
40053	731	6	netviewdm3	IBM NetView DM/6000 receive/tcp
40054	731	17	netviewdm3	IBM NetView DM/6000 receive/tcp
40055	740	6	netcp (old)	NETscout Control Protocol (old)
40056	740	17	netcp (old)	NETscout Control Protocol (old)
40057	741	6	netgw	NetGW
40058	741	17	netgw	NetGW
40059	742	6	netrcs	Network based Rev. Cont. Sys.
40060	742	17	netrcs	Network based Rev. Cont. Sys.
40061	744	6	flexlm	Flexible License Manager
40062	744	17	flexlm	Flexible License Manager
40063	747	6	fujitsu-dev	Fujitsu Device Control
40064	747	17	fujitsu-dev	Fujitsu Device Control
40065	748	6	ris-cm	Russell Info Sci Calendar Manager
40066	748	17	ris-cm	Russell Info Sci Calendar Manager
40067	749	6	kerberos-adm	Kerberos admin/changepw (v5)
40068	749	17	kerberos-adm	Kerberos admin/changepw (v5)
40069	750	17	kerberos-iv	Kerberos authentication (v4); alias=kdc
40070	750	6	rfile	rfile
40071	750	17	rfile	rfile
40072	750	17	loadav	
40073	751	6	kerberos-master	Kerberos "kadmin" (v4)
40074	751	17	kerberos-master	Kerberos "kadmin" (v4)
40075	751	6	pump	pump
40076	751	17	pump	pump
40077	752	6	qrh	Kerberos password server
40078	752	17	qrh	Kerberos password server
40079	753	6	rrh	Kerberos userreg server
40080	753	17	rrh	Kerberos userreg server
40081	754	6	krb_prop	Kerberos/v5 server propagation
40082	754	6	tell	Send
40083	754	17	tell	Send
40084	758	6	nlogin	
40085	758	17	nlogin	
40086	759	6	con	
40087	759	17	con	
40088	760	17	ns	
40089	760	6	krbupdate	kreg, kerberos/4 registration
40090	761	17	rxe	
40091	761	6	kpasswd	kpwd, Kerberos/4 password
40092	762	6	quotad	
40093	762	17	quotad	
40094	763	6	cycleserv	
40095	763	17	cycleserv	
40096	764	6	omserv	
40097	764	17	omserv	
40098	765	6	webster	
40099	765	17	webster	
40100	767	6	phonebook	Phone
40101	767	17	phonebook	Phone
40102	769	6	vid	
40103	769	17	vid	
40104	770	6	cadlock	
40105	770	17	cadlock	
40106	771	6	rtip	
40107	771	17	rtip	
40108	772	6	cycleserv2	
40109	772	17	cycleserv2	
40110	773	6	submit	
40111	773	17	notify	
40112	774	6	rpasswd	
40113	774	17	acmaint_dbd	
40114	775	6	entomb	
40115	775	17	acmaint_transd	
40116	776	6	wpages	
40117	776	17	wpages	
40118	777	6	multiling-http	Muiltiling HTTP
40119	777	17	multiling-http	Muiltiling HTTP
40120	780	6	wpgs	
40121	780	17	wpgs	
40122	781	6	hp-collector	HP performance data collector
40123	781	17	hp-collector	HP performance data collector
40124	782	6	hp-managed- node	HP performance data managed node
40125	782	17	hp-managed- node	HP performance data managed node
40126	783	6	hp-alarm-mgr	HP performance data alarm manager
40127	783	17	hp-alarm-mgr	HP performance data alarm manager
40128	786	6	concert	concert
40129	786	17	concert	concert
40130	799	6	controlit	
40131	800	6	mdbs_daemon	
40132	800	17	mdbs_daemon	
40133	801	6	device	
40134	801	17	device	
40135	810	6	fcp-udp	FCP Datagram
40136	810	17	fcp-udp	FCP Datagram
40137	828	6	itm-mcell-s	itm-mcell-s
40138	828	17	itm-mcell-s	itm-mcell-s
40139	829	6	pkix-3-ca-ra	PKIX-3 CA/RA
40140	829	17	pkix-3-ca-ra	PKIX-3 CA/RA
40141	871	6	supfilesrv	SUP server
40142	872	0		Unassigned
40143	873	6	rsync	rsync
40144	873	17	rsync	rsync
40145	886	6	iclcnet-locate	ICL coNETion locate service
40146	886	17	iclcnet-locate	ICL coNETion locate service
40147	887	6	iclcnet_svinfo	ICL coNETion server info
40148	887	17	iclcnet_svinfo	ICL coNETion server info
40149	888	6	accessbuilder	AccessBuilder @3com.com
40150	888	17	accessbuilder	AccessBuilder @3com.com
40151	888	6	cddbp	CD Database Protocol @moonsoft.com
40152	888	6	erlogin	Logon and environment passing
40153	901	6	smpnameres	SMPNAMERES, Samba Swat, IIS RealSecure
40154	901	17	smpnameres	SMPNAMERES, Samba Swat, IIS RealSecure
40155	902	6	ideafarm-chat	IDEAFARM-CHAT
40156	902	17	ideafarm-chat	IDEAFARM-CHAT
40157	903	6	ideafarm-catch	IDEAFARM-CATCH
40158	903	17	ideafarm-catch	IDEAFARM-CATCH
40159	911	6	xact-backup	xact-backup @xactlabs.com
40160	911	17	xact-backup	xact-backup @xactlabs.com
40161	989	6	ftps-data	FTP protocol, data, over TLS/SSL @consensus.com
40162	989	17	ftps-data	FTP protocol, data, over TLS/SSL @consensus.com
40163	990	6	ftps	FTP protocol, control, over TLS/SSL @consensus.com
40164	990	17	ftps	FTP protocol, control, over TLS/SSL @consensus.com
40165	991	6	nas	Netnews Administration System @fu-berlin.de
40166	991	17	nas	Netnews Administration System @fu-berlin.de
40167	992	6	telnets	Telnet protocol over TLS/SSL @consensus.com
40168	992	17	telnets	Telnet protocol over TLS/SSL @consensus.com
40169	993	6	imaps	Imap4 protocol over TLS/SSL @consensus.com
40170	993	17	imaps	Imap4 protocol over TLS/SSL @consensus.com
40171	994	6	ircs	irc protocol over TLS/SSL @consensus.com
40172	994	17	ircs	irc protocol over TLS/SSL @consensus.com
40173	995	6	pop3s	pop3 protocol over TLS/SSL (was spop3) @microsoft.com
40174	995	17	pop3s	pop3 protocol over TLS/SSL (was spop3) @microsoft.com
40175	996	6	vsinet	vsinet
40176	996	17	vsinet	vsinet
40177	996	6	xtreelic	XTREE License Server
40178	996	17	xtreelic	XTREE License Server
40179	997	6	maitrd	
40180	997	17	maitrd	
40181	998	6	busboy	
40182	998	17	puparp	
40183	999	6	garcon	
40184	999	17	applix ac	Applix ac
40185	999	6	puprouter	
40186	999	17	puprouter	
40187	1000	6	cadlock	
40188	1000	17	ock	
40189	1001	6	silenser	Silencer Trojan
40190	1001	17	silenser	Silencer Trojan
40191	1001	6	WebEx	WebEx Trojan
40192	1001	17	WebEx	WebEx Trojan
40193	1008	6	ufsd	UFS-aware server
40194	1008	17	ufsd	UFS-aware server
40195	1010	6	surf	surf
40196	1010	17	surf	surf
40197	1011	6	doly	Doly Trojan
40198	1011	17	doly	Doly Trojan
40199	1012	17	sometimes-rpcl	This is rstatd on a openBSD box
40200	1025	6	listen	listener RFS remote_file_sharing
40201	1025	17	blackjack	Network blackjack
40202	1026	6	nterm	remote_login network_terminal
40203	1030	6	iad1	BBN IAD @timeplex.com
40204	1030	17	iad1	BBN IAD @timeplex.com
40205	1031	6	iad2	BBN IAD @timeplex.com
40206	1031	17	iad2	BBN IAD @timeplex.com
40207	1032	6	iad3	BBN IAD @timeplex.com
40208	1032	17	iad3	BBN IAD @timeplex.com
40209	1033	6	Netspy	Netspy Trojan
40210	1033	17	Netspy	Netspy Trojan
40211	1047	6	neod1	Suns NEO Object Request Broker
40212	1047	17	neod1	Suns NEO Object Request Broker
40213	1048	6	neod2	Suns NEO Object Request Broker
40214	1048	17	neod2	Suns NEO Object Request Broker
40215	1049	6	td-postman	Tobit David Management Agent
40216	1049	17	td-postman	Tobit David Management Agent
40217	1050	6	cma	COBRA management Agent
40218	1050	17	cma	COBRA management Agent
40219	1051	6	optima-vnet	Opima VNET
40220	1052	6	ddt	Dynamic DNS Tools
40221	1052	17	ddt	Dynamic DNS Tools
40222	1053	6	remote-as	Remote Assistant (RA)
40223	1053	17	remote-as	Remote Assistant (RA)
40224	1054	6	brvread	BRVREAD
40225	1054	17	brvread	BRVREAD
40226	1055	6	ansyslmd	ANSYS - License Manager
40227	1055	17	ansyslmd	ANSYS - License Manager
40228	1056	6	vfo	VFO
40229	1056	17	vfo	VFO
40230	1057	6	startron	STARTRON
40231	1057	17	startron	STARTRON
40232	1058	6	nim	nim @austin.ibm.com
40233	1058	17	nim	nim @austin.ibm.com
40234	1059	6	nimreg	nimreg @austin.ibm.com
40235	1059	17	nimreg	nimreg @austin.ibm.com
40236	1060	6	polestar	POLESTAR
40237	1060	17	polestar	POLESTAR
40238	1061	6	kiosk	KIOSK
40239	1061	17	kiosk	KIOSK
40240	1062	6	veracity	VERACITY freeveracity.org
40241	1062	17	veracity	VERACITY freeveracity.org
40242	1063	6	kyocerantdev	KyoceraNetDev
40243	1063	17	kyocerantdev	KyoceraNetDev
40244	1064	6	jstel	JSTEL
40245	1064	17	jstel	JSTEL
40246	1065	6	syscomlan	SYSCOMLAN
40247	1065	17	syscomlan	SYSCOMLAN
40248	1067	6	instl_boots	Installation Bootstrap Proto. Serv. @hpfcrn.fc.hp.com
40249	1067	17	instl_boots	Installation Bootstrap Proto. Serv. @hpfcrn.fc.hp.com
40250	1068	6	instl_bootc	Installation Bootstrap Proto. Cli. @hpfcrn.fc.hp.com
40251	1068	17	instl_bootc	Installation Bootstrap Proto. Cli. @hpfcrn.fc.hp.com
40252	1069	6	cognex-insight	COGNEX-INSIGHT
40253	1069	17	cognex-insight	COGNEX-INSIGHT
40254	1080	6	socks	Socks @syl.dl.nec.com
40255	1080	17	socks	Socks @syl.dl.nec.com
40256	1083	6	ansoft-lm-1	Anasoft License Manager
40257	1083	17	ansoft-lm-1	Anasoft License Manager
40258	1084	6	ansoft-lm-2	Anasoft License Manager
40259	1084	17	ansoft-lm-2	Anasoft License Manager
40260	1085	6	webobjects	WEBObjects apple.com
40261	1085	17	webobjects	WEBObjects apple.com
40262	1097	6	sunclustermgr	Sun Cluster Manager
40263	1097	17	sunclustermgr	Sun Cluster Manager
40264	1098	6	rmiactivation	RMI Activation
40265	1098	17	rmiactivation	RMI Activation
40266	1099	6	rmiregistry	RMI Registry
40267	1099	17	rmiregistry	RMI Registry
40268	1103	6	xaudio	Xaserver # X Audio Server
40269	1109	6	kpop	Pop with Kerberos
40270	1110	6	nfsd-status	Cluster status info @hpfclj.fc.hp.com
40271	1110	17	nfsd-keepalive	Client status info @hpfclj.fc.hp.com
40272	1111	6	lmsocialserver	LM Social Server @likeminds.com
40273	1111	17	lmsocialserver	LM Social Server @likeminds.com
40274	1112	6	msql	mini-sql server
40275	1114	17	mini-sql	Mini SQL
40276	1123	6	murray	Murray @j51.com
40277	1123	17	murray	Murray @j51.com
40278	1127	6	supfiledbg	SUP debugging
40279	1155	6	nfa	Network File Access @mailhost.unidata.com
40280	1155	17	nfa	Network File Access @mailhost.unidata.com
40281	1161	6	health-polling	Health Polling
40282	1161	17	health-polling	Health Polling
40283	1162	6	health-trap	Health Trap
40284	1162	17	health-trap	Health Trap
40285	1167	17	phone	conference calling
40286	1169	6	tripwire	TRIPWARE
40287	1169	17	tripwire	TRIPWARE
40288	1170	6	audiotrojan	Streaming Audio Trojan
40289	1170	17	audiotrojan	Streaming Audio Trojan
40290	1170	6	psyber	Psyber Stream Server Trojan
40291	1170	17	psyber	Psyber Stream Server Trojan
40292	1178	6	skkserv	SKK (kanji input)
40293	1180	6	mc-client	Millicent Client Proxy @pa.dec.com
40294	1180	17	mc-client	Millicent Client Proxy @pa.dec.com
40295	1182	6	caauthd.exe	Computer Associates BrightStor Enterprise Backup
40296	1188	6	hp-webadmin	HP Web Admin
40297	1188	17	hp-webadmin	HP Web Admin
40298	1200	6	scol	SCOL
40299	1200	17	scol	SCOL
40300	1202	6	caiccipc	caiccipc
40301	1202	17	caiccipc	caiccipc
40302	1210	6	mediasvr.exe	Computer Associates BrightStor Enterprise Backup
40303	1210	0	mediasvr.exe	Computer Associates BrightStor Enterprise Backup
40304	1212	6	lupa	lupa @databus.com
40305	1212	17	lupa	lupa @databus.com
40306	1214	6	kazaa	Morpheus or KaZaA peer to peer music/file sharing
40307	1214	17	kazaa	Morpheus or KaZaA peer to peer music/file sharing
40308	1215	6	scanstat-1	scanSTAT 1.0
40309	1215	17	scanstat-1	scanSTAT 1.0
40310	1222	6	nerv	SNI R&D network @sni.de
40311	1222	17	nerv	SNI R&D network @sni.de
40312	1227	6	dns2go	DNS to Go
40313	1227	17	dns2go	DNS to Go
40314	1234	6	search-agent	Infoseek Search Agent @infoseek.com
40315	1234	17	search-agent	Infoseek Search Agent @infoseek.com
40316	1234	6	ultors	Ultors Trojan
40317	1234	17	ultors	Ultors Trojan
40318	1239	6	nmsd	NMSD @ptc.com
40319	1239	17	nmsd	NMSD @ptc.com
40320	1240	6	LQServer.exe	Computer Associates BrighStor Enterprise Backup
40321	1241	6	msg	remote message service
40322	1243	6	sub7	SubSeven trojan
40323	1243	17	sub7	SubSeven trojan
40324	1245	6	subseven	Subseven backdoor remote access tool
40325	1245	6	vodoo	Vodoo Trojan
40326	1245	6	netbus	NetBus Trojan
40327	1245	6	gabanbus	GabanBus Trojan
40328	1245	6	voodoodoll	VooDoo Doll Trojan
40329	1248	6	hermes	
40330	1248	17	hermes	
40331	1269	6	Cadiscovd.exe	Computer Associates BrighStor Enterprise Backup
40332	1269	0	Cadiscovd.exe	Computer Associates BrighStor Enterprise Backup
40333	1300	6	h323hostcallsc	H323 Host Call Secure @ideal.jf.intel.com
40334	1300	17	h323hostcallsc	H323 Host Call Secure @ideal.jf.intel.com
40335	1310	6	husky	Husky
40336	1310	17	husky	Husky
40337	1311	6	rxmon	RxMon
40338	1311	17	rxmon	RxMon
40339	1312	6	sti-envision	STI Envision
40340	1312	17	sti-envision	STI Envision
40341	1313	6	bmc_patroldb	BMC_PATROLDB @crow.bmc.com
40342	1313	17	bmc_patroldb	BMC_PATROLDB @crow.bmc.com
40343	1314	6	pdps	Photoscript Distributed Printing System @cix.compulink.co.uk
40344	1314	17	pdps	Photoscript Distributed Printing System @cix.compulink.co.uk
40345	1319	6	panja-icsp	Panja-ICSP
40346	1319	17	panja-icsp	Panja-ICSP
40347	1320	6	panja-axbnet	Panja-AXBNET
40348	1320	17	panja-axbnet	Panja-AXBNET
40349	1321	6	pip	PIP
40350	1321	17	pip	PIP
40351	1335	6	digital-notary	Digital Notary Protocol
40352	1335	17	digital-notary	Digital Notary Protocol
40353	1338	6	miworm	Millenium Worm
40354	1338	17	miworm	Millenium Worm
40355	1345	6	vpjp	VPJP @aol.com
40356	1345	17	vpjp	VPJP @aol.com
40357	1346	6	alta-ana-lm	Alta Analytics License Manager
40358	1346	17	alta-ana-lm	Alta Analytics License Manager
40359	1347	6	bbn-mmc	Multimedia conferencing
40360	1347	17	bbn-mmc	Multimedia conferencing
40361	1348	6	bbn-mmx	Multimedia conferencing
40362	1348	17	bbn-mmx	Multimedia conferencing
40363	1349	6	sbook	Registration Network Protocol
40364	1349	17	sbook	Registration Network Protocol
40365	1350	6	editbench	Registration Network Protocol
40366	1350	17	editbench	Registration Network Protocol
40367	1351	6	equationbuilder	Digital Tool Works (MIT)
40368	1351	17	equationbuilder	Digital Tool Works (MIT)
40369	1352	6	lotusnote	Lotus Note
40370	1352	17	lotusnote	Lotus Note
40371	1353	6	relief	Relief Consulting @uu2.psi.com
40372	1353	17	relief	Relief Consulting @uu2.psi.com
40373	1354	6	rightbrain	RightBrain Software @rightbrain.com
40374	1354	17	rightbrain	RightBrain Software @rightbrain.com
40375	1355	6	intuitive-edge	Intuitive Edge @nextnorth.acs.ohio-state.edu
40376	1355	17	intuitive-edge	Intuitive Edge @nextnorth.acs.ohio-state.edu
40377	1356	6	cuillamartin	CuillaMartin Company
40378	1356	17	cuillamartin	CuillaMartin Company
40379	1357	6	pegboard	Electronic PegBoard @clout.chi.il.us
40380	1357	17	pegboard	Electronic PegBoard @clout.chi.il.us
40381	1358	17	connlcli	CONNLCLI
40382	1359	6	ftsrv	FTSRV @brfapesp.bitnet
40383	1359	17	ftsrv	FTSRV @brfapesp.bitnet
40384	1360	6	mimer	MIMER @mimer.se
40385	1360	17	mimer	MIMER @mimer.se
40386	1361	6	linx	LinX
40387	1361	17	linx	LinX
40388	1362	6	timeflies	TimeFlies @nwnexus.wa.com
40389	1362	17	timeflies	TimeFlies @nwnexus.wa.com
40390	1363	6	ndm-requester	Network DataMover Requester
40391	1363	17	ndm-requester	Network DataMover Requester
40392	1364	6	ndm-server	Network DataMover Server @godzilla.rsc.spdd.ricoh.co.j
40393	1364	17	ndm-server	Network DataMover Server @godzilla.rsc.spdd.ricoh.co.j
40394	1365	6	adapt-sna	Network Software Associates
40395	1365	17	adapt-sna	Network Software Associates
40396	1366	6	netware-csp	Novell NetWare Comm Service Platform @novell.com
40397	1366	17	netware-csp	Novell NetWare Comm Service Platform @novell.com
40398	1367	6	dcs	DCS @dcs.de
40399	1367	17	dcs	DCS @dcs.de
40400	1368	6	screencast	ScreenCast @uunet.UU.NET
40401	1368	17	screencast	ScreenCast @uunet.UU.NET
40402	1369	6	gv-us	GlobalView to Unix Shell
40403	1369	17	gv-us	GlobalView to Unix Shell
40404	1370	6	us-gv	Unix Shell to GlobalView @ssdev.ksp.fujixerox.co.jp
40405	1370	17	us-gv	Unix Shell to GlobalView @ssdev.ksp.fujixerox.co.jp
40406	1371	6	fc-cli	Fujitsu Config Protocol
40407	1371	17	fc-cli	Fujitsu Config Protocol
40408	1372	6	fc-ser	Fujitsu Config Protocol @spad.sysrap.cs.fujitsu.co.jp
40409	1372	17	fc-ser	Fujitsu Config Protocol @spad.sysrap.cs.fujitsu.co.jp
40410	1373	6	chromagrafx	Chromagrafx @chromagrafx.com
40411	1373	17	chromagrafx	Chromagrafx @chromagrafx.com
40412	1374	6	molly	EPI Software Systems @epimbe.com
40413	1374	17	molly	EPI Software Systems @epimbe.com
40414	1375	6	bytex	Bytex @uunet.UU.NET
40415	1375	17	bytex	Bytex @uunet.UU.NET
40416	1376	6	ibm-pps	IBM Person to Person Software @vnet.ibm.com
40417	1376	17	ibm-pps	IBM Person to Person Software @vnet.ibm.com
40418	1377	6	cichlid	Cichlid License Manager @cichlid.com
40419	1377	17	cichlid	Cichlid License Manager @cichlid.com
40420	1378	6	elan	Elan License Manager @elan.com
40421	1378	17	elan	Elan License Manager @elan.com
40422	1379	6	dbreporter	Integrity Solutions @uunet.UU.NET
40423	1379	17	dbreporter	Integrity Solutions @uunet.UU.NET
40424	1380	6	telesis-licman	Telesis Network License Manager @telesis.com
40425	1380	17	telesis-licman	Telesis Network License Manager @telesis.com
40426	1381	6	apple-licman	Apple Network License Manager @apple.com
40427	1381	17	apple-licman	Apple Network License Manager @apple.com
40428	1382	6	udt_os	
40429	1382	17	udt_os	
40430	1383	6	gwha	GW Hannaway Network License Manager @gwha.com
40431	1383	17	gwha	GW Hannaway Network License Manager @gwha.com
40432	1384	6	os-licman	Objective Solutions License Manager @objective.com
40433	1384	17	os-licman	Objective Solutions License Manager @objective.com
40434	1385	6	atex_elmd	Atex Publishing License Manager @atex.com
40435	1385	17	atex_elmd	Atex Publishing License Manager @atex.com
40436	1386	6	checksum	CheckSum License Manager @sirius.com
40437	1386	17	checksum	CheckSum License Manager @sirius.com
40438	1387	6	cadsi-lm	Computer Aided Design Software Inc LM
40439	1387	17	cadsi-lm	Computer Aided Design Software Inc LM
40440	1388	6	objective-dbc	Objective Solutions DataBase Cache
40441	1388	17	objective-dbc	Objective Solutions DataBase Cache
40442	1389	6	iclpv-dm	Document Manager
40443	1389	17	iclpv-dm	Document Manager
40444	1390	6	iclpv-sc	Storage Controller
40445	1390	17	iclpv-sc	Storage Controller
40446	1391	6	iclpv-sas	Storage Access Server
40447	1391	17	iclpv-sas	Storage Access Server
40448	1392	6	iclpv-pm	Print Manager
40449	1392	17	iclpv-pm	Print Manager
40450	1393	6	iclpv-nls	Network Log Server
40451	1393	17	iclpv-nls	Network Log Server
40452	1394	6	iclpv-nlc	Network Log Client
40453	1394	17	iclpv-nlc	Network Log Client
40454	1395	6	iclpv-wsm	PC Workstation Manager software @bra0112.wins.icl.co.uk
40455	1395	17	iclpv-wsm	PC Workstation Manager software @bra0112.wins.icl.co.uk
40456	1396	6	dvl-activemail	DVL Active Mail
40457	1396	17	dvl-activemail	DVL Active Mail
40458	1397	6	audio-activmail	Audio Active Mail
40459	1397	17	audio-activmail	Audio Active Mail
40460	1398	6	video-activmail	Video Active Mail @wisdon.weizmann.ac.il
40461	1398	17	video-activmail	Video Active Mail @wisdon.weizmann.ac.il
40462	1399	6	cadkey-licman	Cadkey License Manager
40463	1399	17	cadkey-licman	Cadkey License Manager
40464	1400	6	cadkey-tablet	Cadkey Tablet Daemon @cadkey.com
40465	1400	17	cadkey-tablet	Cadkey Tablet Daemon @cadkey.com
40466	1401	6	goldleaf-licman	Goldleaf License Manager
40467	1401	17	goldleaf-licman	Goldleaf License Manager
40468	1402	6	prm-sm-np	Prospero Resource Manager
40469	1402	17	prm-sm-np	Prospero Resource Manager
40470	1403	6	prm-nm-np	Prospero Resource Manager @isi.edu
40471	1403	17	prm-nm-np	Prospero Resource Manager @isi.edu
40472	1404	6	igi-lm	Infinite Graphics License Manager
40473	1404	17	igi-lm	Infinite Graphics License Manager
40474	1405	6	ibm-res	IBM Remote Execution Starter
40475	1405	17	ibm-res	IBM Remote Execution Starter
40476	1406	6	netlabs-lm	NetLabs License Manager
40477	1406	17	netlabs-lm	NetLabs License Manager
40478	1407	6	dbsa-lm	DBSA License Manager @dbsa.com
40479	1407	17	dbsa-lm	DBSA License Manager @dbsa.com
40480	1408	6	sophia-lm	Sophia License Manager @uunet.UU.net
40481	1408	17	sophia-lm	Sophia License Manager @uunet.UU.net
40482	1409	6	here-lm	Here License Manager @dialup.oar.net
40483	1409	17	here-lm	Here License Manager @dialup.oar.net
40484	1410	6	hiq	HiQ License Manager @bilmillennium.com
40485	1410	17	hiq	HiQ License Manager @bilmillennium.com
40486	1411	6	af	AudioFile @crl.dec.com
40487	1411	17	af	AudioFile @crl.dec.com
40488	1412	6	innosys	InnoSys
40489	1412	17	innosys	InnoSys
40490	1413	6	innosys-acl	Innosys-ACL
40491	1413	17	innosys-acl	Innosys-ACL
40492	1414	6	ibm-mqseries	IBM MQSeries @vnet.ibm.com
40493	1414	17	ibm-mqseries	IBM MQSeries @vnet.ibm.com
40494	1415	6	dbstar	DBStar @dbstar.com
40495	1415	17	dbstar	DBStar @dbstar.com
40496	1416	6	novell-lu6.2	Novell LU6.2
40497	1416	17	novell-lu6.2	Novell LU6.2
40498	1417	6	timbuktu-srv1	Timbuktu Service 1 Port
40499	1417	17	timbuktu-srv1	Timbuktu Service 1 Port
40500	1418	6	timbuktu-srv2	Timbuktu Service 2 Port
40501	1418	17	timbuktu-srv2	Timbuktu Service 2 Port
40502	1419	6	timbuktu-srv3	Timbuktu Service 3 Port
40503	1419	17	timbuktu-srv3	Timbuktu Service 3 Port
40504	1420	6	timbuktu-srv4	Timbuktu Service 4 Port @waygate.farallon.com
40505	1420	17	timbuktu-srv4	Timbuktu Service 4 Port @waygate.farallon.com
40506	1421	6	gandalf-lm	Gandalf License Manager @gandalf.ca
40507	1421	17	gandalf-lm	Gandalf License Manager @gandalf.ca
40508	1422	6	autodesk-lm	Autodesk License Manager @autodesk.com
40509	1422	17	autodesk-lm	Autodesk License Manager @autodesk.com
40510	1423	6	essbase	Essbase Arbor Software
40511	1423	17	essbase	Essbase Arbor Software
40512	1424	6	hybrid	Hybrid Encryption Protocol @hybrid.com
40513	1424	17	hybrid	Hybrid Encryption Protocol @hybrid.com
40514	1425	6	zion-lm	Zion Software License Manager @zion.com
40515	1425	17	zion-lm	Zion Software License Manager @zion.com
40516	1426	6	sais-1	Satellite-data Acquisition System 1 @ssec.wisc.edu
40517	1426	17	sais-1	Satellite-data Acquisition System 1 @ssec.wisc.edu
40518	1427	6	mloadd	mloadd monitoring tool @isi.edu
40519	1427	17	mloadd	mloadd monitoring tool @isi.edu
40520	1428	6	informatik-lm	Informatik License Manager @informatik.uni-muenchen.de
40521	1428	17	informatik-lm	Informatik License Manager @informatik.uni-muenchen.de
40522	1429	6	nms	Hypercom NMS
40523	1429	17	nms	Hypercom NMS
40524	1430	6	tpdu	Hypercom TPDU @hypercom.com
40525	1430	17	tpdu	Hypercom TPDU @hypercom.com
40526	1431	6	rgtp	Reverse Gossip Transport @cam-orl.co.uk
40527	1431	17	rgtp	Reverse Gossip Transport @cam-orl.co.uk
40528	1432	6	blueberry-lm	Blueberry Software License Manager @uunet.uu.net
40529	1432	17	blueberry-lm	Blueberry Software License Manager @uunet.uu.net
40530	1433	6	ms-sql-s	Microsoft-SQL-Server
40531	1433	17	ms-sql-s	Microsoft-SQL-Server
40532	1434	6	ms-sql-m	Microsoft-SQL-Monitor @microsoft.com
40533	1434	17	ms-sql-m	Microsoft-SQL-Monitor @microsoft.com
40534	1435	6	ibm-cics	IBM CICS @ibmmail.COM
40535	1435	17	ibm-cics	IBM CICS @ibmmail.COM
40536	1436	6	saism	Satellite-data Acquisition System 2 @ssec.wisc.edu
40537	1436	17	saism	Satellite-data Acquisition System 2 @ssec.wisc.edu
40538	1437	6	tabula	Tabula @taunivm.tau.ac.il
40539	1437	17	tabula	Tabula @taunivm.tau.ac.il
40540	1438	6	eicon-server	Eicon Security Agent/Server
40541	1438	17	eicon-server	Eicon Security Agent/Server
40542	1439	6	eicon-x25	Eicon X25/SNA Gateway
40543	1439	17	eicon-x25	Eicon X25/SNA Gateway
40544	1440	6	eicon-slp	Eicon Service Location Protocol @admin.eicon.qc.ca
40545	1440	17	eicon-slp	Eicon Service Location Protocol @admin.eicon.qc.ca
40546	1441	6	cadis-1	Cadis License Management
40547	1441	17	cadis-1	Cadis License Management
40548	1442	6	cadis-2	Cadis License Management @csn.org
40549	1442	17	cadis-2	Cadis License Management @csn.org
40550	1443	6	ies-lm	Integrated Engineering Software @integrated.mb.ca
40551	1443	17	ies-lm	Integrated Engineering Software @integrated.mb.ca
40552	1444	6	marcam-lm	Marcam License Management @marcam.com
40553	1444	17	marcam-lm	Marcam License Management @marcam.com
40554	1445	6	proxima-lm	Proxima License Manager
40555	1445	17	proxima-lm	Proxima License Manager
40556	1446	6	ora-lm	Optical Research Associates License Manager
40557	1446	17	ora-lm	Optical Research Associates License Manager
40558	1447	6	apri-lm	Applied Parallel Research LM @apri.com
40559	1447	17	apri-lm	Applied Parallel Research LM @apri.com
40560	1448	6	oc-lm	OpenConnect License Manager @oc.com
40561	1448	17	oc-lm	OpenConnect License Manager @oc.com
40562	1449	6	peport	PEport @ColumbiaSC.NCR.COM
40563	1449	17	peport	PEport @ColumbiaSC.NCR.COM
40564	1450	6	dwf	Tandem Distributed Workbench Facility @tandem.com
40565	1450	17	dwf	Tandem Distributed Workbench Facility @tandem.com
40566	1451	6	infoman	IBM Information Management
40567	1451	17	infoman	IBM Information Management
40568	1452	6	gtegsc-lm	GTE Government Systems License Man @msmail.iipo.gtegsc.com
40569	1452	17	gtegsc-lm	GTE Government Systems License Man @msmail.iipo.gtegsc.com
40570	1453	6	genie-lm	Genie License Manager @genie.geis.com
40571	1453	17	genie-lm	Genie License Manager @genie.geis.com
40572	1454	6	interhdl_elmd	interHDL License Manager @interhdl.com
40573	1454	17	interhdl_elmd	interHDL License Manager @interhdl.com
40574	1455	6	esl-lm	ESL License Manager @willy.esl.com
40575	1455	17	esl-lm	ESL License Manager @willy.esl.com
40576	1456	6	dca	DCA @netcom.com
40577	1456	17	dca	DCA @netcom.com
40578	1457	6	valisys-lm	Valisys License Manager @valisys.com
40579	1457	17	valisys-lm	Valisys License Manager @valisys.com
40580	1458	6	nrcabq-lm	Nichols Research Corp. @tumbleweed.nrcabq.com
40581	1458	17	nrcabq-lm	Nichols Research Corp. @tumbleweed.nrcabq.com
40582	1459	6	proshare1	Proshare Notebook Application
40583	1459	17	proshare1	Proshare Notebook Application
40584	1460	6	proshare2	Proshare Notebook Application @ccm.hf.intel.com
40585	1460	17	proshare2	Proshare Notebook Application @ccm.hf.intel.com
40586	1461	6	ibm_wrless_lan	IBM Wireless LAN @vnet.IBM.COM
40587	1461	17	ibm_wrless_lan	IBM Wireless LAN @vnet.IBM.COM
40588	1462	6	world-lm	World License Manager @world.std.com
40589	1462	17	world-lm	World License Manager @world.std.com
40590	1463	6	nucleus	Nucleus @fafner.Stanford.EDU
40591	1463	17	nucleus	Nucleus @fafner.Stanford.EDU
40592	1464	6	msl_lmd	MSL License Manager
40593	1464	17	msl_lmd	MSL License Manager
40594	1465	6	pipes	Pipes Platform @peerlogic.com
40595	1465	17	pipes	Pipes Platform @peerlogic.com
40596	1466	6	oceansoft-lm	Ocean Software License Manager @oceansoft.com
40597	1466	17	oceansoft-lm	Ocean Software License Manager @oceansoft.com
40598	1467	6	csdmbase	CSDMBASE
40599	1467	17	csdmbase	CSDMBASE
40600	1468	6	csdm	CSDM @informatik.uni-muenchen.de
40601	1468	17	csdm	CSDM @informatik.uni-muenchen.de
40602	1469	6	aal-lm	Active Analysis Limited License Manager
40603	1469	17	aal-lm	Active Analysis Limited License Manager
40604	1470	6	uaiact	Universal Analytics @uai.com
40605	1470	17	uaiact	Universal Analytics @uai.com
40606	1471	6	csdmbase	csdmbase
40607	1471	17	csdmbase	csdmbase
40608	1472	6	csdm	csdm @informatik.uni-muenchen.de
40609	1472	17	csdm	csdm @informatik.uni-muenchen.de
40610	1473	6	openmath	OpenMath @maplesoft.on.ca
40611	1473	17	openmath	OpenMath @maplesoft.on.ca
40612	1474	6	telefinder	Telefinder @spiderisland.com
40613	1474	17	telefinder	Telefinder @spiderisland.com
40614	1475	6	taligent-lm	Taligent License Manager @taligent.com
40615	1475	17	taligent-lm	Taligent License Manager @taligent.com
40616	1476	6	clvm-cfg	clvm-cfg @cup.hp.com
40617	1476	17	clvm-cfg	clvm-cfg @cup.hp.com
40618	1477	6	ms-sna-server	ms-sna-server
40619	1477	17	ms-sna-server	ms-sna-server
40620	1478	6	ms-sna-base	ms-sna-base @microsoft.com
40621	1478	17	ms-sna-base	ms-sna-base @microsoft.com
40622	1479	6	dberegister	dberegister @dancingbear.com
40623	1479	17	dberegister	dberegister @dancingbear.com
40624	1480	6	pacerforum	PacerForum @pacvax.pacersoft.com
40625	1480	17	pacerforum	PacerForum @pacvax.pacersoft.com
40626	1481	6	airs	AIRS
40627	1481	17	airs	AIRS
40628	1482	6	miteksys-lm	Miteksys License Manager @miteksys.com
40629	1482	17	miteksys-lm	Miteksys License Manager @miteksys.com
40630	1483	6	afs	AFS License Manager @afs.com
40631	1483	17	afs	AFS License Manager @afs.com
40632	1484	6	confluent	Confluent License Manager @pa.confluent.com
40633	1484	17	confluent	Confluent License Manager @pa.confluent.com
40634	1485	6	lansource	LANSource @hookup.net
40635	1485	17	lansource	LANSource @hookup.net
40636	1486	6	nms_topo_serv	nms_topo_serv @Novell.CO
40637	1486	17	nms_topo_serv	nms_topo_serv @Novell.CO
40638	1487	6	localinfosrvr	LocalInfoSrvr @ibist.ibis.com
40639	1487	17	localinfosrvr	LocalInfoSrvr @ibist.ibis.com
40640	1488	6	docstor	DocStor @salix.com
40641	1488	17	docstor	DocStor @salix.com
40642	1489	6	dmdocbroker	dmdocbroker @documentum.com
40643	1489	17	dmdocbroker	dmdocbroker @documentum.com
40644	1490	6	insitu-conf	insitu-conf @insitu.com
40645	1490	17	insitu-conf	insitu-conf @insitu.com
40646	1491	6	anynetgateway	anynetgateway @VNET.IBM.COM
40647	1491	17	anynetgateway	anynetgateway @VNET.IBM.COM
40648	1492	6	ftp99cmp	FTP 99 CMP Trojan Horse
40649	1492	17	stone-design-1	stone-design-1 @stone.com
40650	1493	6	netmap_lm	netmap_lm @extro.ucc.su.OZ.AU
40651	1493	17	netmap_lm	netmap_lm @extro.ucc.su.OZ.AU
40652	1494	6	citrix-ica	citrix-ICA Protocol
40653	1494	17	citrix-ica	citrix-ICA Protocol
40654	1495	6	cvc	cvc @equalizer.cray.com
40655	1495	17	cvc	cvc @equalizer.cray.com
40656	1496	6	liberty-lm	liberty-lm @pacbell.com
40657	1496	17	liberty-lm	liberty-lm @pacbell.com
40658	1497	6	rfx-lm	rfx-lm @rfx.rfx.com
40659	1497	17	rfx-lm	rfx-lm @rfx.rfx.com
40660	1498	6	sysbase-sqlany	Sybase SQL Any @sybase.com
40661	1498	17	sysbase-sqlany	Sybase SQL Any @sybase.com
40662	1499	6	fhc	Federico Heinz Consultora @heinz.com
40663	1499	17	fhc	Federico Heinz Consultora @heinz.com
40664	1500	6	vlsi-lm	VLSI License Manager @mdk.sanjose.vlsi.com
40665	1500	17	vlsi-lm	VLSI License Manager @mdk.sanjose.vlsi.com
40666	1501	6	sas-3	Satellite-data Acquisition System 3 @ssec.wisc.edu
40667	1501	17	sas-3	Satellite-data Acquisition System 3 @ssec.wisc.edu
40668	1502	6	shivadiscovery	Shiva @Shiva.COM
40669	1502	17	shivadiscovery	Shiva @Shiva.COM
40670	1503	6	imtc-mcs	Databeam @databeam.com, T.120
40671	1503	17	imtc-mcs	Databeam @databeam.com, T.120
40672	1504	6	evb-elm	EVB Software Engineering License Manager @sett.com
40673	1504	17	evb-elm	EVB Software Engineering License Manager @sett.com
40674	1505	6	funkproxy	Funk Software, Inc @willowpond.com
40675	1505	17	funkproxy	Funk Software, Inc @willowpond.com
40676	1506	6	utcd	Universal Time daemon (utcd) @ironwood.cray.com
40677	1506	17	utcd	Universal Time daemon (utcd) @ironwood.cray.com
40678	1507	6	symplex	symplex @symplex.com
40679	1507	17	symplex	symplex @symplex.com
40680	1508	6	diagmond	diagmond @hprdstl0.rose.hp.com
40681	1508	17	diagmond	diagmond @hprdstl0.rose.hp.com
40682	1509	6	robcad-lm	Robcad, Ltd. License Manager @uunet.uu.net
40683	1509	17	robcad-lm	Robcad, Ltd. License Manager @uunet.uu.net
40684	1509	6	pysberstr	Psyber Streaming Server Trojan
40685	1509	17	pysberstr	Psyber Streaming Server Trojan
40686	1510	6	mvx-lm	Midland Valley Exploration Ltd. Lic. Man. @indigo2.mvel.demon.co.uk
40687	1510	17	mvx-lm	Midland Valley Exploration Ltd. Lic. Man. @indigo2.mvel.demon.co.uk
40688	1511	6	3l-l1	3l-l1 @threel.co.uk
40689	1511	17	3l-l1	3l-l1 @threel.co.uk
40690	1512	6	wins	Microsofts Windows Internet Name Service
40691	1512	17	wins	Microsofts Windows Internet Name Service
40692	1513	6	fujitsu-dtc	Fujitsu Systems Business of America Inc
40693	1513	17	fujitsu-dtc	Fujitsu Systems Business of America Inc
40694	1514	6	fujitsu-dtcns	Fujitsu Systems Business of America Inc
40695	1514	17	fujitsu-dtcns	Fujitsu Systems Business of America Inc
40696	1515	6	ifor-protocol	ifor-protocol
40697	1515	17	ifor-protocol	ifor-protocol
40698	1516	6	vpad	Virtual Places Audio Data
40699	1516	17	vpad	Virtual Places Audio Data
40700	1517	6	vpac	Virtual Places Audio Control
40701	1517	17	vpac	Virtual Places Audio Control
40702	1518	6	vpvd	Virtual Places Video data
40703	1518	17	vpvd	Virtual Places Video data
40704	1519	6	vpvc	Virtual Places Video Control
40705	1519	17	vpvc	Virtual Places Video Control
40706	1520	6	atm-zip-office	atm zip office
40707	1520	17	atm-zip-office	atm zip office
40708	1521	6	ncube-lm	nCube License Manager
40709	1521	17	ncube-lm	nCube License Manager
40710	1521	6	oraclesql	Oracle SQL
40711	1521	17	oraclesql	Oracle SQL
40712	1522	6	rna-lm	Ricardo North America License Manager
40713	1522	17	rna-lm	Ricardo North America License Manager
40714	1523	6	cichild-lm	cichild
40715	1523	17	cichild-lm	cichild
40716	1524	6	ingreslock	Ingres
40717	1524	17	ingreslock	Ingres
40718	1525	6	orasrv	Oracle or Propero Directory Service non-priv
40719	1525	17	orasrv	Oracle or Propero Directory Service non-priv
40720	1526	6	pdap-np	Prospero Data Access nonprivileged
40721	1526	17	pdap-np	Prospero Data Access nonprivileged
40722	1527	6	tlisrv	Oracle SqlNet 2
40723	1527	17	tlisrv	Oracle SqlNet 2
40724	1528	6	mciautoreg	
40725	1528	17	mciautoreg	
40726	1529	6	support	prmsd gnatsd #cygnus bug tracker
40727	1529	17	coauthor	Oracle
40728	1530	6	rap-service	rap-service
40729	1530	17	rap-service	rap-service
40730	1531	6	rap-listen	
40731	1531	17	rap-listen	
40732	1532	6	microconnect	
40733	1532	17	microconnect	
40734	1533	6	virtual-places	Virtual Places Software
40735	1533	17	virtual-places	Virtual Places Software
40736	1534	6	micromuse-lm	
40737	1534	17	micromuse-lm	
40738	1535	6	ampr-info	
40739	1535	17	ampr-info	
40740	1536	6	ampr-inter	
40741	1536	17	ampr-inter	
40742	1537	6	sdsc-lm	
40743	1537	17	sdsc-lm	
40744	1538	6	3ds-lm	
40745	1538	17	3ds-lm	
40746	1539	6	intellistor-lm	Intellistor License Manager
40747	1539	17	intellistor-lm	Intellistor License Manager
40748	1540	6	rds	
40749	1540	17	rds	
40750	1541	6	rds2	
40751	1541	17	rds2	
40752	1542	6	gridgen-elmd	
40753	1542	17	gridgen-elmd	
40754	1543	6	simba-cs	
40755	1543	17	simba-cs	
40756	1544	6	aspeclmd	
40757	1544	17	aspeclmd	
40758	1545	6	vistium-share	
40759	1545	17	vistium-share	
40760	1546	6	abbaccuray	
40761	1546	17	abbaccuray	
40762	1547	6	laplink	
40763	1547	17	laplink	
40764	1548	6	axon-lm	Axon License Manager
40765	1548	17	axon-lm	Axon License Manager
40766	1549	6	shivahose	Shiva Hose
40767	1549	17	Shivasound	Shiva Sound
40768	1550	6	3m-image-lm	Image Store License Manager 3M Company
40769	1550	17	3m-image-lm	Image Store License Manager 3M Company
40770	1551	6	hecmtl-db	
40771	1551	17	hecmtl-db	
40772	1552	6	pciarray	
40773	1552	17	pciarray	
40774	1553	6	sna-cs	
40775	1553	17	sna-cs	
40776	1554	6	caci-lm	
40777	1554	17	caci-lm	
40778	1555	6	livelan	
40779	1555	17	livelan	
40780	1556	6	ashwin	AshWin CI Technologies
40781	1556	17	ashwin	AshWin CI Technologies
40782	1557	6	arbortext-lm	ArborText License Manager
40783	1557	17	arbortext-lm	ArborText License Manager
40784	1558	6	xingmpeg	
40785	1558	17	xingmpeg	
40786	1559	6	web2host	
40787	1559	17	web2host	
40788	1560	6	asci-val	
40789	1560	17	asci-val	
40790	1561	6	facilityview	
40791	1561	17	facilityview	
40792	1562	6	pconnectmgr	
40793	1562	17	pconnectmgr	
40794	1563	6	cadabra-lm	Cadabra License Manager
40795	1563	17	cadabra-lm	Cadabra License Manager
40796	1564	6	pay-per-view	Pay-Per-View
40797	1564	17	pay-per-view	Pay-Per-View
40798	1565	6	winddlb	WinDD
40799	1565	17	winddlb	WinDD
40800	1566	6	corelvideo	Corel Video
40801	1566	17	corelvideo	Corel Video
40802	1567	6	jlicelmd	
40803	1567	17	jlicelmd	
40804	1568	6	tsspmap	
40805	1568	17	tsspmap	
40806	1569	6	ets	
40807	1569	17	ets	
40808	1570	6	orbixd	
40809	1570	17	orbixd	
40810	1571	6	rdb-dbs-disp	Oracle remote Data Base
40811	1571	17	rdb-dbs-disp	Oracle remote Data Base
40812	1572	6	chip-lm	Chipcom license Manager
40813	1572	17	chip-lm	Chipcom license Manager
40814	1573	6	itscomm-ns	
40815	1573	17	itscomm-ns	
40816	1574	6	mvel-lm	
40817	1574	17	mvel-lm	
40818	1575	6	oraclenames	
40819	1575	17	oraclenames	
40820	1576	6	moldflow-lm	
40821	1576	17	moldflow-lm	
40822	1577	6	hypercube-lm	
40823	1577	17	hypercube-lm	
40824	1578	6	jacobus-lm	
40825	1578	17	jacobus-lm	
40826	1579	6	ioc-sea-lm	
40827	1579	17	ioc-sea-lm	
40828	1580	6	tn-tl-r1	
40829	1580	17	tn-tl-r2	
40830	1581	6	mil-2045-47001	
40831	1581	17	mil-2045-47001	
40832	1582	6	msims	
40833	1582	17	msims	
40834	1583	6	simbaexpress	
40835	1583	17	simbaexpress	
40836	1584	6	tn-tl-fd2	
40837	1584	17	tn-tl-fd2	
40838	1585	6	intv	
40839	1585	17	intv	
40840	1586	6	ibm-abstract	
40841	1586	17	ibm-abstract	
40842	1587	6	pra_elmd	
40843	1587	17	pra_elmd	
40844	1588	6	triquest-lm	
40845	1588	17	triquest-lm	
40846	1589	6	vqp	
40847	1589	17	vqp	
40848	1590	6	gemini-lm	
40849	1590	17	gemini-lm	
40850	1591	6	ncpm-mp	
40851	1591	17	ncpm-mp	
40852	1592	6	commonspace	
40853	1592	17	commonspace	
40854	1593	6	mainsoft-lm	
40855	1593	17	mainsoft-lm	
40856	1594	6	sixtrak	
40857	1594	17	sixtrak	
40858	1595	6	radio	
40859	1595	17	radio	
40860	1596	6	radio-sm	
40861	1596	17	orbplus-iiop	
40862	1597	6	radio-sm	Robert A. Kukura kukura@apollo.hp.com
40863	1597	17	radio-sm	Robert A. Kukura kukura@apollo.hp.com
40864	1598	6	oicknfs	
40865	1598	17	oicknfs	
40866	1599	6	simbaservices	
40867	1599	17	simbaservices	
40868	1600	6	issd	
40869	1600	17	issd	
40870	1600	6	shivaburka	Shiva Burka Trojan Horse
40871	1600	17	shivaburka	Shiva Burka Trojan Horse
40872	1600	6	shivkaburka	Shivka-Burka Trojan Horse
40873	1600	17	shivkaburka	Shivka-Burka Trojan Horse
40874	1601	6	aas	
40875	1601	17	aas	
40876	1602	6	inspect	
40877	1602	17	inspect	
40878	1603	6	picodbc	
40879	1603	17	picodbc	
40880	1604	6	icabrowser	Citrix Metaframe - ICA Browser Connection
40881	1604	17	icabrowser	Citrix Metaframe - ICA Browser Connection
40882	1605	6	slp	Salutation Manager (Salutation protocol)
40883	1605	17	slp	Salutation Manager (Salutation protocol)
40884	1606	6	slm-api	Salutation Manager (SLM-API)
40885	1606	17	slm-api	Salutation Manager (SLM-API)
40886	1607	6	stt	
40887	1607	17	stt	
40888	1608	6	smart-lm	Smart Corp. License Manager
40889	1608	17	smart-lm	Smart Corp. License Manager
40890	1609	6	isysg-lm	
40891	1609	17	isysg-lm	
40892	1610	6	taurus-wh	
40893	1610	17	taurus-wh	
40894	1611	6	ill	Inter Library Loan
40895	1611	17	ill	Inter Library Loan
40896	1612	6	netbill-trans	NetBill Transaction Server
40897	1612	17	netbill-trans	NetBill Transaction Server
40898	1613	6	netbill-keyrep	NetBill key repoistory
40899	1613	17	netbill-keyrep	NetBill key repoistory
40900	1614	6	netbill-cred	NetBill Credential Server
40901	1614	17	netbill-cred	NetBill Credential Server
40902	1615	6	netbill-auth	NetBill Authorization Server
40903	1615	17	netbill-auth	NetBill Authorization Server
40904	1616	6	netbill-prod	NetBill Product Server
40905	1616	17	netbill-prod	NetBill Product Server
40906	1617	6	nimrod-agent	Nimrod Inter-Agent Communication
40907	1617	17	nimrod-agent	Nimrod Inter-Agent Communication
40908	1618	6	skytelnet	
40909	1618	17	skytelnet	
40910	1619	6	xs-openstorage	XuiS Software Ltd.
40911	1619	17	xs-openstorage	XuiS Software Ltd.
40912	1620	6	faxportwinport	chris_wells@lansource.com
40913	1620	17	faxportwinport	chris_wells@lansource.com
40914	1621	6	softdataphone	
40915	1621	17	softdataphone	
40916	1622	6	ontime	
40917	1622	17	ontime	
40918	1623	6	jalesond	
40919	1623	17	jalesond	
40920	1624	6	udp-sr-port	
40921	1624	17	udp-sr-port	
40922	1625	6	svs-omagent	
40923	1625	17	svs-omagent	
40924	1626	6	Shockwave	sallen@macromedia.com
40925	1626	17	Shockwave	sallen@macromedia.com
40926	1627	6	t128-gateway	T.128 Gateway datcon.co.uk
40927	1627	17	t128-gateway	T.128 Gateway datcon.co.uk
40928	1628	6	lontalk-norm	LonTalk normal
40929	1628	17	lontalk-norm	LonTalk normal
40930	1629	6	lontalk-urgnt	LonTalk urgent
40931	1629	17	lontalk-urgnt	LonTalk urgent
40932	1630	6	oraclenet8cman	Oracle Net8 Cman
40933	1630	17	oraclenet8cman	Oracle Net8 Cman
40934	1631	6	visitview	Visit View
40935	1631	17	visitview	Visit View
40936	1632	6	pammratc	
40937	1632	17	pammratc	
40938	1633	6	pammrpc	
40939	1633	17	pammrpc	
40940	1634	6	loaprobe	Log On America Probe
40941	1634	17	loaprobe	Log On America Probe
40942	1635	6	edb-server1	EDB Server 1
40943	1635	17	edb-server1	EDB Server 1
40944	1636	6	cncp	CableNet Control Protocol
40945	1636	17	cncp	CableNet Control Protocol
40946	1637	6	cnap	CableNet Admin Protocol
40947	1637	17	cnap	CableNet Admin Protocol
40948	1638	6	cnip	CableNet Info protocol
40949	1638	17	cnip	CableNet Info protocol
40950	1639	6	cert-initiator	markson@osmosys.incog.com
40951	1639	17	cert-initiator	markson@osmosys.incog.com
40952	1640	6	cert-responder	markson@osmosys.incog.com
40953	1640	17	cert-responder	markson@osmosys.incog.com
40954	1641	6	invision	InVision
40955	1641	17	invision	InVision
40956	1642	6	isis-am	kchapman@isis.com
40957	1642	17	isis-am	kchapman@isis.com
40958	1643	6	isis-ambc	kchapman@isis.com
40959	1643	17	isis-ambc	kchapman@isis.com
40960	1644	6	saiseh	Satellite-data Acquistion Systems 4
40961	1644	17	saiseh	Satellite-data Acquistion Systems 4
40962	1645	6	datametrics	jerryj@datametrics.com
40963	1645	17	datametrics	jerryj@datametrics.com
40964	1645	17	radius	radius authentication
40965	1646	17	sa-msg-port	eawhiteh@itt.com
40966	1646	17	radacct	radius accounting
40967	1647	6	rsap	Holger.Reif@prakinf.tu-ilmenau.de
40968	1647	17	rsap	Holger.Reif@prakinf.tu-ilmenau.de
40969	1648	6	concurrent-lm	mjb@concurrent.co.uk
40970	1648	17	concurrent-lm	mjb@concurrent.co.uk
40971	1649	6	kermit	fdc@watsun.cc.columbia.edu
40972	1649	17	kermit	fdc@watsun.cc.columbia.edu
40973	1650	6	nkd	
40974	1650	17	nkd	
40975	1651	6	shiva_confsrvr	
40976	1651	17	shiva_confsrvr	
40977	1652	6	xnmp	scomm@cerf.net
40978	1652	17	xnmp	scomm@cerf.net
40979	1653	6	alpatech-lm	joseph.hauk@alphatech.com
40980	1653	17	alpatech-lm	joseph.hauk@alphatech.com
40981	1654	6	stargatech-lm	ccm.jf.intel.com
40982	1654	17	stargatech-lm	ccm.jf.intel.com
40983	1655	6	dec-mbadmin	mrmog.reo.dec.com
40984	1655	17	dec-mbadmin	mrmog.reo.dec.com
40985	1656	6	dec-mbadmin-h	mrmog.reo.dec.com
40986	1656	17	dec-mbadmin-h	mrmog.reo.dec.com
40987	1657	6	fujitsu-mmpdc	NAE01421@niftyserve.or.jp
40988	1657	17	fujitsu-mmpdc	NAE01421@niftyserve.or.jp
40989	1658	6	sixnetudr	wizvax.net
40990	1658	17	sixnetudr	wizvax.net
40991	1659	6	sg-lm	Silicon grail License Manager
40992	1659	17	sg-lm	Silicon grail License Manager
40993	1660	6	skiup-mc-gikreq	osmoys.incog.com
40994	1660	17	skiup-mc-gikreq	osmoys.incog.com
40995	1661	6	netview-aix-1	
40996	1661	17	netview-aix-1	
40997	1662	6	netview-aix-2	
40998	1662	17	netview-aix-2	
40999	1663	6	netview-aix-3	
41000	1663	17	netview-aix-3	
41001	1664	6	netview-aix-4	
41002	1664	17	netview-aix-4	
41003	1665	6	netview-aix-5	
41004	1665	17	netview-aix-5	
41005	1666	6	netview-aix-6	
41006	1666	17	netview-aix-6	
41007	1666	17	maze	
41008	1667	6	netview-aix-7	
41009	1667	17	netview-aix-7	
41010	1668	6	netview-aix-8	
41011	1668	17	netview-aix-8	
41012	1669	6	netview-aix-9	
41013	1669	17	netview-aix-9	
41014	1670	6	netview-aix-10	
41015	1670	17	netview-aix-10	
41016	1671	6	netview-aix-11	
41017	1671	17	netview-aix-11	
41018	1672	6	netview-aix-12	
41019	1672	17	netview-aix-12	
41020	1673	6	proshare-mc-1	Intel ProShare Mulicast
41021	1673	17	proshare-mc-1	Intel ProShare Mulicast
41022	1674	6	proshare-mc2	Intel Proshare Multicast
41023	1674	17	proshare-mc2	Intel Proshare Multicast
41024	1675	6	pdp	Pacific Data Products
41025	1675	17	pdp	Pacific Data Products
41026	1676	6	netcomm1	BKasman@symantec.com
41027	1676	17	netcomm1	BKasman@symantec.com
41028	1676	17	netcomm2	BKasman@symantec.com
41029	1677	6	groupwise	novell.com
41030	1677	17	groupwise	novell.com
41031	1678	6	prolink	soul.tv.tek.com
41032	1678	17	prolink	soul.tv.tek.com
41033	1679	6	darcorp-lm	aol.com
41034	1679	17	darcorp-lm	aol.com
41035	1680	6	microcom-sbp	smtp.microcom.com
41036	1680	17	microcom-sbp	smtp.microcom.com
41037	1680	6	carcopy	Carbon Copy v5.0 remote control
41038	1680	17	carcopy	Carbon Copy v5.0 remote control
41039	1681	6	sd-elmd	softdesk.com
41040	1681	17	sd-elmd	softdesk.com
41041	1682	6	lanyon-lantern	lanyon.com
41042	1682	17	lanyon-lantern	lanyon.com
41043	1683	6	ncpm-hip	hpindacx.cup.hp.com
41044	1683	17	ncpm-hip	hpindacx.cup.hp.com
41045	1684	6	snaresecure	capres.com
41046	1684	17	snaresecure	capres.com
41047	1685	6	n2nremote	net2net.com
41048	1685	17	n2nremote	net2net.com
41049	1686	6	cvmon	hpmfas3.cup.hp.com
41050	1686	17	cvmon	hpmfas3.cup.hp.com
41051	1687	6	nsjtp-ctrl	wsbgrd01.italy.hp.com
41052	1687	17	nsjtp-ctrl	wsbgrd01.italy.hp.com
41053	1688	6	nsjtp-data	wsbgrd01.italy.hp.com
41054	1688	17	nsjtp-data	wsbgrd01.italy.hp.com
41055	1689	6	firefox	firefox.co.uk
41056	1689	17	firefox	firefox.co.uk
41057	1690	6	ng-umds	compuserve.com
41058	1690	17	ng-umds	compuserve.com
41059	1691	6	empire-empuma	empiretech.com
41060	1691	17	empire-empuma	empiretech.com
41061	1692	6	sstsys-lm	ix.netcom.com
41062	1692	17	sstsys-lm	ix.netcom.com
41063	1693	6	rrirtr	access.rrinc.com
41064	1693	17	rrirtr	access.rrinc.com
41065	1694	6	rrimwm	access.rrinc.com
41066	1694	17	rrimwm	access.rrinc.com
41067	1695	6	rrilwm	access.rrinc.com
41068	1695	17	rrilwm	access.rrinc.com
41069	1696	6	rrifwm	access.rrinc.com
41070	1696	17	rrifwm	access.rrinc.com
41071	1697	6	rrisat	access.rrinc.com
41072	1697	17	rrisat	access.rrinc.com
41073	1698	6	rsvp-encap1	RSVP-ENCAPSULATION-1
41074	1698	17	rsvp-encap1	RSVP-ENCAPSULATION-1
41075	1699	6	rsvp-encap2	RSVP-ENCAPSULATION-2
41076	1699	17	rsvp-encap2	RSVP-ENCAPSULATION-2
41077	1700	6	mps-raft	Jleupen@aol.com
41078	1700	17	mps-raft	Jleupen@aol.com
41079	1701	6	l2f	vandys-lap.cisco.com
41080	1701	17	l2f	vandys-lap.cisco.com
41081	1701	6	l2f	L2TPLSF cisco.com
41082	1701	17	l2f	L2TPLSF cisco.com
41083	1702	6	l2tp	vandys-lap.cisco.com
41084	1702	17	l2tp	vandys-lap.cisco.com
41085	1703	6	hb-engine	cchou@zoom.com
41086	1703	17	hb-engine	cchou@zoom.com
41087	1704	6	bcs-broker	andy@knoware.nl
41088	1704	17	bcs-broker	andy@knoware.nl
41089	1705	6	slingshot	paulg@jetform.com
41090	1705	17	slingshot	paulg@jetform.com
41091	1706	6	jetform	gdeinsta@jetform.com
41092	1706	17	jetform	gdeinsta@jetform.com
41093	1707	6	vdmplay	vadim@magic.fr
41094	1707	17	vdmplay	vadim@magic.fr
41095	1708	6	get-lmd	igor@global-tech.com
41096	1708	17	get-lmd	igor@global-tech.com
41097	1709	6	centra	dwolff@centra.net
41098	1709	17	centra	dwolff@centra.net
41099	1710	6	impera	cambell@uniprise.com
41100	1710	17	impera	cambell@uniprise.com
41101	1711	6	pptconference	microsoft.com
41102	1711	17	pptconference	microsoft.com
41103	1712	6	registrar	Resource Monitoring Service, hp.com
41104	1712	17	registrar	Resource Monitoring Service, hp.com
41105	1713	6	conferencetalk	videoserver.com
41106	1713	17	conferencetalk	videoserver.com
41107	1714	6	sesi-lm	sidefax.com
41108	1714	17	sesi-lm	sidefax.com
41109	1715	6	houdini-lm	sidefax.com
41110	1715	17	houdini-lm	sidefax.com
41111	1716	6	xmsg	xantel.com
41112	1716	17	xmsg	xantel.com
41113	1717	6	fj-hdnet	al.fijitsu.co.jp
41114	1717	17	fj-hdnet	al.fijitsu.co.jp
41115	1717	6	convoy	Link Layer Convoy protocol & MS clustering services
41116	1717	17	convoy	Link Layer Convoy protocol & MS clustering services
41117	1718	6	h323gatedisc	intel.com
41118	1718	17	h323gatedisc	intel.com
41119	1719	6	h323gatestat	intel.com
41120	1719	17	h323gatestat	intel.com
41121	1720	6	h323hostcall	H.323/Q.931 Microsoft Netmeeting intel.com
41122	1720	17	h323hostcall	H.323/Q.931 Microsoft Netmeeting intel.com
41123	1721	6	caicci	cai.com
41124	1721	17	caicci	cai.com
41125	1722	6	hks-lm	HKS License Manager althea.hks.com
41126	1722	17	hks-lm	HKS License Manager althea.hks.com
41127	1723	6	PPTP	also needs GRE protocol microsoft.com
41128	1724	6	csbphonemaster	Mark_Kellerhuis@msn.com
41129	1724	17	csbphonemaster	Mark_Kellerhuis@msn.com
41130	1725	6	iden-ralp	comm.mot.com
41131	1725	17	iden-ralp	comm.mot.com
41132	1726	6	iberiagames	73374.313@compuserver.com
41133	1726	17	iberiagames	73374.313@compuserver.com
41134	1727	6	winddx	vnd.tek.com
41135	1727	17	winddx	vnd.tek.com
41136	1728	6	telindus	telindus.be
41137	1728	17	telindus	telindus.be
41138	1729	6	citynl	CityNL License Manager citydisc@euronet.nl
41139	1729	17	citynl	CityNL License Manager citydisc@euronet.nl
41140	1730	6	roketz	ahti.bluemonn.ee
41141	1730	17	roketz	ahti.bluemonn.ee
41142	1731	6	msiccp	MS NetMeeting Audio Call Control
41143	1732	6	proxim	proxim.com
41144	1732	17	proxim	proxim.com
41145	1733	6	siipat	SIMS SLIPAT Protocol for Alarm Tranmission
41146	1733	17	siipat	SIMS SLIPAT Protocol for Alarm Tranmission
41147	1734	6	cambertx-lm	Camber Corporation License Manger cambertx.com
41148	1734	17	cambertx-lm	Camber Corporation License Manger cambertx.com
41149	1735	6	privatechat	76400.3371@compuserver.com
41150	1735	17	privatechat	76400.3371@compuserver.com
41151	1736	6	street-stream	ix.netcom.com
41152	1736	17	street-stream	ix.netcom.com
41153	1737	6	ultimad	ultimatech.com
41154	1737	17	ultimad	ultimatech.com
41155	1738	6	gamegen1	multigen.com
41156	1738	17	gamegen1	multigen.com
41157	1739	6	webaccess	asymetrix.com
41158	1739	17	webaccess	asymetrix.com
41159	1740	6	encore	promis.com
41160	1740	17	encore	promis.com
41161	1741	6	cisco-net-mgmt	cisco.com
41162	1741	17	cisco-net-mgmt	cisco.com
41163	1742	6	3Com-nsd	3com.com
41164	1742	17	3Com-nsd	3com.com
41165	1743	6	cinegrfx-lm	Cinema Graphics License Manager cyclone.rfx.com
41166	1743	17	cinegrfx-lm	Cinema Graphics License Manager cyclone.rfx.com
41167	1744	6	ncpm-ft	ix.netcom.com
41168	1744	17	ncpm-ft	ix.netcom.com
41169	1745	6	remote-winsock	micosoft.com
41170	1745	17	remote-winsock	micosoft.com
41171	1746	6	ftrapid-1	trpro4.tr.unisys.com
41172	1746	17	ftrapid-1	trpro4.tr.unisys.com
41173	1747	6	ftrapid-2	trpro4.tr.unisys.com
41174	1747	17	ftrapid-2	trpro4.tr.unisys.com
41175	1748	6	oracle-em1	us.oracle.com
41176	1748	17	oracle-em1	us.oracle.com
41177	1749	6	aspen-services	aspenres.com
41178	1749	17	aspen-services	aspenres.com
41179	1750	6	sslp	Simple Socket Librarys PortMaster gryphon.gsfc.nasa.gov/td>
41180	1750	17	sslp	Simple Socket Librarys PortMaster gryphon.gsfc.nasa.gov/td>
41181	1751	6	swiftnet	pentek.com
41182	1751	17	swiftnet	pentek.com
41183	1752	6	lofr-lm	Leap of Faith Research License Manager
41184	1752	17	lofr-lm	Leap of Faith Research License Manager
41185	1753	6	translogic-lm	Translogic License Manager translogic.com
41186	1753	17	translogic-lm	Translogic License Manager translogic.com
41187	1754	6	oracle-em2	oracle.com
41188	1754	17	oracle-em2	oracle.com
41189	1755	6	ms-streaming	Windows Media .asf
41190	1755	17	ms-streaming	Windows Media .asf
41191	1756	6	capfast-lmd	phase3.com
41192	1756	17	capfast-lmd	phase3.com
41193	1757	6	cnhrp	atml.co.uk
41194	1757	17	cnhrp	atml.co.uk
41195	1758	6	tftp-mcast	lanworks.com
41196	1758	17	tftp-mcast	lanworks.com
41197	1759	6	spss-lm	SPSS License Manager spss.com
41198	1759	17	spss-lm	SPSS License Manager spss.com
41199	1760	6	www-ldap-gw	altavista.digital.com
41200	1760	17	www-ldap-gw	altavista.digital.com
41201	1761	6	cft-0	Martine Marchard 16 1 46 59 24 84
41202	1761	17	cft-0	Martine Marchard 16 1 46 59 24 84
41203	1762	6	cft-1	Martine Marchard 16 1 46 59 24 84
41204	1762	17	cft-1	Martine Marchard 16 1 46 59 24 84
41205	1763	6	cft-2	Martine Marchard 16 1 46 59 24 84
41206	1763	17	cft-2	Martine Marchard 16 1 46 59 24 84
41207	1764	6	cft-3	Martine Marchard 16 1 46 59 24 84
41208	1764	17	cft-3	Martine Marchard 16 1 46 59 24 84
41209	1765	6	cft-4	Martine Marchard 16 1 46 59 24 84
41210	1765	17	cft-4	Martine Marchard 16 1 46 59 24 84
41211	1766	6	cft-5	Martine Marchard 16 1 46 59 24 84
41212	1766	17	cft-5	Martine Marchard 16 1 46 59 24 84
41213	1767	6	cft-6	Martine Marchard 16 1 46 59 24 84
41214	1767	17	cft-6	Martine Marchard 16 1 46 59 24 84
41215	1768	6	cft-7	Martine Marchard 16 1 46 59 24 84
41216	1768	17	cft-7	Martine Marchard 16 1 46 59 24 84
41217	1769	6	bmc-net-adm	bmc.com
41218	1769	17	bmc-net-adm	bmc.com
41219	1770	6	bmc-net-svc	bmc.com
41220	1770	17	bmc-net-svc	bmc.com
41221	1771	6	vaultbase	vaultbase.com
41222	1771	17	vaultbase	vaultbase.com
41223	1772	6	essweb-gw	EssWeb Gateway arborsoft.com
41224	1772	17	essweb-gw	EssWeb Gateway arborsoft.com
41225	1773	6	kmscontrol	kmsys.com
41226	1773	17	kmscontrol	kmsys.com
41227	1774	6	global-dtserv	globalcomm.co.uk
41228	1774	17	global-dtserv	globalcomm.co.uk
41229	1775	6		Unassigned
41230	1775	17		Unassigned
41231	1776	6	femis	Federal Emergency Management Information System pnl.com
41232	1776	17	femis	Federal Emergency Management Information System pnl.com
41233	1777	6	powerguardian	benatong.com
41234	1777	17	powerguardian	benatong.com
41235	1778	6	prodigy-intrnet	Prodigy-Internet staff.prodigy.com
41236	1778	17	prodigy-intrnet	Prodigy-Internet staff.prodigy.com
41237	1779	6	pharmasoft	pharmasoft.se
41238	1779	17	pharmasoft	pharmasoft.se
41239	1780	6	dpkeyserv	omronsoft.co.jp
41240	1780	17	dpkeyserv	omronsoft.co.jp
41241	1781	6	answersoft-lm	answersoft.com
41242	1781	17	answersoft-lm	answersoft.com
41243	1782	6	hp-hcip	boi.hp.com
41244	1782	17	hp-hcip	boi.hp.com
41245	1783	6		Decomissioned Port 04/14/00 fujitsu.co.jp
41246	1783	17		Decomissioned Port 04/14/00 fujitsu.co.jp
41247	1784	6	finle-lm	Finle License Manager finle.com
41248	1784	17	finle-lm	Finle License Manager finle.com
41249	1785	6	windlm	Wind River Systems License Manager wrs.com
41250	1785	17	windlm	Wind River Systems License Manager wrs.com
41251	1786	6	funk-logger	funk.com
41252	1786	17	funk-logger	funk.com
41253	1787	6	funk-license	funk.com
41254	1787	17	funk-license	funk.com
41255	1788	6	psmond	fc.hp.com
41256	1788	17	psmond	fc.hp.com
41257	1789	6	hello	koobera.math.uic.edu
41258	1789	17	hello	koobera.math.uic.edu
41259	1790	6	nmsp	Narrative media Streaming Protocol narrative.com
41260	1790	17	nmsp	Narrative media Streaming Protocol narrative.com
41261	1791	6	ea1	ea.com
41262	1791	17	ea1	ea.com
41263	1792	6	ibm-dt-2	uk.ibm.com
41264	1792	17	ibm-dt-2	uk.ibm.com
41265	1793	6	rsc-robot	relsoft.com
41266	1793	17	rsc-robot	relsoft.com
41267	1794	6	cera-bcm	dk.ibm.com
41268	1794	17	cera-bcm	dk.ibm.com
41269	1795	6	dpi-proxy	digprod.com
41270	1795	17	dpi-proxy	digprod.com
41271	1796	6	vocaltec-admin	Vocaltec Server Administration vocaltec.com
41272	1796	17	vocaltec-admin	Vocaltec Server Administration vocaltec.com
41273	1797	6	uma	opengroup.org
41274	1797	17	uma	opengroup.org
41275	1798	6	etp	Event Transfer Protocol plb.hpl.hp.com
41276	1798	17	etp	Event Transfer Protocol plb.hpl.hp.com
41277	1799	6	netrisk	tds.com
41278	1799	17	netrisk	tds.com
41279	1800	6	ansys-lm	ansyspo.ansys.com
41280	1800	17	ansys-lm	ansyspo.ansys.com
41281	1801	6	msmq	Microsoft Message Que
41282	1801	17	msmq	Microsoft Message Que
41283	1802	6	concomp1	concomp.com
41284	1802	17	concomp1	concomp.com
41285	1803	6	hp-hcip-gwy	boi.hp.com
41286	1803	17	hp-hcip-gwy	boi.hp.com
41287	1804	6	enl	veritas.com
41288	1804	17	enl	veritas.com
41289	1805	6	enl-name	veritas.com
41290	1805	17	enl-name	veritas.com
41291	1806	6	musiconline	syspace.co.uk
41292	1806	17	musiconline	syspace.co.uk
41293	1807	6	fhsp	Fujitsu Hot Standby Protocol
41294	1807	17	fhsp	Fujitsu Hot Standby Protocol
41295	1807	6	spysender	SpySender Trojan
41296	1807	17	spysender	SpySender Trojan
41297	1808	6	oracle-vp2	us.oracle.com
41298	1808	17	oracle-vp2	us.oracle.com
41299	1809	6	oracle-vp1	us.oracle.com
41300	1809	17	oracle-vp1	us.oracle.com
41301	1810	6	jerand-lm	jerand.com
41302	1810	17	jerand-lm	jerand.com
41303	1811	6	scientia-sdb	scientia.com
41304	1811	17	scientia-sdb	scientia.com
41305	1812	17	radius	Radius Authentication protocol (rfc 2138) livingston.com
41306	1813	6	radius-acct	RADIUS Accounting (rfc 2139) livingston.com
41307	1813	17	radius-acct	RADIUS Accounting (rfc 2139) livingston.com
41308	1814	6	tdp-suite	rob.lockhart@mot.com
41309	1814	17	tdp-suite	rob.lockhart@mot.com
41310	1815	6	mmpft	Ralf Muckenhirn
41311	1815	17	mmpft	Ralf Muckenhirn
41312	1816	6	harp	cs.pdx.edu
41313	1816	17	harp	cs.pdx.edu
41314	1817	6	rkb-oscs	bobbreton@hotmail.com
41315	1817	17	rkb-oscs	bobbreton@hotmail.com
41316	1818	6	etftp	Enhanced Trivial File Tranfer Protocol mitre.org
41317	1818	17	etftp	Enhanced Trivial File Tranfer Protocol mitre.org
41318	1819	6	plato-lm	ermuk.com
41319	1819	17	plato-lm	ermuk.com
41320	1820	6	mcagent	vnet.ibm.com
41321	1820	17	mcagent	vnet.ibm.com
41322	1821	6	donnyworld	donnyworld.com
41323	1821	17	donnyworld	donnyworld.com
41324	1822	6	es-elmd	es.com
41325	1822	17	es-elmd	es.com
41326	1823	6	unisys-lm	Unisys Natural Language License Manager
41327	1823	17	unisys-lm	Unisys Natural Language License Manager
41328	1824	6	metrics-pas	metrics.com
41329	1824	17	metrics-pas	metrics.com
41330	1825	6	direcpc-video	DirecPC Video hns.com
41331	1825	17	direcpc-video	DirecPC Video hns.com
41332	1826	6	ardt	ardent.com.au
41333	1826	17	ardt	ardent.com.au
41334	1827	6	asi	usiny.mail.abb.com
41335	1827	17	asi	usiny.mail.abb.com
41336	1828	6	itm-mcell-u	us.imasters.com
41337	1828	17	itm-mcell-u	us.imasters.com
41338	1829	6	optika-emedia	optika.com
41339	1829	17	optika-emedia	optika.com
41340	1830	6	net8-cman	Oracle Net8 CMan Admin
41341	1830	17	net8-cman	Oracle Net8 CMan Admin
41342	1831	6	myrtle	genscan.com
41343	1831	17	myrtle	genscan.com
41344	1832	6	tht-treasure	signiform.com
41345	1832	17	tht-treasure	signiform.com
41346	1833	6	udpradio	guus@warande3094.warande.uu.nl
41347	1833	17	udpradio	guus@warande3094.warande.uu.nl
41348	1834	6	ardusuni	ARDUS Unicast pfu.co.jp
41349	1834	17	ardusuni	ARDUS Unicast pfu.co.jp
41350	1835	6	ardusmul	ARDUS Multicast pfu.co.jp
41351	1835	17	ardusmul	ARDUS Multicast pfu.co.jp
41352	1836	6	ste-smsc	st-electronics.be
41353	1836	17	ste-smsc	st-electronics.be
41354	1837	6	csoft1	csoft.co.uk
41355	1837	17	csoft1	csoft.co.uk
41356	1838	6	talnet	taltrade.com
41357	1838	17	talnet	taltrade.com
41358	1839	6	netopia-vol1	netopia.com
41359	1839	17	netopia-vol1	netopia.com
41360	1840	6	netopia-vol2	netopia.com
41361	1840	17	netopia-vol2	netopia.com
41362	1841	6	netopia-vol3	netopia.com
41363	1841	17	netopia-vol3	netopia.com
41364	1842	6	netopia-vol4	netopia.com
41365	1842	17	netopia-vol4	netopia.com
41366	1843	6	netopia-vol5	netopia.com
41367	1843	17	netopia-vol5	netopia.com
41368	1844	6	direcpc-dll	DirecPC-DLL hns.com
41369	1844	17	direcpc-dll	DirecPC-DLL hns.com
41370	1850	6	gsi	usa.net
41371	1850	17	gsi	usa.net
41372	1851	6	ctcd	cybertrace.com
41373	1851	17	ctcd	cybertrace.com
41374	1860	6	sunscalar-svc	SunSCALAR Services
41375	1860	17	sunscalar-svc	SunSCALAR Services
41376	1861	6	lecroy-vicp	lecroy.com
41377	1861	17	lecroy-vicp	lecroy.com
41378	1862	6	techra-server	maxware.no
41379	1862	17	techra-server	maxware.no
41380	1863	6	msnp	micosoft.com
41381	1863	17	msnp	micosoft.com
41382	1864	6	paradym-31port	wizdom.com
41383	1864	17	paradym-31port	wizdom.com
41384	1865	6	entp	exc.epson.co.jp
41385	1865	17	entp	exc.epson.co.jp
41386	1870	6	sunscalar-dns	SunSCALAR DNS Service
41387	1870	17	sunscalar-dns	SunSCALAR DNS Service
41388	1871	6	canocentral0	Cano Central 0 research.canon.com
41389	1871	17	canocentral0	Cano Central 0 research.canon.com
41390	1872	6	canocentral1	Cano Central 1 research.canon.com
41391	1872	17	canocentral1	Cano Central 1 research.canon.com
41392	1873	6	fjmpjps	ael.fujitsu.co.jp
41393	1873	17	fjmpjps	ael.fujitsu.co.jp
41394	1874	6	fjswapsnp	ael.fujitsu.co.jp
41395	1874	17	fjswapsnp	ael.fujitsu.co.jp
41396	1881	6	ibm-mqseries2	IBM MQseries uk.ibm.com
41397	1881	17	ibm-mqseries2	IBM MQseries uk.ibm.com
41398	1895	6	vista-4gl	vistacomp.com
41399	1895	17	vista-4gl	vistacomp.com
41400	1899	6	mc2studios	thecube.com
41401	1899	17	mc2studios	thecube.com
41402	1900	6	ssdp	microsoft.com
41403	1900	17	ssdp	microsoft.com
41404	1900	6	UPnP	UPnP Universal Plug & Play microsoft.com
41405	1900	17	UPnP	UPnP Universal Plug & Play microsoft.com
41406	1901	6	fjicl-tep-a	Fujitsu ICL Terminal Emulator Program A oasis.icl.co.uk
41407	1901	17	fjicl-tep-a	Fujitsu ICL Terminal Emulator Program A oasis.icl.co.uk
41408	1902	6	fjicl-tep-b	Fujitsu ICL Terminal Emulator Program B oasis.icl.co.uk
41409	1902	17	fjicl-tep-b	Fujitsu ICL Terminal Emulator Program B oasis.icl.co.uk
41410	1903	6	linkname	Local Link Name Resolution lucent.com
41411	1903	17	linkname	Local Link Name Resolution lucent.com
41412	1904	6	fjicl-tep-c	Fujitsu ICL Terminal Emulator Program C oasis.icl.co.uk
41413	1904	17	fjicl-tep-c	Fujitsu ICL Terminal Emulator Program C oasis.icl.co.uk
41414	1905	6	sugp	Secure UP.Link Gateway protocol uplanet.com
41415	1905	17	sugp	Secure UP.Link Gateway protocol uplanet.com
41416	1906	6	tpmd	TPortMapperReq vnet.ibm.com
41417	1906	17	tpmd	TPortMapperReq vnet.ibm.com
41418	1907	6	intrastar	IntraSTAR teles.de
41419	1907	17	intrastar	IntraSTAR teles.de
41420	1908	6	dawn	travsoft.com
41421	1908	17	dawn	travsoft.com
41422	1909	6	global-wlink	Global World link globalcomm.co.uk
41423	1909	17	global-wlink	Global World link globalcomm.co.uk
41424	1910	6	ultrabac	cnw.com
41425	1910	17	ultrabac	cnw.com
41426	1911	6	mtp	Starlight Networks Multimedia Transport Protocl iserver.starlight.com
41427	1911	17	mtp	Starlight Networks Multimedia Transport Protocl iserver.starlight.com
41428	1912	6	rhp-iibp	m-ware.com
41429	1912	17	rhp-iibp	m-ware.com
41430	1913	6	armadp	armltd.co.uk
41431	1913	17	armadp	armltd.co.uk
41432	1914	6	elm-momentum	mds.com
41433	1914	17	elm-momentum	mds.com
41434	1915	6	facelink	hiscom.nl
41435	1915	17	facelink	hiscom.nl
41436	1916	6	persona	Persoft Persona persoft.com
41437	1916	17	persona	Persoft Persona persoft.com
41438	1917	6	noagent	nOAgent datawatch.com
41439	1917	17	noagent	nOAgent datawatch.com
41440	1918	6	can-nds	Candle Directory Service - NDS candle.com
41441	1918	17	can-nds	Candle Directory Service - NDS candle.com
41442	1919	6	can-dch	Candle Directory Service - DCH candle.com
41443	1919	17	can-dch	Candle Directory Service - DCH candle.com
41444	1920	6	can-ferret	Candle Directory Service - FERRET candle.com
41445	1920	17	can-ferret	Candle Directory Service - FERRET candle.com
41446	1921	6	noadmin	NoAdmin datawatch.com
41447	1921	17	noadmin	NoAdmin datawatch.com
41448	1922	6	tapestry	namg.us.anritsu.com
41449	1922	17	tapestry	namg.us.anritsu.com
41450	1923	6	spice	sendit.se
41451	1923	17	spice	sendit.se
41452	1924	6	xiip	HMRinc.com
41453	1924	17	xiip	HMRinc.com
41454	1930	6	driveappserver	Drive AppServer bliss-support
41455	1930	17	driveappserver	Drive AppServer bliss-support
41456	1931	6	amdsched	AMD SCHED warwick.net
41457	1931	17	amdsched	AMD SCHED warwick.net
41458	1944	6	close-combat	microsoft.com
41459	1944	17	close-combat	microsoft.com
41460	1945	6	dialogic-elmd	nz.dialogic.com
41461	1945	17	dialogic-elmd	nz.dialogic.com
41462	1946	6	tekpls	vnd.tek.com
41463	1946	17	tekpls	vnd.tek.com
41464	1947	6	hlserver	fast-ag.de
41465	1947	17	hlserver	fast-ag.de
41466	1948	6	eye2eye	iguana.iosoftware.com
41467	1948	17	eye2eye	iguana.iosoftware.com
41468	1949	6	ismaeasdaqlive	ISMA Easdaq Live isma.co.uk
41469	1949	17	ismaeasdaqlive	ISMA Easdaq Live isma.co.uk
45169	54320	6	bo2k	Back Orifice 2000 (TCP)
41470	1950	6	ismaeasdaqtest	ISMA Easdaq Test isma.co.uk
41471	1950	17	ismaeasdaqtest	ISMA Easdaq Test isma.co.uk
41472	1951	6	bca-lmserver	knoware.nl
41473	1951	17	bca-lmserver	knoware.nl
41474	1952	6	mpnjsc	pfu.co.jp
41475	1952	17	mpnjsc	pfu.co.jp
41476	1953	6	rapidbase	Rapid Base vtt.fi
41477	1953	17	rapidbase	Rapid Base vtt.fi
41478	1961	6	bts-appserver	sabre.com
41479	1961	17	bts-appserver	sabre.com
41480	1964	6	solid-e-engine	solidtech.com
41481	1964	17	solid-e-engine	solidtech.com
41482	1965	6	tivoli-npm	trivoli.com
41483	1965	17	tivoli-npm	trivoli.com
41484	1966	6	slush	ibs.com.au
41485	1966	17	slush	ibs.com.au
41486	1967	6	sns-quote	calicotech.com
41487	1967	17	sns-quote	calicotech.com
41488	1972	6	intersys-cache	intersys.com
41489	1972	17	intersys-cache	intersys.com
41490	1973	6	dlsrap	Data Link Switching Remote Access Protocol cisco.com
41491	1973	17	dlsrap	Data Link Switching Remote Access Protocol cisco.com
41492	1974	6	drp	cisco.com
41493	1974	17	drp	cisco.com
41494	1975	6	tcoflashagent	TCO Flash Agent tcosoft.com
41495	1975	17	tcoflashagent	TCO Flash Agent tcosoft.com
41496	1976	6	tcoregagent	TCO Reg Agent tcosoft.com
41497	1976	17	tcoregagent	TCO Reg Agent tcosoft.com
41498	1977	6	tcoaddressbook	TCO Address Book tcosoft.com
41499	1977	17	tcoaddressbook	TCO Address Book tcosoft.com
41500	1978	6	unisql	UniSQL windtraveller.com
41501	1978	17	unisql	UniSQL windtraveller.com
41502	1979	6	unisql-java	UniSQL Java windtraveller.com
41503	1979	17	unisql-java	UniSQL Java windtraveller.com
41504	1981	6	shockrave	ShockRave Trojan
41505	1981	17	shockrave	ShockRave Trojan
41506	1984	6	bb	maclawran.ca
41507	1984	17	bb	maclawran.ca
41508	1985	6	hsrp	Hot Standby Router Protocol cisco.com
41509	1985	17	hsrp	Hot Standby Router Protocol cisco.com
41510	1986	6	licensedaemon	Cisco license management
41511	1986	17	licensedaemon	Cisco license management
41512	1987	6	tr-rsrb-p1	Cisco RSRB Priority 1 port
41513	1987	17	tr-rsrb-p1	Cisco RSRB Priority 1 port
41514	1988	6	tr-rsrb-p2	Cisco RSRB Priority 2 port
41515	1988	17	tr-rsrb-p2	Cisco RSRB Priority 2 port
41516	1989	6	tr-rsrb-p3	Cisco RSRB Priority 3 port
41517	1989	17	tr-rsrb-p3	Cisco RSRB Priority 3 port
41518	1989	6	mshnet	MHSnet system Unassigned but widely used
41519	1989	17	mshnet	MHSnet system Unassigned but widely used
41520	1990	6	stun-p1	Cisco STUN Priority 1 port
41521	1990	17	stun-p1	Cisco STUN Priority 1 port
41522	1991	6	stun-p2	Cisco STUN Priority 2 port
41523	1991	17	stun-p2	Cisco STUN Priority 2 port
41524	1992	6	stun-p3	Cisco STUN Priority 3 port
41525	1992	17	stun-p3	Cisco STUN Priority 3 port
41526	1992	6	ipsendmsg	Unassigned but widely used
41527	1992	17	ipsendmsg	Unassigned but widely used
41528	1993	6	snmp-tcp-port	Cisco SNMP tcp port
41529	1993	17	snmp-tcp-port	Cisco SNMP tcp port
41530	1994	6	stun-port	Cisco Serial Tunnel Port
41531	1994	17	stun-port	Cisco Serial Tunnel Port
41532	1995	6	perf-port	Cisco Perf Port
41533	1995	17	perf-port	Cisco Perf Port
41534	1996	6	tr-rsrb-port	Cisco Remote SRB Port
41535	1996	17	tr-rsrb-port	Cisco Remote SRB Port
41536	1997	6	gdb-port	Cisco Gateway Discovery Protocol
41537	1997	17	gdb-port	Cisco Gateway Discovery Protocol
41538	1998	6	x25-svc-port	Cisco X.25 Service (XOT)
41539	1998	17	x25-svc-port	Cisco X.25 Service (XOT)
41540	1999	6	tcp-id-port	Cisco Identification Port
41541	1999	17	tcp-id-port	Cisco Identification Port
41542	1999	6	Backdoor	Backdoor Trojan Horse
41543	1999	17	Backdoor	Backdoor Trojan Horse
41544	2000	6	callbook	
41545	2000	17	callbook	
41546	2001	6	glimpse	popular glimpse search engine
41547	2001	6	panda	Panda Antivirus for Novell
41548	2001	17	wizard	Curry
41549	2001	6	trojancow	Trojan Cow Trojan Horse
41550	2001	17	trojancow	Trojan Cow Trojan Horse
41551	2002	6	globe	
41552	2002	17	globe	
41553	2003	6	cfingerd	GNU finger
41554	2004	6	mailbox	
41555	2004	17	emce	CCWS mm conf
41556	2005	6	berknet	
41557	2005	6	deslogin	encrypted symmetric telnet/login
41558	2005	17	oracle	
41559	2006	6	invokator	
41560	2006	17	raid-cc	RAID
41561	2007	6	dectalk	
41562	2007	17	raid-am	
41563	2008	6	conf	
41564	2008	17	terminaldb	
41565	2009	6	news	
41566	2009	17	whosockami	
41567	2010	6	search	
41568	2010	17	pipe-server	
41569	2011	6	raid-cc	RAID
41570	2011	17	servserv	
41571	2012	6	ttyinfo	
41572	2012	17	raid-ac	
41573	2013	6	raid-am	
41574	2013	17	raid-cd	
41575	2014	6	troff	
41576	2014	17	raid-sf	
41577	2015	6	cypress	
41578	2015	17	raid-cs	
41579	2016	6	bootserver	
41580	2016	17	bootserver	
41581	2017	6	cypress-stat	
41582	2017	17	bootclient	
41583	2018	6	terminaldb	
41584	2018	17	rellpack	
41585	2019	6	whosockami	
41586	2019	17	about	
41587	2020	6	xinupageserver	
41588	2020	17	xinupageserver	
41589	2021	6	servexec	
41590	2021	17	xinuexpansion1	
41591	2022	6	down	
41592	2022	17	xinuexpansion2	
41593	2023	6	xinuexpansion3	
41594	2023	17	xinuexpansion3	
41595	2023	6	ripper	Ripper Trojan Horse
41596	2023	17	ripper	Ripper Trojan Horse
41597	2024	6	xinuexpansion4	
41598	2024	17	xinuexpansion4	
41599	2025	6	ellpack	
41600	2025	17	xribs	
41601	2026	6	scrabble	
41602	2026	17	scrabble	
41603	2027	6	shadowserver	
41604	2027	17	shadowserver	
41605	2028	6	submitserver	
41606	2028	17	submitserver	
41607	2030	6	device2	
41608	2030	17	device2	
41609	2032	6	blackboard	
41610	2032	17	blackboard	
41611	2033	6	glogger	
41612	2033	17	glogger	
41613	2034	6	scoremgr	
41614	2034	17	scoremgr	
41615	2034	6	rconj	Novell remote administration Novell 5 and 6
41616	2034	17	rconj	Novell remote administration Novell 5 and 6
41617	2035	6	imsldoc	
41618	2035	17	imsldoc	
41619	2038	6	objectmanager	
41620	2038	17	objectmanager	
41621	2040	6	lam	
41622	2040	17	lam	
41623	2041	6	interbase	
41624	2041	17	interbase	
41625	2042	6	isis	
41626	2042	17	isis	
41627	2043	6	isis-bcast	
41628	2043	17	isis-bcast	
41629	2044	6	rimsl	
41630	2044	17	rimsl	
41631	2045	6	cdfunc	
41632	2045	17	cdfunc	
41633	2046	6	sdfunc	
41634	2046	17	sdfunc	
41635	2047	6	dls	
41636	2047	17	dls	
41637	2048	6	dls-monitor	
41638	2048	17	dls-monitor	
41639	2049	6	nfs	Sun NFS
41640	2049	17	nfs	Sun NFS
41641	2049	6	shilp	Conflict with Sun NFS
41642	2049	17	shilp	Conflict with Sun NFS
41643	2053	6	knetd	Kerberos de-multiplexer
41644	2064	6	distrib-net	http://www.distributed.net
41645	2065	6	dlsrpn	Data Link Switch Read Port Number
41646	2065	17	dlsrpn	Data Link Switch Read Port Number
41647	2067	6	dlswpn	Data Link Switch Write Port Number
41648	2067	17	dlswpn	Data Link Switch Write Port Number
41649	2090	6	lrp	Load Report Protocol radware.co.il
41650	2090	17	lrp	Load Report Protocol radware.co.il
41651	2091	6	prp	radware.co.il
41652	2091	17	prp	radware.co.il
41653	2092	6	descent3	outrage.com
41654	2092	17	descent3	outrage.com
41655	2093	6	nbx-cc	nbxcorp.com
41656	2093	17	nbx-cc	nbxcorp.com
41657	2094	6	nbx-au	nbxcorp.com
41658	2094	17	nbx-au	nbxcorp.com
41659	2095	6	nbx-ser	nbxcorp.com
41660	2095	17	nbx-ser	nbxcorp.com
41661	2096	6	nbx-dir	nbxcorp.com
41662	2096	17	nbx-dir	nbxcorp.com
41663	2097	6	jetformpreview	jetform.com
41664	2097	17	jetformpreview	jetform.com
41665	2098	6	dialog-port	cisco.com
41666	2098	17	dialog-port	cisco.com
41667	2099	6	h2250-annex-g	vocaltec.com
41668	2099	17	h2250-annex-g	vocaltec.com
41669	2100	6	amiganetfs	cli.di.unipi.it
41670	2100	17	amiganetfs	cli.di.unipi.it
41671	2101	6	rtcm-sc104	wsrcc.com
41672	2101	17	rtcm-sc104	wsrcc.com
41673	2102	6	zephyr-srv	Zephyr Server zephyr-bugs@mit.edu
41674	2102	17	zephyr-srv	Zephyr Server zephyr-bugs@mit.edu
41675	2103	17	zephyr-clt	Zephyr serv-hm connection zephyr-bugs@mit.edu
41676	2104	17	zephyr-hm	Zephyr hostmanager zephyr-bugs@mit.edu
41677	2105	6	minipay	vnet.ibm.com
41678	2105	17	minipay	vnet.ibm.com
41679	2105	6	eklogin	Kerberos (v4) encrypted rlogin
41680	2105	17	eklogin	Kerberos (v4) encrypted rlogin
41681	2106	17	mzap	Multicast-Scope Zone Announcement Protocol microsoft.com
41682	2106	6	ekshell	Kerberos (v4) encrypted rshell
41683	2106	17	ekshell	Kerberos (v4) encrypted rshell
41684	2107	6	bintec-admin	bintec.de
41685	2107	17	bintec-admin	bintec.de
41686	2108	6	comcam	comcam.net
41687	2108	17	comcam	comcam.net
41688	2108	6	rkinit	Kerberos (v4) remote initialization
41689	2108	17	rkinit	Kerberos (v4) remote initialization
41690	2109	6	egolight	ledalite.com
41691	2109	17	egolight	ledalite.com
41692	2110	6	umsp	softhome.net
41693	2110	17	umsp	softhome.net
41694	2111	6	dsatp	altaworks.com
41695	2111	17	dsatp	altaworks.com
41696	2112	6	idonix-metanet	idonix.co.uk
41697	2112	17	idonix-metanet	idonix.co.uk
41698	2113	6	hsl-storm	hermes.si
41699	2113	17	hsl-storm	hermes.si
41700	2114	6	newheights	nh.ca
41701	2114	17	newheights	nh.ca
41702	2115	6	kdm	gd-cs.com
41703	2115	17	kdm	gd-cs.com
41704	2115	6	bugs	Bugs Trojan
41705	2115	17	bugs	Bugs Trojan
41706	2116	6	ccowcmr	sentillion.com
41707	2116	17	ccowcmr	sentillion.com
41708	2117	6	mentaclient	mentasoftware.com
41709	2117	17	mentaclient	mentasoftware.com
41710	2118	6	mentaserver	mentasoftware.com
41711	2118	17	mentaserver	mentasoftware.com
41712	2119	6	gsigatekeeper	mcs.anl.gov
41713	2119	17	gsigatekeeper	mcs.anl.gov
41714	2120	6	qencp	Quick Eagle Networks quickeagle.com
41715	2120	17	qencp	Quick Eagle Networks quickeagle.com
41716	2120	6	kauth	remote Kauth
41717	2121	6	scientia-ssdb	scientia.com
41718	2121	17	scientia-ssdb	scientia.com
41719	2122	6	caupc-remote	CauPC Remote Control environics.fi
41720	2122	17	caupc-remote	CauPC Remote Control environics.fi
41721	2123	6	gtp-control	GPT-Control Plane (3GPP) computer.org
41722	2123	17	gtp-control	GPT-Control Plane (3GPP) computer.org
41723	2124	6	elatelink	tao-group.com
41724	2124	17	elatelink	tao-group.com
41725	2125	6	lockstep	lockstep.com
41726	2125	17	lockstep	lockstep.com
41727	2126	6	pktcable-cops	PktCable-COPS cablelabs.com
41728	2126	17	pktcable-cops	PktCable-COPS cablelabs.com
41729	2127	6	index-pc-wb	lucent.com
41730	2127	17	index-pc-wb	lucent.com
41731	2128	6	net-steward	Net Steward Control ndl.co.uk
41732	2128	17	net-steward	Net Steward Control ndl.co.uk
41733	2129	6	cs-live	cs-live.com
41734	2129	17	cs-live	cs-live.com
41735	2130	6	swc-xds	swc.com
41736	2130	17	swc-xds	swc.com
41737	2131	6	avantageb2b	Avi Software logava.com
41738	2131	17	avantageb2b	Avi Software logava.com
41739	2132	6	avail-epmap	pacbell.net
41740	2132	17	avail-epmap	pacbell.net
41741	2133	6	zymed-zpp	zmi.com
41742	2133	17	zymed-zpp	zmi.com
41743	2134	6	avenue	csmags.com
41744	2134	17	avenue	csmags.com
41745	2135	6	gris	Grad Resource information Server mcs.anl.gov
41746	2135	17	gris	Grad Resource information Server mcs.anl.gov
41747	2136	6	appworxsvr	appworx.com
41748	2136	17	appworxsvr	appworx.com
41749	2137	6	connect	connectrf.com
41750	2137	17	connect	connectrf.com
41751	2138	6	unbind-clister	pandore.qc.ca
41752	2138	17	unbind-clister	pandore.qc.ca
41753	2139	6	ias-auth	intel.com
41754	2139	17	ias-auth	intel.com
41755	2140	6	ias-reg	intel.com
41756	2140	17	ias-reg	intel.com
41757	2140	6	deepthroat	Deep Throat Trojan Backdoor (Windows 9x)
41758	2140	17	deepthroat	Deep Throat Trojan Backdoor (Windows 9x)
41759	2140	6	invasor	The Invasor Trojan
41760	2140	17	invasor	The Invasor Trojan
41761	2141	6	ias-admind	intel.com
41762	2141	17	ias-admind	intel.com
41763	2142	6	tdm-over-ip	rad.co.il
41764	2142	17	tdm-over-ip	rad.co.il
41765	2143	6	lv-jc	Live Vault Job Control livevault.com
41766	2143	17	lv-jc	Live Vault Job Control livevault.com
41767	2144	6	lv-ffx	Live Vault Fast object Transfer livevault.com
41768	2144	17	lv-ffx	Live Vault Fast object Transfer livevault.com
41769	2145	6	lv-pici	Live Vault Remote Diagnostic Console Support livevault.com
41770	2145	17	lv-pici	Live Vault Remote Diagnostic Console Support livevault.com
41771	2146	6	lv-not	Live Vault Admin Event Notifcation livevault.com
41772	2146	17	lv-not	Live Vault Admin Event Notifcation livevault.com
41773	2147	6	lv-auth	Live Vault Authenication livevault.com
41774	2147	17	lv-auth	Live Vault Authenication livevault.com
41775	2148	6	veritas-ucl	Veritas Universal Communication Layer
41776	2148	17	veritas-ucl	Veritas Universal Communication Layer
41777	2149	6	acptsys	psdesign.com.au
41778	2149	17	acptsys	psdesign.com.au
41779	2150	6	dynamic3d	novagate.de
41780	2150	17	dynamic3d	novagate.de
41781	2151	6	docent	docent.com
41782	2151	17	docent	docent.com
41783	2152	6	gtp-user	GTP-User Plane (3GPP) computer.org
41784	2152	17	gtp-user	GTP-User Plane (3GPP) computer.org
41785	2165	6	x-bone-api	isi.edu
41786	2165	17	x-bone-api	isi.edu
41787	2166	6	iwserver	oz.quest.com
41788	2166	17	iwserver	oz.quest.com
41789	2180	6	mc-gt-srv	Millicent Vendor Gateway Server pa.dec.com
41790	2180	17	mc-gt-srv	Millicent Vendor Gateway Server pa.dec.com
41791	2181	6	eforward	flagship.com
41792	2181	17	eforward	flagship.com
41793	2200	6	ici	unisys.com
41794	2200	17	ici	unisys.com
41795	2201	6	ats	Advanced Training System Program
41796	2201	17	ats	Advanced Training System Program
41797	2202	6	imtc-map	Int. Multimedia Teleconferencing Cosortium databeam.com
41798	2202	17	imtc-map	Int. Multimedia Teleconferencing Cosortium databeam.com
41799	2213	6	kali	clc.vet.uga.edu
41800	2213	17	kali	clc.vet.uga.edu
41801	2220	6	ganymede	anymedesoftware.com
41802	2220	17	ganymede	anymedesoftware.com
41803	2221	6	rockwell-csp1	ra.rockwell.com
41804	2221	17	rockwell-csp1	ra.rockwell.com
41805	2222	6	rockwell-csp2	ra.rockwell.com
41806	2222	17	rockwell-csp2	ra.rockwell.com
41807	2223	6	rockwell-csp1	ra.rockwell.com
41808	2223	17	rockwell-csp1	ra.rockwell.com
41809	2232	6	ivs-video	IVS Video default sophia.inria.fr
41810	2232	17	ivs-video	IVS Video default sophia.inria.fr
41811	2233	6	infocrypt	isolation.com
41812	2233	17	infocrypt	isolation.com
41813	2234	6	directplay	microsoft.com
41814	2234	17	directplay	microsoft.com
41815	2235	6	sercomm-wlink	tpel.sercomm.com.tw
41816	2235	17	sercomm-wlink	tpel.sercomm.com.tw
41817	2236	6	nani	eng.eds.com
41818	2236	17	nani	eng.eds.com
41819	2237	6	optech-port-lm	Optech Port1 license Manager opticaltech.com
41820	2237	17	optech-port-lm	Optech Port1 license Manager opticaltech.com
41821	2238	6	aviva-sna	vickenK@192.219.82.71
41822	2238	17	aviva-sna	vickenK@192.219.82.71
41823	2239	6	imagequery	numinous.com
41824	2239	17	imagequery	numinous.com
41825	2240	6	recipe	RECIPe gsc.gte.com
41826	2240	17	recipe	RECIPe gsc.gte.com
41827	2241	6	ivsd	IVS deamon sophia.inria.fr
41828	2241	17	ivsd	IVS deamon sophia.inria.fr
41829	2242	6	foliocorp	Folio Remote Control folio.com
41830	2242	17	foliocorp	Folio Remote Control folio.com
41831	2243	6	magicom	Magicom protocol magicom.co.il
41832	2243	17	magicom	Magicom protocol magicom.co.il
41833	2244	6	nmsserver	nmss.com
41834	2244	17	nmsserver	nmss.com
41835	2245	6	hao	HaO hao.org
41836	2245	17	hao	HaO hao.org
41837	2279	6	xmquery	austin.ibm.com
41838	2279	17	xmquery	austin.ibm.com
41839	2280	6	lnvpoller	crd.lotus.com
41840	2280	17	lnvpoller	crd.lotus.com
41841	2281	6	lnvconsole	crd.lotus.com
41842	2281	17	lnvconsole	crd.lotus.com
41843	2282	6	lnvalarm	crd.lotus.com
41844	2282	17	lnvalarm	crd.lotus.com
41845	2283	6	lnvstatus	crd.lotus.com
41846	2283	17	lnvstatus	crd.lotus.com
41847	2284	6	lnvmaps	crd.lotus.com
41848	2284	17	lnvmaps	crd.lotus.com
41849	2285	6	lnvmailmon	crd.lotus.com
41850	2285	17	lnvmailmon	crd.lotus.com
41851	2286	6	nas-metering	symantec.com
41852	2286	17	nas-metering	symantec.com
41853	2287	6	dna	ricochet.net
41854	2287	17	dna	ricochet.net
41855	2288	6	netml	krypton.de
41856	2288	17	netml	krypton.de
41857	2294	6	konshus-lm	Konshus license Manager (FLEX) konshus.com
41858	2294	17	konshus-lm	Konshus license Manager (FLEX) konshus.com
41859	2295	6	advant-lm	Advant License Manager seisy.mail.abb.com
41860	2295	17	advant-lm	Advant License Manager seisy.mail.abb.com
41861	2296	6	theta-lm	Theta License Manager (rainbow) theta-ent.com
41862	2296	17	theta-lm	Theta License Manager (rainbow) theta-ent.com
41863	2297	6	d2k-datamover1	d2k.com
41864	2297	17	d2k-datamover1	d2k.com
41865	2298	6	d2k-datamover2	d2k.com
41866	2298	17	d2k-datamover2	d2k.com
41867	2299	6	pc-telecommute	PC Telecommute sysmantec.com
41868	2299	17	pc-telecommute	PC Telecommute sysmantec.com
41869	2300	6	cvmmon	cup.hp.com
41870	2300	17	cvmmon	cup.hp.com
41871	2301	6	cpq-wbem	Compaq Insight Management Web Agent
41872	2301	17	cpq-wbem	Compaq Insight Management Web Agent
41873	2302	6	binderysupport	novell.com
41874	2302	17	binderysupport	novell.com
41875	2303	6	proxy-gateway	funk.com
41876	2303	17	proxy-gateway	funk.com
41877	2304	6	attachmate-uts	attachmate.com
41878	2304	17	attachmate-uts	attachmate.com
41879	2305	6	mt-scalesever	mt.com
41880	2305	17	mt-scalesever	mt.com
41881	2306	6	tappi-boxnet	allaincetechnical.com
41882	2306	17	tappi-boxnet	allaincetechnical.com
41883	2307	6	pehelp	bbn.hp.com
41884	2307	17	pehelp	bbn.hp.com
41885	2308	6	sdhelp	bbn.hp.com
41886	2308	17	sdhelp	bbn.hp.com
41887	2309	6	sdserver	bbn.hp.com
41888	2309	17	sdserver	bbn.hp.com
41889	2310	6	sdclient	bbn.hp.com
41890	2310	17	sdclient	bbn.hp.com
41891	2311	6	messageservice	
41892	2311	17	messageservice	
41893	2313	6	iapp	IAPP (Inter Access point Protocol)
41894	2313	17	iapp	IAPP (Inter Access point Protocol)
41895	2314	6	cr-websystems	peddie.org
41896	2314	17	cr-websystems	peddie.org
41897	2315	6	precise-sft	precisesoft.co.il
41898	2315	17	precise-sft	precisesoft.co.il
41899	2316	6	sent-lm	axis-inc.com
41900	2316	17	sent-lm	axis-inc.com
41901	2317	6	attachmate-g32	attachmate.com
41902	2317	17	attachmate-g32	attachmate.com
41903	2318	6	cadencecontrol	ploygon.com
41904	2318	17	cadencecontrol	ploygon.com
41905	2319	6	infolibria	infolibria.com
41906	2319	17	infolibria	infolibria.com
41907	2320	6	siebel-ns	siebel.com
41908	2320	17	siebel-ns	siebel.com
41909	2321	6	rdlap	crw010@email.mot.com
41910	2321	17	rdlap	crw010@email.mot.com
41911	2322	6	ofsd	commvault.com
41912	2322	17	ofsd	commvault.com
41913	2323	6	3d-nfsd	commvault.com
41914	2323	17	3d-nfsd	commvault.com
41915	2327	6	Netconf	Netscape Conference
41916	2327	17	Netconf	Netscape Conference
41917	2336	6	augcont	Apple UG Control
41918	2336	17	augcont	Apple UG Control
41919	2401	6	cvspserver	CVS network Server
41920	2401	17	cvspserver	CVS network Server
41921	2402	6	taskmaster2000	TaskMaster 2000 Server datacap.com
41922	2402	17	taskmaster2000	TaskMaster 2000 Server datacap.com
41923	2403	6	taskmaster2000	TaskMaster 2000 Web datacap.com
41924	2403	17	taskmaster2000	TaskMaster 2000 Web datacap.com
41925	2404	6	iec870-5-104	sat-automation.com
41926	2404	17	iec870-5-104	sat-automation.com
41927	2405	6	trc-netpoll	telcores.com
41928	2405	17	trc-netpoll	telcores.com
41929	2406	6	jediserver	columbiasc.ncr.com
41930	2406	17	jediserver	columbiasc.ncr.com
41931	2407	6	orion	pcug.org.au
41932	2407	17	orion	pcug.org.au
41933	2408	6	optimanet	opimal.com
41934	2408	17	optimanet	opimal.com
41935	2409	6	sns-protocol	netmanage.co.il
41936	2409	17	sns-protocol	netmanage.co.il
41937	2410	6	vrts-registry	veritas.com
41938	2410	17	vrts-registry	veritas.com
41939	2411	6	netware-ap-mgmt	netwave-wireless.com
41940	2411	17	netware-ap-mgmt	netwave-wireless.com
41941	2412	6	cdn	netmind.com
41942	2412	17	cdn	netmind.com
41943	2413	6	orion-rmi-reg	us.ibm.com
41944	2413	17	orion-rmi-reg	us.ibm.com
41945	2414	6	interlingua	vitual-unlimited.com
41946	2414	17	interlingua	vitual-unlimited.com
41947	2415	6	comtest	comtest.co.uk
41948	2415	17	comtest	comtest.co.uk
41949	2416	6	rmtserver	simware.com
41950	2416	17	rmtserver	simware.com
41951	2417	6	composit-server	pfu.co.jp
41952	2417	17	composit-server	pfu.co.jp
41953	2418	6	cas	net.paso.fujitus.co.jp
41954	2418	17	cas	net.paso.fujitus.co.jp
41955	2419	6	attachmate-s2s	attachmate.com
41956	2419	17	attachmate-s2s	attachmate.com
41957	2420	6	dslremote-mgmt	DSL Remote Management westell.com
41958	2420	17	dslremote-mgmt	DSL Remote Management westell.com
41959	2421	6	g-talk	four-sight.co.uk
41960	2421	17	g-talk	four-sight.co.uk
41961	2422	6	crmsbits	vaccmell.telstra.co.au
41962	2422	17	crmsbits	vaccmell.telstra.co.au
41963	2423	6	rnrp	sw.seisy.abb.se
41964	2423	17	rnrp	sw.seisy.abb.se
41965	2424	6	kofax-svr	kofax.com
41966	2424	17	kofax-svr	kofax.com
41967	2425	6	fjitsuappmgr	Fujitsu App Manager
41968	2425	17	fjitsuappmgr	Fujitsu App Manager
41969	2426	6	applianttcp	Appliant TCP appliant.com
41970	2426	17	appliantudp	Appliant UDP appliant.com
41971	2427	6	mgcp-gateway	Media Gateway Control Protocol Gateway research.telcordia.com
41972	2427	17	mgcp-gateway	Media Gateway Control Protocol Gateway research.telcordia.com
41973	2428	6	ott	One Way Trip Time bbn.com
41974	2428	17	ott	One Way Trip Time bbn.com
41975	2429	6	ft-role	FT-ROLE atg.clr.com
41976	2429	17	ft-role	FT-ROLE atg.clr.com
41977	2430	6	venus	venue cyrus.watson.org
41978	2430	17	venus	venue cyrus.watson.org
41979	2431	6	venus-se	venue-se cyrus.watson.org
41980	2431	17	venus-se	venue-se cyrus.watson.org
41981	2432	6	codasrv	codasrv cyrus.watson.org
41982	2432	17	codasrv	codasrv cyrus.watson.org
41983	2433	6	codasrv-se	codasrv-se cyrus.watson.org
41984	2433	17	codasrv-se	codasrv-se cyrus.watson.org
41985	2434	6	pxc-epmap	pxc-epmap cp10.es.xerox.com
41986	2434	17	pxc-epmap	pxc-epmap cp10.es.xerox.com
41987	2435	6	optilogic	optilogic wirespeed.com
41988	2435	17	optilogic	optilogic wirespeed.com
41989	2436	6	topx	TOP/X cd.ubbcluj.ro
41990	2436	17	topx	TOP/X cd.ubbcluj.ro
41991	2437	6	unicontrol	UniControl hsd.at
41992	2437	17	unicontrol	UniControl hsd.at
41993	2438	6	msp	MSP acc.com
41994	2438	17	msp	MSP acc.com
41995	2439	6	sybasedbsynch	SybaseDBSynch sybase.com
41996	2439	17	sybasedbsynch	SybaseDBSynch sybase.com
41997	2440	6	spearway	Spearway Lockers spearway.com
41998	2440	17	spearway	Spearway Lockers spearway.com
41999	2441	6	pvsw-inet	pervasive.com
42000	2441	17	pvsw-inet	pervasive.com
42001	2442	6	netangel	Netangel identcode.sk
42002	2442	17	netangel	Netangel identcode.sk
42003	2443	6	powerclientcsf	PowerClinet Central Storage Facility Unisys.com
42004	2443	17	powerclientcsf	PowerClinet Central Storage Facility Unisys.com
42005	2444	6	btpp2sectrans	BT PP2 Sectrans bt-sys.bt.co.uk
42006	2444	17	btpp2sectrans	BT PP2 Sectrans bt-sys.bt.co.uk
42007	2445	6	dtn1	DTN1 dtn.com
42008	2445	17	dtn1	DTN1 dtn.com
42009	2446	6	bues_service	04.mstr02.telekom400.dbp.de
42010	2446	17	bues_service	04.mstr02.telekom400.dbp.de
42011	2447	6	ovwdb	OpenView NNM daemon fc.hp.com
42012	2447	17	ovwdb	OpenView NNM daemon fc.hp.com
42013	2448	6	hpppssvr	boi.hp.com
42014	2448	17	hpppssvr	boi.hp.com
42015	2449	6	ratl	RATL unisys.com
42016	2449	17	ratl	RATL unisys.com
42017	2450	6	netadmin	cu-muc.de
42018	2450	17	netadmin	cu-muc.de
42019	2451	6	netchat	cu-muc.de
42020	2451	17	netchat	cu-muc.de
42021	2452	6	snifferclient	SnifferClient nai.com
42022	2452	17	snifferclient	SnifferClient nai.com
42023	2453	6	madge-om	dev.madge.com
42024	2453	17	madge-om	dev.madge.com
42025	2454	6	indx-dds	IndX-DDS indx.net
42026	2454	17	indx-dds	IndX-DDS indx.net
42027	2455	6	wago-io-system	ieee.org
42028	2455	17	wago-io-system	ieee.org
42029	2456	6	altav-remmgt	digital.com
42030	2456	17	altav-remmgt	digital.com
42031	2457	6	rapido-ip	Rapido_IP wamnet.co.uk
42032	2457	17	rapido-ip	Rapido_IP wamnet.co.uk
42033	2458	6	griffin	unisys.com
42034	2458	17	griffin	unisys.com
42035	2459	6	community	webmaster.com
42036	2459	17	community	webmaster.com
42037	2460	6	ms-theater	microsoft.com
42038	2460	17	ms-theater	microsoft.com
42039	2461	6	qadmifoper	tellabs.fi
42040	2461	17	qadmifoper	tellabs.fi
42041	2462	6	qadmifevent	tellabs.fi
42042	2462	17	qadmifevent	tellabs.fi
42043	2463	6	symbios-raid	Symbios Raid symbios.com
42044	2463	17	symbios-raid	Symbios Raid symbios.com
42045	2464	6	direcpc-si	DirecPC SI hns.com
42046	2464	17	direcpc-si	DirecPC SI hns.com
42047	2465	6	lbm	Load Balance Management pfu.co.jp
42048	2465	17	lbm	Load Balance Management pfu.co.jp
42049	2466	6	lbf	Load Balance Forwarding pfu.co.jp
42050	2466	17	lbf	Load Balance Forwarding pfu.co.jp
42051	2467	6	high-criteria	High Criteria highcriteria.com
42052	2467	17	high-criteria	High Criteria highcriteria.com
42053	2468	6	qip-msgd	lucent.com
42054	2468	17	qip-msgd	lucent.com
42055	2469	6	mti-tcs-comm	microtempus.com
42056	2469	17	mti-tcs-comm	microtempus.com
42057	2470	6	taskman-port	Taskman Port himel.com
42058	2470	17	taskman-port	Taskman Port himel.com
42059	2471	6	seaodbc	SeaODBC aran.co.uk
42060	2471	17	seaodbc	SeaODBC aran.co.uk
42061	2472	6	c3	com-on.de
42062	2472	17	c3	com-on.de
42063	2473	6	aker-cdp	aker.com.br
42064	2473	17	aker-cdp	aker.com.br
42065	2474	6	vitalanalysis	Vital Analysis vitalsigns.com
42066	2474	17	vitalanalysis	Vital Analysis vitalsigns.com
42067	2475	6	ace-server	ACE Server securitydynamics.com
42068	2475	17	ace-server	ACE Server securitydynamics.com
42069	2476	6	ace-svr-prop	ACE Server Propogation securitydynamics.com
42070	2476	17	ace-svr-prop	ACE Server Propogation securitydynamics.com
42071	2477	6	ssm-cvs	SecurSight Certification Valifation Service securitydynamics.com
42072	2477	17	ssm-cvs	SecurSight Certification Valifation Service securitydynamics.com
42073	2478	6	ssm-cssps	SecurSight Authenication Server (SSL) securitydynamics.com
42074	2478	17	ssm-cssps	SecurSight Authenication Server (SSL) securitydynamics.com
42075	2479	6	ssm-els	SecurSight Event Logging Server (SSL) securitydynamics.com
42076	2479	17	ssm-els	SecurSight Event Logging Server (SSL) securitydynamics.com
42077	2480	6	lingwood	Lingwoods Detial btinternet.com
42078	2480	17	lingwood	Lingwoods Detial btinternet.com
42079	2481	6	giop	Oracle GIOP us.oracle.com
42080	2481	17	giop	Oracle GIOP us.oracle.com
42081	2482	6	giop-ssl	Oracle GIOP SSL us.oracle.com
42082	2482	17	giop-ssl	Oracle GIOP SSL us.oracle.com
42083	2483	6	ttc	Oracle TTC us.oracle.com
42084	2483	17	ttc	Oracle TTC us.oracle.com
42085	2484	6	ttc-ssl	Oracle TTC SSL us.oracle.com
42086	2484	17	ttc-ssl	Oracle TTC SSL us.oracle.com
42087	2485	6	netobjects1	netobjects.com
42088	2485	17	netobjects1	netobjects.com
42089	2486	6	netobjects2	netobjects.com
42090	2486	17	netobjects2	netobjects.com
42091	2487	6	pns	Policy Notice Service net.paso.fijitsu.co.jp
42092	2487	17	pns	Policy Notice Service net.paso.fijitsu.co.jp
42093	2488	6	moy-corp	Moy Corporation
42094	2488	17	moy-corp	Moy Corporation
42095	2489	6	tsilb	TSILB travsoft.com
42096	2489	17	tsilb	TSILB travsoft.com
42097	2490	6	qip-qdhcp	lucent.com
42098	2490	17	qip-qdhcp	lucent.com
42099	2491	6	conclave-cpp	Conclave CPP interdyn.com
42100	2491	17	conclave-cpp	Conclave CPP interdyn.com
42101	2492	6	groove	rocks.com
42102	2492	17	groove	rocks.com
42103	2493	6	talarian-mqs	Talarian MQS talarian.com
42104	2493	17	talarian-mqs	Talarian MQS talarian.com
42105	2494	6	bmc-ar	BMC AR bmc.com
42106	2494	17	bmc-ar	BMC AR bmc.com
42107	2495	6	fast-rem-serv	Fast Remote Services ntc.adaptec.com
42108	2495	17	fast-rem-serv	Fast Remote Services ntc.adaptec.com
42109	2496	6	dirgis	DIRGRIS dirg.de
42110	2496	17	dirgis	DIRGRIS dirg.de
42111	2497	6	quaddb	Quad DB quad-sys.com
42112	2497	17	quaddb	Quad DB quad-sys.com
42113	2498	6	odn-castraq	ODN-CasTraq source.net
42114	2498	17	odn-castraq	ODN-CasTraq source.net
42115	2499	6	unicontrol	UniControl
42116	2499	17	unicontrol	UniControl
42117	2500	6	rtsserv	Resource Tracking System Server etsuadmn.etsu.edu
42118	2500	17	rtsserv	Resource Tracking System Server etsuadmn.etsu.edu
42119	2501	6	rtsclient	Resource Tracking System Client etsuadmn.etsu.edu
42120	2501	17	rtsclient	Resource Tracking System Client etsuadmn.etsu.edu
42121	2502	6	kentrox-prot	Kentox Protocol kentrox.com
42122	2502	17	kentrox-prot	Kentox Protocol kentrox.com
42123	2503	6	nms-dpnss	NMS-DPNSS NMS-Europe.com
42124	2503	17	nms-dpnss	NMS-DPNSS NMS-Europe.com
42125	2504	6	wlbs	WLBS microsoft.com
42126	2504	17	wlbs	WLBS microsoft.com
42127	2505	6	torque-raffic	torque.com
42128	2505	17	torque-raffic	torque.com
42129	2506	6	jbroker	objectscape.com
42130	2506	17	jbroker	objectscape.com
42131	2507	6	spock	tamu.edu
42132	2507	17	spock	tamu.edu
42133	2508	6	jdatastore	JDataStore inprise.com
42134	2508	17	jdatastore	JDataStore inprise.com
42135	2509	6	fjmpss	saint.nm.fujitsu.co.jp
42136	2509	17	fjmpss	saint.nm.fujitsu.co.jp
42137	2510	6	fjappmgrbulk	ael.fujitsu.co.jp
42138	2510	17	fjappmgrbulk	ael.fujitsu.co.jp
42139	2511	6	metastorm	metastorm.com
42140	2511	17	metastorm	metastorm.com
42141	2512	6	citrixima	Citrix IMA citrix.com
42142	2512	17	citrixima	Citrix IMA citrix.com
42143	2513	6	citrixadmin	Citrix Admin citrix.com
42144	2513	17	citrixadmin	Citrix Admin citrix.com
42145	2514	6	facsys-ntp	Facsys NTP facsys.com
42146	2514	17	facsys-ntp	Facsys NTP facsys.com
42147	2515	6	facsys-router	Facsys Router facsys.com
42148	2515	17	facsys-router	Facsys Router facsys.com
42149	2516	6	maincontrol	Main Control maincontrol.com
42150	2516	17	maincontrol	Main Control maincontrol.com
42151	2517	6	call-sig-trans	H.323 Annex E Call Signalling Transport vocaltec.com
42152	2517	17	call-sig-trans	H.323 Annex E Call Signalling Transport vocaltec.com
42153	2518	6	willy	hudsmoar.com
42154	2518	17	willy	hudsmoar.com
42155	2519	6	globmsgsvc	hf.intel.com
42156	2519	17	globmsgsvc	hf.intel.com
42157	2520	6	pvsw	pervasive.com
42158	2520	17	pvsw	pervasive.com
42159	2521	6	adaptecmgr	Adaptec Manager ntc.adaptec.com
42160	2521	17	adaptecmgr	Adaptec Manager ntc.adaptec.com
42161	2522	6	windb	arium.com
42162	2522	17	windb	arium.com
42163	2523	6	qke-llc-v3	Qke LLC V.3 kecam-han.de
45170	54321	17	nbsp;	Back Orifice 2000 (UDP)
42164	2523	17	qke-llc-v3	Qke LLC V.3 kecam-han.de
42165	2524	6	optiwave-lm	Optiwave License Management opticwave.com
42166	2524	17	optiwave-lm	Optiwave License Management opticwave.com
42167	2525	6	ms-v-worlds	MS V-Worlds microsoft.com
42168	2525	17	ms-v-worlds	MS V-Worlds microsoft.com
42169	2526	6	ema-sent-lm	EMA License Manager emaden.com
42170	2526	17	ema-sent-lm	EMA License Manager emaden.com
42171	2527	6	iqserver	IQ Server akbs.com
42172	2527	17	iqserver	IQ Server akbs.com
42173	2528	6	ncr_ccl	NCR CCL woodbridgeNJ.ncr.com
42174	2528	17	ncr_ccl	NCR CCL woodbridgeNJ.ncr.com
42175	2529	6	utsftp	UTS FTP uttc-uts.com
42176	2529	17	utsftp	UTS FTP uttc-uts.com
42177	2530	6	vrcommerce	VR Commerce haifa.vnet.ibm.com
42178	2530	17	vrcommerce	VR Commerce haifa.vnet.ibm.com
42179	2531	6	ito-e-gui	ITO-E GUI hp.com
42180	2531	17	ito-e-gui	ITO-E GUI hp.com
42181	2532	6	ovtopmd	hp.com
42182	2532	17	ovtopmd	hp.com
42183	2533	6	snifferserver	SnifferServer nai.com
42184	2533	17	snifferserver	SnifferServer nai.com
42185	2534	6	combox-web-acc	Combox Web Access combox.co.il
42186	2534	17	combox-web-acc	Combox Web Access combox.co.il
42187	2535	17	madcap	Multicast Address Dynamic Client Allocation Protocol sun.com
42188	2536	6	btpp2audctrl	bt-sys.bt.co.uk
42189	2536	17	btpp2audctrl	bt-sys.bt.co.uk
42190	2537	6	upgrade	Upgrade Protocol dst-inc.com
42191	2537	17	upgrade	Upgrade Protocol dst-inc.com
42192	2538	6	vnwk-prapi	VisualNetworks.com
42193	2538	17	vnwk-prapi	VisualNetworks.com
42194	2539	6	vsiadmin	VSI Admin vsi.com
42195	2539	17	vsiadmin	VSI Admin vsi.com
42196	2540	6	lonworks	LonWorks echelon.com
42197	2540	17	lonworks	LonWorks echelon.com
42198	2541	6	lonwork2	LonWorks2 echelon.com
42199	2541	17	lonwork2	LonWorks2 echelon.com
42200	2542	6	davinci	daVinci tzi.de
42201	2542	17	davinci	daVinci tzi.de
42202	2543	6	reftek	reftek.com
42203	2543	17	reftek	reftek.com
42204	2543	6	sip	rfc2543
42205	2543	17	sip	rfc2543
42206	2544	6	novell-zen	Novell ZEN novell.com
42207	2544	17	novell-zen	Novell ZEN novell.com
42208	2545	6	sis-emt	securicor.co.uk
42209	2545	17	sis-emt	securicor.co.uk
42210	2546	6	vytalvaultbrtp	vytalnet.com
42211	2546	17	vytalvaultbrtp	vytalnet.com
42212	2547	6	vytalvaultvsmp	vytalnet.com
42213	2547	17	vytalvaultvsmp	vytalnet.com
42214	2548	6	vytalvaultpipe	vytalnet.com
42215	2548	17	vytalvaultpipe	vytalnet.com
42216	2549	6	ipass	pass.com
42217	2549	17	ipass	pass.com
42218	2550	6	ads	adobe.com
42219	2550	17	ads	adobe.com
42220	2551	6	isg-uda-server	ISG UDA Server isgsoft.com
42221	2551	17	isg-uda-server	ISG UDA Server isgsoft.com
42222	2552	6	call-logging	ascend.com
42223	2552	17	call-logging	ascend.com
42224	2553	6	efidiningport	execpc.com
42225	2553	17	efidiningport	execpc.com
42226	2554	6	vcnet-link-v10	freemail.c3.hu
42227	2554	17	vcnet-link-v10	freemail.c3.hu
42228	2555	6	compaq-wcp	compaq.com
42229	2555	17	compaq-wcp	compaq.com
42230	2556	6	nicetec-nmsvc	nicetec.de
42231	2556	17	nicetec-nmsvc	nicetec.de
42232	2557	6	nicetec-mgmt	nicetec.de
42233	2557	17	nicetec-mgmt	nicetec.de
42234	2558	6	pclemultimedia	PCLE Multi Media pinnaclesys.com
42235	2558	17	pclemultimedia	PCLE Multi Media pinnaclesys.com
42236	2559	6	lstp	us.ibm.com
42237	2559	17	lstp	us.ibm.com
42238	2560	6	labrat	austin.ibm.com
42239	2560	17	labrat	austin.ibm.com
42240	2561	6	mosaixcc	MosaixCC mosaix.com
42241	2561	17	mosaixcc	MosaixCC mosaix.com
42242	2562	6	delibo	novawiz.com
42243	2562	17	delibo	novawiz.com
42244	2563	6	cti-redwood	CTI Redwood daou.co.kr
42245	2563	17	cti-redwood	CTI Redwood daou.co.kr
42246	2564	6	hp-3000-telnet	HP 3000 NS/VT block mode telnet
42247	2565	6	coord-svr	Coordinator Server ensemblesoft.com
42248	2565	17	coord-svr	Coordinator Server ensemblesoft.com
42249	2565	6	striker	Striker Trojan Horse
42250	2565	17	striker	Striker Trojan Horse
42251	2566	6	pcs-pcw	pcare.com
42252	2566	17	pcs-pcw	pcare.com
42253	2567	6	clp	Cisco Line Protocol cisco.com
42254	2567	17	clp	Cisco Line Protocol cisco.com
42255	2568	6	spamtrap	Spam Trap benatong.com
42256	2568	17	spamtrap	Spam Trap benatong.com
42257	2569	6	sonuscallsig	Sonus Call Signal sonusnet.com
42258	2569	17	sonuscallsig	Sonus Call Signal sonusnet.com
42259	2570	6	hs-port	il.netect.com
42260	2570	17	hs-port	il.netect.com
42261	2571	6	cecsvc	corder-eng.com
42262	2571	17	cecsvc	corder-eng.com
42263	2572	6	ibp	IBP activ.net.au
42264	2572	17	ibp	IBP activ.net.au
42265	2573	6	trustestablish	Trust Establish haifa.vnet.ibm.com
42266	2573	17	trustestablish	Trust Establish haifa.vnet.ibm.com
42267	2574	6	blockade-bpsp	Blockade BPSP blockade.com
42268	2574	17	blockade-bpsp	Blockade BPSP blockade.com
42269	2575	6	hl7	HL7
42270	2575	17	hl7	HL7
42271	2576	6	tclprodebugger	TCL Pro Bebugger scriptics.com
42272	2576	17	tclprodebugger	TCL Pro Bebugger scriptics.com
42273	2577	6	scipticslsrvr	Scriptics Lsrvr scriptics.com
42274	2577	17	scipticslsrvr	Scriptics Lsrvr scriptics.com
42275	2578	6	rvs-isdn-dcp	RVS ISDN DCP rvscom.com
42276	2578	17	rvs-isdn-dcp	RVS ISDN DCP rvscom.com
42277	2579	6	mpfoncl	kel.fujitsu.co.jp
42278	2579	17	mpfoncl	kel.fujitsu.co.jp
42279	2580	6	tributary	bristol.com
42280	2580	17	tributary	bristol.com
42281	2581	6	argis-te	ARGIS TE argis.com
42282	2581	17	argis-te	ARGIS TE argis.com
42283	2582	6	argis-ds	ARGIS DS argis.com
42284	2582	17	argis-ds	ARGIS DS argis.com
42285	2583	6	mon	transmeta.com
42286	2583	17	mon	transmeta.com
42287	2583	6	wincrash	Wincrash Trojan Horse
42288	2583	17	wincrash	Wincrash Trojan Horse
42289	2584	6	cyaserv	cyasolutions.com
42290	2584	17	cyaserv	cyasolutions.com
42291	2585	6	netx-server	ipmetrics.com
42292	2585	17	netx-server	ipmetrics.com
42293	2586	6	netx-agent	ipmetrics.com
42294	2586	17	netx-agent	ipmetrics.com
42295	2587	6	masc	catarina.usc.edu
42296	2587	17	masc	catarina.usc.edu
42297	2588	6	privilege	aks.com
42298	2588	17	privilege	aks.com
42299	2589	6	quartus-tcl	quartus tcl altera.com
42300	2589	17	quartus-tcl	quartus tcl altera.com
42301	2590	6	idotdist	invino.com
42302	2590	17	idotdist	invino.com
42303	2591	6	maytagshuffle	Maytag Shuffle maytag.com
42304	2591	17	maytagshuffle	Maytag Shuffle maytag.com
42305	2592	6	netrek	teamquest.com
42306	2592	17	netrek	teamquest.com
42307	2593	6	mns-mail	MNS Mail Notice Service nd.net.fujitsu.co.jp
42308	2593	17	mns-mail	MNS Mail Notice Service nd.net.fujitsu.co.jp
42309	2594	6	dts	Database Server home-online.de
42310	2594	17	dts	Database Server home-online.de
42311	2595	6	worldfusion1	worldfusion.com
42312	2595	17	worldfusion1	worldfusion.com
42313	2596	6	worldfusion2	worldfusion.com
42314	2596	17	worldfusion2	worldfusion.com
42315	2597	6	homesteadglory	Homestead Glory homestead.com
42316	2597	17	homesteadglory	Homestead Glory homestead.com
42317	2598	6	citriximaclient	Citrix MA Client citrix.com
42318	2598	17	citriximaclient	Citrix MA Client citrix.com
42319	2599	6	meridiandata	Meridian Data meridian-data.com
42320	2599	17	meridiandata	Meridian Data meridian-data.com
42321	2600	6	hpstgmgr	cnd.hp.com
42322	2600	17	hpstgmgr	cnd.hp.com
42323	2600	6	zebrasrv	zebra service
42324	2601	6	discp-client	3Com.com
42325	2601	17	discp-client	3Com.com
42326	2601	6	zebra	zebra vty
42327	2602	6	discp-server	3Com.com
42328	2602	17	discp-server	3Com.com
42329	2602	6	ripd	RIPd vty
42330	2603	6	servicemeter	Service meter synoia.com
42331	2603	17	servicemeter	Service meter synoia.com
42332	2603	6	ripngd	RIPngd vty
42333	2604	6	nsc-ccs	NSC CCS networksciences.net
42334	2604	17	nsc-ccs	NSC CCS networksciences.net
42335	2604	6	ospfd	OSPFd vty
42336	2605	6	nsc-posa	NSC POSA networksciences.net
42337	2605	17	nsc-posa	NSC POSA networksciences.net
42338	2605	6	bgpd	BGPd vty
42339	2606	6	netmon	Dell Netmon dell.com
42340	2606	17	netmon	Dell Netmon dell.com
42341	2607	6	connection	Dell Connection dell.com
42342	2607	17	connection	Dell Connection dell.com
42343	2608	6	wag-service	wag.ch
42344	2608	17	wag-service	wag.ch
42345	2609	6	system-monitor	alphalink.com.au
42346	2609	17	system-monitor	alphalink.com.au
42347	2610	6	versa-tek	versatek.com
42348	2610	17	versa-tek	versatek.com
42349	2611	6	lionhead	lionhead.co.uk
42350	2611	17	lionhead	lionhead.co.uk
42351	2612	6	qpasa-agent	mqsoftware.com
42352	2612	17	qpasa-agent	mqsoftware.com
42353	2613	6	smntubootstrap	SMNTBootstrap metrics.com
42354	2613	17	smntubootstrap	SMNTBootstrap metrics.com
42355	2614	6	neveroffline	Never offline amo.net
42356	2614	17	neveroffline	Never offline amo.net
42357	2615	6	firepower	surfree.com
42358	2615	17	firepower	surfree.com
42359	2616	6	appswitch-emp	toplayer.com
42360	2616	17	appswitch-emp	toplayer.com
42361	2617	6	cmadmin	Clinical Context Managers sentillion.com
42362	2617	17	cmadmin	Clinical Context Managers sentillion.com
42363	2618	6	priority-e-com	Priority E-Com eshbel.com
42364	2618	17	priority-e-com	Priority E-Com eshbel.com
42365	2619	6	bruce	sun.com
42366	2619	17	bruce	sun.com
42367	2620	6	lpsrecommender	andromedia.com
42368	2620	17	lpsrecommender	andromedia.com
42369	2621	6	miles-apart	Miles Apart jukebox Server milesinfo.com
42370	2621	17	miles-apart	Miles Apart jukebox Server milesinfo.com
42371	2622	6	metricadbc	MetricaDBC metrica.co.uk
42372	2622	17	metricadbc	MetricaDBC metrica.co.uk
42373	2623	6	lmdp	rockettalk.com
42374	2623	17	lmdp	rockettalk.com
42375	2624	6	aria	andromedia.com
42376	2624	17	aria	andromedia.com
42377	2625	6	blwnkl-port	Blwnkl Port 3Com.com
42378	2625	17	blwnkl-port	Blwnkl Port 3Com.com
42379	2626	6	gbjd816	tfn.com
42380	2626	17	gbjd816	tfn.com
42381	2627	6	moshebeeri	Moshe Berri whale-com.com
42382	2627	17	moshebeeri	Moshe Berri whale-com.com
42383	2627	6	webster	Network Directory
42384	2627	17	webster	Network Directory
42385	2628	6	dict	cs.unc.edu
42386	2628	17	dict	cs.unc.edu
42387	2629	6	sitaraserver	Sitara Server sitaranetworks.com
42388	2629	17	sitaraserver	Sitara Server sitaranetworks.com
42389	2630	6	sitaramgmt	Sitara Management sitaranetworks.com
42390	2630	17	sitaramgmt	Sitara Management sitaranetworks.com
42391	2631	6	sitaradir	Sitara Dir sitaranetworks.com
42392	2631	17	sitaradir	Sitara Dir sitaranetworks.com
42393	2632	6	irdg-post	IRdg Post irdg.com
42394	2632	17	irdg-post	IRdg Post irdg.com
42395	2633	6	interintelli	inter-intelli.com
42396	2633	17	interintelli	inter-intelli.com
42397	2634	6	pk-electronics	PK Electronics pkworld.com
42398	2634	17	pk-electronics	PK Electronics pkworld.com
42399	2635	6	backburner	Back Burner metacreations.com
42400	2635	17	backburner	Back Burner metacreations.com
42401	2636	6	solve	sydney.sterling.com
42402	2636	17	solve	sydney.sterling.com
42403	2637	6	imdocsvc	Import Document Service netright.com
42404	2637	17	imdocsvc	Import Document Service netright.com
42405	2638	6	sybaseanywhere	SSybase Anywhere sybase.com
42406	2638	17	sybaseanywhere	SSybase Anywhere sybase.com
42407	2639	6	aminet	AMInet alcorn.com
42408	2639	17	aminet	AMInet alcorn.com
42409	2640	6	sai_sentlm	Sabbagh Associates license Manager sabbagh.com
42410	2640	17	sai_sentlm	Sabbagh Associates license Manager sabbagh.com
42411	2641	6	hdl-srv	HDL Server cnri.reston.va.us
42412	2641	17	hdl-srv	HDL Server cnri.reston.va.us
42413	2642	6	tragic	j51.com
42414	2642	17	tragic	j51.com
42415	2643	6	gte-samp	GSC.GTE.com
42416	2643	17	gte-samp	GSC.GTE.com
42417	2644	6	travsoft-ipx-t	Travsoft IPX Tunnel travsoft.com
42418	2644	17	travsoft-ipx-t	Travsoft IPX Tunnel travsoft.com
42419	2645	6	novell-ipx-cmd	novell.com
42420	2645	17	novell-ipx-cmd	novell.com
42421	2646	6	and-lm	AND License Manager and.nl
42422	2646	17	and-lm	AND License Manager and.nl
42423	2647	6	syncserver	syncinc.com
42424	2647	17	syncserver	syncinc.com
42425	2648	6	upsnotifyprot	pro.via-rs.com.br
42426	2648	17	upsnotifyprot	pro.via-rs.com.br
42427	2649	6	vpsipport	csir.co.za
42428	2649	17	vpsipport	csir.co.za
42429	2650	6	eristwoguns	netpro.com
42430	2650	17	eristwoguns	netpro.com
42431	2651	6	ebinsite	EBInSite ebi.com
42432	2651	17	ebinsite	EBInSite ebi.com
42433	2652	6	interpathpanel	interpath.net
42434	2652	17	interpathpanel	interpath.net
42435	2653	6	sonus	sonusnet.com
42436	2653	17	sonus	sonusnet.com
42437	2654	6	corel_vncadmin	Corel VNC Admin corelcomputer.com
42438	2654	17	corel_vncadmin	Corel VNC Admin corelcomputer.com
42439	2655	6	unglue	UNIX Nt Glue pscomp.com
42440	2655	17	unglue	UNIX Nt Glue pscomp.com
42441	2656	6	kana	kana.com
42442	2656	17	kana	kana.com
42443	2657	6	sns-dispatcher	firstfloor.com
42444	2657	17	sns-dispatcher	firstfloor.com
42445	2658	6	sns-admin	firstfloor.com
42446	2658	17	sns-admin	firstfloor.com
42447	2659	6	sns-query	firstfloor.com
42448	2659	17	sns-query	firstfloor.com
42449	2660	6	gcmonitor	geodesic.com
42450	2660	17	gcmonitor	geodesic.com
42451	2661	6	olhost	lan-aces.com
42452	2661	17	olhost	lan-aces.com
42453	2662	6	bintec-capi	BinTec-CAPI
42454	2662	17	bintec-capi	BinTec-CAPI
42455	2663	6	bintec-tapi	BinTec-TAPI
42456	2663	17	bintec-tapi	BinTec-TAPI
42457	2664	6	command-mq-gm	Command MQ GM boole.com
42458	2664	17	command-mq-gm	Command MQ GM boole.com
42459	2665	6	command-mq-pm	Command MQ PM boole.com
42460	2665	17	command-mq-pm	Command MQ PM boole.com
42461	2666	6	extensis	extensis.com
42462	2666	17	extensis	extensis.com
42463	2667	6	alarm-clock-s	Alarm Clock Server tatanka.com
42464	2667	17	alarm-clock-s	Alarm Clock Server tatanka.com
42465	2668	6	alarm-clock-c	Alarm clock Client tatanka.com
42466	2668	17	alarm-clock-c	Alarm clock Client tatanka.com
42467	2669	6	toad	tanaka.com
42468	2669	17	toad	tanaka.com
42469	2670	6	tve-announce	TVE Announce corp.webtv.net
42470	2670	17	tve-announce	TVE Announce corp.webtv.net
42471	2671	6	newlixreg	gaaj.qc.ca
42472	2671	17	newlixreg	gaaj.qc.ca
42473	2672	6	nhserver	aran.co.uk
42474	2672	17	nhserver	aran.co.uk
42475	2673	6	firstcall42	First Call 42 tfn.com
42476	2673	17	firstcall42	First Call 42 tfn.com
42477	2674	6	ewnn	omronsoft.co.jp
42478	2674	17	ewnn	omronsoft.co.jp
42479	2675	6	ttc-etap	ttc.com
42480	2675	17	ttc-etap	ttc.com
42481	2676	6	simslink	simsware.com
42482	2676	17	simslink	simsware.com
42483	2677	6	gadgetgate1way	Gadget Gate 1 Way internetgadgets.com
42484	2677	17	gadgetgate1way	Gadget Gate 1 Way internetgadgets.com
42485	2678	6	gadgetgate2way	Gadget Gate 2 Way internetgadgets.com
42486	2678	17	gadgetgate2way	Gadget Gate 2 Way internetgadgets.com
42487	2679	6	syncserverssl	Sync Server SSL syncinc.com
42488	2679	17	syncserverssl	Sync Server SSL syncinc.com
42489	2680	6	pxc-sapxom	cp10.es.xerox.com
42490	2680	17	pxc-sapxom	cp10.es.xerox.com
42491	2681	6	mpnjsomb	pfu.co.jp
42492	2681	17	mpnjsomb	pfu.co.jp
42493	2682	6	srsp	cs.umu.se
42494	2682	17	srsp	cs.umu.se
42495	2683	6	ncdloadbalance	NCDLoadBalance ncd.com
42496	2683	17	ncdloadbalance	NCDLoadBalance ncd.com
42497	2684	6	mpnjsosv	pfu.co.jp
42498	2684	17	mpnjsosv	pfu.co.jp
42499	2685	6	mpnjsocl	pfu.co.jp
42500	2685	17	mpnjsocl	pfu.co.jp
42501	2686	6	mpnjsomg	pfu.co.jp
42502	2686	17	mpnjsomg	pfu.co.jp
42503	2687	6	pq-lic-mgmt	pqsystems.com
42504	2687	17	pq-lic-mgmt	pqsystems.com
42505	2688	6	md-cg-http	execmail.ca
42506	2688	17	md-cg-http	execmail.ca
42507	2689	6	fastlynx	sewelld.com
42508	2689	17	fastlynx	sewelld.com
42509	2690	6	hp-nnm-data	HP NNM Embedded Database cnd.hp.com
42510	2690	17	hp-nnm-data	HP NNM Embedded Database cnd.hp.com
42511	2691	6	itinternet	IT Internet itinternet.net
42512	2691	17	itinternet	IT Internet itinternet.net
42513	2692	6	admins-lms	Admins LMS admins.com
42514	2692	17	admins-lms	Admins LMS admins.com
42515	2693	6	belarc-http	belarc.com
42516	2693	17	belarc-http	belarc.com
42517	2694	6	pwrsevent	np.lps.cs.fujitsu.co.jp
42518	2694	17	pwrsevent	np.lps.cs.fujitsu.co.jp
42519	2695	6	vspread	np.lps.cs.fujitsu.co.jp
42520	2695	17	vspread	np.lps.cs.fujitsu.co.jp
42521	2696	6	unifyadmin	Unify Admin unity.com
42522	2696	17	unifyadmin	Unify Admin unity.com
42523	2697	6	oce-snmp-trap	Oce SNMP Trap Port oce.nl
42524	2697	17	oce-snmp-trap	Oce SNMP Trap Port oce.nl
42525	2698	6	mck-ivpip	mck.com
42526	2698	17	mck-ivpip	mck.com
42527	2699	6	csoft-plusclnt	Csoft Plus Client csoft.bg
42528	2699	17	csoft-plusclnt	Csoft Plus Client csoft.bg
42529	2700	6	tqdata	teamquest.com
42530	2700	17	tqdata	teamquest.com
42531	2701	6	sms-rcinfo	microsoft.com
42532	2701	17	sms-rcinfo	microsoft.com
42533	2702	6	sms-xfer	microsoft.com
42534	2702	17	sms-xfer	microsoft.com
42535	2703	6	sms-chat	microsoft.com
42536	2703	17	sms-chat	microsoft.com
42537	2704	6	sms-remctrl	microsoft.com
42538	2704	17	sms-remctrl	microsoft.com
42539	2705	6	sds-admin	sun.com
42540	2705	17	sds-admin	sun.com
42541	2706	6	ncdmirroring	NCD Mirroring ncd.com
42542	2706	17	ncdmirroring	NCD Mirroring ncd.com
42543	2707	6	emcsymapiport	emc.com
42544	2707	17	emcsymapiport	emc.com
42545	2708	6	banyan-net	banyannetworks.com
42546	2708	17	banyan-net	banyannetworks.com
42547	2709	6	supermon	acl.lanl.gov
42548	2709	17	supermon	acl.lanl.gov
42549	2710	6	sso-service	okiok.com
42550	2710	17	sso-service	okiok.com
42551	2711	6	sso-control	okiok.com
42552	2711	17	sso-control	okiok.com
42553	2712	6	aocp	Axapta Object Communication Protocol dk.damgaard.com
42554	2712	17	aocp	Axapta Object Communication Protocol dk.damgaard.com
42555	2713	6	raven1	unified-technologies.com
42556	2713	17	raven1	unified-technologies.com
42557	2714	6	raven2	unified-technologies.com
42558	2714	17	raven2	unified-technologies.com
42559	2715	6	hpstgmgr2	cnd.hp.com
42560	2715	17	hpstgmgr2	cnd.hp.com
42561	2716	6	inova-ip-disco	inovacorp.com
42562	2716	17	inova-ip-disco	inovacorp.com
42563	2717	6	pn-requester	bmc.com
42564	2717	17	pn-requester	bmc.com
42565	2718	6	pn-requester2	bmc.com
42566	2718	17	pn-requester2	bmc.com
42567	2719	6	scan-change	Scan & Change lucent.com
42568	2719	17	scan-change	Scan & Change lucent.com
42569	2720	6	wkars	wirelessknowledge.com
42570	2720	17	wkars	wirelessknowledge.com
42571	2721	6	smart-diagnose	meek.com
42572	2721	17	smart-diagnose	meek.com
42573	2722	6	proactivesrvr	il.ibm.com
42574	2722	17	proactivesrvr	il.ibm.com
42575	2723	6	watchdognt	WatchDog NT llwin.com
42576	2723	17	watchdognt	WatchDog NT llwin.com
42577	2724	6	qotps	queryobject.com
42578	2724	17	qotps	queryobject.com
42579	2725	6	msolap-ptp2	microsoft.com
42580	2725	17	msolap-ptp2	microsoft.com
42581	2726	6	tams	jti.bc.ca
42582	2726	17	tams	jti.bc.ca
42583	2727	6	mgcp-callagent	Media Gateway Control Protocol Call Agent, research.telcordia.com
42584	2727	17	mgcp-callagent	Media Gateway Control Protocol Call Agent, research.telcordia.com
42585	2728	6	sqdr	starquest.com
42586	2728	17	sqdr	starquest.com
42587	2729	6	tcim-control	TCIM Control ftw.rsc.raytheon.com
42588	2729	17	tcim-control	TCIM Control ftw.rsc.raytheon.com
42589	2730	6	nec-raidplus	NEC RaidPlus nw1.file.fc.nec.co.jp
42590	2730	17	nec-raidplus	NEC RaidPlus nw1.file.fc.nec.co.jp
42591	2731	6	netdragon-msngr	NetDragon Messanger rwater.globalnet.co.uk
42592	2731	17	netdragon-msngr	NetDragon Messanger rwater.globalnet.co.uk
42593	2732	6	g5m	acm.org
42594	2732	17	g5m	acm.org
42595	2733	6	signet-ctf	sac.net
42596	2733	17	signet-ctf	sac.net
42597	2734	6	ccs-software	ccs-software.co.za
42598	2734	17	ccs-software	ccs-software.co.za
42599	2735	6	monitorconsole	Monitor Console ganymede.com
42600	2735	17	monitorconsole	Monitor Console ganymede.com
42601	2736	6	radwiz-nms-srv	israels@209.88.177.2
42602	2736	17	radwiz-nms-srv	israels@209.88.177.2
42603	2737	6	srp-feedback	epf1.ch
42604	2737	17	srp-feedback	epf1.ch
42605	2738	6	ndl-tcp-ois-gw	NDL TCP-OSI Gateway
42606	2738	17	ndl-tcp-ois-gw	NDL TCP-OSI Gateway
42607	2739	6	tn-timing	TN Timing engineer.com
42608	2739	17	tn-timing	TN Timing engineer.com
42609	2740	6	alarm	bfpg.ru
42610	2740	17	alarm	bfpg.ru
42611	2741	6	tsb	freeway.proxy.lucent.com
42612	2741	17	tsb	freeway.proxy.lucent.com
42613	2742	6	tsb2	freeway.proxy.lucent.com
42614	2742	17	tsb2	freeway.proxy.lucent.com
42615	2743	6	murx	dachbu.de
42616	2743	17	murx	dachbu.de
42617	2744	6	honyaku	omronsoft.com
42618	2744	17	honyaku	omronsoft.com
42619	2745	6	urbisnet	urbis.net
42620	2745	17	urbisnet	urbis.net
42621	2746	6	cpudpencap	checkpoint.com
42622	2746	17	cpudpencap	checkpoint.com
42623	2747	6	fjippol-swrly	yk.fujitsu.co.jp
42624	2747	17	fjippol-swrly	yk.fujitsu.co.jp
42625	2748	6	fjippol-polsvr	yk.fujitsu.co.jp
42626	2748	17	fjippol-polsvr	yk.fujitsu.co.jp
42627	2749	6	fjippol-cns1	yk.fujitsu.co.jp
42628	2749	17	fjippol-cns1	yk.fujitsu.co.jp
42629	2750	6	fjippol-port1	yk.fujitsu.co.jp
42630	2750	17	fjippol-port1	yk.fujitsu.co.jp
42631	2751	6	fjippol-port2	yk.fujitsu.co.jp
42632	2751	17	fjippol-port2	yk.fujitsu.co.jp
42633	2752	6	rsisysaccess	RSISYS ACCESS
42634	2752	17	rsisysaccess	RSISYS ACCESS
42635	2753	6	de-spot	digitalenvoy.net
42636	2753	17	de-spot	digitalenvoy.net
42637	2754	6	apollo-cc	brandcomms.com
42638	2754	17	apollo-cc	brandcomms.com
42639	2755	6	expresspay	netcom.ca
42640	2755	17	expresspay	netcom.ca
42641	2756	6	simplement-tie	netvision.net.il
42642	2756	17	simplement-tie	netvision.net.il
42643	2757	6	cnrp	se.abb.com
42644	2757	17	cnrp	se.abb.com
42645	2758	6	apollo-status	brandcomms.com
42646	2758	17	apollo-status	brandcomms.com
42647	2759	6	apollo-gms	brandcomms.com
42648	2759	17	apollo-gms	brandcomms.com
42649	2760	6	sabams	Saba MS saba.com
42650	2760	17	sabams	Saba MS saba.com
42651	2761	6	dicom-iscl	DICOM ISCL scr.siemens.com
42652	2761	17	dicom-iscl	DICOM ISCL scr.siemens.com
42653	2762	6	dicom-tls	DICOM TLS scr.siemens.com
42654	2762	17	dicom-tls	DICOM TLS scr.siemens.com
42655	2763	6	desktop-dna	Desktop DNA miramarsys.com
42656	2763	17	desktop-dna	Desktop DNA miramarsys.com
42657	2764	6	data-insurance	Data insurance standard.com
42658	2764	17	data-insurance	Data insurance standard.com
42659	2765	6	qip-audup	lucent.com
42660	2765	17	qip-audup	lucent.com
42663	2766	6	listen	System V listener port
42664	2767	6	uadtc	appliedis.com
42665	2767	17	uadtc	appliedis.com
42666	2768	6	uacs	appliedis.com
42667	2768	17	uacs	appliedis.com
42668	2769	6	singlept-mvs	Single Point MVS clark.net
42669	2769	17	singlept-mvs	Single Point MVS clark.net
42670	2770	6	veronica	coyote.org
42671	2770	17	veronica	coyote.org
42672	2771	6	vergencecm	Vergence CM sentillion.com
42673	2771	17	vergencecm	Vergence CM sentillion.com
42674	2772	6	auris	tid.es
42675	2772	17	auris	tid.es
42676	2773	6	pcbakcup1	PC Backup1 alice.net
42677	2773	17	pcbakcup1	PC Backup1 alice.net
42678	2774	6	pcbakcup2	PC Backup2 alice.net
42679	2774	17	pcbakcup2	PC Backup2 alice.net
42680	2775	6	smpp	aldiscon.ie
42681	2775	17	smpp	aldiscon.ie
42682	2776	6	ridgeway1	Ridgeway Systems & Software ridgeway-sys.com
42683	2776	17	ridgeway1	Ridgeway Systems & Software ridgeway-sys.com
42684	2777	6	ridgeway2	Ridgeway Systems & Software ridgeway-sys.com
42685	2777	17	ridgeway2	Ridgeway Systems & Software ridgeway-sys.com
42686	2778	6	gwen-sonya	inconnect.com
42687	2778	17	gwen-sonya	inconnect.com
42688	2779	6	lbc-sync	net.paso.fujitsu.co.jp
42689	2779	17	lbc-sync	net.paso.fujitsu.co.jp
42690	2780	6	lbc-control	net.paso.fujitsu.co.jp
42691	2780	17	lbc-control	net.paso.fujitsu.co.jp
42692	2781	6	whosells	gnss.com
42693	2781	17	whosells	gnss.com
42694	2782	6	everydayrc	ahti.bluemoon.ee
42695	2782	17	everydayrc	ahti.bluemoon.ee
42696	2783	6	aises	pgaero.co.uk
42697	2783	17	aises	pgaero.co.uk
42698	2784	6	www-dev	World Wide Web - development
42699	2784	17	www-dev	World Wide Web - development
42700	2785	6	aic-np	american.com
42701	2785	17	aic-np	american.com
42702	2786	6	aic-oncrpc	Destiny MCD Database american.com
42703	2786	17	aic-oncrpc	Destiny MCD Database american.com
42704	2787	6	piccolo	Cornerstone Software corsof.com
42705	2787	17	piccolo	Cornerstone Software corsof.com
42706	2788	6	fryeserv	NetWare Loadable Module - Seagate Software
42707	2788	17	fryeserv	NetWare Loadable Module - Seagate Software
42708	2789	6	media-agent	brm.com
42709	2789	17	media-agent	brm.com
42710	2790	6	plgproxy	PLG Proxy aks.com
42711	2790	17	plgproxy	PLG Proxy aks.com
42712	2791	6	mtport-regist	MT Port Registrator iname.com
42713	2791	17	mtport-regist	MT Port Registrator iname.com
42714	2792	6	f5-globalsite	f5.com
42715	2792	17	f5-globalsite	f5.com
42716	2793	6	initlsmsad	compaq.com
42717	2793	17	initlsmsad	compaq.com
42718	2794	6	aaftp	ql.org
42719	2794	17	aaftp	ql.org
42720	2795	6	livestats	avidsports.com
42721	2795	17	livestats	avidsports.com
42722	2796	6	ac-tech	ac-tech.com
42723	2796	17	ac-tech	ac-tech.com
42724	2797	6	esp-encap	datafellows.com
42725	2797	17	esp-encap	datafellows.com
42726	2798	6	tmesis-upshot	timesis.com
42727	2798	17	tmesis-upshot	timesis.com
42728	2799	6	icon-discover	icon.at
42729	2799	17	icon-discover	icon.at
42730	2800	6	acc-raid	ntc.adaptec.com
42731	2800	17	acc-raid	ntc.adaptec.com
42732	2801	6	igcp	codemasters.com
42733	2801	17	igcp	codemasters.com
42734	2801	6	phineas	Phineas Phucker Trojan
42735	2801	17	phineas	Phineas Phucker Trojan
42736	2803	6	btprjctrl	bt.com
42737	2803	17	btprjctrl	bt.com
42738	2804	6	telexis-vtu	telexicorp.com
42739	2804	17	telexis-vtu	telexicorp.com
42740	2805	6	xta-wsp-s	WTA WSP-S (WAB Forum) art.alcatel.fr
42741	2805	17	xta-wsp-s	WTA WSP-S (WAB Forum) art.alcatel.fr
42742	2806	6	cspuni	pfu.co.jp
42743	2806	17	cspuni	pfu.co.jp
42744	2807	6	cspmulti	pfu.co.jp
42745	2807	17	cspmulti	pfu.co.jp
42746	2808	6	j-lan-p	jdl.co.jp
42747	2808	17	j-lan-p	jdl.co.jp
42748	2809	6	corbaloc	CORBA LOC dstc.edu.au
42749	2809	17	corbaloc	CORBA LOC dstc.edu.au
42750	2810	6	netsteward	Active Net Steward ndl.co.uk
42751	2810	17	netsteward	Active Net Steward ndl.co.uk
42752	2811	6	gsiftp	GSI FTP ncsa.uiuc.edu
42753	2811	17	gsiftp	GSI FTP ncsa.uiuc.edu
42754	2812	6	atmtcp	epfl.ch
42755	2812	17	atmtcp	epfl.ch
42756	2813	6	llm-pass	llmwin.com
42757	2813	17	llm-pass	llmwin.com
42758	2814	6	llm-csv	llmwin.com
42759	2814	17	llm-csv	llmwin.com
42760	2815	6	lbc-measure	LBC Measurement net.pasofujitsu.co.jp
42761	2815	17	lbc-measure	LBC Measurement net.pasofujitsu.co.jp
42762	2816	6	lbc-watchdog	LBC Watchdog net.paso.fujitsu.co.jp
42763	2816	17	lbc-watchdog	LBC Watchdog net.paso.fujitsu.co.jp
42764	2817	6	nmsigport	NMSig Port mail.inalp.com
42765	2817	17	nmsigport	NMSig Port mail.inalp.com
42766	2818	6	rmlnk	boi.hp.com
42767	2818	17	rmlnk	boi.hp.com
42768	2819	6	fc-faultnotify	FC Fault Notification boi.hp.com
42769	2819	17	fc-faultnotify	FC Fault Notification boi.hp.com
42770	2820	6	univision	fastfreenet.com
42771	2820	17	univision	fastfreenet.com
42772	2821	6	vml-dms	veritas.com
42773	2821	17	vml-dms	veritas.com
42774	2822	6	ka0wuc	ka0wuc.org
42775	2822	17	ka0wuc	ka0wuc.org
42776	2823	6	cqg-netlan	CQG Net/LAN cqg.com
42777	2823	17	cqg-netlan	CQG Net/LAN cqg.com
42778	2826	6	slc-systemlog	airtech.demon.nl
42779	2826	17	slc-systemlog	airtech.demon.nl
42780	2827	6	slc-ctrlrloops	airtech.demon.nl
42781	2827	17	slc-ctrlrloops	airtech.demon.nl
42782	2828	6	itm-lm	ITM License Manager
42783	2828	17	itm-lm	ITM License Manager
42784	2829	6	silkp1	silknet.com
42785	2829	17	silkp1	silknet.com
42786	2830	6	silkp2	silknet.com
42787	2830	17	silkp2	silknet.com
42788	2831	6	silkp3	silknet.com
42789	2831	17	silkp3	silknet.com
42790	2832	6	silkp4	silknet.com
42791	2832	17	silkp4	silknet.com
42792	2833	6	glishd	cv.nrao.edu
42793	2833	17	glishd	cv.nrao.edu
42794	2834	6	evtp	solution-soft.com
42795	2834	17	evtp	solution-soft.com
42796	2835	6	evtp-data	solution-soft.com
42797	2835	17	evtp-data	solution-soft.com
42798	2836	6	catalyst	jsb.com
42799	2836	17	catalyst	jsb.com
42800	2837	6	repliweb	softlinkusa.com
42801	2837	17	repliweb	softlinkusa.com
42802	2838	6	starbot	starbot.org
42803	2838	17	starbot	starbot.org
42804	2839	6	nmsigport	NMSigPort mail.inalp.com
42805	2839	17	nmsigport	NMSigPort mail.inalp.com
42806	2840	6	l3-exprt	l-3security.com
42807	2840	17	l3-exprt	l-3security.com
42808	2841	6	l3-ranger	l-3security.com
42809	2841	17	l3-ranger	l-3security.com
42810	2842	6	l3-hawk	l-3security.com
42811	2842	17	l3-hawk	l-3security.com
42812	2843	6	pdnet	PDnet apex.de
42813	2843	17	pdnet	PDnet apex.de
42814	2844	6	bpcp-poll	bestpower.gensig.com
42815	2844	17	bpcp-poll	bestpower.gensig.com
42816	2845	6	bpcp-trap	bestpower.gensig.com
42817	2845	17	bpcp-trap	bestpower.gensig.com
42818	2846	6	aimpp-hello	AIMPP Hello automationintelligence.com
42819	2846	17	aimpp-hello	AIMPP Hello automationintelligence.com
42820	2847	6	aimpp-port-reg	AIMPP Port Req automationintelligence.com
42821	2847	17	aimpp-port-reg	AIMPP Port Req automationintelligence.com
42822	2848	6	amt-blc-port	interbusiness.it
42823	2848	17	amt-blc-port	interbusiness.it
42824	2849	6	fxp	oanda.com
42825	2849	17	fxp	oanda.com
42826	2850	6	metaconsole	netaphor-software.com
42827	2850	17	metaconsole	netaphor-software.com
42828	2851	6	webemshttp	jetstream.com
42829	2851	17	webemshttp	jetstream.com
42830	2852	6	bears-01	bears.aust.com
42831	2852	17	bears-01	bears.aust.com
42832	2853	6	ispipes	emc.com
42833	2853	17	ispipes	emc.com
42834	2854	6	infomover	emc.com
42835	2854	17	infomover	emc.com
42836	2856	6	cesdinv	pfu.co.jp
42837	2856	17	cesdinv	pfu.co.jp
42838	2857	6	simctlp	SimCtIP gmx.net
42839	2857	17	simctlp	SimCtIP gmx.net
42840	2858	6	ecnp	certsoft.com
42841	2858	17	ecnp	certsoft.com
42842	2859	6	activememory	Active Memory edaconsulting.com
42843	2859	17	activememory	Active Memory edaconsulting.com
42844	2860	6	dialpad-voice1	dialpad.com
42845	2860	17	dialpad-voice1	dialpad.com
42846	2861	6	dialpad-voice2	dialpad.com
42847	2861	17	dialpad-voice2	dialpad.com
42848	2862	6	ttg-protocol	ttgsoftware.com
42849	2862	17	ttg-protocol	ttgsoftware.com
42850	2863	6	sonardata	sonardata.com
42851	2863	17	sonardata	sonardata.com
42852	2864	6	astromed-main	Main 5001 cmd astromed.com
42853	2864	17	astromed-main	Main 5001 cmd astromed.com
42854	2865	6	pit-vpn	linuxnetworks.de
42855	2865	17	pit-vpn	linuxnetworks.de
42856	2866	6	lwlistner	oz.quest.com
42857	2866	17	lwlistner	oz.quest.com
42858	2867	6	esps-portal	esps.com
42859	2867	17	esps-portal	esps.com
42860	2868	6	npep-messaging	norman.no
42861	2868	17	npep-messaging	norman.no
42862	2869	6	icslap	microsoft.com
42863	2869	17	icslap	microsoft.com
42864	2870	6	daishi	memphis.edu
42865	2870	17	daishi	memphis.edu
42866	2871	6	msi-selectplay	MSI Select Play mediastation.com
42867	2871	17	msi-selectplay	MSI Select Play mediastation.com
42868	2872	6	contract	telenor.com
42869	2872	17	contract	telenor.com
42870	2873	6	paspar2-zoomin	PASPAR2 Zoomin paspar2.com
42871	2873	17	paspar2-zoomin	PASPAR2 Zoomin paspar2.com
42872	2874	6	dxmessagebase1	delphix.com
42873	2874	17	dxmessagebase1	delphix.com
42874	2875	6	dxmessagebase2	delphix.com
42875	2875	17	dxmessagebase2	delphix.com
42876	2876	6	sps-tunnel	fortresstech.com
42877	2876	17	sps-tunnel	fortresstech.com
42878	2877	6	bluelance	bluelance.com
42879	2877	17	bluelance	bluelance.com
42880	2878	6	aap	sun.com
42881	2878	17	aap	sun.com
42882	2879	6	ucentric-ds	alevx@204.165.216.115
42883	2879	17	ucentric-ds	alevx@204.165.216.115
42884	2880	6	synapse	bix.com
42885	2880	17	synapse	bix.com
42886	2881	6	ndsp	gmx.at
42887	2881	17	ndsp	gmx.at
42888	2882	6	ndtp	gmx.at
42889	2882	17	ndtp	gmx.at
42890	2883	6	ndnp	gmx.at
42891	2883	17	ndnp	gmx.at
42892	2884	6	flashmsg	zinknet.com
42893	2884	17	flashmsg	zinknet.com
42894	2885	6	topflow	toplayer.com
42895	2885	17	topflow	toplayer.com
42896	2886	6	responselogic	responselogic.com
42897	2886	17	responselogic	responselogic.com
42898	2887	6	aironetddp	aironet.com
42899	2887	17	aironetddp	aironet.com
42900	2888	6	spcsdlobby	SPCsd_MWDD@hotmail.com
42901	2888	17	spcsdlobby	SPCsd_MWDD@hotmail.com
42902	2889	6	rsom	corsof.com
42903	2889	17	rsom	corsof.com
42904	2890	6	cspclmlti	pfu.co.jp
42905	2890	17	cspclmlti	pfu.co.jp
42906	2891	6	cinegrfx-elmd	CINEGRFX-ELMD License Manager cinegrfx.com
42907	2891	17	cinegrfx-elmd	CINEGRFX-ELMD License Manager cinegrfx.com
42908	2892	6	snifferdata	nai.com
42909	2892	17	snifferdata	nai.com
42910	2893	6	vseconnector	de.ibm.com
42911	2893	17	vseconnector	de.ibm.com
42912	2894	6	abacus-remote	zarak.com
42913	2894	17	abacus-remote	zarak.com
42914	2895	6	natuslink	natus.com
42915	2895	17	natuslink	natus.com
42916	2896	6	ecovisiong6-1	ecovision.se
42917	2896	17	ecovisiong6-1	ecovision.se
42918	2897	6	citrix-rtmp	citrix.com
42919	2897	17	citrix-rtmp	citrix.com
42920	2898	6	appliance-cfg	criticallink.com
42921	2898	17	appliance-cfg	criticallink.com
42922	2899	6	powergemplus	case.nm.fujitsu.co.jp
42923	2899	17	powergemplus	case.nm.fujitsu.co.jp
42924	2900	6	quicksuite	magisoft.com
42925	2900	17	quicksuite	magisoft.com
42926	2901	6	allstorcns	allstor.com
42927	2901	17	allstorcns	allstor.com
42928	2902	6	netaspi	NET ASPI mail.sercomm.com
42929	2902	17	netaspi	NET ASPI mail.sercomm.com
42930	2903	6	suitcase	extensis.com
42931	2903	17	suitcase	extensis.com
42932	2904	6	m2ua	nortelnetworks.com
42933	2904	17	m2ua	nortelnetworks.com
42934	2905	6	m3ua	nortelnetworks.com
42935	2905	17	m3ua	nortelnetworks.com
42936	2906	6	caller9	aol.com
42937	2906	17	caller9	aol.com
42938	2907	6	webmethods-b2b	webmethods.com
42939	2907	17	webmethods-b2b	webmethods.com
42940	2908	6	mao	babafou.eu.org
42941	2908	17	mao	babafou.eu.org
42942	2909	6	funk-dialout	funk.com
42943	2909	17	funk-dialout	funk.com
42944	2910	6	tdaccess	TDAccess metrics.com
42945	2910	17	tdaccess	TDAccess metrics.com
42946	2911	6	blockade	interlog.com
42947	2911	17	blockade	interlog.com
42948	2912	6	epicon	epicon.com
42949	2912	17	epicon	epicon.com
42950	2913	6	boosterware	Boster Ware netvision.net.il
42951	2913	17	boosterware	Boster Ware netvision.net.il
42952	2914	6	gamelobby	pfh@dial.pipex.com
42953	2914	17	gamelobby	pfh@dial.pipex.com
42954	2915	6	tksocket	TK Socket protix.com
42955	2915	17	tksocket	TK Socket protix.com
42956	2916	6	elvin_server	pobox.com
42957	2916	17	elvin_server	pobox.com
42958	2917	6	elvin_client	pobox.com
42959	2917	17	elvin_client	pobox.com
42960	2918	6	kastenchasepad	Kasten Chase Pad kastenchase.com
42961	2918	17	kastenchasepad	Kasten Chase Pad kastenchase.com
42962	2919	6	rober	heroix.co.uk
42963	2919	17	rober	heroix.co.uk
42964	2920	6	roboeda	heroix.co.uk
42965	2920	17	roboeda	heroix.co.uk
42966	2921	6	cesdcdman	CESD Contents Delivery Management pfu.co.jp
42967	2921	17	cesdcdman	CESD Contents Delivery Management pfu.co.jp
42968	2922	6	cesdcdtrn	CESD Contents Delivery Data Tranfer pfu.co.jp
42969	2922	17	cesdcdtrn	CESD Contents Delivery Data Tranfer pfu.co.jp
42970	2923	6	wta-wsp-wtp-s	(WAP Forum) art.alcatel.fr
42971	2923	17	wta-wsp-wtp-s	(WAP Forum) art.alcatel.fr
42972	2924	6	precise-vip	precisesoft.co.il
42973	2924	17	precise-vip	precisesoft.co.il
42974	2925	6	frp	Firewall Redundancy Protocol ffnet.com
42975	2925	17	frp	Firewall Redundancy Protocol ffnet.com
42976	2926	6	mobile-file-dl	toda@mmedia.mci.mei.co.jp
42977	2926	17	mobile-file-dl	toda@mmedia.mci.mei.co.jp
42978	2927	6	unimobilectrl	graycell.com
42979	2927	17	unimobilectrl	graycell.com
42980	2928	6	restone-cpss	looman.org
42981	2928	17	restone-cpss	looman.org
42982	2929	6	panja-webadmin	panja.com
42983	2929	17	panja-webadmin	panja.com
42984	2930	6	panja-weblinx	panja.com
42985	2930	17	panja-weblinx	panja.com
42986	2931	6	circle-x	normfree@worldnet.att.net
42987	2931	17	circle-x	normfree@worldnet.att.net
42988	2932	6	incp	phobos.com
42989	2932	17	incp	phobos.com
42990	2933	6	4-tieropmgw	4-TIER OPM GW 4tier.com
42991	2933	17	4-tieropmgw	4-TIER OPM GW 4tier.com
42992	2934	6	4-tieropmcli	4-TIER OPM CLI 4tier.com
42993	2934	17	4-tieropmcli	4-TIER OPM CLI 4tier.com
42994	2935	6	qtp	inetco.com
42995	2935	17	qtp	inetco.com
42996	2936	6	otpatch	opentable.com
42997	2936	17	otpatch	opentable.com
42998	2937	6	pnaconsult-lm	nijssen.nl
42999	2937	17	pnaconsult-lm	nijssen.nl
43000	2938	6	sm-pas-1	metrics.com
43001	2938	17	sm-pas-1	metrics.com
43002	2939	6	sm-pas-2	metrics.com
43003	2939	17	sm-pas-2	metrics.com
43004	2940	6	sm-pas-3	metrics.com
43005	2940	17	sm-pas-3	metrics.com
43006	2941	6	sm-pas-4	metrics.com
43007	2941	17	sm-pas-4	metrics.com
43008	2942	6	sm-pas-5	metrics.com
43009	2942	17	sm-pas-5	metrics.com
43010	2943	6	ttnrepository	teltone.com
43011	2943	17	ttnrepository	teltone.com
43012	2944	6	megaco-h248	Megaco H-248 nortelnetworks.com
43013	2944	17	megaco-h248	Megaco H-248 nortelnetworks.com
43014	2945	6	h248-binary	H-248 Binary nortelnetworks.com
43015	2945	17	h248-binary	H-248 Binary nortelnetworks.com
43016	2946	6	fjsvmpor	fjh.se.fujitsu.co.jp
43017	2946	17	fjsvmpor	fjh.se.fujitsu.co.jp
43018	2947	6	gpsd	dementia.org
43019	2947	17	gpsd	dementia.org
43020	2948	6	wap-push	(WAP Forum) mail.wapforum.org
43021	2948	17	wap-push	(WAP Forum) mail.wapforum.org
43022	2949	6	wap-pushsecure	(WAP Forum) mail.forum.org
43023	2949	17	wap-pushsecure	(WAP Forum) mail.forum.org
43024	2950	6	esip	hp.com
43025	2950	17	esip	hp.com
43026	2951	6	ottp	onstreamsystems.com
43027	2951	17	ottp	onstreamsystems.com
43028	2952	6	mpfwsas	saint.nm.fujitsu.co.jp
43029	2952	17	mpfwsas	saint.nm.fujitsu.co.jp
43030	2953	6	ovalarmsrv	hp.com
43031	2953	17	ovalarmsrv	hp.com
43032	2954	6	ovalarmsrv-cmd	hp.com
43033	2954	17	ovalarmsrv-cmd	hp.com
43034	2955	6	csnotify	clickservice.com
43035	2955	17	csnotify	clickservice.com
43036	2956	6	ovrimosdbman	altera.gr
43037	2956	17	ovrimosdbman	altera.gr
43038	2957	6	jmact5	yk.fujitsu.co.jp
43039	2957	17	jmact5	yk.fujitsu.co.jp
43040	2958	6	jmact6	yk.fujitsu.co.jp
43041	2958	17	jmact6	yk.fujitsu.co.jp
43042	2959	6	rmopagt	yk.fujitsu.co.jp
43043	2959	17	rmopagt	yk.fujitsu.co.jp
43044	2960	6	dfoxserver	rentek.net
43045	2960	17	dfoxserver	rentek.net
43046	2961	6	boldsoft-lm	boldsoft.com
43047	2961	17	boldsoft-lm	boldsoft.com
43048	2962	6	iph-policy-cli	iphighway.com
43049	2962	17	iph-policy-cli	iphighway.com
43050	2963	6	iph-policy-adm	iphighway.com
43051	2963	17	iph-policy-adm	iphighway.com
43052	2964	6	bullant-srap	bullant.net
43053	2964	17	bullant-srap	bullant.net
43054	2965	6	bullant-rap	bullant.net
43055	2965	17	bullant-rap	bullant.net
43056	2966	6	idp-infotrieve	idpco.com
43057	2966	17	idp-infotrieve	idpco.com
43058	2967	6	ssc-agent	symantec.com
43059	2967	17	ssc-agent	symantec.com
43060	2968	6	enpp	exc.epson.co.jp
43061	2968	17	enpp	exc.epson.co.jp
43062	2969	6	essp	exc.epson.co.jp
43063	2969	17	essp	exc.epson.co.jp
43064	2970	6	index-net	lucent.com
43065	2970	17	index-net	lucent.com
43066	2971	6	netclip	cli.di.unipi.it
43067	2971	17	netclip	cli.di.unipi.it
43068	2972	6	pmsm-webrctl	pmsmicado.com
43069	2972	17	pmsm-webrctl	pmsmicado.com
43070	2973	6	svnetworks	svnetworks.com
43071	2973	17	svnetworks	svnetworks.com
43072	2974	6	signal	icall.com
43073	2974	17	signal	icall.com
43074	2975	6	fjmpcm	Fujitsu Configuration Management Service aint.nm.fujitsu.co.jp
43075	2975	17	fjmpcm	Fujitsu Configuration Management Service aint.nm.fujitsu.co.jp
43076	2976	6	cns-srv-port	CNS Server Port cisco.com
43077	2976	17	cns-srv-port	CNS Server Port cisco.com
43078	2977	6	ttc-etap-ns	TTCs Enterprise Test Access Protocol NS ttc.com
43079	2977	17	ttc-etap-ns	TTCs Enterprise Test Access Protocol NS ttc.com
43080	2978	6	ttc-etap-ds	TTCs Enterprise Test Access protocol DS ttc.com
43081	2978	17	ttc-etap-ds	TTCs Enterprise Test Access protocol DS ttc.com
43082	2979	6	h263-video	H.s63 Video Streaming acm.org
43083	2979	17	h263-video	H.s63 Video Streaming acm.org
43084	2980	6	wimd	Instant Messaging Service pobox.com
43085	2980	17	wimd	Instant Messaging Service pobox.com
43086	2981	6	mylxamport	mylex.com
43087	2981	17	mylxamport	mylex.com
43088	2982	6	iwb-whiteboard	adicarte.co.uk
43089	2982	17	iwb-whiteboard	adicarte.co.uk
43090	2983	6	netplan	bitrot.de
43091	2983	17	netplan	bitrot.de
43092	2984	6	hpidsadmin	cup.hp.com
43093	2984	17	hpidsadmin	cup.hp.com
43094	2985	6	hpidsagent	cup.hp.com
43095	2985	17	hpidsagent	cup.hp.com
43096	2986	6	stonefalls	stonefalls.com
43097	2986	17	stonefalls	stonefalls.com
43098	2987	6	identify	gnss.com
43099	2987	17	identify	gnss.com
43100	2988	6	classify	gnss.com
43101	2988	17	classify	gnss.com
43102	2989	6	zarkov	zarkov.com
43103	2989	17	zarkov	zarkov.com
43104	2990	6	boscap	hillbrecht.de
43105	2990	17	boscap	hillbrecht.de
43106	2991	6	wkstn-mon	lmco.com
43107	2991	17	wkstn-mon	lmco.com
43108	2992	6	itb301	itchigo.com
43109	2992	17	itb301	itchigo.com
43110	2993	6	veritas-vis1	veritas.com
43111	2993	17	veritas-vis1	veritas.com
43112	2994	6	veritas-vis2	veritas.com
43113	2994	17	veritas-vis2	veritas.com
43114	2995	6	idrs	intermec.com
43115	2995	17	idrs	intermec.com
43116	2996	6	vsixml	vsi.com
43117	2996	17	vsixml	vsi.com
43118	2997	6	rebol	REBOL rebol.net
43119	2997	17	rebol	REBOL rebol.net
43120	2998	6	realsecure	IIS Real Secure Console Service Port iss.net
43121	2998	17	realsecure	IIS Real Secure Console Service Port iss.net
43122	2999	6	remoteware-un	RemoteWare Unassigned xcellenet.com
43123	2999	17	remoteware-un	RemoteWare Unassigned xcellenet.com
43124	3000	6	hbci	ibm.net
43125	3000	17	hbci	ibm.net
43126	3000	6	remoteware-cl	Unassigned but widespred use xcellenet.com
43127	3000	17	remoteware-cl	Unassigned but widespred use xcellenet.com
43128	3000	6	firstclass	FirstClass (ftp channel on 510 TCP)
43129	3000	17	firstclass	FirstClass (ftp channel on 510 TCP)
43130	3000	6	ppp	Unassigned, User-level ppp daemon
43131	3001	6	redwood-broker	powerframe.com
43132	3001	17	redwood-broker	powerframe.com
43133	3002	6	exlm-agent	EXLM Agent clemson.edu
43134	3002	17	exlm-agent	EXLM Agent clemson.edu
43135	3003	6	cgms	tiscom.uscg.mil
43136	3003	17	cgms	tiscom.uscg.mil
43137	3004	6	csoftragent	Csoft Agent csoft.bg
43138	3004	17	csoftragent	Csoft Agent csoft.bg
43139	3005	6	geniuslm	Gebius License Manager genius.de
43140	3005	17	geniuslm	Gebius License Manager genius.de
43141	3005	6	deslogin	Unassigned, encrypted symmetric telnet/login
43142	3006	6	ii-admin	Instant Internet Admin baynetworks.com
43143	3006	17	ii-admin	Instant Internet Admin baynetworks.com
43144	3005	6	deslogind	Unassigned
43145	3007	6	lotusmtap	Lotus Mail Tracking Agent Protocol lotus.com
43146	3007	17	lotusmtap	Lotus Mail Tracking Agent Protocol lotus.com
43147	3008	6	midnight-tech	Midnight Technologies midnighttech.com
43148	3008	17	midnight-tech	Midnight Technologies midnighttech.com
43149	3009	6	pxc-ntfy	cp10.es.xerox.com
43150	3009	17	pxc-ntfy	cp10.es.xerox.com
43151	3010	6	gw	Telerate Workstation ccmail.dowjones.com
43152	3010	17	ping-pong	Telerate Workstation ccmail.dowjones.com
43153	3011	6	trusted-web	sse.ie
43154	3011	17	trusted-web	sse.ie
43155	3012	6	twsdss	sse.ie
43156	3012	17	twsdss	sse.ie
43157	3013	6	gilatskysurfer	Gilat Sky Surfer gilat.com
43158	3013	17	gilatskysurfer	Gilat Sky Surfer gilat.com
43159	3014	6	broker_service	novell.com
43160	3014	17	broker_service	novell.com
43161	3015	6	nati-dstp	natinst.com
43162	3015	17	nati-dstp	natinst.com
43163	3016	6	notify_srvr	novell.com
43164	3016	17	notify_srvr	novell.com
43165	3017	6	event_listener	novell.com
43166	3017	17	event_listener	novell.com
43167	3018	6	srvc_registry	Service Registry novell.com
43168	3018	17	srvc_registry	Service Registry novell.com
43169	3019	6	resource_mgr	Resource Manager novell.com
43170	3019	17	resource_mgr	Resource Manager novell.com
43171	3020	6	cifs	microsoft.com
43172	3020	17	cifs	microsoft.com
43173	3021	6	agriserver	AGRI Server websmile.com
43174	3021	17	agriserver	AGRI Server websmile.com
43175	3022	6	csregagent	csoft.bg
43176	3022	17	csregagent	csoft.bg
43177	3023	6	magicnotes	magicnotes.com
43178	3023	17	magicnotes	magicnotes.com
43179	3024	6	nds_sso	novell.com
43180	3024	17	nds_sso	novell.com
43181	3024	6	wincrash	Wincrash Trojan Horse
43182	3024	17	wincrash	Wincrash Trojan Horse
43183	3025	6	arepa-raft	Arepa Raft ieee.org
43184	3025	17	arepa-raft	Arepa Raft ieee.org
43185	3026	6	agri-gateway	AGRI Gateway agri-datalog.com
43186	3026	17	agri-gateway	AGRI Gateway agri-datalog.com
43187	3027	6	LiebDevMgmt_C	Liebert.com
43188	3027	17	LiebDevMgmt_C	Liebert.com
43189	3028	6	LiebDevMgmt_DM	Liebert.com
43190	3028	17	LiebDevMgmt_DM	Liebert.com
43191	3029	6	LiebDevMgmt_A	Liebert.com
43192	3029	17	LiebDevMgmt_A	Liebert.com
43193	3030	6	arepa-cas	arepa.com
43194	3030	17	arepa-cas	arepa.com
43195	3031	6	agentvu	AgentVU apple.com
43196	3031	17	agentvu	AgentVU apple.com
43197	3032	6	redwood-chat	daou.co.kr
43198	3032	17	redwood-chat	daou.co.kr
43199	3033	6	pdb	pixstream.com
43200	3033	17	pdb	pixstream.com
43201	3034	6	osmosis-aeea	interaccess.com
43202	3034	17	osmosis-aeea	interaccess.com
43203	3035	6	fjsv-gssagt	ael.fujitsu.co.jp
43204	3035	17	fjsv-gssagt	ael.fujitsu.co.jp
43205	3036	6	hagel-dump	hageltech.com
43206	3036	17	hagel-dump	hageltech.com
43207	3037	6	hp-san-mgmt	HP SAN Mgmt hp.com
43208	3037	17	hp-san-mgmt	HP SAN Mgmt hp.com
43209	3038	6	santek-ups	Santek UPS sc.stk.com.cn
43210	3038	17	santek-ups	Santek UPS sc.stk.com.cn
43211	3039	6	cogitate	Cogitate Inc infowest.com
43212	3039	17	cogitate	Cogitate Inc infowest.com
43213	3040	6	tomato-springs	tomatosprings.com
43214	3040	17	tomato-springs	tomatosprings.com
43215	3041	6	di-traceware	digisle.net
43216	3041	17	di-traceware	digisle.net
43217	3042	6	journee	journee.com
43218	3042	17	journee	journee.com
43219	3043	6	brp	hns.com
43220	3043	17	brp	hns.com
43221	3045	6	responsenet	reponsenetworks.com
43222	3045	17	responsenet	reponsenetworks.com
43223	3046	6	di-ase	digisle.net
43224	3046	17	di-ase	digisle.net
43225	3047	6	hlserver	Fast Security HL Server fast-ag.de
43226	3047	17	hlserver	Fast Security HL Server fast-ag.de
43227	3048	6	pctrader	Sierra Net PC Trader sierra.net
43228	3048	17	pctrader	Sierra Net PC Trader sierra.net
43229	3049	6	nsws	psilink.com
43230	3049	17	nsws	psilink.com
43231	3049	6	cfs	Unassigned, cryptographic file system (nfs)
43232	3049	17	cfs	Unassigned, cryptographic file system (nfs)
43233	3050	6	gds_db	interbase.com
43234	3050	17	gds_db	interbase.com
43235	3051	6	galaxy-server	gts-tkts.com
43236	3051	17	galaxy-server	gts-tkts.com
43237	3052	6	apcpcns	apcc.com
43238	3052	17	apcpcns	apcc.com
43239	3053	6	dsom-server	pnl.gov
43240	3053	17	dsom-server	pnl.gov
43241	3054	6	amt-cnf-prot	interbusiness.it
43242	3054	17	amt-cnf-prot	interbusiness.it
43243	3055	6	policyserver	sonusnet.com
43244	3055	17	policyserver	sonusnet.com
43245	3056	6	cdl-server	engineer.com
43246	3056	17	cdl-server	engineer.com
43247	3057	6	goahead-fldup	goahead.com
43248	3057	17	goahead-fldup	goahead.com
43249	3058	6	videobeans	eng.sun.com
43250	3058	17	videobeans	eng.sun.com
43251	3059	6	qsoft	earlhaig.com
43252	3059	17	qsoft	earlhaig.com
43253	3060	6	interserver	interbase.com
43254	3060	17	interserver	interbase.com
43255	3061	6	cautcpd	cai.com
43256	3061	17	cautcpd	cai.com
43257	3062	6	ncacn-ip-tcp	cai.com
43258	3062	17	ncacn-ip-tcp	cai.com
43259	3063	6	ncadg-ip-udp	cai.com
43260	3063	17	ncadg-ip-udp	cai.com
43261	3065	6	slinterbase	interbase.com
43262	3065	17	slinterbase	interbase.com
43263	3066	6	netattachsdmp	natattach.com
43264	3066	17	netattachsdmp	natattach.com
43265	3067	6	fjhpjp	np.lps.cs.fujitsu.co.jp
43266	3067	17	fjhpjp	np.lps.cs.fujitsu.co.jp
43267	3068	6	ls3bcast	ls3 Broadcast powerware.com
43268	3068	17	ls3bcast	ls3 Broadcast powerware.com
43269	3069	6	ls3	powerware.com
43270	3069	17	ls3	powerware.com
43271	3070	6	mgxswitch	metagenix.com
43272	3070	17	mgxswitch	metagenix.com
43273	3075	6	orbix-locator	Orbix 2000 locator iona.com
43274	3075	17	orbix-locator	Orbix 2000 locator iona.com
43275	3076	6	orbix-config	Orbix 2000 Config iona.com
43276	3076	17	orbix-config	Orbix 2000 Config iona.com
43277	3077	6	orbix-loc-ssl	Orbix 2000 Locator SSL iona.com
43278	3077	17	orbix-loc-ssl	Orbix 2000 Locator SSL iona.com
43279	3078	6	orbix-cfg-ssl	Orbix 2000 Locator SSL iona.com
43280	3078	17	orbix-cfg-ssl	Orbix 2000 Locator SSL iona.com
43281	3079	6	lv-frontpanel	LV Front Panel ni.com
43282	3079	17	lv-frontpanel	LV Front Panel ni.com
43283	3080	6	stm_pproc	server.stmi.com
43284	3080	17	stm_pproc	server.stmi.com
43285	3081	6	tl1-lv	TL1-LV SONET Internetworking Forum (SIF) lucent.com
43286	3081	17	tl1-lv	TL1-LV SONET Internetworking Forum (SIF) lucent.com
43287	3082	6	tl1-raw	TL1-RAW SONET Internetworking Forum (SIF) lucent.com
43288	3082	17	tl1-raw	TL1-RAW SONET Internetworking Forum (SIF) lucent.com
43289	3083	6	tl1-telnet	TL1-TELNET SONET Internetworking Forum (SIF) lucent.com
43290	3083	17	tl1-telnet	TL1-TELNET SONET Internetworking Forum (SIF) lucent.com
43291	3084	6	itm-mccs	ITM-MCCS itmaster.com
43292	3084	17	itm-mccs	ITM-MCCS itmaster.com
43293	3085	6	pcihreq	PCIHreq p.sanders@dial.pipex.com
43294	3085	17	pcihreq	PCIHreq p.sanders@dial.pipex.com
43295	3086	6	jdl-dbkitchen	alles.or.jp
43296	3086	17	jdl-dbkitchen	alles.or.jp
43297	3086	6	sj3	SJ3 (Kanji input)
43298	3105	6	cardbox	cardbox.co.uk
43299	3105	17	cardbox	cardbox.co.uk
43300	3106	6	cardbox-http	cardbox.co.uk
43301	3106	17	cardbox-http	cardbox.co.uk
43302	3128	6	squid-http	Squid is a caching proxy server
43303	3130	6	icpv2	ICPv2 nlanr.net
43304	3130	17	icpv2	ICPv2 nlanr.net
43305	3130	17	squid-ipc	(UDP) Internet Cache Protocol (ICP)
43306	3131	6	netbookmark	Net Book Mark haifa.vnet.ibm.com
43307	3131	17	netbookmark	Net Book Mark haifa.vnet.ibm.com
43308	3141	6	vmodem	psilink.com
43309	3141	17	vmodem	psilink.com
43310	3142	6	rdc-wh-eos	ncc.co.il
43311	3142	17	rdc-wh-eos	ncc.co.il
43312	3143	6	seaview	Sea View notes.seagate.com
43313	3143	17	seaview	Sea View notes.seagate.com
43314	3144	6	tarantella	sco.com
43315	3144	17	tarantella	sco.com
43316	3145	6	csi-lfap	CSI-LFAP @.ctron.com
43317	3145	17	csi-lfap	CSI-LFAP @.ctron.com
43318	3146	6	#	Unassigned
43319	3146	17	#	Unassigned
43320	3147	6	rfio	@cern.ch
43321	3147	17	rfio	@cern.ch
43322	3148	6	nm-game-admin	NetMike Game Administrator visionplus.co.nz
43323	3148	17	nm-game-admin	NetMike Game Administrator visionplus.co.nz
43324	3148	17	bozo	Bozo Trojan Horse
43325	3149	6	nm-game-server	NetMike Game Server visionplus.co.nz
43326	3149	17	nm-game-server	NetMike Game Server visionplus.co.nz
43327	3150	6	nm-access-admin	NetMike Assessor Administrator visionplus.co.nz
43328	3150	17	nm-access-admin	NetMike Assessor Administrator visionplus.co.nz
43329	3150	6	deep	Deep Troat or Invasro Trojan Hores
43330	3150	17	deep	Deep Troat or Invasro Trojan Hores
43331	3151	6	nm-assessor	NetMike Assessor visionplus.co.nz
43332	3151	17	nm-assessor	NetMike Assessor visionplus.co.nz
43333	3152	6	feitianrockery	FeriTian Port, Huang Yu
43334	3152	17	feitianrockery	FeriTian Port, Huang Yu
43335	3153	6	s8-client-port	S8Cargo Client Port, Jon S. Kyle
43336	3153	17	s8-client-port	S8Cargo Client Port, Jon S. Kyle
43337	3154	6	ccmrmi	ON RMI Registry
43338	3154	17	ccmrmi	ON RMI Registry
43339	3155	6	jpegmpeg	JpegMpeg, Richard Bassous
43340	3155	17	jpegmpeg	JpegMpeg, Richard Bassous
43341	3156	6	indura	Indura Collector, Don Schoenecker
43342	3156	17	indura	Indura Collector, Don Schoenecker
43343	3157	6	e3consultants	CCC Listner Port, Brian Carnell
43344	3157	17	e3consultants	CCC Listner Port, Brian Carnell
43345	3158	6	stvp	SmashTV Protocol, Christan Wolff
43346	3158	17	stvp	SmashTV Protocol, Christan Wolff
43347	3159	6	navegaweb-port	NavegaWeb Tarification, Migel Angel Fernandez
43348	3159	17	navegaweb-port	NavegaWeb Tarification, Migel Angel Fernandez
43349	3160	6	tip-app-server	TOP Application Server, Olivier Mascia
43350	3160	17	tip-app-server	TOP Application Server, Olivier Mascia
43351	3161	6	doc11m	DOC1 License Manager, Greg Goodson
43352	3161	17	doc11m	DOC1 License Manager, Greg Goodson
43353	3162	6	sf1m	SFLM, Keith Turner
43354	3162	17	sf1m	SFLM, Keith Turner
43355	3163	6	res-sap	RES-SAP, Bob Janssen
43356	3163	17	res-sap	RES-SAP, Bob Janssen
43357	3164	6	imprs	IMPRS, Lars Bohn
43358	3164	17	imprs	IMPRS, Lars Bohn
43359	3165	6	newgenpay	Newgenpay Engine Service, Ilan Zisser
43360	3165	17	newgenpay	Newgenpay Engine Service, Ilan Zisser
43361	3166	6	grepos	Quest Repository, Fred Surr
43362	3166	17	grepos	Quest Repository, Fred Surr
43363	3167	6	poweroncontact	poweroncontact
43364	3167	17	poweroncontact	poweroncontact
43365	3168	6	poweronnud	poweronnud, Paul Cone
43366	3168	17	poweronnud	poweronnud, Paul Cone
43367	3169	6	serverview-as	Serverview-AS
43368	3169	17	serverview-as	Serverview-AS
43369	3170	6	serverview-asn	Serverview-ASN
43370	3170	17	serverview-asn	Serverview-ASN
43371	3171	6	serverview-gf	Serverview-GF
43372	3171	17	serverview-gf	Serverview-GF
43373	3172	6	serverview-rm	Serverview-RM
43374	3172	17	serverview-rm	Serverview-RM
43375	3173	6	serverview-icc	Serverview-ICC, Guenther Kroenert
43376	3173	17	serverview-icc	Serverview-ICC, Guenther Kroenert
43377	3174	6	armi-server	ARMI Server, Bobby Martin
43378	3174	17	armi-server	ARMI Server, Bobby Martin
43379	3175	6	t1-e1-over-ip	T1_E1_Over_IP, Mark Doyle
43380	3175	17	t1-e1-over-ip	T1_E1_Over_IP, Mark Doyle
43381	3176	6	ars-master	ARS Master, Ade Adebayo
43382	3176	17	ars-master	ARS Master, Ade Adebayo
43383	3177	6	phonex-port	Phonex Protocol, Doug Grover
43384	3177	17	phonex-port	Phonex Protocol, Doug Grover
43385	3178	6	radclientport	Radiance UltraEdge Port, Sri Subramanium
43386	3178	17	radclientport	Radiance UltraEdge Port, Sri Subramanium
43387	3179	6	h2gf-w-2m	H2GF W.2m Handover Protocol
43388	3179	17	h2gf-w-2m	H2GF W.2m Handover Protocol
43389	3180	6	mc-brk-srv	Millicent Broker Server pa.dec.com
43390	3180	17	mc-brk-srv	Millicent Broker Server pa.dec.com
43391	3181	6	bmcpatrolagent	BMC Patrol Agent bmc.com
43392	3181	17	bmcpatrolagent	BMC Patrol Agent bmc.com
43393	3182	6	bmcpatrolrnvu	BMC Patrol Rendevous bmc.com
43394	3182	17	bmcpatrolrnvu	BMC Patrol Rendevous bmc.com
43395	3183	17	cops-tls	COPS/TLS, Mark Stevens
43396	3184	6	apogeex-port	ApopgeeX Port, Tom Nys
43397	3184	17	apogeex-port	ApopgeeX Port, Tom Nys
43398	3185	6	smpppd	SuSE Meta PPPD, Avin Schnell
43399	3185	17	smpppd	SuSE Meta PPPD, Avin Schnell
43400	3186	6	iiw-port	IIW Monitor User Port, Corey Burnett
43401	3186	17	iiw-port	IIW Monitor User Port, Corey Burnett
43402	3187	6	odi-port	Open Design Listen, Phivos Aristides
43403	3187	17	odi-port	Open Design Listen, Phivos Aristides
43404	3188	6	brcm-comm-port	Broadcom Port, Thomas L. Johnson
43405	3188	17	brcm-comm-port	Broadcom Port, Thomas L. Johnson
43406	3189	6	pcle-infex	Pinnacle Sys InfEx Port, Anthon van der Neut
43407	3189	17	pcle-infex	Pinnacle Sys InfEx Port, Anthon van der Neut
43408	3190	6	csvr-proxy	ConServR Proxy
43409	3190	17	csvr-proxy	ConServR Proxy
43410	3191	6	csvr-sslproxy	ConServR SSL Proxy, Mikhail Kruk
43411	3191	17	csvr-sslproxy	ConServR SSL Proxy, Mikhail Kruk
43412	3192	6	firemonrcc	FireMon Revision Control, Micheal Bishop
43413	3192	17	firemonrcc	FireMon Revision Control, Micheal Bishop
43414	3193	6	cordataport	Cordaxis Data Port, Jay Fesco
43415	3193	17	cordataport	Cordaxis Data Port, Jay Fesco
43416	3194	6	magbind	Rockstorm MAG protocolm Jens Nilsson
43417	3194	17	magbind	Rockstorm MAG protocolm Jens Nilsson
43418	3195	6	ncu-1	Network Control Unit
43419	3195	17	ncu-1	Network Control Unit
43420	3196	6	ncu-2	Network Control Unit, Charlie Hundre
43421	3196	17	ncu-2	Network Control Unit, Charlie Hundre
43422	3197	6	embrace-dp-s	Embrace Device Protocol Server
43423	3197	17	embrace-dp-s	Embrace Device Protocol Server
43424	3198	6	embrace-dp-c	Emnrace Device Protocol Client, Elliot Schwartz
43425	3198	17	embrace-dp-c	Emnrace Device Protocol Client, Elliot Schwartz
43426	3199	6	dmod-workspace	DMOD Workspace, Nick Plante
43427	3199	17	dmod-workspace	DMOD Workspace, Nick Plante
43428	3200	6	tick-port/td>	Press-sense Tick Port, Boris Svetlitsky
43429	3200	17	tick-port/td>	Press-sense Tick Port, Boris Svetlitsky
43430	3201	6	cpq-taskmart	CPQ-TaskSmart, Jackie Lau
43431	3201	17	cpq-taskmart	CPQ-TaskSmart, Jackie Lau
43432	3202	6	intraintra	IntraIntra, Matthew Asham
43433	3202	17	intraintra	IntraIntra, Matthew Asham
43434	3203	6	netwatcher-mon	Network Watcher monitor
43435	3203	17	netwatcher-mon	Network Watcher monitor
43436	3204	6	netwatcher-db	Network Watcher DB Access, Hirokazu Fujisawa
43437	3204	17	netwatcher-db	Network Watcher DB Access, Hirokazu Fujisawa
43438	3205	6	isns	iSNS Server Port, Josh Tseng
43439	3205	17	isns	iSNS Server Port, Josh Tseng
43440	3206	6	ironmail	IronMail POP Proxy, Mike Hudack
43441	3206	17	ironmail	IronMail POP Proxy, Mike Hudack
43442	3207	6	vx-auth-port	Veritas Authenication Port, Senthil Ponnuswamy
43443	3207	17	vx-auth-port	Veritas Authenication Port, Senthil Ponnuswamy
43444	3208	6	pfu-prcallback	PFU PR Callback, Tetsuharu Hanada
43445	3208	17	pfu-prcallback	PFU PR Callback, Tetsuharu Hanada
43446	3209	6	newkpathengine	HP OpenView Network Path Engine Server, Anthony Walker
43447	3209	17	newkpathengine	HP OpenView Network Path Engine Server, Anthony Walker
43448	3210	6	flamenco-proxy	Flamenco Networks Proxy
43449	3210	17	flamenco-proxy	Flamenco Networks Proxy
43450	3211	6	avsecuremgmt	Avocent Secure Management, Brian S. Stewart
43451	3211	17	avsecuremgmt	Avocent Secure Management, Brian S. Stewart
43452	3212	6	surveyinst	Survey Instrument, Al Amet
43453	3212	17	surveyinst	Survey Instrument, Al Amet
43454	3213	6	neon24x7	NEON 24X7 Mission Control
43455	3213	17	neon24x7	NEON 24X7 Mission Control
43456	3214	6	jmq-daemon-1	JMQ Daemon Port 1
43457	3214	17	jmq-daemon-1	JMQ Daemon Port 1
43458	3215	6	jmq-daemon-2	JMQ Daemon Port 2, Martin West
43459	3215	17	jmq-daemon-2	JMQ Daemon Port 2, Martin West
43460	3216	6	ferrari-foam	Ferrari electronic FOAM, Johann Deutinger
43461	3216	17	ferrari-foam	Ferrari electronic FOAM, Johann Deutinger
43462	3217	6	unite	Unified IP & Telecomm Env, Christer Gunnarsson
43463	3217	17	unite	Unified IP & Telecomm Env, Christer Gunnarsson
43464	3218	6	smartpackets	EMC SmartPackets, Steve Spataro
43465	3218	17	smartpackets	EMC SmartPackets, Steve Spataro
43466	3219	6	wms-messenger	WMS Messenger, Michael Monasterio
43467	3219	17	wms-messenger	WMS Messenger, Michael Monasterio
43468	3220	6	xnm-ssl	XML NM over SSL
43469	3220	17	xnm-ssl	XML NM over SSL
43470	3221	6	xnm-clear-text	JXML NM over TCP, Mark Trostler
43471	3221	17	xnm-clear-text	JXML NM over TCP, Mark Trostler
43472	3222	6	glbp	Gateway Load Balancing Pr, Douglas McLaggan
43473	3222	17	glbp	Gateway Load Balancing Pr, Douglas McLaggan
43474	3223	6	digivote	DIGIVOTE (R) Vote Server, Christian Trezoks
43475	3223	17	digivote	DIGIVOTE (R) Vote Server, Christian Trezoks
43476	3224	6	aes-discovery	AES Discovery Port, Ken Richard
43477	3224	17	aes-discovery	AES Discovery Port, Ken Richard
43478	3225	6	fcip-port	FCIP, Murali Rajagopal
43479	3225	17	fcip-port	FCIP, Murali Rajagopal
43480	3226	6	isi-irp	ISI industry Software IRP, Peter Sandstrom
43481	3226	17	isi-irp	ISI industry Software IRP, Peter Sandstrom
43482	3227	6	dwnmshttp	DiamondWave NMS Server
43483	3227	17	dwnmshttp	DiamondWave NMS Server
43484	3228	6	dwmsgserver	DiamondWave MSG Server, Varma Bhupatiraju
43485	3228	17	dwmsgserver	DiamondWave MSG Server, Varma Bhupatiraju
43486	3229	6	global-cd-port	Global CD Port, Vitaly Revsin
43487	3229	17	global-cd-port	Global CD Port, Vitaly Revsin
43488	3230	6	sftdst-port	Software Distribution Port, Andrea Lanza
43489	3230	17	sftdst-port	Software Distribution Port, Andrea Lanza
43490	3231	6	dsnl	Delta Solutions Direct, Peter Ijkhout
43491	3231	17	dsnl	Delta Solutions Direct, Peter Ijkhout
43492	3232	6	mdtp	MDT Port, IJsbrand Wijnands
43493	3232	17	mdtp	MDT Port, IJsbrand Wijnands
43494	3233	6	whisker	WhiskerControl main port, Rudolf Cardinal 02-2002
43495	3233	17	whisker	WhiskerControl main port, Rudolf Cardinal 02-2002
43496	3234	6	alchemy	Alchemy Server. Mikhail Belov 02-2002
43497	3234	17	alchemy	Alchemy Server. Mikhail Belov 02-2002
43498	3235	6	mdap-port	MDAP prot, Johan Deleu 02-2002
43499	3235	17	mdap-port	MDAP prot, Johan Deleu 02-2002
43500	3236	6	apparent-ts	appareNet Test Server
43501	3236	17	apparent-ts	appareNet Test Server
43502	3237	6	apparent-tps	appareNet Test Packet Sequencer
43503	3237	17	apparent-tps	appareNet Test Packet Sequencer
43504	3238	6	apparent-as	appareNet Analysis Server
43505	3238	17	apparent-as	appareNet Analysis Server
43506	3239	6	apparent-ui	appareNet User Interface, Fred Klassen 02-2002
43507	3239	17	apparent-ui	appareNet User Interface, Fred Klassen 02-2002
43508	3240	6	triomotion	Trio Motion Control Port, Tony Matthews 02-2002
43509	3240	17	triomotion	Trio Motion Control Port, Tony Matthews 02-2002
43510	3241	6	sysorb/td>	SysOrb Monitoring Server, Jakob Oestergaard 02-2002
43511	3241	17	sysorb/td>	SysOrb Monitoring Server, Jakob Oestergaard 02-2002
45171	61466	0	telecom	Telecommando Trojan
43512	3242	6	sdp-id-port	Session Description ID, Greg Rose 02-2002
43513	3242	17	sdp-id-port	Session Description ID, Greg Rose 02-2002
43514	3243	6	timelot	Timelot Port, David Ferguson 02-2002
43515	3243	17	timelot	Timelot Port, David Ferguson 02-2002
43516	3244	6	onesaf	OneSAF, Gene McCulley 02-2002
43517	3244	17	onesaf	OneSAF, Gene McCulley 02-2002
43518	3245	6	vieo-fe	VIEO Fabric Executive, James Cox 02-2002
43519	3245	17	vieo-fe	VIEO Fabric Executive, James Cox 02-2002
43520	3246	6	dvt-system	DVT System Port
43521	3246	17	dvt-system	DVT System Port
43522	3247	6	dvt-data	DVT Data Link, Phillip Heil, 02-2002
43523	3247	17	dvt-data	DVT Data Link, Phillip Heil, 02-2002
43524	3248	6	procos-lm	Procos LM, Torsten Rendelmann 02-2002
43525	3248	17	procos-lm	Procos LM, Torsten Rendelmann 02-2002
43526	3249	6	ssp	Sate Sync Protocol, Stephane Beaulieu 02-2002
43527	3249	17	ssp	Sate Sync Protocol, Stephane Beaulieu 02-2002
43528	3250	6	hicp	HMS hicp port, HMS industrial Networks AB 02-2002
43529	3250	17	hicp	HMS hicp port, HMS industrial Networks AB 02-2002
43530	3251	6	sysscanner	Sys Scanner, Dick Georges 02-2002
43531	3251	17	sysscanner	Sys Scanner, Dick Georges 02-2002
43532	3252	6	dhe	DHE port, Fabrizio Massimo Ferrara 02-2002
43533	3252	17	dhe	DHE port, Fabrizio Massimo Ferrara 02-2002
43534	3253	6	pda-data	PDA Data
43535	3253	17	pda-data	PDA Data
43536	3254	6	pda-sys	PDA System, Jian Fan 02-2002
43537	3254	17	pda-sys	PDA System, Jian Fan 02-2002
43538	3255	6	semaphore	Semaphore Connection, Jay Eckles 02-20002
43539	3255	17	semaphore	Semaphore Connection, Jay Eckles 02-20002
43540	3256	6	cpqrpm-agent	Compaq RPM Agent Port
43541	3256	17	cpqrpm-agent	Compaq RPM Agent Port
43542	3257	6	cpqrpm-server	Compaq RPM Server Port, Royal King 02-2002
43543	3257	17	cpqrpm-server	Compaq RPM Server Port, Royal King 02-2002
43544	3258	6	ivecon-port	Ivecon Server Port, Serguei Tevs 02-2002
43545	3258	17	ivecon-port	Ivecon Server Port, Serguei Tevs 02-2002
43546	3259	6	epncdp2	Epson Network Common Devi, SEIKO EPSON Corp 02-2002
43547	3259	17	epncdp2	Epson Network Common Devi, SEIKO EPSON Corp 02-2002
43548	3260	6	isci-target	iSCSI port, Julian Satran
43549	3260	17	isci-target	iSCSI port, Julian Satran
43550	3261	6	winshadow	winShadow, Colin Barry
43551	3261	17	winshadow	winShadow, Colin Barry
43552	3262	6	necp	isi.edu
43553	3262	17	necp	isi.edu
43554	3263	6	ecolor-imager	E-Color Ebterprise Imager, Tamara Baker
43555	3263	17	ecolor-imager	E-Color Ebterprise Imager, Tamara Baker
43556	3264	6	ccmail	CC:mail/Lotus
43557	3264	17	ccmail	CC:mail/Lotus
43558	3265	6	altav-tunnel	digital.com
43559	3265	17	altav-tunnel	digital.com
43560	3266	6	ns-cfg-server	netsoft.com
43561	3266	17	ns-cfg-server	netsoft.com
43562	3267	6	ibm-dial-out	vnet.ibm.com
43563	3267	17	ibm-dial-out	vnet.ibm.com
43564	3268	6	msft-gc	Microsoft Global Catalog @.microsoft.com
43565	3268	17	msft-gc	Microsoft Global Catalog @.microsoft.com
43566	3269	6	msft-gc-ssl	Microsoft Global Catalog with LDAP/SSL @.microsoft.com
43567	3269	17	msft-gc-ssl	Microsoft Global Catalog with LDAP/SSL @.microsoft.com
43568	3270	6	verismart	vfi.com
43569	3270	17	verismart	vfi.com
43570	3271	6	csoft-prev	CSoft Prev Port iname.com
43571	3271	17	csoft-prev	CSoft Prev Port iname.com
43572	3272	6	user-manager	Fijitsu User Manager ael.fujitsu.co.jp
43573	3272	17	user-manager	Fijitsu User Manager ael.fujitsu.co.jp
43574	3273	6	sxmp	Simple Extensible Multiplexed Protocol webdash.com
43575	3273	17	sxmp	Simple Extensible Multiplexed Protocol webdash.com
43576	3274	6	ordinox-server	Ordinox Server prdinox.com
43577	3274	17	ordinox-server	Ordinox Server prdinox.com
43578	3275	6	samd	fc.hp.com
43579	3275	17	samd	fc.hp.com
43580	3276	6	maxim-asics	Maxim ASICs mxim.com
43581	3276	17	maxim-asics	Maxim ASICs mxim.com
43582	3277	6	awg-proxy	AWG Proxy anhp.com
43583	3277	17	awg-proxy	AWG Proxy anhp.com
43584	3278	6	lkcmserver	LKCM Server
43585	3278	17	lkcmserver	LKCM Server
43586	3279	6	admind	chistech.com
43587	3279	17	admind	chistech.com
43588	3280	6	vs-server	godlew.com
43589	3280	17	vs-server	godlew.com
43590	3281	6	sysopt	unx.dec.com
43591	3281	17	sysopt	unx.dec.com
43592	3282	6	datusorb	datus-usa.com
43593	3282	17	datusorb	datus-usa.com
43594	3283	6	net-assistant	apple.com
43595	3283	17	net-assistant	apple.com
43596	3284	6	4talk	four-sight.co.uk
43597	3284	17	4talk	four-sight.co.uk
43598	3285	6	plato	tro.com
43599	3285	17	plato	tro.com
43600	3286	6	e-net	austin.eent.com
43601	3286	17	e-net	austin.eent.com
43602	3287	6	directvdata	worldnet.att.net
43603	3287	17	directvdata	worldnet.att.net
43604	3288	6	cops	iphighway.com
43605	3288	17	cops	iphighway.com
43606	3289	6	enpc	exc.epson.co.jp
43607	3289	17	enpc	exc.epson.co.jp
43608	3290	6	caps-lm	Caps logistics Toolkit-LM caps.com
43609	3290	17	caps-lm	Caps logistics Toolkit-LM caps.com
43610	3291	6	sah-lm	S A Holditch & Associates-LM nmail.holditch.com
43611	3291	17	sah-lm	S A Holditch & Associates-LM nmail.holditch.com
43612	3292	6	cart-o-rama	Cart O Rama saelabs.com
43613	3292	17	cart-o-rama	Cart O Rama saelabs.com
43614	3293	6	fg-fps	freegate.net
43615	3293	17	fg-fps	freegate.net
43616	3294	6	fg-gip	freegate.net
43617	3294	17	fg-gip	freegate.net
43618	3295	6	dyniplookup	Dynamic IP Lookup
43619	3295	17	dyniplookup	Dynamic IP Lookup
43620	3296	6	rib-slm	Rib License Manager rib.de
43621	3296	17	rib-slm	Rib License Manager rib.de
43622	3297	6	cytel-lm	Cytel license Manager cytel.com
43623	3297	17	cytel-lm	Cytel license Manager cytel.com
43624	3298	6	transview	mch.sni.de
43625	3298	17	transview	mch.sni.de
43626	3299	6	pdrncs	vnd.tek.com
43627	3299	17	pdrncs	vnd.tek.com
43628	3302	6	mcs-fastmail	mcsdallas.com
43629	3302	17	mcs-fastmail	mcsdallas.com
43630	3303	6	opsession-clnt	netmanage.co.il
43631	3303	17	opsession-clnt	netmanage.co.il
43632	3304	6	opession-srvr	netmanage.co.il
43633	3304	17	opession-srvr	netmanage.co.il
43634	3305	6	odetto-ftp	ford.com
43635	3305	17	odetto-ftp	ford.com
43636	3306	6	mysql	MySQL analytikerna.se
43637	3306	17	mysql	MySQL analytikerna.se
43638	3307	6	opessession-prxy	OP Session Proxy netmanage.co.il
43639	3307	17	opessession-prxy	OP Session Proxy netmanage.co.il
43640	3308	6	tns-server	taec.enet.dec.com
43641	3308	17	tns-server	taec.enet.dec.com
43642	3309	6	tns-adv	taec.enet.dec.com
43643	3309	17	tns-adv	taec.enet.dec.com
43644	3310	6	dyna-access	cornerstonesoftware.com
43645	3310	17	dyna-access	cornerstonesoftware.com
43646	3311	6	mcns-tel-ret	home.net
43647	3311	17	mcns-tel-ret	home.net
43648	3312	6	appman-server	Application Management Server unify.com
43649	3312	17	appman-server	Application Management Server unify.com
43650	3313	6	uorb	Unify Object Broker unify.com
43651	3313	17	uorb	Unify Object Broker unify.com
43652	3314	6	uohost	Unify Object Host unify.com
43653	3314	17	uohost	Unify Object Host unify.com
43654	3315	6	cdid	chat.ru
43655	3315	17	cdid	chat.ru
43656	3316	6	aicc-cmi	atc.boeing.com
43657	3316	17	aicc-cmi	atc.boeing.com
43658	3317	6	vsaiport	isl.mei.co.jp
43659	3317	17	vsaiport	isl.mei.co.jp
43660	3318	6	ssrip	Switch to Switch routing protocol flare.nd.net.fujitsu.co.jp
43661	3318	17	ssrip	Switch to Switch routing protocol flare.nd.net.fujitsu.co.jp
43662	3319	6	sdt-lmd	SDT License Manager @tin.it
43663	3319	17	sdt-lmd	SDT License Manager @tin.it
43664	3320	6	officelink2000	teltone.com
43665	3320	17	officelink2000	teltone.com
43666	3321	6	vnsstr	isl.mei.co.jp
43667	3321	17	vnsstr	isl.mei.co.jp
43668	3326	6	sftu	spacenet.com.br
43669	3326	17	sftu	spacenet.com.br
43670	3327	6	bbars	outlx.bandl.com
43671	3327	17	bbars	outlx.bandl.com
43672	3328	6	egptlm	Eaglepoint License Manager eaglepoint.com
43673	3328	17	egptlm	Eaglepoint License Manager eaglepoint.com
43674	3329	6	hp-device-disc	HP Device Disc hp.com
43675	3329	17	hp-device-disc	HP Device Disc hp.com
43676	3330	6	mcs-calypsoicf	MCS Calypso ICF mcsdallas.com
43677	3330	17	mcs-calypsoicf	MCS Calypso ICF mcsdallas.com
43678	3331	6	mcs-messaging	MCS Messaging mcsdallas.com
43679	3331	17	mcs-messaging	MCS Messaging mcsdallas.com
43680	3332	6	mcs-mailsvr	MCS Mail Server mcsdallas.com
43681	3332	17	mcs-mailsvr	MCS Mail Server mcsdallas.com
43682	3333	6	dec-notes	DEC Notes via.enet.dec.com
43683	3333	17	dec-notes	DEC Notes via.enet.dec.com
43684	3334	6	directv-web	Direct TV Webcasting worldnet.att.net
43685	3334	17	directv-web	Direct TV Webcasting worldnet.att.net
43686	3335	6	directv-soft	Direct TV Software Updates worldnet.att.net
43687	3335	17	directv-soft	Direct TV Software Updates worldnet.att.net
43688	3336	6	directv-tick	Direct TV Tickers worldnet.att.net
43689	3336	17	directv-tick	Direct TV Tickers worldnet.att.net
43690	3337	6	directv-catlg	Direct TV Data Catalog worldnet.att.net
43691	3337	17	directv-catlg	Direct TV Data Catalog worldnet.att.net
43692	3338	6	anet-b	OMF data b sw.seisy.abb.se
43693	3338	17	anet-b	OMF data b sw.seisy.abb.se
43694	3339	6	anet-l	OMF data L sw.seisy.abb.se
43695	3339	17	anet-l	OMF data L sw.seisy.abb.se
43696	3340	6	anet-m	OMF data m sw.seisy.abb.se
43697	3340	17	anet-m	OMF data m sw.seisy.abb.se
43698	3341	6	anet-h	OMF data 4 sw.seisy.abb.se
43699	3341	17	anet-h	OMF data 4 sw.seisy.abb.se
43700	3342	6	webtie	WebTIE ngdc.noaa.gov
43701	3342	17	webtie	WebTIE ngdc.noaa.gov
43702	3343	6	ms-cluster-net	MS Cluster Net microsoft.com
43703	3343	17	ms-cluster-net	MS Cluster Net microsoft.com
43704	3344	6	bnt-manager	bhead.co.uk
43705	3344	17	bnt-manager	bhead.co.uk
43706	3345	6	influence	topia.com
43707	3345	17	influence	topia.com
43708	3346	6	trnsprntproxy	ccm.al.intel.com
43709	3346	17	trnsprntproxy	ccm.al.intel.com
43710	3347	6	phoenix-rpc	phoenix.com
43711	3347	17	phoenix-rpc	phoenix.com
43712	3348	6	pangolin-laser	msn.com
43713	3348	17	pangolin-laser	msn.com
43714	3349	6	chevinservices	chevin.com
43715	3349	17	chevinservices	chevin.com
43716	3350	6	findviatv	8x8.com
43717	3350	17	findviatv	8x8.com
43718	3351	6	btrieve	pervasive-sw.com
43719	3351	17	btrieve	pervasive-sw.com
43720	3352	6	ssql	pervasive-sw.com
43721	3352	17	ssql	pervasive-sw.com
43722	3353	6	fatpipe	ragula.com
43723	3353	17	fatpipe	ragula.com
43724	3354	6	suitjd	unx.dec.com
43725	3354	17	suitjd	unx.dec.com
43726	3355	6	ordinox-dbase	ordinox.com
43727	3355	17	ordinox-dbase	ordinox.com
43728	3356	6	upnotifyps	uplanet.com
43729	3356	17	upnotifyps	uplanet.com
43730	3357	6	adtech-test	Adtech Test IP adtech-inc.com
43731	3357	17	adtech-test	Adtech Test IP adtech-inc.com
43732	3358	6	mpsysrmsvr	Mp Sys Rmsvr ael.fujitsu.co.jp
43733	3358	17	mpsysrmsvr	Mp Sys Rmsvr ael.fujitsu.co.jp
43734	3359	6	wg-netforce	WG NetForce wg.com
43735	3359	17	wg-netforce	WG NetForce wg.com
43736	3360	6	kv-server	cipartners.com
43737	3360	17	kv-server	cipartners.com
43738	3361	6	Kv-agent	cipartners.com
43739	3361	17	Kv-agent	cipartners.com
43740	3362	6	dj-ilm	DJ ILM
43741	3362	17	dj-ilm	DJ ILM
43742	3363	6	neti-vi-server	natinst.com
43743	3363	17	neti-vi-server	natinst.com
43744	3364	6	creativeserver	notes.emotion.com
43745	3364	17	creativeserver	notes.emotion.com
43746	3365	6	contentserver	notes.emotion.com
43747	3365	17	contentserver	notes.emotion.com
43748	3366	6	creativepartnr	notes.emotion.com
43749	3366	17	creativepartnr	notes.emotion.com
43750	3372	6	tip2	loc252.tandem.com
43751	3372	17	tip2	loc252.tandem.com
43752	3373	6	lavenir-lm	lavenir.com
43753	3373	17	lavenir-lm	lavenir.com
43754	3374	6	cluster-disc	columbiasc.ncr.com
43755	3374	17	cluster-disc	columbiasc.ncr.com
43756	3375	6	vsmn-agent	vitalsigns.com
43757	3375	17	vsmn-agent	vitalsigns.com
43758	3376	6	cdborker	CD Broker esps.com
43759	3376	17	cdborker	CD Broker esps.com
43760	3377	6	cogsys-lm	Cogsys Network license Manager cogsys.co.uk
43761	3377	17	cogsys-lm	Cogsys Network license Manager cogsys.co.uk
43762	3378	6	wsicopy	WSICOPY
43763	3378	17	wsicopy	WSICOPY
43764	3379	6	socorfs	SOCORFS
43765	3379	17	socorfs	SOCORFS
43766	3380	6	sns-channels	firstfloor.com
43767	3380	17	sns-channels	firstfloor.com
43768	3381	6	geneous	histech.com
43769	3381	17	geneous	histech.com
43770	3382	6	fujitsu-neat	Fujitsu Network Enhanced Antitheft function team.icl.se
43771	3382	17	fujitsu-neat	Fujitsu Network Enhanced Antitheft function team.icl.se
43772	3383	6	esp-lm	entsoft.com
43773	3383	17	esp-lm	entsoft.com
43774	3384	6	hp-clic	cup.hp.com
43775	3384	17	hp-clic	cup.hp.com
43776	3385	6	qnxnetman	qnx.com
43777	3385	17	qnxnetman	qnx.com
43778	3386	6	gprs-data	etsi.fr
43779	3386	17	gprs-data	etsi.fr
43780	3387	6	backroomnet	carreker.com
43781	3387	17	backroomnet	carreker.com
43782	3388	6	cbserver	arborsoft.com
43783	3388	17	cbserver	arborsoft.com
43784	3389	6	ms-wbt-server	Remote Display protocol microsoft.com
43785	3389	17	ms-wbt-server	Remote Display protocol microsoft.com
43786	3390	6	dsc	Distributed Service Coordinator secant.com
43787	3390	17	dsc	Distributed Service Coordinator secant.com
43788	3391	6	savant	theprogammers.com
43789	3391	17	savant	theprogammers.com
43790	3392	6	efi-lm	execpc.com
43791	3392	17	efi-lm	execpc.com
43792	3393	6	d2k-tapestry1	D2K Tapestry Client to Server d2k.com
43793	3393	17	d2k-tapestry1	D2K Tapestry Client to Server d2k.com
43794	3394	6	d2k-tapestry2	D2k Tapestry Server to Server d2k.com
43795	3394	17	d2k-tapestry2	D2k Tapestry Server to Server d2k.com
43796	3395	6	dyna-lm	dyna.com
43797	3395	17	dyna-lm	dyna.com
43798	3396	6	printer_agent	novell.com
43799	3396	17	printer_agent	novell.com
43800	3397	6	cloanto-lm	cloanto.com
43801	3397	17	cloanto-lm	cloanto.com
43802	3398	6	mercantile	inet.uni2.dk
43803	3398	17	mercantile	inet.uni2.dk
43804	3399	6	csms	cedros.com
43805	3399	17	csms	cedros.com
43806	3400	6	csms2	cedros.com
43807	3400	17	csms2	cedros.com
43808	3401	6	filecast	pair.com
43809	3401	17	filecast	pair.com
43810	3421	6	bmap	BULL Apprise portmapper ma30.bull.com
43811	3421	17	bmap	BULL Apprise portmapper ma30.bull.com
43812	3454	6	mira	Apple Remote Access Protocol um.cc.umich.edu
43813	3454	17	mira	Apple Remote Access Protocol um.cc.umich.edu
43814	3455	6	prsvp	RSVP Port isi.edu
43815	3455	17	prsvp	RSVP Port isi.edu
43816	3456	6	vat	VAT default data ee.lbl.gov
43817	3456	17	vat	VAT default data ee.lbl.gov
43818	3457	6	vat-control	VAT default control ee.lbl.gov
43819	3457	17	vat-control	VAT default control ee.lbl.gov
43820	3458	6	d3winosfi	picksys.com
43821	3458	17	d3winosfi	picksys.com
43822	3459	6	integral	TIP Integral tipgroup.com
43823	3459	17	integral	TIP Integral tipgroup.com
43824	3460	6	edm-manager	novadigm.com
43825	3460	17	edm-manager	novadigm.com
43826	3461	6	edm-stager	novadigm.com
43827	3461	17	edm-stager	novadigm.com
43828	3462	6	edm-std-notify	novadigm.com
43829	3462	17	edm-std-notify	novadigm.com
43830	3462	6	track	Unassigned, Software Distribution
43831	3463	6	edm-adm-notify	novadigm.com
43832	3463	17	edm-adm-notify	novadigm.com
43833	3464	6	edm-mgr-sync	novadigm.com
43834	3464	17	edm-mgr-sync	novadigm.com
43835	3465	6	edm-mgr-cntrl	novadigm.com
43836	3465	17	edm-mgr-cntrl	novadigm.com
43837	3466	6	workflow	csesys.co.at
43838	3466	17	workflow	csesys.co.at
43839	3467	6	rcst	remotecontrolsextoys.com
43840	3467	17	rcst	remotecontrolsextoys.com
43841	3468	6	ttcmremotectrl	proxy.co.il
43842	3468	17	ttcmremotectrl	proxy.co.il
43843	3469	6	pluribus	caplet.com
43844	3469	17	pluribus	caplet.com
43845	3470	6	jt400	us.ibm.com
43846	3470	17	jt400	us.ibm.com
43847	3471	6	jt400-ssl	us.ibm.com.com
43848	3471	17	jt400-ssl	us.ibm.com.com
43849	3535	6	ms-la	microsoft.com
43850	3535	17	ms-la	microsoft.com
43851	3521	6	netrek	StarTrek network game netrek.org
43852	3521	17	netrek	StarTrek network game netrek.org
43853	3563	6	watcomdebug	watcom.on.ca
43854	3563	17	watcomdebug	watcom.on.ca
43855	3572	6	harlequinorb	harlequin.co.uk
43856	3572	17	harlequinorb	harlequin.co.uk
43857	3700	6	potaldoom	Portal of Doom Trojan
43858	3700	17	potaldoom	Portal of Doom Trojan
43859	3845	6	v-one-spp	V-ONE Single Port Proxy v-one.com
43860	3845	17	v-one-spp	V-ONE Single Port Proxy v-one.com
43861	3802	6	vhd	intoo.com
43862	3802	17	vhd	intoo.com
43863	3900	6	udt_os	Unidata UDT OS mailhost.unidata.com
43864	3900	17	udt_os	Unidata UDT OS mailhost.unidata.com
43865	3984	6	mapper-nodemgr	MAPPER network node manager unisys.com
43866	3984	17	mapper-nodemgr	MAPPER network node manager unisys.com
43867	3985	6	mapper-mapethd	MAPPER TCP/IP Server unisys.com
43868	3985	17	mapper-mapethd	MAPPER TCP/IP Server unisys.com
43869	3986	6	mapper-ws_ethd	MAPPER Workstation Server unisys.com
43870	3986	17	mapper-ws_ethd	MAPPER Workstation Server unisys.com
43871	3987	6	centerline	centerline.com
43872	3987	17	centerline	centerline.com
43873	4000	17	ICQ	ICQ server icq.com (Unoffically)
43874	4000	6	terabase	terabase.com
43875	4000	17	terabase	terabase.com
43876	4001	6	newoak	NewOak newoak.com
43877	4001	17	newoak	NewOak newoak.com
43878	4002	6	pxc-spvr-ft	cp10.es.xerox.com
43879	4002	17	pxc-spvr-ft	cp10.es.xerox.com
43880	4003	6	pxc-splr-ft	cp10.es.xerox.com
43881	4003	17	pxc-splr-ft	cp10.es.xerox.com
43882	4004	6	pxc-roid	cp10.es.xerox.com
43883	4004	17	pxc-roid	cp10.es.xerox.com
43884	4005	6	pxc-pin	cp10.es.xerox.com
43885	4005	17	pxc-pin	cp10.es.xerox.com
43886	4006	6	pxc-spvr	cp10.es.xerox.com
43887	4006	17	pxc-spvr	cp10.es.xerox.com
43888	4007	6	pxc-splr	cp10.es.xerox.com
43889	4007	17	pxc-splr	cp10.es.xerox.com
43890	4008	6	netcheque	NetCheque accounting isi.edu
43891	4008	17	netcheque	NetCheque accounting isi.edu
43892	4009	6	chimera-hwm	Chimera HEM kleber.ics.uci.edu
43893	4009	17	chimera-hwm	Chimera HEM kleber.ics.uci.edu
43894	4010	6	samsung-unidex	samsung.ru
43895	4010	17	samsung-unidex	samsung.ru
43896	4011	6	altserviceboot	Alernate Service Boot intel.com
43897	4011	17	altserviceboot	Alernate Service Boot intel.com
43898	4012	6	pda-gate	jp.ibm.com
43899	4012	17	pda-gate	jp.ibm.com
43900	4013	6	acl-manager	fulitsu.co.jp
43901	4013	17	acl-manager	fulitsu.co.jp
43902	4014	6	taiclock	koobera.math.uic.edu
43903	4014	17	taiclock	koobera.math.uic.edu
43904	4015	6	talarian-mcast1	talarian.com
43905	4015	17	talarian-mcast1	talarian.com
43906	4016	6	talarian-mcast2	talarian.com
43907	4016	17	talarian-mcast2	talarian.com
43908	4017	6	talarian-mcast3	talarian.com
43909	4017	17	talarian-mcast3	talarian.com
43910	4018	6	talarian-mcast4	talarian.com
43911	4018	17	talarian-mcast4	talarian.com
43912	4019	6	talarian-mcast5	talarian.com
43913	4019	17	talarian-mcast5	talarian.com
43914	4045	6	lockd	NFS lock daemon/manager
43915	4045	17	lockd	NFS lock daemon/manager
43916	4092	6	wincrash	WinCrash Trojan
43917	4092	17	wincrash	WinCrash Trojan
43918	4096	6	bre	Bridge Relay Element timeplex.com
43919	4096	17	bre	Bridge Relay Element timeplex.com
43920	4096	6	wincrash	WinCrash Trojan Horse
43921	4096	17	wincrash	WinCrash Trojan Horse
43922	4097	6	patrolview	bmc.com
43923	4097	17	patrolview	bmc.com
43924	4098	6	drmsfsd	fujitsu.co.jp
43925	4098	17	drmsfsd	fujitsu.co.jp
43926	4099	6	dpcp	clista.demon.co.uk
43927	4099	17	dpcp	clista.demon.co.uk
43928	4132	6	nuts_dem	NUTS daemon
43929	4132	17	nuts_dem	NUTS daemon
43930	4133	6	nuts_bootp	NUTS Bootp Server
43931	4133	17	nuts_bootp	NUTS Bootp Server
43932	4134	6	nifty-hmi	NIFTY-Serve HMI protocol niftyserve.or.jp
43933	4134	17	nifty-hmi	NIFTY-Serve HMI protocol niftyserve.or.jp
43934	4141	6	oirtgsvc	Workflow Server sns.ca
43935	4141	17	oirtgsvc	Workflow Server sns.ca
43936	4142	6	oidocsvc	Document Server sns.ca
43937	4142	17	oidocsvc	Document Server sns.ca
43938	4143	6	oidsr	Documnet Replication sns.ca
43939	4143	17	oidsr	Documnet Replication sns.ca
43940	4144	6	wincim	Compuserve pc windows (unoffically)
43941	4144	17	wincim	Compuserve pc windows (unoffically)
43942	4160	6	jini-discovery	sun.com
43943	4160	17	jini-discovery	sun.com
43944	4199	6	eims-admin	qualcomm.co.nz
43945	4199	17	eims-admin	qualcomm.co.nz
43946	4300	6	corelccam	corelcomputer.com
43947	4300	17	corelccam	corelcomputer.com
43948	4321	6	rwhois	Remote Who Is internic.com
43949	4321	17	rwhois	Remote Who Is internic.com
43950	4333	6	msql	mini-sql server
43951	4343	6	unicall	unidata.comp
43952	4343	17	unicall	unidata.comp
43953	4344	6	vinainstall	vina-tech.com
43954	4344	17	vinainstall	vina-tech.com
43955	4345	6	m4-network-as	macro4.com
43956	4345	17	m4-network-as	macro4.com
43957	4346	6	elanlm	projtech.com
43958	4346	17	elanlm	projtech.com
43959	4347	6	lansurveyor	LAN Surveyor neon.com
43960	4347	17	lansurveyor	LAN Surveyor neon.com
43961	4348	6	itose	hp.com
43962	4348	17	itose	hp.com
43963	4349	6	fsportmap	File System Port Map sarnoff.com
43964	4349	17	fsportmap	File System Port Map sarnoff.com
43965	4350	6	net-device	microsoft.com
43966	4350	17	net-device	microsoft.com
43967	4351	6	plcy-net-svs	PLCY Net Services
43968	4351	17	plcy-net-svs	PLCY Net Services
43969	4353	6	f5-iquery	f5.com
43970	4353	17	f5-iquery	f5.com
43971	4442	6	saris	TeleConsult Gmb t-online.de
43972	4442	17	saris	TeleConsult Gmb t-online.de
43973	4443	6	pharos	AOL Instant Messenging images, TeleConsult Gmb t-online.de
43974	4443	17	pharos	AOL Instant Messenging images, TeleConsult Gmb t-online.de
43975	4444	6	krb524	kerberos 5 to 4 ticket xlator isi.edu
43976	4444	17	krb524	kerberos 5 to 4 ticket xlator isi.edu
43977	4444	6	nv-video	NV video default, use port without assignment parc.xerox.com
43978	4444	17	nv-video	NV video default, use port without assignment parc.xerox.com
43979	4445	6	upnotifyp	uplanet.com
43980	4445	17	upnotifyp	uplanet.com
43981	4446	6	n1-fwp	network-1.com
43982	4446	17	n1-fwp	network-1.com
43983	4447	6	n1-rmgmt	network-1.com
43984	4447	17	n1-rmgmt	network-1.com
43985	4448	6	asc-slmd	ASA license Manager ascinc.com
43986	4448	17	asc-slmd	ASA license Manager ascinc.com
43987	4449	6	privatewire	arx.com
43988	4449	17	privatewire	arx.com
43989	4450	6	camp	controltechnology.com
43990	4450	17	camp	controltechnology.com
43991	4451	6	ctisystemmsg	CTI System Msg controltechnology.com
43992	4451	17	ctisystemmsg	CTI System Msg controltechnology.com
43993	4452	6	ctiprogramload	CTI Program Load controltechnology.com
43994	4452	17	ctiprogramload	CTI Program Load controltechnology.com
43995	4453	6	nssalertmgr	NSS Alert Manager symantec.com
43996	4453	17	nssalertmgr	NSS Alert Manager symantec.com
43997	4454	6	nssagentmgr	NSS Agent Manager symantec.com
43998	4454	17	nssagentmgr	NSS Agent Manager symantec.com
43999	4455	6	prchat-user	PR Chat User us.ibm.net
44000	4455	17	prchat-user	PR Chat User us.ibm.net
44001	4456	6	prchat-server	PR Chat Server us.ibm.net
44002	4456	17	prchat-server	PR Chat Server us.ibm.net
44003	4457	6	prRegister	PR Register us.ibm.net
44004	4457	17	prRegister	PR Register us.ibm.net
44005	4500	6	sae-urn	proper.com
44006	4500	17	sae-urn	proper.com
44007	4501	6	urn-x-cdchoice	proper.com
44008	4501	17	urn-x-cdchoice	proper.com
44009	4545	6	worldscores	optum-inc.com
44010	4545	17	worldscores	optum-inc.com
44011	4546	6	sf-lm	SF License Manager (sentinel) sf.com
44012	4546	17	sf-lm	SF License Manager (sentinel) sf.com
44013	4547	6	lanner-lm	lanner.co.uk
44014	4547	17	lanner-lm	lanner.co.uk
44015	4557	6	fax	FAX transmission service
44016	4559	6	hylafax	HylaFAX client-service protocol
44017	4567	6	filenail	File Nail Trojan Horse
44018	4567	17	filenail	File Nail Trojan Horse
44019	4568	6	bmc-reporting	bmc.com
44020	4590	6	icqtrojan	ICQ Trojan
44021	4600	6	piranha1	primark.com
44022	4601	6	piranha2	primark.com
44023	4672	6	rfa	Remote file access server
44024	4672	17	rfa	Remote file access server
44025	4800	6	iims	Icona Instant Messenging System icona.it
44026	4801	6	iwec	Icona Web Embedded Chat icona.it
44027	4802	6	ilss	Icona License System Server icona.it
44028	4827	6	htcp	Hyper Text Caching Protocol vix.com
44029	4868	6	phrelay	Photon Relay qnx.com
44030	4869	6	phrelaydbg	Photon Relay Debug qnx.com
44031	4885	6	abbs	ark.dyn.ml.org
44032	4983	6	att-intercom	AT&T Intercom reseach.att.com
44033	4950	6	icqtrojen	ICQ Trojen Trojan Horse
44034	5000	6	commplex-main	filmaker.com
44035	5000	17	commplex-main	filmaker.com
44036	5000	6	UPnP	UPnP Universal Plug & Play microsoft.com
44037	5000	17	UPnP	UPnP Universal Plug & Play microsoft.com
44038	5001	6	commplex-link	filmaker.com
44039	5001	17	commplex-link	filmaker.com
44040	5002	6	rfe	Radio Free Ethernet filmaker.com
44041	5002	17	rfe	Radio Free Ethernet filmaker.com
44042	5003	6	fmpro-internal	Filemaker IP filmaker.com
44043	5003	17	fmpro-internal	Filemaker IP filmaker.com
44044	5004	6	avt-profile-1	RTP fokus.gmd.de
44045	5004	17	avt-profile-1	RTP fokus.gmd.de
44046	5005	6	avt-profile-2	RTP fokus.gmd.de
44047	5005	17	avt-profile-2	RTP fokus.gmd.de
44048	5006	6	wsm-server	wrq.com
44049	5006	17	wsm-server	wrq.com
44050	5007	6	wsm-server-ssl	wrq.com
44051	5007	17	wsm-server-ssl	wrq.com
44052	5010	6	telepathstart	vnet.imb.com
44053	5010	17	telepathstart	vnet.imb.com
44054	5010	6	yahmess	Yahoo! Messenger
44055	5010	17	yahmess	Yahoo! Messenger
44056	5011	6	telepathattack	vnet.imb.com
44057	5011	17	telepathattack	vnet.imb.com
44058	5020	6	zenginkyo-1	noa.nttdata.jp
44059	5020	17	zenginkyo-1	noa.nttdata.jp
44060	5021	6	zenginkyo-2	noa.nttdata.jp
44061	5021	17	zenginkyo-2	noa.nttdata.jp
44062	5042	6	asnaacceler8db	asna.com
44063	5042	17	asnaacceler8db	asna.com
44064	5050	6	mmcc	multimedia conference control tool isi.edu
44065	5050	17	mmcc	multimedia conference control tool isi.edu
44066	5051	6	ita-agent	axent.com
44067	5051	17	ita-agent	axent.com
44068	5052	6	ita-manager	axent.com
44069	5052	17	ita-manager	axent.com
44070	5055	6	unot	cmgsolutions.com
44071	5055	17	unot	cmgsolutions.com
44072	5060	6	sip	cs.columbia.edu
44073	5060	17	sip	cs.columbia.edu
44074	5069	6	i-net-2000-npr	I/Net 2000-NPR csicontrols.com
44075	5069	17	i-net-2000-npr	I/Net 2000-NPR csicontrols.com
44076	5071	6	powerschool	powerschool.com
44077	5071	17	powerschool	powerschool.com
44078	5145	6	rmonitor-secure	ascend.com
44079	5145	17	rmonitor-secure	ascend.com
44080	5150	6	atmp	Ascend Tunnel Management Protocol ascend.com
44081	5150	17	atmp	Ascend Tunnel Management Protocol ascend.com
44082	5151	6	esri_sde	esri.com
44083	5151	17	esri_sde	esri.com
44084	5152	6	sde-discovery	esri.com
44085	5152	17	sde-discovery	esri.com
44086	5165	6	ife_icorp	bull.se
44087	5165	17	ife_icorp	bull.se
44088	5190	6	aol	America-Online
44089	5190	17	aol	America-Online
44090	5191	6	aol-1	America-Online1
44091	5191	17	aol-1	America-Online1
44092	5192	6	aol-2	America-Online2
44093	5192	17	aol-2	America-Online2
44094	5193	6	aol-3	America-Online3
44095	5193	17	aol-3	America-Online3
44096	5200	6	targus-aib1	targusinfo.com
44097	5200	17	targus-aib1	targusinfo.com
44098	5201	6	targus-aib2	targusinfo.com
44099	5201	17	targus-aib2	targusinfo.com
44100	5202	6	targus-tnts1	targusinfo.com
44101	5202	17	targus-tnts1	targusinfo.com
44102	5203	6	targus-tnts2	targusinfo.com
44103	5203	17	targus-tnts2	targusinfo.com
44104	5232	6	sgi-dgl	SGI Distribution Graphics
44105	5236	6	padl2sim	nbsp;
44106	5236	17	padl2sim	nbsp;
44107	5272	6	pk	eba.net
44108	5272	17	pk	eba.net
44109	5300	6	hacl-hb	HA cluster heartbeat hp.com
44110	5300	17	hacl-hb	HA cluster heartbeat hp.com
44111	5301	6	hacl-gs	HA cluster general service hp.com
44112	5301	17	hacl-gs	HA cluster general service hp.com
44113	5302	6	hacl-cfg	HA cluster configuration hp.com
44114	5302	17	hacl-cfg	HA cluster configuration hp.com
44115	5303	6	hacl-probe	HA cluster probing hp.com
44116	5303	17	hacl-probe	HA cluster probing hp.com
44117	5304	6	hacl-local	HA Cluster Commands hp.com
44118	5304	17	hacl-local	HA Cluster Commands hp.com
44119	5305	6	hacl-test	HA Cluster Test hp.com
44120	5305	17	hacl-test	HA Cluster Test hp.com
44121	5306	6	sun-mc-grp	Sun MC Group eng.sun.com
44122	5306	17	sun-mc-grp	Sun MC Group eng.sun.com
44123	5307	6	sco-aip	sco.com
44124	5307	17	sco-aip	sco.com
44125	5308	6	cfengine	iu.hioslo.no
44126	5308	17	cfengine	iu.hioslo.no
44127	5309	6	jprinter	bristol.com
44128	5309	17	jprinter	bristol.com
44129	5310	6	outlaws	lucasart.com
44130	5310	17	outlaws	lucasart.com
44131	5311	6	tmlogin	east.sun.com
44132	5311	17	tmlogin	east.sun.com
44133	5321	6	firehotker	Fire Hot Keyer Trojan Horse
44134	5400	6	excerpt	Excerpt Search alma.com
44135	5400	17	excerpt	Excerpt Search alma.com
44136	5401	6	excerpts	Excerpt Search Secure alma.com
44137	5401	17	excerpts	Excerpt Search Secure alma.com
44138	5402	6	mftp	starburstscom.com
44139	5402	17	mftp	starburstscom.com
44140	5403	6	hpoms-ci-lstn	cup.hp.com
44141	5403	17	hpoms-ci-lstn	cup.hp.com
44142	5404	6	hpoms-dps-lstn	cup.hp.com
44143	5404	17	hpoms-dps-lstn	cup.hp.com
44144	5405	6	netsupport	pe77@dial.pipex.com
44145	5405	17	netsupport	pe77@dial.pipex.com
44146	5406	6	systemics-sox	systemics.com
44147	5406	17	systemics-sox	systemics.com
44148	5407	6	foresyte-clear	foresyte.com
44149	5407	17	foresyte-clear	foresyte.com
44150	5408	6	foresyte-sec	foresyte.com
44151	5408	17	foresyte-sec	foresyte.com
44152	5409	6	salient-dtasrv	Salient Data Server salient.com
44153	5409	17	salient-dtasrv	Salient Data Server salient.com
44154	5410	6	salient-usrmgr	Salient User Manager salient.com
44155	5410	17	salient-usrmgr	Salient User Manager salient.com
44156	5411	6	actnet	actresearch.com
44157	5411	17	actnet	actresearch.com
44158	5412	6	continuus	continuus.com
44159	5412	17	continuus	continuus.com
44160	5413	6	wwiotalk	wonderware.com
44161	5413	17	wwiotalk	wonderware.com
44162	5414	6	statusd	satelnet.org
44163	5414	17	statusd	satelnet.org
44164	5415	6	ns-server	netsoft.com
44165	5415	17	ns-server	netsoft.com
44166	5416	6	sns-gateway	firstfloor.com
44167	5416	17	sns-gateway	firstfloor.com
44168	5417	6	sns-agent	firstfloor.com
44169	5417	17	sns-agent	firstfloor.com
44170	5418	6	mcntp	pilhuhn.de
44171	5418	17	mcntp	pilhuhn.de
44172	5419	6	dj-ice	cor.dowjones.com
44173	5419	17	dj-ice	cor.dowjones.com
44174	5420	6	cylink-c	cylink.com
44175	5420	17	cylink-c	cylink.com
44176	5421	6	netsupport2	p.sanders@dial.pipex.com
44177	5421	17	netsupport2	p.sanders@dial.pipex.com
44178	5422	6	salient-mux	salient.com
44179	5422	17	salient-mux	salient.com
44180	5423	6	virtualuser	apple.com
44181	5423	17	virtualuser	apple.com
44182	5426	6	devbasic	vsin.com
44183	5426	17	devbasic	vsin.com
44184	5427	6	sco-peer-tta	sco.com
44185	5427	17	sco-peer-tta	sco.com
44186	5428	6	telaconsol	flounder.com
44187	5428	17	telaconsol	flounder.com
44188	5429	6	base	Billing & Accounting System Exchange ioag.de
44189	5429	17	base	Billing & Accounting System Exchange ioag.de
44190	5430	6	radec-corp	softlife.co.nz
44191	5430	17	radec-corp	softlife.co.nz
44192	5431	6	park-agent	veritas.com
44193	5431	17	park-agent	veritas.com
44194	5432	6	postgres	postgres database server
44195	5454	6	apc-tcp-udp-4	apcc.com
44196	5454	17	apc-tcp-udp-4	apcc.com
44197	5455	6	apc-tcp-udp-5	apcc.com
44198	5455	17	apc-tcp-udp-5	apcc.com
44199	5456	6	apc-tcp-udp-6	apcc.com
44200	5456	17	apc-tcp-udp-6	apcc.com
44201	5461	6	silkmeter	segue.com
44202	5461	17	silkmeter	segue.com
44203	5465	6	netops-broker	netops.com
44204	5465	17	netops-broker	netops.com
44205	5500	6	fcp-addr-srvr1	ac.com
44206	5500	17	fcp-addr-srvr1	ac.com
44207	5500	17	secuid	SecurID
44208	5501	17	secuidprop	SecurID ACE/Server Slave
44209	5501	6	fcp-addr-srvr2	ac.com
44210	5501	17	fcp-addr-srvr2	ac.com
44211	5502	6	fcp-srvr-inst1	ac.com
44212	5502	17	fcp-srvr-inst1	ac.com
44213	5503	6	fcp-srvr-inst2	ac.com
44214	5503	17	fcp-srvr-inst2	ac.com
44215	5504	6	fcp-cics-gwl	ac.com
44216	5504	17	fcp-cics-gwl	ac.com
44217	5510	6	securidprop	ACE/Server Services
44218	5520	6	sdlog	ACE/Server Services
44219	5530	6	sdserv	ACE/Server Services
44220	5540	6	sdreport	ACE/Server Services
44221	5540	17	sdxauth	ACE/Server Services
44222	5550	6	sdadmind	ACE/Server Services
44223	5554	6	sgi-esphttp	SGI ESP HTTP sgi.com
44224	5554	17	sgi-esphttp	SGI ESP HTTP sgi.com
44225	5555	6	personal-agent	infoseek.com
44226	5555	17	personal-agent	infoseek.com
44227	5555	17	nbsp;	HP Omniback (clashes with personal-agent)
44228	5555	6	serverme	ServerMe Trojan Horse
44229	5555	17	serverme	ServerMe Trojan Horse
44230	5556	6	mtb	Mtbd (mtb backup)
44231	5559	6	esinstall	Enterprise Security Remote Install axent.com
44232	5569	6	robohack	Robo Hack trojan Horse
44233	5600	6	esmanager	Enterprise Security Manager axent.com
44234	5601	6	esmagent	Enterprise Security Agent axent.com
44235	5602	6	a1-msc	lucent.com
44236	5603	6	a1-bs	lucent.com
44237	5604	6	a3-sdunode	lucent.com
44238	5605	6	a4-sdunode	lucent.com
44239	5631	6	pcanywheredata	pcANYWHEREdata symantec.com
44240	5631	17	pcanywheredata	pcANYWHEREdata symantec.com
44241	5632	6	pcanywherestat	pcANYWHEREstat symantec.com
44242	5632	17	pcanywherestat	pcANYWHEREstat symantec.com
44243	5678	6	rrac	Remote Replication Agent Connection microsoft.com
44244	5679	6	dccm	Direct Cable Connect Manager microsoft.com
44245	5680	6	canna	Canna (Japanese Input)
44246	5713	6	proshareaudio	Proshare Conf Audio intel.com
44247	5713	17	proshareaudio	Proshare Conf Audio intel.com
44248	5714	6	prosharevideo	Proshare Conf Video intel.com
44249	5714	17	prosharevideo	Proshare Conf Video intel.com
44250	5715	6	prosharedata	Proshare Conf Data intel.com
44251	5715	17	prosharedata	Proshare Conf Data intel.com
44252	5716	6	prosharerequest	Proshare Conf Request intel.com
44253	5716	17	prosharerequest	Proshare Conf Request intel.com
44254	5717	6	prosharenotify	Proshare Conf Notify intel.com
44255	5717	17	prosharenotify	Proshare Conf Notify intel.com
44256	5729	6	openmail	Openmail User Agent Layer hp.com
44257	5729	17	openmail	Openmail User Agent Layer hp.com
44258	5741	6	ida-discover1	i-data.com
44259	5741	17	ida-discover1	i-data.com
44260	5742	6	ida-discover2	i-data.com
44261	5742	17	ida-discover2	i-data.com
44262	5742	6	wincrash	Wincrash Trojan
44263	5745	6	fcopy-server	softlinkusa.com
44264	5745	17	fcopy-server	softlinkusa.com
44265	5746	6	fcopys-server	softlinkusa.com
44266	5746	17	fcopys-server	softlinkusa.com
44267	5755	6	openmailg	Openmail Desk Gateway Server hp.com
44268	5755	17	openmailg	Openmail Desk Gateway Server hp.com
44269	5757	6	x500ms	Openmail X.500 Directory Server hp.com
44270	5757	17	x500ms	Openmail X.500 Directory Server hp.com
44271	5766	6	openmailns	Openmail NewMail Server hp.com
44272	5766	17	openmailns	Openmail NewMail Server hp.com
44273	5767	6	s-openmail	Openmail Suer Agent Layer (secure) hp.com
44274	5767	17	s-openmail	Openmail Suer Agent Layer (secure) hp.com
44275	5768	6	openmailpxy	Openmail CMTS Server hp.com
44276	5768	17	openmailpxy	Openmail CMTS Server hp.com
44277	5771	6	netagent	share.com
44278	5771	17	netagent	share.com
44279	5800	6	vnc	AT&T Virtual Network Computing
44280	5801	6	vnc	AT&T Virtual Network Computing
44281	5813	6	icmpd	opennms.com
44282	5813	17	icmpd	opennms.com
44283	5900	6	vnc	AT&T Virtual Network Computing
44284	5901	6	vnc	AT&T Virtual Network Computing
44285	5968	6	mppolicy-v5	fujitsu.co.jp
44286	5968	17	mppolicy-v5	fujitsu.co.jp
44287	5969	6	mppolicy-mgr	fujitsu.co.jp
44288	5969	17	mppolicy-mgr	fujitsu.co.jp
44289	5977	6	ncd-pref-tcp	NCD preferences tcp port
44290	5978	6	ncd-diag-tcp	NCD diagnostic tcp port
44291	5979	6	ncd-conf-tcp	NCD configuration tcp port
44292	5997	6	ncd-pref	NCD preferences telnet port
44293	5998	6	ncd-diag	NCD diagnostic telnet port
44294	5999	6	ncd-conf	NCD configuration telnet port
44295	5999	6	cvsup	inet.org
44296	5999	17	cvsup	inet.org
44297	6000	6	x11	X Windows System mit.edu
44298	6000	17	x11	X Windows System mit.edu
44299	6064	6	ndl-ahp-svc	dnl.co.uk
44300	6064	17	ndl-ahp-svc	dnl.co.uk
44301	6065	6	winpharaoh	gnnettest.com
44302	6065	17	winpharaoh	gnnettest.com
44303	6066	6	ewctsp	ericsson.com
44304	6066	17	ewctsp	ericsson.com
44305	6067	6	srb	nexos.com
44306	6067	17	srb	nexos.com
44307	6068	6	gsmp	nokia.com
44308	6068	17	gsmp	nokia.com
44309	6069	6	trip	cisco.com
44310	6069	17	trip	cisco.com
44311	6070	6	messageasap	officedomain.com
44312	6070	17	messageasap	officedomain.com
44313	6071	6	ssdtp	softsys-inc.com
44314	6071	17	ssdtp	softsys-inc.com
44315	6072	6	diagmose-proc	handsfreenetworks.com
44316	6072	17	diagmose-proc	handsfreenetworks.com
44317	6073	6	directplay8	microsoft.com
44318	6073	17	directplay8	microsoft.com
44319	6100	6	synchronet-db	parasoldev.com
44320	6100	17	synchronet-db	parasoldev.com
44321	6101	6	synchronet-rtc	parasoldev.com
44322	6101	17	synchronet-rtc	parasoldev.com
44323	6102	6	synchronet-udp	parasoldev.com
44324	6102	17	synchronet-udp	parasoldev.com
44325	6103	6	rets	optc.com
44326	6103	17	rets	optc.com
44327	6104	6	dbdb	lithic.org
44328	6104	17	dbdb	lithic.org
44329	6105	6	primaserver	prima.com.hk
44330	6105	17	primaserver	prima.com.hk
44331	6106	6	mpsserver	prima.com.hk
44332	6106	17	mpsserver	prima.com.hk
44333	6107	6	etc-control	etcconnect.com
44334	6107	17	etc-control	etcconnect.com
44335	6108	6	sercomm-scadmin	sercomm.com.tw
44336	6108	17	sercomm-scadmin	sercomm.com.tw
44337	6109	6	globecast-id	globecastne.com
44338	6109	17	globecast-id	globecastne.com
44339	6110	6	softcm	HP SoftBench CM hp.com
44340	6110	17	softcm	HP SoftBench CM hp.com
44341	6111	6	sub-process	HP SoftBench Sub-Process Control hp.com
44342	6111	17	sub-process	HP SoftBench Sub-Process Control hp.com
44343	6112	6	dtspcd	CDE subprocess control eng.sun.com
44344	6112	17	dtspcd	CDE subprocess control eng.sun.com
44345	6112	6	battlenet	multiplayer game "Diablo"
44346	6112	17	battlenet	multiplayer game "Diablo"
44347	6123	6	backup-express	syncsort.com
44348	6123	17	backup-express	syncsort.com
44349	6141	6	meta-corp	Meta Corporation License Manager
44350	6141	17	meta-corp	Meta Corporation License Manager
44351	6142	6	aspentec-lm	Aspen Technology License Manager aspentec.com
44352	6142	17	aspentec-lm	Aspen Technology License Manager aspentec.com
44353	6143	6	watershed-lm	Watershed License Manager zion.com
44354	6143	17	watershed-lm	Watershed License Manager zion.com
44355	6144	6	statsci1-lm	StatSci License Manager-1 statsci.com
44356	6144	17	statsci1-lm	StatSci License Manager-1 statsci.com
44357	6145	6	statsci2-lm	StatSci License Manager-2 statsci.com
44358	6145	17	statsci2-lm	StatSci License Manager-2 statsci.com
44359	6146	6	lonewolf-lm	Lone Wolf Systems License Manager lonewolf.com
44360	6146	17	lonewolf-lm	Lone Wolf Systems License Manager lonewolf.com
44361	6147	6	montage-lm	Montage License Manager montage.com
44362	6147	17	montage-lm	Montage License Manager montage.com
44363	6148	6	ricardo-lm	Ricardo North America License Manager aol.com
44364	6148	17	ricardo-lm	Ricardo North America License Manager aol.com
44365	6149	6	tal-pod	taligent.com
44366	6149	17	tal-pod	taligent.com
44367	6253	6	crip	ciena.com
44368	6253	17	crip	ciena.com
44369	6346	6	gnutella	Gnutella file sharing Application
44370	6347	6	gnutella	Gnutella file sharing Application
44371	6389	6	clariion-evr01	clariion.com
44372	6389	17	clariion-evr01	clariion.com
44373	6400	6	info-aps	saegatesoftware.com
44374	6400	17	info-aps	saegatesoftware.com
44375	6400	6	thething	The Thing Trojan Horse
44376	6400	17	thething	The Thing Trojan Horse
44377	6401	6	info-was	saegatesoftware.com
44378	6401	17	info-was	saegatesoftware.com
44379	6402	6	info-eventsvr	saegatesoftware.com
44380	6402	17	info-eventsvr	saegatesoftware.com
44381	6403	6	info-cachesvr	saegatesoftware.com
44382	6403	17	info-cachesvr	saegatesoftware.com
44383	6404	6	info-filesvr	saegatesoftware.com
44384	6404	17	info-filesvr	saegatesoftware.com
44385	6405	6	info-pagesvr	saegatesoftware.com
44386	6405	17	info-pagesvr	saegatesoftware.com
44387	6406	6	info-processvr	saegatesoftware.com
44388	6406	17	info-processvr	saegatesoftware.com
44389	6407	6	reserved1	saegatesoftware.com
44390	6407	17	reserved1	saegatesoftware.com
44391	6408	6	reserved2	saegatesoftware.com
44392	6408	17	reserved2	saegatesoftware.com
44393	6409	6	reserved3	saegatesoftware.com
44394	6409	17	reserved3	saegatesoftware.com
44395	6410	6	info-aps	saegatesoftware.com
44396	6410	17	info-aps	saegatesoftware.com
44397	6455	6	skip-cert-recv	osmosys.incog.com
44398	6455	17	skip-cert-recv	osmosys.incog.com
44399	6456	6	skip-cert-send	osmosys.incog.com
44400	6456	17	skip-cert-send	osmosys.incog.com
44401	6471	6	lvision-lm	lvision.com
44402	6471	17	lvision-lm	lvision.com
44403	6500	6	boks	BoKS Master dynas.se
44404	6500	17	boks	BoKS Master dynas.se
44405	6501	6	boks_servc	BoKS Servc dynas.se
44406	6501	17	boks_servc	BoKS Servc dynas.se
44407	6502	6	boks_servm	BoKS Servm dynas.se
44408	6502	17	boks_servm	BoKS Servm dynas.se
44409	6502	6	netconf	Netscape Conference
44410	6502	17	netconf	Netscape Conference
44411	6503	6	boks_clntd	BoKS Clntd dynas.se
44412	6503	17	boks_clntd	BoKS Clntd dynas.se
44413	6505	6	badm_priv	BoKS Admin Private Port dynas.se
44414	6505	17	badm_priv	BoKS Admin Private Port dynas.se
44415	6506	6	badm_pub	BoKS Admin Public Port dynas.se
44416	6506	17	badm_pub	BoKS Admin Public Port dynas.se
44417	6507	6	bdir_priv	BoKS Dir Server, Private Port dynas.se
44418	6507	17	bdir_priv	BoKS Dir Server, Private Port dynas.se
44419	6508	6	bdir_pub	BoKS Dir Server, Public Port dynas.se
44420	6508	17	bdir_pub	BoKS Dir Server, Public Port dynas.se
44421	6547	6	apc-tcp-udp-1	apcc.com
44422	6547	17	apc-tcp-udp-1	apcc.com
44423	6548	6	apc-tcp-udp-2	apcc.com
44424	6548	17	apc-tcp-udp-2	apcc.com
44425	6549	6	apc-tcp-udp-3	apcc.com
44426	6549	17	apc-tcp-udp-3	apcc.com
44427	6550	6	fg-sysupdate	freegate.com
44428	6550	17	fg-sysupdate	freegate.com
44429	6558	6	xdsxdm	nbsp;
44430	6558	17	xdsxdm	nbsp;
44431	6588	6	analogx	AnalogX http https proxy, analogx.com
44432	6588	17	analogx	AnalogX http https proxy, analogx.com
44433	6665	6	ircu	Internet Relay Chat acrux.com
44434	6665	17	ircu	Internet Relay Chat acrux.com
44435	6666	6	ircu	Internet Relay Chat acrux.com
44436	6666	17	ircu	Internet Relay Chat acrux.com
44437	6667	6	ircu	Internet Relay Chat acrux.com
44438	6667	17	ircu	Internet Relay Chat acrux.com
44439	6668	6	ircu	Internet Relay Chat acrux.com
44440	6668	17	ircu	Internet Relay Chat acrux.com
44441	6669	6	ircu	Internet Relay Chat acrux.com
44442	6669	17	ircu	Internet Relay Chat acrux.com
44443	6665	6	irc	Internet Relay Chat
44444	6666	6	irc-serv	Internet Relay Chat Server
44445	6667	6	irc	Internet Relay Chat
44446	6668	6	irc	Internet Relay Chat
44447	6669	6	irc	Internet Relay Chat
44448	6670	6	vocaltec-gold	Vocaltec Global online Directory vocaltec.com
44449	6670	17	vocaltec-gold	Vocaltec Global online Directory vocaltec.com
44450	6670	6	deepthroat	Deep Throat Trojan Horse
44451	6671	6	deepthroat	Deep Throat Trojan Horse
44452	6672	6	vision_server	gis.shl.com
44453	6672	17	vision_server	gis.shl.com
44454	6673	6	vision_elmd	gis.shl.com
44455	6673	17	vision_elmd	gis.shl.com
44456	6673	6	vision_elmd	gis.shl.com
44457	6673	17	vision_elmd	gis.shl.com
44458	6699	6	napster	www.napster.com communication
44459	6699	17	napster	www.napster.com communication
44460	6700	6	napster	www.napster.com communication
44461	6700	17	napster	www.napster.com communication
44462	6701	6	kti-icad-srvr	KTI/ICAD Nameserver KTIworld.com
44463	6701	17	kti-icad-srvr	KTI/ICAD Nameserver KTIworld.com
44464	6711	6	sub7	Sub Seven Trojan Horse
44465	6723	6	nbsp;	Mstream DDOS communication TCP
44466	6767	6	bmc-perf-agent	bmc.com
44467	6767	17	bmc-perf-agent	bmc.com
44468	6768	6	bmc-perf-mgrd	bmc.com
44469	6768	17	bmc-perf-mgrd	bmc.com
44470	6776	6	sub7	Sub Seven Trojan Horse
44471	6790	6	hnmp	nas.nasa.gov
44472	6790	17	hnmp	nas.nasa.gov
44473	6831	6	ambit-lm	ambit.com
44474	6831	17	ambit-lm	ambit.com
44475	6838	17	nbsp;	Mstream DDOS communication UDP
44476	6841	6	netmo-default	netmosphere.com
44477	6841	17	netmo-default	netmosphere.com
44478	6842	6	netmo-http	netmosphere.com
44479	6842	17	netmo-http	netmosphere.com
44480	6850	6	iccrushmore	icc.net
44481	6850	17	iccrushmore	icc.net
44482	6888	6	muse	muse3d.com
44483	6888	17	muse	muse3d.com
44484	6939	6	indoc	Indoctrination trojan Horse
44485	6939	17	indoc	Indoctrination trojan Horse
44486	6961	6	jmact3	fujitsu.co.jp
44487	6961	17	jmact3	fujitsu.co.jp
44488	6962	6	jmevt2	fujitsu.co.jp
44489	6962	17	jmevt2	fujitsu.co.jp
44490	6963	6	swismgr1	fujitsu.co.jp
44491	6963	17	swismgr1	fujitsu.co.jp
44492	6964	6	swismgr2	fujitsu.co.jp
44493	6964	17	swismgr2	fujitsu.co.jp
44494	6965	6	swistrap	fujitsu.co.jp
44495	6965	17	swistrap	fujitsu.co.jp
44496	6966	6	swispol	fujitsu.co.jp
44497	6966	17	swispol	fujitsu.co.jp
44498	6969	6	acmsoda	GateCrasher remote access backdoor (Win9x/NT) as well as ACMSODA and Priority Trojan
44499	6969	17	acmsoda	GateCrasher remote access backdoor (Win9x/NT) as well as ACMSODA and Priority Trojan
44500	6970	17		Real Audio (inclusive) for incoming traffic only
44501	6998	6	iatp-highpri	mci.com
44502	6998	17	iatp-highpri	mci.com
44503	6999	6	iatp-normalpri	mci.com
44504	6999	17	iatp-normalpri	mci.com
44505	7000	6	afs3-fileserver	File server itself, msdos
44506	7000	17	afs3-fileserver	File server itself, msdos
44507	7000	6	nbsp;	Real Audio Control
44508	7000	6	remotegrabber	Remote Grabber Trojan Horse
44509	7000	17	remotegrabber	Remote Grabber Trojan Horse
44510	7001	6	afs3-callback	Callbacks to cache managers
44511	7001	17	afs3-callback	Callbacks to cache managers
44512	7002	6	afs3-prserver	Users and groups database
44513	7002	17	afs3-prserver	Users and groups database
44514	7003	6	afs3-vlserver	Volume location database
44515	7003	17	afs3-vlserver	Volume location database
44516	7004	6	afs3-kaserver	AFS Kerberos authentication service
44517	7004	17	afs3-kaserver	AFS Kerberos authentication service
44518	7005	6	afs3-volser	Volume management server
44519	7005	17	afs3-volser	Volume management server
44520	7006	6	afs3-errors	Error interpretation service
44521	7006	17	afs3-errors	Error interpretation service
44522	7007	6	afs3-bos	Basic overseer process
44523	7007	17	afs3-bos	Basic overseer process
44524	7007	6	msbd	Windows Media Encoder
44525	7007	17	msbd	Windows Media Encoder
44526	7008	6	afs3-update	Server-to-server updater
44527	7008	17	afs3-update	Server-to-server updater
44528	7009	6	afs3-rmtsys	Remote cache manager service
44529	7009	17	afs3-rmtsys	Remote cache manager service
44530	7010	6	ups-onlinet	Onlinet UPSs exide.com
44531	7010	17	ups-onlinet	Onlinet UPSs exide.com
44532	7011	6	talon-disc	Talon Discovery Port powerware.com
44533	7011	17	talon-disc	Talon Discovery Port powerware.com
44534	7012	6	talon-engine	Talon Engine powerware.com
44535	7012	17	talon-engine	Talon Engine powerware.com
44536	7020	6	dpserve	hummingbird.com
44537	7020	17	dpserve	hummingbird.com
44538	7021	6	dpserveadmin	hummingbird.com
44539	7021	17	dpserveadmin	hummingbird.com
44540	7070	6	arcp	nas.nasa.gov
44541	7070	17	arcp	nas.nasa.gov
44542	7070	6		Real Audio Versions 3, 4, 5 / QuickTime
44543	7099	6	lazy-ptop	scitex.com
44544	7099	17	lazy-ptop	scitex.com
44545	7100	6	font-service	X Font Service lcs.mit.edu
44546	7100	17	font-service	X Font Service lcs.mit.edu
44547	7121	6	virprot-lm	sarchmo.virtualprototypes.ca
44548	7121	17	virprot-lm	sarchmo.virtualprototypes.ca
44549	7141	6	clutild	vnet.ibm.com
44550	7141	17	clutild	vnet.ibm.com
44551	7161	6	nbsp;	Cisco Catalyst
44552	7200	6	fodms	FODMS FLIP rockwell.com
44553	7200	17	fodms	FODMS FLIP rockwell.com
44554	7201	6	dlip	rockwell.com
44555	7201	17	dlip	rockwell.com
44556	7300	6	netmonitor	Netmonitor Trojan Horse
44557	7301	6	netmonitor	Netmonitor Trojan Horse
44558	7306	6	netmonitor	Netmonitor Trojan Horse
44559	7307	6	netmonitor	Netmonitor Trojan Horse
44560	7308	6	netmonitor	Netmonitor Trojan Horse
44561	7323	6	nbsp;	SyGate 3.11 Remote Administration
44562	7326	6	icb	Internet Citizens Band
44563	7395	6	winqedit	robelle.com
44564	7395	17	winqedit	robelle.com
44565	7426	6	pmdmgr	OpenView DM Post Manager hp.com
44566	7426	17	pmdmgr	OpenView DM Post Manager hp.com
44567	7427	6	oveadmgr	OpenView DM Event Agent Manager hp.com
44568	7427	17	oveadmgr	OpenView DM Event Agent Manager hp.com
44569	7428	6	ovladmgr	OpenView DM log Agent Manager hp.com
44570	7428	17	ovladmgr	OpenView DM log Agent Manager hp.com
44571	7429	6	opi-sock	OpenView DM rqt communication hp.com
44572	7429	17	opi-sock	OpenView DM rqt communication hp.com
44573	7430	6	xmpv7	OpenView DM xmpv7 api pipe hp.com
44574	7430	17	xmpv7	OpenView DM xmpv7 api pipe hp.com
44575	7431	6	pmd	OpenView DM ovc/xmpv3 api pipe hp.com
44576	7431	17	pmd	OpenView DM ovc/xmpv3 api pipe hp.com
44577	7437	6	faximum	faximum.com
44578	7437	17	faximum	faximum.com
44579	7491	6	telops-lmd	telops.com
44580	7491	17	telops-lmd	telops.com
44581	7511	6	pafec-lm	pafec.co.uk
44582	7511	17	pafec-lm	pafec.co.uk
44583	7544	6	nta-ds	FlowAnalyzer DisplayServer cisco.com
44584	7544	17	nta-ds	FlowAnalyzer DisplayServer cisco.com
44585	7545	6	nta-us	FlowAnalyzer UtilityServer cisco.com
44586	7545	17	nta-us	FlowAnalyzer UtilityServer cisco.com
44587	7566	6	vsi-omega	vsin.com
44588	7566	17	vsi-omega	vsin.com
44589	7570	6	aries-kfinder	ariessys.com
44590	7570	17	aries-kfinder	ariessys.com
44591	7588	6	sun-lm	eng.sun.com
44592	7588	17	sun-lm	eng.sun.com
44593	7597	6	QAZ	Unassigned QAZ TROJAN WORM
44594	7597	17	QAZ	Unassigned QAZ TROJAN WORM
44595	7633	6	pmdfmgt	innosoft.com
44596	7633	17	pmdfmgt	innosoft.com
44597	7640	6	nbsp;	CUSeeMe (TCP, UDP)
44598	7640	17	nbsp;	CUSeeMe (TCP, UDP)
44599	7648	17	cucme-1	CUCME live video/audio server
44600	7649	17	cucme-2	CUCME live video/audio server
44601	7650	17	cucme-3	CUCME live video/audio server
44602	7651	17	cucme-4	CUCME live video/audio server
44603	7777	6	cbt	cs.ucl.ac.uk
44604	7777	17	cbt	cs.ucl.ac.uk
44605	7778	6	unreal	Unreal Tournament
44606	7778	17	unreal	Unreal Tournament
44607	7781	6	accu-lmgr	accugraph.com
44608	7781	17	accu-lmgr	accugraph.com
44609	7786	6	minivend	minivend.com
44610	7786	17	minivend	minivend.com
44611	7789	6	ickiller	ICKiller Trojan Hose
44612	7932	6	t2-drm	Tier 2 Data Resource Manager tier2.com
44613	7932	17	t2-drm	Tier 2 Data Resource Manager tier2.com
44614	7933	6	t2-brm	Tier 2 Business Rules Manager tier2.com
44615	7933	17	t2-brm	Tier 2 Business Rules Manager tier2.com
44616	7967	6	supercell	sigsci.com
44617	7967	17	supercell	sigsci.com
44618	7979	6	micomuse-ncps	micromuse.com
44619	7979	17	micomuse-ncps	micromuse.com
44620	7980	6	quest-vista	quests.com
44621	7980	17	quest-vista	quests.com
44622	7983	17	nbsp;	Mstraem DDOS communication UDP
44623	7999	6	irdmi2	intel.com
44624	7999	17	irdmi2	intel.com
44625	8000	6	irdmi	intel.com
44626	8000	17	irdmi	intel.com
44627	8001	6	vcom-tunnel	us.ibm.com
44628	8001	17	vcom-tunnel	us.ibm.com
44629	8002	6	teradataordbms	Teradata ORDBMS ncr.com
44630	8002	17	teradataordbms	Teradata ORDBMS ncr.com
44631	8002	6	nbsp;	Cmail Web Admin
44632	8008	6	http-alt	w3.org
44633	8008	17	http-alt	w3.org
44634	8010	6	wingate	WinGate 2.1
44635	8010	17	wingate	WinGate 2.1
44636	8032	6	pro-ed	goldrush.com
44637	8032	17	pro-ed	goldrush.com
44638	8033	6	mindprint	goldrush.com
44639	8033	17	mindprint	goldrush.com
44640	8080	6	http-proxy	Common HTTP proxy/second web server port
44641	8181	6	nbsp;	Imail Monitor plus HTTP management
44642	8200	6	trivent1	trivnet.com
44643	8200	17	trivent1	trivnet.com
44644	8201	6	trivent2	trivnet.com
44645	8201	17	trivent2	trivnet.com
44646	8204	6	lm-perfworks	LM Perfworks landmark.com
44647	8204	17	lm-perfworks	LM Perfworks landmark.com
44648	8205	6	lm-instmgr	LM Instmgr landmark.com
44649	8205	17	lm-instmgr	LM Instmgr landmark.com
44650	8206	6	lm-dta	LM Dta landmark.com
44651	8206	17	lm-dta	LM Dta landmark.com
44652	8207	6	lm-sserver	LM SServer landmark.com
44653	8207	17	lm-sserver	LM SServer landmark.com
44654	8208	6	lm-webwatcher	LM Webwatcher landmark.com
44655	8208	17	lm-webwatcher	LM Webwatcher landmark.com
44656	8351	6	server-find	chancery.com
44657	8351	17	server-find	chancery.com
44658	8376	6	cruise-enum	Cruise ENUM cruisetech.com
44659	8376	17	cruise-enum	Cruise ENUM cruisetech.com
44660	8377	6	cruise-swroute	Cruise SWROUTE cruisetech.com
44661	8377	17	cruise-swroute	Cruise SWROUTE cruisetech.com
44662	8378	6	cruise-config	Cruise CONFIG cruisetech.com
44663	8378	17	cruise-config	Cruise CONFIG cruisetech.com
44664	8379	6	cruise-diags	Cruise DIAGS cruisetech.com
44665	8379	17	cruise-diags	Cruise DIAGS cruisetech.com
44666	8380	6	cruise-update	Cruise UPDATE cruisetech.com
44667	8380	17	cruise-update	Cruise UPDATE cruisetech.com
44668	8383	6	imailwww	IMail http www.ipswitch.com
44669	8383	17	imailwww	IMail http www.ipswitch.com
44670	8400	6	cvd	CVD commvault.com
44671	8400	17	cvd	CVD commvault.com
44672	8401	6	sabarsd	SABARSD commvault.com
44673	8401	17	sabarsd	SABARSD commvault.com
44674	8402	6	abarsd	ABARSD commvault.com
44675	8402	17	abarsd	ABARSD commvault.com
44676	8403	6	admind	ADMIND commvault.com
44677	8403	17	admind	ADMIND commvault.com
44678	8431	6	nbsp;	Trend Micro PC-Cilin
44679	8450	6	npmp	npmp tanagra.demon.co.uk
44680	8450	17	npmp	npmp tanagra.demon.co.uk
44681	8473	6	vp2p	Virtual Point to Point atos-group.com
44682	8473	17	vp2p	Virtual Point to Point atos-group.com
44683	8554	6	rtsp-alt	RTSP Alternate (see port 554) precept.com
44684	8554	17	rtsp-alt	RTSP Alternate (see port 554) precept.com
44685	8602	6	XBConnect	XBConnect for playing Microsoft xbox linkable games online
44686	8602	17	XBConnect	XBConnect for playing Microsoft xbox linkable games online
44687	8763	6	mc-appsserver	microcomgroup.com
44688	8763	17	mc-appsserver	microcomgroup.com
44689	8764	6	openqueue	newsblip.com
44690	8764	17	openqueue	newsblip.com
44691	8765	6	ultraseek-http	Ultraseek HTTP infoseek.com
44692	8765	17	ultraseek-http	Ultraseek HTTP infoseek.com
44693	8804	6	truecm	truebluesoftware.com
44694	8804	17	truecm	truebluesoftware.com
44695	8875	6	napster	napster
44696	8875	17	napster	napster
44697	8880	6	CDDBP	moonsoft.com
44698	8880	17	CDDBP	moonsoft.com
44699	8888	6	napster	napster
44700	8888	17	napster	napster
44701	8888	6	sun-answerbook	Sun Answerbook HTTP server
44702	8888	6	ddi-tcp-1	NewsEDGE server desktopdata.com
44703	8888	17	ddi-tcp-1	NewsEDGE server desktopdata.com
44704	8889	6	ddi-tcp2	Desktop Data (tcp 1) NewsEDGE server broadcast(udp) desktopdata.com
44705	8889	17	ddi-tcp2	Desktop Data (tcp 1) NewsEDGE server broadcast(udp) desktopdata.com
44706	8890	6	ddi-tcp3	Desktop Data (tcp 2) NewsEDGE client broadcast(udp) desktopdata.com
44707	8890	17	ddi-tcp3	Desktop Data (tcp 2) NewsEDGE client broadcast(udp) desktopdata.com
44708	8891	6	ddi-tcp4	Desktop Data (tcp 3) NESS application desktopdata.com
44709	8891	17	ddi-tcp4	Desktop Data (tcp 3) NESS application desktopdata.com
44710	8892	6	ddi-tcp5	Desktop Data (tcp 4) FARM product desktopdata.com
44711	8892	17	ddi-tcp5	Desktop Data (tcp 4) FARM product desktopdata.com
44712	8893	6	ddi-tcp6	Desktop Data (tcp 5) NewsEDGE/Web application desktopdata.com
44713	8893	17	ddi-tcp6	Desktop Data (tcp 5) NewsEDGE/Web application desktopdata.com
44714	8894	6	ddi-tcp7	Desktop Data (tcp 6) COAL application desktopdata.com
44715	8894	17	ddi-tcp7	Desktop Data (tcp 6) COAL application desktopdata.com
44716	8900	6	jmb-cds1	creativedesign.com
44717	8900	17	jmb-cds1	creativedesign.com
44718	8901	6	jmb-cds2	creativedesign.com
44719	8901	17	jmb-cds2	creativedesign.com
44720	8999	6	nbsp;	Gauntlet Firewall
44721	9000	6	clistener	CSlistener cincom.com
44722	9000	17	clistener	CSlistener cincom.com
44723	9090	6	websm	WebSM austin.ibm.com
44724	9090	17	websm	WebSM austin.ibm.com
44725	9100	6	jetdirect	HP JetDirect card hp.com
44726	9160	6	netlock1	netlock.com
44727	9160	17	netlock1	netlock.com
44728	9161	6	netlock2	netlock.com
44729	9161	17	netlock2	netlock.com
44730	9162	6	netlock3	netlock.com
44731	9162	17	netlock3	netlock.com
44732	9163	6	netlock4	netlock.com
44733	9163	17	netlock4	netlock.com
44734	9164	6	netlock5	netlock.com
44735	9164	17	netlock5	netlock.com
44736	9200	6	wap-wsp	WAP connectionless session service wapforum.org
44737	9200	17	wap-wsp	WAP connectionless session service wapforum.org
44738	9201	6	wap-wsp-wtp	WAP session service wapforum.org
44739	9201	17	wap-wsp-wtp	WAP session service wapforum.org
44740	9202	6	wap-wsp-s	WAP secure connectionless session service wapforum.org
44741	9202	17	wap-wsp-s	WAP secure connectionless session service wapforum.org
44742	9203	6	wap-wsp-wtp-s	WAP secure session service wapforum.org
44743	9203	17	wap-wsp-wtp-s	WAP secure session service wapforum.org
44744	9204	6	wap-vcard	WAP vCard wapforum.org
44745	9204	17	wap-vcard	WAP vCard wapforum.org
44746	9205	6	wap-vcal	WAP vCal wapforum.org
44747	9205	17	wap-vcal	WAP vCal wapforum.org
44748	9206	6	wap-vcard-s	WAP vCard Secure wapforum.org
44749	9206	17	wap-vcard-s	WAP vCard Secure wapforum.org
44750	9207	6	wap-vcal-s	WAP vCal Secure wapforum.org
44751	9207	17	wap-vcal-s	WAP vCal Secure wapforum.org
44752	9297	17	netlock6	Netlock Agent communication over NAT netlock.com
44753	9321	6	guibase	fujitsu.co.jp
44754	9321	17	guibase	fujitsu.co.jp
44755	9325	17	nbsp;	Mstream DDOS communication UDP
44756	9343	6	mpidcmgr	fujitsu.co.jp
44757	9343	17	mpidcmgr	fujitsu.co.jp
44758	9344	6	mphlpdmc	fujitsu.co.jp
44759	9344	17	mphlpdmc	fujitsu.co.jp
44760	9374	6	fjdmimgr	fujitsu.co.jp
44761	9374	17	fjdmimgr	fujitsu.co.jp
44762	9396	6	fjinvmgr	fujitsu.co.jp
44763	9396	17	fjinvmgr	fujitsu.co.jp
44764	9397	6	mpidcagt	fujitsu.co.jp
44765	9397	17	mpidcagt	fujitsu.co.jp
44766	9500	6	ismserver	micromuse.co.uk
44767	9500	17	ismserver	micromuse.co.uk
44768	9535	6	man	Remote man server intel.com
44769	9535	17	man	Remote man server intel.com
44770	9536	6	W	nbsp;
44771	9537	6	mantst	Remote man server, testing
44772	9594	6	msgsys	Message System intel.com
44773	9594	17	msgsys	Message System intel.com
44774	9595	6	pds	Ping Discovery Service intel.com
44775	9595	17	pds	Ping Discovery Service intel.com
44776	9753	6	rasadv	microsoft.com
44777	9753	17	rasadv	microsoft.com
44778	9872	6	portalofdoom	Portal of Doom Trojan Horse
44779	9873	6	portalofdoom	Portal of Doom Trojan Horse
44780	9874	6	portalofdoom	Portal of Doom Trojan Horse
44781	9875	6	portalofdoom	Portal of Doom Trojan Horse
44782	9876	6	sd	Session Director ee.lbl.gov
44783	9876	17	sd	Session Director ee.lbl.gov
44784	9888	6	cyborg-systems	cyborg.com
44785	9888	17	cyborg-systems	cyborg.com
44786	9898	6	monkeycom	niftyserve.or.jp
44787	9898	17	monkeycom	niftyserve.or.jp
44788	9899	6	sctp-tunneling	nortelnetworks.com
44789	9899	17	sctp-tunneling	nortelnetworks.com
44790	9989	6	inikiller	IniKiller Trojan Horse
44791	9900	6	iua	nortelnetworks.com
44792	9900	17	iua	nortelnetworks.com
44793	9909	6	domaintime	greyware.com
44794	9909	17	domaintime	greyware.com
44795	9950	6	apcpcpluswin1	apcc.com
44796	9950	17	apcpcpluswin1	apcc.com
44797	9951	6	apcpcpluswin2	apcc.com
44798	9951	17	apcpcpluswin2	apcc.com
44799	9952	6	apcpcpluswin3	apcc.com
44800	9952	17	apcpcpluswin3	apcc.com
44801	9998	6	distinct32	distinct.com
44802	9998	17	distinct32	distinct.com
44803	9999	6	distinct	distinct.com
44804	9999	17	distinct	distinct.com
44805	10000	6	ndmp	Network Data Management Protocol netapp.com
44806	10000	17	ndmp	Network Data Management Protocol netapp.com
44807	10000	6	bnews	
44808	10000	17	rscsO	
44809	10001	6	queue	
44810	10001	17	rscsl	
44811	10002	6	poker	
44812	10002	17	rscs2	
44813	10003	6	gateway	
44814	10003	17	rscs3	
44815	10004	6	remp	
44816	10004	17	rscs4	
44817	10005	6	stel	Secure telnet
44818	10005	17	rscs5	
44819	10006	17	rscs6	
44820	10007	6	mvs-capacity	us.ibm.com
44821	10007	17	mvs-capacity	us.ibm.com
44822	10007	17	rscs7	
44823	10008	17	rscs8	
44824	10008	17	cworm	Cheese Worm
44825	10009	17	rscs9	
44826	10010	17	rscsa	
44827	10011	17	rscsb	
44828	10012	6	qmaster	
44829	10012	17	qmaster	
44830	10067	17	pod	Portal of Doom remote access backdoor
44831	10080	6	amanda	Backup Server Control amanda.org
44832	10080	17	amanda	Backup Server Control amanda.org
44833	10082	6	amandaidx	Amanda Indexing amanda.org
44834	10083	6	amidxtape	Amanda Tape Indexing amanda.org
44835	10115	6	ganymede-endpt	ganymede.com
44836	10115	17	ganymede-endpt	ganymede.com
44837	10128	6	bmc-perf-sd	bmc.com
44838	10128	17	bmc-perf-sd	bmc.com
44839	10167	17	pod	Portal of Doom remote access backdoor
44840	10288	6	blocks	Blocks
44841	10288	17	blocks	Blocks
44842	10498	17	nbsp;	Mstream DDOS Communication UDP
44843	10520	6	acidshivers	Acid Shivers Trojan Horse
44844	10520	17	acidshivers	Acid Shivers Trojan Horse
44845	10607	6	coma	Coma Trojan Horse
44846	10607	17	coma	Coma Trojan Horse
44847	11000	6	irisa	datamedia.fr
44848	11000	17	irisa	datamedia.fr
44849	11000	6	sennaspy	Senna Spy Trojan Horse
44850	11001	6	metasys	jci.com
44851	11001	17	metasys	jci.com
44852	11111	6	vce	Viral Computing Enviroment all.net
44853	11111	17	vce	Viral Computing Enviroment all.net
44854	11223	6	projenic	Projenic Trojan Horse
44855	11367	6	atm-uhas	attachmate.com
44856	11367	17	atm-uhas	attachmate.com
44857	11371	6	pgp5	PGP 5 Keyserver
44858	11371	17	pgp5	PGP 5 Keyserver
44859	11720	6	h323callsigalt	H323 Call Signal Alternate cisco.com
44860	11720	17	h323callsigalt	H323 Call Signal Alternate cisco.com
44861	12000	6	entextxid	IBM Enterprise Exteneder SNA XID Exchnage ibm.com
44862	12000	17	entextxid	IBM Enterprise Exteneder SNA XID Exchnage ibm.com
44863	12001	6	entextnetwork	IBM Enterprise Exteneder SNA COS Network Priority ibm.com
44864	12001	17	entextnetwork	IBM Enterprise Exteneder SNA COS Network Priority ibm.com
44865	12002	6	entexthigh	IBM Enterprise Exteneder SNA COS High Priority ibm.com
44866	12002	17	entexthigh	IBM Enterprise Exteneder SNA COS High Priority ibm.com
44867	12003	6	entextmed	IBM Enterprise Exteneder SNA COS Medium Priority ibm.com
44868	12003	17	entextmed	IBM Enterprise Exteneder SNA COS Medium Priority ibm.com
44869	12004	6	entextlow	IBM Enterprise Exteneder SNA COS Low Priority ibm.com
44870	12004	17	entextlow	IBM Enterprise Exteneder SNA COS Low Priority ibm.com
44871	12076	6	gjammer	GJamer Trojan Horse
44872	12172	6	hivep	HiveP skenbe.net
44873	12172	17	hivep	HiveP skenbe.net
44874	12223	6	hack99	kack99 Trojan Horse
44875	12223	6	keylogger	KeyLogger Trojan Horse
44876	12345	6	NetBus	Gabanbus, X-bill, NetBus Backdoor Trojan
44877	12346	6	NetBus	NetBus Backdoor Trojan
44878	12361	6	whackamole	Whack a Mole Trojan Horse
44879	12362	6	whackamole	Whack a Mole Trojan Horse
44880	12631	6	whackjob	Whack Job Trojan Horse
44881	12753	6	tsaf	tsaf port
44882	12753	17	tsaf	tsaf port
44883	12754	6	nbsp;	Mstream DDOS communication TCP
44884	13000	6	sennaspy	Senna Spy Trojan Horse
44885	13000	17	sennaspy	Senna Spy Trojan Horse
44886	13160	6	i-zipqd	quarterdeck.com
44887	13160	17	i-zipqd	quarterdeck.com
44888	13223	6	popwow	PowWow by Tribal Voice
44889	13223	17	popwow	PowWow by Tribal Voice
44890	13224	6	popwow	PowWow by Tribal Voice
44891	13224	17	popwow	PowWow by Tribal Voice
44892	13326	6	nbsp;	Crossfire game
44893	13720	6	bprd	BPRD protocol (Veritas NetBackup) veritas.com
44894	13720	17	bprd	BPRD protocol (Veritas NetBackup) veritas.com
44895	13721	6	bpbm	BPBEM protocol (Veritas NetBackup) veritas.com
44896	13721	17	bpbm	BPBEM protocol (Veritas NetBackup) veritas.com
44897	13722	6	bjava-msvc	BP Java MSVC protocol veritas.com
44898	13722	17	bjava-msvc	BP Java MSVC protocol veritas.com
44899	13782	6	bpcd	Veritas NetBackup veritas.com
44900	13782	17	bpcd	Veritas NetBackup veritas.com
44901	13783	6	vopied	VOPIED Protocol veritas.com
44902	13783	17	vopied	VOPIED Protocol veritas.com
44903	13818	6	dsmcc-config	DSMCC Config sciatl.com
44904	13818	17	dsmcc-config	DSMCC Config sciatl.com
44905	13819	6	dsmcc-session	DSMCC Session Message sciatl.com
44906	13819	17	dsmcc-session	DSMCC Session Message sciatl.com
44907	13820	6	dsmcc-passthru	DSMCC Pass-Thru Message sciatl.com
44908	13820	17	dsmcc-passthru	DSMCC Pass-Thru Message sciatl.com
44909	13821	6	dsmcc-download	DSMCC Download Protocol sciatl.com
44910	13821	17	dsmcc-download	DSMCC Download Protocol sciatl.com
44911	13822	6	dsmcc-ccp	DSMCC Channel Change Protocol sciatl.com
44912	13822	17	dsmcc-ccp	DSMCC Channel Change Protocol sciatl.com
44913	14001	6	itu-sccp-ss7	ericsson.com
44914	14001	17	itu-sccp-ss7	ericsson.com
44915	14237	6	palm	Palm HotSync
44916	14237	17	palm	Palm HotSync
44917	14238	6	palm	Palm HotSync
44918	14238	17	palm	Palm HotSync
44919	15104	6	nbsp;	Mstream DDOS communication TCP
44920	16360	6	netserialext1	aquilagroup.com
44921	16360	17	netserialext1	aquilagroup.com
44922	16361	6	netserialext2	aquilagroup.com
44923	16361	17	netserialext2	aquilagroup.com
44924	16367	6	netserialext3	aquilagroup.com
44925	16367	17	netserialext3	aquilagroup.com
44926	16368	6	netserialext4	aquilagroup.com
44927	16368	17	netserialext4	aquilagroup.com
44928	16660	6	stacheldraht	Stacheldraht distributed attack tool client --> handler
44929	16959	6	subseven	Subseven DEFCON8 2.1 backdoor remote access tool
44930	16969	6	priority	Priority Trojan Horse
44931	16991	6	intel-rci-mp	intel.com
44932	16991	17	intel-rci-mp	intel.com
44933	17007	6	isode-dua	nbsp;
44934	17007	17	isode-dua	nbsp;
44935	17219	6	chipper	achipper.nl
44936	17219	17	chipper	achipper.nl
44937	17300	6	kuang2	Kuang2 Trojan Virus
44938	17300	17	kuang2	Kuang2 Trojan Virus
44939	18000	6	biimenu	Beckman Instrumnets Inc beckman.com
44940	18000	17	biimenu	Beckman Instrumnets Inc beckman.com
44941	18181	6	opsec-cvp	checkpoint.com
44942	18181	17	opsec-cvp	checkpoint.com
44943	18182	6	opsec-ufp	checkpoint.com
44944	18182	17	opsec-ufp	checkpoint.com
44945	18183	6	opsec-sam	checkpoint.com
44946	18183	17	opsec-sam	checkpoint.com
44947	18184	6	opsec-lea	checkpoint.com
44948	18184	17	opsec-lea	checkpoint.com
44949	18185	6	opsec-omi	checkpoint.com
44950	18185	17	opsec-omi	checkpoint.com
44951	18187	6	opsec-ela	checkpoint.com
44952	18187	17	opsec-ela	checkpoint.com
44953	18487	6	ac-cluster	cup.hp.com
44954	18487	17	ac-cluster	cup.hp.com
44955	18753	6	shaft	Shaft distributed attack tool handler --> agent
44956	18753	17	shaft	Shaft distributed attack tool handler --> agent
44957	18888	6	apc-necmp	astralpoint.com
44958	18888	17	apc-necmp	astralpoint.com
44959	18888	6	liquidaudio	Liquid Audio Server
44960	18888	17	liquidaudio	Liquid Audio Server
44961	19283	6	keysrvr	Key Server sassafras.com
44962	19283	17	keysrvr	Key Server sassafras.com
44963	19315	6	keyshadow	Key Shadow sassafras.com
44964	19315	17	keyshadow	Key Shadow sassafras.com
44965	19410	6	hp-sco	cup.hp.com
44966	19410	17	hp-sco	cup.hp.com
44967	19411	6	hp-sca	cup.hp.com
44968	19411	17	hp-sca	cup.hp.com
44969	19412	6	hp-sessmon	cup.hp.com
44970	19412	17	hp-sessmon	cup.hp.com
44971	19541	6	jcp	JCP Clinet jci.co.jp
44972	19541	17	jcp	JCP Clinet jci.co.jp
44973	20000	6	dnp	acsatlanta.com
44974	20000	17	dnp	acsatlanta.com
44975	20000	6	millennium	Millennium Trojan Horse
44976	20001	6	millennium	Millennium Trojan Horse
44977	20005	6	btx	xcept4 (Interacts with German Telekoms CEPT videotext service)
44978	20034	6	netbusn	NetBus II (!!! trojan)
44979	20432	6	shaft	Shaft distributed attack client --> handler
44980	20432	17	shaft	Shaft distributed attack agent --> handler
44981	20670	6	track	nawcad.navy.mil
44982	20670	17	track	nawcad.navy.mil
44983	20999	6	athand-mmp	At Hand MMP hand.com
44984	20999	17	athand-mmp	At Hand MMP hand.com
44985	21157	17	activision	Activision gaming protocol (UDP)
44986	21544	6	girlf	GirlFriend Trojan Horse
44987	21554	6	girlf	GirlFriend Trojan Horse
44988	21590	6	vofr-gateway	tollbridgetech.com
44989	21590	17	vofr-gateway	tollbridgetech.com
44990	21845	6	webphone	webphona netspeak.com
44991	21845	17	webphone	webphona netspeak.com
44992	21846	6	netspeak-is	Directory Service netspeak.com
44993	21846	17	netspeak-is	Directory Service netspeak.com
44994	21847	6	netspeak-cs	Connection Service netspeak.com
44995	21847	17	netspeak-cs	Connection Service netspeak.com
44996	21848	6	netspeak-acd	Automatic Call Distribution netspeak.com
44997	21848	17	netspeak-acd	Automatic Call Distribution netspeak.com
44998	21849	6	netspeak-cps	Credit Processing System netspeak.com
44999	21849	17	netspeak-cps	Credit Processing System netspeak.com
45000	22000	6	snapenetio	SNAPenetIO opto22.com
45001	22000	17	snapenetio	SNAPenetIO opto22.com
45002	22001	6	optocontrol	OptoControl opto22.com
45003	22001	17	optocontrol	OptoControl opto22.com
45004	22222	6	prosiak	Prosiak Trojan Horse
45005	22273	6	wnn6	Wnn6 (Japanese Input) omronsoft.co.jp
45006	22289	6	wnn6_Cn	Wnn6 (Chinese Input)
45007	22305	6	wnn6_Kr	Wnn6 (Korean Input)
45008	22321	6	wnn6_Tw	Wnn6 (Taiwanese Input)
45009	22555	6	vocaltec-wconf	Vocaltec Web Conference Internet Phone vocaltec.com
45010	22555	17	vocaltec-wconf	Vocaltec Web Conference Internet Phone vocaltec.com
45011	22800	6	aws-brf	Telerate Information Platform LAN dowjones.com
45012	22800	17	aws-brf	Telerate Information Platform LAN dowjones.com
45013	22951	6	brf-gw	Telerate Information Platform WAN dowjones.com
45014	22951	17	brf-gw	Telerate Information Platform WAN dowjones.com
45015	23213	6	powwow	PowWow by Tribal Voice
45016	23214	6	powwow	PowWow by Tribal Voice
45017	23456	6	evilftp	Evil FTP or WhackJob Trojan Horse
45018	24000	6	med-ltp	hp.com
45019	24000	17	med-ltp	hp.com
45020	24001	6	med-fsp-rx	hp.com
45021	24001	17	med-fsp-rx	hp.com
45022	24002	6	med-fsp-tx	hp.com
45023	24002	17	med-fsp-tx	hp.com
45024	24003	6	med-supp	hp.com
45025	24003	17	med-supp	hp.com
45026	24004	6	med-ovw	hp.com
45027	24004	17	med-ovw	hp.com
45028	24005	6	med-ci	hp.com
45029	24005	17	med-ci	hp.com
45030	24006	6	med-net-svc	hp.com
45031	24006	17	med-net-svc	hp.com
45032	24386	6	intel_rci	intel.com
45033	24386	17	intel_rci	intel.com
45034	24554	6	blickp	ritlabs.com
45035	24554	17	blickp	ritlabs.com
45036	25000	6	icl-twobase1	icl.co.uk
45037	25000	17	icl-twobase1	icl.co.uk
45038	25001	6	icl-twobase2	icl.co.uk
45039	25001	17	icl-twobase2	icl.co.uk
45040	25002	6	icl-twobase3	icl.co.uk
45041	25002	17	icl-twobase3	icl.co.uk
45042	25003	6	icl-twobase4	icl.co.uk
45043	25003	17	icl-twobase4	icl.co.uk
45044	25004	6	icl-twobase5	icl.co.uk
45045	25004	17	icl-twobase5	icl.co.uk
45046	25005	6	icl-twobase6	icl.co.uk
45047	25005	17	icl-twobase6	icl.co.uk
45048	25006	6	icl-twobase7	icl.co.uk
45049	25006	17	icl-twobase7	icl.co.uk
45050	25007	6	icl-twobase8	icl.co.uk
45051	25007	17	icl-twobase8	icl.co.uk
45052	25008	6	icl-twobase9	icl.co.uk
45053	25008	17	icl-twobase9	icl.co.uk
45054	25009	6	icl-twobase10	icl.co.uk
45055	25009	17	icl-twobase10	icl.co.uk
45056	25793	6	vocaltec-hos	Vocaltec Address Server vocaltec.com
45057	25793	17	vocaltec-hos	Vocaltec Address Server vocaltec.com
45058	26000	6	quake	Quake-based games (e.g. Half-Life, Quakeworld, QuakeIII, etc.)
45059	26000	17	quake	Quake-based games (e.g. Half-Life, Quakeworld, QuakeIII, etc.)
45060	26208	6	wnn6_Ds	Wnn6 (Dserver) omronsoft.co.jp
45061	26208	17	wnn6_Ds	Wnn6 (Dserver) omronsoft.co.jp
45062	26274	17	deltasource	Delta Source Trojan Horse
45063	27001	6	quakew	Quake World
45064	27001	17	quakew	Quake World
45065	27010	6	halflife	Half-Life Game
45066	27010	17	halflife	Half-Life Game
45067	27015	6	halflife	Half-Life Game
45068	27015	17	halflife	Half-Life Game
45069	27374	6	ramen	Linux.Ramen.Worm attacks RedHat Linux
45070	27374	17	ramen	Linux.Ramen.Worm attacks RedHat Linux
45071	27444	17	trinoo_bcast	Trinoo distributed attack tool Master -> Bcast Daemon communication
45072	27665	6	trinoo_master	Trinoo distributed attack tool Master server control port
45073	27960	17	q3	Quake3 server
45074	27999	6	tw-auth-key	TW Authenication Key Distribution and Attribute Certificate Services sse.ie
45075	27999	17	tw-auth-key	TW Authenication Key Distribution and Attribute Certificate Services sse.ie
45076	29891	17	theunexplained	The Unexplained Trojan Horse
45077	30029	6	aoladmin	AOL Admin 1.1
45078	30100	6	netsphere	Netsphere Remote Access Trojan (Win 9x)
45079	30102	6	netsphere	Netsphere Remote Access Trojan (Win 9x)
45080	30129	6	netsphere	Masters Paradise Trojan
45081	30303	6	socketdetroie	Socket de Troie Trojan Horse
45082	30999	6	kuang	Kuang Trojan
45083	31335	17	trinoo_register	Trinoo distributed attack tool Bcast Daemon registration port
45084	31337	6	Elite	Sometimes interseting stuff found on this port
45085	31337	17	orifice	Back orifice and NetBus Trogan Horse Programs
45086	31338	17	deepbo	Deep bo Trick Trojan Horse
45087	31339	6	netspy	NetSpy Trojan Horse
45088	31339	17	netspy	NetSpy Trojan Horse
45089	31666	6	bowhack	BoWhack Trojan Horse
45090	31785	6	hack-a-tack	Hack-A-Tack Remote Access Trojan (Win 9x)
45091	31787	6	hack-a-tack	Hack-A-Tack Remote Access Trojan (Win 9x)
45092	31789	6	hack-a-tack	Hack-A-Tack Remote Access Trojan (Win 9x)
45093	31789	17	hack-a-tack	Hack-A-Tack Remote Access Trojan (Win 9x)
45094	31790	6	hack-a-tack	Hack-A-Tack Remote Access Trojan (Win 9x)
45095	31790	17	hack-a-tack	Hack-A-Tack Remote Access Trojan (Win 9x)
45096	31791	6	hack-a-tack	Hack-A-Tack Remote Access Trojan (Win 9x)
45097	31791	17	hack-a-tack	Hack-A-Tack Remote Access Trojan (Win 9x)
45098	32000	6	nbsp;	Artisoft XtraMail v1.11
45099	32768	6	filenet-tms	filenet.com
45100	32768	17	filenet-tms	filenet.com
45101	32769	6	filenet-rpc	filenet.com
45102	32769	17	filenet-rpc	filenet.com
45103	32770	6	filenet-nch	filenet.com
45104	32770	17	filenet-nch	filenet.com
45105	32773	6	rpcttd	Sun puts RPC services in this region
45106	32773	17	rpcttd	Sun puts RPC services in this region
45107	32776	6	rpcspray	Sun puts RPC services in this region
45108	32776	17	rpcspray	Sun puts RPC services in this region
45109	32779	6	rpccmds	Sun puts RPC services in this region
45110	32779	17	rpccmds	Sun puts RPC services in this region
45111	33270	17	trinity	Trinity v3 distributed attack tool
45112	33333	6	prosiak	Prosiak Trojan Horse
45113	33434	6	traceroute	traceroute use iana.org
45114	33434	17	traceroute	traceroute use iana.org
45115	34324	6	biggluck,tn	Biggluck & TN or Tiny Telnet Server Trojan Horses
45116	34324	17	biggluck,tn	Biggluck & TN or Tiny Telnet Server Trojan Horses
45117	34555	17	wintrinoo	Trinoo distributed attack tool Handler to/from agent
45118	36794	6	bugbear	Bugbear Email Worm/Trojan
45119	36794	17	bugbear	Bugbear Email Worm/Trojan
45120	36865	6	kastenxpipe	kastenchase.com
45121	36865	17	kastenxpipe	kastenchase.com
45122	38036	6	timestep	Timestep VPN from Saytek
45123	38036	17	timestep	Timestep VPN from Saytek
45124	40193	6	novellbug	Novell servers can be crashed by sending random data to this port.
45125	40193	17	novellbug	Novell servers can be crashed by sending random data to this port.
45126	40412	6	thespy	The Spy Trojan Horse
45127	40412	17	thespy	The Spy Trojan Horse
45128	40421	6	paradise	Masters Paradise Trojan Horse
45129	40422	6	paradise	Masters Paradise Trojan Horse
45130	40423	6	paradise	Masters Paradise Trojan Horse
45131	40425	6	paradise	Masters Paradise Trojan Horse
45132	40426	6	paradise	Masters Paradise Trojan Horse
45133	40841	6	cscp	centerspan.com
45134	40841	17	cscp	centerspan.com
45135	41524	6	arcedis	Arcserver Discovery
45136	41524	17	arcedis	Arcserver Discovery
45137	41525	17	casdscsvc.exe	Computer Associates BrighStor Enterprise Backup
45138	43188	6	reachout	Reach Out
45139	44818	6	rockwell-encap	Rockwell Encapsulation rockwell.com
45140	44818	17	rockwell-encap	Rockwell Encapsulation rockwell.com
45141	45000	6	cisconet	RCisco SAFE IDS /NetRanger postofficed
45142	45000	17	cisconet	RCisco SAFE IDS /NetRanger postofficed
45143	45678	6	eba	EBA Prise eba.net
45144	45678	17	eba	EBA Prise eba.net
45145	45966	6	ssr-servermgr	geac.com
45146	45966	17	ssr-servermgr	geac.com
45147	47262	17	deltasource	Delta Source Trojan Horse
45148	47557	6	dbbrowse	Databeam Corporation databeam.com
45149	47557	17	dbbrowse	Databeam Corporation databeam.com
45150	47624	6	directplaysrvr	Direct Play Server microsoft.com
45151	47624	17	directplaysrvr	Direct Play Server microsoft.com
45152	47806	6	ap	ALC Protocol automatedlogic.com
45153	47806	17	ap	ALC Protocol automatedlogic.com
45154	47808	6	bacnet	Building Automation and Control Networks cornell.edu
45155	47808	17	bacnet	Building Automation and Control Networks cornell.edu
45156	48000	6	nimcontroller	Nimbus Controller nimsoft.no
45157	48000	17	nimcontroller	Nimbus Controller nimsoft.no
45158	48001	6	nimspooler	Nimbus Spooler nimsoft.no
45159	48001	17	nimspooler	Nimbus Spooler nimsoft.no
45160	48002	6	nimhub	Nimbus Hub nimsoft.no
45161	48002	17	nimhub	Nimbus Hub nimsoft.no
45162	48003	6	nimgtw	Nimbus Gateway nimsoft.no
45163	48003	17	nimgtw	Nimbus Gateway nimsoft.no
45164	50505	6	sockdetrois	Sockets de Trois V2 Trojan Horse
45165	50766	6	fore	Fore or Schwindler Trojan Horse
45166	50766	17	fore	Fore or Schwindler Trojan Horse
45167	53001	6	remoteshut	Remote Shutdown Trojan Horse
45172	65000	6	devil	Devil Trojan, Stacheldraht distributed attack tool Handler to/from agent
45173	65301	6	pcanywhere	Used sometimes by PCAnywhere
\.


--
-- TOC entry 3081 (class 0 OID 4630999)
-- Dependencies: 2007
-- Data for Name: billservice_prepaidtraffic; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_prepaidtraffic (id, traffic_transmit_service_id, size, group_id) FROM stdin;
\.


--
-- TOC entry 3115 (class 0 OID 4632564)
-- Dependencies: 2077
-- Data for Name: billservice_radiusattrs; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_radiusattrs (id, tarif_id, vendor, attrid, value) FROM stdin;
\.


--
-- TOC entry 3082 (class 0 OID 4631005)
-- Dependencies: 2009
-- Data for Name: billservice_salecard; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_salecard (id, dealer_id, sum_for_pay, paydeffer, discount, discount_sum, prepayment, created) FROM stdin;
\.


--
-- TOC entry 3083 (class 0 OID 4631008)
-- Dependencies: 2010
-- Data for Name: billservice_salecard_cards; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_salecard_cards (id, salecard_id, card_id) FROM stdin;
\.


--
-- TOC entry 3084 (class 0 OID 4631015)
-- Dependencies: 2013
-- Data for Name: billservice_settlementperiod; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_settlementperiod (id, name, time_start, length, length_in, autostart) FROM stdin;
1	+Месяц	2009-08-29 17:20:04.50	0	MONTH	t
\.


--
-- TOC entry 3085 (class 0 OID 4631025)
-- Dependencies: 2015
-- Data for Name: billservice_shedulelog; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY billservice_shedulelog (id, account_id, ballance_checkout, prepaid_traffic_reset, prepaid_traffic_accrued, prepaid_time_reset, prepaid_time_accrued, balance_blocked, accounttarif_id) FROM stdin;
\.


--
-- TOC entry 3086 (class 0 OID 4631030)
-- Dependencies: 2017
-- Data for Name: billservice_speedlimit; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_speedlimit (id, limit_id, max_tx, max_rx, burst_tx, burst_rx, burst_treshold_tx, burst_treshold_rx, burst_time_tx, burst_time_rx, min_tx, min_rx, priority, speed_units, change_speed_type) FROM stdin;
\.


--
-- TOC entry 3087 (class 0 OID 4631035)
-- Dependencies: 2019
-- Data for Name: billservice_suspendedperiod; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_suspendedperiod (id, account_id, start_date, end_date) FROM stdin;
\.


--
-- TOC entry 3088 (class 0 OID 4631040)
-- Dependencies: 2021
-- Data for Name: billservice_systemuser; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_systemuser (id, username, password, last_ip, last_login, description, created, status, host, role) FROM stdin;
1	admin	21232f297a57a5a743894a0e4a801fc3	\N	2008-08-21 14:28:22.10	Default admin account	\N	t	0.0.0.0/0	0
2	webadmin	d316aa00ff0c50b26f09cdebe3177769	\N	\N		\N	t	0.0.0.0/0	0
\.


--
-- TOC entry 3089 (class 0 OID 4631054)
-- Dependencies: 2024
-- Data for Name: billservice_template; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_template (id, name, type_id, body) FROM stdin;
4	Акт выполненных работ	4	Акт выполненных работ
5	Счет фактура	3	Счет фактура
6	Договор на подключение юр. лиц	2	<html>\n            <head>\n            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />\n            </head>\n            <body>\n            Имя: ${account.username}  <br>\n${organization.name} \n${bank.bankcode} \n            </body>\n            </html>
7	Кассовый чек	5	<html>\n <head>\n <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n <style>\n   td{\n        FONT: 9px Times New Roman;\n    }\n    h1{\n        FONT: 9px Arial;\n    }\n  </style>\n </head>\n <body>\n  <table align=center width="85%">\n    <tr>\n     <td>\n       <h1 align=center> <b> Квитанция об оплате услуг № ${transaction_id} </b> </h1>\n       <strong>Абонент:</strong> ${account.fullname} <br>\n       <strong>Тарифный план:</strong> ${tarif.name} <br>\n       <strong>Логин:</strong> ${account.username}<br>\n       <strong>Сумма:</strong> ${sum}<br>\n       <strong>Дата приема платежа:</strong> ${created}<br>\n    </td>\n   </tr>\n  </table>\n </body>\n</html>\n
2	Договор	1	<html>\n            <head>\n            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />\n            </head>\n            <body>\n${account.id}<br />\n${account.username}<br />\n${account.password}<br />\n${account.fullname}<br />\n${account.email}<br />\n${account.address}<br />\n${account.nas_id}<br />\n${account.vpn_ip_address}<br />\n${account.assign_ipn_ip_from_dhcp}<br />\n${account.ipn_ip_address}<br />\n${account.ipn_mac_address}<br />\n${account.ipn_status}<br />\n${account.status}<br />\n${account.suspended}<br />\n${account.created}<br />\n${account.ballance}<br />\n${account.credit}<br />\n${account.disabled_by_limit}<br />\n${account.balance_blocked}<br />\n${account.ipn_speed}<br />\n${account.vpn_speed}<br />\n${account.netmask}<br />\n${account.ipn_added}<br />\n${account.city}<br />\n${account.postcode}<br />\n${account.region}<br />\n${account.street}<br />\n${account.house}<br />\n${account.house_bulk}<br />\n${account.entrance}<br />\n${account.room}<br />\n${account.vlan}<br />\n${account.allow_webcab}<br />\n${account.allow_expresscards}<br />\n${account.assign_dhcp_null}<br />\n${account.assign_dhcp_block}<br />\n${account.allow_vpn_null}<br />\n${account.allow_vpn_block}<br />\n${account.passport}<br />\n${account.passport_date}<br />\n${account.passport_given}<br />\n\n${tarif.name}<br />\n\n\n${created}<br />\n            \n            \n            \n            </body>\n            </html>\n
8	Накладная на карты экспресс-оплаты	6	<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"\n"http://www.w3.org/TR/html4/loose.dtd">\n<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n</head>\n\n<body>\n<div style="width:100%; "> \n<div style="float:right ">\n<span style="font-weight:bold; ">Дилер</span><br>\t\t\nОрганизация: ${dealer.organization}<br>\t\nДиректор: ${dealer.director}<br>\t\nЮр адрес: ${dealer.uraddress}<br>\t\nр/с: ${dealer.rs}<br>\t\nУНН: ${dealer.unp}<br>\t\nОКПО: ${dealer.okpo}<br>\t\nБанк: ${dealer.bank}, код ${dealer.bankcode}<br>\t\n</div>\n\n<div style="float:left ">\n\t<span style="font-weight:bold; ">Оператор</span><br>\t\n\tОрганизация: ${operator.organization}<br>\t\n\tДиректор: ${operator.director}<br>\t\n\tЮр адрес: ${operator.uraddress}<br>\n  р/с: ${operator.rs}\t<br>\t\n\tУНН: ${operator.unp}<br>\t\n\tОКПО: ${operator.okpo}<br>\t\n\tБанк: ${operator.bank}, Код ${operator.bankcode}<br>\t\n</div>\n</div>\n\n<div style="font-weight:bold; float:left; width:100%; text-align:center; margin-bottom:20px; margin-top:20px; ">Накладная от ${created}</div>\n\n<div style="clear:both "></div>\n<table border="1" align="center" style="width:100%">\n\t<tr>\n\t\t<td>ID карты</td>\n\t\t<td>Серия</td>\n\t\t<td>Номинал</td>\n\t\t<td>Активировать С</td>\n\t\t<td>Активировать По</td>\n\t</tr>\n\t\n\t% for card in cards:\n\t<tr>\n\t   <td>${card.id}</td>\n\t   <td>${card.series}</td>\n\t   <td>${card.nominal}</td>\n\t   <td>${card.start_date}</td>\n\t   <td>${card.end_date}</td>\n\t</tr>\n\t% endfor\n</table>\n\nИтого ${cardcount} карт на сумму: ${sum_for_pay}<br>\t\nСкидка: ${discount} на сумму ${discount_sum}<br>\t\nОплачено: ${pay}<br>\t\nОплатить до:${paydeffer}\n\n</body>\n</html>
9	Шаблон карты экспресс-оплаты	7	<div style="position:relative; display:block; width:255px; height:143px; font-face:Arial;">\n<img src="img/card_blue.gif" style="border:none;">\n\t<div style="position:absolute; display:block; top:60px; left:16px; font-size:32px;">${card.nominal}</div>\n\t<div style="position:absolute; display:block; top:96px; left:3px; font-size:10px;">PIN: ${card.pin}</div>\n\t<div style="position:absolute; display:block; top:96px; left:175px; font-size:10px;">Серия: ${card.series}</div>\n\t<div style="position:absolute; display:block; top:118px; left:3px; font-size:6px;">Активировать c ${card.start_date} по ${card.end_date} </div>\n\t<div style="position:absolute; display:block; top:128px; left:3px; font-size:6px;">${operator.organization}. Тел. ${operator.phone}</div>\n</div>\n
\.


--
-- TOC entry 3090 (class 0 OID 4631062)
-- Dependencies: 2026
-- Data for Name: billservice_timeaccessnode; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_timeaccessnode (id, time_access_service_id, time_period_id, cost) FROM stdin;
\.


--
-- TOC entry 3091 (class 0 OID 4631068)
-- Dependencies: 2028
-- Data for Name: billservice_timeaccessservice; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_timeaccessservice (id, prepaid_time, reset_time) FROM stdin;
\.


--
-- TOC entry 3092 (class 0 OID 4631075)
-- Dependencies: 2030
-- Data for Name: billservice_timeperiod; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_timeperiod (id, name) FROM stdin;
1	Круглосуточно
2	Понедельник
3	Вторник
4	Рабочая неделя
5	Weekend
\.


--
-- TOC entry 3093 (class 0 OID 4631080)
-- Dependencies: 2032
-- Data for Name: billservice_timeperiod_time_period_nodes; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_timeperiod_time_period_nodes (id, timeperiod_id, timeperiodnode_id) FROM stdin;
1	1	1
4	4	4
5	4	5
6	4	6
7	4	7
8	4	8
9	5	9
10	5	10
\.


--
-- TOC entry 3094 (class 0 OID 4631085)
-- Dependencies: 2034
-- Data for Name: billservice_timeperiodnode; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_timeperiodnode (id, name, time_start, length, repeat_after) FROM stdin;
4	Понедельник	2008-01-07 00:00:00	86400	WEEK
6	Среда	2008-01-09 00:00:00	86400	WEEK
5	Вторник	2008-01-08 00:00:00	86400	WEEK
7	Четверг	2008-01-10 00:00:00	86400	WEEK
8	Пятница	2008-01-11 00:00:00	86400	WEEK
10	Воскресенье	2008-01-13 00:00:00	86400	WEEK
1	Сутки	2008-01-01 00:00:00	86400	DAY
9	Суббота	2008-01-12 00:00:00	86400	WEEK
\.


--
-- TOC entry 3095 (class 0 OID 4631095)
-- Dependencies: 2036
-- Data for Name: billservice_timespeed; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_timespeed (id, access_parameters_id, time_id, max_limit, min_limit, burst_limit, burst_treshold, burst_time, priority) FROM stdin;
\.


--
-- TOC entry 3113 (class 0 OID 4632062)
-- Dependencies: 2073
-- Data for Name: billservice_timetransaction; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_timetransaction (id, timeaccessservice_id, account_id, accounttarif_id, summ, datetime) FROM stdin;
\.


--
-- TOC entry 3114 (class 0 OID 4632150)
-- Dependencies: 2075
-- Data for Name: billservice_tpchangerule; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_tpchangerule (id, from_tariff_id, to_tariff_id, disabled, cost, ballance_min, settlement_period_id) FROM stdin;
\.


--
-- TOC entry 3096 (class 0 OID 4631106)
-- Dependencies: 2038
-- Data for Name: billservice_trafficlimit; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_trafficlimit (id, tarif_id, name, settlement_period_id, size, mode, group_id, action) FROM stdin;
\.


--
-- TOC entry 3097 (class 0 OID 4631111)
-- Dependencies: 2040
-- Data for Name: billservice_trafficlimit_traffic_class; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_trafficlimit_traffic_class (id, trafficlimit_id, trafficclass_id) FROM stdin;
\.


--
-- TOC entry 3112 (class 0 OID 4632039)
-- Dependencies: 2071
-- Data for Name: billservice_traffictransaction; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_traffictransaction (id, traffictransmitservice_id, account_id, accounttarif_id, summ, datetime) FROM stdin;
\.


--
-- TOC entry 3098 (class 0 OID 4631116)
-- Dependencies: 2042
-- Data for Name: billservice_traffictransmitnodes; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_traffictransmitnodes (id, traffic_transmit_service_id, cost, edge_start, edge_end, group_id) FROM stdin;
\.


--
-- TOC entry 3099 (class 0 OID 4631124)
-- Dependencies: 2044
-- Data for Name: billservice_traffictransmitnodes_time_nodes; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_traffictransmitnodes_time_nodes (id, traffictransmitnodes_id, timeperiod_id) FROM stdin;
\.


--
-- TOC entry 3100 (class 0 OID 4631129)
-- Dependencies: 2046
-- Data for Name: billservice_traffictransmitnodes_traffic_class; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_traffictransmitnodes_traffic_class (id, traffictransmitnodes_id, trafficclass_id) FROM stdin;
\.


--
-- TOC entry 3101 (class 0 OID 4631134)
-- Dependencies: 2048
-- Data for Name: billservice_traffictransmitservice; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_traffictransmitservice (id, reset_traffic, cash_method, period_check) FROM stdin;
\.


--
-- TOC entry 3102 (class 0 OID 4631142)
-- Dependencies: 2050
-- Data for Name: billservice_transaction; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_transaction (id, bill, account_id, type_id, approved, tarif_id, summ, description, created, systemuser_id, promise, end_promise, promise_expired, accounttarif_id) FROM stdin;
\.


--
-- TOC entry 3103 (class 0 OID 4631150)
-- Dependencies: 2052
-- Data for Name: billservice_transactiontype; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_transactiontype (id, name, internal_name) FROM stdin;
1	Периодическая услуга со снятием денег в течении расчётного периода	PS_GRADUAL
2	Периодическая услуга со снятием денег в конце расчётного периода	PS_AT_END
3	периодическая услуга со снятием денег в начале расчётного периода	PS_AT_START
4	Снятие денег за время, проведённое в сети	TIME_ACCESS
5	Снятие денег за трафик	NETFLOW_BILL
6	Снятие денег до стоимости тарифного плана	END_PS_MONEY_RESET
7	Ручная проводка	MANUAL_TRANSACTION
8	Карта экспресс-оплаты	ACTIVATION_CARD
9	Разовая услуга	ONETIME_SERVICE
10	Оплата через ОСМП	OSMP_BILL
11	Списание средств за преждевременное отключение услуги абонентом	ADDONSERVICE_WYTE_PAY
13	Списание по подключаемой периодической услуге со снятием денег в течении периода	ADDONSERVICE_PERIODICAL_GRADUAL
14	Списание по подключаемой периодической услуге со снятием денег в начале периода	ADDONSERVICE_PERIODICAL_AT_START
15	Списание по подключаемой периодической услуге со снятием денег в конце периода	ADDONSERVICE_PERIODICAL_AT_END
17	Списание по разовой услуге за подключаемую услугу	ADDONSERVICE_ONETIME
18	Оплата по карте экспресс-оплаты	PAY_CARD
\.


--
-- TOC entry 3116 (class 0 OID 4632662)
-- Dependencies: 2079
-- Data for Name: billservice_x8021; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY billservice_x8021 (id, account_id, nas_id, port, typeauth, vlan_accept, vlan_reject, simpleauth) FROM stdin;
\.


--
-- TOC entry 3104 (class 0 OID 4631155)
-- Dependencies: 2054
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY django_admin_log (id, action_time, user_id, content_type_id, object_id, object_repr, action_flag, change_message) FROM stdin;
\.


--
-- TOC entry 3105 (class 0 OID 4631164)
-- Dependencies: 2056
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY django_content_type (id, name, app_label, model) FROM stdin;
1	permission	auth	permission
2	group	auth	group
3	user	auth	user
4	message	auth	message
5	content type	contenttypes	contenttype
6	session	sessions	session
7	site	sites	site
8	log entry	admin	logentry
9	session	radius	session
10	active session	radius	activesession
11	Сервер доступа	nas	nas
12	Класс трафика	nas	trafficclass
13	Направление трафика	nas	trafficnode
14	Нода временного периода	billservice	timeperiodnode
15	Временной период	billservice	timeperiod
16	Расчётный период	billservice	settlementperiod
17	Периодическая услуга	billservice	periodicalservice
18	История проводок по пер. услугам	billservice	periodicalservicehistory
19	Разовый платеж	billservice	onetimeservice
20	Доступ с учётом времени	billservice	timeaccessservice
21	Период доступа	billservice	timeaccessnode
22	Параметры доступа	billservice	accessparameters
23	настройка скорости	billservice	timespeed
24	Предоплаченный трафик	billservice	prepaidtraffic
25	Доступ с учётом трафика	billservice	traffictransmitservice
26	цена за направление	billservice	traffictransmitnodes
27	Предоплаченый трафик пользователя	billservice	accountprepaystrafic
28	Предоплаченное время пользователя	billservice	accountprepaystime
29	лимит трафика	billservice	trafficlimit
30	Тариф	billservice	tariff
31	Аккаунт	billservice	account
32	тип проводки	billservice	transactiontype
33	Проводка	billservice	transaction
34	привязка	billservice	accounttarif
35	скорости IPN клиентов	billservice	accountipnspeed
37	NetFlow статистика	billservice	netflowstream
38	Периодическая операция	billservice	shedulelog
39	one time service history	billservice	onetimeservicehistory
40	system user	billservice	systemuser
41	ports	billservice	ports
47	sale card	billservice	salecard
43	card	billservice	card
44	operator	billservice	operator
45	bank data	billservice	bankdata
46	dealer	billservice	dealer
48	dealer pay	billservice	dealerpay
49	organization	billservice	organization
50	document type	billservice	documenttype
51	template	billservice	template
52	document	billservice	document
53	suspended period	billservice	suspendedperiod
54	group	billservice	group
55	group stat	billservice	groupstat
56	speed limit	billservice	speedlimit
57	account speed limit	billservice	accountspeedlimit
58	ip pool	billservice	ippool
59	ip in use	billservice	ipinuse
\.


--
-- TOC entry 3106 (class 0 OID 4631169)
-- Dependencies: 2058
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY django_session (session_key, session_data, expire_date) FROM stdin;
\.


--
-- TOC entry 3107 (class 0 OID 4631175)
-- Dependencies: 2059
-- Data for Name: django_site; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY django_site (id, domain, name) FROM stdin;
1	example.com	example.com
\.


--
-- TOC entry 3108 (class 0 OID 4631181)
-- Dependencies: 2061
-- Data for Name: nas_nas; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY nas_nas (id, type, name, ipaddress, secret, login, password, allow_pptp, allow_pppoe, allow_ipn, user_add_action, user_enable_action, user_disable_action, user_delete_action, vpn_speed_action, ipn_speed_action, reset_action, confstring, multilink, identify) FROM stdin;
\.


--
-- TOC entry 3109 (class 0 OID 4631198)
-- Dependencies: 2063
-- Data for Name: nas_trafficclass; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY nas_trafficclass (id, name, weight, color, store, passthrough) FROM stdin;
\.


--
-- TOC entry 3110 (class 0 OID 4631206)
-- Dependencies: 2065
-- Data for Name: nas_trafficnode; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY nas_trafficnode (id, traffic_class_id, name, direction, protocol, src_ip, src_port, dst_ip, dst_port, next_hop) FROM stdin;
\.


--
-- TOC entry 3111 (class 0 OID 4631222)
-- Dependencies: 2067
-- Data for Name: radius_activesession; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY radius_activesession (id, account_id, sessionid, interrim_update, date_start, date_end, caller_id, called_id, nas_id, session_time, framed_protocol, bytes_in, bytes_out, session_status, speed_string, framed_ip_address, nas_int_id) FROM stdin;
\.


--
-- TOC entry 3049 (class 0 OID 4630711)
-- Dependencies: 1941
-- Data for Name: radius_session; Type: TABLE DATA; Schema: public; Owner: ebs
--

COPY radius_session (id, account_id, sessionid, interrim_update, date_start, date_end, caller_id, called_id, nas_id, session_time, framed_protocol, bytes_in, bytes_out, checkouted_by_time, checkouted_by_trafic, disconnect_status, framed_ip_address, transaction_id) FROM stdin;
\.


--
-- TOC entry 2636 (class 2606 OID 4631298)
-- Dependencies: 1942 1942
-- Name: auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- TOC entry 2640 (class 2606 OID 4631300)
-- Dependencies: 1944 1944 1944
-- Name: auth_group_permissions_group_id_key; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_key UNIQUE (group_id, permission_id);


--
-- TOC entry 2642 (class 2606 OID 4631302)
-- Dependencies: 1944 1944
-- Name: auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- TOC entry 2638 (class 2606 OID 4631304)
-- Dependencies: 1942 1942
-- Name: auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- TOC entry 2644 (class 2606 OID 4631306)
-- Dependencies: 1946 1946
-- Name: auth_message_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY auth_message
    ADD CONSTRAINT auth_message_pkey PRIMARY KEY (id);


--
-- TOC entry 2648 (class 2606 OID 4631308)
-- Dependencies: 1948 1948 1948
-- Name: auth_permission_content_type_id_key; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_key UNIQUE (content_type_id, codename);


--
-- TOC entry 2650 (class 2606 OID 4631310)
-- Dependencies: 1948 1948
-- Name: auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- TOC entry 2656 (class 2606 OID 4631312)
-- Dependencies: 1951 1951
-- Name: auth_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);


--
-- TOC entry 2658 (class 2606 OID 4631314)
-- Dependencies: 1951 1951 1951
-- Name: auth_user_groups_user_id_key; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_key UNIQUE (user_id, group_id);


--
-- TOC entry 2652 (class 2606 OID 4631316)
-- Dependencies: 1950 1950
-- Name: auth_user_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);


--
-- TOC entry 2660 (class 2606 OID 4631318)
-- Dependencies: 1954 1954
-- Name: auth_user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);


--
-- TOC entry 2662 (class 2606 OID 4631320)
-- Dependencies: 1954 1954 1954
-- Name: auth_user_user_permissions_user_id_key; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_key UNIQUE (user_id, permission_id);


--
-- TOC entry 2654 (class 2606 OID 4631322)
-- Dependencies: 1950 1950
-- Name: auth_user_username_key; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);


--
-- TOC entry 2665 (class 2606 OID 4631324)
-- Dependencies: 1956 1956
-- Name: billservice_accessparameters_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_accessparameters
    ADD CONSTRAINT billservice_accessparameters_pkey PRIMARY KEY (id);


--
-- TOC entry 2669 (class 2606 OID 4631326)
-- Dependencies: 1958 1958
-- Name: billservice_account_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_account
    ADD CONSTRAINT billservice_account_pkey PRIMARY KEY (id);


--
-- TOC entry 2671 (class 2606 OID 4631328)
-- Dependencies: 1958 1958
-- Name: billservice_account_username_key; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_account
    ADD CONSTRAINT billservice_account_username_key UNIQUE (username);


--
-- TOC entry 2902 (class 2606 OID 4632775)
-- Dependencies: 2085 2085
-- Name: billservice_accountaddonservice_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_accountaddonservice
    ADD CONSTRAINT billservice_accountaddonservice_pkey PRIMARY KEY (id);


--
-- TOC entry 2677 (class 2606 OID 4631330)
-- Dependencies: 1960 1960
-- Name: billservice_accountipnspeed_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_accountipnspeed
    ADD CONSTRAINT billservice_accountipnspeed_pkey PRIMARY KEY (id);


--
-- TOC entry 2680 (class 2606 OID 4631332)
-- Dependencies: 1962 1962
-- Name: billservice_accountprepaystime_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_accountprepaystime
    ADD CONSTRAINT billservice_accountprepaystime_pkey PRIMARY KEY (id);


--
-- TOC entry 2684 (class 2606 OID 4631334)
-- Dependencies: 1964 1964
-- Name: billservice_accountprepaystrafic_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_accountprepaystrafic
    ADD CONSTRAINT billservice_accountprepaystrafic_pkey PRIMARY KEY (id);


--
-- TOC entry 2688 (class 2606 OID 4631336)
-- Dependencies: 1966 1966
-- Name: billservice_accountspeedlimit_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_accountspeedlimit
    ADD CONSTRAINT billservice_accountspeedlimit_pkey PRIMARY KEY (id);


--
-- TOC entry 2691 (class 2606 OID 4631340)
-- Dependencies: 1968 1968 1968
-- Name: billservice_accounttarif_acc_dt_uq_key; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_accounttarif
    ADD CONSTRAINT billservice_accounttarif_acc_dt_uq_key UNIQUE (account_id, datetime);


--
-- TOC entry 2694 (class 2606 OID 4631338)
-- Dependencies: 1968 1968
-- Name: billservice_accounttarif_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_accounttarif
    ADD CONSTRAINT billservice_accounttarif_pkey PRIMARY KEY (id);


--
-- TOC entry 2891 (class 2606 OID 4632714)
-- Dependencies: 2081 2081
-- Name: billservice_addonservice_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_addonservice
    ADD CONSTRAINT billservice_addonservice_pkey PRIMARY KEY (id);


--
-- TOC entry 2897 (class 2606 OID 4632747)
-- Dependencies: 2083 2083
-- Name: billservice_addonservicetarif_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_addonservicetarif
    ADD CONSTRAINT billservice_addonservicetarif_pkey PRIMARY KEY (id);


--
-- TOC entry 2908 (class 2606 OID 4632799)
-- Dependencies: 2087 2087
-- Name: billservice_addonservicetransaction_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_addonservicetransaction
    ADD CONSTRAINT billservice_addonservicetransaction_pkey PRIMARY KEY (id);


--
-- TOC entry 2697 (class 2606 OID 4631342)
-- Dependencies: 1970 1970
-- Name: billservice_bankdata_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_bankdata
    ADD CONSTRAINT billservice_bankdata_pkey PRIMARY KEY (id);


--
-- TOC entry 2700 (class 2606 OID 4631344)
-- Dependencies: 1972 1972
-- Name: billservice_card_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_card
    ADD CONSTRAINT billservice_card_pkey PRIMARY KEY (id);


--
-- TOC entry 2705 (class 2606 OID 4631346)
-- Dependencies: 1974 1974
-- Name: billservice_dealer_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_dealer
    ADD CONSTRAINT billservice_dealer_pkey PRIMARY KEY (id);


--
-- TOC entry 2708 (class 2606 OID 4631348)
-- Dependencies: 1976 1976
-- Name: billservice_dealerpay_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_dealerpay
    ADD CONSTRAINT billservice_dealerpay_pkey PRIMARY KEY (id);


--
-- TOC entry 2712 (class 2606 OID 4631350)
-- Dependencies: 1978 1978
-- Name: billservice_document_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_document
    ADD CONSTRAINT billservice_document_pkey PRIMARY KEY (id);


--
-- TOC entry 2715 (class 2606 OID 4631352)
-- Dependencies: 1980 1980
-- Name: billservice_documenttype_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_documenttype
    ADD CONSTRAINT billservice_documenttype_pkey PRIMARY KEY (id);


--
-- TOC entry 2718 (class 2606 OID 4631354)
-- Dependencies: 1982 1982 1982
-- Name: billservice_globalstat_acc_dt_uq_key; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_globalstat
    ADD CONSTRAINT billservice_globalstat_acc_dt_uq_key UNIQUE (account_id, datetime);


--
-- TOC entry 2722 (class 2606 OID 4631356)
-- Dependencies: 1982 1982
-- Name: billservice_globalstat_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_globalstat
    ADD CONSTRAINT billservice_globalstat_pkey PRIMARY KEY (id);


--
-- TOC entry 2724 (class 2606 OID 4631358)
-- Dependencies: 1984 1984
-- Name: billservice_group_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_group
    ADD CONSTRAINT billservice_group_pkey PRIMARY KEY (id);


--
-- TOC entry 2726 (class 2606 OID 4631360)
-- Dependencies: 1986 1986 1986
-- Name: billservice_group_trafficclass_group_id_key; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_group_trafficclass
    ADD CONSTRAINT billservice_group_trafficclass_group_id_key UNIQUE (group_id, trafficclass_id);


--
-- TOC entry 2728 (class 2606 OID 4631362)
-- Dependencies: 1986 1986
-- Name: billservice_group_trafficclass_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_group_trafficclass
    ADD CONSTRAINT billservice_group_trafficclass_pkey PRIMARY KEY (id);


--
-- TOC entry 2609 (class 2606 OID 4631364)
-- Dependencies: 1937 1937 1937 1937
-- Name: billservice_groupstat_group_id_key; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_groupstat
    ADD CONSTRAINT billservice_groupstat_group_id_key UNIQUE (group_id, account_id, datetime);


--
-- TOC entry 2611 (class 2606 OID 4631366)
-- Dependencies: 1937 1937
-- Name: billservice_groupstat_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_groupstat
    ADD CONSTRAINT billservice_groupstat_pkey PRIMARY KEY (id);


--
-- TOC entry 2730 (class 2606 OID 4631368)
-- Dependencies: 1989 1989
-- Name: billservice_ipinuse_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_ipinuse
    ADD CONSTRAINT billservice_ipinuse_pkey PRIMARY KEY (id);


--
-- TOC entry 2735 (class 2606 OID 4631370)
-- Dependencies: 1991 1991
-- Name: billservice_ippool_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_ippool
    ADD CONSTRAINT billservice_ippool_pkey PRIMARY KEY (id);


--
-- TOC entry 2615 (class 2606 OID 4631372)
-- Dependencies: 1938 1938
-- Name: billservice_netflowstream_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_netflowstream
    ADD CONSTRAINT billservice_netflowstream_pkey PRIMARY KEY (id);


--
-- TOC entry 2737 (class 2606 OID 4631374)
-- Dependencies: 1994 1994
-- Name: billservice_onetimeservice_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_onetimeservice
    ADD CONSTRAINT billservice_onetimeservice_pkey PRIMARY KEY (id);


--
-- TOC entry 2742 (class 2606 OID 4631376)
-- Dependencies: 1996 1996
-- Name: billservice_onetimeservicehistory_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_onetimeservicehistory
    ADD CONSTRAINT billservice_onetimeservicehistory_pkey PRIMARY KEY (id);


--
-- TOC entry 2745 (class 2606 OID 4631378)
-- Dependencies: 1998 1998
-- Name: billservice_operator_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_operator
    ADD CONSTRAINT billservice_operator_pkey PRIMARY KEY (id);


--
-- TOC entry 2748 (class 2606 OID 4631380)
-- Dependencies: 2000 2000
-- Name: billservice_organization_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_organization
    ADD CONSTRAINT billservice_organization_pkey PRIMARY KEY (id);


--
-- TOC entry 2750 (class 2606 OID 4631382)
-- Dependencies: 2002 2002
-- Name: billservice_periodicalservice_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_periodicalservice
    ADD CONSTRAINT billservice_periodicalservice_pkey PRIMARY KEY (id);


--
-- TOC entry 2628 (class 2606 OID 4631384)
-- Dependencies: 1940 1940
-- Name: billservice_periodicalservicehistory_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_periodicalservicehistory
    ADD CONSTRAINT billservice_periodicalservicehistory_pkey PRIMARY KEY (id);


--
-- TOC entry 2754 (class 2606 OID 4631386)
-- Dependencies: 2005 2005
-- Name: billservice_ports_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_ports
    ADD CONSTRAINT billservice_ports_pkey PRIMARY KEY (id);


--
-- TOC entry 2756 (class 2606 OID 4631388)
-- Dependencies: 2007 2007
-- Name: billservice_prepaidtraffic_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_prepaidtraffic
    ADD CONSTRAINT billservice_prepaidtraffic_pkey PRIMARY KEY (id);


--
-- TOC entry 2883 (class 2606 OID 4632569)
-- Dependencies: 2077 2077
-- Name: billservice_radiusattrs_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_radiusattrs
    ADD CONSTRAINT billservice_radiusattrs_pkey PRIMARY KEY (id);


--
-- TOC entry 2763 (class 2606 OID 4631390)
-- Dependencies: 2010 2010
-- Name: billservice_salecard_cards_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_salecard_cards
    ADD CONSTRAINT billservice_salecard_cards_pkey PRIMARY KEY (id);


--
-- TOC entry 2765 (class 2606 OID 4631392)
-- Dependencies: 2010 2010 2010
-- Name: billservice_salecard_cards_salecard_id_key; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_salecard_cards
    ADD CONSTRAINT billservice_salecard_cards_salecard_id_key UNIQUE (salecard_id, card_id);


--
-- TOC entry 2761 (class 2606 OID 4631394)
-- Dependencies: 2009 2009
-- Name: billservice_salecard_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_salecard
    ADD CONSTRAINT billservice_salecard_pkey PRIMARY KEY (id);


--
-- TOC entry 2767 (class 2606 OID 4631396)
-- Dependencies: 2013 2013
-- Name: billservice_settlementperiod_name_key; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_settlementperiod
    ADD CONSTRAINT billservice_settlementperiod_name_key UNIQUE (name);


--
-- TOC entry 2769 (class 2606 OID 4631398)
-- Dependencies: 2013 2013
-- Name: billservice_settlementperiod_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_settlementperiod
    ADD CONSTRAINT billservice_settlementperiod_pkey PRIMARY KEY (id);


--
-- TOC entry 2771 (class 2606 OID 4631400)
-- Dependencies: 2015 2015
-- Name: billservice_shedulelog_account_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY billservice_shedulelog
    ADD CONSTRAINT billservice_shedulelog_account_id_key UNIQUE (account_id);


--
-- TOC entry 2773 (class 2606 OID 4631402)
-- Dependencies: 2015 2015
-- Name: billservice_shedulelog_accounttarif_id; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY billservice_shedulelog
    ADD CONSTRAINT billservice_shedulelog_accounttarif_id UNIQUE (accounttarif_id);


--
-- TOC entry 2775 (class 2606 OID 4631404)
-- Dependencies: 2015 2015
-- Name: billservice_shedulelog_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY billservice_shedulelog
    ADD CONSTRAINT billservice_shedulelog_pkey PRIMARY KEY (id);


--
-- TOC entry 2778 (class 2606 OID 4631406)
-- Dependencies: 2017 2017
-- Name: billservice_speedlimit_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_speedlimit
    ADD CONSTRAINT billservice_speedlimit_pkey PRIMARY KEY (id);


--
-- TOC entry 2781 (class 2606 OID 4631408)
-- Dependencies: 2019 2019
-- Name: billservice_suspendedperiod_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_suspendedperiod
    ADD CONSTRAINT billservice_suspendedperiod_pkey PRIMARY KEY (id);


--
-- TOC entry 2783 (class 2606 OID 4631410)
-- Dependencies: 2021 2021
-- Name: billservice_systemuser_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_systemuser
    ADD CONSTRAINT billservice_systemuser_pkey PRIMARY KEY (id);


--
-- TOC entry 2785 (class 2606 OID 4631412)
-- Dependencies: 2021 2021
-- Name: billservice_systemuser_username_key; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_systemuser
    ADD CONSTRAINT billservice_systemuser_username_key UNIQUE (username);


--
-- TOC entry 2621 (class 2606 OID 4631414)
-- Dependencies: 1939 1939
-- Name: billservice_tariff_name_key; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_tariff
    ADD CONSTRAINT billservice_tariff_name_key UNIQUE (name);


--
-- TOC entry 2623 (class 2606 OID 4631416)
-- Dependencies: 1939 1939
-- Name: billservice_tariff_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_tariff
    ADD CONSTRAINT billservice_tariff_pkey PRIMARY KEY (id);


--
-- TOC entry 2787 (class 2606 OID 4631418)
-- Dependencies: 2024 2024
-- Name: billservice_template_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_template
    ADD CONSTRAINT billservice_template_pkey PRIMARY KEY (id);


--
-- TOC entry 2790 (class 2606 OID 4631420)
-- Dependencies: 2026 2026
-- Name: billservice_timeaccessnode_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_timeaccessnode
    ADD CONSTRAINT billservice_timeaccessnode_pkey PRIMARY KEY (id);


--
-- TOC entry 2794 (class 2606 OID 4631422)
-- Dependencies: 2028 2028
-- Name: billservice_timeaccessservice_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_timeaccessservice
    ADD CONSTRAINT billservice_timeaccessservice_pkey PRIMARY KEY (id);


--
-- TOC entry 2796 (class 2606 OID 4631424)
-- Dependencies: 2030 2030
-- Name: billservice_timeperiod_name_key; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_timeperiod
    ADD CONSTRAINT billservice_timeperiod_name_key UNIQUE (name);


--
-- TOC entry 2798 (class 2606 OID 4631426)
-- Dependencies: 2030 2030
-- Name: billservice_timeperiod_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_timeperiod
    ADD CONSTRAINT billservice_timeperiod_pkey PRIMARY KEY (id);


--
-- TOC entry 2800 (class 2606 OID 4631428)
-- Dependencies: 2032 2032
-- Name: billservice_timeperiod_time_period_nodes_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_timeperiod_time_period_nodes
    ADD CONSTRAINT billservice_timeperiod_time_period_nodes_pkey PRIMARY KEY (id);


--
-- TOC entry 2802 (class 2606 OID 4631430)
-- Dependencies: 2032 2032 2032
-- Name: billservice_timeperiod_time_period_nodes_timeperiod_id_key; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_timeperiod_time_period_nodes
    ADD CONSTRAINT billservice_timeperiod_time_period_nodes_timeperiod_id_key UNIQUE (timeperiod_id, timeperiodnode_id);


--
-- TOC entry 2804 (class 2606 OID 4631432)
-- Dependencies: 2034 2034
-- Name: billservice_timeperiodnode_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_timeperiodnode
    ADD CONSTRAINT billservice_timeperiodnode_pkey PRIMARY KEY (id);


--
-- TOC entry 2807 (class 2606 OID 4631434)
-- Dependencies: 2036 2036
-- Name: billservice_timespeed_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_timespeed
    ADD CONSTRAINT billservice_timespeed_pkey PRIMARY KEY (id);


--
-- TOC entry 2874 (class 2606 OID 4632067)
-- Dependencies: 2073 2073
-- Name: billservice_timetransaction_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_timetransaction
    ADD CONSTRAINT billservice_timetransaction_pkey PRIMARY KEY (id);


--
-- TOC entry 2878 (class 2606 OID 4632159)
-- Dependencies: 2075 2075
-- Name: billservice_tpchangerule_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_tpchangerule
    ADD CONSTRAINT billservice_tpchangerule_pkey PRIMARY KEY (id);


--
-- TOC entry 2810 (class 2606 OID 4631436)
-- Dependencies: 2038 2038
-- Name: billservice_trafficlimit_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_trafficlimit
    ADD CONSTRAINT billservice_trafficlimit_pkey PRIMARY KEY (id);


--
-- TOC entry 2814 (class 2606 OID 4631438)
-- Dependencies: 2040 2040
-- Name: billservice_trafficlimit_traffic_class_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_trafficlimit_traffic_class
    ADD CONSTRAINT billservice_trafficlimit_traffic_class_pkey PRIMARY KEY (id);


--
-- TOC entry 2816 (class 2606 OID 4631440)
-- Dependencies: 2040 2040 2040
-- Name: billservice_trafficlimit_traffic_class_trafficlimit_id_key; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_trafficlimit_traffic_class
    ADD CONSTRAINT billservice_trafficlimit_traffic_class_trafficlimit_id_key UNIQUE (trafficlimit_id, trafficclass_id);


--
-- TOC entry 2870 (class 2606 OID 4632044)
-- Dependencies: 2071 2071
-- Name: billservice_traffictransaction_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_traffictransaction
    ADD CONSTRAINT billservice_traffictransaction_pkey PRIMARY KEY (id);


--
-- TOC entry 2818 (class 2606 OID 4631442)
-- Dependencies: 2042 2042
-- Name: billservice_traffictransmitnodes_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_traffictransmitnodes
    ADD CONSTRAINT billservice_traffictransmitnodes_pkey PRIMARY KEY (id);


--
-- TOC entry 2821 (class 2606 OID 4631444)
-- Dependencies: 2044 2044 2044
-- Name: billservice_traffictransmitnodes_ti_traffictransmitnodes_id_key; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_traffictransmitnodes_time_nodes
    ADD CONSTRAINT billservice_traffictransmitnodes_ti_traffictransmitnodes_id_key UNIQUE (traffictransmitnodes_id, timeperiod_id);


--
-- TOC entry 2823 (class 2606 OID 4631446)
-- Dependencies: 2044 2044
-- Name: billservice_traffictransmitnodes_time_nodes_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_traffictransmitnodes_time_nodes
    ADD CONSTRAINT billservice_traffictransmitnodes_time_nodes_pkey PRIMARY KEY (id);


--
-- TOC entry 2825 (class 2606 OID 4631448)
-- Dependencies: 2046 2046 2046
-- Name: billservice_traffictransmitnodes_tr_traffictransmitnodes_id_key; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_traffictransmitnodes_traffic_class
    ADD CONSTRAINT billservice_traffictransmitnodes_tr_traffictransmitnodes_id_key UNIQUE (traffictransmitnodes_id, trafficclass_id);


--
-- TOC entry 2827 (class 2606 OID 4631450)
-- Dependencies: 2046 2046
-- Name: billservice_traffictransmitnodes_traffic_class_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_traffictransmitnodes_traffic_class
    ADD CONSTRAINT billservice_traffictransmitnodes_traffic_class_pkey PRIMARY KEY (id);


--
-- TOC entry 2829 (class 2606 OID 4631452)
-- Dependencies: 2048 2048
-- Name: billservice_traffictransmitservice_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_traffictransmitservice
    ADD CONSTRAINT billservice_traffictransmitservice_pkey PRIMARY KEY (id);


--
-- TOC entry 2832 (class 2606 OID 4631454)
-- Dependencies: 2050 2050
-- Name: billservice_transaction_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_transaction
    ADD CONSTRAINT billservice_transaction_pkey PRIMARY KEY (id);


--
-- TOC entry 2837 (class 2606 OID 4631456)
-- Dependencies: 2052 2052
-- Name: billservice_transactiontype_internal_name_key; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_transactiontype
    ADD CONSTRAINT billservice_transactiontype_internal_name_key UNIQUE (internal_name);


--
-- TOC entry 2839 (class 2606 OID 4631458)
-- Dependencies: 2052 2052
-- Name: billservice_transactiontype_name_key; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_transactiontype
    ADD CONSTRAINT billservice_transactiontype_name_key UNIQUE (name);


--
-- TOC entry 2841 (class 2606 OID 4631460)
-- Dependencies: 2052 2052
-- Name: billservice_transactiontype_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_transactiontype
    ADD CONSTRAINT billservice_transactiontype_pkey PRIMARY KEY (id);


--
-- TOC entry 2888 (class 2606 OID 4632667)
-- Dependencies: 2079 2079
-- Name: billservice_x8021_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_x8021
    ADD CONSTRAINT billservice_x8021_pkey PRIMARY KEY (id);


--
-- TOC entry 2844 (class 2606 OID 4631462)
-- Dependencies: 2054 2054
-- Name: django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- TOC entry 2847 (class 2606 OID 4631464)
-- Dependencies: 2056 2056 2056
-- Name: django_content_type_app_label_key; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_app_label_key UNIQUE (app_label, model);


--
-- TOC entry 2849 (class 2606 OID 4631466)
-- Dependencies: 2056 2056
-- Name: django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- TOC entry 2851 (class 2606 OID 4631468)
-- Dependencies: 2058 2058
-- Name: django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- TOC entry 2853 (class 2606 OID 4631470)
-- Dependencies: 2059 2059
-- Name: django_site_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY django_site
    ADD CONSTRAINT django_site_pkey PRIMARY KEY (id);


--
-- TOC entry 2855 (class 2606 OID 4631472)
-- Dependencies: 2061 2061
-- Name: nas_nas_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY nas_nas
    ADD CONSTRAINT nas_nas_pkey PRIMARY KEY (id);


--
-- TOC entry 2857 (class 2606 OID 4631474)
-- Dependencies: 2063 2063
-- Name: nas_trafficclass_name_key; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY nas_trafficclass
    ADD CONSTRAINT nas_trafficclass_name_key UNIQUE (name);


--
-- TOC entry 2859 (class 2606 OID 4631476)
-- Dependencies: 2063 2063
-- Name: nas_trafficclass_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY nas_trafficclass
    ADD CONSTRAINT nas_trafficclass_pkey PRIMARY KEY (id);


--
-- TOC entry 2861 (class 2606 OID 4631478)
-- Dependencies: 2063 2063
-- Name: nas_trafficclass_weight_key; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY nas_trafficclass
    ADD CONSTRAINT nas_trafficclass_weight_key UNIQUE (weight);


--
-- TOC entry 2863 (class 2606 OID 4631480)
-- Dependencies: 2065 2065
-- Name: nas_trafficnode_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY nas_trafficnode
    ADD CONSTRAINT nas_trafficnode_pkey PRIMARY KEY (id);


--
-- TOC entry 2733 (class 2606 OID 4631482)
-- Dependencies: 1989 1989 1989
-- Name: pool_ip_unique; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY billservice_ipinuse
    ADD CONSTRAINT pool_ip_unique UNIQUE (pool_id, ip);


--
-- TOC entry 2867 (class 2606 OID 4631484)
-- Dependencies: 2067 2067
-- Name: radius_activesession_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY radius_activesession
    ADD CONSTRAINT radius_activesession_pkey PRIMARY KEY (id);


--
-- TOC entry 2634 (class 2606 OID 4631486)
-- Dependencies: 1941 1941
-- Name: radius_session_pkey; Type: CONSTRAINT; Schema: public; Owner: ebs; Tablespace: 
--

ALTER TABLE ONLY radius_session
    ADD CONSTRAINT radius_session_pkey PRIMARY KEY (id);


--
-- TOC entry 2645 (class 1259 OID 4631487)
-- Dependencies: 1946
-- Name: auth_message_user_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX auth_message_user_id ON auth_message USING btree (user_id);


--
-- TOC entry 2646 (class 1259 OID 4631488)
-- Dependencies: 1948
-- Name: auth_permission_content_type_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX auth_permission_content_type_id ON auth_permission USING btree (content_type_id);


--
-- TOC entry 2663 (class 1259 OID 4631489)
-- Dependencies: 1956
-- Name: billservice_accessparameters_access_time_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_accessparameters_access_time_id ON billservice_accessparameters USING btree (access_time_id);


--
-- TOC entry 2666 (class 1259 OID 4631490)
-- Dependencies: 1958
-- Name: billservice_account_ipn_ip_address; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_account_ipn_ip_address ON billservice_account USING btree (ipn_ip_address);


--
-- TOC entry 2667 (class 1259 OID 4631491)
-- Dependencies: 1958
-- Name: billservice_account_nas_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_account_nas_id ON billservice_account USING btree (nas_id);


--
-- TOC entry 2672 (class 1259 OID 4631492)
-- Dependencies: 1958
-- Name: billservice_account_vpn_ip_address; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_account_vpn_ip_address ON billservice_account USING btree (vpn_ip_address);


--
-- TOC entry 2900 (class 1259 OID 4632786)
-- Dependencies: 2085
-- Name: billservice_accountaddonservice_account_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_accountaddonservice_account_id ON billservice_accountaddonservice USING btree (account_id);


--
-- TOC entry 2903 (class 1259 OID 4632787)
-- Dependencies: 2085
-- Name: billservice_accountaddonservice_service_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_accountaddonservice_service_id ON billservice_accountaddonservice USING btree (service_id);


--
-- TOC entry 2675 (class 1259 OID 4631493)
-- Dependencies: 1960
-- Name: billservice_accountipnspeed_account_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_accountipnspeed_account_id ON billservice_accountipnspeed USING btree (account_id);


--
-- TOC entry 2678 (class 1259 OID 4631494)
-- Dependencies: 1962
-- Name: billservice_accountprepaystime_account_tarif_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_accountprepaystime_account_tarif_id ON billservice_accountprepaystime USING btree (account_tarif_id);


--
-- TOC entry 2681 (class 1259 OID 4631495)
-- Dependencies: 1962
-- Name: billservice_accountprepaystime_prepaid_time_service_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_accountprepaystime_prepaid_time_service_id ON billservice_accountprepaystime USING btree (prepaid_time_service_id);


--
-- TOC entry 2682 (class 1259 OID 4631496)
-- Dependencies: 1964
-- Name: billservice_accountprepaystrafic_account_tarif_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_accountprepaystrafic_account_tarif_id ON billservice_accountprepaystrafic USING btree (account_tarif_id);


--
-- TOC entry 2685 (class 1259 OID 4631497)
-- Dependencies: 1964
-- Name: billservice_accountprepaystrafic_prepaid_traffic_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_accountprepaystrafic_prepaid_traffic_id ON billservice_accountprepaystrafic USING btree (prepaid_traffic_id);


--
-- TOC entry 2686 (class 1259 OID 4631498)
-- Dependencies: 1966
-- Name: billservice_accountspeedlimit_account_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_accountspeedlimit_account_id ON billservice_accountspeedlimit USING btree (account_id);


--
-- TOC entry 2689 (class 1259 OID 4631499)
-- Dependencies: 1966
-- Name: billservice_accountspeedlimit_speedlimit_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_accountspeedlimit_speedlimit_id ON billservice_accountspeedlimit USING btree (speedlimit_id);


--
-- TOC entry 2692 (class 1259 OID 4631500)
-- Dependencies: 1968
-- Name: billservice_accounttarif_account_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_accounttarif_account_id ON billservice_accounttarif USING btree (account_id);


--
-- TOC entry 2695 (class 1259 OID 4631501)
-- Dependencies: 1968
-- Name: billservice_accounttarif_tarif_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_accounttarif_tarif_id ON billservice_accounttarif USING btree (tarif_id);


--
-- TOC entry 2889 (class 1259 OID 4632735)
-- Dependencies: 2081
-- Name: billservice_addonservice_nas_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_addonservice_nas_id ON billservice_addonservice USING btree (nas_id);


--
-- TOC entry 2892 (class 1259 OID 4632736)
-- Dependencies: 2081
-- Name: billservice_addonservice_sp_period_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_addonservice_sp_period_id ON billservice_addonservice USING btree (sp_period_id);


--
-- TOC entry 2893 (class 1259 OID 4632737)
-- Dependencies: 2081
-- Name: billservice_addonservice_timeperiod_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_addonservice_timeperiod_id ON billservice_addonservice USING btree (timeperiod_id);


--
-- TOC entry 2894 (class 1259 OID 4632738)
-- Dependencies: 2081
-- Name: billservice_addonservice_wyte_period_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_addonservice_wyte_period_id ON billservice_addonservice USING btree (wyte_period_id);


--
-- TOC entry 2895 (class 1259 OID 4632763)
-- Dependencies: 2083
-- Name: billservice_addonservicetarif_activation_count_period_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_addonservicetarif_activation_count_period_id ON billservice_addonservicetarif USING btree (activation_count_period_id);


--
-- TOC entry 2898 (class 1259 OID 4632764)
-- Dependencies: 2083
-- Name: billservice_addonservicetarif_service_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_addonservicetarif_service_id ON billservice_addonservicetarif USING btree (service_id);


--
-- TOC entry 2899 (class 1259 OID 4632765)
-- Dependencies: 2083
-- Name: billservice_addonservicetarif_tarif_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_addonservicetarif_tarif_id ON billservice_addonservicetarif USING btree (tarif_id);


--
-- TOC entry 2904 (class 1259 OID 4632825)
-- Dependencies: 2087
-- Name: billservice_addonservicetransaction_account_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_addonservicetransaction_account_id ON billservice_addonservicetransaction USING btree (account_id);


--
-- TOC entry 2905 (class 1259 OID 4632826)
-- Dependencies: 2087
-- Name: billservice_addonservicetransaction_accountaddonservice_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_addonservicetransaction_accountaddonservice_id ON billservice_addonservicetransaction USING btree (accountaddonservice_id);


--
-- TOC entry 2906 (class 1259 OID 4632827)
-- Dependencies: 2087
-- Name: billservice_addonservicetransaction_accounttarif_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_addonservicetransaction_accounttarif_id ON billservice_addonservicetransaction USING btree (accounttarif_id);


--
-- TOC entry 2909 (class 1259 OID 4632828)
-- Dependencies: 2087
-- Name: billservice_addonservicetransaction_service_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_addonservicetransaction_service_id ON billservice_addonservicetransaction USING btree (service_id);


--
-- TOC entry 2698 (class 1259 OID 4631502)
-- Dependencies: 1972
-- Name: billservice_card_activated_by_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_card_activated_by_id ON billservice_card USING btree (activated_by_id);


--
-- TOC entry 2703 (class 1259 OID 4631503)
-- Dependencies: 1974
-- Name: billservice_dealer_bank_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_dealer_bank_id ON billservice_dealer USING btree (bank_id);


--
-- TOC entry 2706 (class 1259 OID 4631504)
-- Dependencies: 1976
-- Name: billservice_dealerpay_dealer_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_dealerpay_dealer_id ON billservice_dealerpay USING btree (dealer_id);


--
-- TOC entry 2709 (class 1259 OID 4631505)
-- Dependencies: 1976
-- Name: billservice_dealerpay_salecard_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_dealerpay_salecard_id ON billservice_dealerpay USING btree (salecard_id);


--
-- TOC entry 2710 (class 1259 OID 4631506)
-- Dependencies: 1978
-- Name: billservice_document_account_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_document_account_id ON billservice_document USING btree (account_id);


--
-- TOC entry 2713 (class 1259 OID 4631507)
-- Dependencies: 1978
-- Name: billservice_document_type_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_document_type_id ON billservice_document USING btree (type_id);


--
-- TOC entry 2716 (class 1259 OID 4631508)
-- Dependencies: 1982 1982
-- Name: billservice_globalstat_acc_dt_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_globalstat_acc_dt_id ON billservice_globalstat USING btree (account_id, datetime);


--
-- TOC entry 2719 (class 1259 OID 4631509)
-- Dependencies: 1982
-- Name: billservice_globalstat_account_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_globalstat_account_id ON billservice_globalstat USING btree (account_id);


--
-- TOC entry 2720 (class 1259 OID 4631510)
-- Dependencies: 1982
-- Name: billservice_globalstat_datetime; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_globalstat_datetime ON billservice_globalstat USING btree (datetime);


--
-- TOC entry 2731 (class 1259 OID 4631511)
-- Dependencies: 1989
-- Name: billservice_ipinuse_pool_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_ipinuse_pool_id ON billservice_ipinuse USING btree (pool_id);


--
-- TOC entry 2612 (class 1259 OID 4631512)
-- Dependencies: 1938
-- Name: billservice_netflowstream_account_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_netflowstream_account_id ON billservice_netflowstream USING btree (account_id);


--
-- TOC entry 2613 (class 1259 OID 4631513)
-- Dependencies: 1938
-- Name: billservice_netflowstream_nas_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_netflowstream_nas_id ON billservice_netflowstream USING btree (nas_id);


--
-- TOC entry 2616 (class 1259 OID 4631514)
-- Dependencies: 1938
-- Name: billservice_netflowstream_tarif_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_netflowstream_tarif_id ON billservice_netflowstream USING btree (tarif_id);


--
-- TOC entry 2617 (class 1259 OID 4631515)
-- Dependencies: 1938
-- Name: billservice_netflowstream_traffic_class_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_netflowstream_traffic_class_id ON billservice_netflowstream USING btree (traffic_class_id);


--
-- TOC entry 2618 (class 1259 OID 4631516)
-- Dependencies: 1938
-- Name: billservice_netflowstream_traffic_transmit_node_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_netflowstream_traffic_transmit_node_id ON billservice_netflowstream USING btree (traffic_transmit_node_id);


--
-- TOC entry 2738 (class 1259 OID 4631517)
-- Dependencies: 1994
-- Name: billservice_onetimeservice_tarif_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_onetimeservice_tarif_id ON billservice_onetimeservice USING btree (tarif_id);


--
-- TOC entry 2739 (class 1259 OID 4631518)
-- Dependencies: 1996
-- Name: billservice_onetimeservicehistory_accounttarif_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_onetimeservicehistory_accounttarif_id ON billservice_onetimeservicehistory USING btree (accounttarif_id);


--
-- TOC entry 2740 (class 1259 OID 4631519)
-- Dependencies: 1996
-- Name: billservice_onetimeservicehistory_onetimeservice_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_onetimeservicehistory_onetimeservice_id ON billservice_onetimeservicehistory USING btree (onetimeservice_id);


--
-- TOC entry 2751 (class 1259 OID 4631520)
-- Dependencies: 2002
-- Name: billservice_periodicalservice_settlement_period_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_periodicalservice_settlement_period_id ON billservice_periodicalservice USING btree (settlement_period_id);


--
-- TOC entry 2752 (class 1259 OID 4631521)
-- Dependencies: 2002
-- Name: billservice_periodicalservice_tarif_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_periodicalservice_tarif_id ON billservice_periodicalservice USING btree (tarif_id);


--
-- TOC entry 2629 (class 1259 OID 4631522)
-- Dependencies: 1940
-- Name: billservice_periodicalservicehistory_service_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_periodicalservicehistory_service_id ON billservice_periodicalservicehistory USING btree (service_id);


--
-- TOC entry 2630 (class 1259 OID 4631523)
-- Dependencies: 1940
-- Name: billservice_periodicalservicehistory_transaction_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_periodicalservicehistory_transaction_id ON billservice_periodicalservicehistory USING btree (transaction_id);


--
-- TOC entry 2757 (class 1259 OID 4631524)
-- Dependencies: 2007
-- Name: billservice_prepaidtraffic_traffic_transmit_service_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_prepaidtraffic_traffic_transmit_service_id ON billservice_prepaidtraffic USING btree (traffic_transmit_service_id);


--
-- TOC entry 2884 (class 1259 OID 4632575)
-- Dependencies: 2077
-- Name: billservice_radiusattrs_tarif_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_radiusattrs_tarif_id ON billservice_radiusattrs USING btree (tarif_id);


--
-- TOC entry 2759 (class 1259 OID 4631525)
-- Dependencies: 2009
-- Name: billservice_salecard_dealer_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_salecard_dealer_id ON billservice_salecard USING btree (dealer_id);


--
-- TOC entry 2776 (class 1259 OID 4631526)
-- Dependencies: 2017
-- Name: billservice_speedlimit_limit_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_speedlimit_limit_id ON billservice_speedlimit USING btree (limit_id);


--
-- TOC entry 2779 (class 1259 OID 4631527)
-- Dependencies: 2019
-- Name: billservice_suspendedperiod_account_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_suspendedperiod_account_id ON billservice_suspendedperiod USING btree (account_id);


--
-- TOC entry 2619 (class 1259 OID 4631528)
-- Dependencies: 1939
-- Name: billservice_tariff_access_parameters_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_tariff_access_parameters_id ON billservice_tariff USING btree (access_parameters_id);


--
-- TOC entry 2624 (class 1259 OID 4631529)
-- Dependencies: 1939
-- Name: billservice_tariff_settlement_period_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_tariff_settlement_period_id ON billservice_tariff USING btree (settlement_period_id);


--
-- TOC entry 2625 (class 1259 OID 4631530)
-- Dependencies: 1939
-- Name: billservice_tariff_time_access_service_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_tariff_time_access_service_id ON billservice_tariff USING btree (time_access_service_id);


--
-- TOC entry 2626 (class 1259 OID 4631531)
-- Dependencies: 1939
-- Name: billservice_tariff_traffic_transmit_service_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_tariff_traffic_transmit_service_id ON billservice_tariff USING btree (traffic_transmit_service_id);


--
-- TOC entry 2788 (class 1259 OID 4631532)
-- Dependencies: 2024
-- Name: billservice_template_type_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_template_type_id ON billservice_template USING btree (type_id);


--
-- TOC entry 2791 (class 1259 OID 4631533)
-- Dependencies: 2026
-- Name: billservice_timeaccessnode_time_access_service_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_timeaccessnode_time_access_service_id ON billservice_timeaccessnode USING btree (time_access_service_id);


--
-- TOC entry 2792 (class 1259 OID 4631534)
-- Dependencies: 2026
-- Name: billservice_timeaccessnode_time_period_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_timeaccessnode_time_period_id ON billservice_timeaccessnode USING btree (time_period_id);


--
-- TOC entry 2805 (class 1259 OID 4631535)
-- Dependencies: 2036
-- Name: billservice_timespeed_access_parameters_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_timespeed_access_parameters_id ON billservice_timespeed USING btree (access_parameters_id);


--
-- TOC entry 2808 (class 1259 OID 4631536)
-- Dependencies: 2036
-- Name: billservice_timespeed_time_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_timespeed_time_id ON billservice_timespeed USING btree (time_id);


--
-- TOC entry 2872 (class 1259 OID 4632083)
-- Dependencies: 2073
-- Name: billservice_timetransaction_account_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_timetransaction_account_id ON billservice_timetransaction USING btree (account_id);


--
-- TOC entry 2875 (class 1259 OID 4632084)
-- Dependencies: 2073 2073 2073
-- Name: billservice_timetransaction_traffictransmitservice_id_account_i; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_timetransaction_traffictransmitservice_id_account_i ON billservice_timetransaction USING btree (timeaccessservice_id, accounttarif_id, datetime);


--
-- TOC entry 2876 (class 1259 OID 4632175)
-- Dependencies: 2075
-- Name: billservice_tpchangerule_from_tariff_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_tpchangerule_from_tariff_id ON billservice_tpchangerule USING btree (from_tariff_id);


--
-- TOC entry 2879 (class 1259 OID 4632176)
-- Dependencies: 2075
-- Name: billservice_tpchangerule_settlement_period_id_index; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_tpchangerule_settlement_period_id_index ON billservice_tpchangerule USING btree (settlement_period_id);


--
-- TOC entry 2880 (class 1259 OID 4632177)
-- Dependencies: 2075 2075
-- Name: billservice_tpchangerule_tariff_tariff; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE UNIQUE INDEX billservice_tpchangerule_tariff_tariff ON billservice_tpchangerule USING btree (from_tariff_id, to_tariff_id);


--
-- TOC entry 2881 (class 1259 OID 4632178)
-- Dependencies: 2075
-- Name: billservice_tpchangerule_to_tariff_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_tpchangerule_to_tariff_id ON billservice_tpchangerule USING btree (to_tariff_id);


--
-- TOC entry 2811 (class 1259 OID 4631537)
-- Dependencies: 2038
-- Name: billservice_trafficlimit_settlement_period_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_trafficlimit_settlement_period_id ON billservice_trafficlimit USING btree (settlement_period_id);


--
-- TOC entry 2812 (class 1259 OID 4631538)
-- Dependencies: 2038
-- Name: billservice_trafficlimit_tarif_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_trafficlimit_tarif_id ON billservice_trafficlimit USING btree (tarif_id);


--
-- TOC entry 2868 (class 1259 OID 4632055)
-- Dependencies: 2071
-- Name: billservice_traffictransaction_account_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_traffictransaction_account_id ON billservice_traffictransaction USING btree (account_id);


--
-- TOC entry 2871 (class 1259 OID 4632056)
-- Dependencies: 2071 2071 2071
-- Name: billservice_traffictransaction_traffictransmitservice_id_accoun; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_traffictransaction_traffictransmitservice_id_accoun ON billservice_traffictransaction USING btree (traffictransmitservice_id, accounttarif_id, datetime);


--
-- TOC entry 2819 (class 1259 OID 4631539)
-- Dependencies: 2042
-- Name: billservice_traffictransmitnodes_traffic_transmit_service_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_traffictransmitnodes_traffic_transmit_service_id ON billservice_traffictransmitnodes USING btree (traffic_transmit_service_id);


--
-- TOC entry 2830 (class 1259 OID 4631540)
-- Dependencies: 2050
-- Name: billservice_transaction_account_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_transaction_account_id ON billservice_transaction USING btree (account_id);


--
-- TOC entry 2833 (class 1259 OID 4631541)
-- Dependencies: 2050
-- Name: billservice_transaction_tarif_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_transaction_tarif_id ON billservice_transaction USING btree (tarif_id);


--
-- TOC entry 2835 (class 1259 OID 4632788)
-- Dependencies: 2052
-- Name: billservice_transactiontype_ind; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE UNIQUE INDEX billservice_transactiontype_ind ON billservice_transactiontype USING btree (id);


--
-- TOC entry 2885 (class 1259 OID 4632678)
-- Dependencies: 2079
-- Name: billservice_x8021_account_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_x8021_account_id ON billservice_x8021 USING btree (account_id);


--
-- TOC entry 2886 (class 1259 OID 4632679)
-- Dependencies: 2079
-- Name: billservice_x8021_nas_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX billservice_x8021_nas_id ON billservice_x8021 USING btree (nas_id);


--
-- TOC entry 2842 (class 1259 OID 4631542)
-- Dependencies: 2054
-- Name: django_admin_log_content_type_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX django_admin_log_content_type_id ON django_admin_log USING btree (content_type_id);


--
-- TOC entry 2845 (class 1259 OID 4631543)
-- Dependencies: 2054
-- Name: django_admin_log_user_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX django_admin_log_user_id ON django_admin_log USING btree (user_id);


--
-- TOC entry 2673 (class 1259 OID 4631544)
-- Dependencies: 1958
-- Name: fki_billservice_account_ipnipinuse_fkey; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX fki_billservice_account_ipnipinuse_fkey ON billservice_account USING btree (ipn_ipinuse_id);


--
-- TOC entry 2674 (class 1259 OID 4631545)
-- Dependencies: 1958
-- Name: fki_billservice_account_vpnipinuse_fkey; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX fki_billservice_account_vpnipinuse_fkey ON billservice_account USING btree (vpn_ipinuse_id);


--
-- TOC entry 2910 (class 1259 OID 4633009)
-- Dependencies: 2087
-- Name: fki_billservice_addonservicetransaction_type_id_fkey; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX fki_billservice_addonservicetransaction_type_id_fkey ON billservice_addonservicetransaction USING btree (type_id);


--
-- TOC entry 2701 (class 1259 OID 4631546)
-- Dependencies: 1972
-- Name: fki_billservice_card_account_fkey; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX fki_billservice_card_account_fkey ON billservice_card USING btree (account_id);


--
-- TOC entry 2702 (class 1259 OID 4631547)
-- Dependencies: 1972
-- Name: fki_billservice_card_tarif_fkey; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX fki_billservice_card_tarif_fkey ON billservice_card USING btree (tarif_id);


--
-- TOC entry 2743 (class 1259 OID 4631548)
-- Dependencies: 1996
-- Name: fki_billservice_onetimeservicehistory_transaction_id_fkey; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX fki_billservice_onetimeservicehistory_transaction_id_fkey ON billservice_onetimeservicehistory USING btree (transaction_id);


--
-- TOC entry 2746 (class 1259 OID 4631549)
-- Dependencies: 1998
-- Name: fki_billservice_operator_bank_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX fki_billservice_operator_bank_id ON billservice_operator USING btree (bank_id);


--
-- TOC entry 2758 (class 1259 OID 4631550)
-- Dependencies: 2007
-- Name: fki_billservice_prepaidtraffic_group_id_fkey; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX fki_billservice_prepaidtraffic_group_id_fkey ON billservice_prepaidtraffic USING btree (group_id);


--
-- TOC entry 2834 (class 1259 OID 4632004)
-- Dependencies: 2050
-- Name: fki_billservice_systemuser_fkey; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX fki_billservice_systemuser_fkey ON billservice_transaction USING btree (systemuser_id);


--
-- TOC entry 2864 (class 1259 OID 4631551)
-- Dependencies: 2065
-- Name: nas_trafficnode_traffic_class_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX nas_trafficnode_traffic_class_id ON nas_trafficnode USING btree (traffic_class_id);


--
-- TOC entry 2865 (class 1259 OID 4631552)
-- Dependencies: 2067
-- Name: radius_activesession_account_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX radius_activesession_account_id ON radius_activesession USING btree (account_id);


--
-- TOC entry 2631 (class 1259 OID 4631553)
-- Dependencies: 1941
-- Name: radius_session_account_id; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX radius_session_account_id ON radius_session USING btree (account_id);


--
-- TOC entry 2632 (class 1259 OID 4632582)
-- Dependencies: 1941 1941 1941
-- Name: radius_session_account_session_interrim_idx; Type: INDEX; Schema: public; Owner: ebs; Tablespace: 
--

CREATE INDEX radius_session_account_session_interrim_idx ON radius_session USING btree (account_id, sessionid, interrim_update);


--
-- TOC entry 3028 (class 2620 OID 4632585)
-- Dependencies: 178 1939
-- Name: a_set_deleted_trg; Type: TRIGGER; Schema: public; Owner: ebs
--

CREATE TRIGGER a_set_deleted_trg
    BEFORE DELETE ON billservice_tariff
    FOR EACH ROW
    EXECUTE PROCEDURE set_deleted_trg_fn();


--
-- TOC entry 3037 (class 2620 OID 4632036)
-- Dependencies: 1996 96
-- Name: acc_otsh_trg; Type: TRIGGER; Schema: public; Owner: ebs
--

CREATE TRIGGER acc_otsh_trg
    AFTER INSERT OR DELETE OR UPDATE ON billservice_onetimeservicehistory
    FOR EACH ROW
    EXECUTE PROCEDURE account_transaction_trg_fn();


--
-- TOC entry 3031 (class 2620 OID 4632024)
-- Dependencies: 96 1940
-- Name: acc_psh_trg; Type: TRIGGER; Schema: public; Owner: ebs
--

CREATE TRIGGER acc_psh_trg
    BEFORE INSERT OR DELETE OR UPDATE ON billservice_periodicalservicehistory
    FOR EACH ROW
    EXECUTE PROCEDURE account_transaction_trg_fn();


--
-- TOC entry 3041 (class 2620 OID 4632059)
-- Dependencies: 96 2071
-- Name: acc_tftrans_trg; Type: TRIGGER; Schema: public; Owner: ebs
--

CREATE TRIGGER acc_tftrans_trg
    AFTER INSERT OR DELETE OR UPDATE ON billservice_traffictransaction
    FOR EACH ROW
    EXECUTE PROCEDURE account_transaction_trg_fn();


--
-- TOC entry 3043 (class 2620 OID 4632087)
-- Dependencies: 2073 96
-- Name: acc_tmtrans_trg; Type: TRIGGER; Schema: public; Owner: ebs
--

CREATE TRIGGER acc_tmtrans_trg
    AFTER INSERT OR DELETE OR UPDATE ON billservice_timetransaction
    FOR EACH ROW
    EXECUTE PROCEDURE account_transaction_trg_fn();


--
-- TOC entry 3038 (class 2620 OID 4631555)
-- Dependencies: 96 2050
-- Name: acc_trans_trg; Type: TRIGGER; Schema: public; Owner: ebs
--

CREATE TRIGGER acc_trans_trg
    AFTER INSERT OR DELETE OR UPDATE ON billservice_transaction
    FOR EACH ROW
    EXECUTE PROCEDURE account_transaction_trg_fn();


--
-- TOC entry 3044 (class 2620 OID 4632830)
-- Dependencies: 96 2087
-- Name: adds_trans_trg; Type: TRIGGER; Schema: public; Owner: ebs
--

CREATE TRIGGER adds_trans_trg
    AFTER INSERT OR DELETE OR UPDATE ON billservice_addonservicetransaction
    FOR EACH ROW
    EXECUTE PROCEDURE account_transaction_trg_fn();


--
-- TOC entry 3027 (class 2620 OID 4631998)
-- Dependencies: 155 1939
-- Name: clear_tariff_services_trg; Type: TRIGGER; Schema: public; Owner: ebs
--

CREATE TRIGGER clear_tariff_services_trg
    BEFORE DELETE ON billservice_tariff
    FOR EACH ROW
    EXECUTE PROCEDURE clear_tariff_services_trg_fn();


--
-- TOC entry 3025 (class 2620 OID 4631556)
-- Dependencies: 99 1938
-- Name: del_nfs_trg; Type: TRIGGER; Schema: public; Owner: ebs
--

CREATE TRIGGER del_nfs_trg
    AFTER DELETE ON billservice_netflowstream
    FOR EACH ROW
    EXECUTE PROCEDURE del_nfs_trg_fn();


--
-- TOC entry 3034 (class 2620 OID 4631557)
-- Dependencies: 1958 102
-- Name: free_unused_account_ip_trg; Type: TRIGGER; Schema: public; Owner: ebs
--

CREATE TRIGGER free_unused_account_ip_trg
    AFTER DELETE OR UPDATE ON billservice_account
    FOR EACH ROW
    EXECUTE PROCEDURE free_unused_account_ip_trg_fn();


--
-- TOC entry 3036 (class 2620 OID 4631558)
-- Dependencies: 1972 103
-- Name: free_unused_card_ip_trg; Type: TRIGGER; Schema: public; Owner: ebs
--

CREATE TRIGGER free_unused_card_ip_trg
    AFTER DELETE ON billservice_card
    FOR EACH ROW
    EXECUTE PROCEDURE free_unused_card_ip_trg_fn();


--
-- TOC entry 3023 (class 2620 OID 4631559)
-- Dependencies: 115 1937
-- Name: gpst_del_trg; Type: TRIGGER; Schema: public; Owner: ebs
--

CREATE TRIGGER gpst_del_trg
    AFTER DELETE ON billservice_groupstat
    FOR EACH ROW
    EXECUTE PROCEDURE gpst_del_trg_fn();


--
-- TOC entry 3024 (class 2620 OID 4631560)
-- Dependencies: 1937 116
-- Name: gpst_ins_trg; Type: TRIGGER; Schema: public; Owner: ebs
--

CREATE TRIGGER gpst_ins_trg
    BEFORE INSERT ON billservice_groupstat
    FOR EACH ROW
    EXECUTE PROCEDURE gpst_ins_trg_fn();


--
-- TOC entry 3035 (class 2620 OID 4631561)
-- Dependencies: 1958 98
-- Name: ins_account_trg; Type: TRIGGER; Schema: public; Owner: ebs
--

CREATE TRIGGER ins_account_trg
    BEFORE INSERT ON billservice_account
    FOR EACH ROW
    EXECUTE PROCEDURE check_allowed_users_trg_fn();


--
-- TOC entry 3026 (class 2620 OID 4631562)
-- Dependencies: 126 1938
-- Name: ins_nfs_trg; Type: TRIGGER; Schema: public; Owner: ebs
--

CREATE TRIGGER ins_nfs_trg
    BEFORE INSERT ON billservice_netflowstream
    FOR EACH ROW
    EXECUTE PROCEDURE nfs_ins_trg_fn();


--
-- TOC entry 3029 (class 2620 OID 4631563)
-- Dependencies: 1940 133
-- Name: psh_del_trg; Type: TRIGGER; Schema: public; Owner: ebs
--

CREATE TRIGGER psh_del_trg
    AFTER DELETE ON billservice_periodicalservicehistory
    FOR EACH ROW
    EXECUTE PROCEDURE psh_del_trg_fn();


--
-- TOC entry 3030 (class 2620 OID 4631564)
-- Dependencies: 1940 136
-- Name: psh_ins_trg; Type: TRIGGER; Schema: public; Owner: ebs
--

CREATE TRIGGER psh_ins_trg
    BEFORE INSERT ON billservice_periodicalservicehistory
    FOR EACH ROW
    EXECUTE PROCEDURE psh_ins_trg_fn();


--
-- TOC entry 3032 (class 2620 OID 4631565)
-- Dependencies: 146 1941
-- Name: rsss_del_trg; Type: TRIGGER; Schema: public; Owner: ebs
--

CREATE TRIGGER rsss_del_trg
    AFTER DELETE ON radius_session
    FOR EACH ROW
    EXECUTE PROCEDURE rsss_del_trg_fn();


--
-- TOC entry 3033 (class 2620 OID 4631566)
-- Dependencies: 1941 147
-- Name: rsss_ins_trg; Type: TRIGGER; Schema: public; Owner: ebs
--

CREATE TRIGGER rsss_ins_trg
    BEFORE INSERT ON radius_session
    FOR EACH ROW
    EXECUTE PROCEDURE rsss_ins_trg_fn();


--
-- TOC entry 3040 (class 2620 OID 4632058)
-- Dependencies: 157 2071
-- Name: tftrans_ins_trg; Type: TRIGGER; Schema: public; Owner: ebs
--

CREATE TRIGGER tftrans_ins_trg
    BEFORE INSERT ON billservice_traffictransaction
    FOR EACH ROW
    EXECUTE PROCEDURE tftrans_ins_trg_fn();


--
-- TOC entry 3042 (class 2620 OID 4632086)
-- Dependencies: 2073 158
-- Name: tmtrans_ins_trg; Type: TRIGGER; Schema: public; Owner: ebs
--

CREATE TRIGGER tmtrans_ins_trg
    BEFORE INSERT ON billservice_timetransaction
    FOR EACH ROW
    EXECUTE PROCEDURE tmtrans_ins_trg_fn();


--
-- TOC entry 3039 (class 2620 OID 4632015)
-- Dependencies: 2050 154
-- Name: trans_acctf_ins_trg; Type: TRIGGER; Schema: public; Owner: ebs
--

CREATE TRIGGER trans_acctf_ins_trg
    BEFORE INSERT ON billservice_transaction
    FOR EACH ROW
    EXECUTE PROCEDURE trans_acctf_ins_trg_fn();


--
-- TOC entry 2998 (class 2606 OID 4631567)
-- Dependencies: 2067 2668 1958
-- Name: account_id_refs_id_16c70393; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY radius_activesession
    ADD CONSTRAINT account_id_refs_id_16c70393 FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2922 (class 2606 OID 4631572)
-- Dependencies: 1941 2668 1958
-- Name: account_id_refs_id_600b3363; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY radius_session
    ADD CONSTRAINT account_id_refs_id_600b3363 FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2937 (class 2606 OID 4631577)
-- Dependencies: 1968 2693 1962
-- Name: account_tarif_id_refs_id_48fe22d0; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_accountprepaystime
    ADD CONSTRAINT account_tarif_id_refs_id_48fe22d0 FOREIGN KEY (account_tarif_id) REFERENCES billservice_accounttarif(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2939 (class 2606 OID 4631582)
-- Dependencies: 1964 1968 2693
-- Name: account_tarif_id_refs_id_7d07606a; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_accountprepaystrafic
    ADD CONSTRAINT account_tarif_id_refs_id_7d07606a FOREIGN KEY (account_tarif_id) REFERENCES billservice_accounttarif(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2924 (class 2606 OID 4631587)
-- Dependencies: 1942 1944 2637
-- Name: auth_group_permissions_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_fkey FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2925 (class 2606 OID 4631592)
-- Dependencies: 1948 1944 2649
-- Name: auth_group_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2926 (class 2606 OID 4631597)
-- Dependencies: 1946 1950 2651
-- Name: auth_message_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY auth_message
    ADD CONSTRAINT auth_message_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2928 (class 2606 OID 4631602)
-- Dependencies: 2637 1951 1942
-- Name: auth_user_groups_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_fkey FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2929 (class 2606 OID 4631607)
-- Dependencies: 2651 1951 1950
-- Name: auth_user_groups_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2930 (class 2606 OID 4631612)
-- Dependencies: 1954 2649 1948
-- Name: auth_user_user_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2931 (class 2606 OID 4631617)
-- Dependencies: 2651 1954 1950
-- Name: auth_user_user_permissions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2932 (class 2606 OID 4631622)
-- Dependencies: 2030 1956 2797
-- Name: billservice_accessparameters_access_time_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_accessparameters
    ADD CONSTRAINT billservice_accessparameters_access_time_id_fkey FOREIGN KEY (access_time_id) REFERENCES billservice_timeperiod(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2933 (class 2606 OID 4631627)
-- Dependencies: 1989 2729 1958
-- Name: billservice_account_ipnipinuse_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_account
    ADD CONSTRAINT billservice_account_ipnipinuse_fkey FOREIGN KEY (ipn_ipinuse_id) REFERENCES billservice_ipinuse(id) ON DELETE CASCADE;


--
-- TOC entry 2934 (class 2606 OID 4631632)
-- Dependencies: 1958 2854 2061
-- Name: billservice_account_nas_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_account
    ADD CONSTRAINT billservice_account_nas_id_fkey FOREIGN KEY (nas_id) REFERENCES nas_nas(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2935 (class 2606 OID 4631637)
-- Dependencies: 1958 1989 2729
-- Name: billservice_account_vpnipinuse_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_account
    ADD CONSTRAINT billservice_account_vpnipinuse_fkey FOREIGN KEY (vpn_ipinuse_id) REFERENCES billservice_ipinuse(id) ON DELETE CASCADE;


--
-- TOC entry 3016 (class 2606 OID 4632776)
-- Dependencies: 2668 2085 1958
-- Name: billservice_accountaddonservice_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_accountaddonservice
    ADD CONSTRAINT billservice_accountaddonservice_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3017 (class 2606 OID 4632781)
-- Dependencies: 2890 2085 2081
-- Name: billservice_accountaddonservice_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_accountaddonservice
    ADD CONSTRAINT billservice_accountaddonservice_service_id_fkey FOREIGN KEY (service_id) REFERENCES billservice_addonservice(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 2936 (class 2606 OID 4631642)
-- Dependencies: 1960 1958 2668
-- Name: billservice_accountipnspeed_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_accountipnspeed
    ADD CONSTRAINT billservice_accountipnspeed_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2938 (class 2606 OID 4631647)
-- Dependencies: 1962 2028 2793
-- Name: billservice_accountprepaystime_prepaid_time_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_accountprepaystime
    ADD CONSTRAINT billservice_accountprepaystime_prepaid_time_service_id_fkey FOREIGN KEY (prepaid_time_service_id) REFERENCES billservice_timeaccessservice(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2940 (class 2606 OID 4631652)
-- Dependencies: 1964 2007 2755
-- Name: billservice_accountprepaystrafic_prepaid_traffic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_accountprepaystrafic
    ADD CONSTRAINT billservice_accountprepaystrafic_prepaid_traffic_id_fkey FOREIGN KEY (prepaid_traffic_id) REFERENCES billservice_prepaidtraffic(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2941 (class 2606 OID 4631657)
-- Dependencies: 1966 1958 2668
-- Name: billservice_accountspeedlimit_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_accountspeedlimit
    ADD CONSTRAINT billservice_accountspeedlimit_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 2942 (class 2606 OID 4631662)
-- Dependencies: 1966 2017 2777
-- Name: billservice_accountspeedlimit_speedlimit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_accountspeedlimit
    ADD CONSTRAINT billservice_accountspeedlimit_speedlimit_id_fkey FOREIGN KEY (speedlimit_id) REFERENCES billservice_speedlimit(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 2943 (class 2606 OID 4631667)
-- Dependencies: 1968 1958 2668
-- Name: billservice_accounttarif_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_accounttarif
    ADD CONSTRAINT billservice_accounttarif_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2944 (class 2606 OID 4631672)
-- Dependencies: 1968 1939 2622
-- Name: billservice_accounttarif_tarif_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_accounttarif
    ADD CONSTRAINT billservice_accounttarif_tarif_id_fkey FOREIGN KEY (tarif_id) REFERENCES billservice_tariff(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 3009 (class 2606 OID 4632715)
-- Dependencies: 2061 2854 2081
-- Name: billservice_addonservice_nas_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_addonservice
    ADD CONSTRAINT billservice_addonservice_nas_id_fkey FOREIGN KEY (nas_id) REFERENCES nas_nas(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3010 (class 2606 OID 4632720)
-- Dependencies: 2081 2013 2768
-- Name: billservice_addonservice_sp_period_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_addonservice
    ADD CONSTRAINT billservice_addonservice_sp_period_id_fkey FOREIGN KEY (sp_period_id) REFERENCES billservice_settlementperiod(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3011 (class 2606 OID 4632725)
-- Dependencies: 2030 2797 2081
-- Name: billservice_addonservice_timeperiod_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_addonservice
    ADD CONSTRAINT billservice_addonservice_timeperiod_id_fkey FOREIGN KEY (timeperiod_id) REFERENCES billservice_timeperiod(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3012 (class 2606 OID 4632730)
-- Dependencies: 2081 2013 2768
-- Name: billservice_addonservice_wyte_period_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_addonservice
    ADD CONSTRAINT billservice_addonservice_wyte_period_id_fkey FOREIGN KEY (wyte_period_id) REFERENCES billservice_settlementperiod(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3013 (class 2606 OID 4632748)
-- Dependencies: 2083 2768 2013
-- Name: billservice_addonservicetarif_activation_count_period_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_addonservicetarif
    ADD CONSTRAINT billservice_addonservicetarif_activation_count_period_id_fkey FOREIGN KEY (activation_count_period_id) REFERENCES billservice_settlementperiod(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3014 (class 2606 OID 4632753)
-- Dependencies: 2083 2890 2081
-- Name: billservice_addonservicetarif_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_addonservicetarif
    ADD CONSTRAINT billservice_addonservicetarif_service_id_fkey FOREIGN KEY (service_id) REFERENCES billservice_addonservice(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3015 (class 2606 OID 4632758)
-- Dependencies: 2622 2083 1939
-- Name: billservice_addonservicetarif_tarif_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_addonservicetarif
    ADD CONSTRAINT billservice_addonservicetarif_tarif_id_fkey FOREIGN KEY (tarif_id) REFERENCES billservice_tariff(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3018 (class 2606 OID 4632800)
-- Dependencies: 2668 2087 1958
-- Name: billservice_addonservicetransaction_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_addonservicetransaction
    ADD CONSTRAINT billservice_addonservicetransaction_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3019 (class 2606 OID 4632805)
-- Dependencies: 2901 2087 2085
-- Name: billservice_addonservicetransaction_accountaddonservice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_addonservicetransaction
    ADD CONSTRAINT billservice_addonservicetransaction_accountaddonservice_id_fkey FOREIGN KEY (accountaddonservice_id) REFERENCES billservice_accountaddonservice(id) ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3020 (class 2606 OID 4632810)
-- Dependencies: 2693 1968 2087
-- Name: billservice_addonservicetransaction_accounttarif_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_addonservicetransaction
    ADD CONSTRAINT billservice_addonservicetransaction_accounttarif_id_fkey FOREIGN KEY (accounttarif_id) REFERENCES billservice_accounttarif(id) ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3021 (class 2606 OID 4632815)
-- Dependencies: 2890 2087 2081
-- Name: billservice_addonservicetransaction_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_addonservicetransaction
    ADD CONSTRAINT billservice_addonservicetransaction_service_id_fkey FOREIGN KEY (service_id) REFERENCES billservice_addonservice(id) ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3022 (class 2606 OID 4633004)
-- Dependencies: 2087 2836 2052
-- Name: billservice_addonservicetransaction_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_addonservicetransaction
    ADD CONSTRAINT billservice_addonservicetransaction_type_id_fkey FOREIGN KEY (type_id) REFERENCES billservice_transactiontype(internal_name) ON DELETE SET NULL;


--
-- TOC entry 2945 (class 2606 OID 4631677)
-- Dependencies: 1972 1958 2668
-- Name: billservice_card_account_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_card
    ADD CONSTRAINT billservice_card_account_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2946 (class 2606 OID 4631682)
-- Dependencies: 1972 1989 2729
-- Name: billservice_card_ipinuse_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_card
    ADD CONSTRAINT billservice_card_ipinuse_fkey FOREIGN KEY (ipinuse_id) REFERENCES billservice_ipinuse(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2947 (class 2606 OID 4631687)
-- Dependencies: 1972 2854 2061
-- Name: billservice_card_nas_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_card
    ADD CONSTRAINT billservice_card_nas_fkey FOREIGN KEY (nas_id) REFERENCES nas_nas(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2948 (class 2606 OID 4631692)
-- Dependencies: 1972 2622 1939
-- Name: billservice_card_tarif_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_card
    ADD CONSTRAINT billservice_card_tarif_fkey FOREIGN KEY (tarif_id) REFERENCES billservice_tariff(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2949 (class 2606 OID 4631697)
-- Dependencies: 1972 2024 2786
-- Name: billservice_card_template_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_card
    ADD CONSTRAINT billservice_card_template_fkey FOREIGN KEY (template_id) REFERENCES billservice_template(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2950 (class 2606 OID 4631702)
-- Dependencies: 2696 1974 1970
-- Name: billservice_dealer_bank_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_dealer
    ADD CONSTRAINT billservice_dealer_bank_id_fkey FOREIGN KEY (bank_id) REFERENCES billservice_bankdata(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 2951 (class 2606 OID 4631707)
-- Dependencies: 1974 1976 2704
-- Name: billservice_dealerpay_dealer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_dealerpay
    ADD CONSTRAINT billservice_dealerpay_dealer_id_fkey FOREIGN KEY (dealer_id) REFERENCES billservice_dealer(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2952 (class 2606 OID 4631712)
-- Dependencies: 2009 1976 2760
-- Name: billservice_dealerpay_salecard_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_dealerpay
    ADD CONSTRAINT billservice_dealerpay_salecard_id_fkey FOREIGN KEY (salecard_id) REFERENCES billservice_salecard(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2953 (class 2606 OID 4631717)
-- Dependencies: 1958 1978 2668
-- Name: billservice_document_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_document
    ADD CONSTRAINT billservice_document_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 2954 (class 2606 OID 4631722)
-- Dependencies: 1980 1978 2714
-- Name: billservice_document_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_document
    ADD CONSTRAINT billservice_document_type_id_fkey FOREIGN KEY (type_id) REFERENCES billservice_documenttype(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 2955 (class 2606 OID 4631727)
-- Dependencies: 1958 1982 2668
-- Name: billservice_globalstat_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_globalstat
    ADD CONSTRAINT billservice_globalstat_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 2956 (class 2606 OID 4631732)
-- Dependencies: 2723 1984 1986
-- Name: billservice_group_trafficclass_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_group_trafficclass
    ADD CONSTRAINT billservice_group_trafficclass_group_id_fkey FOREIGN KEY (group_id) REFERENCES billservice_group(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 2957 (class 2606 OID 4631737)
-- Dependencies: 2858 2063 1986
-- Name: billservice_group_trafficclass_trafficclass_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_group_trafficclass
    ADD CONSTRAINT billservice_group_trafficclass_trafficclass_id_fkey FOREIGN KEY (trafficclass_id) REFERENCES nas_trafficclass(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 2911 (class 2606 OID 4631742)
-- Dependencies: 1937 2668 1958
-- Name: billservice_groupstat_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_groupstat
    ADD CONSTRAINT billservice_groupstat_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 2912 (class 2606 OID 4631747)
-- Dependencies: 2723 1937 1984
-- Name: billservice_groupstat_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_groupstat
    ADD CONSTRAINT billservice_groupstat_group_id_fkey FOREIGN KEY (group_id) REFERENCES billservice_group(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 2958 (class 2606 OID 4631752)
-- Dependencies: 1991 1989 2734
-- Name: billservice_ipinuse_pool_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_ipinuse
    ADD CONSTRAINT billservice_ipinuse_pool_id_fkey FOREIGN KEY (pool_id) REFERENCES billservice_ippool(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 2913 (class 2606 OID 4631757)
-- Dependencies: 2668 1958 1938
-- Name: billservice_netflowstream_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_netflowstream
    ADD CONSTRAINT billservice_netflowstream_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2914 (class 2606 OID 4631762)
-- Dependencies: 2854 2061 1938
-- Name: billservice_netflowstream_nas_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_netflowstream
    ADD CONSTRAINT billservice_netflowstream_nas_id_fkey FOREIGN KEY (nas_id) REFERENCES nas_nas(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2915 (class 2606 OID 4631767)
-- Dependencies: 1938 1939 2622
-- Name: billservice_netflowstream_tarif_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_netflowstream
    ADD CONSTRAINT billservice_netflowstream_tarif_id_fkey FOREIGN KEY (tarif_id) REFERENCES billservice_tariff(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2916 (class 2606 OID 4631772)
-- Dependencies: 2042 1938 2817
-- Name: billservice_netflowstream_traffic_transmit_node_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_netflowstream
    ADD CONSTRAINT billservice_netflowstream_traffic_transmit_node_id_fkey FOREIGN KEY (traffic_transmit_node_id) REFERENCES billservice_traffictransmitnodes(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2959 (class 2606 OID 4631777)
-- Dependencies: 2622 1939 1994
-- Name: billservice_onetimeservice_tarif_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_onetimeservice
    ADD CONSTRAINT billservice_onetimeservice_tarif_id_fkey FOREIGN KEY (tarif_id) REFERENCES billservice_tariff(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2962 (class 2606 OID 4632026)
-- Dependencies: 1958 1996 2668
-- Name: billservice_onetimeservicehistory_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_onetimeservicehistory
    ADD CONSTRAINT billservice_onetimeservicehistory_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 2960 (class 2606 OID 4631782)
-- Dependencies: 1968 2693 1996
-- Name: billservice_onetimeservicehistory_accounttarif_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_onetimeservicehistory
    ADD CONSTRAINT billservice_onetimeservicehistory_accounttarif_id_fkey FOREIGN KEY (accounttarif_id) REFERENCES billservice_accounttarif(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2963 (class 2606 OID 4632031)
-- Dependencies: 1996 1994 2736
-- Name: billservice_onetimeservicehistory_onetimeservice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_onetimeservicehistory
    ADD CONSTRAINT billservice_onetimeservicehistory_onetimeservice_id_fkey FOREIGN KEY (onetimeservice_id) REFERENCES billservice_onetimeservice(id) ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 2961 (class 2606 OID 4631787)
-- Dependencies: 1996 2831 2050
-- Name: billservice_onetimeservicehistory_transaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_onetimeservicehistory
    ADD CONSTRAINT billservice_onetimeservicehistory_transaction_id_fkey FOREIGN KEY (transaction_id) REFERENCES billservice_transaction(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2964 (class 2606 OID 4631792)
-- Dependencies: 1998 2696 1970
-- Name: billservice_operator_bank_id; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_operator
    ADD CONSTRAINT billservice_operator_bank_id FOREIGN KEY (bank_id) REFERENCES billservice_bankdata(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2965 (class 2606 OID 4631797)
-- Dependencies: 2668 2000 1958
-- Name: billservice_organization_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_organization
    ADD CONSTRAINT billservice_organization_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 2966 (class 2606 OID 4631802)
-- Dependencies: 2013 2002 2768
-- Name: billservice_periodicalservice_settlement_period_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_periodicalservice
    ADD CONSTRAINT billservice_periodicalservice_settlement_period_id_fkey FOREIGN KEY (settlement_period_id) REFERENCES billservice_settlementperiod(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2967 (class 2606 OID 4631807)
-- Dependencies: 2002 2622 1939
-- Name: billservice_periodicalservice_tarif_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_periodicalservice
    ADD CONSTRAINT billservice_periodicalservice_tarif_id_fkey FOREIGN KEY (tarif_id) REFERENCES billservice_tariff(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2921 (class 2606 OID 4632019)
-- Dependencies: 2668 1940 1958
-- Name: billservice_periodicalservicehistory_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_periodicalservicehistory
    ADD CONSTRAINT billservice_periodicalservicehistory_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 2968 (class 2606 OID 4631812)
-- Dependencies: 2007 1984 2723
-- Name: billservice_prepaidtraffic_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_prepaidtraffic
    ADD CONSTRAINT billservice_prepaidtraffic_group_id_fkey FOREIGN KEY (group_id) REFERENCES billservice_group(id) ON DELETE CASCADE;


--
-- TOC entry 3006 (class 2606 OID 4632570)
-- Dependencies: 2622 2077 1939
-- Name: billservice_radiusattrs_tarif_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_radiusattrs
    ADD CONSTRAINT billservice_radiusattrs_tarif_id_fkey FOREIGN KEY (tarif_id) REFERENCES billservice_tariff(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 2971 (class 2606 OID 4631817)
-- Dependencies: 2010 2760 2009
-- Name: billservice_salecard_cards_salecard_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_salecard_cards
    ADD CONSTRAINT billservice_salecard_cards_salecard_id_fkey FOREIGN KEY (salecard_id) REFERENCES billservice_salecard(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2970 (class 2606 OID 4631822)
-- Dependencies: 2704 2009 1974
-- Name: billservice_salecard_dealer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_salecard
    ADD CONSTRAINT billservice_salecard_dealer_id_fkey FOREIGN KEY (dealer_id) REFERENCES billservice_dealer(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2972 (class 2606 OID 4631987)
-- Dependencies: 2015 1958 2668
-- Name: billservice_shedulelog_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY billservice_shedulelog
    ADD CONSTRAINT billservice_shedulelog_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2973 (class 2606 OID 4632586)
-- Dependencies: 2015 1968 2693
-- Name: billservice_shedulelog_accounttarif_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY billservice_shedulelog
    ADD CONSTRAINT billservice_shedulelog_accounttarif_id_fkey FOREIGN KEY (accounttarif_id) REFERENCES billservice_accounttarif(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 2974 (class 2606 OID 4631837)
-- Dependencies: 2017 2809 2038
-- Name: billservice_speedlimit_limit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_speedlimit
    ADD CONSTRAINT billservice_speedlimit_limit_id_fkey FOREIGN KEY (limit_id) REFERENCES billservice_trafficlimit(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 2975 (class 2606 OID 4631842)
-- Dependencies: 2668 1958 2019
-- Name: billservice_suspendedperiod_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_suspendedperiod
    ADD CONSTRAINT billservice_suspendedperiod_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 2993 (class 2606 OID 4631999)
-- Dependencies: 2021 2050 2782
-- Name: billservice_systemuser_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_transaction
    ADD CONSTRAINT billservice_systemuser_fkey FOREIGN KEY (systemuser_id) REFERENCES billservice_systemuser(id) ON DELETE SET NULL DEFERRABLE;


--
-- TOC entry 2917 (class 2606 OID 4631847)
-- Dependencies: 1956 2664 1939
-- Name: billservice_tariff_access_parameters_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_tariff
    ADD CONSTRAINT billservice_tariff_access_parameters_id_fkey FOREIGN KEY (access_parameters_id) REFERENCES billservice_accessparameters(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2918 (class 2606 OID 4631852)
-- Dependencies: 2013 2768 1939
-- Name: billservice_tariff_settlement_period_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_tariff
    ADD CONSTRAINT billservice_tariff_settlement_period_id_fkey FOREIGN KEY (settlement_period_id) REFERENCES billservice_settlementperiod(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2919 (class 2606 OID 4631857)
-- Dependencies: 1939 2028 2793
-- Name: billservice_tariff_time_access_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_tariff
    ADD CONSTRAINT billservice_tariff_time_access_service_id_fkey FOREIGN KEY (time_access_service_id) REFERENCES billservice_timeaccessservice(id);


--
-- TOC entry 2920 (class 2606 OID 4631862)
-- Dependencies: 1939 2828 2048
-- Name: billservice_tariff_traffic_transmit_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_tariff
    ADD CONSTRAINT billservice_tariff_traffic_transmit_service_id_fkey FOREIGN KEY (traffic_transmit_service_id) REFERENCES billservice_traffictransmitservice(id);


--
-- TOC entry 2976 (class 2606 OID 4631867)
-- Dependencies: 2024 2714 1980
-- Name: billservice_template_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_template
    ADD CONSTRAINT billservice_template_type_id_fkey FOREIGN KEY (type_id) REFERENCES billservice_documenttype(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 2977 (class 2606 OID 4631872)
-- Dependencies: 2793 2026 2028
-- Name: billservice_timeaccessnode_time_access_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_timeaccessnode
    ADD CONSTRAINT billservice_timeaccessnode_time_access_service_id_fkey FOREIGN KEY (time_access_service_id) REFERENCES billservice_timeaccessservice(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2978 (class 2606 OID 4631877)
-- Dependencies: 2026 2797 2030
-- Name: billservice_timeaccessnode_time_period_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_timeaccessnode
    ADD CONSTRAINT billservice_timeaccessnode_time_period_id_fkey FOREIGN KEY (time_period_id) REFERENCES billservice_timeperiod(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2979 (class 2606 OID 4631882)
-- Dependencies: 2797 2030 2032
-- Name: billservice_timeperiod_time_period_nodes_timeperiod_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_timeperiod_time_period_nodes
    ADD CONSTRAINT billservice_timeperiod_time_period_nodes_timeperiod_id_fkey FOREIGN KEY (timeperiod_id) REFERENCES billservice_timeperiod(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2980 (class 2606 OID 4631887)
-- Dependencies: 2034 2032 2803
-- Name: billservice_timeperiod_time_period_nodes_timeperiodnode_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_timeperiod_time_period_nodes
    ADD CONSTRAINT billservice_timeperiod_time_period_nodes_timeperiodnode_id_fkey FOREIGN KEY (timeperiodnode_id) REFERENCES billservice_timeperiodnode(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2981 (class 2606 OID 4631892)
-- Dependencies: 2664 2036 1956
-- Name: billservice_timespeed_access_parameters_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_timespeed
    ADD CONSTRAINT billservice_timespeed_access_parameters_id_fkey FOREIGN KEY (access_parameters_id) REFERENCES billservice_accessparameters(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2982 (class 2606 OID 4631897)
-- Dependencies: 2797 2030 2036
-- Name: billservice_timespeed_time_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_timespeed
    ADD CONSTRAINT billservice_timespeed_time_id_fkey FOREIGN KEY (time_id) REFERENCES billservice_timeperiod(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 3001 (class 2606 OID 4632068)
-- Dependencies: 1958 2668 2073
-- Name: billservice_timetransaction_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_timetransaction
    ADD CONSTRAINT billservice_timetransaction_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3002 (class 2606 OID 4632073)
-- Dependencies: 2793 2073 2028
-- Name: billservice_timetransaction_timeaccessservice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_timetransaction
    ADD CONSTRAINT billservice_timetransaction_timeaccessservice_id_fkey FOREIGN KEY (timeaccessservice_id) REFERENCES billservice_timeaccessservice(id) ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3003 (class 2606 OID 4632160)
-- Dependencies: 2622 2075 1939
-- Name: billservice_tpchangerule_from_tariff_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_tpchangerule
    ADD CONSTRAINT billservice_tpchangerule_from_tariff_id_fkey FOREIGN KEY (from_tariff_id) REFERENCES billservice_tariff(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3004 (class 2606 OID 4632165)
-- Dependencies: 2013 2075 2768
-- Name: billservice_tpchangerule_settlement_period_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_tpchangerule
    ADD CONSTRAINT billservice_tpchangerule_settlement_period_id_fkey FOREIGN KEY (settlement_period_id) REFERENCES billservice_settlementperiod(id) ON DELETE SET NULL;


--
-- TOC entry 3005 (class 2606 OID 4632170)
-- Dependencies: 2622 2075 1939
-- Name: billservice_tpchangerule_to_tariff_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_tpchangerule
    ADD CONSTRAINT billservice_tpchangerule_to_tariff_id_fkey FOREIGN KEY (to_tariff_id) REFERENCES billservice_tariff(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 2983 (class 2606 OID 4631902)
-- Dependencies: 2723 1984 2038
-- Name: billservice_trafficlimit_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_trafficlimit
    ADD CONSTRAINT billservice_trafficlimit_group_id_fkey FOREIGN KEY (group_id) REFERENCES billservice_group(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2984 (class 2606 OID 4631907)
-- Dependencies: 2768 2013 2038
-- Name: billservice_trafficlimit_settlement_period_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_trafficlimit
    ADD CONSTRAINT billservice_trafficlimit_settlement_period_id_fkey FOREIGN KEY (settlement_period_id) REFERENCES billservice_settlementperiod(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2985 (class 2606 OID 4631912)
-- Dependencies: 2038 1939 2622
-- Name: billservice_trafficlimit_tarif_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_trafficlimit
    ADD CONSTRAINT billservice_trafficlimit_tarif_id_fkey FOREIGN KEY (tarif_id) REFERENCES billservice_tariff(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2986 (class 2606 OID 4631917)
-- Dependencies: 2063 2858 2040
-- Name: billservice_trafficlimit_traffic_class_trafficclass_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_trafficlimit_traffic_class
    ADD CONSTRAINT billservice_trafficlimit_traffic_class_trafficclass_id_fkey FOREIGN KEY (trafficclass_id) REFERENCES nas_trafficclass(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2987 (class 2606 OID 4631922)
-- Dependencies: 2809 2038 2040
-- Name: billservice_trafficlimit_traffic_class_trafficlimit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_trafficlimit_traffic_class
    ADD CONSTRAINT billservice_trafficlimit_traffic_class_trafficlimit_id_fkey FOREIGN KEY (trafficlimit_id) REFERENCES billservice_trafficlimit(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2999 (class 2606 OID 4632045)
-- Dependencies: 2668 2071 1958
-- Name: billservice_traffictransaction_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_traffictransaction
    ADD CONSTRAINT billservice_traffictransaction_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3000 (class 2606 OID 4632050)
-- Dependencies: 2048 2071 2828
-- Name: billservice_traffictransaction_traffictransmitservice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_traffictransaction
    ADD CONSTRAINT billservice_traffictransaction_traffictransmitservice_id_fkey FOREIGN KEY (traffictransmitservice_id) REFERENCES billservice_traffictransmitservice(id) ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 2988 (class 2606 OID 4631927)
-- Dependencies: 2048 2042 2828
-- Name: billservice_traffictransmitnod_traffic_transmit_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_traffictransmitnodes
    ADD CONSTRAINT billservice_traffictransmitnod_traffic_transmit_service_id_fkey FOREIGN KEY (traffic_transmit_service_id) REFERENCES billservice_traffictransmitservice(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2989 (class 2606 OID 4631992)
-- Dependencies: 2042 1984 2723
-- Name: billservice_traffictransmitnodes_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_traffictransmitnodes
    ADD CONSTRAINT billservice_traffictransmitnodes_group_id_fkey FOREIGN KEY (group_id) REFERENCES billservice_group(id) ON DELETE CASCADE;


--
-- TOC entry 2990 (class 2606 OID 4631937)
-- Dependencies: 2797 2044 2030
-- Name: billservice_traffictransmitnodes_time_nodes_timeperiod_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_traffictransmitnodes_time_nodes
    ADD CONSTRAINT billservice_traffictransmitnodes_time_nodes_timeperiod_id_fkey FOREIGN KEY (timeperiod_id) REFERENCES billservice_timeperiod(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2991 (class 2606 OID 4631942)
-- Dependencies: 2046 2858 2063
-- Name: billservice_traffictransmitnodes_traffic_c_trafficclass_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_traffictransmitnodes_traffic_class
    ADD CONSTRAINT billservice_traffictransmitnodes_traffic_c_trafficclass_id_fkey FOREIGN KEY (trafficclass_id) REFERENCES nas_trafficclass(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2992 (class 2606 OID 4631947)
-- Dependencies: 2050 2668 1958
-- Name: billservice_transaction_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_transaction
    ADD CONSTRAINT billservice_transaction_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2994 (class 2606 OID 4632007)
-- Dependencies: 2050 1939 2622
-- Name: billservice_transaction_tarif_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_transaction
    ADD CONSTRAINT billservice_transaction_tarif_id_fkey FOREIGN KEY (tarif_id) REFERENCES billservice_tariff(id) ON DELETE SET NULL DEFERRABLE;


--
-- TOC entry 3007 (class 2606 OID 4632668)
-- Dependencies: 2079 1958 2668
-- Name: billservice_x8021_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_x8021
    ADD CONSTRAINT billservice_x8021_account_id_fkey FOREIGN KEY (account_id) REFERENCES billservice_account(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3008 (class 2606 OID 4632673)
-- Dependencies: 2061 2079 2854
-- Name: billservice_x8021_nas_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_x8021
    ADD CONSTRAINT billservice_x8021_nas_id_fkey FOREIGN KEY (nas_id) REFERENCES nas_nas(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 2927 (class 2606 OID 4631957)
-- Dependencies: 2056 2848 1948
-- Name: content_type_id_refs_id_728de91f; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT content_type_id_refs_id_728de91f FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2995 (class 2606 OID 4631962)
-- Dependencies: 2054 2056 2848
-- Name: django_admin_log_content_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_fkey FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2996 (class 2606 OID 4631967)
-- Dependencies: 2651 1950 2054
-- Name: django_admin_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2997 (class 2606 OID 4631972)
-- Dependencies: 2065 2063 2858
-- Name: nas_trafficnode_traffic_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY nas_trafficnode
    ADD CONSTRAINT nas_trafficnode_traffic_class_id_fkey FOREIGN KEY (traffic_class_id) REFERENCES nas_trafficclass(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 2923 (class 2606 OID 4632577)
-- Dependencies: 2073 2873 1941
-- Name: radius_session_transaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY radius_session
    ADD CONSTRAINT radius_session_transaction_id_fkey FOREIGN KEY (transaction_id) REFERENCES billservice_timetransaction(id) ON DELETE SET NULL DEFERRABLE;


--
-- TOC entry 2969 (class 2606 OID 4631977)
-- Dependencies: 2007 2048 2828
-- Name: traffic_transmit_service_id_refs_id_4797c3b9; Type: FK CONSTRAINT; Schema: public; Owner: ebs
--

ALTER TABLE ONLY billservice_prepaidtraffic
    ADD CONSTRAINT traffic_transmit_service_id_refs_id_4797c3b9 FOREIGN KEY (traffic_transmit_service_id) REFERENCES billservice_traffictransmitservice(id) ON DELETE CASCADE DEFERRABLE;


--
-- TOC entry 3125 (class 0 OID 0)
-- Dependencies: 6
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
REVOKE ALL ON SCHEMA public FROM ebs;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO ebs;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2009-08-29 17:57:20

--
-- PostgreSQL database dump complete
--

