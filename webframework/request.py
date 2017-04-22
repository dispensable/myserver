from .utils import LocalVar
from http.cookies import SimpleCookie
from urllib import parse
from json import load, JSONDecodeError
from io import BytesIO
from cgi import FieldStorage
from .utils import FileUpload

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
    def cookie(self):
        """ 返回SIMPLECOOKIE生成的SimpleCookie实例"""
        return SimpleCookie(self.environ['HTTP_COOKIE'])

    @property
    def method(self):
        return self.environ['REQUEST_METHOD']

    @property
    def query_str(self):
        return self.environ['QUERY_STRING']

    @property
    def parsed_url(self):
        return parse.urlparse(self.url)

    @property
    def query(self):
        """ 返回一个query字典 形式如 {'q': ['a'],...}
            [] 用来指定多次指定相同参数的情况
        """
        return parse.parse_qs(self.query_str)

    @property
    def environ(self):
        """ 返回一个wsgi environ字典的副本 """
        return self.environ.copy()

    @property
    def json(self):
        json_header = self.environ.get('HTTP_CONTENT_TYPE', '').lower()
        if ('application/json' in json_header) or \
            ('application/json-rpc' in json_header):
            try:
                return load(self.body)
            except TypeError as e:
                # TODO: 替换为400错误
                raise e
            except JSONDecodeError as e:
                raise e
        raise AttributeError('Not json body !')

    @property
    def body(self):
        """ 返回一个 BytesIO 对象， 后续访问只seek（0）后返回"""
        body = self.environ['wsgi.input']
        # 非第一次读取
        if isinstance(body, BytesIO):
            body.seek(0)
            return body
        # 第一次读取，替换input为BoytesIO对象
        else:
            body_data = body.read()
            self.environ['wsgi.input'] = BytesIO()
            body = self.environ['wsgi.input']
            body.write(body_data)
            return body

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

    @property
    def content_type(self):
        return self.environ.get('HTTP_CONTENT_TYPE', '')

    @property
    def form(self):
        """ use cgi fieldstorage 解析 multipart body and return a FileStorage object"""
        if self.method.upper() == 'POST' and self.content_type.upper().startswith('MULTIPART/'):
            form = FieldStorage(fp=self.body, environ=self.environ, keep_blank_values=True)
            return form
        else:
            raise AttributeError("Can not parse form data. May form not exists.")

    @property
    def files(self):
        """ from forms parse FileUpload file instance and
         return a dict {filename: FileUpload instance}"""
        try:
            field_list = self.form.list()
        except AttributeError:
            raise

        files = {}
        field_list = field_list or []
        for field in field_list:
            if field.filename:
                files[field.name] = FileUpload(field.file, field.filename,
                                               field.name, field.headers)

        return files

    def get_form_value(self, value, default=None):
        """
        get form value from forms
        :param value: form name
        :param default: if form name field not exists, use this default value to avoid error
        :return: FieldStorage instance or MiniFieldStorage instance with these attrs in f:
        f.name -> field name
        f.filename -> client filesystem filename when upload it
        f.value -> string value
        f.file -> filelike object
        f.type -> content type
        f.type_options -> 在HTTP请求行的内容类型行指定的选项字典
        f.headers -> headers
        see: https://hg.python.org/cpython/file/2.7/Lib/cgi.py
        """
        try:
            return self.form.getvalue(value, default)
        except AttributeError:
            raise


class RequestWrapper(Request):
    environ = LocalVar()
    init = Request.__init__

