# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from object_log.models import LogItem

from ebsadmin.forms import LogViewer
import commands
import os
log = LogItem.objects.log_action



@login_required
@render_to('ebsadmin/logview.html')
def logview(request):
        
    if  not (request.user.account.has_perm('billservice.view_log_files')):
        return {'status':False, 'message': u'У вас нет прав на просмотр лог-файлов'}
    if  not (request.user.account.has_perm('billservice.list_log_files')):
        return {'status':False, 'message': u'У вас нет прав на получение списка лог-файлов'}
    
    logfiles = os.listdir('/opt/ebs/data/log/')
    
    if request.method=='GET':
        form = LogViewer(request.GET)
        form.fields['log'].choices=[(x,x) for x in logfiles]
        o=''

        if form.is_valid():
            log_name = form.cleaned_data.get("log")
            count =  form.cleaned_data.get("lines", 0)
            all_file = form.cleaned_data.get('full')
    

            if all_file:
                s, o = commands.getstatusoutput("cat /opt/ebs/data/log/%s" % log_name.replace('/',''))
            else:
                s, o = commands.getstatusoutput("tail -n %s /opt/ebs/data/log/%s" % (count, log_name.replace('/','')))

            return { 'form':form, 'content':unicode(o, errors='ignore') }
    

    form = LogViewer()
    form.fields['log'].choices=[(x,x) for x in logfiles]

    return { 'form':form}


    