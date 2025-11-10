# client/client_service.py
#
#       TRABALHO EM ANDAMENTO - MTA IA AINDA
#

import socket
import os
import json
import sys
from dotenv import load_dotenv
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

load_dotenv()

class ClientService(QObject):
    """
    Gerencia a lógica de rede do cliente em uma thread separada.
    Comunica-se com a GUI (qualquer QWidget) apenas através de sinais e slots.
    """
    
    # --- Sinais para a GUI ---
    # Sinais de conexão e login
    connection_error = pyqtSignal(str)
    login_sucess = pyqtSignal(str) # Envia o user_id ou nome
    login_failed = pyqtSignal(str)
    server_disconnected = pyqtSignal()

    # Sinais de chat (recebidos do servidor)
    new_private_message = pyqtSignal(str, str) # sender, message
    new_group_message = pyqtSignal(str, str, str) # group_id, sender, message
    new_general_message = pyqtSignal(str, str) # sender, message
    
    # Sinais de informação (ex: lista de usuários)
    user_list_updated = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.sock = None
        self.host = str(os.getenv("HOST", "127.0.0.1"))
        self.port = int(os.getenv("PORT", 12345))
        self.user_id = None

    @pyqtSlot()
    def connect_and_listen(self):
        """
        Slot principal que roda na QThread. Conecta e entra no loop de escuta.
        Este é o "run" da nossa thread.
        """
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
        except Exception as e:
            self.connection_error.emit(f"Erro ao conectar: {e}")
            return

        # Uma vez conectado, entra no loop de escuta
        try:
            while True:
                data = self.sock.recv(4096)
                if not data:
                    break # Servidor fechou a conexão
                
                # O servidor pode enviar múltiplos JSONs de uma vez
                for msg_str in self.decode_messages(data):
                    try:
                        msg = json.loads(msg_str)
                        self.handle_server_message(msg)
                    except json.JSONDecodeError:
                        print(f"JSON inválido recebido: {msg_str}")
            
        except Exception as e:
            print(f"Erro no loop de escuta: {e}")
        
        self.server_disconnected.emit()
        self.sock.close()

    def decode_messages(self, data):
        """
        Decodifica o buffer. O `client.py` envia JSONs com '\n',
        então vamos assumir que o servidor faz o mesmo.
        """
        buffer = data.decode('utf-8')
        # Se seus colegas não usam '\n' como delimitador,
        # você terá que ajustar essa lógica (ex: JSONL)
        for msg in buffer.strip().split('\n'):
            if msg:
                yield msg

    def handle_server_message(self, msg: dict):
        """
        Processa a mensagem JSON do servidor e emite o sinal apropriado.
        """
        msg_type = msg.get("type")
        payload = msg.get("payload", {})

        if msg_type == "response":
            # Resposta a um comando (ex: login)
            if msg.get("command") == "login":
                if msg.get("status") == "success":
                    self.user_id = payload.get("username", "user") # Salva quem somos
                    self.login_sucess.emit(self.user_id)
                else:
                    self.login_failed.emit(msg.get("message", "Login falhou."))
        
        elif msg_type == "private_message":
            # Mensagem privada recebida
            self.new_private_message.emit(
                payload.get("sender"), 
                payload.get("body")
            )

        elif msg_type == "group_message":
            # Mensagem de grupo recebida
            self.new_group_message.emit(
                payload.get("group_id"),
                payload.get("sender"), 
                payload.get("body")
            )

        elif msg_type == "broadcast" or msg_type == "general_message":
            # Mensagem geral
            self.new_general_message.emit(
                payload.get("sender"), 
                payload.get("body")
            )
        
        elif msg_type == "user_list":
            # Atualização da lista de usuários
            self.user_list_updated.emit(payload.get("users", []))
            
        else:
            print(f"Tipo de mensagem não tratada: {msg_type}")

    def send_json(self, data: dict):
        """Helper para enviar dados JSON ao servidor."""
        if not self.sock:
            return
        try:
            # Usando '\n' como delimitador, baseado no `client.py`
            message = json.dumps(data, ensure_ascii=False) + "\n"
            self.sock.sendall(message.encode('utf-8'))
        except Exception as e:
            print(f"Erro ao enviar JSON: {e}")
            self.server_disconnected.emit() # Provavelmente a conexão caiu

    # --- Slots para a GUI ---

    @pyqtSlot(str, str)
    def try_login(self, username, password):
        """Slot para receber o sinal de login da LoginScreen."""
        # Formato baseado no `client_back/services/login.py`
        

        msg = {
            "type": "request",
            "payload": {
                "command": "login",
                "username": username,
                "password": password
            }
        }
        self.send_json(msg)

    @pyqtSlot(str, str)
    def send_private_message(self, recipient_user, message):
        """Slot para enviar uma mensagem privada."""
        # Formato baseado no `client.py`
        msg = {
            "type": "private", 
            "to": recipient_user, 
            "message": message
        }
        self.send_json(msg)

    @pyqtSlot(str, str)
    def send_group_message(self, group_id, message):
        """Slot para enviar uma mensagem de grupo."""
        # Formato baseado no `client.py`
        msg = {
            "type": "group", 
            "group_id": group_id, 
            "message": message
        }
        self.send_json(msg)

    @pyqtSlot(str)
    def send_general_message(self, message):
        """Slot para enviar uma mensagem geral/broadcast."""
        # Formato baseado no `client.py`
        msg = {
            "type": "general", 
            "message": message
        }
        self.send_json(msg)