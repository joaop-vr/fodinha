import socket
import json
import sys
import random

# Configurações da rede
PLAYING = True
SHACKLE = 0
ROUND = 0
TOKEN = False
IS_DEALER = False
DEALER_ID = 0
SHUFFLED_CARDS = []
CARDS = []
MY_LIST = []
MY_CARDS = []
COUNT_WINS = [0, 0, 0, 0]
GUESSES = [None, None, None, None]
MOVES = [0, 0, 0, 0]
PLAYERS_HPS = [7, 7, 7, 7]
PLAYERS_IPS = ["10.254.223.39", "10.254.223.40", "10.254.223.41", "10.254.223.38"]
PLAYERS_PORTS = [5039, 5040, 5041, 5042]
MY_ID = 0
MY_IP = 0
MY_PORT = 0
NEXT_ID = 0
NEXT_IP = 0
NEXT_PORT = 0

# Função de inicialização do jogo
def init_round(sock):
    global TOKEN, MY_LIST, IS_DEALER, ROUND, TABLE_CARD, MY_CARDS

    print("Você é o carteador da rodada!")

    # O carteador é o primeiro a receber um token
    TOKEN = True

    # Contador de rodadas
    ROUND = ROUND + 1

    # Distribui as cartas para os jogadores e armazena em 'player_cards'
    player_cards = distribute_cards()

    # Configurando o jogador que começou o jogo como carteador (dealer)
    IS_DEALER = True

    # Elabora a lista com os IDs dos destinatários da mensagem
    destination = []
    for i in range(1,4):
        destination.append((MY_ID + i) % 4) # Isso possibilita a universalização do carteador

    # Engatilha a mensagem de distribuição de cartas
    msg = {
        "type": "init",
        "broadcast": True,
        "from_player": MY_ID,
        "to_player": destination,  
        "data": player_cards,
        "acks": [0, 0, 0, 0]
    }
    MY_LIST.append(msg)

    # Engatilha a mensagem de solicitação de palpites
    msg = {
        "type": "take_guesses",
        "broadcast": True,
        "from_player": MY_ID,
        "to_player": destination, 
        "data": [0, 0, 0, 0],
        "acks": [0, 0, 0, 0]
    }
    MY_LIST.append(msg)

    # Guardando as cartas do carteador e imprime 
    # as informações iniciais do carteador
    MY_CARDS = player_cards[MY_ID][0]
    print(f"\nRodada: {ROUND}")
    print(f"Manilha: {SHACKLE}")
    print(f"Configuração da partida: {CARDS}")
    print(f"Suas cartas: {MY_CARDS}.")
    
    # Envia a primeira mensagem da lista
    msg = MY_LIST.pop(0)
    
    send_message(sock, msg)

# Função para distribuir cartas
def distribute_cards():
    global ROUND, SHUFFLED_CARDS
    
    suits = ['C', 'O', 'E', 'P']  # Copas, Ouros, Espadas, Paus
    values = ['4', '5', '6', '7', 'Q', 'J', 'K', 'A', '2', '3']
    cards = [value + suit for suit in suits for value in values]
    random.shuffle(cards)
    players_cards = [[] for _ in range(4)]
    
    for i in range(ROUND):  # ROUND == número de cartas sorteadas
        for j in range(4):
            if cards:
                players_cards[j].append(cards.pop())

    # Embaralhando o baralho
    SHUFFLED_CARDS = values[:]
    random.shuffle(SHUFFLED_CARDS)

    # Sorteando a manilha (SHACKLE)
    global SHACKLE
    aux_card = SHUFFLED_CARDS.pop()
    try:
        # Encontra a posição da Manilha
        index = values.index(aux_card)
        # Calcula a posição do próximo elemento, considerando a circularidade
        next_index = (index + 1) % len(values)
        # Remove o próximo elemento
        SHACKLE = values.pop(next_index)
    except ValueError:
        print(f"A Manilha {SHACKLE} não foi encontrada na lista.")
    
    global CARDS
    CARDS = values[:]
    CARDS.append(SHACKLE)  # Coloca a Manilha no extremo direito do "values" de cartas
    
    output = [[] for _ in range(4)]
    for i in range(4):
        output[i].append(players_cards[i])
        output[i].append(SHACKLE)
        output[i].append(CARDS)

    # output[i] = [[cartas sorteadas do player],[Manilha],[Configuração do poder das cartas nessa partida]]
    #print(f"[DEBUG] saida do distribute-cards(): {output}'")
    return output

