from io import BytesIO
from HTTP.errors import InvalidRequestLine, NoMoreData, InvalidHeader
import re
from HTTP.body import LengthBody, ChunkedBody, MultipartBody


class Request(object):
    def __init__(self, config, buffer, req_count):
        self.config = config
        self.buffer = buffer
        self.req_count = req_count

        self.version = (0, 0)
        self.method = None
        self.path = None
        self.header = {}
        self.body = None
        self.trailers = []  # chunked transfer encode

    def is_keep_alive(self):
        if self.version == (1, 0):
            if "connection" in self.header:
                connection = self.header['connection'].lower()
                return True if connection == 'keep-alive' else False
            return False
        elif self.version == (1, 1):
            if "connection" in self.header:
                connection = self.header["connection"].lower()
                return False if connection == 'close' else True
            return True
        else:
            return False

    def get_data(self):
        # from socket get data
        data = self.buffer.read_data()

        # data recive end
        if not data:
            raise NoMoreData(self.buffer)
        return data

    def parse(self):
        buf = BytesIO()
        meta_data = self.get_data()
        buf.write(meta_data)

        # parse request line and delelte it
        req_line_index = self.parse_request_line(buf)
        data = buf.getvalue()
        buf = BytesIO()
        buf.write(data[req_line_index:])

        # parse headers line and delete it
        headers_index = self.parse_headers(buf)

        self.buffer.write(data[headers_index:])

        # parse body
        self.parse_body()

    def parse_request_line(self, buf):
        """
        从接收到的数据中解析出请求行
        :param meta_data: 从socket中接受到的数据
        :return: (method, path, version)
        """
        while True:
            data = buf.getvalue()
            if "\r\n" in data:
                break
            buf.write(self.get_data())

        request_line = data.decode().split("\r\n")[0]

        try:
            self.method, self.path, version = request_line.split(' ')
        except ValueError:
            # 处理http 0.9
            self.method, self.path = request_line.split(' ')
            self.version = (0, 9)
            return data.find(b'\r\n') + 2

        # HTTP/x.y
        version = version[5:]
        x, y = version.split(".")
        self.version = (int(x), int(y))

        return data.find(b'\r\n') + 2

    def parse_headers(self, buf):
        while True:
            data = buf.getvalue()
            if "\r\n\r\n" in data:
                break
            buf.write(self.get_data())

        meta_header_index = data.find(b'\r\n\r\n')

        if meta_header_index == 0:
            self.header = None
            return meta_header_index + 4

        meta_header = data[:meta_header_index].decode()

        # 处理首部延续行
        meta_header = re.sub(r'\r\n[ \t]+', ' ', meta_header)
        meta_header_list = meta_header.split('\r\n')

        for header in meta_header_list:
            # 处理可选空格
            if ": " in header: splitor = ": "
            elif ":" in header: splitor = ":"
            else: raise InvalidHeader(header)

            h, v = header.split(splitor)
            self.header[h.lower()] = v

        return meta_header_index + 4

    def parse_body(self):
        if "transfer-encoding" in self.header:
            if "trailer" not in self.header:
                trailer_count = 0
            else:
                trailer_count = len(self.header['trailer'].split(','))
            self.body = ChunkedBody(self.buffer, trailer_count)
        elif "content-length" in self.header:
            self.body = LengthBody(self.buffer, int(self.header["content-lenght"]))
        elif "content-type" in self.header and \
            "multipart/byteranges" in self.header["content-type"].lower():
            self.body = MultipartBody(self.buffer)



