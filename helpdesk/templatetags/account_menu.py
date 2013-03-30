# -*- coding=utf-8 -*-
# $Id: account_menu.py 182 2010-08-03 20:59:49Z dmitry $
from django import template
from django.conf import settings
from helpdesk.settings import PERSONAL_AREA_MENU

register = template.Library()


@register.inclusion_tag('top_menu.html', takes_context=True)
def account_menu(context):
    """
    Show menu for user's "cabinet"
    """
    from lib.menu import Menu
    menu = Menu(context['current_view_name']) 
    for view_name, verbose_name in PERSONAL_AREA_MENU:
        menu.add(view_name, verbose_name)
    
    return {'menu': menu}

@register.inclusion_tag('helpdesk/tags/account_profile_menu.html', takes_context=True)
def account_profile_menu(context):
    """
    Show right menu in profile page
    """
    from lib.menu import Menu
    menu = Menu()
    for view_name, verbose_name, attrs in \
                                    (context['user'].get_profile().is_juridical and \
                                    settings.PROFILE_MENU_JURIDICAL or settings.PROFILE_MENU_PHISICAL):
        menu.add(view_name, verbose_name, attrs)
    
    return {'account_profile_menu_items':menu, 'user':context['user']}

@register.inclusion_tag('top_menu.html', takes_context=True)
def staff_menu(context):
    """
    Show menu for user's "cabinet" for staff
    """
    from lib.menu import Menu
    menu = Menu(context['current_view_name']) 
    for view_name, verbose_name, id in settings.PERSONAL_AREA_STAFF_MENU:
        menu.add(view_name, verbose_name, attrs={"id": id})
    
    return {'menu': menu}
