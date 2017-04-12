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

            while crlf_count > 0:
                crlf_index = include_trailer.find(b'\r\n')
                trailer += include_trailer[:crlf_index]
                include_trailer = include_trailer[crlf_index:]
                crlf_count -= 1

            self.trailer = trailer
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


class MultipartBody(object):
    def __init__(self, buff):
        self.buf = buff

    def read(self):
        pass