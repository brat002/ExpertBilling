# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem

from ebsadmin.tables import NewsTable

from billservice.forms import NewsForm
from billservice.models import News, AccountViewedNews, Account
from django.contrib import messages
log = LogItem.objects.log_action
from billservice.helpers import systemuser_required


@systemuser_required
@render_to('ebsadmin/news_list.html')
def news(request):
    if  not (request.user.has_perm('billservice.view_news')):
        messages.error(request, u'У вас нет прав на доступ в этот раздел.', extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')
    res = News.objects.all()
    table = NewsTable(res)
    table_to_report = RequestConfig(request, paginate=False if request.GET.get('paginate')=='False' else {"per_page": request.COOKIES.get("ebs_per_page")}).configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
    return {"table": table} 
    
@systemuser_required
@render_to('ebsadmin/news_edit.html')
def news_edit(request):
    id = request.POST.get("id")

    item = None

    if request.method == 'POST': 

        if id:
            model = News.objects.get(id=id)
            form = NewsForm(request.POST, instance=model) 
            if  not (request.user.account.has_perm('billservice.change_news')):
                messages.error(request, u'У вас нет прав на редактирование новости', extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)
        else:
            form = NewsForm(request.POST) 
            if  not (request.user.account.has_perm('billservice.add_news')):
                messages.error(request, u'У вас нет прав на создание новости', extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)


        if form.is_valid():
            accounts = form.cleaned_data.get('accounts', [])
            model = form.save(commit=False)
            model.save()
            accounts_viewednews = [x.get("account__id") for x in AccountViewedNews.objects.filter(news=model).values('account__id')]
            if model.private or model.agent:
                AccountViewedNews.objects.filter(news=model).exclude(account__in=accounts).delete() # Удалили AccountViewedNews аккаунтов, которых нет в новом списке 
                for ac in accounts: #Досоздали недостающие аккаунты
                    if ac in accounts_viewednews: continue
                    AccountViewedNews.objects.create(news=model, account=Account.objects.get(id=ac), viewed=False)
            elif not (model.private or model.agent):
                AccountViewedNews.objects.filter(news=model, account__in=accounts).delete() 
    
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return HttpResponseRedirect(reverse("news"))
        else:

            return {'form':form,  'status': False, 'item': model} 
    else:
        id = request.GET.get("id")
        if  not (request.user.account.has_perm('billservice.view_news')):
            messages.error(request, u'У вас нет прав на доступ в этот раздел.', extra_tags='alert-danger')
            return HttpResponseRedirect('/ebsadmin/')
        if id:


            item = News.objects.get(id=id)
            accounts = [x.get("account__id") for x in AccountViewedNews.objects.filter(news=item).values('account__id')]
            print accounts
            form = NewsForm(instance=item, initial={'accounts': accounts})
        else:
            accounts = request.GET.get('accounts', '')
            if accounts:
                form = NewsForm(initial={'accounts': accounts.split(",")})
            else:
                form = NewsForm()

    return { 'form':form, 'status': False, 'item': item} 

@ajax_request
@systemuser_required
def news_delete(request):
    if  not (request.user.account.has_perm('billservice.delete_news')):
        return {'status':False, 'message': u'У вас нет прав на удаление новостей'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = News.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанная новость не найдена %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "News not found"} 
    