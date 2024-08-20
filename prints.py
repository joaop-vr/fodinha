# Arquivo com as funções que imprimem informações ao longo do jogo
import global_vars

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