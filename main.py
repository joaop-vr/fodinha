import socket
import json
import sys
import random

# Configurações da rede
PLAYING = True
SHACKLE = 0
ROUND = 0
SUB_ROUND = 0
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
#i31 i32 i33 i34
PLAYERS_IPS = ["10.254.224.58", "10.254.224.59", "10.254.224.60", "10.254.224.61"]
PLAYERS_PORTS = [5039, 5040, 5041, 5042]
MY_ID = 0
MY_IP = 0
MY_PORT = 0
NEXT_ID = 0
NEXT_IP = 0
NEXT_PORT = 0

# Função de inicialização do jogo
def init_round(sock):
    global IS_DEALER, ROUND, SUB_ROUND

    # Contador de rodadas
    ROUND = ROUND + 1
    SUB_ROUND = 0

    # Configurando o jogador que começou o jogo como carteador (dealer)
    IS_DEALER = True

    # Elabora a lista com os IDs dos destinatários da mensagem
    destination = []
    for i in range(1,4):
        destination.append((MY_ID + i) % 4) # Isso possibilita a universalização do carteador

    # Engatilha a mensagem de distribuição de cartas
    msg = {
        "type": "informing_dealer",
        "broadcast": True,
        "from_player": MY_ID,
        "to_player": destination,  
            "data": [],
        "acks": [0, 0, 0, 0]
    }
    
    # Envia a primeira mensagem da lista
    send_message(sock, msg)

# Função para distribuir cartas
def distribute_cards():
    global ROUND, SHUFFLED_CARDS, SHACKLE, CARDS
    
    suits = ['C', 'O', 'E', 'P']  # Copas, Ouros, Espadas, Paus
    values = ['4', '5', '6', '7', 'Q', 'J', 'K', 'A', '2', '3']
    cards = [value + suit for suit in suits for value in values]
    random.shuffle(cards)
    players_cards = [[] for _ in range(4)]
    
    for i in range(ROUND):  # ROUND == número de cartas sorteadas
        for j in range(4):
            if cards:
                players_cards[j].append(cards.pop())


    # Sorteando a manilha (SHACKLE)
    aux_card = cards.pop()[0]
  
    try:
        # Encontra a posição da Manilha
        index = values.index(aux_card)
        # Calcula a posição do próximo elemento, considerando a circularidade
        next_index = (index + 1) % len(values)
        # Remove o próximo elemento
        SHACKLE = values.pop(next_index)
    except ValueError:
        print(f"A Manilha {SHACKLE} não foi encontrada na lista.")

    # Configuração do poder das cartas
    CARDS = values[:]
    CARDS.append(SHACKLE)  # Coloca a Manilha no extremo direito do "values" de cartas
    
    output = [[] for _ in range(4)]
    for i in range(4):
        output[i].append(players_cards[i])
        output[i].append(SHACKLE)
        output[i].append(CARDS)

    # output[i] = [[cartas sorteadas do player],[Manilha],[Configuração do poder das cartas nessa partida]]
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
        print(f"\nCartas já jogadas: {aux}")
    return

def print_moves(moves):
    print(f"\n")
    for move in moves:
        if move[0] != -1:
            print(f"O jogador {move[0]+1} jogou: {move[1]}.")
        else:
            print(f"O jogador {move[0]+1} foi desqualificado.")
    return

def print_round_info(message):
    # Imprime o ganahdor da sub-rodada
    print(f"\n### Informações da rodada ###")
    winner_index = message[0]
    if winner_index != -1:
        print(f"Ganhador: Jogador {winner_index+1}!")
    else:
        print("Ganhador: não houve ganhador nessa sub-rodada!")

    if len(message[1]) > 0:
        dead_players = [player + 1 for player in message[1]]
        print(f"Jogadores eliminados: {dead_players}")
    return

def print_dealer(message):
    print(f"O Carteador dessa rodada é o Jogador {message['from_player']+1}!")
    return
    
# Atualiza as suas vidas
def update_HP(message):
    global PLAYERS_HPS, MY_ID
    PLAYERS_HPS[MY_ID] = message["data"][2][MY_ID]
    print(f"HP: {PLAYERS_HPS[MY_ID]}")
    return

def check_players_alive():
    global PLAYERS_HPS
    players_alive = []
    for i in range(len(PLAYERS_HPS)):
        if PLAYERS_HPS[i] > 0:
            players_alive.append(i)
    return players_alive

