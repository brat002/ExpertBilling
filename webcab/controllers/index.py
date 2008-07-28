# -*- coding=utf-8 -*-
import web
from render import render

class StartPage:
    def GET(self, name):
        i = web.input(times=1)
        if not name: name = 'world'
        web.output(render.index.start_page(name=name))
