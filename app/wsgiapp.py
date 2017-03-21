# -*- coding:utf-8 -*-


def wsgi_app(environ, start_response):
    print(environ)
    status = "200 OK"
    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)

    response = ['hello world', 'stranger']

    return (line.encode() for line in response)