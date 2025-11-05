import socket

HOST = '127.0.0.1'
PORT = 12345

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))
    print(f"Servidor UDP escutando em {HOST}:{PORT}...")
    while True:
        data, addr = s.recvfrom(1024)
        print(f"Recebido de {addr}: {data.decode()}")
        data2 = b'Ola, Cliente!'
        s.sendto(data2, addr)  # ecoa a mensagem de volta