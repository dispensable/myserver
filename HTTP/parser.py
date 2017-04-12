from HTTP.request import Request
from HTTP.buffer import Buffer


class RequestParser(object):
    def __init__(self, config, client):
        self.config = config
        self.buffer = Buffer(client)
        self.request = None
        self.request_count = 0

    def __iter__(self):
        return self

    def __next__(self):
        # 非keep_alive连接
        if self.request and not self.request.is_keep_alive():
            raise StopIteration()
        # 复用连接下读取前一个请求的所有未读取数据
        if self.request:
            data = self.request.body.read(8192)
            while data:
                data = self.request.body.read(8192)

        # 构造请求
        self.request_count += 1
        self.request = Request(self.config, self.buffer, self.request_count)

        # 若请求为空
        if not self.request:
            raise StopIteration()

        return self.request