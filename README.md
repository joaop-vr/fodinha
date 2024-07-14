# Multiplayer Card Game

Este projeto implementa um jogo de cartas multiplayer distribuído, onde cada jogador é representado por um script Python específico. Os arquivos incluídos são:

1. `1jogador.py`
2. `2jogador.py`
3. `3jogador.py`
4. `carteador.py`

## Descrição dos Arquivos

### 1. `carteador.py`
Este script representa o carteador, responsável por distribuir as cartas e iniciar o jogo.

- **Configurações de Rede**: Define as configurações de rede para o carteador [IP:10.254.223.39, máquina: h11].
- **Funções de Rede**: Criação de socket UDP, envio e recepção de mensagens.
- **Distribuição de Cartas**: Lógica para distribuir as cartas para os jogadores.
- **Início do Jogo**: Envia mensagens de inicialização para todos os jogadores.

### 2. `1jogador.py`
Este script representa o primeiro jogador no jogo de cartas. As principais funções e funcionalidades incluem:

- **Configurações de Rede**: Define o IP e a porta para comunicação com os outros jogadores [IP:10.254.223.40, máquina: h12].
- **Funções de Rede**: Cria socket UDP, envia e recebe mensagens.
- **Processamento de Mensagens**: Processa diferentes tipos de mensagens, como inicialização, tomada de palpites e informações de palpites.
- **Jogadas**: Lógica para fazer jogadas e passar a vez para o próximo jogador.

### 3. `2jogador.py`
Este script representa o segundo jogador no jogo de cartas. As funcionalidades são similares às do `1jogador.py`, mas adaptadas para o segundo jogador.

- **Configurações de Rede**: Define o IP e a porta para o segundo jogador [IP:10.254.223.41, máquina: h13].
- **Funções de Rede**: Criação de socket UDP, envio e recepção de mensagens.
- **Processamento de Mensagens**: Tratamento de mensagens de inicialização, palpites e jogadas.
- **Jogadas**: Implementa a lógica de jogadas para o segundo jogador.

### 4. `3jogador.py`
Este script representa o terceiro jogador no jogo de cartas, com funcionalidades semelhantes às dos outros scripts de jogador.

- **Configurações de Rede**: Define o IP e a porta para o terceiro jogador [IP:10.254.223.42, máquina: h14].
- **Funções de Rede**: Criação de socket UDP, envio e recepção de mensagens.
- **Processamento de Mensagens**: Tratamento de mensagens de inicialização, palpites e jogadas.
- **Jogadas**: Implementa a lógica de jogadas para o terceiro jogador.

## Como Executar

### Passo 1: Configurar o Ambiente

Certifique-se de que todas as máquinas envolvidas no jogo tenham o Python instalado e estejam na mesma rede.

### Passo 2: Executar os Scripts

1. Inicie o carteador primeiro com o parãmetro "start":
   ```bash
   python carteador.py start

2. Em seguida, inicie cada jogador em suas respectivas máquinas:
   ```bash
   python 1jogador.py
   ```
   ```bash
   python 2jogador.py
   ````
   ```bash
   python 3jogador.py

## Observações

+ Certifique-se de ajustar os endereços IP e as portas nos scripts para refletir a configuração da sua rede.
+ Os scripts usam comunicação via UDP, então certifique-se de que os firewalls e outras configurações de rede permitam o tráfego UDP nas portas especificadas.
