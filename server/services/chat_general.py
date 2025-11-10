from server.repositories.message_repository import MessageRepository
from server.repositories import UserRepository
from server.models import Message
from datetime import datetime


def _conversation_key() -> str:
	"""Chave usada para armazenar mensagens do chat geral."""
	return "general"


def send_general_message(sender_id: str, text: str) -> Message | None:
	"""Valida remetente, cria e persiste uma mensagem no chat geral.

	Retorna o objeto Message persistido ou None em caso de falha.
	"""
	# valida existência do remetente
	if not UserRepository.get_user_by_id(sender_id):
		return None

	msg = Message(from_=sender_id, to="general", text=text)
	key = _conversation_key()
	MessageRepository.append_message(key, msg)
	return msg


def get_general_messages() -> list:
	"""Retorna as mensagens do chat geral (lista de Message)."""
	key = _conversation_key()
	return MessageRepository.get_messages(key)

