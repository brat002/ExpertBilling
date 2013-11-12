# -*- coding=utf-8 -*-
from django.db import models
from ebscab.nas.models import Nas
from billservice.models import Account

def create_nas(name=None):
        
    nas = Nas()
    nas.name = name if name else 'nas_test'
    nas.ipaddress = 'test_address'
    nas.secret = 'test_secret'    
    nas.save()
    
    return nas

def create_user(username=None, password=None):
    
    user = Account()
    user.username = username if username else 'test' 
    user.password = password if password else 'test' 
    user.city='Minsk'
    user.region=''
    user.street=''
    user.house=''
    user.house_bulk = ''
    user.entrance = ''
    user.room=''
    user.ballance=566 
    user.nas= create_nas()
    user.vlan=1 
    user.allow_webcab=True 
    user.allow_expresscards = True
    user.assign_dhcp_null = True
    user.assign_dhcp_block = True
    user.allow_vpn_null = True
    user.allow_vpn_block = True
    
    user.save()
    
    return user