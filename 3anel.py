import socket
import sys

# Configurações para Máquina 3
MY_IP = "10.254.223.41"  # IP desta máquina
MY_PORT = 5041           # Porta para receber mensagens
NEXT_IP = "10.254.223.42"  # IP da próxima máquina no anel
NEXT_PORT = 5042         # Porta para enviar mensagens

def create_socket():
    # Criação e ligação do socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((MY_IP, MY_PORT))
    return sock

def receive_message(sock):
    while True:
        # Recepção de dados
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        print(f"Received message: {data} from {addr}")
        if data:  # Se os dados são recebido psassam para a próxima máquina
            pass_message(sock, data)

def pass_message(sock, message):
    # Envio de mensagem para o próximo IP e po 3"
    print(f"Passing message to {NEXT_IP}:{NEXT_PORT}")
    sock.sendto(message, (NEXT_IP, NEXT_PORT))

def main():
    sock = create_socket()
    if len(sys.argv) > 1 and sys.argv[1] == 'start':
        # Envia a mensagem inicial para iniciar a comunicação em anel
        initial_message = b"Hello from Machine 3"
        pass_message(sock, initial_message)
    receive_message(sock)

if __name__ == "__main__":
    main()