# Função para o usuário informar o palpite
def take_guess(count_guesses=-12):
    global PLAYERS_HPS, MY_ID
    guess = 0
    if PLAYERS_HPS[MY_ID] > 0:
        while True:
            try:
                guess = int(input("Informe o seu palpite: "))
                if guess > len(MY_CARDS) or guess < 0:
                    raise ValueError("Não é possível dar um palpite maior que o número de cartas que possui ou menor que zero.")
                break
            except ValueError as e:
                print(f"Entrada inválida: {e}. Tente novamente.")

        # Verifica se o palpite é maior que o número de cartas que possui
        while guess > len(MY_CARDS) or guess < 0:
            print("Não é possível dar um palpite maior que o número de cartas que possui ou menor que zero.")
            guess = int(input("Dê outro palpite: "))

        # Verifica se a soma dos palpites é igual ao número de rodadas
        if count_guesses != -12:
            while count_guesses + guess == ROUND:
                print(f"A soma dos palpites deve ser diferente de {ROUND}.")
                guess = int(input("Dê outro palpite: "))
                while guess > len(MY_CARDS) or guess < 0:
                    print("Não é possível dar um palpite maior que o número de cartas que possui ou menor que zero.")
                    guess = int(input("Dê outro palpite: "))
    else:
        guess = -1
    return guess

def make_move():
    global MY_CARDS, MY_ID, PLAYERS_HPS, SUB_ROUND
    SUB_ROUND += 1
    response = 0
    if PLAYERS_HPS[MY_ID] > 0:
        print(f"Suas cartas: {MY_CARDS}")
        response = input("Informe sua jogada: ")
        if response == "-":
            response = MY_CARDS.pop()
        else:
            response.upper()
            while response not in MY_CARDS:
                response = input("Ops! Sua resposta não foi interpretada como uma carta que você possue, tente novamente: ")
            MY_CARDS.remove(response)
    else:
        response = [-1]
        print("Você morreu. Mensagem sendo passada adiante...")
    return (MY_ID, response)

def count_points():
    global SHACKLE, MOVES, COUNT_WINS
    
    suits = ['O', 'E', 'C', 'P']
    index_players = []
    same_value = []
    same_value_shackle = []

    MOVES = sorted(MOVES, key=lambda x: x[0])
    
    # Obter os índices das cartas nos movimentos
    for move in MOVES:
        try:
            card_index = CARDS.index(move[1][0])
        except ValueError:
            card_index = -1 # O jogador morreu, então a carta jogada (-1) não está no paralho
        index_players.append(card_index)
    
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
    
    # Ajustar índices dos movimentos SHACKLE com o valor do naipe
    final_points = index_players[:]
    for index in same_value_shackle:
        final_points[index] = final_points[index] + suits.index(MOVES[index][1][1]) 

    sum = 0
    for i in final_points:
        sum += i

    if sum == -4:
        return -1
    else:
        max_value = max(final_points)
        index_winner = final_points.index(max_value)
        COUNT_WINS[index_winner] += 1
        return index_winner

def reset_vars():
    global SHACKLE, DEALER_ID, CARDS, MY_CARDS, COUNT_WINS, GUESSES, MOVES
    SHACKLE = 0
    DEALER_ID = 0
    CARDS = []
    MY_CARDS = []
    COUNT_WINS = [0, 0, 0, 0]
    GUESSES = [None, None, None, None]
    MOVES = [None, None, None, None]
    return 
    
def finish_round():
    global PLAYERS_HPS
    
    # Subtrai elemento por elemento
    final_points = [guess - win for guess, win in zip(GUESSES, COUNT_WINS)]
    
    # Atualiza os pontos negativos diretamente na lista
    final_points = [-point if point > 0 else point for point in final_points]

    # Contabiliza quais foram os jogadores que 'morreram' nessa rodada
    old_players_hp = PLAYERS_HPS[:]
    new_dead_players = []
    for i in range(len(PLAYERS_HPS)):
        PLAYERS_HPS[i] = PLAYERS_HPS[i] + final_points[i]
        if old_players_hp[i] > 0 and PLAYERS_HPS[i] <= 0 :
            new_dead_players.append(i)

    # Reseta o contador de vitórias
    for count in COUNT_WINS:
        count = 0
    
    #return [index_winner, new_dead_players, PLAYERS_HPS]
    return [new_dead_players, PLAYERS_HPS]

