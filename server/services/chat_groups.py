from repositories import GroupRepository
from repositories.message_repository import MessageRepository
from models import Message


def send_group_message(sender_id: str, group_id: str, text: str) -> bool:
    """Envia e persiste uma mensagem para o grupo.

    Valida se o grupo existe e se o remetente é membro. Persiste a mensagem
    usando MessageRepository com a chave do grupo.
    """
    group = GroupRepository.get_group_by_id(group_id)
    if not group or sender_id not in getattr(group, "users", []):
        return False
    msg = Message(from_=sender_id, to=group_id, text=text)
    MessageRepository.append_message(group_id, msg)
    return True


def get_group_messages(group_id: str):
    """Retorna as mensagens persistidas do grupo (lista de Message)."""
    return MessageRepository.get_messages(group_id)
