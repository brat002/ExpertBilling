# -*- coding:utf-8 -*-
from lib.decorators import render_to

from django.http import HttpResponseRedirect
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login, logout

from account.forms import LoginForm

@render_to('account/login.html')
def _login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(username=username, password=password)
        print 1
        if user is not None:
            login(request, user)
            print 2
            return HttpResponseRedirect('/files/category/')
        else:
            error_messge = u'Проверьте заполнение полей формы.'
            form = LoginForm({'username':username, 'password':password })
            print 3
            return {
                     'error_messge':error_messge,
                     'form':form,
                    }
    else:
        print 4
        form = LoginForm()
        return {
                'form':form,
                }

        
def _logout(request):
    logout(request)
    return HttpResponseRedirect('/login/')
