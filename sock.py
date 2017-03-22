# -*- coding:utf-8 -*-

import os.path
import socket
import errno
import time
import sys


def from_addr_get_addinfo(addr):
    if ':' in addr:
        host, port = addr.split(":")
        try:
            addr_info = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        except socket.gaierror as e:
            raise
        return addr_info[0]


def create_sockets(cfg, log, fd=None):
    # TODO: UNIX LOCAL socket and systemd socket activition support

    listeners = []

    addresses = [cfg.get('bind')]

    ca_file = cfg.get('certfile')
    key_file = cfg.get('keyfile')

    if ca_file and not os.path.exists(ca_file):
        raise ValueError("CA file {} does not exists.".format(ca_file))
    if key_file and not os.path.exists(key_file):
        raise ValueError("Key file {} does not exists.".format(key_file))

    for addr in addresses:

        try:
            addr_info = from_addr_get_addinfo(addr)
        except socket.gaierror as e:
            log.error("Get addrinfo error: %d %s", e.args[0], e.args[1])

        sock = socket.socket(addr_info[0], addr_info[1], addr_info[2])
        sock.set_inheritable(True)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.setblocking(0)

        for retry in range(5):
            try:
                sock.bind(addr_info[-1])
            except socket.error as e:
                if e.args[0] == errno.EADDRINUSE:
                    log.error("Connection in use: %s", str(addr))
                if e.args[0] == errno.EADDRNOTAVAIL:
                    log.error("Invalid address: %s", str(addr))
                if retry < 4:
                    msg = "connect %s:%d error"
                    log.debug(msg, str(addr_info[-1][0]), addr_info[-1][1])
                    log.debug('will retry in 1 second')
                    time.sleep(1)
                if retry == 4:
                    sock.close()
                    log.error("cannot connected to %s:%d",
                              str(addr_info[-1][0]), addr_info[-1][1])
                    sys.exit(1)
            else:
                break

        sock.listen(cfg.get('backlog'))
        listeners.append(sock)
    return listeners
