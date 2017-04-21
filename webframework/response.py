from .utils import LocalVar


class Response(object):
    def __init__(self, status_code='', status='', headers=None, body=''):
        self.status_code = status_code
        self.status = status
        self.headers = []

        if headers and isinstance(headers, list):
            self.headers += headers

        self.body = body

    def add_header(self, header, value):
        self.headers.append((header, value))

    def add_body(self, body):
        self.body = body


class ResponseWrapper(Response):
    init = Response.__init__
    status_code = LocalVar()
    status = LocalVar()
    headers = LocalVar()
    body = LocalVar()
