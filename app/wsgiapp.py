# -*- coding:utf-8 -*-

from webframework.myframwork import MyApp, request, response, error
from webframework.template import render_template
from webframework.utils import check_cookie

wsgi_app = MyApp()


@wsgi_app.route('/4')
def hello():
    response.status = 200
    if request.cookie is None:
        response.set_cookie('wang', 'test', secret_key='wang')
    else:
        print('-----')
        print(request.cookie['wang'].value)
        is_passed = check_cookie(request.cookie['wang'].value, 'wang')
        if is_passed:
            print('Cookie check passed!')
        else:
            print('Cookie check failed!')

    return '<h1>hello world!</h1>'


@wsgi_app.route(r'/wiki/<name>')
def test(name):
    response.status = 200
    response.add_header('Content-Length', '15')
    return 'hello world' + name


@wsgi_app.route(r'/test')
def test1():
    return error(404)


@wsgi_app.route(r'/render')
def test3():
    return render_template('base.html', name='Mako')


