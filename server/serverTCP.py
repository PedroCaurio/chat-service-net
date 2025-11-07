import socket
import os
import threading
from dotenv import load_dotenv

load_dotenv()

HOST = str(os.getenv("HOST", "0.0.0.0")) # 
PORT = int(os.getenv("PORT", 12345))

# Lista para manter todos os sockets de clientes conectados
clients = [] 
lock = threading.Lock() # Lock para sincronizar o acesso a lista de clientes, por que 
# ele faz que apenas uma thread por vez pode acessar a lista. Depois tenho que ler a documentação certinho sobre lock
# por que se várias threads tentarem modificar a lista tem risco de dar problema

# broadcast é a função que envia mensagens para todos os clientes conectados

def broadcast(mensagem_bytes, socket_remetente):
    """ Envia uma mensagem para todos os clientes, exceto ele mesmo """
    with lock: # 
        for client in clients:
            if client != socket_remetente:
                try:
                    client.sendall(mensagem_bytes)
                except Exception as e:
                    print(f" Não foi possível enviar mensagem {e}")
                    
             
# função que vai lidar com cada cliente em uma thread separada    
def thread_client(conn, addr):
    
    """ Função que roda em uma thread para cada cliente. """
    addr_str = f"{addr[0]}:{addr[1]}"
    print(f"{addr_str} conectado.")

    # coloca o novo cliente a lista clients = []
    with lock:
        clients.append(conn)

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                # Se não houver dados, o cliente desconecta 
                print(f" Cliente {addr_str} desconectou.")
                break

            message = data.decode("utf-8")
            print(f"[MENSAGEM DE {addr_str}] {message}")
            
            # Retransmite a mensagem pra todo mundo, tirando ele mesmo
            broadcast(data, conn)

    except ConnectionResetError:
        print(f" Conexão perdida com o cliente {addr_str}.")
    except Exception as e:
        print(f" Erro inesperado com {addr_str}: {e}")
    
    finally:
        # Tira o cliente da lista quando ele sair
        with lock:
            if conn in clients:
                clients.remove(conn)
        # Fecha a conexão dele
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