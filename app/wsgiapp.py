# -*- coding:utf-8 -*-

from webframework.myframwork import MyApp, request, response

wsgi_app = MyApp()


@wsgi_app.route('/')
def hello():
    response.status_code = 200
    response.status = str(response.status_code) + ' OK'
    response.add_header('Content-Length', '11')
    return 'hello world'


@wsgi_app.route(r'/wiki/(?P<name>[A-Za-z0-9_]+)')
def test(name):
    response.status_code = 200
    response.status = str(response.status_code) + ' OK'
    response.add_header('Content-Length', '15')
    return 'hello world' + name
