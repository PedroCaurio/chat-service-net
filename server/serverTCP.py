import socket
import os
import threading
import json
from dotenv import load_dotenv

load_dotenv()
from models.message import Message
from repositories import UserRepository, GroupRepository
from database.lock_manager import get_lock # get_lock pega o lock global do recurso 'clients'
from services.chat_private import send_private_message, get_private_messages
from services.groups import send_group_message, get_group_messages


HOST = str(os.getenv("HOST", "0.0.0.0")) 
PORT = int(os.getenv("PORT", 12345))

## att 3: Exclui os comentários para dar uma limpada, eu vou fazer umas anotações pra tentar
# ajudar a entender o fluxo eu fiquei um pouco perdido por que mesmo que aqui seja
# o alto nivel do servidor, tem muitos tratamentos acontecendo também no handle_message
# e com os novos repositories e a adequação do database_instance preciso repassar por cada função pra ver se 
# ta tudo de acordo com o fluxo

# vou passar o start_server pro final

clients = {}  # agora é {user_id: conn}
clients_lock = get_lock("clients")
# clients_lock é o lock manager central para o recurso 'clients'
# att 2 agora usa a implementação de user do Felipe

# broadcast é a função que envia mensagens para todos os clientes conectados
def broadcast(mensagem_bytes, remetente_user_id): # Chat geral
    """Envia uma mensagem para todos os clientes conectados, exceto o remetente."""
    with clients_lock:
        for client_id, client_conn in clients.items():
            if client_id != remetente_user_id:
                try:
                    client_conn.sendall(mensagem_bytes)
                except Exception as e:
                    print(f"Não foi possível enviar mensagem para {client_id}: {e}")
                    
             
# função que vai lidar com cada cliente em uma thread separada  
# ela espera o user_id, valida, e depois processa mensagens, faz broadcast etc  
# att 2 ela só precisa usar os métodos do repository
# att 3 agora ele usa o handle_message pra processar as mensagens
# no começo ele fazia tudo, agora ele só valida e repassa pro handle_message
def thread_client(conn, addr):
    """ Função que roda em uma thread para cada cliente. """
    user_id = None
    try:
        conn.sendall(b'Conecte com seu user_id:')
        user_id_data = conn.recv(1024).decode("utf-8").strip() 
        # o user_id_data é a string temporaria que vai receber
        # o user_id enviado pelo cliente e se for valido
        # vai ser armazenado na variavel user_id

        # Valida user_id usando UserRepository.
        # Aceita tanto o user_id quanto o username: se for username, busca o user_id correspondente.
        user_obj = UserRepository.get_user_by_id(user_id_data)
        if user_obj is None:
            # tenta por username
            user_obj = UserRepository.get_user_by_username(user_id_data)
            if user_obj is None:
                conn.sendall(b'User invalido')
                conn.close()
                return
        user_id = user_obj.user_id
        with clients_lock:
            clients[user_id] = conn
        print(f"Usuario {user_id} conectado de {addr}") #  log da conexão
        conn.sendall(b'Conectado ao chat geral!\n')
        while True:
            data = conn.recv(1024)
            if not data:
                print(f"Usuario {user_id} desconectou")
                break
            # Vou tentar usar o handle_message, essa parte 
            # era veio antes da função handle_message existir (ela funciona)
            # só vou deixar aqui pra eu não esquecer caso realmente de errado
            # ele só funcionava pro chat geral
            #mensagem = data.decode("utf-8")
            #print(f"[{user_id}@{addr}] {mensagem}")
            #broadcast(f"[{user_id}]: {mensagem}".encode("utf-8"), user_id)
            try: 
                envelope = json.loads(data.decode("utf-8")) 
            except json.JSONDecodeError:
                conn.sendall(b"Formato JSON invalido\n")
                continue
        # Então agora ela valida -> gerencia a conexão -> decodifica a mensagem -> envia para o handle_message
        # Aqui é onde a mensagem é processada
            response = handle_message(user_id, envelope, conn)
            if response:
                # envia a resposta de volta ao cliente... pode ser util
                # pra depois colocar campos novos
                conn.sendall((json.dumps(response)).encode("utf-8"))
            if response.get("status") == "error":
                conn.sendall(f"Erro: {response.get('message')}\n".encode("utf-8"))

    except ConnectionResetError:
        print(f"Conexão perdida com o usuario {user_id}")
    except Exception as e:
        print(f"Erro inesperado com {user_id}: {e}")
    finally:
        with clients_lock:
            if user_id in clients:
                del clients[user_id]
        conn.close()


def send_to_user(target_user_id, payload_bytes):
    """Envia bytes para o usuário conectado, se presente."""
    with clients_lock:
        sock = clients.get(target_user_id)
    if sock:
        try:
            sock.sendall(payload_bytes)
        except Exception as e:
            print(f"Falha ao enviar para {target_user_id}: {e}")

