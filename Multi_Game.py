from Textures_Audio import *
from Game_Parameters import *
import socket
import select
import random
import glob


class Client_Globals:
    def __init__(self):
        self.player_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = get_name()

        # ints
        self.position1 = 0
        self.rotation1 = 0
        self.bullets = 30

        # booleans
        self.feed_changed = False
        self.health_changed = False
        self.alive = True
        self.game_ended = False

        # strings
        self.feed = ""
        self.data = ""
        self.me_position = ""
        self.me_rotation = ""

        # entities
        self.enemy = Enemy(position=(0, -1, 0))

        # texts
        self.dead_txt = Text(parent=camera.ui, text="Dead", color=color.red, scale=5, position=(-0.15, 0.2, 0))
        self.dead_txt.disable()
        self.bullets_txt = Text(parent=camera.ui, text=str(self.bullets), color=color.blue,
                                position=(0.78, -0.4, 0), scale=3)
        self.feed_txt = Text(parent=camera.ui, text="", color=color.dark_gray, position=(-0.88, 0.47, 0))
        self.health_txt = Text(parent=camera.ui, text="100", color=color.blue, position=(-0.85, -0.4, 0), scale=3)
        self.most_kills_txt = Text(parent=camera.ui, text="", position=(0, 0.5, 0))
        self.kills_txt = Text(parent=camera.ui, text="", color=color.blue, position=(0.78, 0.45, 0), scale=2)
        self.win_lost_txt = Text(parent=camera.ui, text="", color=color.red, scale=5)


class Enemy(Button):
    def __init__(self, position=(0, 0, 0), rotation=(0, 0, 0), player_name=""):
        super().__init__(
            parent=scene,
            model='cube',
            color=color.red,
            position=position,
            rotation=rotation)
        self.name = player_name
        self.alive = True

    def is_hovered(self):
        """
        checks if current player is hovered by another player
        :return: true if current player is hovered by another, false else
        """
        if self.hovered:
            return True
        return False


def get_name():
    """
    gets name from user
    :return: str
    """
    name = input(
        "Enter a name (name cannot contain space, '-', '|', '/', '*' name length <= 8 and name only in English): ")
    while 0 > len(name) or len(
            name) > 8 or "|" in name or "-" in name or "/" in name or "*" in name or " " in name or not check_ascii_name(name):
        print("Invalid name!")
        name = input(
            "Enter a different name (name cannot contain space, '-', '|', '/', '*' name length <= 8 and name only in "
            "English): ")
    return name


def check_ascii_name(name1):
    """
    checks if the name is in a different language, returns true if the name is in english or in a language that contains English letters
    :param name1: name that we want to check
    :return: boolean
    """
    if len(ascii(name1)) != len(name1) + 2:
        return False
    return True


def send_and_create_position_rotation_message():
    """
    creating and sending the rotation position name message
    """
    me_position = str(fps_camera.position)
    me_rotation = str(fps_camera.rotation)
    message = (me_position.split("Vec3")[1]).replace("(", "").replace(")", "") + "|" + (
        me_rotation.split("Vec3")[1]).replace("(", "").replace(")", "")
    length = str(len(message))
    client_globals.player_socket.send((length.zfill(2) + message).encode())


def shoot():
    """
    shoots the gun and sends the server a message that the current player shot
    """
    gunfire_sound.play()
    client_globals.bullets -= 1
    client_globals.bullets_txt.text = str(client_globals.bullets)
    fps_camera.update(1)
    length1 = str(len("shoot"))
    client_globals.player_socket.send((length1.zfill(2) + "shoot").encode())
    if client_globals.enemy.alive:
        if client_globals.enemy.hovered:
            hit_sound.play()
            message = client_globals.name + " shot " + client_globals.enemy.name
            length1 = str(len(message))
            client_globals.player_socket.send((length1.zfill(2) + message).encode())


def reload():
    """
    reloads the gun
    """
    reload_sound.play()
    client_globals.bullets = 30
    client_globals.bullets_txt.text = str(client_globals.bullets)


