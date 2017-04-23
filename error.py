from .utils import _HTTP_STATUS_LINES


class MyFramworkException(Exception):
    pass


class RouteNotFoundException(MyFramworkException):
    def __init__(self, path, method):
        self.path = path
        self.method = method

    def __str__(self):
        return "{} {} didn't match any route.".format(self.method, self.path)


class HeaderNotAllowed(MyFramworkException):
    def __init__(self, header, code):
        self.header = header
        self.code = code

    def __str__(self):
        return "{!s} not allwoed in {!s} status code".format(self.header, self.code)


class RouteException(MyFramworkException):
    pass


class UnknownFilterException(RouteException):
    def __init__(self, filter_name):
        self.filter = filter_name

    def __str__(self):
        return 'Unknown filter {}, try to add it?'.format(self.filter)


class CookieAuthError(MyFramworkException):
    def __init__(self, cookie):
        self.cookie = cookie

    def __str__(self):
        return "Cookie {} not authenticated! ".format(self.cookie)


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
