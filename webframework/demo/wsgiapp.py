# -*- coding:utf-8 -*-

from webframework.myframwork import MyApp, request, response, error, redirect
from webframework.myframwork import render_template
from webframework.utils import check_cookie

import os

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


@wsgi_app.route(r'/wiki/json')
def json():
    return {'test': 1, 'test2': 2}


@wsgi_app.route(r'/test')
def test1():
    return error(404)


@wsgi_app.route(r'/render')
def test3():
    return render_template('base.html', name='Mako',
                           template_dir=os.getcwd()+'/demo/templates')


@wsgi_app.route(r'/')
def test4():
    return redirect('http://127.0.0.1:8080/4')


@wsgi_app.hook(name='after_request')
def test22():
    print('test after request hook')


@wsgi_app.route(r'/render', method='POST')
def form_test():
    print(request.form.getvalue('beans'))
    response.status_code = 201
    return 'test'
