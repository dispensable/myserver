# -*- coding:utf-8 -*-

import os
import errno
import os.path
import tempfile


class Pidfile(object):
    def __init__(self, pathname):
        self.pathname = pathname
        self.pid = None

    def create(self, pid):
        # 检查原来的文件pid是否和该pid相同
        old_pid = self.validate(self.pathname)
        if old_pid:
            if old_pid == os.getpid():
                return
            raise RuntimeError('Already has a pid file: {}'.format(old_pid))

        self.pid = pid

        # 检查是否存在该文件目录
        path = os.path.dirname(self.pathname)
        if path and not os.path.isdir(path):
            raise RuntimeError("{} doesn't exists, can't create pidfile.".format(path))

        # 创建临时文件并写入pid
        fd, pathname = tempfile.mkstemp(dir=path)
        os.write(fd, "{}\n".format(pid).encode())

        # 重命名该文件
        if self.pathname:
            self.rename(pathname)
        else:
            self.pathname = pathname
        os.close(fd)

        # 设置文件权限
        os.chmod(self.pathname, 420)

    def delete(self):
        try:
            with open(self.pathname, 'r') as pidfile:
                pid = int(pidfile.read() or 0)

            if pid == self.pid:
                os.unlink(self.pathname)
        except Exception:
            pass

    def rename(self, path):
        self.delete()
        self.pathname = path
        self.create(self.pid)

    def validate(self, pathname):
        # pathname 不存在则还未创建pidfile
        if not self.pathname:
            return

        # 验证pathname内的pid
        try:
            with open(pathname, 'r') as f:
                try:
                    pid = int(f.read())
                except ValueError:
                    return

                try:
                    # 发送空信号 检查进程是否存在
                    os.kill(pid, 0)
                    return pid
                except OSError as e:
                    # 若进程不存在
                    if e.args[0] == errno.ESRCH:
                        return
                    # 进程存在，但是无权向目标进程发送信号
                    if e.args[0] == errno.EPERM:
                        return pid
                    raise
        except IOError as e:
            # 文件目录不存在
            if e.args[0] == errno.ENOENT:
                return
            raise
