from ajax_select import LookupChannel
from django.utils.html import escape
from django.db.models import Q
from billservice.models import Account, City, Street, House, Hardware, Organization, SubAccount

class AccountFTSLookup(LookupChannel):

    model = Account

    def get_query(self,q,request):
        return Account.objects.filter(Q(username__icontains=q) | Q(contactperson__icontains=q) | Q(fullname__icontains=q)  | Q(phone_h__icontains=q) | Q(phone_m__icontains=q)   ).order_by('username')

    def get_result(self,obj):
        u""" result is the simple text that is the completion of what the person typed """
        return obj.username

    def format_match(self,obj):
        """ (HTML) formatted item for display in the dropdown """
        return self.format_item_display(obj)

    def format_item_display(self,obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return u"%s %s %s %s %s %s" % (escape(obj.username),escape(obj.fullname), escape(obj.contract), escape(obj.contactperson), escape(obj.phone_h), escape(obj.phone_m))
    
class AccountFullnameLookup(LookupChannel):

    model = Account

    def get_query(self,q,request):
        return Account.objects.filter(fullname__icontains=q).order_by('fullname')

    def get_result(self,obj):
        u""" result is the simple text that is the completion of what the person typed """
        return obj.fullname

    def format_match(self,obj):
        """ (HTML) formatted item for display in the dropdown """
        return self.format_item_display(obj)

    def format_item_display(self,obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return u"%s" % (escape(obj.fullname))
    

class AccountUsernameLookup(LookupChannel):

    model = Account

    def get_query(self,q,request):
        return Account.objects.filter(username__icontains=q).order_by('username')

    def get_result(self,obj):
        u""" result is the simple text that is the completion of what the person typed """
        return obj.username

    def format_match(self,obj):
        """ (HTML) formatted item for display in the dropdown """
        return self.format_item_display(obj)

    def format_item_display(self,obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return u"%s" % (escape(obj.username))
    
class AccountContractLookup(LookupChannel):

    model = Account

    def get_query(self,q,request):
        return Account.objects.filter(contract__icontains=q).order_by('contract')

    def get_result(self,obj):
        u""" result is the simple text that is the completion of what the person typed """
        return obj.contract

    def format_match(self,obj):
        """ (HTML) formatted item for display in the dropdown """
        return self.format_item_display(obj)

    def format_item_display(self,obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return u"%s" % (escape(obj.contract))

class AccountContactPersonLookup(LookupChannel):

    model = Account

    def get_query(self,q,request):
        return Account.objects.filter(contactperson__icontains=q).order_by('contactperson')

    def get_result(self,obj):
        u""" result is the simple text that is the completion of what the person typed """
        return obj.contactperson

    def format_match(self,obj):
        """ (HTML) formatted item for display in the dropdown """
        return self.format_item_display(obj)

    def format_item_display(self,obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return u"%s" % (escape(obj.contactperson))
    
class CityLookup(LookupChannel):

    model = City

    def get_query(self,q,request):
        return City.objects.filter(name__icontains=q).order_by('name')

    def get_result(self,obj):
        u""" result is the simple text that is the completion of what the person typed """
        return obj.name

    def format_match(self,obj):
        """ (HTML) formatted item for display in the dropdown """
        return self.format_item_display(obj)

    def format_item_display(self,obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return u"%s" % (escape(obj.name))

class StreetLookup(LookupChannel):

    model = Street

    def get_query(self,q,request):
        return Street.objects.filter(name__icontains=q).order_by('name')

    def get_result(self,obj):
        u""" result is the simple text that is the completion of what the person typed """
        return obj.name

    def format_match(self,obj):
        """ (HTML) formatted item for display in the dropdown """
        return self.format_item_display(obj)

    def format_item_display(self,obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return u"%s" % (escape(obj.name))

class HouseLookup(LookupChannel):

    model = House

    def get_query(self,q,request):
        return House.objects.filter(name__icontains=q).order_by('name')

    def get_result(self,obj):
        u""" result is the simple text that is the completion of what the person typed """
        return obj.name

    def format_match(self,obj):
        """ (HTML) formatted item for display in the dropdown """
        return self.format_item_display(obj)

    def format_item_display(self,obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return u"%s" % (escape(obj.name))
    
class HardwareLookup(LookupChannel):

    model = Hardware

    def get_query(self,q,request):
        return Hardware.objects.filter(Q(macaddress__icontains=q) |Q(name__icontains=q) | Q(model__name__icontains=q)| Q(sn__icontains=q)| Q(comment__icontains=q)).order_by('name')

    def get_result(self,obj):
        u""" result is the simple text that is the completion of what the person typed """
        return obj.name

    def format_match(self,obj):
        """ (HTML) formatted item for display in the dropdown """
        return self.format_item_display(obj)

    def format_item_display(self,obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return u"%s %s %s %s %s %s" % (escape(obj.name),escape(obj.model.name), escape(obj.sn), escape(obj.comment), escape(obj.ipaddress), escape(obj.macaddress))
    
class OrganizationLookup(LookupChannel):

    model = Organization

    def get_query(self,q,request):
        return Organization.objects.filter(name__icontains=q).order_by('name')

    def get_result(self,obj):
        u""" result is the simple text that is the completion of what the person typed """
        return obj.name

    def format_match(self,obj):
        """ (HTML) formatted item for display in the dropdown """
        return self.format_item_display(obj)

    def format_item_display(self,obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return u"%s" % (escape(obj.name),)
    
class SubAccountFTSLookup(LookupChannel):

    model = SubAccount

    def get_query(self,q,request):
        return SubAccount.objects.filter(Q(username__icontains=q) | Q(ipn_mac_address__icontains=q)).order_by('username')

    def get_result(self,obj):
        u""" result is the simple text that is the completion of what the person typed """
        return obj.username

    def format_match(self,obj):
        """ (HTML) formatted item for display in the dropdown """
        return self.format_item_display(obj)

    def format_item_display(self,obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return u"%s<div> %s %s %s</div>" % (escape(obj.username),escape(obj.vpn_ip_address), escape(obj.ipn_ip_address), escape(obj.ipn_mac_address), )
    
    