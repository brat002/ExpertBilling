#-*- coding=utf-8 -*-

#global connection
import sys, traceback, os
from types import NoneType
sys.path.append(os.path.abspath('../'))
from PyQt4 import QtCore, QtGui
from helpers import Object as Object
from helpers import connlogin
import ConfigParser
#===============================================================================
import threading
#===============================================================================
import urllib
import urllib2
import json
import random
import time
import socket
from json import JSONDecoder
import datetime
import decimal
from db import AttrDict

def default(obj):
    '''Convert object to JSON encodable type.'''
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')

    return simplejson.JSONEncoder.default(self, obj)

def default_detail(obj):
    '''Convert object to JSON encodable type.'''
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S.%f')

    return simplejson.JSONEncoder.default(self, obj)

class HttpBot(object):
    """an HttpBot represents one browser session, with cookies."""
    def __init__(self, widget, host):
        self.host = host
        self.widget = widget
        self.username=''
        self.pasword = ''
        cookie_handler= urllib2.HTTPCookieProcessor()
        redirect_handler= urllib2.HTTPRedirectHandler()
        self._opener = urllib2.build_opener(redirect_handler, cookie_handler)

    def GET(self, url):
        return self._opener.open(url).read()

    def get_id(self):
        return random.randint(100000,999999999)
    
    def POST(self, url, parameters={}):
        attempts=0
        #print parameters
        if parameters and '__dict__' in parameters:
            for key in parameters.__dict__:
                value = parameters[key]
                    
                print "key, value", key, value
    
                
                if isinstance(value, unicode):
                    parameters[key] = value.encode('utf-8')
                elif isinstance(value, datetime.datetime):
                    parameters[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(value, NoneType):
                    parameters[key] = ''
                elif isinstance(value, list):
                    parameters[key] = ','.join(map(str, value))
                else:
                    parameters[key] = value

        else:
            for key in parameters.keys():
                value = parameters[key]
                    
                print "key, value", key, value
    
                
                if isinstance(value, unicode):
                    parameters[key] = value.encode('utf-8')
                elif isinstance(value, datetime.datetime):
                    parameters[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(value, NoneType):
                    parameters[key] = ''
                elif isinstance(value, list):
                    parameters[key] = ','.join(map(str, value))
                else:
                    parameters[key] = value
            
        #print 'parameters', parameters
        print "parameters=", parameters     
        error = ''    
        while attempts<=3:
            try:
                data=self._opener.open(url+"?uniqid=%s" % self.get_id(), urllib.urlencode(parameters)).read()
                return self.parse(data)
            except urllib2.HTTPError, e:
                print 'The server couldn\'t fulfill the request.'
                print 'Error code: ', e.code
                k = open("trace.html", "w")
                k.write('\n'.join(e.readlines()))
                k.close()
                attempts+=1
                error = unicode(str(e))
                
            except urllib2.URLError, e:
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason
                error = unicode(str(e))
                attempts+=1
        if error:
            QtGui.QMessageBox.warning(self.widget, unicode(u"Ошибка"), error)
            
        

    
    def parse(self, data):
        if not data: return {}
        #print "before parce=", data
        d = json.loads(data,  object_hook=AttrDict, parse_float=decimal.Decimal)
        #print 'after parce', d
        if hasattr(d, 'status') and d.status==True:

            return d
        elif hasattr(d, 'status') and d.status==False:
            if hasattr(d, 'message'):
                return d
            else:
                return d
        else:
            return d
    
    def warning(self, title, message, errors=[]):
            if errors:
                QtGui.QMessageBox.warning(self.widget, unicode(u"Внимание"), unicode('\n'.join(["%s %s" % (x, ';'.join(errors.get(x))) for x in errors])))
            if message:
                QtGui.QMessageBox.warning(self.widget, unicode(u"Ошибка"), unicode("%s" % message))

    def error(self, response, title=u'Ошибка!'):
            if 'errors' in response:
                print response
                QtGui.QMessageBox.critical(self.widget, unicode(u"Внимание"), unicode('\n'.join(["%s %s" % (x, ';'.join(response.errors.get(x))) for x in response.errors])))
            if 'message' in response:
                QtGui.QMessageBox.critical(self.widget, unicode(u"Ошибка"), unicode("%s" % response.message))
                      
    def log_in(self, name, password):
        url='http://%s/ebsadmin/simple_login/' % self.host 
        self.username=name
        self.password = password
        d = self.POST(url, {'username':name, 'password':password})
        if d and not d.status:
            self.error(d)
            return
        return d

    def get_settlementperiods(self,id=None, autostart=None, fields=[]):
        url='http://%s/ebsadmin/settlementperiods/' % self.host 
        
        d = self.POST(url,{'data': json.dumps({'fields':fields, 'id':id, 'autostart':autostart}, ensure_ascii=False, default=default)})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    

    def get_accessparameters(self,id=None, fields=[]):
        url='http://%s/ebsadmin/accessparameters/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def get_timeperiods(self,id=None, fields=[]):
        url='http://%s/ebsadmin/timeperiods/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def get_timeperiods(self,id=None, fields=[]):
        url='http://%s/ebsadmin/timeperiods/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def get_timenodes(self,id=None, period_id=None, fields=[]):
        url='http://%s/ebsadmin/timeperiodnodes/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'period_id':period_id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d,id)
    
    def get_accounttariffs(self,account_id=None, fields=[]):
        url='http://%s/ebsadmin/accounttariffs/' % self.host 
        
        d = self.POST(url,{ 'account_id':account_id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d)

    def get_authgroups(self, id=None, fields=[]):
        url='http://%s/ebsadmin/authgroups/' % self.host 
        
        d = self.POST(url,{ 'id':id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def postprocess(self,response, id=None):
        if id:
            if response.totalCount==1:
                return response.records[0]
        if response.totalCount>0:
            return response.records
        if response.totalCount==0:
            return response.records
        return response
    
    def get_suspendedperiods(self,id=None, account_id=None, fields=[]):
        url='http://%s/ebsadmin/suspendedperiods/' % self.host 
        
        d = self.POST(url,{'id':id,  'account_id':account_id})
        #print d
        return self.postprocess(d, id)
    
    def get_templates(self,id=None, type_id=None, fields=[]):
        url='http://%s/ebsadmin/templates/' % self.host 
        
        d = self.POST(url,{'id':id,  'fields':fields, 'type_id':type_id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def get_tariff_for_account(self,id=None, fields=[]):
        url='http://%s/ebsadmin/tariffforaccount/' % self.host 
        
        d = self.POST(url,{'id':id,  'fields':fields})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def get_accounts_for_cachier(self, fullname, city, street, house, bulk, room, username, agreement, phone_h, phone_m):
        url='http://%s/ebsadmin/accountsforcashier/' % self.host 
        
        d = self.POST(url,{"data": json.dumps({"fullname": fullname, "city":city, "street":street, "house": house, "bulk": bulk, "room":room, "username": username, "agreement": agreement, "phone_h": phone_h, "phone_m": phone_m}, ensure_ascii=False)})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d)
    
    def get_cards(self,id=None, fields=[]):
        url='http://%s/ebsadmin/cards/' % self.host 
        
        d = self.POST(url,{'id':id,  'fields':fields})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)

    def get_model(self, id, table, fields=[], where={}):
        url='http://%s/ebsadmin/api/getmodel/' % self.host 
        
        d = self.POST(url,{'data':json.dumps({'id':id,  'table':table, 'fields': fields, 'where':where}, default=default)})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def get_models(self, table, fields=[], where={}, order = {'id':'ASC',}):
        url='http://%s/ebsadmin/api/getmodels/' % self.host 
        
        d = self.POST(url,{'data':json.dumps({'order':order,  'table':fields, 'fields': fields, 'where':where}, default=default)})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d)
    
    def cards_save(self,model):
        url='http://%s/ebsadmin/cards/set/' % self.host 
        
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return True

    def cards_delete(self,id):
        url='http://%s/ebsadmin/cards/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return d
    def transaction_delete(self,data):
        url='http://%s/ebsadmin/transactions/delete/' % self.host 
        #print model
        d = self.POST(url,{'data':json.dumps(data, ensure_ascii=False, default=default_detail)})
        if not d.status:
            self.error(d)
            return
        return d
    
    
    def set_cardsstatus(self, ids=[], status=True):
        url='http://%s/ebsadmin/cards/status/set/' % self.host 
        
        d = self.POST(url,{'data':json.dumps({'ids':ids, 'status':status})})
        if not d.status:
            self.error(d)
            return
        return True
    
    def get_subaccounts(self, id='', account_id='', fields=[], normal_fields=True):
        url='http://%s/ebsadmin/subaccounts/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'account_id':account_id, 'normal_fields':normal_fields})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def get_accountaddonservices(self, id=None, account_id=None, subaccount_id=None, normal_fields = False, fields=[]):
        url='http://%s/ebsadmin/accountaddonservices/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'account_id':account_id, 'subaccount_id':subaccount_id, 'normal_fields':normal_fields})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
        
    def get_accounthardware(self, id=None, account_id=None, hardware_id=None, fields=[]):
        url='http://%s/ebsadmin/accounthardware/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'account_id':account_id, 'hardware_id':hardware_id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def accounthardware_save(self,model):
        url='http://%s/ebsadmin/accounthardware/set/' % self.host 
        
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return True
    
    def accounthardware_delete(self,id):
        url='http://%s/ebsadmin/accounthardware/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return d
    
    def get_news(self, id=None, fields=[]):
        url='http://%s/ebsadmin/news/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, })
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def news_save(self,model, accounts=[]):
        url='http://%s/ebsadmin/news/set/' % self.host 
        
        d = self.POST(url,{'data':json.dumps({'model':model, 'accounts':accounts}, ensure_ascii=False, default=default)})
        if not d.status:
            self.error(d)
            return
        return True
    
    def news_delete(self,id):
        url='http://%s/ebsadmin/news/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return d
    
    def get_account(self, id=None, fields=[], limit=None):
        url='http://%s/ebsadmin/account/' % self.host 
        
        d = self.POST(url,{'data':json.dumps({'fields':fields, 'id':id, 'limit':limit})})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
            
    def account_ipn_for_vpn(self, id):
        url='http://%s/ebsadmin/account/ipnforvpn/' % self.host 
        
        d = self.POST(url,{'id':id})
        #print d
        return d
    
    def pod(self, session, id):
        url='http://%s/ebsadmin/sessions/reset/' % self.host 
        
        d = self.POST(url,{'id':id, 'sessionod':sessionid})
        if not d.status:
            self.error(d)
            return
        return d

    
    def change_tarif(self, ids,tarif,date):
        url='http://%s/ebsadmin/accounttariffs/bathset/' % self.host 
        

        d = self.POST(url,{'accounts':ids, 'tariff':tarif, 'date':date})
        if not d.status:
            self.error(d)
            return
        #print d
        return d
    
    def get_mac_for_ip(self, nas_id, ipn_ip):
        url='http://%s/ebsadmin/getmacforip/' % self.host 
        
        d = self.POST(url,{'nas_id':nas_id, 'ipn_ip_address':ipn_ip})
        #print d
        return d
        
    def accountActions(self, account_id, subaccount_id, action):
        url='http://%s/ebsadmin/actions/set/' % self.host 
        
        d = self.POST(url,{'account_id':account_id, 'subaccount_id':subaccount_id, 'action':action})
        #print d
        return d
    
    def get_pool_by_ipinuse(self, ipinuse):
        url='http://%s/ebsadmin/pools/getbyipinuse/' % self.host 
        
        d = self.POST(url,{'ipinuse':ipinuse})
        #print d
        return d
    def check_account_exists(self, username):
        url='http://%s/ebsadmin/account/exists/' % self.host 
        
        d = self.POST(url,{'username':username})
        #print d
        return d
    
    def account_save(self, model, organization, bank, tarif_id=None, template_id=None):
        url='http://%s/ebsadmin/account/save/' % self.host 


        d = self.POST(url, {'data':json.dumps({'tarif_id':tarif_id, 'model':model, 'organization': organization, 'bank':bank},ensure_ascii = False, default=default)})
        if not d.status:
            self.error(d)
            return
        return d

    def subaccount_save(self, model):
        url='http://%s/ebsadmin/subaccounts/set/' % self.host 
        #print model

        #print a
        #print dir(a)
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return d
    
    
    
    def get_transactiontypes(self,id=None, fields=[]):
        url='http://%s/ebsadmin/transactiontypes/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
      
    def get_transaction(self,id=None, normal_fields = False, limit=1, fields=[]):
        url='http://%s/ebsadmin/transaction/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'normal_fields':normal_fields, 'limit':limit})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def transactionreport(self, request):
        url='http://%s/ebsadmin/transactionreport/' % self.host 
        
        d = self.POST(url,{'data':json.dumps(request, default=default)})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d)
    
    def sp_info(self, settlement_period_id, time_start=None, curdatetime=None):
        url='http://%s/ebsadmin/spinfo/' % self.host 
        
        d = self.POST(url,{'data':json.dumps({'settlement_period_id':settlement_period_id, 'time_start':time_start, 'curdatetime':curdatetime}, default=default)})
        if not d.status:
            self.error(d)
            return
        data = self.postprocess(d, 1)

        return data.start, data.end, data.length

    def transactiontypes_save(self, model):
        url='http://%s/ebsadmin/transactiontypes/set/' % self.host 
        #print model
        d = self.POST(url,model)
        #print d
        return d

    def timeperiod_save(self, model):
        url='http://%s/ebsadmin/timeperiods/save/' % self.host 
        #print model
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return d
    
    def timeperiod_delete(self,id):
        url='http://%s/ebsadmin/timeperiods/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return d
    
    def timeperiodnode_save(self, model):
        url='http://%s/ebsadmin/timeperiodnodes/save/' % self.host 
        #print model
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return d
   
    def timeperiodnode_delete(self,id):
        url='http://%s/ebsadmin/timeperiodnodes/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return d

    def timeperiodnode_m2m_save(self, model):
        url='http://%s/ebsadmin/timeperiodnodes/m2m/save/' % self.host 
        #print model
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return d

    def timeperiodnodes_m2m_delete(self, period_id, node_id):
        url='http://%s/ebsadmin/timeperiodnodes/m2m/delete/' % self.host 
        #print model
        d = self.POST(url,{'period_id':period_id, 'node_id':node_id})
        if not d.status:
            self.error(d)
            return
        return d    

    def settlementperiod_save(self, model):
        url='http://%s/ebsadmin/settlementperiods/save/' % self.host 
        #print model
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return d
    
    def commit(self):
        pass
    def rollback(self):
        pass
    
    def sql(self, s):
        url='http://%s/ebsadmin/sql/' % self.host 
        
        d = self.POST(url,{'sql':s})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d)

    def get(self, s):
        url='http://%s/ebsadmin/sql/' % self.host 
        
        d = self.POST(url,{'sql':s})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, 1)
    
    def settlementperiod_delete(self,id):
        url='http://%s/ebsadmin/settlementperiods/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return d

    def get_organizations(self,id=None, account_id=None, fields=[]):
        url='http://%s/ebsadmin/organizations/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'account_id':account_id})
        if not d.status:
            self.error(d)
            return
        return  self.postprocess(d, id if id else account_id)    


       
    def get_log_messages(self, systemuser_id, start_date, end_date):
        url='http://%s/ebsadmin/actionlogs/' % self.host 
        
        d = self.POST(url,{"data":json.dumps({ 'systemuser': systemuser_id, 'start_date': start_date, 'end_date':end_date}, default=default)})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d)    
          
    def list_logfiles(self):
        url='http://%s/ebsadmin/listlogfiles/' % self.host 
        
        d = self.POST(url,{})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d)    
    
    def get_tail_log(self, log_name, log_count, all_file = False):
        url='http://%s/ebsadmin/gettaillog/' % self.host 
        
        d = self.POST(url,{"log_name": log_name, 'log_count':log_count, 'all_file':all_file})
        if not d.status:
            self.error(d)
            return
        return d
    

     
    def get_banks(self,id=None,  fields=[]):
        url='http://%s/ebsadmin/banks/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def banks_save(self,model):
        url='http://%s/ebsadmin/banks/set/' % self.host 

        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return d
    
    def get_sessions(self,  id=None, account_id=None, date_start='', date_end='', only_active=True,  fields=[]):
        url='http://%s/ebsadmin/sessions/' % self.host 
        print 'acc_id', account_id
        d = self.POST(url,{'fields':fields, 'id':id, 'account':account_id, 'date_start':date_start, 'date_end':date_end, 'only_active':only_active})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def get_salecards(self,id=None, dealer_id=None, fields=[]):
        url='http://%s/ebsadmin/salecards/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'dealer_id':dealer_id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)

    def get_dealerpays(self,id=None, dealer_id=None, fields=[]):
        url='http://%s/ebsadmin/dealerpays/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'dealer_id':dealer_id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def add_dealerpay(self,model):
        url='http://%s/ebsadmin/dealerpays/set/' % self.host 
        
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return True
 
    def return_cards(self, dealer_id, cards=[]):
        url='http://%s/ebsadmin/returncards/' % self.host 
        
        d = self.POST(url,{'data':json.dumps({'dealer_id':dealer_id, 'cards':cards})})
        if not d.status:
            self.error(d)
            return
        return True
       
    def salecards_save(self,model, cards=[]):
        url='http://%s/ebsadmin/salecards/set/' % self.host 
        
        d = self.POST(url,{'data':json.dumps({'model':model, 'cards':cards}, default=default)})
        if not d.status:
            self.error(d)
            return
        return True
    
    def salecards_delete(self,id):
        url='http://%s/ebsadmin/salecards/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return d
    
    def get_cities(self,id=None, fields=[]):
        url='http://%s/ebsadmin/cities/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)

    def city_save(self,model):
        url='http://%s/ebsadmin/cities/set/' % self.host 
        
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return True
    
    def city_delete(self,id):
        url='http://%s/ebsadmin/cities/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return d
    
    def get_streets(self,id=None, city_id=None, fields=[]):
        url='http://%s/ebsadmin/streets/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'city_id':city_id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def street_save(self, model):
        url='http://%s/ebsadmin/streets/set/' % self.host 
        
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return True
    
    def street_delete(self,id):
        url='http://%s/ebsadmin/streets/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return d
    
    def get_houses(self,id=None, street_id=None, fields=[]):
        url='http://%s/ebsadmin/houses/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'street_id':street_id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def get_classnodes(self,id=None, traffic_class_id=None, fields=[]):
        url='http://%s/ebsadmin/trafficclassnodes/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'traffic_class_id':traffic_class_id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)

    def classnodes_save(self, model):
        url='http://%s/ebsadmin/trafficclassnodes/set/' % self.host 
        
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return True
    
    def classnodes_delete(self,id):
        url='http://%s/ebsadmin/trafficclassnodes/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return d
    
    def house_save(self, model):
        url='http://%s/ebsadmin/houses/set/' % self.host 
        
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return True

    def house_delete(self,id):
        url='http://%s/ebsadmin/houses/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return d
    
    def template_delete(self,id):
        url='http://%s/ebsadmin/houses/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return d
    
    def get_contracttemplates(self,id=None, fields=[]):
        url='http://%s/ebsadmin/contracttemplates/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def get_hardware(self,id=None, model_id=None,  normal_fields=False, fields=[]):
        url='http://%s/ebsadmin/hardware/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'normal_fields':normal_fields, 'model_id':model_id, })
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)

    def hardware_save(self,model):
        url='http://%s/ebsadmin/hardware/set/' % self.host 
        
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return True
    
    def hardware_delete(self,id):
        url='http://%s/ebsadmin/hardware/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return d
    
    def get_manufacturers(self,id=None, fields=[]):
        url='http://%s/ebsadmin/manufacturers/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)

    def manufacturers_save(self,model):
        url='http://%s/ebsadmin/manufacturers/set/' % self.host 
        
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return True
    
    def manufacturers_delete(self,id):
        url='http://%s/ebsadmin/manufacturers/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return d
    
    
    def get_hardwaretypes(self,id=None, fields=[]):
        url='http://%s/ebsadmin/hardwaretypes/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def hardwaretypes_save(self,model):
        url='http://%s/ebsadmin/hardwaretypes/set/' % self.host 
        
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return True
    
    def hardwaretypes_delete(self,id):
        url='http://%s/ebsadmin/hardwaretypes/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return d
    
    def get_hwmodels(self,id=None, hardwaretype_id=None, manufacturer_id = None, normal_fields=False,  fields=[]):
        url='http://%s/ebsadmin/hwmodels/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'hardwaretype_id':hardwaretype_id, 'manufacturer_id':manufacturer_id,  'normal_fields':normal_fields})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def hwmodels_save(self,model):
        url='http://%s/ebsadmin/hwmodels/set/' % self.host 
        
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return True
    
    def hwmodels_delete(self,id):
        url='http://%s/ebsadmin/hwmodels/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return d
    
    def get_tariffs(self,id=None, fields=[], normal_fields=False):
        
        url='http://%s/ebsadmin/tariffs/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id})
        if not d.status:
            self.error(message=d.message)
            return

        if id:
            if d.totalCount==1:
                return d.records[0]
        if d.totalCount>0:
            return d.records
        if d.totalCount==0:
            return d.records
        return d
    
    def get_nasses(self, id=None, fields=[]):
        url='http://%s/ebsadmin/nasses/' % self.host 
        
        d = self.POST(url, {'fields':fields, 'id':id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)

    def accountsfilter(self, sql=None, fields=[]):
        url='http://%s/ebsadmin/accountsfilter/' % self.host 
        
        d = self.POST(url, {'data': json.dumps(sql,  ensure_ascii=False, default=default)})
        
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d)
    
    def get_groups(self, id=None, fields=[], normal_fields=False):
        url='http://%s/ebsadmin/groups/' % self.host 
        
        d = self.POST(url, {'fields':fields, 'id':id, 'normal_fields':normal_fields})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def groups_detail(self):
        url='http://%s/ebsadmin/groups_detail/' % self.host 
        
        d = self.POST(url)
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d)
    
    def get_trafficclasses(self, id=None, fields=[]):
        url='http://%s/ebsadmin/trafficclasses/' % self.host 
        
        d = self.POST(url, {'fields':fields, 'id':id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    

    def trafficclasses_save(self, model):
        url='http://%s/ebsadmin/trafficclasses/set/' % self.host 
        
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return True

    def trafficclasses_delete(self,id):
        url='http://%s/ebsadmin/trafficclasses/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return d
    
    def get_class_for_group(self, group=None, fields=[]):
        url='http://%s/ebsadmin/classforgroup/' % self.host 
        
        d = self.POST(url, {'fields':fields, 'group':group})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d)
                            
    def get_ippools(self,id=None, fields=[], type=None):
        url='http://%s/ebsadmin/ippools/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'type':type})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)

    def ippool_save(self,model):
        url='http://%s/ebsadmin/ippools/set/' % self.host 
        #print model
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return d
    
    def ippool_delete(self,id):
        url='http://%s/ebsadmin/ippools/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return d
    
    def get_radiusattrs(self, id=None, tarif_id=None, nas_id=None,fields=[]):
        url='http://%s/ebsadmin/radiusattrs/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'tarif_id':tarif_id, 'nas_id':nas_id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def get_accountprepaysradiustrafic(self, id=None, fields=[]):
        url='http://%s/ebsadmin/accountprepaysradiustrafic/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def accountprepaysradiustrafic_save(self,model):
        url='http://%s/ebsadmin/accountprepaysradiustrafic/set/' % self.host 
        #print model
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return d
    
    
    def get_accountprepaystrafic(self, id=None, fields=[]):
        url='http://%s/ebsadmin/accountprepaystrafic/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def accountprepaystrafic_save(self,model):
        url='http://%s/ebsadmin/accountprepaystrafic/set/' % self.host 
        #print model
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return d
    
    def radiusattrs_save(self,model):
        url='http://%s/ebsadmin/radiusattrs/set/' % self.host 
        #print model
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return d
    
    def radiusattrs_delete(self,id):
        url='http://%s/ebsadmin/radiusattrs/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return d

    
    def template_save(self,model):
        url='http://%s/ebsadmin/templates/save/' % self.host 
        #print model
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return d

    def template_delete(self,id):
        url='http://%s/ebsadmin/templstes/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return d
    
    def get_cards_nominal(self):
        url='http://%s/ebsadmin/getcardsnominal/' % self.host 
        
        d = self.POST(url)
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d)
    
    def get_next_cardseries(self):
    
        url='http://%s/ebsadmin/getnextcardseries/' % self.host 
        
        d = self.POST(url)
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d)
    
    def get_templatetypes(self,id=None, fields=[]):
        url='http://%s/ebsadmin/templatetypes/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def get_periodicalservices(self, id=None, tarif_id=None, deleted=False, fields=[], normal_fields=False):
        url='http://%s/ebsadmin/periodicalservices/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'tarif':tarif_id, 'deleted':deleted, 'normal_fields':normal_fields})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
        
    def get_timeaccessservices(self,id=None, fields=[]):
        url='http://%s/ebsadmin/timeaccessservices/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id,})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    
    def get_timespeeds(self,id=None, fields=[], access_parameters=None, normal_fields=True):
        url='http://%s/ebsadmin/timespeeds/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'type':type, 'access_parameters':access_parameters, 'normal_fields':normal_fields})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def get_timeaccessservices_nodes(self, id=None, service_id=None, fields=[], normal_fields=True):
        url='http://%s/ebsadmin/timeaccessservices/nodes/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'service_id':service_id, 'normal_fields':normal_fields})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def get_traffictransmitnodes(self, id=None, service_id=None, fields=[], normal_fields=True):
        url='http://%s/ebsadmin/traffictransmit/nodes/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'service_id':service_id, 'normal_fields':normal_fields})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    
    def get_traffictransmitservices(self, id=None,  fields=[], normal_fields=True):
        url='http://%s/ebsadmin/traffictransmitservices/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id,  'normal_fields':normal_fields})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def get_prepaidtraffic(self, id=None, service_id=None, fields=[], normal_fields=True):
        url='http://%s/ebsadmin/prepaidtraffic/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'service_id':service_id, 'normal_fields':normal_fields})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    
    
    def get_radiustrafficservices(self, id=None, fields=[], normal_fields=True):
        url='http://%s/ebsadmin/radiustrafficservices/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'normal_fields':normal_fields})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def get_speedlimites(self, id=None, limit_id=None, fields=[], normal_fields=True):
        url='http://%s/ebsadmin/speedlimites/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'limit_id':limit_id, 'normal_fields':normal_fields})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def get_addonservicetariff(self, id=None, tarif_id=None, fields=[], normal_fields=True):
        url='http://%s/ebsadmin/addonservicetariff/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'tarif_id':tarif_id, 'normal_fields':normal_fields})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def get_onetimeservices(self, id=None, tarif_id=None, fields=[], normal_fields=True):
        url='http://%s/ebsadmin/onetimeservices/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'tarif_id':tarif_id, 'normal_fields':normal_fields})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def get_trafficlimites(self, id=None, tarif_id=None, fields=[], normal_fields=True):
        url='http://%s/ebsadmin/trafficlimites/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'tarif_id':tarif_id, 'normal_fields':normal_fields})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    
    def get_radiustrafficservices_nodes(self, id=None, service_id=None, fields=[], normal_fields=True):
        url='http://%s/ebsadmin/radiustrafficservices/nodes/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'service_id':service_id, 'normal_fields':normal_fields})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def get_ips_from_ippool(self,pool_id):
        url='http://%s/ebsadmin/ipaddress/getfrompool/' % self.host 
        
        d = self.POST(url,{'pool_id':pool_id})
        #print d
        return d
    
    
    def get_ports_status(self, switch_id):
        url='http://%s/ebsadmin/getportsstatus/' % self.host 
        
        d = self.POST(url,{ 'switch_id':switch_id})
        if not d.status:
            self.error(d)
            return
        return d
    
    def set_portsstatus(self, switch_id):
        url='http://%s/ebsadmin/setportsstatus/' % self.host 
        
        d = self.POST(url,{ 'switch_id':switch_id})
        if not d.status:
            self.error(d)
            return
        return d
    
    def get_switches(self,id=None, fields=[]):
        url='http://%s/ebsadmin/switches/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def switches_save(self, model):
        url='http://%s/ebsadmin/switches/set/' % self.host 
        #print model
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return d
    
    def switches_delete(self,id):
        url='http://%s/ebsadmin/switches/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return True
    
    def get_systemusers(self,id=None, fields=[]):
        url='http://%s/ebsadmin/systemusers/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    

    def get_tpchangerules(self,id=None, normal_fields=False, fields=[]):
        url='http://%s/ebsadmin/tpchangerules/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'normal_fields':normal_fields})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)
    
    def tpchangerules_save(self, model):
        url='http://%s/ebsadmin/tpchangerules/set/' % self.host 
        #print model
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return True
    
    def tpchangerules_delete(self,id):
        url='http://%s/ebsadmin/tpchangerules/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return True
    
    def systemusers_save(self, model):
        url='http://%s/ebsadmin/systemusers/set/' % self.host 
        #print model
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return True
    
    def systemuser_delete(self,id):
        url='http://%s/ebsadmin/systemusers/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return True
    
    def get_addonservices(self,id=None, fields=[], normal_fields=True):
        url='http://%s/ebsadmin/addonservices/' % self.host 
        
        d = self.POST(url,{'fields':fields, 'id':id, 'normal_fields':normal_fields})
        
        if not d.status:
            self.error(message=d.message)
            return

        if id:
            if d.totalCount==1:
                return d.records[0]
        if d.totalCount>0:
            return d.records
        if d.totalCount==0:
            return d.records
        return d
    
    def get_operator(self,id=None, fields=[], normal_fields=True):
        url='http://%s/ebsadmin/operator/' % self.host 
        
        d = self.POST(url)
        
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id=1)
    
    def operator_save(self, op_model, bank_model):
        url='http://%s/ebsadmin/operator/set/' % self.host 
        #print model

        d = self.POST(url,{'data':json.dumps({'op_model':op_model, 'bank_model':bank_model},  ensure_ascii=False, default=default)})

        if not d.status:
            self.error(d)
            return
        return d
    
    def gettariffs(self, fields=[]):
        url='http://%s/ebsadmin/gettariffs/' % self.host 
        
        d = self.POST(url,{})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d)
    
    def get_dealers(self, id=None, fields=[]):
        url='http://%s/ebsadmin/dealers/' % self.host 
        
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d, id)

    def dealers_save(self,model):
        url='http://%s/ebsadmin/dealers/set/' % self.host 
        #print model
        d = self.POST(url,model)
        #print d
        return d
    
    def dealers_delete(self,model):
        url='http://%s/ebsadmin/dealers/delete/' % self.host 
        #print model
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return d
    
    def get_notsold_cards(self, ids=[], fields=[]):
        url='http://%s/ebsadmin/getnotsoldcards/' % self.host 
        
        d = self.POST(url,{'ids':ids})
        print d
        if not d.status:
            self.error(d)
            return
        return self.postprocess(d)
    
    def accountsfortariff(self, tarif_id ):
        url='http://%s/ebsadmin/accountsfortariff/' % self.host 
        
        d = self.POST(url,{'tarif_id':tarif_id})

        if not d.status:
            self.error(d)
            return
        return self.postprocess(d)
    
    def make_transaction(self, model ):
        url='http://%s/ebsadmin/transaction/set/' % self.host 
        
        d = self.POST(url,{'data':json.dumps(model,  ensure_ascii=False, default=default)})
        #print d
        return d
    
    def nas_save(self,model):
        url='http://%s/ebsadmin/nasses/save/' % self.host 
        #print model
        d = self.POST(url,model)
        #print d
        return d
    
    def contracttemplate_save(self,model):
        url='http://%s/ebsadmin/contracttemplate/set/' % self.host 
        #print model
        d = self.POST(url,model)
        #print d
        return d
    
    def contracttemplate_delete(self,model):
        url='http://%s/ebsadmin/contracttemplate/delete/' % self.host 
        #print model
        d = self.POST(url,model)
        if not d.status:
            self.error(d)
            return
        return d
    
    def tariff_delete(self, id):
        url='http://%s/ebsadmin/tariffs/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return d
    
    def tariff_save(self, data):
        url='http://%s/ebsadmin/tariffs/set/' % self.host 
        #print model
        print data
        d = self.POST(url,{'data':json.dumps(data,  ensure_ascii=False, default=default)})
        print "d.status", d.status, type(d.status)
        if not d.status:
            self.error(d)
            return
        return d

    def addonservice_save(self, data):
        url='http://%s/ebsadmin/addonservices/set/' % self.host 
        #print model

        d = self.POST(url,{'data':json.dumps(data,  ensure_ascii=False, default=default)})

        if not d.status:
            self.error(d)
            return
        return True
    
    def accountaddonservice_save(self, model):
        url='http://%s/ebsadmin/accountaddonservices/set/' % self.host 
        #print model
        d = self.POST(url,model)
        print "d.status", d.status, type(d.status)
        if not d.status:
            self.error(d)
            return
        return True
    
    def accounttarif_save(self, model):
        url='http://%s/ebsadmin/accounttariffs/set/' % self.host 
        #print model
        d = self.POST(url,model)
        print "d.status", d.status, type(d.status)
        if not d.status:
            self.error(errors=d.errors)
            return
        return True

    def suspendedperiod_save(self, model):
        url='http://%s/ebsadmin/suspendedperiod/set/' % self.host 
        #print model
        d = self.POST(url,model)
        print "d.status", d.status, type(d.status)
        if not d.status:
            self.error(response=d)
            return
        return True

    def group_save(self, model):
        url='http://%s/ebsadmin/groups/set/' % self.host 
        #print model
        d = self.POST(url,model)

        if not d.status:
            self.error(d)
            return
        return True
    
    def nas_delete(self,id):
        url='http://%s/ebsadmin/nasses/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        #print d
        return d

    def group_delete(self,id):
        url='http://%s/ebsadmin/groups/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        #print d
        return d
    
    def account_delete(self,id):
        url='http://%s/ebsadmin/account/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return d
    
    def addonservice_delete(self,id):
        url='http://%s/ebsadmin/addonservices/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(d)
            return
        return d
    
    def accounttariff_delete(self,id):
        url='http://%s/ebsadmin/accounttariffs/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.error(message=d.message)
            return
        return d

    def delete_suspendedperiod(self,id):
        url='http://%s/ebsadmin/suspendedperiod/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        if not d.status:
            self.postprocess(d)
            return
        return d
    
    def subaccount_delete(self,id):
        url='http://%s/ebsadmin/subaccount/delete/' % self.host 
        #print model
        d = self.POST(url,{'id':id})
        #print d
        return d
    
    
    def testCredentials(self, host, login, password):
        url='http://%s/ebsadmin/test_credentials/' % self.host 
        
        d = self.POST(url,{'host':host, 'login':login, 'password':password,})
        #print d
        return d
    
