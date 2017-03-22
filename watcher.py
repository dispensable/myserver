# -*- coding: utf-8 -*-

import os
import sys
from pidfile import Pidfile


class Watcher(object):

    listeners = []

    def __init__(self, app):
        self.app = app
        self._num_of_workers = None
        self._last_logged_active_worker_count = None
        self.log = None

        self.setup_app(app)

        self.pidfile = None
        self.systemd = False
        self.worker_age = 0
        self.reexec_pid = 0
        self.master_pid = 0
        self.master_name = "Master"

        # save context for reload
        cwd = os.getcwd()

        args = sys.argv[:]
        args.insert(0, sys.executable)

        self.START_CTX = {
            "args": args,
            "cwd": cwd,
            0: sys.executable
        }

    def init_sig(self):
        pass

    def setup_app(self, app):
        self.cfg = app.config

        if self.log is None:
            self.log = self.cfg.get('logger_class')(self.cfg)

        if 'MYSERVER_FD' in os.environ:
            self.log.reopen_files()

        self.worker_class = self.cfg.get('worker_class')
        self.address = self.cfg.get('address')
        self.num_of_workers = self.cfg.get('workers')
        self.timeout = self.cfg.get('timeout')
        self.proc_name = self.cfg.get('procname')

        self.log.debug("Current configuration:\n{0}".format(
            '\n'.join(('{}: {}'.format(key, value) for key, value in self.cfg.settings))))

        if self.cfg.get('env'):
            pass

        if self.cfg.get('preload_app'):
            self.app.wsgi()

    @property
    def num_of_workers(self):
        return self._num_of_workers

    @num_of_workers.setter
    def num_of_workers(self, value):
        old_value = self._num_of_workers
        self._num_of_workers = value
        self.cfg.get('nworkers_changed')(self, value, old_value)

    def setup_pidfile(self):
        self.pid = os.getpid()

        if self.cfg.get('pid'):
            filename = self.cfg.get('pid')
            if self.master_pid != 0:
                filename += '.2'
            self.pidfile = Pidfile(filename)
            self.pidfile.create(self.pid)

    def setup_sockets(self):
        pass

    def setup_log(self):
        pass

    def start(self):
        pass

    def manage_worker(self):
        pass

    def handle_sig(self):
        pass

    def reload(self):
        pass

    def run(self):
        self.start()

        # worker管理

        print('watcher is running...')