# -*- coding: utf-8 -*-

import commands
import datetime

from mako.template import Template as mako_template
from django.template import Template as DjangoTemplate
from django.db import connection
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.db.models.fields import DecimalField
from django.db.models.fields.related import ForeignKey

import IPy
from billservice import authenticate, log_in
from billservice.forms import (
    DocumentModelForm,
    DocumentRenderForm,
    LoginForm,
    TemplateForm
)
from billservice.helpers import systemuser_required
from billservice.models import (
    Account,
    AccountHardware,
    City,
    Document,
    House,
    IPInUse,
    IPPool,
    Operator,
    Organization,
    Street,
    SubAccount,
    SystemUser,
    Template,
    Transaction
)
from ebscab.lib.decorators import ajax_request
from ebscab.lib.ssh_paramiko import ssh_client
from object_log.models import LogItem
from radius.models import ActiveSession
from tasks import cred, rosClient, rosExecute, PoD

import ebsadmin.tables
from ebsadmin.forms import TableColumnsForm
from ebsadmin.lib import instance_dict
from ebsadmin.models import TableSettings
from randgen import GenUsername as nameGen, GenPasswd as GenPasswd2


log = LogItem.objects.log_action


class Object(object):

    def __init__(self, result=[], *args, **kwargs):
        for key in result:
            setattr(self, key, result[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])


@ajax_request
def simple_login(request):
    form = LoginForm(request.POST)
    if form.is_valid():
        try:
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if isinstance(user.account, SystemUser):
                if user.account.host != '0.0.0.0/0':
                    try:
                        if not (IPy.IP(request.META.get("REMOTE_ADDR")) in
                                IPy.IP(user.account.host)):
                            return {
                                "status": False,
                                "message": _(u"Access for your IP address "
                                             u"forbidden")
                            }
                    except Exception, e:
                        return {
                            "status": False,
                            "message": _("Login error. May be systemuser "
                                         "host syntax error")
                        }
                log_in(request, user)
                user.account.last_login = datetime.datetime.now()
                user.account.last_ip = request.META.get("REMOTE_ADDR")
                user.account.save()
                return {
                    "status": True,
                    "message": _("Login succeful")
                }
            else:
                return {
                    "status": False,
                    "message": _("Login forbidden to this action")
                }
        except Exception, e:
            return {
                "status": False,
                "message": _("Login can`t be authenticated")
            }

    return {
        "status": False,
        "message": "Login not found"
    }


@ajax_request
@systemuser_required
def generate_credentials(request):
    action = request.POST.get('action') or request.GET.get('action')
    if action == 'login':
        return {"success": True, 'generated': nameGen()}
    if action == 'password':
        return {"success": True, 'generated': GenPasswd2()}
    return {
        "success": False
    }


@ajax_request
@systemuser_required
def get_mac_for_ip(request):
    if not (request.user.account.has_perm('subaccount.getmacforip')):
        return {
            'status': False,
            'message': _(u'Недостаточно прав для выполнения операции')
        }

    nas_id = request.POST.get('nas_id', None)
    if not nas_id:
        return {
            'status': False,
            'message': _(u'Сервер доступа не указан')
        }
    ipn_ip_address = request.POST.get('ipn_ip_address')

    try:
        nas = Nas.objects.get(id=nas_id)
    except Exception, e:
        return {
            'status': False,
            'message': str(e)
        }

    try:
        IPy.IP(ipn_ip_address)
    except Exception, e:
        return {
            'status': False,
            'message': str(e)
        }

    try:
        apiros = rosClient(nas.ipaddress, nas.login, nas.password)
        command = '/ping =address=%s =count=1' % ipn_ip_address
        rosExecute(apiros, command)
        command = '/ip/arp/print ?address=%s' % ipn_ip_address
        mac = rosExecute(apiros, command).get('mac-address', '')
        apiros.close()
    except Exception, e:
        return {
            'success': False,
            'message': str(e)
        }

    return {
        'success': True,
        'mac': mac
    }


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