from dateutil.relativedelta import relativedelta

DEFAULT_PORT = 7771
LOG_LEVEL    = 0
ROLE = 0

class PrintLogger(object):
    def __getattr__(self, name):
        return self.lprint
    
    def lprint(self, *args):
        if len(args) == 1:
            print 'LOGGER: ', args[0]
        elif len(args) == 2:
            print 'LOGGER: ', args[0] % args[1]


import isdlogger

import mdi_rc

from AccountFrame import AccountsMdiEbs as AccountsMdiChild
from NasFrame import NasEbs
from SettlementPeriodFrame import SettlementPeriodEbs as SettlementPeriodChild
from TimePeriodFrame import TimePeriodChildEbs as TimePeriodChild
from ClassFrame import ClassChildEbs as ClassChild
from MonitorFrame import MonitorEbs as MonitorFrame
from PoolFrame import PoolEbs as PoolFrame
from SystemUser import SystemEbs
from CustomForms import ConnectDialog, ConnectionWaiting, OperatorDialog, RrdReportMainWindow
from Reports import NetFlowReportEbs as NetFlowReport, StatReport , LogViewWindow, SimpleReportEbs
from CardsFrame import CardsChildEbs as CardsChild
from DealerFrame import DealerMdiEbs as DealerMdiChild
from CustomForms import TemplatesWindow, SqlDialog
from TPChangeRules import TPRulesEbs
from AddonServiceFrame import AddonServiceEbs
from MessagesFrame import MessagesEbs
from LogFrame import LogViewEbs
from AddressFrame import AddressEbs
from Reports import TransactionsReportEbs as TransactionsReport
from TransactionTypeFrame import TransactionTypeEbs
from SwitchFrame import SwitchEbs
from HardwareFrame import HardwareManufacturerEbs,HardwareTypeEbs,ModelWindowEbs,HardwareWindowEbs

