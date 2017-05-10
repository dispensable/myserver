# -*- coding: utf-8 -*-


class HaltServer(BaseException):
    def __init__(self, reason, exit_status=1):
        self.reason = reason
        self.exit_status = exit_status

    def __str__(self):
        return "<HaltServer %r %d>" % (self.reason, self.exit_status)


class ConfigError(Exception):
    """ Exception raised on config error """


class AppImportError(Exception):
    """ Exception raised when loading an application """


class StopWaiting(Exception):
    """ Exception raised to stop waiting for a connection"""