def print_previous_guesses(guesses):
    print(f"Palpites anteriores:")
    for i in range(len(guesses)):
        print(f"Palpite do Jogador {i+1}: {guesses[i]}") 
    return

def print_guesses(guesses):
    print(f"\nPalpites:")
    for i in range(len(guesses)):
        if guesses[i] != -1:
            print(f"Jogador {i + 1}: {guesses[i]}.")
        else:
            print(f"Jogador {i + 1}: desqualificado.")
    return 

def print_previous_moves(moves):
    #print(f"[DEBUG] previous moves: {moves}")
    first_move = True
    for move in moves:
        if move != 0:
            first_move = False
            break

    if first_move:
        print("\nVocê é o primeiro a jogar. Boa sorte!")
    else:
        aux = []
        for move in moves:
            if move != -1:
                aux.append(move)
        print(f"Cartas já jogadas: {aux}")
    return

def print_moves(moves):
    print(f"\n")
    for move in moves:
        if move != -1:
            print(f"O jogador {move[0]+1} jogou: {move[1]}.")
        else:
            print(f"O jogador {move[0]+1} foi desqualificado.")
    return

def print_round_info(message):
    # Imprime o ganahdor da sub-rodada
    #print(f"[DEBUG] Informações finais da rodada {ROUND}: {message}")
    print(f"\n### Informações da rodada ###")
    winner_index = message[0]
    if winner_index != -1:
        print(f"Ganhador: Jogador {winner_index+1}!")
    else:
        print("Ganhador: não houve ganhador nessa sub-rodada!")

    if len(message[1]) > 0:
        print(f"Jogadores eliminados: {message[1]}")
    return

# Atualiza as suas vidas
def update_HP(message):
    global PLAYERS_HPS, MY_ID
    print(f"[DEBUG] PLAYERS_HPS[{MY_ID}] no inicio da rodada: {PLAYERS_HPS[MY_ID]}")
    PLAYERS_HPS[MY_ID] = message["data"][2][MY_ID]
    print(f"[DEBUG] PLAYERS_HPS[{MY_ID}] dps da rodada: {PLAYERS_HPS[MY_ID]}")
    print(f"HP: {PLAYERS_HPS[MY_ID]}")

def check_players_alive():
    global PLAYERS_HPS
    players_alive = []
    for i in range(len(PLAYERS_HPS)):
        if PLAYERS_HPS[i] > 0:
            players_alive.append(i)
    return players_alive

# Função para o usuário informar o palpite
def take_guess(count_guesses=0):
    #print(f"[DEBUG] MY_CARDS: {MY_CARDS}")
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

def make_move():
    global MY_CARDS, MY_ID
    print(f"\nSuas cartas: {MY_CARDS}")
    response = input("Informe sua jogada: ")
    if response == "^[[B" and len(MY_CARDS) == 1:
        response = MY_CARDS.pop()
    else:
        response.upper()
        while response not in MY_CARDS:
            response = input("Ops! Sua resposta não foi interpretada como uma carta que você possue, tente novamente: ")
        MY_CARDS.remove(response)
    return (MY_ID, response)

def count_points():
    global SHACKLE, MOVES
    print(f"[DEBUG] dentro da função count_points: MOVES: {MOVES}")
    
    suits = ['O', 'E', 'C', 'P']
    index_players = []
    same_value = []
    same_value_shackle = []

    MOVES = sorted(MOVES, key=lambda x: x[0])
    print(f"MOVES dps da ordenação: {MOVES}")
    
    # Obter os índices das cartas nos movimentos
    for move in MOVES:
        index_players.append(CARDS.index(move[1][0]))
    
    print(f"[DEBUG] index_players: {index_players}")
    
    # Elimina os valores repetidos doferentes da Manilha
    for i in range(len(index_players)):
        current_value = index_players[i]
        same_value = []
        for j in range(i + 1, len(index_players)):
            if current_value == index_players[j]:
                if current_value != CARDS.index(SHACKLE):
                    same_value.append(i)
                    same_value.append(j)
                else:
                    same_value_shackle.append(i)
                    same_value_shackle.append(j)
    
        for j in same_value:
            index_players[j] = -1
    
    print(f"[DEBUG] antes index_players: {index_players}")
    
    # Ajustar índices dos movimentos SHACKLE com o valor do naipe
    final_points = index_players[:]
    for index in same_value_shackle:
        final_points[index] = final_points[index] + suits.index(MOVES[index][1][1]) 
    
    print(f"[DEBUG] deppis index_players: {index_players}")
    print(f"[DEBUG] final_points: {final_points}")
    print(f"[DEBUG] same_value_shackle: {same_value_shackle}")

    sum = 0
    for i in final_points:
        sum += i

    if sum == -4:
        print(f"[DEBUG] Houve 2 enbuxadas consecutivas! Portanto, ninguém ganhou essa rodada.")
        return -1
    else:
        max_value = max(final_points)
        index_winner = final_points.index(max_value)
        global COUNT_WINS
        COUNT_WINS[index_winner] += 1
        print(f"[DEBUG] Quem ganhou a rodada {ROUND} foi o jogador {index_winner}+1")
        return index_winner

