import socket
import os
from dotenv import load_dotenv

load_dotenv()

HOST = str(os.getenv("HOST", "127.0.0.1"))
PORT = int(os.getenv("PORT", 12345))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'Hello, servidor TCP!')
    data = s.recv(1024)

print(f"Resposta do servidor: {data.decode()}")