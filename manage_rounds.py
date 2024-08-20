# Função de inicialização do jogo
def init_round(sock):
    #global IS_DEALER, ROUND, SUB_ROUND

    # Contador de rodadas
    global_vars.ROUND = global_vars.ROUND + 1
    global_vars.SUB_ROUND = 0

    # Configurando o jogador que começou o jogo como carteador (dealer)
    global_vars.IS_DEALER = True

    # Elabora a lista com os IDs dos destinatários da mensagem
    destination = []
    for i in range(1,4):
        destination.append((global_vars.MY_ID + i) % 4) # Isso possibilita a universalização do carteador

    # Engatilha a mensagem de distribuição de cartas
    msg = {
        "type": "informing_dealer",
        "broadcast": True,
        "from_player": global_vars.MY_ID,
        "to_player": destination,  
            "data": [],
        "acks": [0, 0, 0, 0]
    }
    
    # Envia a primeira mensagem da lista
    send_message(sock, msg)

# Função para distribuir cartas
def distribute_cards():
    #global ROUND, SHUFFLED_CARDS, SHACKLE, CARDS
    
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
        global_vars.SHACKLE = values.pop(next_index)
    except ValueError:
        print(f"A Manilha {global_vars.SHACKLE} não foi encontrada na lista.")

    # Configuração do poder das cartas
    global_vars.CARDS = values[:]
    global_vars.ARDS.append(global_vars.SHACKLE)  # Coloca a Manilha no extremo direito do "values" de cartas
    
    output = [[] for _ in range(4)]
    for i in range(4):
        output[i].append(players_cards[i])
        output[i].append(global_vars.SHACKLE)
        output[i].append(global_vars.CARDS)

    # output[i] = [[cartas sorteadas do player],[Manilha],[Configuração do poder das cartas nessa partida]]
    return output
    
# Atualiza as suas vidas
def update_HP(message):
    #global PLAYERS_HPS, MY_ID
    global_vars.PLAYERS_HPS[global_vars.MY_ID] = message["data"][2]global_vars.[global_vars.MY_ID]
    print(f"HP: {global_vars.PLAYERS_HPS[global_vars.MY_ID]}")
    return

def check_players_alive():
    #global PLAYERS_HPS
    players_alive = []
    for i in range(len(global_vars.PLAYERS_HPS)):
        if global_vars.PLAYERS_HPS[i] > 0:
            players_alive.append(i)
    return players_alive

# Função para o usuário informar o palpite
def take_guess(count_guesses=-12):
    #global PLAYERS_HPS, MY_ID
    guess = 0
    if global_vars.PLAYERS_HPS[global_vars.MY_ID] > 0:
        while True:
            try:
                guess = int(input("Informe o seu palpite: "))
                if guess > len(global_vars.MY_CARDS) or guess < 0:
                    raise ValueError("Não é possível dar um palpite maior que o número de cartas que possui ou menor que zero.")
                break
            except ValueError as e:
                print(f"Entrada inválida: {e}. Tente novamente.")

        # Verifica se o palpite é maior que o número de cartas que possui
        while guess > len(global_vars.MY_CARDS) or guess < 0:
            print("Não é possível dar um palpite maior que o número de cartas que possui ou menor que zero.")
            guess = int(input("Dê outro palpite: "))

        # Verifica se a soma dos palpites é igual ao número de rodadas
        if count_guesses != -12:
            while count_guesses + guess == global_vars.ROUND:
                print(f"A soma dos palpites deve ser diferente de {global_vars.ROUND}.")
                guess = int(input("Dê outro palpite: "))
                while guess > len(global_vars.MY_CARDS) or guess < 0:
                    print("Não é possível dar um palpite maior que o número de cartas que possui ou menor que zero.")
                    guess = int(input("Dê outro palpite: "))
    else:
        guess = -1
    return guess

def make_move():
    #global MY_CARDS, MY_ID, PLAYERS_HPS, SUB_ROUND
    global_vars.SUB_ROUND += 1
    response = 0
    if global_vars.PLAYERS_HPS[global_vars.MY_ID] > 0:
        print(f"Suas cartas: {global_vars.MY_CARDS}")
        response = input("Informe sua jogada: ")
        if response == "-":
            response = global_vars.MY_CARDS.pop()
        else:
            response.upper()
            while response not in global_vars.MY_CARDS:
                response = input("Ops! Sua resposta não foi interpretada como uma carta que você possue, tente novamente: ")
            global_vars.MY_CARDS.remove(response)
    else:
        response = [-1]
        print("Você morreu. Mensagem sendo passada adiante...")
    return (global_vars.MY_ID, response)

def count_points():
    #global SHACKLE, MOVES, COUNT_WINS
    
    suits = ['O', 'E', 'C', 'P']
    index_players = []
    same_value = []
    same_value_shackle = []

    global_vars.MOVES = sorted(global_vars.MOVES, key=lambda x: x[0])
    
    # Obter os índices das cartas nos movimentos
    for move in global_vars.MOVES:
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
        final_points[index] = final_points[index] + suits.index(global_vars.MOVES[index][1][1]) 

    sum = 0
    for i in final_points:
        sum += i

    if sum == -4:
        return -1
    else:
        max_value = max(final_points)
        index_winner = final_points.index(max_value)
        global_vars.COUNT_WINS[index_winner] += 1
        return index_winner

def reset_vars():
    #global SHACKLE, DEALER_ID, CARDS, MY_CARDS, COUNT_WINS, GUESSES, MOVES
    global_vars.SHACKLE = 0
    global_vars.DEALER_ID = 0
    global_vars.CARDS = []
    global_vars.MY_CARDS = []
    global_vars.COUNT_WINS = [0, 0, 0, 0]
    global_vars.GUESSES = [None, None, None, None]
    global_vars.MOVES = [None, None, None, None]
    return 
    
def finish_round():
    #global PLAYERS_HPS
    
    # Subtrai elemento por elemento
    final_points = [guess - win for guess, win in zip(global_vars.GUESSES, global_vars.COUNT_WINS)]
    
    # Atualiza os pontos negativos diretamente na lista
    final_points = [-point if point > 0 else point for point in final_points]

    # Contabiliza quais foram os jogadores que 'morreram' nessa rodada
    old_players_hp = global_vars.PLAYERS_HPS[:]
    new_dead_players = []
    for i in range(len(global_vars.PLAYERS_HPS)):
        global_vars.PLAYERS_HPS[i] = global_vars.PLAYERS_HPS[i] + final_points[i]
        if old_players_hp[i] > 0 and global_vars.PLAYERS_HPS[i] <= 0 :
            new_dead_players.append(i)

    # Reseta o contador de vitórias
    for count in global_vars.COUNT_WINS:
        count = 0
    
    #return [index_winner, new_dead_players, PLAYERS_HPS]
    return [new_dead_players, global_vars.PLAYERS_HPS]