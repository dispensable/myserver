# -*- coding:utf-8 -*-

import fcntl
import os
import time


def set_fd_nonblocking(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK
    fcntl.fcntl(fd, fcntl.F_SETFL, flags)


def set_fd_close_on_exec(fd):
    fcntl.fcntl(fd, fcntl.F_SETFD, 1)


def set_now_mmap(m):
    b_time = str(time.time()).encode()
    m.seek(0)
    m.write(b_time)
    m.seek(0)


def get_time_mmap(m, length=11):
    m.seek(0)
    f_time = float((m.read(length)).decode())
    m.seek(0)
    return f_time