def reset_vars():
    global SHACKLE, DEALER_ID, CARDS, COUNT_WINS, GUESSES, MOVES
    SHACKLE = 0
    DEALER_ID = 0
    CARDS = []
    COUNT_WINS = [0, 0, 0, 0]
    GUESSES = [None, None, None, None]
    MOVES = [None, None, None, None]
    return 
    
def finish_round():
    # Contabiliza o vencedor, se não houve vencedor ent recebe -1
    index_winner = count_points()
    
    # Subtrai elemento por elemento
    final_points = [guess - win for guess, win in zip(GUESSES, COUNT_WINS)]
    
    # Atualiza os pontos negativos diretamente na lista
    final_points = [-point if point > 0 else point for point in final_points]

    # Contabiliza quais foram os jogadores que 'morreram' nessa rodada
    global PLAYERS_HPS
    old_players_hp = PLAYERS_HPS[:]
    new_dead_players = []
    for i in range(len(PLAYERS_HPS)):
        PLAYERS_HPS[i] = PLAYERS_HPS[i] + final_points[i]
        if old_players_hp[i] > 0 and PLAYERS_HPS[i] <= 0 :
            new_dead_players.append(i)

    print(f"[DEBUG] Estou dentro da função finish_round()")
    print(f"[DEBUG] GUESSES: {GUESSES}")
    print(f"[DEBUG] COUNT_WINS: {COUNT_WINS}")
    print(f"[DEBUG] final_points: {final_points}")
    
    return [index_winner, new_dead_players, PLAYERS_HPS]

