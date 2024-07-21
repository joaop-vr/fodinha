import socket
import json
import sys
import random

# Configurações da rede
MY_ID = 0
TOKEN = False
CARDS = []
GUESSES = [None, None, None, None]
MY_LIST = []
MY_CARDS = []
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
    global TOKEN, CARDS, MY_LIST

    # O carteador é o primeiro a receber um token
    TOKEN = True

    # Distribui as cartas para os jogadores e armazena em 'cards'
    CARDS = distribute_cards()
    #for i in range(3):

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
    values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
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

# Função para processar mensagens recebidas
def process_message(sock, message):
    global TOKEN, MY_LIST, GUESSES
    if TOKEN == True or (message["type"] == "token" and message["to_player"] == MY_ID):
        TOKEN = True
        print(f"Recebi/estou_com o token!.")
                
        if len(MY_LIST) > 0:
            # Caso que em o Carteador recebeu a própria mensagem de volta
            #if message['from_player'] == MY_ID and message['to_player'] != MY_ID:
            #    idx = None
            #    msg = []
            #    # Distribuição de cartas
            #    if message['type'] == "init":
            #        for i, item in enumerate(MY_LIST):
            #            if item['type'] =="init":
            #                idx = i
            #                break
            #        if idx is not None:
            #            msg = MY_LIST.pop(idx)
            #        else:
            #            print("Todos os jogadores ja receberam suas cartas!")

                # Debug
                #idx = None
                #if message['type'] == "init":
                #    for i, item in enumerate(MY_LIST):
                #         if item['type'] =="init":
                #            idx = i
                #            break
                #    if idx is  None:
                #        print("Todos os joagdores ja receberam suas cartas!")
                #        print(f"Cartas do Carteador: {MY_CARDS}")

                # Requisição dos palpites
             #   elif message['type'] == "take_guesses":
             #       for i, item in enumerate(MY_LIST):
             #           if item['type'] =="take_guesses":
             #               idx = i
             #               break
             #       if idx is not None:
             #           msg = MY_LIST.pop(idx)
             #       else:
             #           print("Já pedi os palpites para todos os jogadores!")
             #           guess = take_guess()
             #           GUESSES[3] = guess
                # Debug
                #idx = None
                #if message['type'] == "take_guesses":
                #    for i, item in enumerate(MY_LIST):
                #         if item['type'] =="take_guesses":
                #            idx = i
                #            break
                #    if idx is None:
                #        print("Já pedi os palpites para todos os jogadores!")
                #        guess = take_guess()
                #        GUESSES[3] = guess

                #send_message(sock, msg, NEXT_IP, NEXT_PORT)
            msg = MY_LIST.pop(0)
            print(f"Enviando mensagem: {msg}")
            send_message(sock, msg, NEXT_IP, NEXT_PORT)
        else:
            TOKEN = False
            msg = {
                "type": "token",
                "from_player": MY_ID,
                "to_player": 1,
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
            if message['from_player'] == 3:
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
                #send_message(sock, msg, NEXT_IP, NEXT_PORT)
                pass_message(sock, message)
            else:
                pass_message(sock, message)
        elif message['inform_guesses']:
            print("Palpites: ")
            for i in range(len(message['data'])):
                print(f"Jogaor {i+1}: {message['data'][i]}")
    else:
        pass_message(sock, message)


        #if message["type"] == "init":
        #    if message["to_player"] != 3:
        #        msg = {
        #            "type": "init",
        #            "from_player": MY_ID,
        #            "to_player": message["to_player"]+1,
        #            "data": CARDS[message["to_player"]] # A lista começa com indice 0
        #        }   
        #        send_message(sock, msg, NEXT_IP, NEXT_PORT)
        #    else:
        #        print(f"Todos os jogadores receberam suas cartas!")
        #        print(f"Vou pedir para que mandem seus palpites.")
        #        for i in range(1,3):
        #            msg = {
        #                "type": "take_guesses",
        #                "from_player": MY_ID,
        #                "to_player": i,
        #                "data": []
        #            }
        #            MY_LIST.append(msg)
        #            #print(f"vai pedir o palpite do jogador {msg['to_player']}")
        #        send_message(sock, msg, NEXT_IP, NEXT_PORT)
        #elif message["type"] == "take_guesses":
        #    #global GUESSES
        #    #GUESSES.append(message["data"])
        #    #print(f"Guesses guardados: {GUESSES}")
        #    #print(f"tamo no 'take_guesses', mensagem: {message}")
        #    if message["to_player"]+1 != 4:
        #        msg = {
        #            "type": "take_guesses",
        #            "from_player": MY_ID,
        #            "to_player": message["to_player"]+1,
        #            "data": []
        #        }
        #        #print(f"AQUI  {msg}")
        #        send_message(sock, msg, NEXT_IP, NEXT_PORT)
        #    else:
        #        print(f"Todos os jogadores já receberam as mensagens de solicitação de palpite, agora é preciso passar o bastão.")
        #        TOKEN = False
        #        msg = {
        #            "type": "token",
        #            "from_player": MY_ID,
        #            "to_player": 1,
        #            "data": []
        #        }
        #        print(f"Passei o bastao: {msg}")
        #        send_message(sock, msg, NEXT_IP, NEXT_PORT)
        #        # DEIXOU O (MY) TOKEN FALSO E PASSOU O TOKEN ADIANTE
        ##elif len(GUESSES) == 3:
        ##    print(f"Peguei todos os palpites: {GUESSES}")
        ##    msg = {
        ##        "type":"inform_guesses",
        ##        "from_player": MY_ID,
        ##        "to_player": 
        ##    }
        #elif message['type'] == "end_guesses":
        #    msg = {
        #        "type": "inform_guesses",
        #        "from_player": MY_ID,
        #        "to_player": 1,
        #        "data": GUESSES
        #        }
        #    print(f"Vou começar a informar sobre os palpites")
        #    send_message(sock, msg, NEXT_IP, NEXT_PORT)

        #elif message['type'] == "inform_guesses":
        #    if message['to-player'] != 3:
        #        message['to_player'] = message['to_player']+1
        #        send_message(sock, message, NEXT_IP, NEXT_PORT)
        #    else:
        #        print(f"Todos foram informados dos palpites, podemos começar a jogar!")
    #elif message["to_player"] == MY_ID:
    #    print(f"Recebi uma mensagem! (To be implementado...)")
    #    if message["type"] == "receive_guesses" or message["type"] == "end_guesses":
    #        if len(GUESSES) < 3:
    #            GUESSES.append(message["data"])
    #            print(f"Recebi o seguinte palpite: {message['data']}")
    #            pass_message(sock, message)
    #else:
    #    pass_message(sock, message)

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
    cards = []
    if len(sys.argv) > 1 and sys.argv[1] == 'start':
        init_game(sock)
    receive_message(sock)

if __name__ == "__main__":
    main()
