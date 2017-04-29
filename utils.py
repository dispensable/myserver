# -*- coding:utf-8 -*-

import fcntl
import os
import time
import textwrap


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


def write_error(sock, status_int, reason, mesg):
    html = textwrap.dedent("""\
    <html>
      <head>
        <title>%(reason)s</title>
      </head>
      <body>
        <h1><p>%(reason)s</p></h1>
        %(mesg)s
      </body>
    </html>
    """) % {"reason": reason, "mesg": cgi.escape(mesg)}

    http = textwrap.dedent("""\
    HTTP/1.1 %s %s\r
    Connection: close\r
    Content-Type: text/html\r
    Content-Length: %d\r
    \r
    %s""") % (str(status_int), reason, len(html), html)
    write_nonblock(sock, http.encode('latin1'))


def write_nonblock(sock, data, chunked=False):
    timeout = sock.gettimeout()
    if timeout != 0.0:
        try:
            sock.setblocking(0)
            return write(sock, data, chunked)
        finally:
            sock.setblocking(1)
    else:
        return write(sock, data, chunked)


def write(sock, data, chunked=False):
    if chunked:
        return write_chunk(sock, data)
    sock.sendall(data)


def write_chunk(sock, data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    chunk_size = "%X\r\n" % len(data)
    chunk = b"".join([chunk_size.encode('utf-8'), data, b"\r\n"])
    sock.sendall(chunk)
