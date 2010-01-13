# -*- coding=utf-8 -*-
import web
from render import base, render
from components.auth import login_required, dologin
from models import account
from models import tarif

class StartPage:
    @login_required
    def GET(self):
        session = web.ctx.environ['beaker.session']
        try:
            user = account.get(session['id'])
            atarif = tarif.get_by_account_id(user.id)
        except Exception, e:
            web.debug(e)
            print web.header('HTTP/1.1 GET /', '404 Not Found')
            return False
        web.output(base.layout(render.index.start_page(user, atarif)))
    @login_required
    def POST(self):
        pass

class Login:
    def GET(self):
        web.output(render.index.login_page())
        
    def POST(self):
        post = web.input()
        from models.account import get_user
        
        user = get_user(post.username, post.password)
        if user:
            dologin(user)
            web.seeother('/')
        web.output(render.index.login_page())
