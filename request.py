class Request(object):
    def __init__(self, environ):
        self.environ = environ

    @property
    def header(self):
        pass

    @property
    def cookie(self):
        pass

