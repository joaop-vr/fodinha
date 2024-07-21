import socket
import json
import sys
import random

# Configurações da rede
TABLE_CARD = 0
ROUND = 0
TOKEN = False
IS_DEALER = False
DEALER_ID = 0
CARDS = []
MY_LIST = []
MY_CARDS = []
GUESSES = [None, None, None, None]
PLAYERS_IPS = ["10.254.223.39", "10.254.223.40", "10.254.223.41", "10.254.223.42"]
PLAYERS_PORTS = [5039, 5040, 5041, 5042]
MY_ID = 0
MY_IP = 0
MY_PORT = 0
NEXT_ID = 0
NEXT_IP = 0
NEXT_PORT = 0

# Função de inicialização do jogo
def init_game(sock):
    global TOKEN, CARDS, MY_LIST, IS_DEALER, ROUND, TABLE_CARD

    # O carteador é o primeiro a receber um token
    TOKEN = True
    
    # Contador de rodadas
    ROUND = ROUND + 1

    # Distribui as cartas para os jogadores e armazena em 'cards'
    CARDS = distribute_cards()

    # Configurando o jogador que começou o jogo como carteador (dealer)
    IS_DEALER = True

    # Prepara as mensagens de distribuição de cartas
    for i in range(1,4):
        msg = {
            "type": "init",
            "from_player": MY_ID,
            "to_player": (MY_ID+i)%4, # Isso possibilita a universalização do carteador
            "data": CARDS[i]
        }
        MY_LIST.append(msg)
        
    # Guardando as cartas do carteador
    global MY_CARDS
    # print(f"[DEBUG] len: {len(CARDS)}")
    MY_CARDS = CARDS.pop(0)
    # print(f"[DEBUG] Cartas (total): {MY_CARDS}")    
    TABLE_CARD = MY_CARDS.pop()
    print(f"Manilha: {TABLE_CARD}")
    print(f"Cartas do carteador: {MY_CARDS}")

    # Prepara as mensagens de solicitação de palpites
    for i in range(1,4):
        msg = {
            "type": "take_guesses",
            "from_player": MY_ID,
            "to_player": (MY_ID+i)%4, # Isso possibilita a universalização do carteador
            "data": []
        }
        MY_LIST.append(msg)

    # Envia a primeira mensagem da lista
    # print(f"[DEBUG] Minha lista inicialmente: {MY_LIST}")
    msg = MY_LIST.pop(0)
    # print(f"[DEBUG] Enviando mensagem? {msg}")
    send_message(sock, msg, NEXT_IP, NEXT_PORT)

# Função fictícia para distribuir cartas
def distribute_cards():
    suits = ['C', 'O', 'E', 'P']  # Copas, Ouros, Espadas, Paus
    values = ['A', '2', '3', '4', '5', '6', '7', 'J', 'Q', 'K']
    cards = [value + suit for suit in suits for value in values]
    random.shuffle(cards)
    players_cards = [[] for _ in range(4)]
    for i in range(ROUND): # ROUND == número de cartas sorteadas
        for j in range(4):
            if cards:
                players_cards[j].append(cards.pop())

    # Sorteando a minilha (table_card)
    random.shuffle(values)
    table_card = values.pop()
    for i in range(4):
        players_cards[i].append(table_card)
    return players_cards

# Função para o usuário informar o palpite
def take_guess(count_guesses=0):
    # Solicita o palpite do usuário
    while True:
        try:
            guess = int(input("Informe o seu palpite: "))
            if guess < 0:
                raise ValueError("O palpite deve ser um inteiro natural (não negativo).")
            break
        except ValueError as e:
            print(f"Entrada inválida: {e}. Tente novamente.")

    # Verifica se o palpite é maior que o número de cartas que possui
    while guess > len(MY_CARDS):
        print("Não é possível dar um palpite maior que o número de cartas que possui.")
        guess = int(input("Dê outro palpite: "))
    
    # Verifica se a soma dos palpites é igual ao número de rodadas
    if count_guesses != 0 and ROUND >= 2:
        while count_guesses + guess == ROUND:
            print(f"A soma dos palpites deve ser diferente de {ROUND}.")
            guess = int(input("Dê outro palpite: "))
            while guess > len(MY_CARDS):
                print("Não é possível dar um palpite maior que o número de cartas que possui.")
                guess = int(input("Dê outro palpite: "))

    return guess

