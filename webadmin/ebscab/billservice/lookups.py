# -*- coding: utf-8 -*-

from django.db.models import Q
from django.utils.html import escape

from ajax_select import LookupChannel
from billservice.models import (
    Account,
    City,
    House,
    Organization,
    Street,
    SubAccount
)


class AccountFTSLookup(LookupChannel):
    model = Account
    min_length = 2

    def get_query(self, q, request):
        return (Account.objects
                .filter(Q(username__istartswith=q) |
                        Q(contactperson__icontains=q) |
                        Q(fullname__icontains=q) | Q(phone_h__icontains=q) |
                        Q(phone_m__icontains=q))
                .order_by('username'))

    def get_result(self, obj):
        """result is the simple text that is the completion of what
        the person typed
        """
        return obj.username

    def format_match(self, obj):
        """(HTML) formatted item for display in the dropdown"""
        return self.format_item_display(obj)

    def format_item_display(self, obj):
        """(HTML) formatted item for displaying item in the selected deck area
        """
        return u"%s %s %s %s %s" % (escape(obj.username),
                                    escape(obj.fullname),
                                    escape(obj.contract),
                                    escape(obj.phone_h),
                                    escape(obj.phone_m))


class AccountFullnameLookup(LookupChannel):
    model = Account
    min_length = 2

    def get_query(self, q, request):
        return (Account.objects
                .filter(fullname__istartswith=q)
                .order_by('fullname'))

    def get_result(self, obj):
        """result is the simple text that is the completion of what
        the person typed
        """
        return obj.fullname

    def format_match(self, obj):
        """(HTML) formatted item for display in the dropdown
        """
        return self.format_item_display(obj)

    def format_item_display(self, obj):
        """(HTML) formatted item for displaying item in the selected deck area
        """
        return u"%s" % (escape(obj.fullname))


class AccountUsernameLookup(LookupChannel):
    model = Account
    min_length = 2

    def get_query(self, q, request):
        return (Account.objects
                .filter(username__icontains=q)
                .order_by('username'))

    def get_result(self, obj):
        """result is the simple text that is the completion of what
        the person typed
        """
        return obj.username

    def format_match(self, obj):
        """(HTML) formatted item for display in the dropdown
        """
        return self.format_item_display(obj)

    def format_item_display(self, obj):
        """(HTML) formatted item for displaying item in the selected deck area
        """
        return u"%s" % (escape(obj.username))


class AccountContractLookup(LookupChannel):
    model = Account
    min_length = 2

    def get_query(self, q, request):
        return (Account.objects
                .filter(contract__istartswith=q)
                .order_by('contract'))

    def get_result(self, obj):
        """result is the simple text that is the completion of what
        the person typed
        """
        return obj.contract

    def format_match(self, obj):
        """(HTML) formatted item for display in the dropdown
        """
        return self.format_item_display(obj)

    def format_item_display(self, obj):
        """(HTML) formatted item for displaying item in the selected deck area
        """
        return u"%s" % (escape(obj.contract))


class AccountContactPersonLookup(LookupChannel):

    model = Account
    min_length = 2

    def get_query(self, q, request):
        return (Account.objects
                .filter(contactperson__istartswith=q)
                .order_by('contactperson'))

    def get_result(self, obj):
        """result is the simple text that is the completion of what
        the person typed
        """
        return obj.contactperson

    def format_match(self, obj):
        """(HTML) formatted item for display in the dropdown
        """
        return self.format_item_display(obj)

    def format_item_display(self, obj):
        """(HTML) formatted item for displaying item in the selected deck area
        """
        return u"%s" % (escape(obj.contactperson))


class CityLookup(LookupChannel):

    model = City
    min_length = 3

    def get_query(self, q, request):
        return City.objects.filter(name__istartswith=q).order_by('name')

    def get_result(self, obj):
        """result is the simple text that is the completion of what
        the person typed
        """
        return obj.name

    def format_match(self, obj):
        """(HTML) formatted item for display in the dropdown
        """
        return self.format_item_display(obj)

    def format_item_display(self, obj):
        """(HTML) formatted item for displaying item in the selected deck area
        """
        return u"%s" % (escape(obj.name))


class StreetLookup(LookupChannel):

    model = Street
    min_length = 2

    def get_query(self, q, request):
        return Street.objects.filter(name__istartswith=q).order_by('name')

    def get_result(self, obj):
        """result is the simple text that is the completion of what
        the person typed
        """
        return obj.name

    def format_match(self, obj):
        """(HTML) formatted item for display in the dropdown
        """
        return self.format_item_display(obj)

    def format_item_display(self, obj):
        """(HTML) formatted item for displaying item in the selected deck area
        """
        return u"%s" % (escape(obj.name))


class HouseLookup(LookupChannel):

    model = House
    min_length = 1

    def get_query(self, q, request):
        return House.objects.filter(name__istartswith=q).order_by('name')

    def get_result(self,
                   obj):
        """result is the simple text that is the completion of what
        the person typed
        """
        return obj.name

    def format_match(self, obj):
        """(HTML) formatted item for display in the dropdown
        """
        return self.format_item_display(obj)

    def format_item_display(self, obj):
        """(HTML) formatted item for displaying item in the selected deck area
        """
        return u"%s" % (escape(obj.name))


class OrganizationLookup(LookupChannel):

    model = Organization
    min_length = 1

    def get_query(self, q, request):
        return (Organization.objects
                .filter(name__istartswith=q)
                .order_by('name'))

    def get_result(self, obj):
        """result is the simple text that is the completion of what
        the person typed
        """
        return obj.name

    def format_match(self, obj):
        """(HTML) formatted item for display in the dropdown
        """
        return self.format_item_display(obj)

    def format_item_display(self, obj):
        """(HTML) formatted item for displaying item in the selected deck area
        """
        return u"%s" % (escape(obj.name),)


class SubAccountFTSLookup(LookupChannel):

    model = SubAccount
    min_length = 2

    def get_query(self, q, request):
        return (SubAccount.objects
                .filter(Q(username__istartswith=q) |
                        Q(ipn_mac_address__istartswith=q))
                .order_by('username'))

    def get_result(self, obj):
        """result is the simple text that is the completion of what
        the person typed
        """
        return obj.username

    def format_match(self, obj):
        """(HTML) formatted item for display in the dropdown
        """
        return self.format_item_display(obj)

    def format_item_display(self, obj):
        """(HTML) formatted item for displaying item in the selected deck area
        """
        return u"%s<div> %s %s %s</div>" % (escape(obj.username),
                                            escape(obj.vpn_ip_address),
                                            escape(obj.ipn_ip_address),
                                            escape(obj.ipn_mac_address))
