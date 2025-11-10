import json
from repositories import UserRepository
import client_registry
from message_handler import handle_message

# client_registry: gerencia conexões ativas (user_id -> socket)
# nota: entrega de bytes é responsabilidade do client_registry; as funções
# de serviço (chat_general/chat_private) cuidam de persistência e validação.


def handle_connection(conn, addr):
    """Handler de conexão que roda em uma thread. Recebe a socket e o endereço."""
    user_id = None
    try:
        conn.sendall(b'Conecte com seu user_id:')
        user_id_data = conn.recv(1024).decode("utf-8").strip()

        user_obj = UserRepository.get_user_by_id(user_id_data)
        if user_obj is None:
            user_obj = UserRepository.get_user_by_username(user_id_data)
            if user_obj is None:
                conn.sendall(b'User invalido')
                conn.close()
                return
        user_id = user_obj.user_id
        client_registry.register_client(user_id, conn)
        print(f"Usuario {user_id} conectado de {addr}")
        conn.sendall(b'Conectado ao chat geral!\n')

        while True:
            data = conn.recv(1024)
            if not data:
                print(f"Usuario {user_id} desconectou")
                break
            try:
                envelope = json.loads(data.decode("utf-8"))
            except json.JSONDecodeError:
                conn.sendall(b"Formato JSON invalido\n")
                continue

            response = handle_message(user_id, envelope, conn)
            if response:
                try:
                    conn.sendall((json.dumps(response)).encode("utf-8"))
                except Exception:
                    pass
            if response.get("status") == "error":
                try:
                    conn.sendall(f"Erro: {response.get('message')}\n".encode("utf-8"))
                except Exception:
                    pass

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

# send_to_user e send_to_group são camada de transporte/connection 