def respawn():
    """
    respawns the player and sends to the server a message that the player has respawned
    """
    client_globals.dead_txt.disable()
    client_globals.alive = True
    client_globals.bullets = 30
    client_globals.bullets_txt.text = str(client_globals.bullets)
    client_globals.health_txt.text = "100"
    fps_camera.enable()
    fps_camera.position = (random.randint(-30, 30), 5, random.randint(-70, -30))
    client_globals.feed_changed = True
    feed = client_globals.name + " respawned"
    length = str(len(feed))
    client_globals.player_socket.send((length.zfill(2) + feed).encode())


def restart():
    """
    restart all the variables that need to be restarted
    """
    client_globals.game_ended = False
    client_globals.alive = True
    client_globals.health_changed = True
    client_globals.feed = "Game restarted"
    client_globals.feed_changed = True
    client_globals.bullets = 30
    client_globals.bullets_txt.text = str(client_globals.bullets)
    client_globals.health_txt.text = "100"
    client_globals.kills_txt.text = ""
    client_globals.most_kills_txt.text = ""
    client_globals.win_lost_txt.text = ""
    fps_camera.enable()
    fps_camera.position = (random.randint(-30, 30), 2, random.randint(-70, -30))
    client_globals.enemy.alive = True


def handle_position_rotation():
    """
    handles position, rotation message
    """
    position_1 = client_globals.data.split("|")[0]
    rotation_1 = client_globals.data.split("|")[1]
    client_globals.enemy.position = (
        float(position_1.split(",")[0]), float(position_1.split(",")[1]) + 2, float(position_1.split(",")[2]))
    client_globals.enemy.rotation = (float(rotation_1.split(",")[0]), float(rotation_1.split(",")[1]), float(rotation_1.split(",")[2]))


def handle_killed():
    """
    handles killed message
    """
    client_globals.feed_changed = True
    client_globals.feed = client_globals.data
    client_globals.enemy.alive = False


def handle_respawned():
    """
    handles respawned message
    """
    client_globals.feed_changed = True
    client_globals.feed = client_globals.data
    client_globals.enemy.alive = True


def handle_won():
    """
    handle won message
    """
    client_globals.game_ended = True
    client_globals.dead_txt.disable()
    if client_globals.data.split(" won!")[0] == client_globals.name:
        client_globals.win_lost_txt.position = (-0.15, 0.3, 0)
        client_globals.win_lost_txt.text = "WIN"
        client_globals.win_lost_txt.color = color.blue
        win_sound.play()
    else:
        client_globals.win_lost_txt.position = (-0.2, 0.3, 0)
        client_globals.win_lost_txt.text = "LOSS"
        client_globals.win_lost_txt.color = color.red
        lost_sound.play()


def handle_joined():
    """
    handles joined message
    """
    client_globals.enemy.enable()
    client_globals.feed_changed = True
    client_globals.feed = client_globals.data
    client_globals.enemy.name = client_globals.data.split(" joined!")[0]
    send_and_create_position_rotation_message()


def handle_left():
    """
    handles left message
    """
    client_globals.feed_changed = True
    client_globals.feed = client_globals.data
    client_globals.enemy.disable()


def handle_most_kills_player():
    """
    handles most kills player message
    """
    most_killer = client_globals.data.split(" - ")[0]
    if most_killer == client_globals.name:
        client_globals.most_kills_txt.text = "You" + " - " + client_globals.data.split(" - ")[1]
    else:
        client_globals.most_kills_txt.text = client_globals.data


def handle_health():
    """
    handles health message
    """
    hurt_sound.play()
    health = client_globals.data.split("*")[1]
    if int(health) <= 0:
        client_globals.dead_txt.enable()
        client_globals.health_txt.text = "0"
        client_globals.alive = False
        fps_camera.y = -1.5
        fps_camera.disable()
        client_globals.feed = client_globals.enemy.name + " killed You"
        client_globals.feed_changed = True
    else:
        client_globals.health_txt.text = health


def handle_game_restart():
    """
    handles the game restart messages
    """
    if client_globals.data[17] == "0":
        client_globals.feed = "Game restarted"
        restart()
    else:
        client_globals.feed = client_globals.data
    client_globals.feed_changed = True


