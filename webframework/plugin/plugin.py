# -*- coding:utf-8 -*-

from abc import ABCMeta, abstractmethod


class Plugin(metaclass=ABCMeta):
    """ A abstract class for plugin dev. """
    def __init__(self, name, api_version):
        self.name = name
        self.api = api_version

    @abstractmethod
    def setup(self, app):
        """ called when install plugin to the app
            :param app: Myframwork instance
         """
        raise NotImplementedError

    @abstractmethod
    def __call__(self, callback):
        """ Been called to apply directly to each route callback. """
        raise NotImplementedError

    @abstractmethod
    def apply(self, callback, route):
        raise NotImplementedError

    @abstractmethod
    def close(self):
        """ been called when uninstall this plugin """
        raise NotImplementedError