_reportsdict = [['Статистика по группам',[['report3_users.xml', ['groups'], 'Общий трафик']]],\
                ['Глобальная статистика',[['report3_users.xml', ['gstat_globals'], 'Общий трафик'],['report3_users.xml', ['gstat_multi'], 'Трафик с выбором классов'], ['report3_pie.xml', ['pie_gmulti'], 'Пирог']]],\
                ['Другие отчёты',[['report3_sess.xml', ['sessions'], 'Сессии пользователей'], ['report3_tr.xml', ['trans_crd'], 'Динамика прибыли']]]]

#разделитель для дат по умолчанию
dateDelim = "."


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        self.workspace = QtGui.QWorkspace()

        self.setCentralWidget(self.workspace)

        self.connect(self.workspace, QtCore.SIGNAL("windowActivated(QWidget *)"), self.updateMenus)
        self.windowMapper = QtCore.QSignalMapper(self)
        self.connect(self.windowMapper, QtCore.SIGNAL("mapped(QWidget *)"),
                     self.workspace, QtCore.SLOT("setActiveWindow(QWidget *)"))

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.updateMenus()

        self.readSettings()

        #self.setWindowTitle(u"Expert Billing Client 1.2.1")

    def closeEvent(self, event):
        self.workspace.closeAllWindows()
        if self.activeMdiChild():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()


    def newFile(self):
        self.workspace.windowList()
        

        child =  AccountsMdiChild(connection=connection, parent=self)
        #child.setIcon( QPixmap("images/icon.ico") )        
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        #self.wsp.addSubWindow(child)        
        child.show()
    

    @connlogin
    def templates(self):
        self.workspace.windowList()  

        child =  TemplatesWindow(connection=connection)
        #child.setIcon( QPixmap("images/icon.ico") )        
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        #self.wsp.addSubWindow(child)
        
        child.show()
 
    @connlogin
    def messages(self):
        self.workspace.windowList()  

        child =  MessagesEbs(connection=connection)
        #child.setIcon( QPixmap("images/icon.ico") )        
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        #self.wsp.addSubWindow(child)
        
        child.show()

    @connlogin
    def transactiontype(self):
        self.workspace.windowList()  

        child =  TransactionTypeEbs(connection=connection)
        #child.setIcon( QPixmap("images/icon.ico") )        
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        #self.wsp.addSubWindow(child)
        
        child.show()
        
    @connlogin
    def hardwaremanufacturer(self):
        self.workspace.windowList()  

        child =  HardwareManufacturerEbs(connection=connection)
        #child.setIcon( QPixmap("images/icon.ico") )        
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        #self.wsp.addSubWindow(child)
        
        child.show()

    @connlogin
    def hardwaretype(self):
        self.workspace.windowList()  

        child =  HardwareTypeEbs(connection=connection)
        #child.setIcon( QPixmap("images/icon.ico") )        
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        #self.wsp.addSubWindow(child)
        
        child.show()       
        
    @connlogin
    def modelwindow(self):
        self.workspace.windowList()  

        child =  ModelWindowEbs(connection=connection)
        #child.setIcon( QPixmap("images/icon.ico") )        
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        #self.wsp.addSubWindow(child)
        
        child.show()  

    @connlogin
    def hardwarewindow(self):
        self.workspace.windowList()  

        child =  HardwareWindowEbs(connection=connection)
        #child.setIcon( QPixmap("images/icon.ico") )        
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        #self.wsp.addSubWindow(child)
        
        child.show()  

    @connlogin
    def pool(self):
        self.workspace.windowList()  

        child =  PoolFrame(connection=connection)
        #child.setIcon( QPixmap("images/icon.ico") )        
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        #self.wsp.addSubWindow(child)
        
        child.show()
               


    @connlogin
    def dealers(self):
        self.workspace.windowList()
        child =  DealerMdiChild(parent=self, connection=connection)
        #child.setIcon( QPixmap("images/icon.ico") )

        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)        
        child.show()        

    @connlogin
    def netflowreport(self):
        self.workspace.windowList()
        child =  NetFlowReport(parent=self, connection=connection)
        #child.setIcon( QPixmap("images/icon.ico") )

        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)        
        child.show()    
        
    @connlogin
    def open(self):
        child = NasEbs(connection=connection,parent=self)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return            
        self.workspace.addWindow(child)
        child.show()
        #return child

    @connlogin
    def save(self):
        child=SettlementPeriodChild(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return            
        self.workspace.addWindow(child)
        child.show()


    @connlogin
    def saveAs(self):

        child = SystemEbs(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return            
        self.workspace.addWindow(child)
        child.show()

    @connlogin
    def tpchangerules(self):
        child = TPRulesEbs(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return            
        self.workspace.addWindow(child)
        child.show()       
               
    
    @connlogin
    def cut(self):
        child=TimePeriodChild(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
            
        self.workspace.addWindow(child)
        child.show()

    @connlogin
    def copy(self):
        child=ClassChild(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
            
        self.workspace.addWindow(child)
        child.show()

    @connlogin
    def paste(self):
        child = MonitorFrame(connection=connection, parent=self)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        child.show()

    @connlogin
    def addonservice(self):
        child = AddonServiceEbs(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        child.show()
    
    @connlogin
    def transactionReport(self):

        child = TransactionsReport(connection=connection)
        self.workspace.addWindow(child)
        child.show()
        
    @connlogin
    def adminsLogViewWindow(self):
        child = LogViewEbs(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        child.show()
            
    
    @connlogin
    def logview(self):
        child = LogViewWindow(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        child.show()

    @connlogin
    def rrdAccountReport(self):
        child = RrdReportMainWindow(connection=connection, type='accounts')
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        child.show()

    @connlogin
    def webTransactionReport(self):
        child = RrdReportMainWindow(connection=connection, type='transactions')
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        child.show()
        
    @connlogin
    def rrdNassesReport(self):
        child = RrdReportMainWindow(connection=connection, type='nasses')
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        child.show()

    @connlogin
    def addressview(self):
        child = AddressEbs(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        child.show()

    @connlogin
    def switchWindow(self):
        child = SwitchEbs(parent=self,connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        child.show()
    
    #@connlogin
    def about(self):
        QtGui.QDesktopServices().openUrl(QtCore.QUrl('http://wiki.expertbilling.ru/')) 
        #QtGui.QMessageBox.about(self, u"О программе",
        #                        u"Expert Billing Client<br>Интерфейс конфигурирования.<br>Версия 0.2")
    #@connlogin
    def to_forum(self):
        QtGui.QDesktopServices().openUrl(QtCore.QUrl('http://forum.expertbilling.ru/')) 
        #QtGui.QMessageBox.about(self, u"О программе",
        #     
        
    @connlogin
    def aboutOperator(self):
        child = OperatorDialog(connection=connection)
        child.exec_()
        
    @connlogin
    def sqlDialog(self):
        child = SqlDialog(connection=connection)
        child.exec_()
        
    @connlogin
    def cardsFrame(self):
        child = CardsChild(connection = connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        child.show()

    @connlogin
    def radiuslog_report(self):
        child = SimpleReportEbs(connection = connection, report_type='radius_authlog')
        self.workspace.addWindow(child)
        child.show()
        
        

    def relogin(self):
        global connection
        connection = login()
        global mainwindow
        mainwindow.setWindowTitle("ExpertBilling administrator interface #%s - %s" % (connection.username, connection.host)) 
        

    def updateMenus(self):
        hasMdiChild = (self.activeMdiChild() is not None)
        #self.saveAct.setEnabled(hasMdiChild)
        #self.sysadmAct.setEnabled(hasMdiChild)
        #self.pasteAct.setEnabled(True)
        self.closeAct.setEnabled(hasMdiChild)
        self.closeAllAct.setEnabled(hasMdiChild)
        self.tileAct.setEnabled(hasMdiChild)
        self.cascadeAct.setEnabled(hasMdiChild)
        self.arrangeAct.setEnabled(hasMdiChild)
        self.nextAct.setEnabled(hasMdiChild)
        self.previousAct.setEnabled(hasMdiChild)
        self.separatorAct.setVisible(hasMdiChild)


    def updateWindowMenu(self):
        self.windowMenu.clear()
        self.windowMenu.addAction(self.closeAct)
        self.windowMenu.addAction(self.closeAllAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.tileAct)
        self.windowMenu.addAction(self.cascadeAct)
        self.windowMenu.addAction(self.arrangeAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.nextAct)
        self.windowMenu.addAction(self.previousAct)
        self.windowMenu.addAction(self.separatorAct)

        windows = self.workspace.windowList()
        self.separatorAct.setVisible(len(windows) != 0)

        i = 0

        for child in windows:
            i += 1
            action = self.windowMenu.addAction(child.windowTitle())
            action.setCheckable(True)
            action.setChecked(child == self.activeMdiChild())
            self.connect(action, QtCore.SIGNAL("triggered()"),
                         self.windowMapper, QtCore.SLOT("map()"))
            self.windowMapper.setMapping(action, child)


       
    def createActions(self):
        self.newAct = QtGui.QAction(QtGui.QIcon("images/accounts.png"),
                                    u"&Пользователи и тарифы", self)
        #self.newAct.setShortcut(self.tr("Ctrl+A"))
        self.newAct.setStatusTip(u"Пользователи и тарифы")
        self.connect(self.newAct, QtCore.SIGNAL("triggered()"), self.newFile)

        self.dealerAct = QtGui.QAction(QtGui.QIcon("images/dealer.png"),
                                    u"&Дилеры", self)
        #self.dealerAct.setShortcut(self.tr("Ctrl+D"))
        self.dealerAct.setStatusTip(u"Дилеры")
        self.connect(self.dealerAct, QtCore.SIGNAL("triggered()"), self.dealers)
        
        self.netflowAct = QtGui.QAction(QtGui.QIcon("images/nfstat.png"),
                                    u"&NetFlow статистика", self)
        #self.dealerAct.setShortcut(self.tr("Ctrl+D"))
        self.netflowAct.setStatusTip(u"NetFlow статистика")
        self.connect(self.netflowAct, QtCore.SIGNAL("triggered()"), self.netflowreport)
                
        self.nasAct = QtGui.QAction(QtGui.QIcon("images/nas.png"), u"&Серверы доступа", self)
        
        self.nasAct.setStatusTip(u'Серверы доступа')
        self.connect(self.nasAct, QtCore.SIGNAL("triggered()"), self.open)
        
        self.switchAct = QtGui.QAction(QtGui.QIcon("images/switch.png"), u"&Комутаторы", self)
        
        self.switchAct.setStatusTip(u'Комутаторы')
        self.connect(self.switchAct, QtCore.SIGNAL("triggered()"), self.switchWindow)
       
       
        self.hardwaremanufacturerAct = QtGui.QAction(QtGui.QIcon("images/modem.png"), u"&Производители оборудования", self)
        
        self.hardwaremanufacturerAct.setStatusTip(u'Производители оборудования')
        self.connect(self.hardwaremanufacturerAct, QtCore.SIGNAL("triggered()"), self.hardwaremanufacturer)
        
        self.hardwaretypeAct = QtGui.QAction(QtGui.QIcon("images/modem.png"), u"&Типы оборудования", self)
        
        self.hardwaretypeAct.setStatusTip(u'Типы оборудования')
        self.connect(self.hardwaretypeAct, QtCore.SIGNAL("triggered()"), self.hardwaretype)
        
        self.modelwindowAct = QtGui.QAction(QtGui.QIcon("images/modem.png"), u"&Модели оборудования", self)
        
        self.modelwindowAct.setStatusTip(u'Модели оборудования')
        self.connect(self.modelwindowAct, QtCore.SIGNAL("triggered()"), self.modelwindow)        
        
        
        self.hardwarewindowAct = QtGui.QAction(QtGui.QIcon("images/modem.png"), u"&Подотчётное оборудование", self)
        
        self.hardwarewindowAct.setStatusTip(u'Оборудование провайдера')
        self.connect(self.hardwarewindowAct, QtCore.SIGNAL("triggered()"), self.hardwarewindow)        
        
        self.settlementPeriodAct = QtGui.QAction(QtGui.QIcon("images/sp.png"), u'Расчётные периоды', self)
        self.settlementPeriodAct.setStatusTip(u"Расчётные периоды")
        self.connect(self.settlementPeriodAct, QtCore.SIGNAL("triggered()"), self.save)



        self.adminLogViewAct = QtGui.QAction(QtGui.QIcon("images/add.png"), u'Лог действий', self)
        self.adminLogViewAct.setStatusTip(u"Лог действий")
        self.connect(self.adminLogViewAct, QtCore.SIGNAL("triggered()"), self.adminsLogViewWindow)
        
        self.transactionReportAct = QtGui.QAction(QtGui.QIcon("images/moneybook.png"), u'Платежи и списания', self)
        self.transactionReportAct.setStatusTip(u"Платежи и списания")
        self.connect(self.transactionReportAct, QtCore.SIGNAL("triggered()"), self.transactionReport)
        
        self.addressViewAct = QtGui.QAction(QtGui.QIcon("images/house.png"), u'Адреса домов', self)
        self.addressViewAct.setStatusTip(u"Адреса")
        self.connect(self.addressViewAct, QtCore.SIGNAL("triggered()"), self.addressview)
        
                
        self.sysadmAct = QtGui.QAction(QtGui.QIcon("images/system_administrators.png"),u'Администраторы и работники', self)
        self.sysadmAct.setStatusTip(u"Администраторы и работники")
        self.connect(self.sysadmAct, QtCore.SIGNAL("triggered()"), self.saveAs)

        self.poolAct = QtGui.QAction(QtGui.QIcon("images/ipv4.png"),u'IP пулы', self)
        self.poolAct.setStatusTip(u"Пулы IP адресов")
        self.connect(self.poolAct, QtCore.SIGNAL("triggered()"), self.pool)


        self.exitAct = QtGui.QAction(u"Выход", self)
        self.exitAct.setShortcut(self.tr("Ctrl+Q"))
        self.exitAct.setStatusTip(u"Выход из программы")
        self.connect(self.exitAct, QtCore.SIGNAL("triggered()"), self.close)
        
        
        self.timePeriodAct = QtGui.QAction(QtGui.QIcon("images/tp.png"),
                                    u'Периоды тарификации', self)

        self.timePeriodAct.setStatusTip(u"Периоды тарификации")
        self.connect(self.timePeriodAct, QtCore.SIGNAL("triggered()"), self.cut)

        self.messagesAct = QtGui.QAction(QtGui.QIcon("images/messages.png"),
                                    u'Сообщения абонентам', self)

        self.messagesAct.setStatusTip(u"Сообщениия")
        self.connect(self.messagesAct, QtCore.SIGNAL("triggered()"), self.messages)


        self.sqlDialogAct = QtGui.QAction(QtGui.QIcon("images/sql.png"),u'SQL Консоль', self)

        self.sqlDialogAct.setShortcut(self.tr("Ctrl+Y"))
        self.connect(self.sqlDialogAct, QtCore.SIGNAL("triggered()"), self.sqlDialog)


        self.tclassesAct = QtGui.QAction(QtGui.QIcon("images/tc.png"),
                                     u"Классы трафика", self)
        #self.tclassesAct.setShortcut(self.tr("Ctrl+C"))
        self.tclassesAct.setStatusTip(u"Классы трафика")
        self.connect(self.tclassesAct, QtCore.SIGNAL("triggered()"), self.copy)

        self.sessionsMonAct = QtGui.QAction(QtGui.QIcon("images/monitor.png"),
                                      u"Монитор сессий", self)
        self.sessionsMonAct.setStatusTip(u"Монитор сессий")

        self.connect(self.sessionsMonAct, QtCore.SIGNAL("triggered()"), self.paste)

        self.cardsAct = QtGui.QAction(QtGui.QIcon("images/cards.png"),
                                      u"Карточная система", self)
        #self.reportPropertiesAct.setShortcut(self.tr("Ctrl+V"))
        self.cardsAct.setStatusTip(u"Карточная система")

        self.connect(self.cardsAct, QtCore.SIGNAL("triggered()"), self.cardsFrame)

        self.radiuslogReportAct=QtGui.QAction(QtGui.QIcon("images/easytag.png"), u"История RADIUS авторизаций", self)

        self.radiuslogReportAct.setStatusTip(u"История RADIUS авторизаций пользователей")

        self.connect(self.radiuslogReportAct, QtCore.SIGNAL("triggered()"), self.radiuslog_report)

        self.reloginAct = QtGui.QAction(QtGui.QIcon("images/refresh_connection.png"),self.tr("&Reconnect"), self)
        self.reloginAct.setStatusTip(self.tr("Reconnect"))
        self.connect(self.reloginAct, QtCore.SIGNAL("triggered()"), self.relogin)

        self.templatesAct = QtGui.QAction(QtGui.QIcon("images/templates.png"),u"Шаблоны документов", self)
        #self.reloginAct.setStatusTip(self.tr("Reconnect"))
        self.connect(self.templatesAct, QtCore.SIGNAL("triggered()"), self.templates)


        self.tpchangeAct = QtGui.QAction(QtGui.QIcon("images/tarif_change.png"),u"Правила смены тарифов", self)
        #self.reloginAct.setStatusTip(self.tr("Reconnect"))
        self.connect(self.tpchangeAct, QtCore.SIGNAL("triggered()"), self.tpchangerules)

        self.addonserviceAct = QtGui.QAction(QtGui.QIcon("images/turboicon.png"),u"Подключаемые услуги", self)
        #self.reloginAct.setStatusTip(self.tr("Reconnect"))
        self.connect(self.addonserviceAct, QtCore.SIGNAL("triggered()"), self.addonservice)
 
        self.logViewAct = QtGui.QAction(QtGui.QIcon("images/logs.png"), u"Просмотр логов", self)
        #self.reloginAct.setStatusTip(self.tr("Reconnect"))
        self.connect(self.logViewAct, QtCore.SIGNAL("triggered()"), self.logview)       
        
        self.rrdAccountsAct = QtGui.QAction(QtGui.QIcon("images/accounts.png"),
                                      u"Загрузка VPN аккаунтами", self)
        self.rrdAccountsAct.setStatusTip(u"Загрузка VPN аккаунтами")

        self.connect(self.rrdAccountsAct, QtCore.SIGNAL("triggered()"), self.rrdAccountReport)


        self.rrdNassesAct = QtGui.QAction(QtGui.QIcon("images/nas.png"),
                                      u"Загрузка VPN серверов доступа", self)
        self.rrdNassesAct.setStatusTip(u"Загрузка VPN аккаунтами")

        self.connect(self.rrdNassesAct, QtCore.SIGNAL("triggered()"), self.rrdNassesReport)

        self.webTransactionReportAct = QtGui.QAction(QtGui.QIcon("images/moneybook.png"),
                                      u"Отчёт по списаниям(веб)", self)
        self.webTransactionReportAct.setStatusTip(u"Отчёт по списаниям(веб)")

        self.connect(self.webTransactionReportAct, QtCore.SIGNAL("triggered()"), self.webTransactionReport)
        
        self.transactiontypeAct = QtGui.QAction(QtGui.QIcon("images/moneybook.png"),
                                      u"Типы платежей", self)
        
        self.transactiontypeAct.setStatusTip(u"Типы платежей")

        self.connect(self.transactiontypeAct, QtCore.SIGNAL("triggered()"), self.transactiontype)
        
        
        self.reportActs = []
        i = 0
        
        for branch in _reportsdict:
            j=0
            self.reportActs.append([branch[0],[]])
            for leaf in branch[1]:
                rAct = QtGui.QAction(self.trUtf8(leaf[2]), self)
                rAct.setStatusTip(u"Отчёт")
                rAct.setData(QtCore.QVariant('_'.join((str(i), str(j)))))
                self.connect(rAct, QtCore.SIGNAL("triggered()"), self.reportsMenu)
                self.reportActs[-1][1].append(rAct)
                j+=1
            i += 1

        self.closeAct = QtGui.QAction(self.tr("Cl&ose"), self)
        self.closeAct.setShortcut(self.tr("Ctrl+F4"))
        self.closeAct.setStatusTip(self.tr("Close the active window"))
        self.connect(self.closeAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.closeActiveWindow)

        self.closeAllAct = QtGui.QAction(self.tr("Close &All"), self)
        self.closeAllAct.setStatusTip(self.tr("Close all the windows"))
        self.connect(self.closeAllAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.closeAllWindows)

        self.tileAct = QtGui.QAction(self.tr("&Tile"), self)
        self.tileAct.setStatusTip(self.tr("Tile the windows"))
        self.connect(self.tileAct, QtCore.SIGNAL("triggered()"), self.workspace.tile)

        self.cascadeAct = QtGui.QAction(self.tr("&Cascade"), self)
        self.cascadeAct.setStatusTip(self.tr("Cascade the windows"))
        self.connect(self.cascadeAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.cascade)

        self.arrangeAct = QtGui.QAction(self.tr("Arrange &icons"), self)
        self.arrangeAct.setStatusTip(self.tr("Arrange the icons"))
        self.connect(self.arrangeAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.arrangeIcons)

        self.nextAct = QtGui.QAction(self.tr("Ne&xt"), self)
        self.nextAct.setShortcut(self.tr("Ctrl+F6"))
        self.nextAct.setStatusTip(self.tr("Move the focus to the next window"))
        self.connect(self.nextAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.activateNextWindow)

        self.previousAct = QtGui.QAction(self.tr("Pre&vious"), self)
        self.previousAct.setShortcut(self.tr("Ctrl+Shift+F6"))
        self.previousAct.setStatusTip(self.tr("Move the focus to the previous "
                                              "window"))
        self.connect(self.previousAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.activatePreviousWindow)

        self.separatorAct = QtGui.QAction(self)
        self.separatorAct.setSeparator(True)

        self.aboutAct = QtGui.QAction(u"&Документация", self)
        self.aboutAct.setStatusTip(u"Перейти на страницу документации")
        self.connect(self.aboutAct, QtCore.SIGNAL("triggered()"), self.about)
      
        self.forumAct = QtGui.QAction(u"&Форум проекта", self)
        self.forumAct.setStatusTip(u"Перейти на форум")
        self.connect(self.forumAct, QtCore.SIGNAL("triggered()"), self.to_forum)
        
        self.aboutOperAct = QtGui.QAction(u"Информация о провайдере", self)
        self.aboutOperAct.setStatusTip(self.tr("Show the operator info"))
        self.connect(self.aboutOperAct, QtCore.SIGNAL("triggered()"), self.aboutOperator)

        self.aboutQtAct = QtGui.QAction(self.tr("About &Qt"), self)
        self.aboutQtAct.setStatusTip(self.tr("Show the Qt library's About box"))
        self.connect(self.aboutQtAct, QtCore.SIGNAL("triggered()"),
                     QtGui.qApp, QtCore.SLOT("aboutQt()"))



    def createMenus(self):
        self.mainMenu = self.menuBar().addMenu(u"&Главное меню")
        self.mainMenu.addAction(self.newAct)
        
        #self.mainMenu.addAction(self.settlementPeriodAct)
        
        #self.editMenu = self.menuBar().addMenu(self.tr("&Edit"))
        #self.mainMenu.addAction(self.timePeriodAct)
        self.mainMenu.addSeparator()
        self.mainMenu.addAction(self.tpchangeAct)
        
        self.mainMenu.addAction(self.sessionsMonAct)
        
        #self.mainMenu.addAction(self.poolAct)
        self.mainMenu.addSeparator()
        #self.mainMenu.addAction(self.addressViewAct)
        #self.mainMenu.addSeparator()
        #self.mainMenu.addAction(self.sysadmAct)
        self.mainMenu.addAction(self.dealerAct)
        self.mainMenu.addSeparator()
        #self.mainMenu.addAction(self.templatesAct)

        #self.mainMenu.addSeparator()
        #self.mainMenu.addAction(self.addonserviceAct)
        self.mainMenu.addSeparator()
        self.mainMenu.addAction(self.messagesAct)
        self.mainMenu.addSeparator()
        self.mainMenu.addAction(self.logViewAct)
        
        self.mainMenu.addSeparator()
        
        self.mainMenu.addAction(self.adminLogViewAct)
        self.mainMenu.addSeparator()
        self.mainMenu.addAction(self.sqlDialogAct)
        self.mainMenu.addSeparator()
        self.mainMenu.addAction(self.reloginAct)
        self.mainMenu.addSeparator()
        self.mainMenu.addAction(self.exitAct)

        self.settingsMenu = self.menuBar().addMenu(u"&Справочники")
        self.settingsMenu.addAction(self.nasAct)
        self.settingsMenu.addAction(self.switchAct)
        self.settingsMenu.addAction(self.addonserviceAct)
        self.settingsMenu.addAction(self.settlementPeriodAct)
        self.settingsMenu.addAction(self.timePeriodAct)
        self.settingsMenu.addAction(self.tclassesAct)
        self.settingsMenu.addAction(self.poolAct)
        self.settingsMenu.addAction(self.addressViewAct)
        self.settingsMenu.addAction(self.sysadmAct)
        self.settingsMenu.addAction(self.templatesAct)
        self.settingsMenu.addAction(self.transactiontypeAct)
        self.settingsMenu.addSeparator()
        self.settingsMenu.addAction(self.hardwaremanufacturerAct)
        self.settingsMenu.addAction(self.hardwaretypeAct)
        self.settingsMenu.addAction(self.modelwindowAct)
        self.settingsMenu.addAction(self.hardwarewindowAct)
        self.settingsMenu.addSeparator()
        self.settingsMenu.addAction(self.aboutOperAct)
        
        
        self.windowMenu = self.menuBar().addMenu(u"&Окна")
        self.connect(self.windowMenu, QtCore.SIGNAL("aboutToShow()"),
                     self.updateWindowMenu)
        self.reportsMenu = self.menuBar().addMenu(u"&Отчёты")
        
        for menuName, branch in self.reportActs:
            branchMenu = self.reportsMenu.addMenu(self.trUtf8(menuName))
            for leaf in branch:
                branchMenu.addAction(leaf)
        
        self.reportsMenu.addAction(self.netflowAct)
        self.reportsMenu.addAction(self.rrdAccountsAct)
        self.reportsMenu.addAction(self.rrdNassesAct)
        self.reportsMenu.addAction(self.webTransactionReportAct)
        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu(u"&Справка")
        
        #self.helpMenu.addAction(self.aboutOperAct)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.forumAct)
        #self.helpMenu.addAction(self.aboutQtAct)

    @connlogin
    def reportsMenu(self):
        #print self.sender().data().toInt()
        i,j = [int(vstr) for vstr in str(self.sender().data().toString()).split('_')]
        child=StatReport(connection=connection, chartinfo=_reportsdict[i][1][j])
        self.workspace.addWindow(child)
        child.show()

    def createToolBars(self):
        self.fileToolBar = QtGui.QToolBar(self)
        self.fileToolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.fileToolBar.addAction(self.newAct)
        self.fileToolBar.addAction(self.nasAct)
        self.fileToolBar.addAction(self.transactionReportAct)
        self.fileToolBar.addAction(self.sessionsMonAct)
        self.fileToolBar.addAction(self.radiuslogReportAct)
        
        self.fileToolBar.addAction(self.addonserviceAct)
        self.fileToolBar.addAction(self.cardsAct)
        self.fileToolBar.addAction(self.tclassesAct)
        #self.fileToolBar.addAction(self.settlementPeriodAct)
        self.fileToolBar.setMovable(False)
        self.fileToolBar.setFloatable(False)

        self.fileToolBar.setAllowedAreas(QtCore.Qt.TopToolBarArea)
        self.fileToolBar.setIconSize(QtCore.QSize(16,16))

        #self.fileToolBar.addAction(self.timePeriodAct)
        #self.fileToolBar.addAction(self.tclassesAct)
        
        
        

        self.addToolBar(QtCore.Qt.TopToolBarArea,self.fileToolBar)

    def createStatusBar(self):
        self.statusBar().showMessage(self.tr("Ready"))

    def readSettings(self):
        settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
        pos = settings.value("pos", QtCore.QVariant(QtCore.QPoint(200, 200))).toPoint()
        size = settings.value("size", QtCore.QVariant(QtCore.QSize(400, 400))).toSize()
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
        settings.setValue("pos", QtCore.QVariant(self.pos()))
        settings.setValue("size", QtCore.QVariant(self.size()))

    def activeMdiChild(self):
        return self.workspace.activeWindow()

    def findMdiChild(self, fileName):
        canonicalFilePath = QtCore.QFileInfo(fileName).canonicalFilePath()

        for window in self.workspace.windowList():
            if window.currentFile() == canonicalFilePath:
                return window
        return None
    
class Executor(Object):
    def __init__(self):
        pass
    def execute(self, execcmd):
        inQueue.append(execcmd)
        #use locks etc
        return outQueue.pop()
    
class rpcDispatcher(threading.Thread):
    
    def __init__(self):
        pass
    
    def run(self):
        pass


        
def login():
    child = ConnectDialog()
    while True:

        if child.exec_()==1:
            #waitchild = ConnectionWaiting()
            #waitchild.show()
            global splash, username, server_ip
            pixmap = QtGui.QPixmap("splash.png")
            #splash = QtGui.QSplashScreen(pixmap, QtCore.Qt.WindowStaysOnTopHint)
            splash = QtGui.QSplashScreen(pixmap)
            splash.setMask(pixmap.mask()) # this is usefull if the splashscreen is not a regular ractangle...
            splash.show()
            splash.showMessage(u'Starting...', QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom,QtCore.Qt.yellow)
            # make sure Qt really display the splash screen
            global app
            app.processEvents()

                
                #logger  = PrintLogger()
            try:
                os.mkdir('log')
            except:
                pass
            logger = isdlogger.isdlogger('logging', loglevel=LOG_LEVEL, ident='mdi', filename='log/mdi_log')

            connection = HttpBot(widget=child, host=unicode(child.address))
            data = connection.log_in(unicode(child.name), unicode(child.password))
            username = unicode(child.name)

            if data:
                return connection
            elif data==None:
                #QtGui.QMessageBox.warning(None, unicode(u"Ошибка"), unicode(u"Невозможно подключиться к серверу."))
                pass
            else:
                QtGui.QMessageBox.warning(None, unicode(u"Ошибка"), unicode(u"Отказано в авторизации.\n%s" % data.message))

        else:
            #splash.hide()
            return None

if __name__ == "__main__":
    global app, bot
    app = QtGui.QApplication(sys.argv)
    #translator = QtCore.QTranslator(app)
    #translator.load('ebsadmin_en')
    #app.installTranslator(translator)
    global connection, username, server_ip
    
    #kb.show()
    connection = login() 
       
    if connection is None:
        sys.exit()
    #connection.commit()
    
    try:
        global mainwindow
        mainwindow = MainWindow()
        with open("version",'r') as vf:
            version=vf.read()
            
        splash.finish(mainwindow) 
        mainwindow.show()
        mainwindow.setWindowTitle("ExpertBilling administrator interface v.1.4.1%s-dev #%s - %s" % (version,username, connection.host))  
        #app.setStyle("cleanlooks")
        mainwindow.setWindowIcon(QtGui.QIcon("images/icon.png"))
        app.setStyleSheet(open("skins/style.qss","r").read())

        sys.exit(app.exec_())
        connection.commit()
    except Exception, ex:
        print "main-----------"
        print repr(ex)
        print traceback.format_exc()


    #QtGui.QStyle.SH_Table_GridLineColor

