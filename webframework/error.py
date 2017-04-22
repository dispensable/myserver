from .utils import _HTTP_STATUS_LINES


class MyFramworkException(Exception):
    pass


class HeaderNotAllowed(MyFramworkException):
    def __init__(self, header, code):
        self.header = header
        self.code = code

    def __str__(self):
        return "{!s} not allwoed in {!s} status code".format(self.header, self.code)


class HttpError(Exception):
    def __init__(self, status_code, phrase=None):
        self.status_code = status_code
        self.phrase = phrase or _HTTP_STATUS_LINES.get(status_code)
        self.body = """
                <h1>HTTP ERROR : {!s}</h1>
                <p>REASON: {!s}</p>
                <p>see <a href="http://127.0.0.1:8000">here for detail</a></p>
                """.format(self.status_code, self.phrase)
        self.headers = [('Content-Type', 'text/html; charset=UTF-8'),
                        ('Content-Length', str(len(self.body)))]

    def __str__(self):
        return self.body
