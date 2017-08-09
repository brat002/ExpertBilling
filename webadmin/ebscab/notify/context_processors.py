# -*- coding: utf-8 -*-


def notifications(request):
    return {
        'notifications': request.notifications
    }