def send_to_group(group_id, mensagem_bytes, remetente_id):
    """Enviar mensagem para todos os usuários do grupo, exceto o remetente."""
    group = GroupRepository.get_group_by_id(group_id)
    if not group:
        return
    targets = []
    with clients_lock:
        for uid in getattr(group, 'users', []):
            if uid != remetente_id and uid in clients:
                targets.append(clients[uid])
    for sock in targets:
        try:
            sock.sendall(mensagem_bytes)
        except Exception as e:
            print(f"Falha ao enviar para membro do grupo: {e}")
            


# Cola para as proximas funções, importar lá do services pra ter criar o chat privado, eu tenho 
# send_private_message, get_private_messages eles tem os parametros user_id, sender_id receiver_id
# primeiro vou tentar fazer o handle_message que vai persistir/processar as mensagens

# Tarefa, usar os HELPERs, tem que usar o envelope json eu acho, mesmo que o primeiro
# tipo de dado seja data, tem que ser um json acredito por ser mais facil de expandir
# identificação do tipo de mensagem e do caminho que vai passar

def handle_message(user_id, envelope, conn):
    """Processa diferentes tipos de mensagens (JSON) recebidas do cliente.
    `data` é bytes contendo um JSON por linha."""
    try: 
        # chat geral
        msg_type = envelope.get("type", "general")
        if msg_type == "general":
            text = envelope.get("message")
            if text:
            # usa a model mas só envia a string formatada
                broadcast(f"[{user_id}]: {text}".encode("utf-8"), user_id)
                return {"status": "success"}
        
        elif msg_type == "private":
            receiver = envelope.get("target_user_id") or envelope.get("to")
            text = envelope.get("message") or envelope.get("text") or ""
            if receiver and text:
                # resolve receiver: aceita tanto user_id quanto username
                target_obj = UserRepository.get_user_by_id(receiver)
                if target_obj is None:
                    target_obj = UserRepository.get_user_by_username(receiver)
                if target_obj is None:
                    return {"status": "error", "message": "Usuário não encontrado"}

                receiver_id = target_obj.user_id
                # instancia e envia a mensagem privada usando o helper (que persiste)
                ok = send_private_message(user_id, receiver_id, text)
                if ok:
                    # monta payload com o message model e envia para o socket do receiver
                    msg = Message(from_=user_id, to=receiver_id, text=text)
                    payload = json.dumps(msg.to_dict(), ensure_ascii=False).encode("utf-8")
                    send_to_user(receiver_id, payload)
                    return {"status": "success", "message": f"Mensagem enviada para {receiver}", "payload": msg.to_dict()}
                else:
                    return {"status": "error", "message": "Falha ao persistir/enviar mensagem"}


        elif msg_type == "group":
            group_id = envelope.get("group_id")
            text = envelope.get("message") or envelope.get("text") or ""
            if group_id and text:
                group = GroupRepository.get_group_by_id(group_id)
                if group and user_id in getattr(group, "users", []):
                    ok = send_group_message(user_id, group_id, text)
                    if ok:
                        msg = Message(from_=user_id, to=group_id, text=text)
                        payload = json.dumps(msg.to_dict(), ensure_ascii=False).encode("utf-8")
                        send_to_group(group_id, payload, user_id)
                        return {"status": "success", "message": f"Mensagem enviada para o grupo {getattr(group, 'name', group_id)}", "payload": msg.to_dict()}
                    else:
                        return {"status": "error", "message": "Falha ao enviar para o grupo"}
                else:
                    return {"status": "error", "message": "Grupo não encontrado ou você não é membro"}
            else:
                return {"status": "error", "message": "Campos insuficientes para mensagem de grupo"}
        
        elif msg_type == "get_private_messages":
            other = envelope.get("other_user_id") or envelope.get("with")
            if other:
                messages = get_private_messages(user_id, other)
                # Converte para dict na resposta
                return {
                    "status": "success", 
                    "type": "private_history", 
                    "messages": [msg.to_dict() for msg in messages]
                }
            else:
                return {"status": "error", "message": "Usuário do histórico privado não especificado"}

        elif msg_type == "get_group_messages":
            group_id = envelope.get("group_id")
            if group_id:
                messages = get_group_messages(group_id)
                return {
                    "status": "success", 
                    "type": "group_history", 
                    "group_id": group_id,
                    "messages": [msg.to_dict() for msg in messages]
                }
            else:
                return {"status": "error", "message": "ID do grupo não especificado"}

        elif msg_type == "get_user_groups":
            groups = GroupRepository.get_user_groups(user_id)
            groups_data = [{"group_id": g.group_id, "name": g.name} for g in groups]
            return {"status": "success", "type": "user_groups", "groups": groups_data}
        
        elif msg_type == "get_online_users":
            with clients_lock:
                online_users = list(clients.keys())
            return {"status": "success", "type": "online_users", "users": online_users}
        
        else:
            return {"status": "error", "message": "Tipo de mensagem não suportado"}

    except Exception as e:
        return {"status": "error", "message": f"Erro interno: {str(e)}"}


