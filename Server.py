import asyncio

from Structure import User, Hall
from Socket import Socket


class Server(Socket):

    def __init__(self):
        super(Server, self).__init__()
        print("[ Server Started ]")

        self.hall = Hall()
        self.users = []

    async def main(self):
        await self.accept_sockets()

    async def send_data(self, commands):
        send_functions = [self.main_loop.sock_sendall(user.socket, data) for (data, user) in commands]
        if not send_functions:
            return

        await asyncio.gather(
            *send_functions
        )

    async def listen_socket(self, listened_socket=None):
        if not listened_socket:
            return

        new_user = User(listened_socket)

        while True:
            data = await self.main_loop.sock_recv(listened_socket, self.MSG_BYTES)

            if not data:
                self.users.remove(listened_socket)
                cmd = self.hall.remove_user(new_user)
                await self.send_data(cmd)
                listened_socket.close()
                break

            commands = self.hall.handle_msg(new_user, data.decode())

            await self.send_data(commands)

    def set_up(self):
        self.socket.bind(
            (Socket.HOST, Socket.PORT)
        )
        self.socket.listen(5)
        self.socket.setblocking(False)

    async def accept_sockets(self):
        while True:
            user_socket, addr = await self.main_loop.sock_accept(self.socket)

            self.users.append(user_socket)
            self.main_loop.create_task(self.listen_socket(user_socket))


if __name__ == '__main__':
    server = Server()
    server.set_up()

    server.start()