# Função para processar as mensagens do dealer
def dealer(sock, message):
     global MY_CARDS, GUESSES, MOVES, IS_DEALER, PLAYING, ROUND, SUB_ROUND
     # A mensagem do dealer deu a volta na rede e chegou nele
     msg = {}
     if message["from_player"] == MY_ID:

         # Verifica se todos responderam ACK
         error = False
         for i in range(len(message["acks"])):
             if len(message["acks"]) == 1 and message["acks"][0] == 0: # Bastão foi perdido
                 error = True
             elif message["acks"][i] == 0 and i != MY_ID: # Alguem nao respondeu ACK 1
                 error = True
                 break

         # Se alguém não respondem ACK a mensagem é reenviada para esse(s) jogador(es)
         if error:
             index_players = []
             for i in range(len(message["acks"])):
               if message["acks"][i] == 0:
                 index_players.append(i)
             print(f"Houve um erro! O(s) Jogador(es) {index+1} não retornou/retornaram ACK.")
             print("Mensagem sendo reenviada...")
             message["broadcast"] = False
             message["to_player"] = index_players
             send_message(sock, message)
         else:
             # Elabora a lista com os IDs dos destinatários da mensagem
             destination = []
             for i in range(1,4):
                 destination.append((MY_ID + i) % 4) # Isso possibilita a universalização do carteador
             # Desenvolve os estados do jogo
             msg = {}
             if message["type"] == "informing_dealer":
                 # Distribui as cartas para os jogadores e armazena em 'player_cards'
                 print("Você é o carteador desta rodada!")
                 player_cards = distribute_cards()
                 msg = {
                    "type": "init",
                    "broadcast": True,
                    "from_player": MY_ID,
                    "to_player": destination,  
                    "data": player_cards,
                    "acks": [0, 0, 0, 0]
                 }
             elif message["type"] == "init":
                 if PLAYERS_HPS[MY_ID] > 0:
                    MY_CARDS = message["data"][MY_ID][0]
                    print(f"\nRodada: {ROUND}")
                    print(f"Manilha: {SHACKLE}")
                    print(f"Configuração da partida: {CARDS}")
                    print(f"Suas cartas: {MY_CARDS}.")
                 else:
                     print(f"Você ficou sem vidas.. está como dealer espectador.")
                 msg = {
                    "type": "take_guesses",
                    "broadcast": True,
                    "from_player": MY_ID,
                    "to_player": destination, 
                    "data": [0, 0, 0, 0],
                    "acks": [0, 0, 0, 0]
                }
             elif message["type"] == "take_guesses":
                 GUESSES = message["data"]
                 sum_guesses = 0
                 for guess in message["data"]:
                     if guess != -1:
                         sum_guesses += guess
                 guess = take_guess(sum_guesses)
                 GUESSES[MY_ID] = guess
                 msg = {
                    "type": "informing_guesses",
                    "broadcast": True,
                    "from_player": MY_ID,
                    "to_player": destination, 
                    "data": GUESSES,
                    "acks": [0, 0, 0, 0]
                 }
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
             elif message["type"] == "make_move":
                 MOVES = message["data"]
                 print_previous_moves(message["data"])
                 move = make_move()
                 MOVES.append(move)
                 msg = {
                    "type": "informing_moves",
                    "broadcast": True,
                    "from_player": MY_ID,
                    "to_player": destination, 
                    "data": MOVES,
                    "acks": [0, 0, 0, 0]
                 }
             elif message["type"] == "informing_moves":
                 print_moves(message["data"])
                 # Inicializa a lista round_info com três elementos (jogador da rodada, jogadores eliminados, HP dos jogadores)
                 round_info = [0, [], []] 
                 # Contabiliza o vencedor, se não houve vencedor ent recebe -1
                 index_winner = count_points()
                 round_info[0] = index_winner  # Armazena o índice do vencedor

                 # Adiciona as informações dos jogadores que morreram e HP dos players
                 if SUB_ROUND == ROUND:
                     aux = finish_round()
                     round_info[1] = aux[0]  # Lista de jogadores que morreram
                     round_info[2] = aux[1]  # Lista de HPs dos jogadores

                 msg = {
                    "type": "round_info",
                    "broadcast": True,
                    "from_player": MY_ID,
                    "to_player": destination, 
                    "data": round_info,
                    "acks": [0, 0, 0, 0]
                 }
             elif message["type"] == "round_info":
                 print_round_info(message["data"])
                 if SUB_ROUND == ROUND:
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
                 else:
                     if SUB_ROUND != ROUND:
                         msg = {
                            "type": "make_move",
                            "broadcast": True,
                            "from_player": MY_ID,
                            "to_player": destination, 
                            "data": [],
                            "acks": [0, 0, 0, 0]
                         }
                     else:
                         msg = {
                            "type": "reset_vars",
                            "broadcast": True,
                            "from_player": MY_ID,
                            "to_player": destination, 
                            "data": [],
                            "acks": [0, 0, 0, 0]
                         }
             elif message["type"] == "reset_vars":
                 reset_vars()
                 dealer_info = [ROUND, PLAYERS_HPS]
                 msg = {
                    "type": "dealer_token",
                    "broadcast": False,
                    "from_player": MY_ID,
                    "to_player": NEXT_ID, 
                    "data": dealer_info,
                    "acks": [0]
                 }
                 print(f"Você não é mais o carteador.")
             elif message["type"] == "dealer_token":
                 IS_DEALER = False
             elif message["type"] == "end_game":
                 if len(message["data"]) != 0:
                    print(f"\nO último jogador que se manteve de pé foi o Jogador {message['data'][0] + 1}")
                 else:
                    print(f"\nHouve empate! A verdadeira vitória são os amigos que fizemos no caminho...")
                 PLAYING = False
                 return
    
     if IS_DEALER:
         send_message(sock, msg)
     else:
         receive_message(sock)

