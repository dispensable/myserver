# -*- coding:utf-8 -*-
from io import BytesIO
from HTTP.errors import InvalidChunkSize, NoMoreData
import sys


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
        self.trailer = None

    def read(self, size):
        if size < 0:
            raise ValueError("size must > 0")
        if size == 0:
            return b''

        # 读取全部chunk并保存到buffer
        buffer = BytesIO()
        data = self.buf.read_data()
        while data:
            buffer.write(data)
            if b'0\r\n' in buffer.getvalue():
                break
            data = self.buf.read_data()

        # 找到chunk index
        all_data_end_index = buffer.getvalue().find(b'0\r\n') + 3
        data = buffer.getvalue()
        # 验证chunk
        if not self.validate_data(data[:all_data_end_index]):
            raise InvalidChunkSize(data[:all_data_end_index])

        # 如果没有拖挂
        if self.trailer_count == 0:
            self.buf.write_data(data[all_data_end_index:])
            return data[:all_data_end_index]
        # 如果有拖挂
        if self.trailer_count > 0:
            # 继续接受拖挂
            crlf_count = self.trailer_count # 首部中标识的拖挂数
            crlf_num = data[all_data_end_index:].count(b'\r\n')  # 已读取数据中拖挂的数量

            # 仍需要读取的拖挂数量
            num = crlf_count - crlf_num
            while num > 0:
                trailer = self.buf.read_data()
                buffer.write(trailer)
                if b'\r\n' in trailer:
                    num -= trailer.count(b'\r\n')

            data = buffer.getvalue()
            include_trailer = data[all_data_end_index:]
            trailer = ''
            # 分离拖挂数据
            while crlf_count > 0:
                crlf_index = include_trailer.find(b'\r\n')
                trailer += include_trailer[:crlf_index]
                include_trailer = include_trailer[crlf_index:]
                crlf_count -= 1

            self.trailer = trailer
            # 将不属于拖挂的数据放回
            self.buf.write_data(include_trailer)

            return data[:all_data_end_index]

    def validate_data(self, data):
        data_list = data.split(b'\r\n')

        if len(data_list) % 2 != 0:
            return False

        for i in range(0, len(data_list), 2):
            chunk_size = int(data_list[i], 16)
            if len(data_list[i+1]) != chunk_size:
                return False
        return True


class Body(object):
    def __init__(self, body_type):
        self.body_type = body_type
        self.buf = BytesIO()

    def __iter__(self):
        return self

    def __next__(self):
        data = self.readline()
        if not data:
            raise StopIteration()
        return data

    def read(self, size=sys.maxsize):
        """ WSGI 1.0.1 """

        if size == b'':
            return b''

        size = self.validate_size_num(size)

        if size < self.buf.tell():
            return Body.get_size_data(self.buf, size)

        elif size > self.buf.tell():
            while self.buf.tell() < size:
                new_data = self.body_type.read(1024)
                if not new_data:
                    break
                self.buf.write(new_data)

            return Body.get_size_data(self.buf, size)
        else:
            data = self.buf.getvalue()
            self.buf = BytesIO()
            return data

    @staticmethod
    def get_size_data(buf, size):
        data = buf.getvalue()
        size_data, rest = data[:size], data[size:]
        buf = BytesIO()
        buf.write(rest)
        return size_data

    def validate_size_num(self, size):
        if size < 0:
            return sys.maxsize
        if size is not isinstance(size, int):
            raise TypeError('size must > 0')
        return size

    def readline(self, size=sys.maxsize):
        """ WSGI 1.0.1 """
        if size == 0:
            return b''

        size = self.validate_size_num(size)

        data = self.buf.getvalue()
        self.buf = BytesIO()

        while len(data) <= size or data.find(b'\n', 0, size) < size:
            index = data.find(b'\n', 0, size)
            # 缓存区一行数据已经读取完毕
            if index > 0:
                index += 1
                self.buf.write(data[index:])
                return data[:index]
            # 缓存区尚未完整读入一行数据
            new_data = self.body_type.read(min(1024, size))
            if not new_data:
                return data
            data += new_data

        # 读取到超过size的数据但仍然没有换行，返回size的数据，
        # 保存多余数据
        self.buf.write(data[size:])
        return data[:size]

    def readlines(self, size=None):
        """ WSGI 1.0.1 """
        return self.read().split(b'\n')