@ajax_request
@systemuser_required
def templates(request):
    if not (request.user.account.has_perm('billservice.template_view')):
        return {
            'status': True,
            'records': [],
            'totalCount': 0
        }

    fields = request.POST.get('fields', [])
    id = request.POST.get('id', None)
    type_id = request.POST.get('type_id', None)
    if id and id != 'None':
        items = Template.objects.filter(id=id)
        if not items:
            return {
                'status': False,
                'message': 'Template item with id=%s not found' % id
            }
        if len(items) > 1:
            return {
                'status': False,
                'message': 'Returned >1 items with id=%s' % id
            }
    elif type_id:
        items = Template.objects.filter(type__id=type_id)
    else:
        items = Template.objects.all()

    res = []
    for item in items:
        res.append(instance_dict(item, fields=fields, normal_fields=False))

    return {
        "records": res,
        'status': True,
        'totalCount': len(res)
    }


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


@ajax_request
@systemuser_required
def sql(request):
    if not (request.user.account.has_perm('billservice.rawsqlexecution')):
        return {
            'status': False,
            'records': [],
            'totalCount': 0
        }

    s = request.POST.get('sql', '')
    if not s:
        return {
            'status': False,
            'message': 'SQL not defined'
        }

    cur = connection.cursor()
    try:
        log('RAWSQL',
            request.user,
            request.user.account,
            data={'sql': unicode(s, errors="ignore")})
    except:
        pass

    try:
        cur.execute(s)
        res = dictfetchall(cur)
    except Exception, e:
        return {
            'status': False,
            'message': str(e)
        }

    return {
        "records": res,
        'status': True,
        'totalCount': len(res)
    }


@ajax_request
@systemuser_required
def session_reset(request):
    if not request.user.account.has_perm('radius.reset_activesession'):
        return {
            'status': False,
            'message': _(u'У вас нет прав на сброс сессии')
        }

    id = request.POST.get('id', None)
    res = False
    if id and id != 'None':
        session = ActiveSession.objects.get(id=id)
        if not session:
            return {
                'status': False,
                'message': 'Session item with id=%s not found' % (id,)
            }

        n = session.nas_int
        nas = instance_dict(n)
        acc = instance_dict(session.account)
        subacc = instance_dict(session.subaccount)
        res = PoD.delay(acc,
                        subacc,
                        nas,
                        access_type=session.framed_protocol,
                        session_id=str(session.sessionid),
                        vpn_ip_address=session.framed_ip_address,
                        caller_id=str(session.caller_id),
                        format_string=str(n.reset_action))
        return {
            'status': True,
            'message': _(u'Сессия поставлена в очередь на сброс.')
        }

    return {
        "message": _(u"Данная функция временно не реализована"),
        'status': False
    }


@ajax_request
@systemuser_required
def session_hardreset(request):
    if not request.user.account.has_perm('radius.reset_activesession'):
        return {
            'status': False,
            'message': _(u'У вас нет прав на сброс сессии')
        }

    id = request.POST.get('id', None)
    res = False
    if id and id != 'None':
        session = ActiveSession.objects.get(id=id)
        if not session:
            return {
                'status': False,
                'message': 'Session item with id=%s not found' % (id, )
            }

        n = session.nas_int
        nas = instance_dict(n)
        acc = instance_dict(session.account)
        subacc = instance_dict(session.subaccount)
        res = PoD.delay(acc,
                        subacc,
                        nas,
                        access_type=session.framed_protocol,
                        session_id=str(session.sessionid),
                        vpn_ip_address=session.framed_ip_address,
                        caller_id=str(session.caller_id),
                        format_string=str(n.reset_action))
        session.session_status = 'ACK'
        session.save()
        try:
            if session.ipinuse:
                ipin = session.ipinuse
                ipin.disabled = datetime.datetime.now()
                ipin.save()
        except:
            pass

        return {
            'status': True,
            'message': _(u'Сессия поставлена в очередь на сброс, IP '
                         u'адрес освобождён')
        }

    return {
        "message": _(u"Данная функция временно не реализована"),
        'status': False
    }


@ajax_request
@systemuser_required
def cities(request):
    if not (request.user.account.has_perm('billservice.view_city')):
        return {
            'status': True,
            'records': [],
            'totalCount': 0
        }
    fields = request.POST.get('fields', [])
    id = request.POST.get('id', None)
    if id and id != 'None':
        items = City.objects.filter(id=id)
        if not items:
            return {
                'status': False,
                'message': 'City item with id=%s not found' % id
            }
        if len(items) > 1:
            return {
                'status': False,
                'message': 'Returned >1 items with id=%s' % id
            }

    else:
        items = City.objects.all().order_by('name')

    res = []
    for item in items:
        res.append(instance_dict(item, fields=fields))

    return {
        "records": res,
        'status': True,
        'totalCount': len(res)
    }


