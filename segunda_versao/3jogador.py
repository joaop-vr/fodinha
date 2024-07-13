import socket
import json
import sys

# Configurações da rede
MY_ID = 3
MY_IP = "10.254.223.42"  # IP desta máquina
MY_PORT = 5042           # Porta para receber mensagens
NEXT_IP = "10.254.223.39"  # IP da próxima máquina no anel
NEXT_PORT = 5039         # Porta para enviar mensagens

# Função para criar socket UDP
def create_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((MY_IP, MY_PORT))
    return sock

# Função para enviar mensagem UDP
def send_message(sock, message, ip, port):
    sock.sendto(json.dumps(message).encode(), (ip, port))

# Função para processar mensagens recebidas
def process_message(sock, message):
    if message["player"] == MY_ID:
        print(f"Jogador {MY_ID} recebeu suas cartas: {message['cards']}")
    
    pass_message(sock, message)
    #elif message["type"] == "play":
    #    if message["next_player"] == 2:
    #        make_move(sock, message)
    #    else:
    #        pass_message(sock, message)

# Função para fazer uma jogada
def make_move(sock, message):
    jogada = {
        "type": "play",
        "player": 2,
        "cards_played": ["2H", "2D"],
        "declared_value": "2",
        "table_cards": message.get("table_cards", []) + ["2H", "2D"],
        "next_player": 3,
        "challenge": False,
        "challenge_result": None
    }
    send_message(sock, jogada, NEXT_IP, NEXT_PORT)

# Função para passar a mensagem adiante
def pass_message(sock, message):
    #next_player_index = (message["next_player"] - 1) % len(PLAYERS_IPS)
    #next_ip = PLAYERS_IPS[next_player_index]
    #next_port = PLAYERS_PORTS[next_player_index]
    send_message(sock, message, NEXT_IP, NEXT_PORT)

# Função para receber e processar mensagens
def receive_message(sock):
    while True:
        data, addr = sock.recvfrom(1024)
        message = json.loads(data.decode())
        process_message(sock, message)

def main():
    sock = create_socket()
    receive_message(sock)

if __name__ == "__main__":
    main()
