# -*- coding:utf-8 -*-

import mmap
import os
import signal
import sys
import time
from ssl import SSLError

import utils
from utils import set_now_mmap, write_error

from myserver.HTTP.response import Response
from myserver.HTTP.wsgi import default_environ
from myserver.reloader import reloaders
from myserver.HTTP.errors import *


class BaseWorker(object):

    SIGNALS = [
        signal.SIGABRT,
        signal.SIGHUP,
        signal.SIGQUIT,
        signal.SIGINT,
        signal.SIGTERM,
        signal.SIGUSR1,
        signal.SIGUSR2,
        signal.SIGWINCH,
        signal.SIGCHLD
    ]

    def __init__(self, age, pid, app, log, listeners, timeout, config):
        self.age = age
        self.ppid = pid
        self.app = app
        self.log = log
        self.listeners = listeners
        self.timeout = timeout
        self.config = config
        self.reloader = None
        self.max_requests = config.get('max_requests') or sys.maxsize

        self.heart_beat_mmap = mmap.mmap(-1, 20)
        set_now_mmap(self.heart_beat_mmap)
        self.alive = True
        self.booted = False
        self.aborted = False
        self.request_handled = 0

        self.watch_fds = []
        self.pipe = os.pipe()

    def init(self):
        # init pipe
        for fd in self.pipe:
            utils.set_fd_nonblocking(fd)
            utils.set_fd_close_on_exec(fd)

        signal.set_wakeup_fd(self.pipe[1])

        # init socket
        for sock in self.listeners:
            utils.set_fd_close_on_exec(sock)

        self.log.close_on_exec()

        self.watch_fds = self.listeners + [self.pipe[0]]

        self.init_sig()

        self.load_wsgi()

        # set reloader
        reloader = self.config.get('reload_engine')
        if reloader in reloaders:

            def on_change(fname):
                self.log.info("worker reloading: %s modified", fname)
                self.alive = False
                self.config.get('before_worker_init')()
                time.sleep(0.1)
                sys.exit(0)

            self.reloader = reloaders[reloader](callback=on_change)
            self.reloader.start()

        self.config.get('after_worker_init')(self)

        self.booted = True
        self.run()

    def init_sig(self):
        # reset default signal handle
        for sig in self.SIGNALS:
            signal.signal(sig, signal.SIG_DFL)

        # set signal handler
        signal.signal(signal.SIGQUIT, self.handle_quit)
        signal.signal(signal.SIGTERM, self.handle_exit)
        signal.signal(signal.SIGINT, self.handle_quit)
        signal.signal(signal.SIGUSR1, self.handle_usr1)
        signal.signal(signal.SIGABRT, self.handle_abort)

        signal.siginterrupt(signal.SIGTERM, False)
        signal.siginterrupt(signal.SIGUSR1, False)

    def handle_usr1(self, sig, frame):
        self.log.reopen_files()

    def handle_exit(self, sig, frame):
        self.alive = False

    def handle_quit(self, sig, frame):
        self.alive = False
        self.config.get('after_worker_quit')(self)
        time.sleep(0.1)
        sys.exit(0)

    def handle_abort(self, sig, frame):
        self.alive = False
        self.config.get('worker_abort_hook')(self)
        sys.exit(1)

    def load_wsgi(self):
        try:
            self.wsgi = self.app.wsgi()
        except SyntaxError as e:
            raise e

    def i_am_alive(self):
        set_now_mmap(self.heart_beat_mmap)

    def handle_error(self, req, client, addr, exc):
        request_start = time.time()
        addr = addr or ('', -1)

        if isinstance(exc, (InvalidRequestLine, InvalidRequestMethod,
                            InvalidHTTPVersion, InvalidHeader, InvalidHeaderName,
                            LimitRequestLine, LimitRequestHeaders,
                            InvalidProxyLine, ForbiddenProxyRequest,
                            SSLError)):
            status_int = 400
            reason = "Bad Request"

            if isinstance(exc, InvalidRequestLine):
                msg = "Invalid request line: {!s}".format(exc)
            elif isinstance(exc, InvalidRequestMethod):
                msg = "Invalid method: {!s}".format(exc)
            elif isinstance(exc, InvalidHTTPVersion):
                msg = "Invalid http version: {!s}".format(exc)
            elif isinstance(exc, (InvalidHeaderName, InvalidHeader,)):
                msg = str(exc)
                if not req and hasattr(exc, "req"):
                    req = exc.req
            elif isinstance(exc, LimitRequestLine):
                msg = str(exc)
            elif isinstance(exc, LimitRequestHeaders):
                msg = "Error parsing headers: {!s}".format(exc)
            elif isinstance(exc, SSLError):
                reason = "Forbidden"
                msg = str(exc)
                status_int = 403

            msg = "Invalid request from ip={ip}: {error}"
            self.log.debug(msg.format(ip=addr[0], error=str(exc)))
        else:
            if hasattr(req, 'uri'):
                self.log.exception("Error hanling request {!s}".format(req.uri))
            status_int = 500
            reason = "Internal Server Error"
            msg = ""

        if req is not None:
            request_time = time.time() - request_start
            environ = default_environ(req, client, self.config)
            environ['REMOTE_ADDR'] = addr[0]
            environ['REMOTE_PORT'] = str(addr[1])
            resp = Response(req, client, self.config)
            resp.status = "{} {}".format(status_int, reason)
            resp.length = len(msg)
            self.log.access(resp, req, environ, request_time)

        try:
            write_error(client, status_int, reason, msg)
        except Exception:
            self.log.debug("Failed to send error message.")

    def run(self):
        raise NotImplementedError
