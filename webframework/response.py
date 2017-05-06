import hashlib

from http.cookies import SimpleCookie
from .error import HeaderNotAllowed
from .utils import HTTP_CODES
from .utils import LocalVar
from .utils import sig_cookie


class Response(object):

    default_status_code = 200
    default_content_type = 'text/html; charset=UTF-8'

    # https://www.ietf.org/rfc/rfc2616.txt 10.2 etc.
    blacklist_headers = {
        204: frozenset(('Content-Type', 'Content-Length')),
        304: frozenset(('Allow', 'Content-Encoding', 'Content-Language',
                        'Content-Length', 'Content-Range', 'Content-Type',
                        'Content-Md5', 'Last-Modified'))
    }

    def __init__(self, status_code='', headers=None, body=''):
        self.status_code = status_code or Response.default_status_code
        self.status_phrase = ''
        self.headers = []

        if headers and isinstance(headers, list):
            self.headers += headers
        self.body = body

        self.add_header('Content-Type', Response.default_content_type)

    def add_header(self, header, value, unique=False):

        if not isinstance(header, str):
            raise TypeError('Header name should be string get {!s}'.format(header))
        if not isinstance(value, str):
            raise TypeError('Header value should be string get {!s}'.format(value))

        if unique:
            self.del_header(header)

        if self.status in Response.blacklist_headers:
            if header in Response.blacklist_headers[self.status]:
                raise HeaderNotAllowed(header, self.status)

        self.headers.append((header, value))

    def del_header(self, header):
        header = header.lower()
        header_copy = self.headers.copy()
        for value in header_copy:
            if value[0].lower() == header:
                self.headers.remove(value)

    def get_header(self, header):
        """ get header return (header, value) tuple"""
        header = header.lower()
        for h in self.headers:
            if h[0].lower() == header:
                return h

    def add_body(self, body):
        self.body = body

    @property
    def charset(self):
        _, content_type = self.get_header('content-type')
        _, charset = content_type.split('charset=')
        return charset

    @charset.setter
    def charset(self, encoding):
        if not isinstance(encoding, str):
            raise TypeError('encoding should be str get {!s]'.format(encoding))
        h_and_v = self.get_header('content-type')
        if h_and_v:
            h, v = h_and_v
            rest, _ = v.split('charset=')
            new_h, new_v = 'Content-Type', rest + 'charset=' + encoding
            self.del_header(h)
            self.add_header(new_h, new_v)

    @property
    def status_line(self):
        return ''.join([str(self.status_code), ' ', self.status_phrase])

    @property
    def status(self):
        return self.status_code

    @status.setter
    def status(self, code):
        if isinstance(code, int):
            code, phrase = code, HTTP_CODES.get(code) or 'Unknown'
        elif ' ' in code:
            code, phrase = int(code.split()[0]), code.split()[1]
        else:
            raise ValueError('status should be "code status", not {!s}'.format(code))

        if code < 100 or code > 999:
            raise ValueError('status code {!s} our of range'.format(code))

        self.status_code = code
        self.status_phrase = phrase

    def set_cookie(self, name, value, expires=None, path=None, comment=None,
                   domain=None, max_age=None, secure=None, version=None,
                   httponly=None, header='Set-Cookie', secret_key=None,
                   secret_level=hashlib.sha256):
        """ set cookie in the header
            :param name: cookie name (str type and can not use reserved key)
            :param value: cookie value
            :return: None
            see: https://www.ietf.org/rfc/rfc2965.txt
        """

        temp_cookie = SimpleCookie()

        # set cookie name: value
        if not isinstance(name, str):
            raise ValueError("cookie name {!s} should be str".format(name))

        if secret_key:
            if not isinstance(value, str):
                raise ValueError("cookie value should be string")

            value = sig_cookie(name, value, secret_key, secret_level)

        temp_cookie[name] = value

        #  set property for this cookie
        this_cookie = temp_cookie[name]
        if expires:
            this_cookie['expires'] = expires
        if path:
            this_cookie['path'] = path
        if comment:
            this_cookie['comment'] = comment
        if domain:
            this_cookie['domain'] = domain
        if max_age:
            this_cookie['max_age'] = max_age
        if secure:
            this_cookie['secure'] = secure
        if version:
            this_cookie['version'] = version
        if httponly:
            this_cookie['httponly'] = httponly

        # add cookie to the headers
        cookie_str = temp_cookie.output(header=header)
        header_len = len(header)
        self.add_header(cookie_str[:header_len], cookie_str[header_len:])

    def del_cookie(self, name, path=None, domain=None):
        """
        delete cookie
        :param name: same name as you set
        :param path: same path as you set
        :param domain: same domain as you set
        :return: None
        """
        self.set_cookie(name, '', expires=0, path=path, domain=domain, max_age=-1)

    def __iter__(self):
        return iter(self.body)

    def close(self):
        if hasattr(self.body, 'close'):
            self.body.close()

    @property
    def content_len(self):
        return self.get_header('Content-Length')

    @content_len.setter
    def content_len(self, value):
        if not isinstance(value, int):
            raise TypeError("Content length must be int, get {!s}".format(value))
        self.add_header('Content-Length', str(value), unique=True)

    @property
    def content_type(self):
        return self.get_header('Content-Type')

    @content_type.setter
    def content_type(self, value):
        if not isinstance(value, str):
            raise TypeError("Content type must be string, get {!s}".format(value))
        self.add_header('Content-Type', value)

    @staticmethod
    def iter_file_range(fp, offset, bytes, maxread=2 ** 20):
        fp.seek(offset)
        while bytes > 0:
            part = fp.read(min(bytes, maxread))
            if not part:
                break
            bytes -= len(part)
            yield part

class ResponseWrapper(Response):
    init = Response.__init__
    status_code = LocalVar()
    status_phrase = LocalVar()
    headers = LocalVar()
    body = LocalVar()
