
nf_sql = {'nas':"SELECT id, ipaddress from nas_nas;",
          'accounts':"SELECT ba.id as account_id, array(SELECT sa.vpn_ip_address || '|' || sa.ipn_ip_address || '|' || sa.nas_id FROM billservice_subaccount as sa WHERE sa.account_id=ba.id) as addresses, bacct.id as acctf_id, bacct.tarif_id FROM billservice_account AS ba JOIN billservice_accounttarif AS bacct ON bacct.id=(SELECT id FROM billservice_accounttarif AS att WHERE  att.account_id=ba.id and att.datetime<%s  ORDER BY datetime DESC LIMIT 1);",
          'nnodes':"SELECT weight, traffic_class_id, store, direction, passthrough, protocol, dst_port, src_port, src_ip as src_ip_src_mask, dst_ip as dst_ip_dst_mask, next_hop FROM nas_trafficnode AS tn JOIN nas_trafficclass AS tc ON tn.traffic_class_id=tc.id ORDER BY tc.weight, tc.passthrough;",
          'groups':"SELECT id, ARRAY(SELECT trafficclass_id from billservice_group_trafficclass as bgtc WHERE bgtc.group_id = bsg.id) AS trafficclass, direction, type FROM billservice_group AS bsg;",
          'tgroups':"SELECT tarif_id, int_array_aggregate(group_id) AS group_ids FROM (SELECT tarif_id, group_id FROM billservice_trafficlimit UNION SELECT bt.id, btn.group_id FROM billservice_tariff AS bt JOIN billservice_traffictransmitnodes AS btn ON bt.traffic_transmit_service_id=btn.traffic_transmit_service_id WHERE btn.group_id IS NOT NULL UNION SELECT bt.id, bpt.group_id FROM billservice_tariff AS bt JOIN billservice_prepaidtraffic AS bpt ON bt.traffic_transmit_service_id=bpt.traffic_transmit_service_id WHERE bpt.group_id IS NOT NULL) AS tarif_group GROUP BY tarif_id;"}
#'accounts': "SELECT ba.id as account_id, array[ba.ipn_ip_address || '|' || ba.vpn_ip_address  || '|' || ba.nas_id] ||  array(SELECT ipn_ip_address || '|' || vpn_ip_address || '|' || nas_id FROM billservice_subaccount WHERE account_id=ba.id) addresses, bacct.id as acctf_id, bacct.tarif_id FROM billservice_account AS ba JOIN billservice_accounttarif AS bacct ON bacct.id=(SELECT id FROM billservice_accounttarif AS att WHERE att.account_id=ba.id and att.datetime<%s) ORDER BY datetime DESC LIMIT 1);",

