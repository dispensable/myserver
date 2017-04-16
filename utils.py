# -*- coding:utf-8 -*-

import fcntl
import os


def set_fd_nonblocking(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK
    fcntl.fcntl(fd, fcntl.F_SETFL, flags)


def set_fd_close_on_exec(fd):
    fcntl.fcntl(fd, fcntl.F_SETFD, 1)