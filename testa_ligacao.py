import socket

MY_IP = "10.254.223.61"
MY_PORT = 5061

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    sock.bind((MY_IP, MY_PORT))
    print("Socket bound successfully")
except OSError as e:
    print(f"Error binding socket: {e}")

