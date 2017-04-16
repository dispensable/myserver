from HTTP import response
from urllib.parse import urlparse
import os
from .. import SERVER_SOFTWARE
import io
import logging
import sys

WSGI_DICT = {
    'CONTENT_LENGTH': 0,
    'CONTENT_TYPE': '',
    'HTTP_ACCEPT': '',
    'HTTP_COOKIE': '',
    'HTTP_REFERER': '',
    'HTTP_USER_AGENT': '',
    'PATH_INFO': '',
    'QUERY_STRING': '',
    'REQUEST_METHOD': '',
    'SCRIPT_NAME': '',
    'SERVER_NAME': '',
    'SERVER_PORT': '',
    'SERVER_PROTOCOL': '',
    'wsgi.version': '',
    'wsgi.url_scheme': '',
    'wsgi.input': '',
    'wsgi.errors': '',
    'wsgi.multithread': '',
    'wsgi.multiprocess': '',
    'wsgi.run_once': ''
}


class WSGIErrorWrapper(io.RawIOBase):
    def __init__(self, config):
        logger = logging.getLogger("myserver.error")
        handlers = logger.handlers
        self.streams = []

        if config.get('errorlog') == 'sys.stderr':
            self.streams.append(sys.stderr)
            handlers = handlers[1:]

        for handler in handlers:
            if hasattr(handler, "stream"):
                self.streams.append(handler.stream)

    def write(self, data):
        for stream in self.streams:
            try:
                stream.write(data)
            except UnicodeError:
                stream.write(data.encode())
            stream.flush()


class FileWrapper(object):
    def __init__(self, filelike, block_size=8192):
        self.filelike = filelike
        self.block_size = block_size
        if hasattr(filelike, 'close'):
            self.close = filelike.close

    def __getitem__(self, item):
        data = self.filelike.read(self.block_size)
        if data:
            return data
        raise IndexError


def init_env(request, client_sock, listener_sock, config):

    header_dict = request.header

    # set content_length
    WSGI_DICT['CONTENT_LENGTH'] = header_dict.get('content-lenght', '')
    # set content type
    WSGI_DICT['CONTENT_TYPE'] = header_dict.get('content-type', '')
    # set http accept
    WSGI_DICT['HTTP_ACCEPT'] = header_dict.get('accept', '')
    # set http cookie
    WSGI_DICT['HTTP_COOKIE'] = header_dict.get('cookie', '')

    WSGI_DICT['HTTP_REFERER'] = header_dict.get('referer', '')
    WSGI_DICT['HTTP_USER_AGENT'] = header_dict.get('user-agent', '')

    # request line
    parser_result = urlparse(request.path)
    WSGI_DICT['PATH_INFO'] = request.path

    # 查询字符串
    WSGI_DICT['QUERY_STRING'] = parser_result.query

    WSGI_DICT['REQUEST_METHOD'] = request.method
    WSGI_DICT['SCRIPT_NAME'] = os.environ.get('SCRIPT_NAME', '')
    WSGI_DICT['SERVER_NAME'] = listener_sock[0]
    WSGI_DICT['SERVER_PORT'] = listener_sock[1]
    WSGI_DICT['SERVER_PROTOCOL'] = "HTTP/{}.{}".format(request.version[0],
                                                       request.version[1])
    WSGI_DICT['wsgi.version'] = (1, 0)
    WSGI_DICT['wsgi.url_scheme'] = 'https' if config.get('ssl') else 'http'
    WSGI_DICT['wsgi.input'] = request.body
    WSGI_DICT['wsgi.errors'] = WSGIErrorWrapper
    WSGI_DICT['wsgi.multithread'] = False
    WSGI_DICT['wsgi.multiprocess'] = config.get('workers') > 1
    WSGI_DICT['wsgi.run_once'] = False
    WSGI_DICT['wsgi.file_wrapper'] = FileWrapper
    WSGI_DICT['SERVER_SOFTWARE'] = SERVER_SOFTWARE
    WSGI_DICT['myserver.sock'] = client_sock
    WSGI_DICT['RAW_URI'] = request.path

    # TODO: proxy

    expect = header_dict.get('expect', None)
    if expect == "100-continue":
        client_sock.send(b'HTTP/1.1 100 Continue\r\n\r\n')

    return WSGI_DICT


def create(request, client, addr, listener_sock, config):
    environ = init_env(request, client, listener_sock, config)
    resp = response.Response(request, client, config)

    return resp, environ
