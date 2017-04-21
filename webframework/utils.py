# -*- coding:utf-8 -*-

from threading import local


class LocalVar(object):
    def __init__(self):
        self.local_var = local()

    def __get__(self, instance, owner):
        try:
            return self.local_var.var
        except ValueError:
            raise ValueError('context not initialized')

    def __set__(self, instance, value):
        self.local_var.var = value

    def __delete__(self, instance):
        del self.local_var.var
