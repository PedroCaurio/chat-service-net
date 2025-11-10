from server.repositories import UserRepository
from server.repositories.message_repository import MessageRepository
from datetime import datetime
from server.models import Message


def conversation_id(a: str, b: str) -> str:
    """Gera um id consistente para a conversa privada entre dois usuários."""
    # ordena para que a conversa entre A e B seja sempre a mesma chave
    return "priv:{}:{}".format(*sorted([a, b]))


def send_private_message(sender_id: str, receiver_id: str, text: str) -> bool:
    """Valida usuários e persiste a mensagem (retorna True se OK)."""
    # valida existência dos usuários via repositório
    if not UserRepository.get_user_by_id(sender_id):
        return False
    if not UserRepository.get_user_by_id(receiver_id):
        return False

    msg = Message(from_=sender_id, to=receiver_id, text=text)
    conv = conversation_id(sender_id, receiver_id)  # gera o id da conversa
    MessageRepository.append_message(conv, msg)  # persiste a mensagem
    return True


def get_private_messages(user_a: str, user_b: str) -> list:
    conv = conversation_id(user_a, user_b)
    return MessageRepository.get_messages(conv)