# Função para processar as mensagens do dealer
def dealer(sock, message):
     if message["from_player"] == MY_ID:

         # Verifica se todos responderam ACK
         error = False
         for i in range(len(message["acks"])):
             if message["acks"][i] == 0 and i != MY_ID:
                 error = True
                 break
                 
         if error:
             index = message["acks"].index(0)
             print(f"Houve um erro! O Jogador {index+1} não retornou ACK.")
             print("Mensagem sendo reenviada...")
             send_message(sock, message)
         else:
             # Elabora a lista com os IDs dos destinatários da mensagem
             destination = []
             for i in range(1,4):
                 destination.append((MY_ID + i) % 4) # Isso possibilita a universalização do carteador
             if message["type"] == "take_guesses":
                 global GUESSES, PLAYERS_HPS
                 GUESSES = message["data"]
                 if PLAYERS_HPS[MY_ID] > 0:
                     sum_guesses = 0
                     for guess in message["data"]:
                        sum_guesses += guess
                     guess = take_guess(sum_guesses)
                     GUESSES[MY_ID] = guess
                 else:
                     GUESSES[MY_ID] = -1
                 msg = {
                    "type": "informing_guesses",
                    "broadcast": True,
                    "from_player": MY_ID,
                    "to_player": destination, 
                    "data": GUESSES,
                    "acks": [0, 0, 0, 0]
                 }
                 MY_LIST.append(msg)
                 #print(f"[DEBUG] Fez o appende de: {msg}")
             elif message["type"] == "informing_guesses":
                 print_guesses(message["data"])
                 msg = {
                    "type": "make_move",
                    "broadcast": True,
                    "from_player": MY_ID,
                    "to_player": destination, 
                    "data": [],
                    "acks": [0, 0, 0, 0]
                 }
                 MY_LIST.append(msg)
                 #print(f"[DEBUG] Fez o appende de: {msg}")
             elif message["type"] == "make_move":
                 global MOVES
                 MOVES = message["data"]
                 if PLAYERS_HPS[MY_ID] > 0:
                     print_previous_moves(message["data"])
                     move = make_move()
                     MOVES.append(move)
                 else:
                     MOVES.append(-1)
                 msg = {
                    "type": "informing_moves",
                    "broadcast": True,
                    "from_player": MY_ID,
                    "to_player": destination, 
                    "data": MOVES,
                    "acks": [0, 0, 0, 0]
                 }
                 MY_LIST.append(msg)
                 #print(f"[DEBUG] Fez o appende de: {msg}")
             elif message["type"] == "informing_moves":
                 print_moves(message["data"])
                 round_info = finish_round()
                 msg = {
                    "type": "round_info",
                    "broadcast": True,
                    "from_player": MY_ID,
                    "to_player": destination, 
                    "data": round_info,
                    "acks": [0, 0, 0, 0]
                 }
                 MY_LIST.append(msg)
                 #print(f"[DEBUG] Fez o appende de: {msg}")
             elif message["type"] == "round_info":
                 print_round_info(message["data"])
                 if len(MY_CARDS) == 0:
                    print(f"[DEBUG] Vai atualizar o HP")
                    update_HP(message)
                 players_alive = check_players_alive()
                 if len(players_alive) <= 1:
                     msg = {
                        "type": "end_game",
                        "broadcast": True,
                        "from_player": MY_ID,
                        "to_player": destination, 
                        "data": players_alive,
                        "acks": [0, 0, 0, 0]
                     }
                     MY_LIST.append(msg)
                 else:
                     if len(MY_CARDS) > 0:
                         msg = {
                            "type": "make_move",
                            "broadcast": True,
                            "from_player": MY_ID,
                            "to_player": destination, 
                            "data": [],
                            "acks": [0, 0, 0, 0]
                         }
                         MY_LIST.append(msg)
                     else:
                         msg = {
                            "type": "reset_vars",
                            "broadcast": True,
                            "from_player": MY_ID,
                            "to_player": destination, 
                            "data": [],
                            "acks": [0, 0, 0, 0]
                         }
                         MY_LIST.append(msg)
             elif message["type"] == "reset_vars":
                 dealer_info = [ROUND, PLAYERS_HPS]
                 reset_vars()
                 IS_DEALER = False
                 msg = {
                    "type": "dealer_token",
                    "broadcast": False,
                    "from_player": MY_ID,
                    "to_player": NEXT_ID, 
                    "data": dealer_info,
                 }
                 MY_LIST.append(msg)
                 print(f"Você não é mais o carteador.")
     
             elif message["type"] == "end_game":
                print(f"O último jogador que se manteve de pé foi o Jogador {message['data']}")
                global PLAYING
                PLAYING = False
                return

     if len(MY_LIST) > 0:
         msg = MY_LIST.pop(0)
         #print(f"[DEBUG] Estou enviando a mensagem: {msg}")
         send_message(sock, msg)
     else:
         #print(f"[DEBUG] O carteador ficou sem mensagens para enviar.")
         normal_player(sock, message)
         #receive_message(sock)

