import socket
import json
import sys
import random

# Configurações da rede
MY_ID = 0
PLAYERS_IPS = ["10.254.223.40", "10.254.223.41", "10.254.223.42"]
PLAYERS_PORTS = [5040, 5041, 5042]
MY_IP = "10.254.223.39"
MY_PORT = 5039
NEXT_IP = "10.254.223.40"
NEXT_PORT = 5040

# Função para criar socket UDP
def create_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((MY_IP, MY_PORT))
    return sock

# Função para enviar mensagem UDP
def send_message(sock, message, ip, port):
    sock.sendto(json.dumps(message).encode(), (ip, port))

# Função de inicialização do jogo
def init_game(sock):
    cards = distribute_cards()
    for i in range(3):
        msg = {
            "type": "init",
            "player": i + 1,
            "cards": cards[i]
        }
        send_message(sock, msg, PLAYERS_IPS[i], PLAYERS_PORTS[i])

# Função fictícia para distribuir cartas
def distribute_cards():
    suits = ['C', 'O', 'E', 'P']  # Copas, Ouros, Espadas, Paus
    values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    cards = [value + suit for suit in suits for value in values]
    random.shuffle(cards)
    players = [[] for _ in range(3)]
    N = 5  # Defina o número de cartas que deseja distribuir para cada jogador
    for i in range(N):
        for j in range(3):
            if cards:
                players[j].append(cards.pop())
    return players

# Função para processar mensagens recebidas
def process_message(sock, message):
    if message["type"] == "init":
        print(f"Todos os jogadores receberam suas cartas!")
        msg = {
            "type": "take_guesses",
            "player": MY_ID,
            "guesses": []
        }
        send_message(sock, msg, NEXT_IP, NEXT_PORT)
    elif message["type"] == "take_guesses":
        print(f"Todos os jogadores já deram os palpites")
        message['type'] = "inform_guesses"
        send_message(sock, message, NEXT_IP, NEXT_PORT)
    elif message['type'] == "inform_guesses":
        print(f"Todos foram informados dos palpites, podemos começar a jogar!")

# Função para fazer uma jogada
def make_move(sock, message):
    jogada = {
        "type": "play",
        "player": 1,
        "cards_played": ["3H", "3D"],
        "declared_value": "3",
        "table_cards": message.get("table_cards", []) + ["3H", "3D"],
        "next_player": 2,
        "challenge": False,
        "challenge_result": None
    }
    send_message(sock, jogada, NEXT_IP, NEXT_PORT)

# Função para passar a mensagem adiante
def pass_message(sock, message):
    next_player_index = (message["next_player"] - 1) % len(PLAYERS_IPS)
    next_ip = PLAYERS_IPS[next_player_index]
    next_port = PLAYERS_PORTS[next_player_index]
    send_message(sock, message, next_ip, next_port)

# Função para receber e processar mensagens
def receive_message(sock):
    while True:
        data, addr = sock.recvfrom(1024)
        message = json.loads(data.decode())
        process_message(sock, message)

def main():
    sock = create_socket()
    if len(sys.argv) > 1 and sys.argv[1] == 'start':
        init_game(sock)
    receive_message(sock)

if __name__ == "__main__":
    main()

