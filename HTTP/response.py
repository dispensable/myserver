from version import SERVER_SOFTWARE
from email.utils import formatdate
from warnings import warn
from utils import CachedProperty
import os, io

try:
    from os import sendfile
except ImportError:
    try:
        from sendfile import sendfile
    except ImportError:
        warn('Can not find sendfile, use normal write method. '
             'Try install pysendfile package or update your python version.')
        sendfile = None

BLKSIZE = 0x3FFFFFFF


class Response(object):
    def __init__(self, request, client_sock, config):
        self.request = request
        self.client_sock = client_sock
        self.config = config
        self.status = None
        self.status_code = None
        self.headers = []
        self.has_header_sent = False
        self.sent_bytes = 0
        self.length = None
        self.upgrade = False
        self.chunked = False
        self.server_version = SERVER_SOFTWARE

        self.must_close = False

    def start_response(self, status, headers, exc_info=None):
        """ 发起响应 """
        if exc_info:
            try:
                if self.status and self.has_header_sent:
                    raise (exc_info[0], exc_info[1], exc_info[2])
            finally:
                exc_info = None

        elif self.status is not None:
            raise AssertionError("Response headers already set!")

        self.status = status

        try:
            self.status_code = self.status.split(' ')[0]
        except ValueError:
            self.status_code = None

        self.set_headers(headers)
        self.chunked = self.is_chunked()
        return self.write

    def set_headers(self, headers):
        for h, v in headers:
            self.validate_header(h)
            value = str(v).strip()
            header = h.lower().strip()
            if header == "content-length":
                self.length = int(value)
            self.headers.append((h.strip(), v))

    def validate_header(self, header):
        if not isinstance(header, str):
            raise TypeError("{0!s} is not string type.".format(header))

    def is_chunked(self):
        if self.length is not None:
            return False
        elif self.request.version <= (1, 0):
            return False
        elif self.request.method == 'HEAD':
            return False
        elif self.status_code in (304, 204):
            return False
        return True

    def force_close(self):
        self.must_close = True

    def write(self, data):
        self.send_headers()

        can_send = len(data)
        # data length limit
        if self.length is not None:
            if self.sent_bytes >= self.length:
                return
            data_len = len(data)
            can_send = min(self.length - self.sent_bytes, data_len)
            if can_send < data_len:
                data = data[:data_len]

        # chunked data
        if self.chunked and can_send == 0:
            return

        self.sent_bytes += can_send
        self.send(data)

    def get_connection(self):
        if self.upgrade:
            return 'upgrade'
        elif self.should_close():
            return 'close'
        else:
            return 'keep-alive'

    def should_close(self):
        if self.must_close or self.request.should_close():
            return True
        if self.length is not None or self.chunked:
            return False
        if self.request.method.lower() == 'head':
            return False
        if self.status_code < 200 or self.status_code in (204, 304):
            return False
        return True

    def default_header(self):
        headers = [
            'HTTP/{0!s}.{1!s} {2!s}'.format(self.request.version[0],
                                            self.request.version[1],
                                            self.status),
            'Server: {}'.format(self.server_version),
            'Date: {}'.format(formatdate()),
            'Connection: {}'.format(self.get_connection())
        ]

        if self.chunked:
            headers.append('Transfer-Encoding: chunked')

        return headers

    def send_headers(self):
        if self.has_header_sent:
            return
        all_headers = self.default_header()
        for h, v in self.headers:
            all_headers.append("{}: {}".format(h, v))

        header_msg = "\r\n".join(all_headers) + '\r\n\r\n'
        print(header_msg)
        self.send(header_msg)
        self.has_header_sent = True

    def send(self, data):
        if not isinstance(data, bytes):
            data = data.encode()
        if self.chunked:
            # add chunked size
            chunked_size = "{!s}\r\n".format(hex(len(data)))
            chunk = b"".join([chunked_size.encode('utf-8'), data, b"\r\n"])
            self.client_sock.sendall(chunk)
        else:
            self.client_sock.sendall(data)

    def write_file(self, file_like):
        """ try to use sendfile system call to send file. else, write file normally. """
        if not self.send_file(file_like):
            for part in file_like:
                self.write(file_like)

    @CachedProperty
    def is_ssl(self):
        return self.config.get('is_ssl')

    @CachedProperty
    def can_sendfile(self):
        return self.config.get('sendfile') is True and sendfile is not None

    def send_file(self, file_like):
        """ use system sendfile to write file efficiently """
        # 能否使用相关系统调用
        if not self.can_sendfile():
            return False

        # ssl
        if self.is_ssl:
            return False

        # sendfile system call only senf file from fd to fd
        if not hasattr(file_like, 'fileno'):
            return False

        fileno = file_like.fileno()

        try:
            offset = os.lseek(fileno, 0, os.SEEK_CUR)
            if self.length is None:
                filesize = os.fstat(fileno).st_size
                if filesize == 0:
                    return False

                nbytes = filesize - offset
            else:
                nbytes = self.length
        except (OSError, io.UnsupportedOperation):
            return False

        self.send_headers()

        if self.is_chunked():
            chunk_size = "%X\r\n" % nbytes
            self.client_sock.sendall(chunk_size.encode())

        sockno = self.client_sock.fileno()
        sent = 0

        while sent != nbytes:
            count = min(nbytes - sent, BLKSIZE)
            sent += sendfile(sockno, fileno, offset + sent, count)

        if self.is_chunked():
            self.client_sock.sendall(b"\r\n")

        os.lseek(fileno, offset, os.SEEK_SET)

        return True

    def close(self):
        if not self.has_header_sent:
            self.send_headers()
        if self.chunked:
            self.write(b'')

    def __str__(self):
        return ''.join(self.headers)