import socket
import json
import sys

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
    
    # Enviar cartas para o próprio dealer
    #msg = {
    #    "type": "init",
    #    "player": len(PLAYERS_IPS) + 1,
    #    "cards": cards[-1]
    #}
    #process_message(sock, msg)

# Função fictícia para distribuir cartas
def distribute_cards():
    return [["3H", "4D", "5S"], ["2H", "2D", "6S"], ["7H", "8D", "9S"], ["AH", "AD", "AS"]]

# Função para processar mensagens recebidas
def process_message(sock, message):
    if message["type"] == "init":
        print(f"Jogador {message['player']} recebeu cartas: {message['cards']}")
        if message['player'] == 1:  # O dealer começa o jogo
            make_move(sock, message)
    elif message["type"] == "play":
        if message["next_player"] == 1:
            make_move(sock, message)
        else:
            pass_message(sock, message)

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
        #process_message(sock, message)

def main():
    sock = create_socket()
    if len(sys.argv) > 1 and sys.argv[1] == 'start':
        init_game(sock)
    receive_message(sock)

if __name__ == "__main__":
    main()

