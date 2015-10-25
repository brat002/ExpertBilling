# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem

from ebsadmin.tables import CommentTable

from ebsadmin.forms import CommentForm, CommentDoneForm
from ebsadmin.models import Comment
from django.contrib import messages

log = LogItem.objects.log_action
from billservice.helpers import systemuser_required
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
import datetime

@systemuser_required
@render_to('ebsadmin/comment_edit.html')
def comment_edit(request):
    

    id = request.POST.get("id")
    
    item = None
    if request.method == 'POST': 
        if  not (request.user.account.has_perm('ebsadmin.edit_comment')):
           return {'status':False, 'message': _(u'У вас нет прав на добавление/редактирование комментариев')}
        print request
        if id:
            
            model = Comment.objects.get(id=id)
            if not request.POST.get('done_comment'):
                form = CommentForm(request.POST, instance=model)
            else:
                 form = CommentDoneForm(request.POST, instance=model)
        else:
            
            form = CommentForm(request.POST) 

        if form.is_valid():

            model = form.save(commit=False)
            model.save()
            log('CREATE', request.user, model) 
                    
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return {  'status': True,  } 
        else:
            print form._errors
            return {'form':form,  'status': False,  } 
    else:
        object_id = request.GET.get("object_id")
        content_type = request.GET.get("content_type")
        id = request.GET.get("id")
        done = request.GET.get("done")
        if object_id and content_type:

            #item = Comment.objects.get(id=id)
            
            form = CommentForm(initial={'object_id': object_id, 'content_type': ContentType.objects.get(id=content_type)})
        elif id:
            if done:
                form = CommentDoneForm(instance = Comment.objects.get(id=id), initial={'done_date': datetime.datetime.now(), 'done_systemuser': request.user.account})
            else:
                form = CommentForm(instance = Comment.objects.get(id=id))
        else:
            form = CommentForm()

    return { 'form':form, 'status': False, 'item': item} 


@ajax_request
@systemuser_required
def comment_delete(request):
   if  not (request.user.account.has_perm('ebsadmin.delete_comment')):
       return {'status':False, 'message': _(u'У вас нет прав на удаление комментариев')}
   id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
   if id:
       try:
           item = Comment.objects.get(id=id)
       except Exception, e:
           return {"status": False, "message": _(u"Указанный комментарий не найден %s") % str(e)}
       log('DELETE', request.user, item)
       item.delete()
       return {"status": True}
   else:
       return {"status": False, "message": "Comment not found"} 
