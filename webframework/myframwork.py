# -*- coding:utf-8 -*-

from .routin import Router
from .request import RequestWrapper
from .routin import Route
from .response import ResponseWrapper
from .error import HttpError, RouteNotFoundException
from json import dumps
import itertools
from .utils import CloseIter


request = RequestWrapper()
response = ResponseWrapper()


class MyApp(object):
    """ WSGI app """
    def __init__(self, name='default_app'):
        self.name = name
        self.router = Router()
        self.routes = []
        self.hooks = {'before_request': [],
                      'after_request': [],
                      'before_first_request': []}

    def __call__(self, environ, start_response, exe_info=None):
        return self.wsgi(environ, start_response)

    def wsgi(self, environ, start_response, exe_info=None):
        body = self.convert_to_wsgi(self.handle_req(environ))
        response.add_body(body)
        start_response(response.status_line, response.headers)
        return response.body

    def handle_req(self, environ):
        """ 处理请求 """
        # 创建全局request和response变量
        request.init(environ)
        response.init()

        # 匹配对应的路由
        try:
            r_route, args = self.router.match(environ)
        except RouteNotFoundException:
            return error(404)

        # 根据路由执行函数并返回值
        if args:
            return r_route.call(**args)
        return r_route.call()

    def convert_to_wsgi(self, respiter):
        """ 将各类返回值转化为wsgi兼容对象
            字典： 转化为json
            空字符串，False, None, None True VALUES: ''
            Unicode字符串（str）： bytes字符串
            HttpError or HttpResponse 对象:
            FilesObject： FileWrapper
            Iterable or Generators： 迭代器对象或者生成器对象，并调用next方法
        """
        if isinstance(respiter, dict):
            response.content_type = 'application/json'
            try:
                content = dumps(respiter).encode()
            except TypeError:
                raise
            response.content_len = len(content)
            return [content]

        elif not respiter:
            response.content_len = 0
            return []

        elif isinstance(respiter, (tuple, list)) and \
                isinstance(respiter[0], (str, bytes)):
            respiter = respiter[0][0:0].join(respiter)
            return self.convert_to_wsgi(respiter)

        elif isinstance(respiter, str):
            response.content_len = len(respiter.encode())
            return [respiter]

        elif isinstance(respiter, bytes):
            response.content_len = len(respiter)
            return [respiter]

        elif isinstance(respiter, HttpError):
            response.status = respiter.status_code
            response.headers = respiter.headers
            return [respiter.body]

        elif hasattr(respiter, 'read'):
            FileWrapper = request.environ.get('wsgi.file_wrapper')
            return FileWrapper(respiter)

        # iter
        try:
            iter_out = iter(respiter)
            first = next(iter_out)

            while not filter:
                first = next(iter_out)

        except StopIteration:
            return self.convert_to_wsgi('')
        except HttpError as e:
            first = e
        except (KeyboardInterrupt, SystemExit, MemoryError):
            raise
        except Exception as error:
            first = HttpError(500, 'Unhandled exception')

        if isinstance(first, HttpError):
            return self.convert_to_wsgi(first)
        elif isinstance(first, bytes):
            new_respiter = itertools.chain([first], iter_out)
        elif isinstance(first, str):
            new_respiter = map(lambda x: x.encode(response.charset),
                               itertools.chain([first], iter_out))
        else:
            return self.convert_to_wsgi(
                HttpError(500, 'Unsupported iter type: {}'.format(type(first))))
        if hasattr(respiter, 'close'):
            new_respiter = CloseIter(new_respiter, iter_out.close)
        return new_respiter

    def add_hook(self, hook):
        pass

    def remove_hook(self, hook):
        pass

    def trigger_hook(self, hook_name, *args, **kwargs):
        pass

    def hook(self, name):
        pass

    def install(self, plugin):
        pass

    def uninstall(self, plugin):
        pass

    def reset_routes(self, route=None):
        pass

    def close(self):
        pass

    def match(self, environ):
        pass

    def url_for(self, routename):
        pass

    def route(self, path=None, method='GET', callback=None,
              name=None, apply=None, skip=None, **config):
        """ 路由装饰器函数
            语法:
            @app.route(path='/hello/<name>')
            def hello_world(name):
                return 'hello world' + str(name)
        """
        def wrapper(func):
            this_route = Route(path, method, callback, name, apply, skip, func, config)
            self.routes.append(this_route)
            self.router.add_route(this_route)
            return func

        return wrapper

    def run(self, port=8080, host='127.0.0.1'):
        pass


def error(status_code, phrase=None):
    return HttpError(status_code, phrase=phrase)


def render_template():
    pass