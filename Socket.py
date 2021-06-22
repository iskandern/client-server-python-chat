import socket
import asyncio


class Socket:
    HOST = '127.0.0.1'
    PORT = 8911
    MSG_BYTES = 1024

    def __init__(self):
        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )

        self.main_loop = asyncio.get_event_loop()

    async def main(self):
        raise NotImplementedError()

    def start(self):
        self.main_loop.run_until_complete(self.main())

    def set_up(self):
        raise NotImplementedError()

    async def send_data(self, commands):
        raise NotImplementedError()

    async def listen_socket(self, listened_socket=None):
        raise NotImplementedError()