@ajax_request
@systemuser_required
def accounthardware(request):
    if not (request.user.account.has_perm('billservice.view_accounthardware')):
        return {
            'status': True,
            'records': [],
            'totalCount': 0
        }
    fields = request.POST.get('fields', [])
    id = request.POST.get('id', None)
    account_id = request.POST.get('account_id', None)
    hardware_id = request.POST.get('hardware_id', None)
    if id and id != 'None':
        items = AccountHardware.objects.filter(id=id)
        if not items:
            return {
                'status': False,
                'message': 'AccountHardware item with id=%s not found' % id
            }
        if len(items) > 1:
            return {
                'status': False,
                'message': 'Returned >1 items with id=%s' % id
            }
    elif account_id:
        items = AccountHardware.objects.filter(account__id=account_id)
    elif hardware_id:
        items = AccountHardware.objects.filter(hardware__id=hardware_id)
    else:
        items = AccountHardware.objects.all()

    res = []
    for item in items:
        res.append(instance_dict(item, fields=fields))

    return {
        "records": res,
        'status': True,
        'totalCount': len(res)
    }


@ajax_request
@systemuser_required
def templates_save(request):
    id = request.POST.get('id')
    if id:
        if not (request.user.account.has_perm('billservice.change_template')):
            return {
                'status': False,
                'message': _(u"У вас нет прав на изменение шаблона")
            }
        item = Template.objects.get(id=id)
        form = TemplateForm(request.POST, instance=item)
    else:
        if not (request.user.account.has_perm('billservice.add_template')):
            return {
                'status': False,
                'message': _(u"У вас нет прав на добавление шаблона")
            }
        form = TemplateForm(request.POST)

    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.save()
            res = {"status": True, 'id': model.id}

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
        except Exception, e:
            res = {
                "status": False,
                "message": str(e)
            }
    else:
        res = {
            "status": False,
            "errors": form._errors
        }

    return res


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
def streets(request):
    if not (request.user.account.has_perm('billservice.view_street')):
        return {
            'status': True,
            'records': [],
            'totalCount': 0
        }

    city_id = request.POST.get('city_id')
    term = request.POST.get('term')
    id = request.POST.get('id')
    items = []
    if city_id:
        if city_id and term:
            items = Street.objects.filter(
                city__id=city_id, name__istartswith=term)
        else:
            items = Street.objects.filter(city__id=city_id)
    elif id:
        items = [Street.objects.get(id=id)]
    else:
        if term:
            items = Street.objects.filter(name__istartswith=term)
        else:
            items = Street.objects.all()
    res = []
    if items.count() > 0:
        for item in items:
            res.append(instance_dict(item))
    else:
        items = Account.objects.filter(
            street__istartswith=term).values('street')
        for item in items:
            res.append({
                'id': None,
                'name': item.get('street')
            })

    return {
        "records": res,
        'status': True,
        'totalCount': len(items)
    }


@ajax_request
@systemuser_required
def getipfrompool(request):
    if not (request.user.account.has_perm('billservice.view_ippool')):
        return {
            'status': True,
            'records': [],
            'totalCount': 0
        }

    default_ip = '0.0.0.0'
    if default_ip:
        default_ip = IPy.IP(default_ip).int()
    pool_id = request.POST.get("pool_id")
    limit = int(request.POST.get("limit", 500))
    start = int(request.POST.get("start", 0))
    term = request.POST.get("term", '')
    if not pool_id:
        return {'records': [], 'status': False}
    pool = IPPool.objects.get(id=pool_id)
    ipinuse = IPInUse.objects.filter(pool=pool, disabled__isnull=True)

    accounts_ip = SubAccount.objects.values_list(
        'ipn_ip_address', 'vpn_ip_address', 'vpn_ipv6_ip_address')
    if term:
        ipinuse = ipinuse.filter(ip__contains=term)

    ipversion = 4 if pool.type < 2 else 6
    accounts_used_ip = []
    for accip in accounts_ip:
        if accip[0]:
            accounts_used_ip.append(IPy.IP(accip[0]).int())
        if accip[1]:
            accounts_used_ip.append(IPy.IP(accip[1]).int())
        if accip[2]:
            accounts_used_ip.append(IPy.IP(accip[2]).int())

    start_pool_ip = IPy.IP(pool.start_ip).int()
    end_pool_ip = IPy.IP(pool.end_ip).int()

    ipinuse_list = [IPy.IP(x.ip).int() for x in ipinuse]
    ipinuse_list += accounts_used_ip

    find = False
    res = []
    x = start_pool_ip
    i = 0
    while x <= end_pool_ip:
        if x not in ipinuse_list and x != default_ip:
            if not term or term and \
                    str(IPy.IP(x, ipversion=ipversion)).rfind(term) != -1:
                res.append(str(IPy.IP(x, ipversion=ipversion)))
            if len(res) == limit:
                break
            i += 1
        x += 1
    return {
        'totalCount': str(len(res)),
        'records': res,
        'status': True
    }


