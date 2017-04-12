class NoMoreData(IOError):
    def __init__(self, buf=None):
        self.buf = buf

    def __str__(self):
        return "No more data after: %r " % self.buf


class ParseException(Exception):
    pass


class InvalidRequestLine(ParseException):
    def __init__(self, req):
        self.req = req
        self.status_code = 400

    def __str__(self):
        return " Invalid HTTP request line: %r " % self.req


class InvalidHeader(ParseException):
    def __init__(self, hdr, req=None):
        self.hdr = hdr
        self.req = req

    def __str__(self):
        return "Invalid HTTP Header: %r" % self.hdr


class InvalidChunkSize(IOError):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return "Invalid chunk size: %r" % self.data