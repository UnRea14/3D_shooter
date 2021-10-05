import socket
import select
import datetime


class Server_Globals:
    def __init__(self):
        self.messages_to_send = []
        self.game_ended = False
        self.t = None
        self.t_count = 5


class Player:
    def __init__(self, sock, player_name):
        self.player_name = player_name
        self.sock = sock
        self.kills = 0
        self.health = 100

    def reset(self, sock=None, player_name=""):
        """
        resets the player to values given/ stock values
        :param sock: player's socket
        :param player_name: player's name
        :return: None
        """
        self.player_name = player_name
        self.sock = sock
        self.kills = 0
        self.health = 100

    def get_name(self):
        """
        returns the player's name
        :return: str
        """
        return self.player_name

    def get_kills(self):
        """
        returns the player's kills
        :return: int
        """
        return self.kills

    def set_kills(self, kills):
        """
        sets the player's kills to the given kills
        :param kills: wanted kills value
        """
        self.kills = kills

    def inc_kills(self):
        """
        increments kills
        """
        self.kills += 1

    def get_sock(self):
        """
        returns the player's socket
        :return: socket
        """
        return self.sock

    def get_health(self):
        """
        returns the player's name
        :return: str
        """
        return self.health

    def set_health(self, health):
        """
        sets the player's health to the given health
        :param health: wanted health value
        """
        self.health = health


def send_kills(player1, player2):
    """
    creates the kills message and appends it to message_to_append list
    :param player1: the other player that we don't want to send the message to
    :param player2: the player that we want to send to his kills
    """
    message = player2.get_name() + "/" + str(player2.get_kills())
    length = str(len(message))
    server_globals.messages_to_send.append((player1.sock, length.zfill(2) + message))  # name/kills


def send_health(player1, player2):
    """
    creates the kills message and appends it to message_to_append list
    :param player1: the other player that we don't want to send the message to
    :param player2: the player that we want to send to his health
    """
    message = player1.get_name() + "*" + str(player1.get_health())
    length = str(len(message))
    server_globals.messages_to_send.append((player2.sock, length.zfill(2) + message))  # name*health


def send_killed(player1, player2):
    """
    creates the kills message and appends it to message_to_append list
    :param player1: the player that got killed
    :param player2: the player that killed
    """
    message = player2.get_name() + " killed " + player1.get_name()
    length = str(len(message))
    server_globals.messages_to_send.append((player1.sock, length.zfill(2) + message))  # name killed name


def send_won(player):
    """
    creates the kills message and appends it to message_to_append list
    :param player: the player who won
    """
    server_globals.t = datetime.datetime.now().second
    server_globals.game_ended = True
    message = player.get_name() + " won!"
    print(message)
    length = str(len(message))
    server_globals.messages_to_send.append((None, length.zfill(2) + message))  # name won!


def send_max_killer(player):
    """
    creates the kills message and appends it to message_to_append list
    :param player: the max killer
    """
    message = player.get_name() + " - " + str(player.get_kills())
    print(message)
    length = str(len(message))
    server_globals.messages_to_send.append((None, length.zfill(2) + message))  # name - 0


def handle_shot(player1, player2, who_shot):
    """
    handles the shot message
    :param player1: player 1
    :param player2: player 2
    :param who_shot: player name - which player shot the other player
    """
    b = False
    if who_shot == player1.get_name():
        player1.set_health(player1.get_health() - 30)
        send_health(player1, player2)
        if player1.get_health() <= 0:
            send_killed(player1, player2)
            player2.inc_kills()
            send_kills(player1, player2)
            b = True
    else:
        player2.set_health(player2.get_health() - 30)
        send_health(player2, player1)
        if player2.get_health() <= 0:
            send_killed(player2, player1)
            player1.inc_kills()
            send_kills(player2, player1)
            b = True

    if player1.get_kills() >= 30 or player2.get_kills() >= 30:
        if player1.get_kills() >= 30:
            send_won(player1)
        else:
            send_won(player2)
        player1.set_health(100)
        player1.set_kills(0)
        player2.set_health(100)
        player2.set_kills(0)
    elif b:
        if player1.get_kills() > player2.get_kills():
            send_max_killer(player1)
        elif player1.get_kills() < player2.get_kills():
            send_max_killer(player2)


def handle_respawned(who, player1, player2):
    """
    handles the respawned message
    :param player1: player 1
    :param player2: player 2
    :param who: the player's name that respawned
    """
    if who == player1.get_name():
        player1.set_health(100)
    else:
        player2.set_health(100)


def handle_joined(player_name, players_socket, player1, player2):
    """
    handles the joined message
    :param player1: player 1
    :param player2: player 2
    :param players_socket: current player socket
    :param player_name: the name of the player that joined
    """
    if player1.get_name() == "":
        player1.reset(players_socket, player_name)
    else:
        player2.reset(players_socket, player_name)


