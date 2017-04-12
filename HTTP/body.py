# -*- coding:utf-8 -*-
from io import BytesIO
from HTTP.errors import InvalidChunkSize, NoMoreData


class LengthBody(object):
    def __init__(self, buf, length):
        self.buf = buf
        self.length = length

    def read(self, size):
        if size < 0:
            raise ValueError("Size must > 0")
        if size == 0:
            return b''

        buffer = BytesIO()
        data = self.buf.read_data()
        while data:
            buffer.write(data)
            if buffer.tell() >= size:
                break
            data = self.buf.read_data()

        all_data = buffer.getvalue()

        result, rest = all_data[:size], all_data[size:]
        self.buf.write_data(rest)
        self.length -= size

        return result


class ChunkedBody(object):
    def __init__(self, buf, trailer_count):
        self.buf = buf
        self.buffer = BytesIO()
        self.trailer_count = trailer_count

    def read(self, size):
        if size < 0:
            raise ValueError("size must > 0")
        if size == 0:
            return b''

        buffer = BytesIO()
        data = self.buf.read_data()
        while data:
            buffer.write(data)
            if b'0\r\n' in buffer.getvalue():
                break
            data = self.buf.read_data()

        all_data_end_index = buffer.getvalue().find(b'0\r\n') + 3

        if not self.validate_data(data[:all_data_end_index]):
            raise InvalidChunkSize(data[:all_data_end_index])

        if self.trailer_count == 0:
            self.buf.write_data(data[all_data_end_index:])
            return data[:all_data_end_index]

        if self.trailer_count > 0:
            # 继续接受拖挂
            crlf_count = self.trailer_count
            if b'\r\n' in data[:all_data_end_index]:
            while crlf_count > 0:
                trailer = self.buf.read_data()


    def validate_data(self, data):
        data_list = data.split(b'\r\n')



class MultipartBody(object):
    def __init__(self, buff):
        self.buf = buff

    def read(self):
        pass