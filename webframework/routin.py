# -*- coding:utf-8 -*-
import re
from .error import RouteNotFoundException
from .error import UnknownFilterException
from .utils import FilterDict


PATTERN = re.compile(r'<(.*?)>')


class Router(object):
    def __init__(self):
        self.routes = []

    def add_route(self, route):
        if not isinstance(route, Route):
            raise TypeError('{} must be a Route instance'.format(route))
        self.routes.append(route)
        self.routes.sort(key=lambda route: route.path)
        self.routes.reverse()

    def url_for(self, router):
        return router.path

    def match(self, environ):
        env_path = environ.get('PATH_INFO', '/')
        method = environ.get('REQUEST_METHOD', 'GET')
        # 匹配出router
        for route in self.routes:
            # 匹配方法
            if route.method != method:
                continue

            # 静态路由匹配
            if route.is_static:
                if route.path == env_path:
                    return route, {}
                continue

            print(route.path, env_path)
            # 动态路由匹配
            is_match = re.match(route.path, env_path)
            if is_match:
                return route, is_match.groupdict()
        raise RouteNotFoundException(env_path, method)

    def add_filter(self, filter_clas):
        """ Add a new filter to the route class.
            name: filter name (str)
            re: filter discard (use re)
        """
        if not isinstance(filter_clas, RouteFilter):
            raise TypeError('Filter must be a filter class.')
        Route.filter_pattern[filter_clas.name] = filter_clas.re


class Route(object):

    filter_pattern = FilterDict()

    def __init__(self, path, method, callback, name, apply, skip, func, config):
        self.path = path
        self.method = method
        self.callback = callback
        self.name = name
        self.apply = apply
        self.skip = skip
        self.func = func
        self.config = config
        self.trans_to_re()

    @property
    def call(self):
        return self.func

    @property
    def is_static(self):
        return '<' not in self.path

    @property
    def is_with_filter(self):
        return '<' in self.path and ':' in self.path

    @property
    def filter(self):
        """ 返回filter 和 其re 模式"""
        # 静态路由
        if self.is_static:
            return 'static', self.filter_pattern['static']
        # 动态无过滤器
        if not self.is_static and not self.is_with_filter:
            return 'regular', self.filter_pattern['regular']
        # 动态有过滤器
        if self.is_with_filter:
            _, f, *rest = self.path.split(':')
            # int, float, path 过滤器
            if f.endswith('>'):
                f = f[:-1]

            # re filter
            if rest[0].endswith('>'):
                rest = rest[0][:-1]
            else:  # re error
                rest = None

            return f.lstrip(), r'(?P<{name}>%s)' % rest if f == 're' else self.filter_pattern[f]

    def trans_to_re(self):
        """ transfer all filter into a re filter """
        # 静态路由不转换
        if self.is_static:
            return
        # dynamic route replace
        self.path = self._replace_filter(self.path,
                                         self.filter,
                                         re.findall(r'<([^/]+)>', self.path))

    def _replace_filter(self, path, filter_and_re, old_name_list):
        new_pattern = filter_and_re[1]
        if new_pattern is None:
            raise UnknownFilterException(filter_and_re[0])
        all_patterns = [new_pattern.format(name=name) for name in old_name_list]
        for index, name in enumerate(old_name_list):
            pattern = r'<{}>'.format(name)
            path = re.sub(pattern, all_patterns[index], path)
        return path


class RouteFilter(object):
    def __init__(self, name, re):
        self.name = name
        self.re = re

    def __str__(self):
        return "{}:{}".format(self.name, self.re)

    def __repr__(self):
        return r'(?P<{name}:var_name>{re})'.format(name=self.name, re=self.re)