@ajax_request
@systemuser_required
def getipfrompool2(request):
    if not (request.user.account.has_perm('billservice.view_ippool')):
        return {
            'status': True,
            'records': [],
            'totalCount': 0
        }

    default_ip = '0.0.0.0'
    if default_ip:
        default_ip = IPy.IP(default_ip).int()
    pool_id = request.POST.get("pool_id") or request.GET.get("pool_id")
    limit = int(request.POST.get("limit", 500))
    start = int(request.POST.get("start", 0))
    if not pool_id:
        return {
            'records': [],
            'status': False
        }
    pool = IPPool.objects.get(id=pool_id)
    ipinuse = IPInUse.objects.filter(pool=pool, disabled__isnull=True)
    accounts_ip = SubAccount.objects.values_list(
        'ipn_ip_address', 'vpn_ip_address')
    ipversion = 4 if pool.type < 2 else 6
    accounts_used_ip = []
    for accip in accounts_ip:
        accounts_used_ip.append(IPy.IP(accip[0]).int())
        accounts_used_ip.append(IPy.IP(accip[1]).int())

    start_pool_ip = IPy.IP(pool.start_ip).int()
    end_pool_ip = IPy.IP(pool.end_ip).int()

    ipinuse_list = [IPy.IP(x.ip).int() for x in ipinuse]
    ipinuse_list += accounts_used_ip

    find = False
    res = []
    x = start_pool_ip
    i = 0
    while x <= end_pool_ip:
        if x not in ipinuse_list and x != default_ip:
            res.append(str(IPy.IP(x, ipversion=ipversion)))
            i += 1
        x += 1
    return [res[start:start + limit]]


@ajax_request
@systemuser_required
def houses(request):
    if not (request.user.account.has_perm('billservice.view_house')):
        return {
            'status': True,
            'records': [],
            'totalCount': 0
        }

    street_name = request.POST.get('street_name')
    city_id = request.POST.get('city_id')
    term = request.POST.get('term')
    id = request.POST.get('id')
    fields = request.POST.get('fields')
    if street_name:
        if term:
            items = (House.objects
                     .filter(street__name__icontains=street_name,
                             name__istartswith=term)
                     .distinct())
        else:
            items = (House.objects
                     .filter(street__name__icontains=street_name)
                     .distinct())
    elif id:
        items = [House.objects.get(id=id)]
    else:
        if term:
            items = House.objects.filter(name__istartswith=term).distinct()
        else:
            items = House.objects.all().distinct()

    res = []
    for item in items:
        res.append(instance_dict(item, fields=fields))

    return {
        "records": res,
        'status': True,
     'totalCount': len(res)
    }


