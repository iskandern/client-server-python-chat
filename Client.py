import asyncio
import threading
import tkinter
import json

from tkinter import simpledialog
from tkinter.scrolledtext import ScrolledText
from Socket import Socket

class Client(Socket):
    def __init__(self):
        super(Client, self).__init__()
        self.nickname = ""
        self.registered = False
        self.gui_done_ev = threading.Event()
        self.gui_done = False
        self.register_win = tkinter.Tk()
        self.cached_operations = []

    async def main(self):

        await self.register()

        gui_thread = threading.Thread(target=self.gui_loop)
        gui_thread.start()

        await asyncio.gather(
            self.main_loop.create_task(self.listen_socket()),
            self.main_loop.create_task(self.send_base_query())
        )

    async def register(self):
        self.registered = False
        while not self.registered:
            input_nickname = simpledialog.askstring(
                "Nickname",
                "Please Choose a nickname",
                parent=self.register_win
            )
            data_to_server = f"<name> {input_nickname}".encode()

            await self.main_loop.sock_sendall(self.socket, data_to_server)
            data = await self.main_loop.sock_recv(self.socket, self.MSG_BYTES)
            msg = data.decode()
            print(msg)
            self.parse_data(data)

    def set_up(self):
        self.socket.connect(
            (Socket.HOST, Socket.PORT)
        )

        self.socket.setblocking(False)
        self.register_win.withdraw()

    def on_send_msg(self):
        message_data = self.msg_input_area.get('1.0', 'end')
        if len(message_data) == 0:
            return

        message = f"<message> {self.msg_input_area.get('1.0', 'end')}"
        data = message.encode()

        loop = asyncio.new_event_loop()
        if loop and loop.is_running():
            print('16 mgb memory')
        loop.run_until_complete(self.send_data(data))

        self.msg_input_area.delete('1.0', 'end')

    def on_send_room(self):
        message_data = self.msg_input_area.get('1.0', 'end')
        if len(message_data) == 0:
            return

        message = f"<join> {self.room_input_area.get('1.0', 'end')}"
        data = message.encode()

        loop = asyncio.new_event_loop()
        if loop and loop.is_running():
            print('16 mgb memory')
        loop.run_until_complete(self.send_data(data))

        self.room_input_area.delete('1.0', 'end')

    async def send_data(self, commands):
        await self.main_loop.sock_sendall(self.socket, commands)

    async def send_base_query(self):
        data_to_server = b"<list>"
        self.gui_done_ev.wait()
        self.gui_done_ev.clear()
        await self.main_loop.sock_sendall(self.socket, data_to_server)

    async def listen_socket(self, listened_socket=None):

        while True:
            data = await self.main_loop.sock_recv(self.socket, self.MSG_BYTES)
            print(data)
            if not data:
                self.stop()

            print(data.decode())
            self.parse_data(data)

    def parse_data(self, data):
        msg = data.decode()
        json_msg = json.loads(msg)

        registered = json_msg.get("registered", '')
        welcome = json_msg.get("welcome", '')
        text_message = json_msg.get("message", '')
        rooms_list = json_msg.get("list", '')

        # if not self.gui_done:
        #     self.gui_done_ev.wait()
        #     self.gui_done_ev.clear()
        #     self.gui_done = True

        if len(registered) > 0:
            self.registered = True
            self.nickname = registered

        if welcome == self.nickname and self.gui_done:
            self.clean_text_area()

        if len(text_message) > 0 and self.gui_done:
            self.add_text_area(text_message)

        if len(rooms_list) > 0 and self.gui_done:
            self.replace_rooms_area(rooms_list)

    def clean_text_area(self):
        self.text_area.config(state='normal')
        self.text_area.delete('1.0', 'end')
        self.text_area.yview('end')
        self.text_area.config(state='disabled')

    def add_text_area(self, text_message):
        self.text_area.config(state='normal')
        self.text_area.insert('end', text_message)
        self.text_area.yview('end')
        self.text_area.config(state='disabled')

    def replace_rooms_area(self, rooms_list):
        self.rooms_area.config(state='normal')
        self.rooms_area.delete('1.0', 'end')
        self.rooms_area.insert('1.0', rooms_list)
        self.rooms_area.yview('end')
        self.rooms_area.config(state='disabled')

    def stop(self):
        self.socket.close()
        self.win.destroy()
        exit(0)

    def gui_loop(self):
        self.win = tkinter.Tk()

        self.chat_label = tkinter.Label(self.win, text="Chat:", bg="lightgray")
        self.chat_label.grid(padx=20, pady=5, column=1, row=0)

        self.text_area = ScrolledText(self.win)
        self.text_area.grid(padx=20, pady=5, column=1, row=1)
        self.text_area.config(state='disabled')

        self.msg_label = tkinter.Label(self.win, text="Message:", bg="lightgray")
        self.msg_label.grid(padx=20, pady=5, column=1, row=2)

        self.msg_input_area = tkinter.Text(self.win, height=3)
        self.msg_input_area.grid(padx=20, pady=5, column=1, row=3)

        self.send_msg_button = tkinter.Button(self.win, text="Send", height=2, width=10, command=self.on_send_msg)
        self.send_msg_button.grid(padx=20, pady=5, column=1, row=4)

        self.rooms_label = tkinter.Label(self.win, text="Rooms:", bg="lightgray")
        self.rooms_label.grid(padx=20, pady=5, column=2, row=0)

        self.rooms_area = ScrolledText(self.win, width=20)
        self.rooms_area.grid(padx=20, pady=5, column=2, row=1)
        self.rooms_area.config(state='disabled')

        self.join_rooms_label = tkinter.Label(self.win, text="Join:", bg="lightgray")
        self.join_rooms_label.grid(padx=20, pady=5, column=2, row=2)

        self.room_input_area = tkinter.Text(self.win, height=3, width=20)
        self.room_input_area.grid(padx=20, pady=5, column=2, row=3)

        self.send_room_button = tkinter.Button(self.win, text="Join", height=2, width=10, command=self.on_send_room)
        self.send_room_button.grid(padx=20, pady=5, column=2, row=4)

        self.exit_button = tkinter.Button(self.win, text="Quit", height=2, width=10, command=self.stop)
        self.exit_button.grid(padx=20, pady=5, column=2, row=5)

        self.gui_done_ev.set()
        self.gui_done = True
        self.win.mainloop()


if __name__ == '__main__':
    client = Client()
    client.set_up()

    client.start()
