import socket
import os
from dotenv import load_dotenv
import json

load_dotenv()

HOST = str(os.getenv("HOST", "127.0.0.1"))
PORT = int(os.getenv("PORT", 12345))

msg = {
    "type": "action",
    "payload": {
        "command": "create_user",
        "username": "aaaaaa",
        "password": "aaaa"
    }
}

json_str = json.dumps(msg)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(json_str.encode()+ b"\n")
    data = s.recv(1024)

print(f"Resposta do servidor: {data.decode()}")