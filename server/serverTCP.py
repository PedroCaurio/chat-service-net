import socket
import os
import threading
from dotenv import load_dotenv

load_dotenv()

from server.repositories import UserRepository

HOST = str(os.getenv("HOST", "0.0.0.0")) # 
PORT = int(os.getenv("PORT", 12345))


# Lista para manter todos os sockets de clientes conectados
clients = {}  # agora é {user_id: conn}
lock = threading.Lock() # Lock para sincronizar o acesso a lista de clientes, por que 
# ele faz que apenas uma thread por vez pode acessar a lista. Depois tenho que ler a documentação certinho sobre lock
# por que se várias threads tentarem modificar a lista tem risco de dar problema

# att 2 agora usa a implementação de user do Felipe

# broadcast é a função que envia mensagens para todos os clientes conectados

def broadcast(mensagem_bytes, remetente_user_id): # Chat geral
    """Envia uma mensagem para todos os clientes conectados, exceto o remetente."""
    with lock:
        for client_id, client_conn in clients.items():
            if client_id != remetente_user_id:
                try:
                    client_conn.sendall(mensagem_bytes)
                except Exception as e:
                    print(f"Não foi possível enviar mensagem para {client_id}: {e}")
                    
             
# função que vai lidar com cada cliente em uma thread separada  
# ela espera o user_id, valida, e depois processa mensagens, faz broadcast etc  
def thread_client(conn, addr):
    
    """ Função que roda em uma thread para cada cliente. """
    user_id = None
    try:
        conn.sendall(b'Conecte com seu user_id:')
        user_id_data = conn.recv(1024).decode("utf-8").strip() # o user_id_data é a string temporaria que vai receber
                                                              # o user_id enviado pelo cliente e se for valido
                                                              # vai ser armazenado na variavel user_id

        # Valida user_id usando UserRepository
        if not UserRepository.get_user_by_id(user_id_data):
            conn.sendall(b'User invalido')
            conn.close()
            return

        user_id = user_id_data # armazena o user_id validado 
        with lock:
            clients[user_id] = conn
        print(f"Usuario {user_id} conectado de {addr}") #  log da conexão

        conn.sendall(b'Conectado ao chat geral!\n')
        
        while True:
            data = conn.recv(1024)
            if not data:
                print(f"Usuario {user_id} desconectou")
                break

            mensagem = data.decode("utf-8")
            print(f"[{user_id}@{addr}] {mensagem}")

            # envio da mensagem para todos os outros
            broadcast(f"[{user_id}]: {mensagem}".encode("utf-8"), user_id)

    except ConnectionResetError:
        print(f"Conexão perdida com o usuario {user_id}")
    except Exception as e:
        print(f"Erro inesperado com {user_id}: {e}")
    finally:
        with lock:
            if user_id in clients:
                del clients[user_id]
        conn.close()

def start_server():
    """ Inicia o servidor e espera por conexões. """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Servidor escutando em {HOST}:{PORT}")

        while True:
            # loop principal
            conn, addr = s.accept()
            
            # inicia uma nova thread para cuidar desse cliente
            # vai voltar para o loop principal e esperar por mais conexões
            thread = threading.Thread(target=thread_client, args=(conn, addr))
            thread.daemon = True # deixa fechar o servidor com Ctrl+C, ou deveria por que pra mim não funcionou
            thread.start()

if __name__ == "__main__":
    start_server()