def get_server_data():
    """
    retrieves server information from a text file, if the text file doest exists creates a new text file and inputs ip and ports
    """
    path = "assets\\Server_Information.txt"
    file_list = glob.glob("assets\\Server_Information.txt")
    if len(file_list) == 0:
        file = open(path, 'w')
        print("Server's information txt file doesn't exists!")
        ip = input("Enter server's ip: ")
        port = input("Enter server's port: ")
        file.write(ip + "," + port)
        file_data = ip + "," + port
    else:
        file = open(path, 'r')
        file_data = file.read()
    file.close()
    return file_data


def receive_from_server():
    """
    receives data from server and acts accordingly
    """
    if client_globals.me_position != str(fps_camera.position) or client_globals.me_rotation != str(fps_camera.rotation):
        send_and_create_position_rotation_message()

    r_list, w_list, e_list = select.select([client_globals.player_socket], [client_globals.player_socket], [])
    for sock in r_list:
        length = client_globals.player_socket.recv(2).decode()
        try:
            client_globals.data = sock.recv(int(length)).decode()
        except ValueError:
            print("error - ValueError")
            quit()

        if "|" not in client_globals.data:
            print(client_globals.data)

        if "|" in client_globals.data:  # 0,0,0|0,0,0
            handle_position_rotation()

        elif "Game restart" in client_globals.data:  # (Game restarts in 5) or (Game restarted)
            handle_game_restart()

        elif "shoot" in client_globals.data:  # shoot
            enemy_fire_sound.play()

        elif " killed " in client_globals.data:  # me killed name
            handle_killed()

        elif "*" in client_globals.data:  # me*health
            handle_health()

        elif "/" in client_globals.data:  # me/kills
            client_globals.kills_txt.text = client_globals.data.split("/")[1]

        elif " respawned" in client_globals.data:  # name respawned
            handle_respawned()

        elif " won!" in client_globals.data:  # name won!
            handle_won()

        elif " joined!" in client_globals.data:  # name joined!
            handle_joined()

        elif " left!" in client_globals.data:  # name left!
            handle_left()

        elif " - " in client_globals.data:  # name - kills
            handle_most_kills_player()


def update():
    """
    called every frame, handles inputs and calls a function that received data from user
    """
    receive_from_server()
    if client_globals.feed_changed:
        client_globals.feed_changed = False
        client_globals.feed_txt.text = client_globals.feed

    if not client_globals.game_ended:
        if held_keys['m'] and not client_globals.alive:
            if not keys_dict['m']:
                keys_dict['m'] = True
                respawn()
        else:
            keys_dict['m'] = False

        if held_keys['q']:
            client_globals.feed = client_globals.name + " left!"
            length1 = str(len(client_globals.feed))
            client_globals.player_socket.send((length1.zfill(2) + client_globals.feed).encode())
            quit()

    if client_globals.alive:
        if held_keys['w'] and held_keys['left shift']:
            gun.active()
        else:
            gun.passive()
            if client_globals.bullets > 0:
                if held_keys['left mouse']:
                    if not keys_dict['left mouse']:
                        keys_dict['left mouse'] = True
                        shoot()
                else:
                    keys_dict['left mouse'] = False

            if held_keys['r']:
                if not keys_dict['r'] and client_globals.bullets < 30:
                    keys_dict['r'] = True
                    reload()
            else:
                keys_dict['r'] = False


def main():
    """
    joining the server, receiving a player name if someone has joined the server and sending the first message
    """
    server_data = get_server_data()
    ip = server_data.split(",")[0]
    port = server_data.split(",")[1]
    print("Connecting to the server...")
    try:
        client_globals.player_socket.connect((ip, int(port)))
    except ConnectionRefusedError:
        print("Server is offline!")
        quit()
    length = client_globals.player_socket.recv(2).decode()
    try:
        client_globals.data = client_globals.player_socket.recv(int(length)).decode()
    except ValueError:
        print("error - ValueError")
        quit()
    if client_globals.data == "Server is full!":
        print(client_globals.data)
        quit()
    client_globals.enemy.name = client_globals.data
    while client_globals.name == client_globals.enemy.name:
        print("Player with the same name already joined the server!")
        client_globals.name = get_name()
    client_globals.feed = client_globals.name + " joined!"
    length = str(len(client_globals.feed))
    client_globals.player_socket.send((length.zfill(2) + client_globals.feed).encode())
    print("Joined!")

    app.run()


client_globals = Client_Globals()

if __name__ == "__main__":
    main()
