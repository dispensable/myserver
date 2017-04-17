# -*- coding:utf-8 -*-


def wsgi_app(environ, start_response):
    print(environ)
    status = "200 OK"
    headers = [('Content-type', 'text/plain'), ('Content-length', 21)]
    start_response(status, headers)

    response = ['hello world\n', 'stranger\n']

    return (line.encode() for line in response)


class MyApp(object):
    """ WSGI app """
    def __init__(self):
        pass

    def __call__(self, environ, start_response, exe_info):
        pass

    def add_url(self, func):
        pass

    def add_filter(self, filter):
        pass

    @property
    def template_engine(self):
        pass

    @template_engine.setter
    def template_engine(self, engine):
        pass

    def run(self, port=8080, host='127.0.0.1'):
        pass