# -*- coding:utf-8 -*-
import re
from .error import RouteNotFoundException

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
            if route.method != method:
                continue
            is_match = re.match(route.path, env_path)
            if is_match:
                return route, is_match.groupdict()
        raise RouteNotFoundException(env_path, method)


class Route(object):
    def __init__(self, path, method, callback, name, apply, skip, func, config):
        self.path = path
        self.method = method
        self.callback = callback
        self.name = name
        self.apply = apply
        self.skip = skip
        self.func = func
        self.config = config

    @property
    def call(self):
        return self.func
