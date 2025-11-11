'''
Script que apenas faz o bind com a porta e cria thread para cada nova conexão. A função executada
por cada thread é a handle_connection do script connection_manager
'''

import socket
import os
from dotenv import load_dotenv
import threading
from connection_manager import handle_connection

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
            thread = threading.Thread(target=handle_connection, args=(conn, addr), daemon=True)
            thread.start()

if __name__ == "__main__":
    start_server()
