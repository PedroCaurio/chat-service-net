"""Registry para conexões de clients (user_id -> socket).

Responsabilidade: manter o mapa de clientes conectados e oferecer API thread-safe
para registrar, desregistrar e enviar bytes aos clientes ou grupos.
"""
from typing import Optional, List
from database.lock_manager import get_lock
from repositories import GroupRepository

from registry import register_command, get_command

# Lock central (usa o lock manager do projeto para consistência)
_lock = get_lock("clients")
# mapa interno: user_id -> socket
_clients: dict[str, object] = {}

@register_command("login")
def register_client(username: str, password: str, conn=None, **kwargs) -> None:
    """Registra ou substitui a conexão de um usuário.

    Se já houver uma conexão anterior, esta função fecha a antiga e substitui
    pelo novo socket.
    """
    auth_func = get_command("auth")

    if not auth_func(username, password):
        return {"status":"error", "payload":{"message":"credenciais ivalidas"}}
    
    with _lock:
        old = _clients.get(username)
        if old is not None and old is not conn:
            try:
                old.close()
            except Exception:
                pass
        _clients[username] = conn
        
    return {"status":"success", "payload":{"message": f"Usuário {username} logado com sucesso"}}

@register_command("logout")
def unregister_client(username: str, **kwargs) -> None:
    """Remove o cliente do registry (não fecha socket se já estiver fechado)."""
    with _lock:
        if username in _clients:
            try:
                _clients[username].close()
            except Exception:
                pass
            del _clients[username]

            return {"status":"success", "payload":{"message": f"Logout do usuário {username} realizado com sucesso"}}
        
        return {"status":"error", "payload":{"message": f"Falha no logout do usuário {username}"}}



def get_socket(username: str):
    """Retorna o socket associado ao username (snapshot)."""
    with _lock:
        return _clients.get(username)


def list_online() -> List[str]:
    """Retorna a lista de usernames online (snapshot)."""
    with _lock:
        return list(_clients.keys())


def send_to_user(username: str, payload: bytes) -> bool:
    """Envia bytes para o usuário se estiver conectado.

    Retorna True se o envio aparentou sucesso, False caso contrário.
    """
    conn = None
    with _lock:
        conn = _clients.get(username)
    if not conn:
        return False
    try:
        conn.sendall(payload)
        return True
    except Exception:
        # falha no envio -> remover cliente para evitar entradas fantasmas
        try:
            unregister_client(username)
        except Exception:
            pass
        return False


def send_to_group(group_name: str, payload: bytes, exclude_id: Optional[str] = None) -> int:
    """Envia payload para todos os membros do grupo que estiverem online.

    Retorna o número de entregas bem-sucedidas.
    """
    group = GroupRepository.get_group_by_name(group_name)
    if not group:
        return 0
    members: list[str] = getattr(group, "users", []) or []
    # snapshot dos membros online
    delivered = 0
    for username in members:
        if username == exclude_id:
            continue
        if send_to_user(username, payload):
            delivered += 1
    return delivered


def clear() -> None:
    """Remove e fecha todas as conexões (uso em testes)."""
    with _lock:
        items = list(_clients.items())
        _clients.clear()
    for _, conn in items:
        try:
            conn.close()
        except Exception:
            pass
