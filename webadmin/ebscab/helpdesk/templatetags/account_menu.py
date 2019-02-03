# -*- coding: utf-8 -*-

from django import template
from django.conf import settings

from helpdesk.settings import PERSONAL_AREA_MENU
from ebscab.utils.menu import Menu


register = template.Library()


@register.inclusion_tag('top_menu.html', takes_context=True)
def account_menu(context):
    """
    Show menu for user's "cabinet"
    """
    menu = Menu(context['current_view_name'])
    for view_name, verbose_name in PERSONAL_AREA_MENU:
        menu.add(view_name, verbose_name)

    return {
        'menu': menu
    }


@register.inclusion_tag('helpdesk/tags/account_profile_menu.html',
                        takes_context=True)
def account_profile_menu(context):
    """
    Show right menu in profile page
    """
    menu = Menu()
    for view_name, verbose_name, attrs in \
        (context['user'].get_profile().is_juridical and
         settings.PROFILE_MENU_JURIDICAL or settings.PROFILE_MENU_PHISICAL):
        menu.add(view_name, verbose_name, attrs)

    return {
        'account_profile_menu_items': menu,
        'user': context['user']
    }


@register.inclusion_tag('top_menu.html', takes_context=True)
def staff_menu(context):
    """
    Show menu for user's "cabinet" for staff
    """
    menu = Menu(context['current_view_name'])
    for view_name, verbose_name, id in settings.PERSONAL_AREA_STAFF_MENU:
        menu.add(view_name, verbose_name, attrs={"id": id})

    return {
        'menu': menu
    }
