# -*- coding:utf-8 -*-

import time
import sys
import os

import utils
import signal

from reloader import reloaders


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

        self.last_heart_beat_time = time.time()
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

        self.load_wsgi()
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
        self.config.get('worker_abort_hook')()
        sys.exit(1)

    def load_wsgi(self):
        try:
            self.wsgi = self.app.wsgi()
        except SyntaxError as e:
            raise e

    def i_am_alive(self):
        self.last_heart_beat_time = time.time()

    def handle_req_error(self, req, client, addr, exc):
        pass

    def run(self):
        raise NotImplementedError
