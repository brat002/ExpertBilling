#-*-coding: utf-8 -*-

from cassa.forms import PayForm
from lib.decorators import render_to
from billservice.models import SystemUser, Transaction, Account, TransactionType
import datetime
@render_to("cassa/index.html")
def index(request):
    message=''
    if request.method == 'POST':
        form = PayForm(request.POST)
        if form.is_valid():
            username=form.cleaned_data['username']
            password=form.cleaned_data['password']
            summ=form.cleaned_data['summ']
            account_username=form.cleaned_data['account_username']
            description=form.cleaned_data['description']
            promise=form.cleaned_data['promise']
            try:
                user=SystemUser.objects.get(username=username, text_password=password)
            except:
                return {'form':form,'message':u'Пользователя с таким логином и паролем не существует',}

            try:
                account=Account.objects.get(username=account_username)
            except:
                return {'form':form,'message':u'Пользователя с таким логином и паролем не существует',}
            
            t=Transaction()
            t.account=account
            t.type=TransactionType.objects.get(internal_name='MANUAL_TRANSACTION')
            t.approved=True
            t.summ=-1*summ
            t.description=description
            t.created=datetime.datetime.now()
            t.promise=promise
            t.systemuser=user
            t.save()
            account=Account.objects.get(username=account_username)
            
            message=u'Платёж успешно выполнен. Новый баланс пользователя %s' % account.ballance
            
    else:
        form = PayForm()
        
    return {'form':form,'message':message}
