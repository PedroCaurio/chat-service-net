import socket
import os
import threading
import json
from dotenv import load_dotenv

from server.database.lock_manager import get_lock

# o json das mensagens vai ter que conter o group_id para saber para qual grupo enviar
# 

# Felipe já fez a lógica de grupos, usuarios no groups.py
# os usuarios vão se autenticar com user_id e depois vão mandar mensagens para grupos
# grupos tem a lista de user_ids

from server.repositories import UserRepository, GroupRepository

load_dotenv()

HOST = str(os.getenv("HOST", "0.0.0.0"))
PORT = int(os.getenv("PORT", 12345))

clients = {}  # {user_id: conn}
# usa o lock manager central para o recurso 'clients' (permite visibilidade centralizada)
clients_lock = get_lock("clients")

def send_to_group(group_id, mensagem_bytes, remetente_id):
    """Enviar mensagem para todos do grupo, exceto o remetente"""
    group = GroupRepository.get_group_by_id(group_id)
    if group:
        with clients_lock:
            for user_id in group.users:
                if user_id != remetente_id and user_id in clients:
                    try:
                        clients[user_id].sendall(mensagem_bytes)
                    except Exception as e:
                        print(f"Falha ao enviar para {user_id}: {e}")

def thread_client(conn, addr):
    """
    Conexão de cada cliente: espera autenticação e depois processa mensagens
    """
    conn.sendall(b'Conecte com {"user_id": "..."}')

    try:
        auth = conn.recv(1024).decode("utf-8")
        auth_json = json.loads(auth)
        user_id = auth_json.get("user_id")
        if not user_id or not UserRepository.get_user_by_id(user_id):
            conn.sendall(b'User invalido!')
            conn.close()
            return

        with clients_lock:
            clients[user_id] = conn

        conn.sendall(b" Envie mensagens como {'group_id':..., 'message':...}")
        while True:
            data = conn.recv(4096)
            if not data:
                break

            try:
                msg_json = json.loads(data.decode("utf-8"))
                group_id = msg_json.get("group_id")
                message = msg_json.get("message")
                if group_id and message:
                    payload = json.dumps({ #
                        "from": user_id,
                        "group_id": group_id,
                        "message": message
                    }).encode("utf-8")
                    send_to_group(group_id, payload, user_id) # payload é a mensagem formatada
            except Exception:
                conn.sendall(b"Mensagem invalida. Use {'group_id':..., 'message':...}") # 

    finally:
        with clients_lock:
            if user_id in clients:
                clients.pop(user_id)
        conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Servidor escutando em {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=thread_client, args=(conn, addr))
            thread.daemon = True
            thread.start()

if __name__ == "__main__":
    start_server()