def send_to_user(target_user_id, payload_bytes):
    """Envia bytes para um usuário conectado, se presente."""
    with clients_lock:
        sock = clients.get(target_user_id)
    if sock:
        try:
            sock.sendall(payload_bytes)
        except Exception as e:
            print(f"Falha ao enviar para {target_user_id}: {e}")


def send_to_group(group_id, mensagem_bytes, remetente_id):
    """Enviar mensagem para todos os usuários do grupo, exceto o remetente."""
    group = GroupRepository.get_group_by_id(group_id)
    if not group:
        return
    targets = []
    with clients_lock:
        for uid in getattr(group, 'users', []):
            if uid != remetente_id and uid in clients:
                targets.append(clients[uid])
    for sock in targets:
        try:
            sock.sendall(mensagem_bytes)
        except Exception as e:
            print(f"Falha ao enviar para membro do grupo: {e}")

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
            # inicia uma nova thread para cuidar desse cliente
            # vai voltar para o loop principal e esperar por mais conexões
            thread = threading.Thread(target=thread_client, args=(conn, addr))
            thread.daemon = True # deixa fechar o servidor com Ctrl+C, ou deveria por que pra mim não funcionou
            thread.start()

if __name__ == "__main__":
    start_server()
    
    
    


# HANDLE MESSAGE ANTIGO
# def handle_message(user_id, data):
#     """Processa diferentes tipos de mensagens (JSON) recebidas do cliente.
#     `data` é bytes contendo um JSON por linha."""
#     try:
#         envelope = json.loads(data.decode("utf-8"))
#     except json.JSONDecodeError:
#         return {"status": "error", "message": "Formato JSON inválido"}

#     msg_type = envelope.get("type", "general")

#     try:
#         if msg_type == "general":
#             text = envelope.get("message")
#             if text:
#                 broadcast(f"[{user_id}]: {text}".encode("utf-8"), user_id)
#                 return {"status": "success"}

#         elif msg_type == "private":
#             # aceita 'target_user_id' ou 'to'
#             receiver = envelope.get("target_user_id") or envelope.get("to")
#             text = envelope.get("message") or envelope.get("text") or ""
#             if receiver and text:
#                 ok = send_private_message(user_id, receiver, text)
#                 if ok:
#                     payload = json.dumps({
#                         "type": "private",
#                         "from": user_id,
#                         "message": text,
#                         "timestamp": envelope.get("timestamp")
#                     }, ensure_ascii=False).encode("utf-8")
#                     send_to_user(receiver, payload)
#                     return {"status": "success", "message": f"Mensagem enviada para {receiver}"}
#                 return {"status": "error", "message": "Usuário não encontrado"}

#         elif msg_type == "group":
#             group_id = envelope.get("group_id")
#             text = envelope.get("message") or envelope.get("text") or ""
#             if group_id and text:
#                 group = GroupRepository.get_group_by_id(group_id)
#                 if group and user_id in getattr(group, "users", []):
#                     payload = json.dumps({
#                         "type": "group",
#                         "from": user_id,
#                         "group_id": group_id,
#                         "group_name": getattr(group, "name", None),
#                         "message": text,
#                         "timestamp": envelope.get("timestamp")
#                     }, ensure_ascii=False).encode("utf-8")
#                     send_to_group(group_id, payload, user_id)
#                     return {"status": "success", "message": f"Mensagem enviada para o grupo {getattr(group, 'name', group_id)}"}
#                 return {"status": "error", "message": "Grupo não encontrado ou você não é membro"}

#         elif msg_type == "get_private_messages":
#             other = envelope.get("other_user_id") or envelope.get("with")
#             if other:
#                 messages = get_private_messages(user_id, other)
#                 return {"status": "success", "type": "private_history", "messages": messages}

#         elif msg_type == "get_user_groups":
#             groups = GroupRepository.get_user_groups(user_id)
#             groups_data = [{"group_id": g.group_id, "name": g.name} for g in groups]
#             return {"status": "success", "type": "user_groups", "groups": groups_data}

#         elif msg_type == "get_online_users":
#             with clients_lock:
#                 online_users = list(clients.keys())
#             return {"status": "success", "type": "online_users", "users": online_users}

#         else:
#             return {"status": "error", "message": "Tipo de mensagem não suportado"}

#     except Exception as e:
#         return {"status": "error", "message": f"Erro interno: {str(e)}"}