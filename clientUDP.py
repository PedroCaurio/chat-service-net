import socket

HOST = '127.0.0.1'
PORT = 12345

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    mensagem = b'Hello, servidor UDP!'
    s.sendto(mensagem, (HOST, PORT))
    data, addr = s.recvfrom(1024)

print(f"Resposta do servidor: {data.decode()}")