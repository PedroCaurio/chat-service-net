'''
Esse script apenas possui a função que é executada por cada thread, sendo a porta de entrada dos clientes.
Ela deve escutar e responder as requisições dos clientes, delegando o serviço solicitado pelo cliente para 
outro script da pasta services.
'''


import json
from repositories import UserRepository
import client_registry
from message_handler import handle_message
from registry import get_command
from services.action import login

def handle_connection(conn, addr):
    """Handler de conexão que roda em uma thread. Recebe a socket e o endereço."""
    user_id = None
    try:
        
        while True:
            data = conn.recv(1024)
            if not data:
                print(f"Usuario {user_id} desconectou")
                break
            try:

                envelope = json.loads(data.decode("utf-8"))
                command = envelope.get("type")
                args = envelope.get("payload")
                func = get_command(command)
                print("args: ",args)
                if command == "login":
                    args["conn"] = conn
                    msg = func(**args)

                    send_json(conn, msg)
                elif func:
                    msg = func(**args)

                    send_json(conn, msg)




            except json.JSONDecodeError:
                conn.sendall(b"Formato JSON invalido\n")
                continue
    except ConnectionResetError:
        print(f"Conexão perdida com o usuario {user_id}")
    except Exception as e:
        print(f"Erro inesperado com {user_id}: {e}")
    finally:
        try:
            client_registry.unregister_client(user_id)
        except Exception:
            pass
        conn.close()

''' Envia o dicionário passado como data para o servidor'''
def send_json(sock, data):
    sock.sendall(json.dumps(data).encode())