@ajax_request
@systemuser_required
def actions_set(request):
    if not (request.user.account.has_perm('billservice.actions_set')):
        return {
            'status': False,
            'message': u'У вас нет прав на управление состоянием субаккаунтов'
        }

    subaccount = request.POST.get('subaccount_id')
    action = request.POST.get('action')
    if subaccount:
        sa = SubAccount.objects.get(id=subaccount)
        if action == 'ipn_disable':
            sa.ipn_sleep = False
            sa.save()
            return {
                'status': True,
                'message': 'Ok'
            }
        if action == 'ipn_enable':
            sa.ipn_sleep = True
            sa.save()
            return {
                'status': True,
                'message': 'Ok'
            }

        subacc = instance_dict(SubAccount.objects.get(id=subaccount))
        acc = instance_dict(sa.account)
        acc['account_id'] = acc['id']

        try:
            n = sa.nas
            nas = instance_dict(n)
        except Exception, e:
            return {
                'status': False,
                'message': u'Не указан или не найден указанный сервер доступа'
            }

        if action == 'disable':
            command = n.subacc_disable_action
        elif action == 'enable':
            command = n.subacc_enable_action
        elif action == 'create':
            command = n.subacc_add_action
        elif action == 'delete':
            command = n.subacc_delete_action

        sended = cred(account=acc,
                      subacc=subacc,
                      access_type='ipn',
                      nas=nas,
                      format_string=command)
        sended.wait()

        if action == 'create' and sended == True:
            sa.ipn_added = True
            sa.speed = ''
            sa.save()
            log('EDIT', request.user, sa)
            # TODO: IPN Actions action

        if action == 'delete' and sended == True:
            sa.ipn_enabled = False
            sa.ipn_added = False
            sa.speed = ''
            sa.save()
            log('EDIT', request.user, sa)
            # TODO: IPN Actions action

        if action == 'disable' and sended == True:
            sa.ipn_enabled = False
            sa.save()
            log('EDIT', request.user, sa)
            # TODO: IPN Actions action

        if action == 'enable' and sended == True:
            sa.ipn_enabled = True
            sa.save()
            log('EDIT', request.user, sa)
            # TODO: IPN Actions action

        return {
            'status': sended,
            'message': 'Ok'
        }
    return {
        'status': False,
        'message': 'Ok'
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
def templaterender(request):
    if not request.user.account.has_perm('billservice.documentrender'):
        return {
            'status': False,
            'message': _(u'У вас нет прав на рендеринг документов')
        }

    form = TemplateForm(request.POST)
    if form.is_valid():
        templatetype = form.cleaned_data.get('type')
        t = DjangoTemplate(
            mark_safe(unicode(unicode(form.cleaned_data.get('body')))))
        data = ''

        cur = connection.cursor()
        if templatetype.id == 1:
            account = Account.objects.all()[0]
            c = {
                'account': account,
                'connection': cur
            }

        if templatetype.id == 2:
            account = Account.objects.all()[0]
            operator = Organization.objects.all()[0]
            c = {
                'account': account,
                'operator': operator,
                'connection': cur
            }

        if templatetype.id == 5:
            transaction = Transaction.objects.all()[0]
            operator = Organization.objects.all()[0]
            c = {
                'transaction': transaction,
                'operator': operator,
                'connection': cur
            }

        try:
            data = t.render(c)
        except Exception, e:
            data = u"Error %s" % str(e)

        res = {
            'success': True,
            'body': data.encode("utf-8", 'replace')
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
    # TODO:Сделать дефолтного оператора
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


@systemuser_required
@ajax_request
def testCredentials(request):
    if not (request.user.account.has_perm('billservice.testcredentials')):
        return {
            'status': False,
            'message': _(u'У вас нет на тестирование подключения')
        }
    host, login, password = (request.POST.get('host'),
                             request.POST.get('login'),
                             request.POST.get('password'))
    try:
        print host, login, password
        a = ssh_client(host, login, password, '')
    except Exception, e:

        return {
            'status': False,
            'message': str(e)
        }
    return {
        'status': True
    }


@systemuser_required
@ajax_request
def get_ports_status(request):
    if not (request.user.account.has_perm('billservice.getportsstatus')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на получение статуса портов')
        }

    switch_id = request.POST.get('switch_id')
    if not switch_id:
        return {
            'status': False
        }

    switch = Switch.objects.get(id=switch_id)
    version = '2c' if switch.snmp_version == 1 else '1'
    # oper status .1.3.6.1.2.1.2.2.1.8.
    status, output = commands.getstatusoutput(
        "snmpwalk -v %s -Oeqsn -c %s %s .1.3.6.1.2.1.2.2.1.7" %
        (version, switch.snmp_community, switch.ipaddress))

    if status != 0:
        return {
            'status': False,
            'message': _(u'Невоззможно получить состояние портов')
        }

    ports_status = {}
    for line in output.split("\n"):
        if line.rfind(".") == -1:
            continue

        try:
            oid, value = line.split(" ")
        except Exception, e:
            continue

        id = oid.split(".")[-1]
        ports_status[id] = value

    status, output = commands.getstatusoutput(
        "snmpwalk -v %s -Oeqsn -c %s %s .1.3.6.1.2.1.2.2.1.5" %
        (version, switch.snmp_community, switch_ipaddress))

    if status != 0:
        return {
            'status': False,
            'message': _(u'Невоззможно получить состояние портов')
        }

    ports_speed_status = {}
    for line in output.split("\n"):
        if line.rfind(".") == -1:
            continue
        try:
            oid, value = line.split(" ")
        except Exception, e:
            continue

        id = oid.split(".")[-1]
        ports_speed_status[id] = value

    return {
        'status': True,
        'ports_status': ports_status,
        'ports_speed_status': ports_speed_status
    }


@systemuser_required
@ajax_request
def set_ports_status(request, switch_id):
    if not (request.user.account.has_perm('billservice.setportsstatus')):
        return {
            'status': False,
            'message': _(u'У вас нет на установку статуса портов')
        }

    switch_id = request.POST.get('switch_id')
    if not switch_id:
        return {
            'status': False
        }

    switch = Switch.objects.get(id=switch_id)
    version = '2c' if switch.snmp_version == 1 else '1'
    # получили статусы, чтобы было с чем сравнивать
    status, output = commands.getstatusoutput(
        "snmpwalk -v %s -Oeqsn -c %s %s .1.3.6.1.2.1.2.2.1.7" %
        (version, switch.snmp_community, switch_ipaddress))

    if status != 0:
        return {
            'status': False,
            'message': _(u'Невоззможно сохранить состояние портов')
        }

    ports_status = {}
    for line in output.split("\n"):
        if line.rfind(".") == -1:
            continue

        try:
            oid, value = line.split(" ")
        except Exception, e:
            continue

        id = oid.split(".")[-1]
        ports_status[id] = value

    for port, status in ports:
        if ports_status[port] != status:
            status, output = commands.getstatusoutput(
                "snmpset -v %s -Oeqsn -c %s %s .1.3.6.1.2.1.2.2.1.7.%s i %s" %
                (version,
                 switch.snmp_community,
                 switch_ipaddress,
                 port,
                 1 if status == True else 2))

    status, output = commands.getstatusoutput(
        "snmpwalk -v %s -Oeqsn -c %s %s .1.3.6.1.2.1.2.2.1.7" %
        (version, switch.snmp_community, switch_ipaddress))
    if status != 0:
        return {
            'status': False,
            'message': _(u'Невоззможно сохранить состояние портов')
        }
    ports_status = {}
    for line in output.split("\n"):
        if line.rfind(".") == -1:
            continue

        try:
            oid, value = line.split(" ")
        except Exception, e:
            continue

        id = oid.split(".")[-1]
        ports_status[id] = value

    return {
        'status': True,
        'ports_status': ports_status
    }


def instance_dict(instance, key_format=None, normal_fields=False, fields=[]):
    """
    Returns a dictionary containing field names and values for the given
    instance
    """
    if key_format:
        assert '%s' in key_format, 'key_format must contain a %s'
    key = lambda key: key_format and key_format % key or key

    pk = instance._get_pk_val()
    d = {}
    for field in instance._meta.fields:
        attr = field.name
        if fields and attr not in fields:
            continue

        try:
            value = getattr(instance, attr)
        except:
            value = None

        if isinstance(field, ForeignKey):
            if value is not None:
                try:
                    d["%s_id" % key(attr)] = value.id
                    if normal_fields == False:
                        value = value._get_pk_val()
                    else:
                        value = unicode(value)
                except Exception, e:
                    print e
            else:
                d["%s_id" % key(attr)] = None
                value = None
        elif isinstance(field, DecimalField):
            value = float(value) if value else 0

        d[key(attr)] = value

    for field in instance._meta.many_to_many:
        if pk:
            d[key(field.name)] = [
                obj._get_pk_val()
                for obj in getattr(instance, field.attname).all()
            ]
        else:
            d[key(field.name)] = []
    return d


@ajax_request
@systemuser_required
def table_settings(request):
    table_name = request.POST.get("table_name")
    per_page = request.POST.get("per_page") or 25
    table = getattr(ebsadmin.tables, table_name)
    form = TableColumnsForm(request.POST)
    form.fields['columns'].choices = [(x, x) for x in table.base_columns]
    if form.is_valid():
        try:
            ts = TableSettings.objects.get(name=table_name, user=request.user)
            ts.value = {'fields': form.cleaned_data.get('columns', [])}
            ts.per_page = per_page if per_page not in ['undefined', ''] else 25
            ts.save()
        except Exception, e:
            ts = TableSettings.objects.create(
                name=table_name,
                value={
                    'fields': form.cleaned_data.get('columns', [])
                },
                per_page=per_page,
                user=request.user)
            ts.save()

    return {
        "status": True
    }
