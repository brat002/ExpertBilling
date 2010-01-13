# -*- coding=utf-8 -*-
# $id$
import web
from beaker.middleware import SessionMiddleware
import controllers

urls = (
     '/login/', 'controllers.index.Login',
     '/account/(.*)/','controllers.account.Account',
     '/', 'controllers.index.StartPage',
)

# Session support
def session_mw(app):
    return SessionMiddleware(app, key = "0985h08tg2q3ogih34ht523th3o4")

web.webapi.internalerror = web.debugerror
# connect to the database
web.config.db_parameters = dict(dbn='postgres', db='mikrobill', user='mikrobill', 
    pw='1234', host='10.10.1.1', port='5432')


if __name__ == "__main__":
    web.run(urls, globals(), web.reloader, *(session_mw,))