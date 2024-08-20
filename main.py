import socket
import json
import sys
import random
import global_vars
from manage_rounds import *
from players import *
import prints

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