# Função para processar as mensagens do dealer
def dealer(sock, message):
    global TOKEN, MY_LIST, GUESSES
    if message["type"] != "token" and message["to_player"] == MY_ID:
        print(f"[DEBUG] Recebi uma mensagem! {message}")
        if message["type"] == "receive_guesses":
            # Armazena o palpite
            GUESSES[message['from_player']] = message["data"]
            # print(f"[DEBUG]Recebi o seguinte palpite: {message['data']}")
            # Contabiliza a quantidade de palpites já recebidos para saber se está
            # na hora do carteador dar o seu palpite (ele é o último a afazer)
            count_nones = 0
            count_guesses = 0
            for guess in GUESSES:
                if guess == None:
                    count_nones = count_nones+1
                else:
                    count_guesses = count_guesses + guess
            if count_nones == 1: # Só falta um palpite: o do carteador
                guess = take_guess(count_guesses)
                GUESSES[MY_ID] = guess
                # print(f"[DEBUG] Palpites completos: {GUESSES}")
                # Preparo das mensagens com a info dos palpites 
                # de forma a deixar o carteador por último
                for i in range(1,4):
                    msg = {
                        "type":"inform_guesses",
                        "from_player": MY_ID,
                        "to_player": (MY_ID+i)%4, # Isso possibilita a universalização do carteador
                        "data": GUESSES
                    }
                    MY_LIST.append(msg)
                msg = {
                    "type":"inform_guesses",
                    "from_player": MY_ID,
                    "to_player": MY_ID, 
                    "data": GUESSES
                }
                MY_LIST.append(msg)
                #print(f"Vou começar a mandar os palpites: {MY_LIST}")
                #msg = MY_LIST.pop(0)
                #print(f"Estou enviando a mensgaem: {msg}")
                pass_message(sock, message)
            else:
                pass_message(sock, message)
        elif message['type'] == "inform_guesses":
            print("Palpites: ")
            for i in range(len(message['data'])):
                print(f"Jogaor {i+1}: {message['data'][i]}")
            # Prepara as mensagens solicitando que façam um movimento
            for i in range(1,4):
                msg = {
                    "type":"make_move",
                    "from_player": MY_ID,
                    "to_player": (MY_ID+i)%4, # Isso possibilita a universalização do carteador
                    "data": GUESSES
                }
                MY_LIST.append(msg)
            msg = {
                "type":"make_move",
                "from_player": MY_ID,
                "to_player": MY_ID, 
                "data": GUESSES
            }
            MY_LIST.append(msg)
            print(f"Mensagens a serem enviadas: {MY_LIST}")
            a = input("Chegou até aqui!")
    elif TOKEN == True or (message["type"] == "token" and message["to_player"] == MY_ID):
        TOKEN = True
        print(f"[DEBUG]Recebi/estou_com o token!.")
                
        if len(MY_LIST) > 0:
            msg = MY_LIST.pop(0)
            print(f"[DEBUG] Enviando mensagem: {msg}")
            send_message(sock, msg, NEXT_IP, NEXT_PORT)
        else:
            TOKEN = False
            msg = {
                "type": "token",
                "from_player": MY_ID,
                "to_player": NEXT_ID,
                "data": []
            }
            print(f"[DEBUG] Paasando bastão: {msg}")
            send_message(sock, msg, NEXT_IP, NEXT_PORT)
    else:
        pass_message(sock, message)

# Função para processar as mensagens do jogador padrão
def normal_player(sock, message):
    global TOKEN, MY_LIST, MY_CARDS
    if TOKEN == True or (message["type"] == "token" and message["to_player"] == MY_ID):
        TOKEN = True
        if len(MY_LIST) > 0:
            msg = MY_LIST.pop(0)
            print(f"[DEBUG] Estou enviando a mensagem: {msg}")
            send_message(sock, msg, NEXT_IP, NEXT_PORT)
        else:
            TOKEN = False
            msg = {
                "type": "token",
                "from_player": MY_ID,
                "to_player": NEXT_ID,
                "data": []
            }
            print(f"[DEBUG] Estou passando o bastao: {msg}")
            send_message(sock, msg, NEXT_IP, NEXT_PORT)
    elif message["to_player"] == MY_ID:
        if message["type"] == "init" and message["to_player"] == MY_ID:
            global DEALER_ID, TABLE_CARD
            DEALER_ID = message["from_player"]
            MY_CARDS = message['data']
            # print(f"[DEBUG] Cartas (total): {MY_CARDS}")    
            TABLE_CARD = MY_CARDS.pop()
            print(f"Manilha: {TABLE_CARD}")
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
            print(f"[DEBUG] Fez o appende de: {msg}")
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
        normal_player(sock, message)

# Função para criar socket UDP
def create_socket(num_player):
    global MY_ID, MY_IP, MY_PORT, NEXT_ID, NEXT_IP, NEXT_PORT
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    MY_ID = num_player-1
    MY_IP = PLAYERS_IPS[MY_ID]
    MY_PORT = PLAYERS_PORTS[MY_ID]
    NEXT_ID = (MY_ID+1)%4
    NEXT_IP = PLAYERS_IPS[NEXT_ID]
    NEXT_PORT = PLAYERS_PORTS[NEXT_ID]
    sock.bind((MY_IP, MY_PORT))
    print(f"[DEBUG] MY_ID: {MY_ID}, MY_IP: {MY_IP}, MY_PORT: {MY_PORT}")
    print(f"[DEBUG] NEXT_ID: {NEXT_ID}, NEXT_IP: {NEXT_IP}, NEXT_PORT: {NEXT_PORT}")
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
    cards = []
    if len(sys.argv) > 1:
      sock = create_socket(int(sys.argv[1]))
      if len(sys.argv) > 2 and sys.argv[2] == 'start':
          init_game(sock)
      receive_message(sock)
    else:
        print("O código espera receber como parâmetro: python3 universal.py <num_jogador> <start>")
        print("Sendo o segundo parãmetro opcional, pois indica quem será o primeiro carteador.")
        sys.exit(1)

if __name__ == "__main__":
    main()
