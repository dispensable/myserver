from .baseworker import BaseWorker
import utils
import select
import os
import errno
import ssl

from HTTP.parser import RequestParser
from HTTP import wsgi
import time
import socket
import HTTP.errors


class SyncWorker(BaseWorker):
    def run(self):
        # for sock in self.listeners:
        #     sock.setblocking(0)

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
        except HTTP.errors.NoMoreData as e:
            self.log.debug("Ignored premature client disconnection {}".format(e))
        except StopIteration as e:
            self.log.debug("Closing connection. {}".format(e))
        except ssl.SSLError as e:
            if e.args[0] == ssl.SSLEOFError:
                self.log.debug("ssl connection closed")
                client.close()
            else:
                self.log.debug("Error processing ssl request.")
                self.handle_error(request, client, addr, e)
        except EnvironmentError as e:
            if e.erron not in (errno.EPIPE, errno.ECONNRESET):
                self.log.exception("Socket error processing request.")
            else:
                if e.erron == errno.ECONNRESET:
                    self.log.debug("Ignoring connection reset.")
                else:
                    self.log.debug("Ignoring EPIPE")
        except Exception as e:
            self.handle_error(request, client, addr, e)
        finally:
            client.close()

    def handle_request(self, listener, request, client, addr):
        try:
            self.config.get('before_handle_req_hook')(self, request)
            start_time = time.time()
            # create wsgi environ
            resp, environ = wsgi.create(request, client, addr,
                                        listener.getsockname(), self.config)
            resp.force_close()
            self.request_handled += 1

            if self.request_handled >= self.max_requests:
                self.log.info("Autorestarting worker after current request.")
                self.alive = False

            # get wsgi iterator
            resp_iter = self.wsgi(environ, resp.start_response)

            try:
                if isinstance(resp_iter, environ['wsgi.file_wrapper']):
                    resp.write_file(resp_iter)
                else:
                    for data in resp_iter:
                        resp.write(data)
                resp.close()
                req_time = time.time() - start_time
                self.log.access(resp, request, environ, req_time)
            finally:
                if hasattr(resp_iter, 'close'):
                    resp_iter.close()
        except EnvironmentError as e:
            raise e
        except Exception:
            if resp and resp.has_header_sent:
                self.log.exception("Error handling request")
                try:
                    client.shutdown(socket.SHUT_RDWR)
                    client.close()
                except EnvironmentError:
                    pass
                raise StopIteration()
            raise
        finally:
            try:
                self.config.get('after_handle_req_hook')(self, request, environ, resp)
            except Exception:
                self.log.exception("Exception in after handle request hook.")
