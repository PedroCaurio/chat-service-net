"""Registry para conexões de clients (user_id -> socket).

Responsabilidade: manter o mapa de clientes conectados e oferecer API thread-safe
para registrar, desregistrar e enviar bytes aos clientes ou grupos.
"""
from typing import Optional, List
from database.lock_manager import get_lock
from repositories import GroupRepository

# Lock central (usa o lock manager do projeto para consistência)
_lock = get_lock("clients")
# mapa interno: user_id -> socket
_clients: dict[str, object] = {}


def register_client(user_id: str, sock) -> None:
    """Registra ou substitui a conexão de um usuário.

    Se já houver uma conexão anterior, esta função fecha a antiga e substitui
    pelo novo socket.
    """
    with _lock:
        old = _clients.get(user_id)
        if old is not None and old is not sock:
            try:
                old.close()
            except Exception:
                pass
        _clients[user_id] = sock


def unregister_client(user_id: str) -> None:
    """Remove o cliente do registry (não fecha socket se já estiver fechado)."""
    with _lock:
        if user_id in _clients:
            try:
                _clients[user_id].close()
            except Exception:
                pass
            del _clients[user_id]


def get_socket(user_id: str):
    """Retorna o socket associado ao user_id (snapshot)."""
    with _lock:
        return _clients.get(user_id)


def list_online() -> List[str]:
    """Retorna a lista de user_ids online (snapshot)."""
    with _lock:
        return list(_clients.keys())


def send_to_user(user_id: str, payload: bytes) -> bool:
    """Envia bytes para o usuário se estiver conectado.

    Retorna True se o envio aparentou sucesso, False caso contrário.
    """
    sock = None
    with _lock:
        sock = _clients.get(user_id)
    if not sock:
        return False
    try:
        sock.sendall(payload)
        return True
    except Exception:
        # falha no envio -> remover cliente para evitar entradas fantasmas
        try:
            unregister_client(user_id)
        except Exception:
            pass
        return False


def send_to_group(group_id: str, payload: bytes, exclude_id: Optional[str] = None) -> int:
    """Envia payload para todos os membros do grupo que estiverem online.

    Retorna o número de entregas bem-sucedidas.
    """
    group = GroupRepository.get_group_by_id(group_id)
    if not group:
        return 0
    members: list[str] = getattr(group, "users", []) or []
    # snapshot dos membros online
    delivered = 0
    for uid in members:
        if uid == exclude_id:
            continue
        if send_to_user(uid, payload):
            delivered += 1
    return delivered


def clear() -> None:
    """Remove e fecha todas as conexões (uso em testes)."""
    with _lock:
        items = list(_clients.items())
        _clients.clear()
    for _, sock in items:
        try:
            sock.close()
        except Exception:
            pass
