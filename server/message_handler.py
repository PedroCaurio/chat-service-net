import json
from typing import Optional

from repositories import UserRepository, GroupRepository
from services.chat_private import send_private_message, get_private_messages
from services.chat_general import send_general_message, get_general_messages
from services.groups import send_group_message, get_group_messages
from models.message import Message
import client_registry

from registry import register_command


@register_command("general")
def handle_general_message(username, envelope, conn, **kwargs):
    text = envelope.get("message")
    if not text:
        return {"status": "error", "message": "Mensagem vazia"}

    msg = send_general_message(username, text)
    if not msg:
        return {"status": "error", "message": "Falha ao persistir mensagem"}

    payload = json.dumps(msg.to_dict(), ensure_ascii=False).encode("utf-8")
    for uid in client_registry.list_online():
        if uid != username:
            client_registry.send_to_user(uid, payload)
    return {"status": "success", "payload": msg.to_dict()}


@register_command("get_general_messages")
def handle_general_history(username, envelope, conn, **kwargs):
    messages = get_general_messages()
    return {
        "status": "success",
        "type": "general_history",
        "messages": [msg.to_dict() for msg in messages]
    }

@register_command("private")
def handle_private_message(username, envelope, conn, **kwargs):
    receiver = envelope.get("target_user_id") or envelope.get("to")
    text = envelope.get("message") or envelope.get("text") or ""
    if not receiver or not text:
        return {"status": "error", "message": "Campos insuficientes"}

    target_obj = UserRepository.get_user_by_id(receiver) or UserRepository.get_user_by_username(receiver)
    if not target_obj:
        return {"status": "error", "message": "Usuário não encontrado"}

    receiver_id = target_obj.user_id
    ok = send_private_message(username, receiver_id, text)
    if not ok:
        return {"status": "error", "message": "Falha ao persistir/enviar mensagem"}

    msg = Message(from_=username, to=receiver_id, text=text)
    payload = json.dumps(msg.to_dict(), ensure_ascii=False).encode("utf-8")
    client_registry.send_to_user(receiver_id, payload)
    return {"status": "success", "message": f"Mensagem enviada para {receiver}", "payload": msg.to_dict()}


@register_command("get_private_messages")
def handle_private_history(username, envelope, conn, **kwargs):
    other = envelope.get("other_user_id") or envelope.get("with")
    if not other:
        return {"status": "error", "message": "Usuário do histórico não especificado"}

    messages = get_private_messages(username, other)
    return {
        "status": "success",
        "type": "private_history",
        "messages": [msg.to_dict() for msg in messages]
    }

@register_command("group")
def handle_group_message(username, envelope, conn, **kwargs):
    group_name = envelope.get("group_name")
    text = envelope.get("message") or envelope.get("text") or ""
    if not group_name or not text:
        return {"status": "error", "message": "Campos insuficientes para mensagem de grupo"}

    group = GroupRepository.get_group_by_id(group_name)
    if not group or username not in getattr(group, "users", []):
        return {"status": "error", "message": "Grupo não encontrado ou você não é membro"}

    ok = send_group_message(username, group_name, text)
    if not ok:
        return {"status": "error", "message": "Falha ao enviar para o grupo"}

    msg = Message(from_=username, to=group_name, text=text)
    payload = json.dumps(msg.to_dict(), ensure_ascii=False).encode("utf-8")
    client_registry.send_to_group(group_name, payload, exclude_id=username)
    return {"status": "success", "message": f"Mensagem enviada para o grupo {group_name}", "payload": msg.to_dict()}


@register_command("get_group_messages")
def handle_group_history(username, envelope, conn, **kwargs):
    group_name = envelope.get("group_name")
    if not group_name:
        return {"status": "error", "message": "ID do grupo não especificado"}

    group = GroupRepository.get_group_by_id(group_name)
    if not group or username not in getattr(group, "users", []):
        return {"status": "error", "message": "Grupo não encontrado ou você não é membro"}

    messages = get_group_messages(group_name)
    return {
        "status": "success",
        "type": "group_history",
        "group_name": group_name,
        "messages": [msg.to_dict() for msg in messages]
    }