def handle_left(name, client_sockets, players_socket, player1, player2):
    """
    handles the left message
    :param player1: player 1
    :param player2: player 2
    :param name: the name of the player that left
    :param client_sockets: the list of players sockets
    :param players_socket: the current player socket
    """
    if (player1.get_name() != "" and player2.get_name() == "") or (
            player1.get_name() == "" and player2.get_name() != ""):
        player1.reset()
        player2.reset()
    else:
        if player1.get_name() == name:
            player1.reset()
            player2.set_kills(0)
            send_kills(player2, player1)
            player2.set_health(100)
            send_health(player2, player1)
            send_won(player2)
        else:
            player2.reset()
            player1.set_kills(0)
            send_kills(player1, player2)
            player1.set_health(100)
            send_health(player1, player2)
            send_won(player1)
    client_sockets.remove(players_socket)
    players_socket.close()


def handle_client_crash(player_socket, client_sockets, player1, player2):
    """
    handles client crash
    :param player_socket: player's socket
    :param client_sockets: lists that contains the players sockets
    :param player1: player 1
    :param player2: player 2
    """
    if player_socket == player1.get_sock():
        message = player1.get_name() + " left!"
        length = str(len(message))
        server_globals.messages_to_send.append((None, length.zfill(2) + message))
        player1 = Player(None, "")
        player2.set_kills(0)
        send_kills(player2, player1)
        player2.set_health(100)
        send_health(player2, player1)
        send_won(player2)
    else:
        message = player1.get_name() + " left!"
        length = str(len(message))
        server_globals.messages_to_send.append((None, length.zfill(2) + message))
        player2 = Player(None, "")
        player1.set_kills(0)
        send_kills(player1, player2)
        player1.set_health(100)
        send_health(player1, player2)
        send_won(player1)
    print(message)
    client_sockets.remove(player_socket)
    player_socket.close()


def main():
    """
    running the server and handles client's data
    """
    print("Setting up server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 8820))
    server_socket.listen()
    print("Looking for players...")
    player1 = Player(None, "")
    player2 = Player(None, "")
    client_sockets = []
    data = ""
    while True:
        r_list, w_list, x_list = select.select([server_socket] + client_sockets, [], [], 0.01)
        if server_globals.game_ended:
            t1 = datetime.datetime.now().second
            if t1 - server_globals.t >= 1:
                message = "Game restarts in " + str(server_globals.t_count)
                print(message)
                length = str(len(message))
                server_globals.messages_to_send.append((None, length.zfill(2) + message))
                if server_globals.t_count == 0:
                    server_globals.game_ended = False
                    server_globals.t_count = 5
                else:
                    server_globals.t_count -= 1
                    server_globals.t = t1

            for player_socket in r_list:
                if player_socket is not server_socket:
                    try:
                        length = player_socket.recv(2).decode()
                        try:
                            data = player_socket.recv(int(length)).decode()

                            if "|" not in data:
                                print(data)

                            length = str(len(data))
                            server_globals.messages_to_send.append((player_socket, length.zfill(2) + data))

                        except ValueError:
                            client_sockets.remove(player_socket)
                            player_socket.close()

                    except ConnectionResetError:
                        handle_client_crash(player_socket, client_sockets, player1, player2)
        else:
            for player_socket in r_list:
                if player_socket is server_socket:
                    connection, client_address = player_socket.accept()
                    if player1.get_name() == "" or player2.get_name() == "":
                        client_sockets.append(connection)
                        if player1.get_name() == "":
                            length = str(len(player2.get_name()))
                            connection.send((length.zfill(2) + player2.get_name()).encode())
                        else:
                            length = str(len(player1.get_name()))
                            connection.send((length.zfill(2) + player1.get_name()).encode())
                    else:
                        connection.send("15Server is full!".encode())
                else:
                    try:
                        length = player_socket.recv(2).decode()
                        try:
                            data = player_socket.recv(int(length)).decode()
                        except ValueError:
                            client_sockets.remove(player_socket)
                            player_socket.close()

                        if "|" not in data:
                            print(data)

                        if " shot " in data:
                            who_shot = data.split(" shot ")[1]
                            handle_shot(player1, player2, who_shot)

                        elif " respawned" in data:
                            length = str(len(data))
                            server_globals.messages_to_send.append((None, length.zfill(2) + data))
                            who = data.split(" respawned")[0]
                            handle_respawned(who, player1, player2)

                        else:
                            length = str(len(data))
                            server_globals.messages_to_send.append((player_socket, length.zfill(2) + data))
                            if " joined!" in data:
                                name = data.split(" joined!")[0]
                                handle_joined(name, player_socket, player1, player2)

                            elif " left!" in data:
                                name = data.split(" left!")[0]
                                handle_left(name, client_sockets, player_socket, player1, player2)

                    except ConnectionResetError:
                        handle_client_crash(player_socket, client_sockets, player1, player2)

        for message in server_globals.messages_to_send:
            current_socket, data = message
            for sock in client_sockets:
                if sock != current_socket:
                    sock.send(data.encode())
        server_globals.messages_to_send = []


server_globals = Server_Globals()
if __name__ == "__main__":
    main()
