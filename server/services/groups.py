from repositories import GroupRepository, UserRepository, MessageRepository
from models.message import Message
from datetime import datetime
from models.message import Message
from services.chat_private import send_private_message as helper_send_private

# o json das mensagens vai ter que conter o group_id para saber para qual grupo enviar

# Felipe já fez a lógica de grupos, usuarios no groups.py
# os usuarios vão se autenticar com user_id e depois vão mandar mensagens para grupos
# grupos tem a lista de user_ids
# ATt2 DESCULPA EU ESQUECI QUE FICOU REDUNDANTE SEM QUERER FICOU COM AS MESMAS FUNÇÕES DO SERVER.TCP.PY
# Depois decidam o que como irão usar o action.py
# Eu imagino que o groups.py tenh as funções helpers e o actions.py as funções registradas no command registry


#@register_command("action", "send_private_message")
    # def send_private_message(sender_id: str, receiver_id: str, message: str) -> bool:
    #     return helper_send_private(sender_id, receiver_id, message)
    
# Eu vou só botar aqui qualquer coisa pra poder rodar o servidor sem erro


def send_group_message(sender_id: str, group_id: str, text: str) -> bool:
    group = GroupRepository.get_group_by_id(group_id)
    if not group or sender_id not in getattr(group, "users", []):
        return False
    msg = Message(from_=sender_id, to=group_id, text=text)
    MessageRepository.append_message(group_id, msg)
    return True

def get_group_messages(group_id: str):
    return MessageRepository.get_messages(group_id)