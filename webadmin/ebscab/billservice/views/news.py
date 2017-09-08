# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _

from ebscab.utils.decorators import ajax_request

from billservice.models import AccountViewedNews


@ajax_request
@login_required
def news_delete(request):
    message = _(u'Невозможно удалить новость, попробуйте позже')
    if request.method == 'POST':
        news_id = request.POST.get('news_id', '')
        try:
            news = (AccountViewedNews.objects
                    .get(id=news_id, account=request.user.account))
        except:
            return {
                'message': message
            }
        news.viewed = True
        news.save()
        return {
            'message': _(u'Новость успешно удалена')
        }
