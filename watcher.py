# -*- coding: utf-8 -*-

import os
import sys
from pidfile import Pidfile
from sock import create_sockets
import utils
import signal
import select
import errno


class Watcher(object):

    LISTENERS = []
    PIPE = []

    # signal HUP QUIT INT TERM TTIN TTOU USR1 USR2 WINCH
    # 需要排队的信号
    SIGLIST = [signal.SIGHUP,
               signal.SIGINT,
               signal.SIGQUIT,
               signal.SIGTERM,
               signal.SIGTTIN,
               signal.SIGTTOU,
               signal.SIGUSR1,
               signal.SIGUSR2,
               signal.SIGWINCH]
    SIGQUEUE = []

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
        """ create a self pipe to avoid select/sig conflicts"""
        for pipe in self.PIPE:
            os.close(pipe)

        # create a pipe and set them unblocking to avoid sig comes too fast
        self.PIPE = fd_pair = os.pipe()
        for fd in fd_pair:
            utils.set_fd_nonblocking(fd)
            utils.set_fd_close_on_exec(fd)
        # 信号到来时首先在管道写入一个'\0'然后使用该信号
        signal.set_wakeup_fd(self.PIPE[1])

        # 为排队信号安装信号处理器
        for sig in self.SIGLIST:
            signal.signal(sig, self.signal)

        # 为子进程退出信号安装处理器
        signal.signal(signal.SIGCHLD, self.handle_chld)

    def signal(self, sig, frame):
        """ 将信号添加到队列中 """
        if len(self.SIGQUEUE) < 5:
            self.SIGQUEUE.append(sig)

    # handler for HUP QUIT INT TERM TTIN TTOU USR1 USR2 WINCH
    def handle_chld(self, sig, frame):
        self.reap_worker()

    def handle_hup(self):
        self.log.info("Hang up: %s ", str(self.master_name))
        self.reload()

    def handle_quit(self):
        self.stop()
        raise StopIteration

    def handle_int(self):
        self.stop()
        raise StopIteration

    def handle_term(self):
        raise StopIteration

    def handle_ttin(self):
        self.num_of_workers += 1
        self.manage_worker()

    def handle_ttou(self):
        if self.num_of_workers <= 1:
            return
        self.num_of_workers -= 1
        self.manage_worker()

    def handle_usr1(self):
        self.log.reopen_files()
        self.kill_worker(signal.SIGUSR1)

    def handle_usr2(self):
        self.reexec()

    def handle_winch(self):
        if self.cfg.get('daemon'):
            self.log.info("Gracefully closing workers")
            self.num_of_workers = 0
            self.kill_workers(signal.SIGTERM)
        else:
            self.log.info("Got sigwinch but ignore, "
                          "cause this process isn't daemon")

    def sleep(self):
        """ use select to check if there is a signal comes """
        while True:
            try:
                has_sig = select.select([self.PIPE[0]], [], [], 1.0)
                # 检查是否包含pipe 读端
                if not has_sig[0]:
                    return
                # readable
                while True:
                    os.read(self.PIPE[0], 1)
            except select.error as e:
                # 处理被信号打断的系统调用和超时重试错误
                if e.args[0] not in (errno.EINTR, errno.EAGAIN):
                    raise
            except IOError as e:
                # 处理pipe读取错误
                if e.args[0] not in (errno.EINTR, errno.EAGAIN):
                    raise
            except KeyboardInterrupt:
                sys.exit()

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
        if not self.LISTENERS:
            self.LISTENERS = create_sockets(self.cfg, self.log)

    def setup_log(self):
        pass

    def start(self):
        pass

    def manage_worker(self):
        pass

    def reload(self):
        pass

    def run(self):
        self.start()

        # worker管理

        print('watcher is running...')

    def reap_worker(self):
        pass

    def stop(self):
        pass

    def kill_worker(self, sig):
        pass

    def kill_workers(self, sig):
        pass

    def reexec(self):
        pass