# -*- coding:utf-8 -*-

from webframework.myframwork import MyApp, request, response, error

wsgi_app = MyApp()


@wsgi_app.route('/')
def hello():
    response.status_code = 200
    response.status = 'OK'
    response.add_header('Content-Length', '11')
    if request.cookie is None:
        response.set_cookie('wang', 'test', secret_key='wang')
    else:
        print(request.cookie)
    return '<h1>hello world!</h1>'


@wsgi_app.route(r'/wiki/(?P<name>[A-Za-z0-9_]+)')
def test(name):
    response.status_code = 200
    response.status = 'OK'
    response.add_header('Content-Length', '15')
    return 'hello world' + name


@wsgi_app.route(r'/test')
def test1():
    return error(404)
