import socket
import json
import sys
import random

# Configurações da rede
MY_ID = 0
TOKEN = False
IS_DEALER = False
DEALER_ID = 0
CARDS = []
MY_LIST = []
MY_CARDS = []
GUESSES = [None, None, None, None]
MY_IP = "10.254.223.39"
MY_PORT = 5039
NEXT_IP = "10.254.223.40"
NEXT_PORT = 5040
NEXT_ID = 1

# Função de inicialização do jogo
def init_game(sock):
    global TOKEN, CARDS, MY_LIST, IS_DEALER

    # O carteador é o primeiro a receber um token
    TOKEN = True

    # Distribui as cartas para os jogadores e armazena em 'cards'
    CARDS = distribute_cards()

    # Configurando o jogador que começou o jogo como carteador (dealer)
    IS_DEALER = True

    # Prepara as mensagens de distribuição de cartas
    for i in range(4):
        msg = {
            "type": "init",
            "from_player": MY_ID,
            "to_player": i,
            "data": CARDS[i]
        }
        MY_LIST.append(msg)
        
    # Guardando as cartas do carteador
    global MY_CARDS
    print(f"len: {len(CARDS)}")
    MY_CARDS = CARDS.pop(0)
    #print(f"Cartas do acrteador: {MY_CARDS}")

    # Prepara as mensagens de solicitação de palpites
    for i in range(4):
        msg = {
            "type": "take_guesses",
            "from_player": MY_ID,
            "to_player": i,
            "data": []
        }
        MY_LIST.append(msg)

    # Envia a primeira mensagem da lista
    print(f"Minha lista inicialmente: {MY_LIST}")
    msg = MY_LIST.pop(0)
    print(f"Enviando mensagem? {msg}")
    send_message(sock, msg, NEXT_IP, NEXT_PORT)

# Função fictícia para distribuir cartas
def distribute_cards():
    suits = ['C', 'O', 'E', 'P']  # Copas, Ouros, Espadas, Paus
    values = ['A', '2', '3', '4', '5', '6', '7', 'J', 'Q', 'K']
    cards = [value + suit for suit in suits for value in values]
    random.shuffle(cards)
    players_cards = [[] for _ in range(4)]
    N = 5  # Defina o número de cartas que deseja distribuir para cada jogador
    for i in range(N):
        for j in range(4):
            if cards:
                players_cards[j].append(cards.pop())
    return players_cards

# Função para o usuário informar o papite
def take_guess():
    guess = int(input("Informe o seu palpite: "))
    return guess

# Função para processar as mensagens do dealer
def dealer(sock, message):
    global TOKEN, MY_LIST, GUESSES
    if TOKEN == True or (message["type"] == "token" and message["to_player"] == MY_ID):
        TOKEN = True
        print(f"Recebi/estou_com o token!.")
                
        if len(MY_LIST) > 0:
            msg = MY_LIST.pop(0)
            print(f"Enviando mensagem: {msg}")
            send_message(sock, msg, NEXT_IP, NEXT_PORT)
        else:
            TOKEN = False
            msg = {
                "type": "token",
                "from_player": MY_ID,
                "to_player": NEXT_ID,
                "data": []
            }
            print(f"Paasando bastão: {msg}")
            send_message(sock, msg, NEXT_IP, NEXT_PORT)

    elif message['to_player'] == MY_ID:
        print(f"Recebi uma mensagem! {message}")
        print(f"antes GUESSES: {GUESSES}")
        if message["type"] == "receive_guesses":
            #print(f"len: {len(GUESSES)}")
            #if len(GUESSES) < 4:
            GUESSES[message['from_player']] = message["data"]
            print(f"Recebi o seguinte palpite: {message['data']}")
            print(f"depois GUESSES: {GUESSES}")
            count_nones = 0
            for guess in GUESSES:
                if guess == None:
                    count_nones++
            if count_nones == 1:
                guess = take_guess()
                GUESSES[MY_ID] = guess
                print(f"Palpites completos: {GUESSES}")
                
                for i in range(1,4):
                    msg = {
                        "type":"inform_guesses",
                        "from_player": MY_ID,
                        "to_player": i,
                        "data": GUESSES
                    }
                    MY_LIST.append(msg)
                #print(f"Vou começar a mandar os palpites: {MY_LIST}")
                #msg = MY_LIST.pop(0)
                #print(f"Estou enviando a mensgaem: {msg}")
                pass_message(sock, message)
            else:
                pass_message(sock, message)
        elif message['inform_guesses']:
            print("Palpites: ")
            for i in range(len(message['data'])):
                print(f"Jogaor {i+1}: {message['data'][i]}")
    else:
        pass_message(sock, message)

# Função para processar as mensagens do jogador padrão
def normal_player(sock, message):
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
                "to_player": NEXT_ID,
                "data": []
            }
            print(f"Estou passando o bastao: {msg}")
            send_message(sock, msg, NEXT_IP, NEXT_PORT)
    elif message["to_player"] == MY_ID:
        if message["type"] == "init" and message["to_player"] == MY_ID:
            global DEALER_ID
            DEALER_ID = message["from_player"]
            MY_CARDS.append(message['data'])
            print(f"Jogador {MY_ID} recebeu suas cartas: {MY_CARDS}.")
            pass_message(sock, message)
        elif message["type"] == "take_guesses":
            guess = take_guess()
            msg = {
                "type": "receive_guesses",
                "from_player": MY_ID,
                "to_player": DEALER_ID,
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
    else:
        pass_message(sock, message)
  
# Função para processar mensagens recebidas
def process_message(sock, message):
    if IS_DEALER:
        dealer(sock, message)
    else:
        normal_player(socl, message)

# Função para criar socket UDP
def create_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((MY_IP, MY_PORT))
    return sock

# Função para enviar mensagem UDP
def send_message(sock, message, ip, port):
    sock.sendto(json.dumps(message).encode(), (ip, port))
    
# Função para passar a mensagem adiante
def pass_message(sock, message):
    send_message(sock, message, NEXT_IP, NEXT_PORT)

# Função para receber e processar mensagens
def receive_message(sock):
    while True:
        data, addr = sock.recvfrom(1024)
        message = json.loads(data.decode())
        process_message(sock, message)

def main():
    sock = create_socket()
    cards = []
    if len(sys.argv) > 1 and sys.argv[1] == 'start':
        init_game(sock)
    receive_message(sock)

if __name__ == "__main__":
    main()
