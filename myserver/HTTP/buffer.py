from io import BytesIO
import os


class Buffer(object):
    def __init__(self, socket, max_chunk=8192):
        self.sock = socket
        self.buffer = BytesIO()
        self.sock_buffer = max_chunk

    def get_data(self):
        return self.sock.recv(self.sock_buffer)

    def read_data(self, size=None):
        if size is not None:
            if size < 0:
                size = None
            if size == 0:
                return b""

        self.buffer.seek(0, os.SEEK_END)

        # buffer有数据
        if size is None and self.buffer.tell():
            data = self.buffer.getvalue()
            self.buffer = BytesIO()
            return data

        # buffer无数据
        if size is None:
            data = self.get_data()
            return data

        # 按大小读取数据
        while self.buffer.tell() < size:
            data = self.get_data()

            # 如果读取完毕，返回所有数据并清空buffer
            if not len(data):
                all_data = self.buffer.getvalue()
                self.buffer = BytesIO()
                return all_data
            # 如果有数据，写入buffer
            self.buffer.write(data)

        # 返回size大小的数据
        data = self.buffer.getvalue()
        self.buffer = BytesIO()
        self.buffer.write(data[size:])
        return data[:size]

    def write_data(self, data):
        self.buffer.seek(0, os.SEEK_END)
        self.buffer.write(data)

    def tell(self):
        return self.buffer.tell()
