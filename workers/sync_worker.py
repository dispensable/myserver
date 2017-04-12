from .baseworker import BaseWorker
import utils
import select
import os
import errno
import ssl

from HTTP.parser import RequestParser
from HTTP.wsgi import wsgi
import time


class SyncWorker(BaseWorker):
    def run(self):
        for sock in self.listeners:
            sock.setblocking(0)

        timeout = self.timeout or 0.5
        self.handle_data(timeout)

    def handle_data(self, timeout):
        while self.alive:
            self.i_am_alive()

            try:
                ready = self.wait(timeout)
            except StopIteration:
                return

            if ready is not None:
                for listener in ready:
                    if listener == self.pipe[0]:
                        continue
                    try:
                        self.accept(listener)
                    except EnvironmentError as e:
                        if e.erron not in (errno.EAGAIN, errno.ECONNABORTED,
                                           errno.EWOULDBLOCK):
                            raise
            if not self.is_parent_alive():
                return

    def is_parent_alive(self):
        if self.ppid != os.getppid():
            self.log.info("parent process changed, shutting down ...")
            return False
        return True

    def accept(self, listener):
        client, addr = listener.accept()
        client.setblocking(1)
        utils.set_fd_close_on_exec(client)
        self.handle(listener, client, addr)

    def wait(self, timeout):
        try:
            self.i_am_alive()
            ready = select.select(self.watch_fds, [], [], timeout)
            if ready[0]:
                if self.pipe[0] in ready[0]:
                    os.read(self.pipe[0], 1)
                return ready[0]
        except select.error as e:
            if e.args[0] == errno.EINTR:
                return self.listeners
            if e.args[0] == errno.EBADF:
                if self.request_handled < 0:
                    return self.listeners
                else:
                    raise StopIteration
            raise

    def handle(self, listener, client, addr):
        try:
            if self.config.get('is_ssl'):
                client = ssl.wrap_socket(client, server_side=True,
                                              certfile=self.config.get('certfile'))
            # parse request
            parser = RequestParser(self.config, client)
            request = next(parser)

            # handle request
            self.handle_request(listener, request, client, addr)
        except Exception as e:
            raise e

    def handle_request(self, listener, request, client, addr):
        try:
            start_time = time.time()

            self.config.get('before_handle_req_hook')(self, request)

            # create wsgi environ
            resp, environ = wsgi.create(request, client, addr,
                                        listener.getsockname(), self.config)

            # get wsgi iterator
            resp_iter = self.wsgi(environ, resp.start_response)

            # send response
            for data in resp_iter:
                resp.write(data)

            time_used = time.time() - start_time
            self.log.access(resp, request, environ, time_used)
        except Exception as e:
            raise e