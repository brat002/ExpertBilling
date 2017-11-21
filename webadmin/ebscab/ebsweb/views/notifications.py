# -*- coding: utf-8 -*-

from billservice.models import AccountViewedNews

from ebsweb.views.base import ProtectedDetailView, ProtectedListView


class NotificationsView(ProtectedListView):
    context_object_name = 'notifications'
    paginate_by = 10
    template_name = 'ebsweb/notifications/list.html'

    def get_queryset(self):
        return (AccountViewedNews.objects
                .filter(account=self.request.user.account)
                .ordered())


class NotificationView(ProtectedDetailView):
    context_object_name = 'notification'
    template_name = 'ebsweb/notifications/detail.html'

    def get_queryset(self):
        return (AccountViewedNews.objects
                .filter(account=self.request.user.account))

    def get_object(self):
        obj = super(NotificationView, self).get_object()
        if not obj.viewed:
            obj.viewed = True
            obj.save()
        return obj
