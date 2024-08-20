import global_vars
from prints import *
from main import *

# Função para processar as mensagens do dealer
def dealer(sock, message):
     #global MY_CARDS, GUESSES, MOVES, IS_DEALER, PLAYING, ROUND, SUB_ROUND
     # A mensagem do dealer deu a volta na rede e chegou nele
     msg = {}
     if message["from_player"] == global_vars.MY_ID:

         # Verifica se todos responderam ACK
         error = False
         for i in range(len(message["acks"])):
             if len(message["acks"]) == 1 and message["acks"][0] == 0: # Bastão foi perdido
                 error = True
             elif message["acks"][i] == 0 and i != global_vars.MY_ID: # Alguem nao respondeu ACK 1
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
                    "from_player": global_vars.MY_ID,
                    "to_player": destination,  
                    "data": player_cards,
                    "acks": [0, 0, 0, 0]
                 }
             elif message["type"] == "init":
                 if global_vars.PLAYERS_HPS[global_vars.MY_ID] > 0:
                    print(f"SUB_ROUND: {global_vars.SUB_ROUND} | ROUND: {global_vars.ROUND} MY_HP: {global_vars.PLAYERS_HPS[global_vars.MY_ID]}")
                    global_vars.MY_CARDS = message["data"][global_vars.MY_ID][0]
                    print(f"\nRodada: {global_vars.ROUND}")
                    print(f"Manilha: {global_vars.SHACKLE}")
                    print(f"Configuração da partida: {global_vars.CARDS}")
                    print(f"Suas cartas: {global_vars.MY_CARDS}.")
                 else:
                     print(f"Você ficou sem vidas.. está como dealer espectador.")
                 msg = {
                    "type": "take_guesses",
                    "broadcast": True,
                    "from_player": global_vars.MY_ID,
                    "to_player": destination, 
                    "data": [0, 0, 0, 0],
                    "acks": [0, 0, 0, 0]
                }
             elif message["type"] == "take_guesses":
                 global_vars.GUESSES = message["data"]
                 sum_guesses = 0
                 for guess in message["data"]:
                     if guess != -1:
                         sum_guesses += guess
                 guess = take_guess(sum_guesses)
                 global_vars.GUESSES[MY_ID] = guess
                 msg = {
                    "type": "informing_guesses",
                    "broadcast": True,
                    "from_player": global_vars.MY_ID,
                    "to_player": destination, 
                    "data": global_vars.GUESSES,
                    "acks": [0, 0, 0, 0]
                 }
             elif message["type"] == "informing_guesses":
                 print_guesses(message["data"])
                 msg = {
                    "type": "make_move",
                    "broadcast": True,
                    "from_player": global_vars.MY_ID,
                    "to_player": destination, 
                    "data": [],
                    "acks": [0, 0, 0, 0]
                 }
             elif message["type"] == "make_move":
                 global_vars.MOVES = message["data"]
                 print_previous_moves(message["data"])
                 move = make_move()
                 global_vars.MOVES.append(move)
                 msg = {
                    "type": "informing_moves",
                    "broadcast": True,
                    "from_player": global_vars.MY_ID,
                    "to_player": destination, 
                    "data": global_vars.MOVES,
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
                 if global_vars.SUB_ROUND == global_vars.ROUND:
                     aux = finish_round()
                     round_info[1] = aux[0]  # Lista de jogadores que morreram
                     round_info[2] = aux[1]  # Lista de HPs dos jogadores

                 msg = {
                    "type": "round_info",
                    "broadcast": True,
                    "from_player": global_vars.MY_ID,
                    "to_player": destination, 
                    "data": round_info,
                    "acks": [0, 0, 0, 0]
                 }
             elif message["type"] == "round_info":
                 print_round_info(message["data"])
                 if global_vars.SUB_ROUND == global_vars.ROUND:
                    update_HP(message)
                 players_alive = check_players_alive()
                 if len(players_alive) <= 1:
                     msg = {
                        "type": "end_game",
                        "broadcast": True,
                        "from_player": global_vars.MY_ID,
                        "to_player": destination, 
                        "data": players_alive,
                        "acks": [0, 0, 0, 0]
                     }
                 else:
                     if global_vars.SUB_ROUND != global_vars.ROUND:
                         msg = {
                            "type": "make_move",
                            "broadcast": True,
                            "from_player": global_vars.MY_ID,
                            "to_player": destination, 
                            "data": [],
                            "acks": [0, 0, 0, 0]
                         }
                     else:
                         msg = {
                            "type": "reset_vars",
                            "broadcast": True,
                            "from_player": global_vars.MY_ID,
                            "to_player": destination, 
                            "data": [],
                            "acks": [0, 0, 0, 0]
                         }
             elif message["type"] == "reset_vars":
                 reset_vars()
                 dealer_info = [global_vars.ROUND, global_vars.PLAYERS_HPS]
                 msg = {
                    "type": "dealer_token",
                    "broadcast": False,
                    "from_player": global_vars.MY_ID,
                    "to_player": global_vars.NEXT_ID, 
                    "data": dealer_info,
                    "acks": [0]
                 }
                 print(f"Você não é mais o carteador.")
             elif message["type"] == "dealer_token":
                 global_vars.IS_DEALER = False
             elif message["type"] == "end_game":
                 if len(message["data"]) != 0:
                    print(f"\nO último jogador que se manteve de pé foi o Jogador {message['data'][0] + 1}")
                 else:
                    print(f"\nHouve empate! A verdadeira vitória são os amigos que fizemos no caminho...")
                 global_vars.PLAYING = False
                 return
    
     if global_vars.IS_DEALER:
         send_message(sock, msg)
     else:
         receive_message(sock)

# Função para processar as mensagens do jogador padrão
def normal_player(sock, message):
    #global PLAYERS_HPS, MY_ID, DEALER_ID, SHACKLE, MY_CARDS, ROUND, PLAYING, ROUND
    # Recebeu uma mensagem destinada a ele
    if message["broadcast"] == True and global_vars.MY_ID in message["to_player"]:
        if global_vars.PLAYERS_HPS[global_vars.MY_ID] <= 0:
            message["acks"][global_vars.MY_ID] = -1
        else:
            message["acks"][global_vars.MY_ID] = 1
        if message["type"] == "informing_dealer":
            global_vars.DEALER_ID = message["from_player"]
            print_dealer(message)
            #send_message(sock, message)
        elif message["type"] == "init":                   # Setando as variaveis do player no inicio da rodada
            aux = message['data'][global_vars.MY_ID]
            global_vars.MY_CARDS = aux[0]
            global_vars.SHACKLE = aux[1]
            global_vars.CARDS = aux[2]
            global_vars.ROUND = len(global_vars.MY_CARDS)
            if PLAYERS_HPS[MY_ID] > 0:
                print(f"\nRodada: {global_vars.ROUND}")
                print(f"Manilha: {global_vars.SHACKLE}")
                print(f"Configuração da partida: {global_vars.CARDS}")
                print(f"Suas cartas: {global_vars.MY_CARDS}.")
            else:
                print(f"Você ficou sem vidas.. está como dealer espectador.")
        elif message["type"] == "take_guesses":         # Faz o palpite
            guess = take_guess()
            message["data"][global_vars.MY_ID] = guess
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
            if len(global_vars.MY_CARDS) == 0:
                update_HP(message)
        elif message["type"] == "reset_vars":           # Reinicia as variaveis globais para poder iniciar uma nova rodada
            reset_vars()
        elif message["type"] == "end_game":
            if len(message["data"]) != 0:
                print(f"\nO último jogador que se manteve de pé foi o Jogador {message['data'][0] + 1}")
            else:
                print(f"\nHouve empate! A verdadeira vitória são os amigos que fizemos no caminho...")
            global_vars.PLAYING = False
        send_message(sock, message)
    elif message["broadcast"] == False and message["to_player"] == global_vars.MY_ID:
        if message["type"] == "dealer_token":
            global_vars.ROUND = message["data"][0]
            global_vars.PLAYERS_HPS = message["data"][1]
            message["acks"][0] = 1
            send_message(sock, message)
            init_round(sock)
            receive_message(sock)
            return
    else:
        send_message(sock, message)
