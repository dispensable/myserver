# -*- ciding:utf-8 -*-

import logging
import threading
import sys
import os
import fcntl
import datetime


def get_level(level_name: str):
    level_name = level_name.lower()
    if level_name == "critical":
        return logging.CRITICAL
    elif level_name == "error":
        return logging.ERROR
    elif level_name == "warning":
        return logging.WARNING
    elif level_name == "info":
        return logging.INFO
    elif level_name == "debug":
        return logging.DEBUG
    else:
        return None


class Logger(object):

    error_fmt = r"%(asctime)s [%(process)d] [%(levelname)s] %(message)s"
    datefmt = r"[%Y-%m-%d %H:%M:%S %z]"

    access_fmt = "%(message)s"
    syslog_fmt = "[%(process)d %(message)s]"

    def __init__(self, cfg):
        self.error_logger = logging.getLogger("myserver.error")
        self.error_logger.propagate = False
        self.access_logger = logging.getLogger("myserver.access")
        self.access_logger.propagate = False
        self.error_handler = []
        self.access_handler = []
        self.cfg = cfg
        self.log_file = None
        self.lock = threading.Lock()
        self.log_level = get_level(cfg.get('log_level')) or logging.INFO
        self.error_logger.setLevel(self.log_level)
        self.access_logger.setLevel(logging.INFO)
        self.setup(cfg)

    def setup(self, cfg):
        if cfg.get('capture_output') and cfg.get('log_file') != "-":
            for stream in sys.stdout, sys.stderr:
                stream.flush()

            self.log_file = open(cfg.get('log_file'), 'a+')
            os.dup2(self.log_file.fileno(), sys.stdout.fileno())
            os.dup2(self.log_file.fileno(), sys.stderr.fileno())
        self._set_handler(self.error_logger, cfg.get('log_file'),
                          logging.Formatter(self.error_fmt, self.datefmt))

        if self.access_logger is not None:
            self._set_handler(self.access_logger, cfg.get('access_logfile'),
                              logging.Formatter(self.access_fmt), sys.stdout)

    @staticmethod
    def _get_myserver_handler(logger):
        for handler in logger.handlers:
            if getattr(handler, "_myserver", False):
                return handler

    def _set_handler(self, log, output, fmt, stream=None):
        h = self._get_myserver_handler(log)
        if h:
            log.handlers.remove(h)

        if output is not None:
            if output == '-':
                h = logging.StreamHandler(stream)
            else:
                h = logging.FileHandler(output)
                try:
                    os.chown(h.baseFilename, self.cfg.get('usr'), self.cfg.get('group'))
                except OSError:
                    pass
            h.setFormatter(fmt)
            h._myserver = True
            log.addHandler(h)

    def critical(self, msg, *args, **kwargs):
        self.error_logger.critical(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.error_logger.error(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.error_logger.warning(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.error_logger.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.error_logger.debug(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self.error_logger.exception(msg, *args, **kwargs)

    def log(self, lvl, msg, *args, **kwargs):
        if isinstance(lvl, str):
            lvl = get_level(lvl)
        self.error_logger.log(lvl, msg, *args, **kwargs)

    def reopen_logfile(self):
        if self.cfg.get('capture_output') and self.cfg.get('log_file') != '-':
            sys.stdout.flush()
            sys.stderr.flush()

            with self.lock():
                if self.log_file is not None:
                    self.log_file.close()
                self.log_file = open(self.cfg.get('log_file'), 'a+')
                os.dup2(self.log_file.fileno(), sys.stdout.fileno())
                os.dup2(self.log_file.fileno(), sys.stderr.fileno())

        for logger in logging.root.manager.loggerDict:
            for handler in logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    handler.acquire()
                    try:
                        if handler.stream:
                            handler.stream.close()
                            handler.stream = open(handler.baseFilename, handler.mode)
                    finally:
                        handler.release()

    def close_on_exec(self):
        for logger in logging.root.manager.loggerDict.values():

            if isinstance(logger, logging.PlaceHolder):
                continue
            for handler in logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    handler.acquire()
                    try:
                        if handler.stream:
                            flags = fcntl.fcntl(handler.stream, fcntl.F_GETFD)
                            flags |= fcntl.FD_CLOEXEC
                            fcntl.fcntl(handler.stream, fcntl.F_SETFD, flags)
                    finally:
                        handler.release()

    def access(self, resp, req, environ, request_time):
        log_format = {
            "remotehost": environ.get('REMOTE_ADDR', '-'),
            "username": req.header.get('username', '-'),
            "auth-username": req.header.get('auth-username', '-'),
            "timestamp": req.header.get('date', datetime.datetime.now()),
            "request-line": ' '.join([req.method, req.path,
                                      'HTTP/{}.{}'.format(req.version[0], req.version[1])]),
            "response-code": str(resp.status_code),
            "response-size": str(resp.sent_bytes),
            "response-time": str(request_time)
        }
        self.access_logger.info("%(remotehost)s %(username)s"
                                " %(auth-username)s %(timestamp)s "
                                "%(request-line)s %(response-code)s"
                                " %(response-size)s %(response-time)s", log_format)