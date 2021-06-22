import json

NO_ROOMS_JSON_PARAM = 'There is no active rooms currently. Create your own'
INSTRUCTIONS = 'You have to choose room and then start typing, button quit to quit'


class Hall:
    def __init__(self):
        self.rooms = {}
        self.room_user_map = {}
        self.users = []

    def list_rooms(self):

        if len(self.rooms) == 0:
            return NO_ROOMS_JSON_PARAM
        else:
            msg = 'Rooms:\n'
            for room in self.rooms:
                msg += '> ' + room + ": " + str(len(self.rooms[room].users)) + ' user(s)\n'
            return msg

    def handle_msg(self, user, msg):

        if "<name>" in msg:
            name = msg.split()[1]
            all_names = [user.name for user in self.users]
            if name in all_names:
                return []

            user.name = name
            self.users.append(user)
            print("New connection from:", user.name)

            json_dict = {
                'list': self.list_rooms(),
                'message': "Room is not selected",
                'registered': user.name
            }
            send_data = json.dumps(json_dict).encode()
            return [(send_data, user)]

        elif "<join>" in msg:
            if len(msg.split()) >= 2:
                room_name = msg.split()[1]
                old_room_users = []
                new_room_users = []
                old_room_dict = {}
                new_room_dict = {}

                if user.name in self.room_user_map:
                    if self.room_user_map[user.name] == room_name:
                        return [(b'{"message": "You are already in room: ' + room_name.encode() + b'"}', user)]

                    old_room = self.room_user_map[user.name]
                    old_room_dict, old_room_users = self.rooms[old_room].remove_user_cmd(user)

                if room_name not in self.rooms:
                    new_room = Room(room_name)
                    self.rooms[room_name] = new_room

                self.rooms[room_name].users.append(user)
                self.room_user_map[user.name] = room_name

                base_dict = {'list': self.list_rooms()}

                new_room_dict, new_room_users = self.rooms[room_name].welcome_new_cmd(user)
                new_room_dict.update(base_dict)
                old_room_dict.update(base_dict)

                to_other_msg = json.dumps(base_dict).encode()
                new_room_msg = json.dumps(new_room_dict).encode()
                old_room_msg = json.dumps(old_room_dict).encode()

                other_users = [
                    user for user in self.users
                    if user not in old_room_users + new_room_users
                ]

                print(to_other_msg, new_room_msg, old_room_msg, '\n')

                commands = [(new_room_msg, room_user) for room_user in new_room_users] + \
                           [(old_room_msg, room_user) for room_user in old_room_users] + \
                           [(to_other_msg, other_user) for other_user in other_users]

                return commands
            else:
                json_dict = {
                    'message': INSTRUCTIONS
                }
                data = json.dumps(json_dict).encode()
                return [(data, user)]

        elif "<list>" in msg:
            json_dict = {
                'list': self.list_rooms()
            }
            data = json.dumps(json_dict).encode()
            return [(data, user)]

        elif "<message>" in msg:
            package = msg.split(' ', 1)
            if len(package) < 2:
                return []
            message = package[1]

            if user.name in self.room_user_map:
                room = self.rooms[self.room_user_map[user.name]]
                room_dict, room_users = room.broadcast_cmd(user, message)
                room_msg = json.dumps(room_dict).encode()
                return [(room_msg, room_user) for room_user in room_users]
            else:
                json_dict = {
                    'message': "You are currently not in any room"
                }
                data = json.dumps(json_dict).encode()
                return [(data, user)]
        else:
            return []

    def remove_user(self, user):
        self.users.remove(user)
        if user.name not in self.room_user_map:
            print("User: " + user.name + " has left\n")
            return []

        room = self.rooms[self.room_user_map[user.name]]
        room_dict, room_users = room.remove_user_cmd(user)
        del self.room_user_map[user.name]

        base_dict = {'list': self.list_rooms()}
        room_dict.update(base_dict)
        other_users = [
            other_user for other_user in self.users if other_user not in room_users
        ]

        to_other_msg = json.dumps(base_dict).encode()
        room_msg = json.dumps(room_dict).encode()

        commands = [(room_msg, room_user) for room_user in room_users] + \
                   [(to_other_msg, other_user) for other_user in other_users]

        print("User: " + user.name + " has left\n")
        return commands


class Room:
    def __init__(self, name):
        self.users = []
        self.name = name

    def welcome_new_cmd(self, from_user):
        msg_dict = {
            'message': self.name + ' welcomes: ' + from_user.name + '\n',
            'welcome': from_user.name
        }
        commands = (msg_dict, self.users)
        return commands

    def broadcast_cmd(self, from_user, msg):
        msg_dict = {
            'message': from_user.name + ": " + msg
        }
        commands = (msg_dict, self.users)
        return commands

    def remove_user_cmd(self, user):
        self.users.remove(user)

        msg_dict = {
            'message': user.name + " has left the room"
        }
        commands = (msg_dict, self.users)
        return commands


class User:
    def __init__(self, socket, name="not registered"):
        socket.setblocking(False)
        self.socket = socket
        self.name = name
