import json
from repositories import UserRepository
import client_registry
from message_handler import handle_message
from services import action

from registry import get_command

# client_registry: gerencia conexões ativas (user_id -> socket)
# nota: entrega de bytes é responsabilidade do client_registry; as funções
# de serviço (chat_general/chat_private) cuidam de persistência e validação.


def handle_connection(conn, addr):
    """Handler de conexão que roda em uma thread. Recebe a socket e o endereço."""
    username = None
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                print(f"Usuario {username} desconectou")
                break
            try:
                msg = json.loads(data.decode("utf-8"))
                msg_type = msg.get("type")
                payload = msg.get("payload")

                if msg_type == "request" and payload:
                    command = payload.get("command")
                    func = get_command(command)
                    if func:
                        result = func(conn=conn, **payload)
                        response = result

                    else:
                        response = {"type": "error", "payload": {"message": f"Comando '{command}' não encontrado."}}

                else:
                    response = {"type": "error", "payload": {"message": "Tipo de mensagem não suportado."}}

            except Exception as e:
                response = {"type": "error", "payload": {"message": str(e)}}

            if response:
                conn.sendall(json.dumps(response).encode())

    except ConnectionResetError:
        print(f"Conexão perdida com o usuario {username}")
    except Exception as e:
        print(f"Erro inesperado com {username}: {e}")
    finally:
        try:
            client_registry.unregister_client(username)
        except Exception:
            pass
        conn.close()

# send_to_user e send_to_group são camada de transporte/connection 
