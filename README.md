# Jogo de Cartas Distribuído (Fodas#)

Este repositório contém um projeto desenvolvido durante a disciplina de Redes de Computadores I. O trabalho consiste na implementação de um jogo de cartas conhecido popularmente como 'Fodas#', utilizando Python e sockets para a comunicação entre os jogadores. O jogo é distribuído e inclui funcionalidades como distribuição de cartas, realização de palpites e jogadas, contagem de pontos, e gestão das vidas dos jogadores.

## Configurações da Rede

O jogo é configurado para rodar na rede local do Dinf com quatro jogadores. Cada jogador deve ter um IP e uma porta específicos:

```python
PLAYERS_IPS = ["10.254.223.57", "10.254.223.58", "10.254.223.59", "10.254.223.60"]
PLAYERS_PORTS = [5039, 5040, 5041, 5042]
````

## Como Executar

1. Configure os IPs e portas dos jogadores na seção de configurações da rede.
2. Execute o script em cada máquina/jogador.
3. O comando deve ser:
   ```python
   python3 main.py <numero_jogador> "start"
   ````
   Obs.: os números dos jogadores são de 1 a 4; "start" indica que o jogador em questão será o carteador inicial; só pode haver um carteador inicial no jogo.
5. O carteador deve ser o último a ser conectado na rede.
6. O jogo iniciará automaticamente, distribuindo as cartas e esperando as ações de cada jogador.
## Variáveis Globais

O jogo utiliza diversas variáveis globais para armazenar o estado do jogo, incluindo cartas distribuídas, vidas dos jogadores, e informações sobre rodadas e sub-rodadas:

```python
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
````




