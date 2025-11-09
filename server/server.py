import socket
import os
import json
from dotenv import load_dotenv
import threading
from server.services import action, login
from server.connection_manager import handle_connection

load_dotenv()
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 12345))



def start_server():
    """ Inicia o servidor e espera por conexões. """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Servidor escutando em {HOST}:{PORT}")

        while True:
            # loop principal
            conn, addr = s.accept()
            print(f"Nova conexão de {addr}")
            # encaminha a conexão para o connection_manager, que cria/roda o handler em thread
            thread = threading.Thread(target=handle_connection, args=(conn, addr))
            thread.daemon = True
            thread.start()

if __name__ == "__main__":
    start_server()
