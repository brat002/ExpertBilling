# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.template import Template as DjangoTemplate
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from mako.template import Template as mako_template

from billservice.forms import DocumentModelForm, DocumentRenderForm
from billservice.utils import systemuser_required
from billservice.models import (
    Account,
    Document,
    Operator,
    Template,
    Transaction
)
from ebscab.lib.decorators import ajax_request
from object_log.models import LogItem

from ebscab.utils import instance_dict


log = LogItem.objects.log_action


@ajax_request
@systemuser_required
def document(request):
    if not (request.user.account.has_perm('billservice.document_view')):
        return {
            'status': True,
            'records': [],
            'totalCount': 0
        }

    account_id = request.POST.get('account_id')
    items = Document.objects.filter(account__id=account_id)
    res = []
    for item in items:
        res.append(instance_dict(item, normal_fields=True))

    return {
        "records": res
    }


@systemuser_required
def documentrender(request):
    if not request.user.account.has_perm('billservice.documentrender'):
        return {
            'status': False,
            'message': u'У вас нет прав на рендеринг документов'
        }

    form = DocumentRenderForm(request.POST)
    if form.is_valid():
        template = Template.objects.get(id=form.cleaned_data.get('template'))
        t = DjangoTemplate(mark_safe(unicode(template.body)))
        print template.type.id
        data = ''
        if template.type.id == 1:
            account = Account.objects.get(id=form.cleaned_data.get('account'))
            c = {'account': account}

        if template.type.id == 5:
            tr = Transaction.objects.get(
                id=form.cleaned_data.get('transaction'))
            c = {'transaction': tr}

        if template.type.id == 7:
            # cards
            c = {'cards': form.cleaned_data.get('cards')}

        try:
            data = t.render(c)
        except Exception, e:
            data = u"Error %s" % str(e)

        res = data.encode("utf-8", 'replace')

    return HttpResponse(res)


@ajax_request
@systemuser_required
def document_save(request):
    id = request.POST.get('id')
    if id:
        item = Document.objects.get(id=id)
        form = DocumentModelForm(request.POST, instance=item)
    else:
        form = DocumentModelForm(request.POST)

    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.save()

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            res = {
                "success": True
            }
        except Exception, e:

            res = {
                "success": False,
                "message": str(e)
            }
    else:
        res = {
            "success": False,
            "errors": form._errors
        }
    return res


@ajax_request
@systemuser_required
def cheque_render(request):
    if not request.user.account.has_perm('billservice.documentrender'):
        return {
            'status': False,
            'message': _(u'У вас нет прав на рендеринг документов')
        }
    id = request.POST.get('id')  # transaction_id
    transaction = Transaction.objects.get(id=id)
    template = Template.objects.get(type__id=5)
    templ = mako_template(unicode(template.body), input_encoding='utf-8')
    data = ''

    account = transaction.account
    # TODO: Сделать дефолтного оператора
    operator = Operator.objects.all()
    if operator:
        operator = operator[0]
    try:
        data = templ.render_unicode(
            account=account, transaction=transaction, operator=operator)
    except Exception, e:
        data = u"Error %s" % str(e)

    res = {
        'success': True,
        'body': data.encode("utf-8", 'replace')
    }

    return res
