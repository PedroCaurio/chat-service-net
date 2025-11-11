import socket
import os
import json
import sys
from dotenv import load_dotenv
from PyQt6.QtWidgets import QMessageBox, QMainWindow
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, Qt, QThread
from client_back.registry import get_command
from client_back.services.login import login
from client_back.data_helper import data_helper

load_dotenv(dotenv_path="../.env")

class NetworkWorker(QThread):
    data_received = pyqtSignal( bytes)
    disconnected = pyqtSignal()

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.running = True
        self.sock = None

    def run(self):
        try:
            print("tentando conexao")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
        except Exception as e:
            self.disconnected.emit()
            return

        try:
            while self.running:
                data = self.sock.recv(4096)
                if not data:
                    break
                print(type(self.sock), data)

                self.data_received.emit(data)
        except Exception as e:
            print(f"Ocorreu um erro ao interceptar o pacote enviado pelo server: {e}")
        self.disconnected.emit()
        if self.sock: # Fecha a conexão caso aconteça algo inesperado
            self.sock.close()
            self.sock = None
        self.run() # Tenta abrir novamente a conexão com o servidor
    
    # def stop(self):
    #     self.running = False
    #     if self.sock:
    #         try:
    #             self.sock.shutdown(socket.SHUT_RDWR)
    #             self.sock.close()
    #         except Exception:
    #             pass


class ClientService(QObject):
    """
    Gerencia a lógica de rede do cliente em uma thread separada.
    Comunica-se com a GUI (qualquer QWidget) apenas através de sinais e slots.
    """
    
    # --- Sinais para a GUI ---
    # Sinais de conexão e login
    connection_error = pyqtSignal(str)
    login_sucess = pyqtSignal(str, dict) # Envia o user_id ou nome
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
        self.user_id = None
        self.worker = NetworkWorker(str(os.getenv("SERVER_IP", "127.0.0.1")), int(os.getenv("PORT", 12346)))
        self.initState(main_window)
    

    def initState(self, main_window: QMainWindow) -> None:
        # --- Conexões de Login e Erro ---
        self.connection_error.connect(main_window.login_screen.show_error)
        self.connection_error.connect(main_window.show_login_screen)

        def on_disconnect():
            QMessageBox.warning(main_window, "Desconectado", "A conexão com o servidor foi perdida.")
            main_window.show_login_screen()
        self.server_disconnected.connect(on_disconnect)
        main_window.login_screen.login_requested.connect(self.try_login)
        main_window.login_screen.register_requested.connect(self.try_register)

        # --- Conexão de Login com main_window ---
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


        # ---- Conexão da Thread que recebe os dados do socket ---
        self.worker.data_received.connect(self.handle_data)
        self.worker.disconnected.connect(self.handle_disconnect)

        # --- Conexão Criação de Grupo ----
        main_window.create_group_screen.create_group_requested.connect(self.manage_group)

        # ---- Inicializa a Thread de recebimento dos dados ----
        self.worker.start()

        if (data_helper.user.get("username", None) is not None):
            main_window.login_screen.login_requested.emit(data_helper.user["username"], data_helper.user["password"])
        
    def manage_group(self, group_name, new_user, user_id):
        msg = {
            "type": "group",
            "payload": { 
                "user_id": user_id,
                "group_name": group_name,
                "new_user": new_user
            }
        }
        self.send_json(msg)
    @pyqtSlot(bytes)
    def handle_data(self,data):
        '''
            Função para tratar o recebimento das mensagens. 
        '''
        for msg_str in self.decode_messages(data):
            try:
                msg = json.loads(msg_str)
                
                print("mensagem recebida:", msg)
                if msg:
                    command = msg.get("type")
                    args = msg.get("payload")
                    func = 'handle_' + command
                    try:
                        getattr(self, func)(**args)
                    except:
                        getattr(self, func, lambda _: print(f"Tipo de mensagem não tratada: {command}"))(msg)
            except json.JSONDecodeError:
                print(f"JSON inválido recebido: {msg_str}")
    
    @pyqtSlot()
    def handle_disconnect(self):
        self.server_disconnected.emit()

    def decode_messages(self, data):
        """
        Decodifica o buffer. O `client.py` envia JSONs com '\n',
        então vamos assumir que o servidor faz o mesmo.
        """
        buffer = data.decode('utf-8')
        for msg in buffer.strip().split('\n'):
            if msg:
                yield msg



    def handle_login(self, msg):
        #payload = msg.get("payload", {})
        if msg.get("type") == "login":
            if msg.get("payload").get("user_id"):
                self.username = msg.get("payload").get("username") # Salva quem somos
                self.login_sucess.emit(self.username, msg.get("payload").get("users"))
                data_helper.user = {"username": self.username, "password": self.last_password}
            else:
                self.login_failed.emit(msg.get("message", "Login falhou."))

    def handle_private_message(self, msg: dict):
        payload = msg.get("payload", {})
        # Mensagem privada recebida
        print("mensagem privada recebida", msg)
        self.new_private_message.emit(
            payload.get("origin"), 
            payload.get("message").get("text")
        )
        
    def handle_group_message(self, msg: dict):
        payload = msg.get("payload", {})
        self.new_group_message.emit(
            payload.get("group_id"),
            payload.get("sender"), 
            payload.get("body")
        )
    def handle_general_message(self, msg:dict):
        payload = msg.get("payload", {})
        self.new_general_message.emit(
            payload.get("origin"),
            payload.get("message").get("text")
        )

    def handle_user_list(self, msg: dict):
        payload = msg.get("payload", {})
        self.user_list_updated.emit(payload.get("users", []))
        
    def send_json(self, data: dict):
        """Helper para enviar dados JSON ao servidor."""
        if not self.worker.sock:
            return
        try:
            # Usando '\n' como delimitador, baseado no `client.py`
            print("enviando")
            message = json.dumps(data, ensure_ascii=False) + "\n"
            self.worker.sock.sendall(message.encode('utf-8'))
        except Exception as e:
            print(f"Erro ao enviar JSON: {e}")
            self.server_disconnected.emit() # Provavelmente a conexão caiu

    # --- Slots para a GUI ---

    @pyqtSlot(str, str)
    def try_login(self, username, password):
        """Slot para receber o sinal de login da LoginScreen."""
        # Formato baseado no `client_back/services/login.py`
        msg = {
            "type": "login",
            "payload": {
                "username": username,
                "password": password
            }
        }
        self.last_password = password
        self.send_json(msg)
    
    @pyqtSlot(str, str)
    def try_register(self, username, password):
        """Slot para receber o sinal de registro."""
        msg = {
            "type": "request",
            "payload": {
                "command": "register",
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
        print(self.username)
        msg = {
            "type": "message",
            "payload": { 
                "origin": self.username,
                "destiny": recipient_user, 
                "message": message
            }
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
            "type": "general_message",
            "payload": { 
                "origin": self.username,
                "message": message
            }
        }
        self.send_json(msg)

def send_json(sock, data):
    sock.sendall(json.dumps(data).encode())