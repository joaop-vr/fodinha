import socket
import json
import sys

# Configurações da rede
MY_ID = 1
MY_IP = "10.254.223.40"  # IP desta máquina
MY_PORT = 5040           # Porta para receber mensagens
NEXT_IP = "10.254.223.41"  # IP da próxima máquina no anel
NEXT_PORT = 5041         # Porta para enviar mensagens
MY_CARDS = []            # Lista com as cartas do jogador
MY_LIST = []
TOKEN = False

# Função para criar socket UDP
def create_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((MY_IP, MY_PORT))
    return sock

# Função para enviar mensagem UDP
def send_message(sock, message, ip, port):
    sock.sendto(json.dumps(message).encode(), (ip, port))

# Função para o usuário informar o papite
def take_guess():
    #print(f"Palpites ate entao: {message['guesses']}")
    guess = int(input("Informe o seu palpite: "))
    #message['guesses'].append(guess)
    return guess

# Função para processar mensagens recebidas
def process_message(sock, message):
    global TOKEN, MY_LIST, MY_CARDS
    if TOKEN == True or (message["type"] == "token" and message["to_player"] == MY_ID):
        TOKEN = True
        if len(MY_LIST) > 0:
            msg = MY_LIST.pop(0)
            print(f"Estou enviando a mensagem: {msg}")
            send_message(sock, msg, NEXT_IP, NEXT_PORT)
        else:
            TOKEN = False
            msg = {
                "type": "token",
                "from_player": MY_ID,
                "to_player": 2,
                "data": []
            }
            print(f"Estou passando o bastao: {msg}")
            send_message(sock, msg, NEXT_IP, NEXT_PORT)
    elif message["to_player"] == MY_ID:
        if message["type"] == "init" and message["to_player"] == 1:
            MY_CARDS.append(message['data'])
            print(f"Jogador {MY_ID} recebeu suas cartas: {MY_CARDS}.")
            pass_message(sock, message)
        elif message["type"] == "take_guesses":
            guess = take_guess()
            msg = {
                "type": "receive_guesses",
                "from_player": MY_ID,
                "to_player": 0,
                "data": guess
            }
            MY_LIST.append(msg)
            print(f"Fez o appende de: {msg}")
            pass_message(sock, message)
        elif message["type"] == "inform_guesses":
            print(f"Palpites:")
            for i in range(len(message['data'])):
                print(f"Jogador {i+1}: {message['data'][i]}.")
            pass_message(sock, message)
            #elif message["type"] == "play":
            #    if message["next_player"] == 2:
            #       make_move(sock, message)
            #    else:
            #        pass_message(sock, message)

    else:
        pass_message(sock, message)

       
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