nfroutine_sql = \
              {'accounts':"""SELECT ba.id, ba.ballance, ba.credit, act.datetime, bt.id, bt.access_parameters_id, bt.time_access_service_id, bt.traffic_transmit_service_id, bt.cost,bt.reset_tarif_cost, bt.settlement_period_id, bt.active, act.id, ba.status   
                                FROM billservice_account as ba
                                LEFT JOIN billservice_accounttarif AS act ON act.id=(SELECT id FROM billservice_accounttarif AS att WHERE att.account_id=ba.id and att.datetime<%s ORDER BY datetime DESC LIMIT 1)
                                LEFT JOIN billservice_tariff AS bt ON bt.id=act.tarif_id;""",
               'tts'     :"""SELECT id, reset_traffic, cash_method, period_check FROM billservice_traffictransmitservice;""",
               'settlepd':"""SELECT id, time_start, length, length_in, autostart FROM billservice_settlementperiod;""",
               'period'  :"""SELECT tpn.time_start, tpn.length, tpn.repeat_after, ttns.traffic_transmit_service_id
                                FROM billservice_timeperiodnode AS tpn
                                JOIN billservice_timeperiod_time_period_nodes AS timeperiod_timenodes ON timeperiod_timenodes.timeperiodnode_id=tpn.id
                                JOIN billservice_traffictransmitnodes_time_nodes AS ttntp ON ttntp.timeperiod_id=timeperiod_timenodes.timeperiod_id
                                JOIN billservice_traffictransmitnodes AS ttns ON ttns.id=ttntp.traffictransmitnodes_id;""",
               'nodes'   :"""SELECT ttsn.id, ttsn.cost, ttsn.edge_start, ttsn.edge_end, tpn.time_start, tpn.length, tpn.repeat_after,
                                        ttsn.group_id, ttsn.traffic_transmit_service_id, ttsn.edge_value 
                                        FROM billservice_traffictransmitnodes as ttsn
                                        JOIN billservice_timeperiodnode AS tpn on tpn.id IN 
                                        (SELECT timeperiodnode_id FROM billservice_timeperiod_time_period_nodes WHERE timeperiod_id IN 
                                        (SELECT timeperiod_id FROM billservice_traffictransmitnodes_time_nodes WHERE traffictransmitnodes_id=ttsn.id));""",
               'prepays' :"""SELECT prepais.id, prepais.size, prepais.account_tarif_id, prepaidtraffic.group_id, prepaidtraffic.traffic_transmit_service_id 
                                        FROM billservice_accountprepaystrafic as prepais
                                        JOIN billservice_prepaidtraffic as prepaidtraffic ON prepaidtraffic.id=prepais.prepaid_traffic_id
                                        WHERE prepais.size>0 AND prepais.current=True and(ARRAY[prepais.account_tarif_id] && get_cur_acct(%s));""",
               'sclasses':"""SELECT int_array_aggregate(id) FROM nas_trafficclass WHERE store=TRUE;""",
               'group_bytes': 
                          """SELECT ba.id AS account_id, bt.id AS tarif_id, act.id AS acctf_id, act.datetime, ARRAY(SELECT ROW(bgps.group_id, SUM(bgps.bytes))::group_bytes FROM billservice_groupstat AS bgps WHERE (bgps.account_id = act.account_id) AND (bgps.group_id IN (SELECT bttn2.group_id FROM billservice_traffictransmitnodes as bttn2 WHERE bttn2.traffic_transmit_service_id = bt.traffic_transmit_service_id)) AND (bgps.datetime BETWEEN act.datetime AND %s) GROUP BY bgps.group_id ORDER BY bgps.group_id) AS gr_bytes 
                                FROM billservice_tariff AS bt 
                                JOIN billservice_accounttarif AS act ON 
                                    EXISTS (SELECT 1 FROM billservice_traffictransmitnodes as bttn1 WHERE bttn1.traffic_transmit_service_id = bt.traffic_transmit_service_id AND bttn1.edge_value > 0) 
                                    AND act.tarif_id=bt.id
                                    AND act.id=(SELECT id FROM billservice_accounttarif AS att WHERE att.account_id=act.account_id and att.datetime<%s ORDER BY datetime DESC LIMIT 1)               
                                JOIN billservice_account as ba ON  
                                    ba.id = act.account_id               
                                ORDER BY bt.id, ba.id;""",
              'tarif_groups':
                          """SELECT bt.id AS tarif_id,  ARRAY(SELECT ROW(bttn1.group_id, sort_asc(int_array_aggregate(bttn1.edge_value::integer)))::group_nodes FROM billservice_traffictransmitnodes as bttn1 WHERE bttn1.traffic_transmit_service_id = bt.traffic_transmit_service_id AND (bttn1.edge_value > 0) GROUP BY bttn1.group_id ORDER BY bttn1.group_id) AS gr_nodes 
                                FROM billservice_tariff AS bt 
                                WHERE EXISTS (SELECT 1 FROM billservice_traffictransmitnodes AS bttn2 WHERE bttn2.traffic_transmit_service_id = bt.traffic_transmit_service_id AND bttn2.edge_value > 0)
                                ORDER BY bt.id;"""}

