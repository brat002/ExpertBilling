# -*- coding: utf-8 -*-

from tasks import subass_recreate, subass_delete

def get_account_data(account):
    
    tariff = account.get_account_tariff()
    accounttarif = account.get_accounttariff()
    data = {'account_id': account.id, 
            'ballance': account.ballance, 
            'credit': account.credit, 
            'datetime': account.created, 
            'tarif_id': tariff.id if tariff else '', 
            'access_parameters_id': tariff.access_parameters.id if tariff and tariff.access_parameters else '', 
            'time_access_service_id': tariff.time_access_service.id if tariff and tariff.time_access_service else '', 
            'traffic_transmit_service_id': tariff.traffic_transmit_service.id if tariff and tariff.traffic_transmit_service else '', 
            'cost': tariff.cost if tariff else '', 
            'reset_tarif_cost': tariff.reset_tarif_cost if tariff else '', 
            'settlement_period_id': tariff.settlement_period.id if tariff and tariff.settlement_period else '', 
            'tarif_active': tariff.active if tariff else '', 
            'acctf_id': accounttarif.id if accounttarif else '', 
            'account_created': account.created, 
            'disabled_by_limit': account.disabled_by_limit, 
            'balance_blocked': account.balance_blocked, 
            'allow_express_pay': account.allow_expresscards, 
            'account_status': account.status, 
            'username': account.username, 
            'password': account.password, 
            'require_tarif_cost': tariff.require_tarif_cost, 
            'radius_traffic_transmit_service_id': tariff.radius_traffic_transmit_service.id if tariff and tariff.radius_traffic_transmit_service else ''

            }
    return data
    
def get_subaccount_data(subaccount):
    
    data = {
            'id': subaccount.id, 
            'account_id': subaccount.account.id, 
            'username': subaccount.username, 
            'password': subaccount.password, 
            'vpn_ip_address': subaccount.vpn_ip_address, 
            'ipn_ip_address': subaccount.ipn_ip_address, 
            'ipn_mac_address': subaccount.ipn_mac_address, 
            'nas_id': subaccount.nas.id if subaccount.nas else '', 
            'ipn_added': subaccount.ipn_added, 
            'ipn_enabled': subaccount.ipn_enabled, 
            'need_resync': subaccount.need_resync, 
            'speed': subaccount.speed, 
            'switch_id': subaccount.switch.id if subaccount.switch else '', 
            'switch_port': subaccount.switch_port, 
            'allow_dhcp': subaccount.allow_dhcp, 
            'allow_dhcp_with_null': subaccount.allow_dhcp_with_null, 
            'allow_dhcp_with_minus': subaccount.allow_dhcp_with_minus , 
            'allow_dhcp_with_block': subaccount.allow_dhcp_with_block, 
            'allow_vpn_with_null': subaccount.allow_dhcp_with_null, 
            'allow_vpn_with_minus': subaccount.allow_vpn_with_minus, 
            'allow_vpn_with_block': subaccount.allow_vpn_with_block, 
            'associate_pptp_ipn_ip': subaccount.associate_pptp_ipn_ip, 
            'associate_pppoe_ipn_mac': subaccount.associate_pppoe_ipn_mac,  
            'ipn_speed': subaccount.ipn_speed, 
            'vpn_speed': subaccount.vpn_speed, 
            'allow_addonservice': subaccount.allow_addonservice, 
            'allow_ipn_with_null': subaccount.allow_ipn_with_null, 
            'allow_ipn_with_minus': subaccount.allow_ipn_with_minus, 
            'allow_ipn_with_block': subaccount.allow_ipn_with_block, 
            'vlan': subaccount.vlan,  
            'vpn_ipv6_ip_address': subaccount.vpn_ipv6_ip_address, 
            'ipv4_ipn_pool_id': subaccount.ipv4_ipn_pool_id, 
            'ipv4_vpn_pool_id': subaccount.ipv4_vpn_pool_id, 

            }
    
    return data

def get_nas_data(nas):
    if not nas: return {}
    data = {
            'id':nas.id, 
            'type':nas.type, 
            'name':nas.name, 
            'ipaddress':nas.ipaddress, 
            'secret':nas.secret, 
            'login':nas.login, 
            'password':nas.password, 
            'user_add_action':nas.user_add_action, 
            'user_enable_action':nas.user_enable_action, 
            'user_disable_action':nas.user_disable_action, 
            'user_delete_action':nas.user_delete_action, 
            'vpn_speed_action':nas.vpn_speed_action,  
            'ipn_speed_action':nas.ipn_speed_action, 
            'reset_action':nas.reset_action, 
            'speed_vendor_1':nas.speed_vendor_1, 
            'speed_vendor_2':nas.speed_vendor_2,  
            'speed_attr_id1':nas.speed_attr_id1, 
            'speed_attr_id2':nas.speed_attr_id2, 
            'speed_value1':nas.speed_value1,  
            'speed_value2':nas.speed_value2, 
            'identify':nas.identify, 
            'subacc_add_action':nas.subacc_add_action, 
            'subacc_enable_action':nas.subacc_enable_action, 
            'subacc_disable_action':nas.subacc_disable_action, 
            'subacc_del_action':nas.subacc_delete_action,  
            'subacc_ipn_speed_action':nas.subacc_ipn_speed_action,  
            'acct_interim_interval':nas.acct_interim_interval, 
            }
    return data

def subaccount_ipn_recreate(account, subaccount, nas, access_type):
    subacc_recreate.delay(get_account_data(account), get_subaccount_data(subaccount), nas, access_type)

def subaccount_ipn_delete(account, subaccount, nas, access_type):
    subass_delete.delay(get_account_data(account), get_subaccount_data(subaccount), get_nas_data(nas), access_type)
    