# Função para processar as mensagens do jogador padrão
def normal_player(sock, message):
    global PLAYERS_HPS, MY_ID, ROUND
    # Recebeu uma mensagem destinada a ele
    if message["broadcast"] == True and MY_ID in message["to_player"]:
        #print(f"Recebi uma mensagem: {message}")
        #a = input(f"\nCheckpoint")
        # Verifica se o jogador está fora do jogo
        if PLAYERS_HPS[MY_ID] <= 0 and message["data"] != "end_game":
            print("Você morreu. Mensagem sendo passada adiante...")
            message["acks"][MY_ID] = -1
            pass_message(sock, message)
        else:
            message["acks"][MY_ID] = 1
            if message["type"] == "init":                   # Setando as variaveis do player no inicio da rodada
                global DEALER_ID, SHACKLE, MY_CARDS, ROUND
                DEALER_ID = message["from_player"]
                # message['data'][MY_ID] := [[cartas sorteadas do player],[Manilha],[Carta mais forte],[Configuração do poder das cartas nessa partida]]
                ##print(f"[DEBUG] message[data]: {message['data']}")
                ##print(f"[DEBUG] aux := {message['data'][MY_ID]}")
                aux = message['data'][MY_ID]
                MY_CARDS = aux[0]
                SHACKLE = aux[1]
                CARDS = aux[2]
                ROUND = len(MY_CARDS)
                print(f"\nRodada: {ROUND}")
                print(f"Manilha: {SHACKLE}")
                print(f"Configuração da partida: {CARDS}")
                print(f"Suas cartas: {MY_CARDS}.")
                pass_message(sock, message)
            elif message["type"] == "take_guesses":         # Faz o palpite
                if PLAYERS_HPS[MY_ID] > 0:
                    guess = take_guess()
                    message["data"][MY_ID] = guess
                else:
                    message["data"][MY_ID] = -1
                pass_message(sock, message)
            elif message["type"] == "informing_guesses":    # Recebe e imprime os palpites de todos
                message["acks"][MY_ID] = 1
                print_guesses(message["data"])
                pass_message(sock, message)
            elif message["type"] == "make_move":            # Faz a jogada
                if PLAYERS_HPS[MY_ID] > 0:
                    print_previous_moves(message["data"])
                    move = make_move()
                    message["data"].append(move)
                else:
                    message["data"].append(-1)
                pass_message(sock, message)
            elif message["type"] == "informing_moves":      # Recebe e imprime as jogadas de todos
                print_moves(message["data"])
                pass_message(sock, message)
            elif message["type"] == "round_info":           # Imprime as informações da rodada que terminou e atualiza HP
                print_round_info(message["data"])
                if len(MY_CARDS) == 0:
                    print(f"[DEBUG] Vai atualizar o HP")
                    update_HP(message)
                pass_message(sock, message)
            elif message["type"] == "reset_vars":           # Reinicia as variaveis globais para poder iniciar uma nova rodada
                reset_vars()
                pass_message(sock, message)
            elif message["type"] == "end_game":
                print(f"\nO último jogador que se manteve de pé foi o Jogador {message['data']}")
                global PLAYING
                PLAYING = False
                pass_message(sock, message)
    elif message["broadcast"] == False and message["to_player"] == MY_ID:
        if message["type"] == "dealer_token":
            global IS_DEALER
            IS_DEALER = True
            ROUND = message["data"][0]
            PLAYERS_HPS = message["data"][1]
            init_round(sock)
            receive_message(sock)
            
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
    MY_ID = num_player - 1
    MY_IP = PLAYERS_IPS[MY_ID]
    MY_PORT = PLAYERS_PORTS[MY_ID]
    NEXT_ID = (MY_ID + 1) % 4
    NEXT_IP = PLAYERS_IPS[NEXT_ID]
    NEXT_PORT = PLAYERS_PORTS[NEXT_ID]
    sock.bind((MY_IP, MY_PORT))
    #print(f"[DEBUG] MY_ID: {MY_ID}, MY_IP: {MY_IP}, MY_PORT: {MY_PORT}")
    #print(f"[DEBUG] NEXT_ID: {NEXT_ID}, NEXT_IP: {NEXT_IP}, NEXT_PORT: {NEXT_PORT}")
    return sock

# Função para enviar mensagem UDP
def send_message(sock, message):
    sock.sendto(json.dumps(message).encode(), (NEXT_IP, NEXT_PORT))

# Função para passar a mensagem adiante
def pass_message(sock, message):
    sock.sendto(json.dumps(message).encode(), (NEXT_IP, NEXT_PORT))

# Função para receber e processar mensagens
def receive_message(sock):
    global PLAYING
    while PLAYING:
        data, addr = sock.recvfrom(1024)
        message = json.loads(data.decode())
        process_message(sock, message)
    print("Obrigado por jogar!")

def main():
    if len(sys.argv) > 1:
        sock = create_socket(int(sys.argv[1]))
        if len(sys.argv) > 2 and sys.argv[2] == 'start':
            init_round(sock)
        receive_message(sock)
    else:
        print("O código espera receber como parâmetro: python3 universal.py <num_jogador> <start>")
        print("Sendo o segundo parâmetro opcional, pois indica quem será o primeiro carteador.")
        sys.exit(1)

if __name__ == "__main__":
    main()
