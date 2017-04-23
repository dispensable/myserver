# -*- coding:utf-8 -*-

from .routin import Router
from .request import RequestWrapper
from .routin import Route
from .response import ResponseWrapper
from .error import HttpError, RouteNotFoundException
from json import dumps
import itertools
from .utils import CloseIter
import traceback


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
        self.plugins = []

    def __call__(self, environ, start_response, exe_info=None):
        return self.wsgi(environ, start_response)

    def wsgi(self, environ, start_response, exe_info=None):
        try:
            body = self.convert_to_wsgi(self.handle_req(environ))

            if response.status in (100, 101, 204, 304) or \
                            environ['REQUEST_METHOD'] == 'HEAD':
                if hasattr(body, 'close'):
                    body.close()
                body = []

            start_response(response.status_line, response.headers)
            return body
        except (KeyboardInterrupt, SystemExit, MemoryError):
            raise
        except Exception as e:
            environ['wsgi.errors'].write(traceback.format_exc())
            environ['wsgi.errors'].flush()

            resp = HttpError(500, 'Internal Server Error',
                             'Error Happened when handle {}'.format(
                                 environ['PATH_INFO']),
                             traceback.format_exc())

            start_response(resp.status_line, resp.headers)
            return [resp.body.encode()]

    def handle_req(self, environ):
        """ 处理请求 """
        # 添加环境变量
        environ['myserver.app'] = self

        # 创建全局request和response变量
        request.init(environ)
        response.init()

        try:
            self.trigger_hook('before_request')
            r_route, args = self.router.match(environ)
            environ['myserver.handle'] = r_route
            environ['myserver.route'] = r_route
            environ['route.url_args'] = args

            if args:
                return r_route.call(**args)
            return r_route.call()
        except RouteNotFoundException:
            return error(404)
        except (KeyboardInterrupt, SystemExit, MemoryError):
            raise
        except Exception as e:
            environ['wsgi.errors'].write(traceback.format_exc())
            environ['wsgi.errors'].flush()
            return error(500, 'Internal Server Error')
        finally:
            try:
                self.trigger_hook('after_request')
            except HttpError as e:
                return e

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

    def add_hook(self, hookname, func):
        self.hooks[hookname].append(func)

    def remove_hook(self, hookname, func):
        if hookname in self.hooks and func in self.hooks[hookname]:
            self.hooks[hookname].remove(func)

    def trigger_hook(self, hook_name, *args, **kwargs):
        return [hook(*args, **kwargs) for hook in self.hooks[hook_name][:]]

    def hook(self, name):
        def wrapper(func):
            if name in self.hooks:
                self.add_hook(name, func)
            return func
        return wrapper

    def install(self, plugin):
        if hasattr(plugin, 'install'):
            plugin.install(self)
        if not callable(plugin) and \
            not hasattr(plugin, 'apply'):
            raise TypeError('Plugin must be callable or implement .apply() method')
        self.plugins.append(plugin)
        self.reset()
        return plugin

    def uninstall(self, plugin):
        pass

    def reset(self, route=None):
        pass

    def close(self):
        for plugin in self.plugins:
            if hasattr(plugin, 'close'):
                plugin.close()

    def match(self, environ):
        self.router.match(environ)

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

    def get(self, path=None, method='GET', **options):
        """ handy decorator with method get """
        return self.route(path, method, **options)

    def post(self, path=None, method='post', **options):
        """ handy decorator with method post """
        return self.route(path, method, **options)

    def put(self, path=None, method='PUT', **options):
        """ handy decorator with method put """
        return self.route(path, method, **options)

    def delete(self, path=None, method='DELETE', **options):
        """ handy decorator with method delete """
        return self.route(path, method, **options)

    def patch(self, path=None, method='PATCH', **options):
        """ handy decorator with method patch """
        return self.route(path, method, **options)

    def run(self, port=8080, host='127.0.0.1'):
        pass


def error(status_code, phrase=None):
    return HttpError(status_code, phrase=phrase)


def render_template():
    pass