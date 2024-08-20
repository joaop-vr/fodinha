import socket
import json
import sys
import random
import global_vars
import manage_rounds
import prints

# Função para criar socket UDP
def create_socket(num_player):
    global MY_ID, MY_IP, MY_PORT, NEXT_ID, NEXT_IP, NEXT_PORT
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    MY_ID = num_player - 1
    MY_IP = PLAYERS_IPS[MY_ID]
    MY_PORT = PLAYERS_PORTS[MY_ID]
    NEXT_ID = (MY_ID + 1) % 4
    NEXT_IP = PLAYERS_IPS[NEXT_ID]
    NEXT_PORT = PLAYERS_PORTS[NEXT_ID]
    sock.bind((MY_IP, MY_PORT))
    return sock

# Função para enviar mensagem na rede
def send_message(sock, message):
    sock.sendto(json.dumps(message).encode(), (NEXT_IP, NEXT_PORT))

# Função para processar mensagens recebidas
def process_message(sock, message):
    if IS_DEALER:
        dealer(sock, message)
    else:
        normal_player(sock, message)

# Função para receber e processar mensagens
def receive_message(sock):
    global PLAYING
    while PLAYING:
        data, addr = sock.recvfrom(1024)
        message = json.loads(data.decode())
        process_message(sock, message)

def main():
    if len(sys.argv) > 1:
        sock = create_socket(int(sys.argv[1]))
        if len(sys.argv) > 2 and sys.argv[2] == 'start':
            init_round(sock)
        receive_message(sock)
        print("Obrigado por jogar!")
    else:
        print("O código espera receber como parâmetro: python3 main.py <num_jogador> <start>")
        print("Sendo <start> é opcional, pois indica quem será o primeiro carteador.")
        sys.exit(1)

if __name__ == "__main__":
    main()