# Função para processar as mensagens do jogador padrão
def normal_player(sock, message):
    global PLAYERS_HPS, MY_ID, DEALER_ID, SHACKLE, MY_CARDS, ROUND, PLAYING, ROUND
    # Recebeu uma mensagem destinada a ele
    if message["broadcast"] == True and MY_ID in message["to_player"]:
        if PLAYERS_HPS[MY_ID] <= 0:
            message["acks"][MY_ID] = -1
        else:
            message["acks"][MY_ID] = 1
        if message["type"] == "informing_dealer":
            DEALER_ID = message["from_player"]
            print_dealer(message)
            #send_message(sock, message)
        elif message["type"] == "init":                   # Setando as variaveis do player no inicio da rodada
            aux = message['data'][MY_ID]
            MY_CARDS = aux[0]
            SHACKLE = aux[1]
            CARDS = aux[2]
            ROUND = len(MY_CARDS)
            if PLAYERS_HPS[MY_ID] > 0:
                print(f"\nRodada: {ROUND}")
                print(f"Manilha: {SHACKLE}")
                print(f"Configuração da partida: {CARDS}")
                print(f"Suas cartas: {MY_CARDS}.")
            else:
                print(f"Você ficou sem vidas.. está como dealer espectador.")
        elif message["type"] == "take_guesses":         # Faz o palpite
            guess = take_guess()
            message["data"][MY_ID] = guess
        elif message["type"] == "informing_guesses":    # Recebe e imprime os palpites de todos
            print_guesses(message["data"])
        elif message["type"] == "make_move":            # Faz a jogada
            print_previous_moves(message["data"])
            move = make_move()
            message["data"].append(move)
        elif message["type"] == "informing_moves":      # Recebe e imprime as jogadas de todos
            print_moves(message["data"])
        elif message["type"] == "round_info":           # Imprime as informações da rodada que terminou e atualiza HP
            print_round_info(message["data"])
            if len(MY_CARDS) == 0:
                update_HP(message)
        elif message["type"] == "reset_vars":           # Reinicia as variaveis globais para poder iniciar uma nova rodada
            reset_vars()
        elif message["type"] == "end_game":
            if len(message["data"]) != 0:
                print(f"\nO último jogador que se manteve de pé foi o Jogador {message['data'][0] + 1}")
            else:
                print(f"\nHouve empate! A verdadeira vitória são os amigos que fizemos no caminho...")
            PLAYING = False
        send_message(sock, message)
    elif message["broadcast"] == False and message["to_player"] == MY_ID:
        if message["type"] == "dealer_token":
            ROUND = message["data"][0]
            PLAYERS_HPS = message["data"][1]
            message["acks"][0] = 1
            send_message(sock, message)
            init_round(sock)
            receive_message(sock)
            return
    else:
        send_message(sock, message)

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
