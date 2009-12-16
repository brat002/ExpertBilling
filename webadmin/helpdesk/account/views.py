# -*- coding=utf-8 -*-
from django.contrib.auth import authenticate, logout as log_out, login as _login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from lib.decorators import render_to
from account.forms import LoginForm

@render_to('account/login.html')
def login(request):
    """
    Аутентификация и авторизация пользователя.
    После успешной авторизации перенаправляет на предыдущую страницу.
    """
    
    if not request.user.is_anonymous():
        return HttpResponseRedirect('/')
    response={}
    if request.method=="POST":
        form =LoginForm(request.POST)
        response['form']  =  form
        if form.is_valid():
            login = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=login, password=password)
            if user:
                _login(request, user)
                return HttpResponseRedirect('/')
    else:
        form  = LoginForm()
    response['form'] =form
    return response
    