core_sql = \
         {'accounts':"""SELECT ba.id, ba.ballance, ba.credit, date_trunc('second', act.datetime), bt.id, bt.access_parameters_id, bt.time_access_service_id, bt.traffic_transmit_service_id, bt.cost,bt.reset_tarif_cost, bt.settlement_period_id, bt.active, act.id, FALSE, ba.created, ba.disabled_by_limit, ba.balance_blocked, ba.nas_id, ba.vpn_ip_address, ba.ipn_ip_address,ba.ipn_mac_address, ba.assign_ipn_ip_from_dhcp, ba.ipn_status, ba.ipn_speed, ba.vpn_speed, ba.ipn_added, bt.ps_null_ballance_checkout, bt.deleted, bt.allow_express_pay, ba.status, ba.allow_vpn_null, ba.allow_vpn_block, ba.username, ba.password, bt.require_tarif_cost, act.periodical_billed, TRUE, False, ba.allow_ipn_with_null, ba.allow_ipn_with_minus, ba.allow_ipn_with_block, bt.radius_traffic_transmit_service_id  
                        FROM billservice_account as ba
                        LEFT JOIN billservice_accounttarif AS act ON act.id=(SELECT id FROM billservice_accounttarif AS att WHERE att.account_id=ba.id and att.datetime<%s ORDER BY datetime DESC LIMIT 1)
                        LEFT JOIN billservice_tariff AS bt ON bt.id=act.tarif_id;""",
          'underbilled_per_accs': 
                     """SELECT ba.id, ba.ballance, ba.credit, date_trunc('second', act.datetime), bt.id, bt.access_parameters_id, bt.time_access_service_id, bt.traffic_transmit_service_id, bt.cost,bt.reset_tarif_cost, bt.settlement_period_id, bt.active, act.id, FALSE, ba.created, ba.disabled_by_limit, ba.balance_blocked, ba.nas_id, ba.vpn_ip_address, ba.ipn_ip_address,ba.ipn_mac_address, ba.assign_ipn_ip_from_dhcp, ba.ipn_status, ba.ipn_speed, ba.vpn_speed, ba.ipn_added, bt.ps_null_ballance_checkout, bt.deleted, bt.allow_express_pay, ba.status, ba.allow_vpn_null, ba.allow_vpn_block, ba.username, ba.password, bt.require_tarif_cost, act.periodical_billed, FALSE    
                            FROM billservice_account as ba
                            LEFT JOIN billservice_accounttarif AS act ON ba.id=act.account_id  
                            LEFT JOIN billservice_tariff AS bt ON bt.id=act.tarif_id WHERE act.datetime >= (SELECT datetime FROM billservice_accounttarif AS att WHERE att.id=act.id AND att.periodical_billed IS FALSE ORDER BY datetime ASC LIMIT 1) AND act.datetime<%s AND bt.active ORDER by ba.id, act.datetime DESC;""",
          'traftrss':"""SELECT id, reset_traffic, cash_method, period_check FROM billservice_traffictransmitservice;""",
          'radiustraftrss':"""SELECT id, direction, tarification_step, rounding, prepaid_direction, prepaid_value, reset_prepaid_traffic FROM billservice_radiustraffic;""",
          'radiustrafnodes':"""select radiustraffic_id, "value",timeperiod_id, "cost"  from billservice_radiustrafficnode;""",
          'settlper':"""SELECT id, date_trunc('second', time_start), length, length_in, autostart FROM billservice_settlementperiod;""",
          'nas'     :"""SELECT id, type, name, ipaddress, secret, login, password, allow_pptp, allow_pppoe, allow_ipn, user_add_action, user_enable_action, user_disable_action, user_delete_action, vpn_speed_action, ipn_speed_action, reset_action, confstring, multilink, speed_vendor_1, speed_vendor_2, speed_attr_id1, speed_attr_id2, speed_value1, speed_value2, identify, subacc_add_action, subacc_enable_action, subacc_disable_action,subacc_delete_action, subacc_ipn_speed_action, acct_interim_interval FROM nas_nas;""",
          'defsp'   :"""SELECT accessparameters.max_limit,accessparameters.burst_limit,
                        accessparameters.burst_treshold, accessparameters.burst_time,
                        accessparameters.priority, accessparameters.min_limit,
                        tariff.id
                        FROM billservice_accessparameters as accessparameters
                        JOIN billservice_tariff as tariff ON tariff.access_parameters_id=accessparameters.id;""",
          'newsp'   :"""SELECT timespeed.max_limit,timespeed.burst_limit,
                        timespeed.burst_treshold,timespeed.burst_time,
                        timespeed.priority, timespeed.min_limit,
                        timenode.time_start, timenode.length, timenode.repeat_after,
                        tariff.id 
                        FROM billservice_timespeed as timespeed
                        JOIN billservice_tariff as tariff ON tariff.access_parameters_id=timespeed.access_parameters_id
                        JOIN billservice_timeperiod_time_period_nodes as tp ON tp.timeperiod_id=timespeed.time_id
                        JOIN billservice_timeperiodnode as timenode ON tp.timeperiodnode_id=timenode.id;""",
          'periodtf':"""SELECT id, settlement_period_id FROM billservice_tariff  as tarif
                        WHERE id in (SELECT tarif_id FROM billservice_periodicalservice WHERE deleted=False or deleted is Null) AND tarif.active=True""",
          'periodset':"""SELECT b.id, b.name, b.cost, b.cash_method, c.name, date_trunc('second', c.time_start),
                        c.length, c.length_in, c.autostart, b.tarif_id, b.condition, b.created, b.deactivated, b.deleted
                        FROM billservice_periodicalservice as b 
                        JOIN billservice_settlementperiod as c ON c.id=b.settlement_period_id
                        WHERE deactivated is Null or (deactivated>=%s) and (deleted=False or deleted is Null);""",
          'timeaccnode':"""SELECT tan.time_period_id, tan.cost, tan.time_access_service_id
                        FROM billservice_timeaccessnode as tan
                        JOIN billservice_timeperiod as tp ON tan.time_period_id=tp.id;""",
          'timepnode':"""SELECT tpn.id, tpn.name, date_trunc('second', tpn.time_start), tpn.length, tpn.repeat_after, tptpn.timeperiod_id 
                        FROM billservice_timeperiodnode as tpn
                        JOIN billservice_timeperiod_time_period_nodes as tptpn ON tpn.id=tptpn.timeperiodnode_id;""",
          'tlimits'  :"""SELECT trafficlimit.id, trafficlimit.tarif_id, trafficlimit."name", 
                        trafficlimit.settlement_period_id, trafficlimit.size, trafficlimit.group_id, 
                        trafficlimit."mode", trafficlimit.action,
                        speedlimit.id, speedlimit.speed_units, speedlimit.change_speed_type 
                        FROM billservice_trafficlimit as trafficlimit
                        LEFT JOIN billservice_speedlimit as speedlimit ON speedlimit.limit_id=trafficlimit.id
                        ORDER BY trafficlimit.size DESC;""",
          'shllog'  :"""SELECT id,account_id, ballance_checkout,date_trunc('second', prepaid_traffic_reset) , date_trunc('second', prepaid_traffic_accrued), 
                        date_trunc('second', prepaid_time_reset), date_trunc('second', prepaid_time_accrued), date_trunc('second', prepaid_radius_traffic_reset), date_trunc('second', prepaid_radius_traffic_accrued), date_trunc('second', balance_blocked), accounttarif_id 
                        FROM billservice_shedulelog;""",
          'timeaccs' :"""SELECT id, prepaid_time, reset_time, rounding, tarification_step FROM billservice_timeaccessservice;""",
          'onetimes' :"""SELECT id, tarif_id, cost, created FROM billservice_onetimeservice;""",
          'accpars'  :"""SELECT id, access_type, access_time_id, max_limit, min_limit, 
                        burst_limit,burst_treshold,burst_time, priority, ipn_for_vpn FROM billservice_accessparameters;""",
          'ipnspeed' :"""SELECT id, account_id, speed, state, static, datetime FROM billservice_accountipnspeed;""",
          'otshist'  :"""SELECT id, accounttarif_id, onetimeservice_id FROM billservice_onetimeservicehistory WHERE ARRAY[accounttarif_id] && get_cur_acct(%s);""", 
          'suspended':"""SELECT id, account_id, start_date, end_date FROM billservice_suspendedperiod WHERE (%s BETWEEN start_date AND end_date);""",
          'tpnaccess':"""SELECT date_trunc('second', tpn.time_start) as time_start, tpn.length as length, tpn.repeat_after as repeat_after, bst.id
                        FROM billservice_timeperiodnode as tpn
                        JOIN billservice_timeperiod_time_period_nodes as tpnds ON tpnds.timeperiodnode_id=tpn.id
                        JOIN billservice_accessparameters AS ap ON ap.access_time_id=tpnds.timeperiod_id
                        JOIN billservice_tariff AS bst ON bst.access_parameters_id=ap.id""",
          'speed_lmt':"""SELECT accountspeedlimit.id, accountspeedlimit.account_id, speedlimit.max_tx, speedlimit.max_rx, 
                      speedlimit.burst_tx, speedlimit.burst_rx, 
                      speedlimit.burst_treshold_tx, speedlimit.burst_treshold_rx, 
                      speedlimit.burst_time_tx, speedlimit.burst_time_rx, 
                      speedlimit.priority,
                      speedlimit.min_tx, speedlimit.min_rx, speedlimit.speed_units, speedlimit.change_speed_type
                      FROM billservice_speedlimit as speedlimit, billservice_accountspeedlimit as accountspeedlimit
                      WHERE accountspeedlimit.speedlimit_id=speedlimit.id;""",
          'addon_service':
                      """SELECT id, "name", allow_activation, service_type, sp_type, sp_period_id, 
                                timeperiod_id, "cost", cancel_subscription, wyte_period_id, wyte_cost, 
                                "action", nas_id, service_activation_action, service_deactivation_action, 
                                deactivate_service_for_blocked_account, change_speed, change_speed_type, 
                                speed_units, max_tx, max_rx, burst_tx, burst_rx, burst_treshold_tx, 
                                burst_treshold_rx, burst_time_tx, burst_time_rx, min_tx, min_rx, 
                                priority
                           FROM billservice_addonservice;""",
          'addon_tarif':
                      """SELECT id, tarif_id, service_id, activation_count, activation_count_period_id
                           FROM billservice_addonservicetarif;""",
          'addon_account':
                      """SELECT accs.id, accs.service_id, accs.account_id, date_trunc('second',accs.activated), date_trunc('second',accs.deactivated), accs.action_status, 

                                accs.speed_status, accs.temporary_blocked, date_trunc('second',accs.last_checkout), accs.subaccount_id

                           FROM billservice_accountaddonservice as accs 
                           JOIN billservice_addonservice as addons ON addons.id=accs.service_id
                           WHERE (accs.deactivated is Null or (accs.last_checkout<accs.deactivated AND (SELECT service_type FROM billservice_addonservice as adds WHERE adds.id=accs.id)='periodical') or 
                           ((SELECT service_type FROM billservice_addonservice as adds WHERE adds.id=accs.service_id)='onetime' and (accs.action_status=True or accs.last_checkout is Null))) or (accs.action_status=True and accs.deactivated is not Null and addons.action=True);""",
        'addon_periodical': """SELECT accas.id, ads.name, ads.cost, ads.sp_type, sp.name, sp.time_start,
                        sp.length, sp.length_in, sp.autostart,
                        accas.account_id, accas.activated, accas.deactivated, accas.temporary_blocked, accas.last_checkout,ads.id, accas.subaccount_id
                        FROM billservice_addonservice AS ads JOIN billservice_settlementperiod AS sp ON ads.sp_period_id = sp.id JOIN billservice_accountaddonservice AS accas ON accas.service_id = ads.id 
                        WHERE ads.service_type = 'periodical' AND (accas.deactivated ISNULL OR accas.last_checkout ISNULL OR NOT accas.last_checkout >= accas.deactivated);"""}
