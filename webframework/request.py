from .utils import LocalVar
from http.cookies import SimpleCookie


class Request(object):
    """ A WSGI environ warper so we can easily access request property"""

    def __init__(self, environ=None):
        self.environ = {} if environ is None else environ
        self.environ['myframework.request'] = self

    @property
    def path(self):
        return self.environ['PATH_INFO']

    @property
    def headers(self):
        headers = {}
        headers['content-length'] = self.environ.get('CONTENT-LENGTH', '')
        headers['content-type'] = self.environ.get('CONTENT-TYPE', '')
        for key in self.environ:
            if key.startswith('HTTP_'):
                headers[key[5:].lower()] = self.environ[key]
        return headers

    @property
    def cookies(self):
        """ 返回SIMPLECOOKIE生成的SimpleCookie实例"""
        return SimpleCookie(self.environ['HTTP_COOKIE'])

    @property
    def method(self):
        return self.environ['REQUEST_METHOD']

    @property
    def query_str(self):
        return self.environ['QUERY_STRING']

    @property
    def body(self):
        return self.environ['wsgi.input']

    @property
    def chunked(self):
        return True if self.environ.get('HTTP_TRANSFER_ENCODING', '') == 'chunked' else False

    @property
    def url(self):
        schema = self.environ['wsgi.url_scheme']
        host = self.environ.get('HTTP_HOST', '')
        path_info = self.environ['PATH_INFO']
        if not host:
            server_name = self.environ['SERVER_NAME']
            server_port = self.environ['SERVER_PORT']
            return ''.join([schema, '://', server_name, ':', server_port, path_info])
        return ''.join([schema, '://', host, path_info])

    @property
    def script_name(self):
        return self.environ['SCRIPT_NAME']

    @property
    def is_xhr(self):
        """ True if the request was triggered by a XMLHttpRequest. This only
            works with JavaScript libraries that support the `X-Requested-With`
            header (most of the popular libraries do). """
        requested_with = self.environ.get('HTTP_X_REQUESTED_WITH', '')
        return requested_with.lower() == 'xmlhttprequest'

    @property
    def is_ajax(self):
        return self.is_xhr

    @property
    def auth(self):
        auth = self.environ.get('HTTP_AUTHORIZATION', '')
        if auth:
            return auth


class RequestWrapper(Request):
    environ = LocalVar()
    init = Request.__init__
