 #-*- coding=UTF-8 -*-
from hashlib import md5

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User 
from billservice.models import Account, SystemUser

import logging
log = logging.getLogger('billservice.backend')

def get_account(**kwargs):
    log.debug("get_account with %r" % kwargs)
    accounts = []
    for m in [Account, SystemUser]:
        try:
            accounts.append(m.objects.get(**kwargs))
            log.debug("Found for model %r" % m)
        except (Account.DoesNotExist, SystemUser.DoesNotExist), e:
            log.debug("An error occured: %r" % e)
    if not accounts:
        return None 
    else:
        return accounts[0]

def check_password(obj, row_password):
    #_hash = md5(row_password).hexdigest()
    if isinstance(obj, Account):
        log.debug('Account obj found, try to compare %s == %s' % (obj.password, row_password))
        return unicode(obj.password) == unicode(row_password)
    else:
        log.debug('SystemUser obj found, try to compare %s == %s' % (obj.text_password, row_password))
        return unicode(obj.text_password) == unicode(row_password) #if password is correct and user role admin or member of support team

class LoginUserBackend(ModelBackend):
    
    def authenticate(self, username=None, password=None):
        log.debug("auth called with args: %r"%locals())
        account = get_account(username=username)
        #print account
        if account and check_password(account, password):
            if isinstance(account, SystemUser) and not account.status:
                return
            user, created = User.objects.get_or_create(username=username)
            log.debug("User %s was %s" % (user, created and 'created' or 'found'))
            if created:
                user.set_password(password)
                user.is_active = True
                user.email = account.email or ''
                if isinstance(account, SystemUser):
                    log.debug("superuser!")
                    user.is_staff = True
                    
                    if account.username=='admin':
                        user.is_superuser = True
                user.save()

            log.debug("User authorized: account is %s, user is %s" % (account, user))
            user.account = account
            return user
        log.debug('Auth failed for account %s'%account)
        return None

        
    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            account = get_account(username=user.username) 
            user.account = account
            return user
        except Exception, e:
            return None
