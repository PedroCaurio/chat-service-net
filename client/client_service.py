# client/client_service.py
#
#       TRABALHO EM ANDAMENTO - MTA IA AINDA
#

import socket
import os
import json
import sys
from dotenv import load_dotenv
from PyQt6.QtWidgets import QMessageBox, QMainWindow
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, Qt

load_dotenv(dotenv_path="../.env")

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

    def __init__(self, main_window: QMainWindow):
        super().__init__()
        self.sock = None
        self.host = str(os.getenv("SERVER_IP", "127.0.0.1"))
        self.port = int(os.getenv("PORT", 12345))
        self.user_id = None
        self.initState(main_window)
    

    def initState(self, main_window: QMainWindow) -> None:
        # --- Conexões de Login e Erro ---
        self.connection_error.connect(main_window.login_screen.show_error)
        self.connection_error.connect(main_window.show_login_screen)

        def on_disconnect():
            QMessageBox.warning(main_window, "Desconectado", "A conexão com o servidor foi perdida.")
            main_window.show_login_screen()
        self.server_disconnected.connect(on_disconnect)
        main_window.login_screen.login_requested.connect(self.try_login, type=Qt.ConnectionType.QueuedConnection)
        self.login_sucess.connect(main_window.show_chat_screen)
        self.login_sucess.connect(main_window.chat_screen.load_user_data)
        self.login_failed.connect(main_window.login_screen.show_error)

        # --- Conexões de Chat (Envio) ---
        main_window.chat_screen.private_message_sended.connect(self.send_private_message)
        main_window.chat_screen.group_message_sended.connect(self.send_group_message)
        main_window.chat_screen.general_message_sended.connect(self.send_general_message)

        # --- Conexões de Chat (Recebimento) ---
        self.new_private_message.connect(main_window.chat_screen.add_private_message)
        self.new_group_message.connect(main_window.chat_screen.add_group_message)
        self.new_general_message.connect(main_window.chat_screen.add_general_message)
        
    


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
                        msg_type = msg.get("type", "")
                        func = 'handle_' + msg_type
                        getattr(self, func, lambda _: print(f"Tipo de mensagem não tratada: {msg_type}"))(msg)
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


    def handle_response(self, msg: dict):
        payload = msg.get("payload", {})
        if msg.get("command") == "login":
            if msg.get("status") == "success":
                self.user_id = payload.get("username", "user") # Salva quem somos
                self.login_sucess.emit(self.user_id)
            else:
                self.login_failed.emit(msg.get("message", "Login falhou."))

    def handle_private_message(self, msg: dict):
        payload = msg.get("payload", {})
        # Mensagem privada recebida
        self.new_private_message.emit(
            payload.get("sender"), 
            payload.get("body")
        )
        
    def handle_group_message(self, msg: dict):
        payload = msg.get("payload", {})
        self.new_group_message.emit(
            payload.get("group_id"),
            payload.get("sender"), 
            payload.get("body")
        )
    
    def handle_user_list(self, msg: dict):
        payload = msg.get("payload", {})
        self.user_list_updated.emit(payload.get("users", []))
        
    def send_json(self, data: dict):
        """Helper para enviar dados JSON ao servidor."""
        if not self.sock:
            return
        try:
            # Usando '\n' como delimitador, baseado no `client.py`
            print("enviando")
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
        print(msg)
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