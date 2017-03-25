# -*- coding: utf-8 -*-

import os
import sys
from pidfile import Pidfile
from sock import create_sockets
import utils
import signal
import select
import errno
from setproctitle import setproctitle
import time


class Watcher(object):

    LISTENERS = []
    PIPE = []

    # workers {pid: worker}
    WORKERS = {}

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

    # error
    WORKER_BOOT_ERROR_EXIT = 2
    APP_LOAD_EXIT_ERROR = 3

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

        # 为gracfully退出的定时器安装处理器
        signal.signal(signal.SIGALRM, self.handle_alrm)

    def signal(self, sig, frame):
        """ 将信号添加到队列中 """
        if len(self.SIGQUEUE) < 5:
            self.SIGQUEUE.append(sig)

    # handler for HUP QUIT INT TERM TTIN TTOU USR1 USR2 WINCH ALARM
    def handle_chld(self, sig, frame):
        self.wait_worker()

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
        self.kill_all_workers(signal.SIGUSR1)

    def handle_usr2(self):
        self.reexec()

    def handle_winch(self):
        if self.cfg.get('daemon'):
            self.log.info("Gracefully closing workers")
            self.num_of_workers = 0
            self.kill_all_workers(signal.SIGTERM)
        else:
            self.log.info("Got sigwinch but ignore, "
                          "cause this process isn't daemon")

    def handle_alrm(self, sig, frame):
        self.kill_all_workers(signal.SIGKILL)

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
        is_num_equal = len(self.WORKERS) - self.num_of_workers
        if is_num_equal == 0:
            return
        elif is_num_equal < 0:
            while len(self.WORKERS) < self.num_of_workers:
                self.spwnworker()
        elif is_num_equal > 0:
            sorted_workers = sorted(self.WORKERS.items(), key=lambda workers: workers[1].age)
            while len(self.WORKERS) < self.num_of_workers:
                oldest_worker = self.WORKERS.pop(sorted_workers[0][0])
                self.kill_worker(oldest_worker.pid, signal.SIGTERM)

        active_worker_num = len(self.WORKERS)
        if self._last_logged_active_worker_count != active_worker_num:
            self._last_logged_active_worker_count = active_worker_num
            self.log.info("%s worker(s) active", str(active_worker_num))

    def spwnworker(self):

        # 实例化worker
        self.worker_age += 1
        Worker_Class = self.cfg.get("worker_class")
        worker = Worker_Class(self.worker_age, self.pid, self.app, self.log, self.LISTENERS, self.timeout / 2)

        # worker fork hook
        self.cfg.get('before_fork_worker')()

        # fork
        childpid = os.fork()

        # watcher进程
        if childpid != 0:
            self.WORKERS[childpid] = worker
            self.num_of_workers += 1
            return childpid

        # worker进程
        if childpid == 0:
            try:
                # 设置进程名称 参考：https://pypi.python.org/pypi/setproctitle 使用该库
                setproctitle(self.cfg.get('default_proc_name') + ' worker {}'.format(childpid))

                worker.pid = os.getpid()
                self.log.info("worker running with pid %s", childpid)
                self.cfg.get('after_worker_fork')(self, worker)
                # pre fork
                worker.init()
                sys.exit(0)
            except Exception as e:
                raise e
            finally:
                self.log.info("worker %s booted", str(childpid))
                try:
                    worker.tmp.close()
                    self.cfg.get('after_worker_exit_hook')(self, worker)
                except Exception as e:
                    self.log.warning("During worker %s exit, error  %s happend.", str(childpid), str(e))

    def reload(self):
        pass

    def kill_timeout_worker(self):
        timeout = self.cfg.get('timeout')

        if timeout:
            for pid, worker in self.WORKERS.items():
                if time.time() - worker.tmp.last_update > timeout:
                    self.kill_worker(pid, signal.SIGKILL)
        return

    def run(self):
        self.start()

        # worker管理

        print('watcher is running...')

    def wait_worker(self):
        """ wait子进程，防止僵尸进程 """
        try:
            # 回收子进程
            while True:
                childid, status = os.waitpid(-1, os.WNOHANG)

                if childid <= 0:
                    break
                else:
                    # 正常终止 15-8 为退出状态 7-0为0
                    if os.WIFEXITED(status):
                        exit_code = os.WEXITSTATUS(status)
                        if exit_code == self.WORKER_BOOT_ERROR_EXIT:
                            pass
                        if exit_code == self.APP_LOAD_EXIT_ERROR:
                            pass
                    worker = self.WORKERS.pop(childid, None)
                    if not worker:
                        continue
                    worker.tmp.close()
                    self.cfg.get('after_child_exit_hook')(self, worker)
        except OSError as e:
            if e.args[0] != errno.ECHILD:
                raise

    def stop(self, gracefully=True):
        # 关闭套接字
        for listener in self.LISTENERS:
            listener.close()

        if gracefully:
            # 设置定时器 超时后将kill all worker
            signal.alarm(self.cfg.get("graceful_timeout"))
            self.kill_all_workers(signal.SIGTERM)
            signal.alarm(0)
        else:
            self.kill_all_workers(signal.SIGKILL)

    def kill_worker(self, pid, sig):
        try:
            os.kill(pid, sig)
        except OSError as e:
            # 无此进程
            if e.args[0] == errno.ESRCH:
                worker = self.WORKERS.pop(pid, None)
                if worker:
                    worker.tmp.close()
                    self.cfg.get('after_worker_exit_hook')(self, worker)
                    return
            raise

    def kill_all_workers(self, sig):
        for pid in self.WORKERS.keys():
            self.kill_worker(pid, sig)

    def reexec(self):
        pass