rad_sql = \
        {'accounts'  :"""SELECT ba.id, ba.username, ba.ipn_mac_address, bt.time_access_service_id, 
                        ba.password, ba.nas_id, ba.vpn_ip_address, bt.id, accps.access_type, 
                        ba.status, ba.balance_blocked, (ba.ballance+ba.credit) as ballance, 
                        ba.disabled_by_limit, ba.vpn_speed, bt.active, 
                        ba.allow_vpn_null, ba.allow_vpn_block, ba.ipn_ip_address, ba.ipn_speed, ba.assign_dhcp_null, ba.assign_dhcp_block, ba.associate_pptp_ipn_ip, ba.associate_pppoe_mac, bt.radius_traffic_transmit_service_id 
                        FROM billservice_account as ba
                        JOIN billservice_accounttarif AS act ON act.id=(SELECT id FROM billservice_accounttarif AS att WHERE att.account_id=ba.id and att.datetime<%s ORDER BY datetime DESC LIMIT 1)
                        JOIN billservice_tariff AS bt ON bt.id=act.tarif_id
                        LEFT JOIN billservice_accessparameters as accps on accps.id = bt.access_parameters_id ;""",
         'nas'      :"""SELECT id, secret, type, multilink, ipaddress, identify, speed_vendor_1, speed_vendor_2, speed_attr_id1, speed_attr_id2, speed_value1, speed_value2, acct_interim_interval FROM nas_nas ORDER BY id, ipaddress, identify;""",
         'period'   :"""SELECT tpn.time_start::timestamp without time zone as time_start, tpn.length as length, tpn.repeat_after as repeat_after, bst.id
                        FROM billservice_timeperiodnode as tpn
                        JOIN billservice_timeperiod_time_period_nodes as tpnds ON tpnds.timeperiodnode_id=tpn.id
                        JOIN billservice_accessparameters AS ap ON ap.access_time_id=tpnds.timeperiod_id
                        JOIN billservice_tariff AS bst ON bst.access_parameters_id=ap.id""",
         'defspeed' :"""SELECT accessparameters.max_limit,accessparameters.burst_limit,
                        accessparameters.burst_treshold, accessparameters.burst_time,
                        accessparameters.priority, accessparameters.min_limit,
                        tariff.id
                        FROM billservice_accessparameters as accessparameters
                        JOIN billservice_tariff as tariff ON tariff.access_parameters_id=accessparameters.id;""",
         'speed'    :"""SELECT timespeed.max_limit,timespeed.burst_limit,
                        timespeed.burst_treshold,timespeed.burst_time,
                        timespeed.priority, timespeed.min_limit,
                        timenode.time_start, timenode.length, timenode.repeat_after,
                        tariff.id 
                        FROM billservice_timespeed as timespeed
                        JOIN billservice_tariff as tariff ON tariff.access_parameters_id=timespeed.access_parameters_id
                        JOIN billservice_timeperiod_time_period_nodes as tp ON tp.timeperiod_id=timespeed.time_id
                        JOIN billservice_timeperiodnode as timenode ON tp.timeperiodnode_id=timenode.id;""",
         'limit'    :"""SELECT accountspeedlimit.id, accountspeedlimit.account_id, speedlimit.max_tx, speedlimit.max_rx, 
                        speedlimit.burst_tx, speedlimit.burst_rx, 
                        speedlimit.burst_treshold_tx, speedlimit.burst_treshold_rx, 
                        speedlimit.burst_time_tx, speedlimit.burst_time_rx, 
                        speedlimit.priority,
                        speedlimit.min_tx, speedlimit.min_rx, speedlimit.speed_units, speedlimit.change_speed_type
                        FROM billservice_speedlimit as speedlimit, billservice_accountspeedlimit as accountspeedlimit
                        WHERE accountspeedlimit.speedlimit_id=speedlimit.id;""",
         'attrs'    :"""SELECT vendor, attrid, value, tarif_id FROM billservice_radiusattrs;""",
         'subaccounts'    :"""SELECT id, account_id, username, password, vpn_ip_address, ipn_ip_address, ipn_mac_address, nas_id, ipn_added, ipn_enabled, need_resync, speed, switch_id, switch_port, allow_dhcp, allow_dhcp_with_null, allow_dhcp_with_minus, allow_dhcp_with_block, allow_vpn_with_null, allow_vpn_with_minus, allow_vpn_with_block, associate_pptp_ipn_ip, associate_pppoe_ipn_mac, ipn_speed, vpn_speed, allow_addonservice, allow_ipn_with_null, allow_ipn_with_minus, allow_ipn_with_block, vlan, vpn_ipv6_ip_address FROM billservice_subaccount;""",

}