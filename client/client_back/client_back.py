'''
Arquivo principal do cliente. Responsável por ouvir e enviar requisições para o servidor
Utiliza threads para ouvir o servidor e ao mesmo tempo permitir interações
do usuário.
'''
import socket
import os
from dotenv import load_dotenv
from services import login
import json
import threading
from PyQt6.QtCore import QObject, pyqtSignal

from registry import get_command

load_dotenv()

HOST = str(os.getenv("HOST", "127.0.0.1"))
PORT = int(os.getenv("PORT", 12345))

USER = None

''' Envia o dicionário passado como data para o servidor'''
def send_json(sock, data):
    sock.sendall(json.dumps(data).encode())

''' Função usada pela Thread para ficar escutando o servidor '''
def listen_server(sock):
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                break
            msg = json.loads(data.decode())
            if msg["type"] == "broadcast":
                print(f"\n[{msg['payload']['sender']}]: {msg['payload']['body']}")
            else:
                print(msg)
        except:
            break
''' Função que conecta ao servidor, roda as threads e recebe os inputs do usuário'''
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
                  
    threading.Thread(target=listen_server, args=(s,), daemon=True).start()

    while True:
        command = input("digite o comando que voce deseja executar: ")
        
        func = get_command(command)
        if func:
            msg = func()

            send_json(s, msg)

if __name__ == "__main__":
    main()